from __future__ import annotations

import time
from typing import Any

import optuna

from ..config import TuningConfig
from ..errors import TrialPruned
from ..objective import normalize_objective_result
from ..runner import EventEmitter, ObjectiveFn
from ..schema import ParamSchema


def run_optuna(
    *,
    schema: ParamSchema,
    objective: ObjectiveFn,
    config: TuningConfig,
    emitter: EventEmitter,
) -> dict[str, Any]:
    sampler = optuna.samplers.TPESampler(seed=config.seed)
    study = optuna.create_study(direction=config.direction, sampler=sampler)
    best_score: float | None = None
    best_trial_number: int | None = None

    # Track per-trial context (params, started time, exc) for after-trial callback.
    _trial_context: dict[int, dict[str, Any]] = {}

    def optuna_objective(trial: optuna.Trial) -> float:
        nonlocal best_score, best_trial_number
        params = schema.suggest(trial)
        started = time.perf_counter()
        _trial_context[trial.number] = {"params": params, "started": started}
        emitter.emit("trial_started", trial_number=trial.number, params=params, state="running")
        try:
            result = normalize_objective_result(objective(params))
        except TrialPruned as exc:
            duration_ms = int((time.perf_counter() - started) * 1000)
            emitter.emit(
                "trial_pruned",
                trial_number=trial.number,
                params=params,
                state="pruned",
                duration_ms=duration_ms,
                error=str(exc),
            )
            raise optuna.exceptions.TrialPruned(str(exc)) from exc
        except Exception as exc:
            # Store the exception so the after-trial callback can emit trial_failed.
            _trial_context[trial.number]["exc"] = exc
            # Re-raise so Optuna records the trial as FAIL (not PRUNED).
            raise

        duration_ms = int((time.perf_counter() - started) * 1000)
        emitter.emit(
            "trial_completed",
            trial_number=trial.number,
            params=params,
            score=result.score,
            state="complete",
            duration_ms=duration_ms,
            metrics=result.metrics,
            artifacts=result.artifacts,
            metadata=result.metadata,
        )
        if _is_better(result.score, best_score, config.direction):
            best_score = result.score
            best_trial_number = trial.number
            emitter.emit(
                "best_updated",
                trial_number=trial.number,
                params=params,
                score=result.score,
                state="complete",
                metrics=result.metrics,
                artifacts=result.artifacts,
                metadata=result.metadata,
            )
        return result.score

    def _after_trial_callback(
        study: optuna.Study,
        frozen_trial: optuna.trial.FrozenTrial,
    ) -> None:
        """Emit trial_failed for trials that Optuna recorded as FAIL."""
        if frozen_trial.state != optuna.trial.TrialState.FAIL:
            return
        ctx = _trial_context.pop(frozen_trial.number, None)
        if ctx is None:
            return
        exc = ctx.get("exc")
        duration_ms = int((time.perf_counter() - ctx["started"]) * 1000)
        emitter.emit(
            "trial_failed",
            trial_number=frozen_trial.number,
            params=ctx["params"],
            state="failed",
            duration_ms=duration_ms,
            error=repr(exc) if exc is not None else "unknown",
        )

    study.optimize(
        optuna_objective,
        n_trials=config.n_trials,
        show_progress_bar=False,
        catch=(Exception,),
        callbacks=[_after_trial_callback],
    )

    complete_trials = [trial for trial in study.trials if trial.state == optuna.trial.TrialState.COMPLETE]
    if not complete_trials:
        return {"best_params": {}, "best_score": None, "best_trial_number": None, "n_trials": len(study.trials)}

    return {
        "best_params": dict(study.best_params),
        "best_score": float(study.best_value),
        "best_trial_number": int(study.best_trial.number),
        "n_trials": len(study.trials),
    }


def _is_better(score: float, best: float | None, direction: str) -> bool:
    if best is None:
        return True
    if direction == "maximize":
        return score > best
    return score < best
