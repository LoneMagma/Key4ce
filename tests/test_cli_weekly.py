"""Tests for weekly summary CLI helper."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from key4ce.__main__ import _summarize_recent_sessions


@dataclass
class _Session:
    ts: str
    wpm: float
    accuracy: float
    duration: float


def test_summarize_recent_sessions_empty():
    summary = _summarize_recent_sessions([], days=7)
    assert summary["sessions"] == 0
    assert summary["avg_wpm"] == 0.0


def test_summarize_recent_sessions_filters_by_window():
    now = datetime.now()
    recent = _Session(ts=(now - timedelta(days=1)).isoformat(), wpm=60, accuracy=95, duration=120)
    old = _Session(ts=(now - timedelta(days=20)).isoformat(), wpm=100, accuracy=99, duration=200)

    summary = _summarize_recent_sessions([recent, old], days=7)
    assert summary["sessions"] == 1
    assert summary["best_wpm"] == 60.0
    assert summary["total_minutes"] == 2.0


def test_summarize_recent_sessions_aggregates_multiple():
    now = datetime.now()
    a = _Session(ts=(now - timedelta(days=2)).isoformat(), wpm=50, accuracy=90, duration=60)
    b = _Session(ts=(now - timedelta(days=3)).isoformat(), wpm=70, accuracy=98, duration=120)

    summary = _summarize_recent_sessions([a, b], days=7)
    assert summary["sessions"] == 2
    assert summary["avg_wpm"] == 60.0
    assert summary["best_wpm"] == 70.0
    assert summary["avg_accuracy"] == 94.0


def test_summarize_recent_sessions_includes_streaks():
    now = datetime.now()
    s1 = _Session(ts=(now - timedelta(days=2)).isoformat(), wpm=45, accuracy=91, duration=60)
    s2 = _Session(ts=(now - timedelta(days=1)).isoformat(), wpm=50, accuracy=93, duration=60)

    summary = _summarize_recent_sessions([s1, s2], days=7)
    assert summary["current_streak_days"] >= 2
    assert summary["longest_streak_days"] >= 2
