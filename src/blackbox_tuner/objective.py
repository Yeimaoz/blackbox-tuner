from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from .errors import SerializationError


@dataclass(frozen=True)
class ObjectiveResult:
    score: float
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_json_dict(self) -> dict[str, Any]:
        payload = {
            "score": float(self.score),
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }
        _assert_json_serializable(payload)
        return payload


def normalize_objective_result(value: float | int | ObjectiveResult) -> ObjectiveResult:
    if isinstance(value, ObjectiveResult):
        value.to_json_dict()
        return value
    try:
        result = ObjectiveResult(score=float(value))
    except (TypeError, ValueError) as exc:
        raise TypeError("objective must return float or ObjectiveResult") from exc
    result.to_json_dict()
    return result


def _assert_json_serializable(value: Any) -> None:
    try:
        json.dumps(value, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise SerializationError("objective result must be JSON-serializable") from exc
