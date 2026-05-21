import json

import pytest

from blackbox_tuner import FloatParam, IntParam, JsonlCheckpoint, ObjectiveResult, ParamSchema, TrialPruned, TuningConfig, tune
from blackbox_tuner.errors import CheckpointError


def test_tune_returns_best_params():
    schema = ParamSchema([
        IntParam("x", low=-5, high=5),
        FloatParam("y", low=-2.0, high=2.0),
    ])

    def objective(params):
        return -((params["x"] - 2) ** 2) - ((params["y"] + 0.5) ** 2)

    result = tune(schema=schema, objective=objective, config=TuningConfig(n_trials=30, seed=3))

    assert result.best_params
    assert result.best_score is not None
    assert result.n_trials == 30
    assert result.state == "complete"


def test_tune_writes_events(tmp_path):
    path = tmp_path / "events.jsonl"
    schema = ParamSchema([IntParam("x", low=0, high=3)])

    def objective(params):
        return ObjectiveResult(
            score=-abs(params["x"] - 1),
            metrics={"distance": abs(params["x"] - 1)},
            metadata={"kind": "synthetic"},
        )

    tune(
        schema=schema,
        objective=objective,
        config=TuningConfig(n_trials=8, seed=1, run_id="run-test"),
        sinks=[JsonlCheckpoint(path)],
    )

    events = [json.loads(line) for line in path.read_text().splitlines()]
    event_types = [event["event_type"] for event in events]
    assert event_types[0] == "run_started"
    assert "trial_completed" in event_types
    assert "best_updated" in event_types
    assert event_types[-1] == "run_completed"
    completed = next(event for event in events if event["event_type"] == "trial_completed")
    assert completed["metadata"] == {"kind": "synthetic"}


def test_failed_objective_emits_trial_failed(tmp_path):
    path = tmp_path / "events.jsonl"
    schema = ParamSchema([IntParam("x", low=0, high=1)])

    def objective(params):
        raise RuntimeError("boom")

    result = tune(
        schema=schema,
        objective=objective,
        config=TuningConfig(n_trials=2, seed=1, run_id="run-fail"),
        sinks=[JsonlCheckpoint(path)],
    )

    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert result.state == "complete"
    assert any(event["event_type"] == "trial_failed" for event in events)


def test_pruned_objective_emits_trial_pruned(tmp_path):
    path = tmp_path / "events.jsonl"
    schema = ParamSchema([IntParam("x", low=0, high=1)])

    def objective(params):
        raise TrialPruned("skip")

    result = tune(
        schema=schema,
        objective=objective,
        config=TuningConfig(n_trials=2, seed=1, run_id="run-pruned"),
        sinks=[JsonlCheckpoint(path)],
    )

    events = [json.loads(line) for line in path.read_text().splitlines()]
    assert result.state == "complete"
    assert any(event["event_type"] == "trial_pruned" for event in events)


class MemorySink:
    def __init__(self):
        self.events = []

    def write(self, event):
        self.events.append(event)


class FailingSink:
    def write(self, event):
        raise CheckpointError("sink failed")


def test_checkpoint_failure_emits_run_failed_to_healthy_sink():
    healthy = MemorySink()
    schema = ParamSchema([IntParam("x", low=0, high=1)])

    with pytest.raises(CheckpointError):
        tune(
            schema=schema,
            objective=lambda params: 1.0,
            config=TuningConfig(n_trials=1, seed=1, run_id="run-checkpoint-fail"),
            sinks=[FailingSink(), healthy],
        )

    assert healthy.events[-1].event_type == "run_failed"


def test_tuning_config_rejects_invalid_direction():
    with pytest.raises(ValueError, match="direction"):
        TuningConfig(direction="sideways")  # type: ignore[arg-type]
