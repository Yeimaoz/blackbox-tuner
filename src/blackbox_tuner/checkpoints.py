from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .errors import CheckpointError
from .events import TrialEvent


class CheckpointSink(Protocol):
    def write(self, event: TrialEvent) -> None:
        """Persist one event or raise CheckpointError."""


class JsonlCheckpoint:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write(self, event: TrialEvent) -> None:
        try:
            payload = event.to_json_dict()
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload, sort_keys=True) + "\n")
        except CheckpointError:
            raise
        except Exception as exc:
            raise CheckpointError(f"failed to write checkpoint event to {self.path}") from exc
