import json

import pytest

from blackbox_tuner import JsonlCheckpoint, TrialEvent
from blackbox_tuner.errors import CheckpointError


def make_event():
    return TrialEvent(
        run_id="run-1",
        event_type="run_started",
        sequence=1,
        created_at="2026-01-01T00:00:00Z",
    )


def test_jsonl_checkpoint_writes_event(tmp_path):
    path = tmp_path / "events.jsonl"
    sink = JsonlCheckpoint(path)

    sink.write(make_event())

    lines = path.read_text().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["event_type"] == "run_started"


def test_jsonl_checkpoint_wraps_write_error(tmp_path):
    path = tmp_path / "missing" / "events.jsonl"
    sink = JsonlCheckpoint(path)

    with pytest.raises(CheckpointError):
        sink.write(make_event())
