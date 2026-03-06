"""Tests for telemetry payload helper."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from key4ce.__main__ import _build_telemetry_payload


@dataclass
class _Session:
    ts: str
    source: str
    wpm: float
    accuracy: float
    duration: float


class _FakeDB:
    def __init__(self, sessions):
        self._sessions = sessions

    def connect(self):
        return None

    def close(self):
        return None

    def list_sessions(self):
        return self._sessions


def test_telemetry_payload_is_aggregated(monkeypatch):
    now = datetime.now()
    sessions = [
        _Session(ts=(now - timedelta(days=1)).isoformat(), source="sentences", wpm=48, accuracy=94, duration=120),
        _Session(ts=(now - timedelta(days=2)).isoformat(), source="words", wpm=52, accuracy=96, duration=150),
    ]
    monkeypatch.setattr("key4ce.data.db.Database", lambda: _FakeDB(sessions))

    payload = _build_telemetry_payload(days=30)

    assert payload["schema"] == "key4ce.telemetry.v1"
    assert payload["totals"]["sessions"] == 2
    assert payload["sources"]["sentences"] == 1
    assert payload["privacy"]["contains_keystroke_timings"] is False
