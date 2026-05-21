from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal

from .errors import SerializationError


EventType = Literal[
    "run_started",
    "trial_started",
    "trial_completed",
    "trial_failed",
    "trial_pruned",
    "best_updated",
    "run_completed",
    "run_failed",
]


@dataclass(frozen=True)
class TrialEvent:
    run_id: str
    event_type: EventType
    sequence: int
    created_at: str
    trial_number: int | None = None
    params: dict[str, Any] = field(default_factory=dict)
    score: float | None = None
    state: str | None = None
    duration_ms: int | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    schema_version: int = 1

    def to_json_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "event_type": self.event_type,
            "sequence": self.sequence,
            "created_at": self.created_at,
            "trial_number": self.trial_number,
            "params": self.params,
            "score": self.score,
            "state": self.state,
            "duration_ms": self.duration_ms,
            "metrics": self.metrics,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
            "error": self.error,
        }
        try:
            json.dumps(payload, allow_nan=False, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise SerializationError("trial event must be JSON-serializable") from exc
        return payload
