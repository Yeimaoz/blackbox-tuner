from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Sequence
from uuid import uuid4

from .checkpoints import CheckpointSink
from .config import TuningConfig
from .errors import CheckpointError
from .events import TrialEvent
from .objective import ObjectiveResult
from .schema import ParamSchema


ObjectiveFn = Callable[[dict[str, Any]], float | int | ObjectiveResult]


@dataclass(frozen=True)
class TuningResult:
    """Result of a completed tuning run.

    Known Limitations:
    - ``state`` is typed as ``str`` but ``tune()`` always returns ``"complete"``
      on success (exceptions are raised on failure).  A future version may
      narrow this to ``Literal["complete"]``.
    - ``started_at`` and ``finished_at`` are ISO 8601 UTC strings
      (``YYYY-MM-DDTHH:MM:SS.ffffffZ``), typed as ``str`` for forward
      compatibility.
    """

    run_id: str
    best_params: dict[str, Any]
    best_score: float | None
    best_trial_number: int | None
    n_trials: int
    state: str
    started_at: str
    finished_at: str
    summary: dict[str, Any]


class EventEmitter:
    def __init__(self, run_id: str, sinks: Sequence[CheckpointSink]) -> None:
        self.run_id = run_id
        self.sinks = list(sinks)
        self.sequence = 0
        self._failed_sink_ids: set[int] = set()

    def emit(self, event_type: str, **kwargs: Any) -> None:
        self.sequence += 1
        event = TrialEvent(
            run_id=self.run_id,
            event_type=event_type,  # type: ignore[arg-type]
            sequence=self.sequence,
            created_at=utc_now(),
            **kwargs,
        )
        self._write_event(event)

    def emit_run_failed_to_healthy_sinks(self, error: str) -> None:
        self.sequence += 1
        event = TrialEvent(
            run_id=self.run_id,
            event_type="run_failed",
            sequence=self.sequence,
            created_at=utc_now(),
            state="failed",
            error=error,
        )
        self._write_event(event, raise_on_failure=False)

    def _write_event(self, event: TrialEvent, *, raise_on_failure: bool = True) -> None:
        first_error: CheckpointError | None = None
        for sink in self.sinks:
            if id(sink) in self._failed_sink_ids:
                continue
            try:
                sink.write(event)
            except CheckpointError as exc:
                self._failed_sink_ids.add(id(sink))
                if first_error is None:
                    first_error = exc
        if first_error is not None and raise_on_failure:
            raise first_error


def tune(
    *,
    schema: ParamSchema,
    objective: ObjectiveFn,
    config: TuningConfig | None = None,
    sinks: Sequence[CheckpointSink] = (),
) -> TuningResult:
    from .backends.optuna import run_optuna

    config = config or TuningConfig()
    run_id = config.run_id or f"run-{uuid4().hex[:12]}"
    started_at = utc_now()
    emitter = EventEmitter(run_id, sinks)
    try:
        emitter.emit("run_started", state="running")
        backend_result = run_optuna(schema=schema, objective=objective, config=config, emitter=emitter)
        finished_at = utc_now()
        emitter.emit("run_completed", state="complete")
    except CheckpointError as exc:
        emitter.emit_run_failed_to_healthy_sinks(repr(exc))
        raise
    except Exception as exc:
        emitter.emit_run_failed_to_healthy_sinks(repr(exc))
        raise
    return TuningResult(
        run_id=run_id,
        best_params=backend_result["best_params"],
        best_score=backend_result["best_score"],
        best_trial_number=backend_result["best_trial_number"],
        n_trials=backend_result["n_trials"],
        state="complete",
        started_at=started_at,
        finished_at=finished_at,
        summary={"backend": "optuna"},
    )


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
