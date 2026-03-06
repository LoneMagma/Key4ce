"""Tests for KPI snapshot helper."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from key4ce.__main__ import _build_kpi_snapshot


@dataclass
class _Session:
    ts: str
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


def test_kpi_snapshot_empty(monkeypatch):
    monkeypatch.setattr("key4ce.data.db.Database", lambda: _FakeDB([]))
    out = _build_kpi_snapshot(days=30)
    assert out["sessions"] == 0


def test_kpi_snapshot_basic_metrics(monkeypatch):
    now = datetime.now()
    sessions = [
        _Session(ts=(now - timedelta(days=2)).isoformat(), wpm=50, accuracy=95, duration=120),
        _Session(ts=(now - timedelta(days=1)).isoformat(), wpm=70, accuracy=97, duration=180),
    ]
    monkeypatch.setattr("key4ce.data.db.Database", lambda: _FakeDB(sessions))
    out = _build_kpi_snapshot(days=30)
    assert out["sessions"] == 2
    assert out["best_wpm"] == 70.0
    assert out["avg_accuracy"] == 96.0
