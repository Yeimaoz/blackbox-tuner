import pytest

from blackbox_tuner import ObjectiveResult, TrialEvent, TrialPruned, normalize_objective_result
from blackbox_tuner.errors import SerializationError


def test_normalizes_float_result():
    result = normalize_objective_result(1.25)
    assert result == ObjectiveResult(score=1.25)


def test_accepts_structured_result():
    result = normalize_objective_result(ObjectiveResult(score=2.0, metrics={"loss": 0.1}))
    assert result.score == 2.0
    assert result.metrics == {"loss": 0.1}


def test_rejects_non_json_metric_value():
    result = ObjectiveResult(score=1.0, metrics={"bad": object()})
    with pytest.raises(SerializationError, match="JSON-serializable"):
        result.to_json_dict()


def test_rejects_non_finite_score():
    result = ObjectiveResult(score=float("nan"))
    with pytest.raises(SerializationError, match="JSON-serializable"):
        result.to_json_dict()


def test_rejects_non_finite_metric_value():
    result = ObjectiveResult(score=1.0, metrics={"bad": float("inf")})
    with pytest.raises(SerializationError, match="JSON-serializable"):
        result.to_json_dict()


def test_trial_event_serializes():
    event = TrialEvent(
        run_id="run-1",
        event_type="trial_completed",
        sequence=1,
        created_at="2026-01-01T00:00:00Z",
        trial_number=0,
        params={"x": 1},
        score=1.0,
        state="complete",
        duration_ms=3,
        metrics={"loss": 0.0},
        artifacts={},
        metadata={"note": "ok"},
        error=None,
    )

    assert event.to_json_dict()["event_type"] == "trial_completed"


def test_trial_pruned_carries_reason():
    exc = TrialPruned("not promising")
    assert str(exc) == "not promising"
