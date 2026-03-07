"""Tests for analytics recommendation and trend helpers."""

from key4ce.data.db import SessionRecord, StatsSnapshot
from key4ce.themes.themes import DEFAULT_THEME
from key4ce.ui.screens.analytics import AnalyticsScreen, _build_overview, _fallback_recommendation


def _session(i: int, wpm: float, acc: float, errs: int) -> SessionRecord:
    return SessionRecord(
        id=i,
        ts=f"2026-01-0{i}T00:00:00",
        source="sentences",
        wpm=wpm,
        accuracy=acc,
        duration=60,
        chars_typed=250,
        errors=[{"expected": "a", "got": "s"}] * errs,
        timings=[100, 120],
    )


def test_fallback_recommendation_low_accuracy():
    stats = StatsSnapshot(total_sessions=5, best_wpm=80, avg_wpm=65, avg_accuracy=92, recent_sessions=[])
    sessions = [_session(1, 70, 91, 3), _session(2, 66, 92, 4)]
    ov = _build_overview(stats, sessions)
    rec = _fallback_recommendation(ov, sessions)
    assert "accuracy" in rec.lower()


def test_analytics_screen_renders():
    stats = StatsSnapshot(total_sessions=1, best_wpm=72, avg_wpm=72, avg_accuracy=96, recent_sessions=[])
    sessions = [_session(1, 72, 96, 2)]
    screen = AnalyticsScreen(DEFAULT_THEME, stats, sessions)
    assert screen.render() is not None
