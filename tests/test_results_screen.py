"""Tests for results-screen phase 1 coaching hints."""

from key4ce.core.analyzer import SessionAnalysis
from key4ce.themes.themes import DEFAULT_THEME
from key4ce.ui.screens.results import ResultsScreen


def _analysis(wpm: float, accuracy: float, chars: int = 50, errors: int = 2) -> SessionAnalysis:
    return SessionAnalysis(
        wpm=wpm,
        accuracy=accuracy,
        duration_sec=30,
        chars_typed=chars,
        total_errors=errors,
        top_errors=[],
        slow_digraphs=[],
        problem_keys=[],
        wpm_buckets=[],
        error_log=[],
    )


def test_next_step_prioritizes_accuracy_when_low():
    screen = ResultsScreen(_analysis(wpm=70, accuracy=85), "sentences", 60, DEFAULT_THEME)
    assert "accuracy" in screen._next_step_text().lower()


def test_next_step_prioritizes_rhythm_for_new_typists():
    screen = ResultsScreen(_analysis(wpm=30, accuracy=97), "sentences", 40, DEFAULT_THEME)
    text = screen._next_step_text().lower()
    assert "25 words" in text or "rhythm" in text


def test_next_step_suggests_focus_when_error_rate_high():
    screen = ResultsScreen(_analysis(wpm=55, accuracy=94, chars=40, errors=8), "code", 56, DEFAULT_THEME)
    assert "focus mode" in screen._next_step_text().lower()


def test_pace_insight_for_bucket_variation():
    a = _analysis(wpm=55, accuracy=95)
    a.wpm_buckets = [40.0, 55.0, 62.0]
    screen = ResultsScreen(a, "sentences", 50, DEFAULT_THEME)
    text = screen._pace_insight_text().lower()
    assert "peak" in text
    assert "bucket" in text


def test_pace_insight_empty_for_short_series():
    a = _analysis(wpm=55, accuracy=95)
    a.wpm_buckets = [50.0]
    screen = ResultsScreen(a, "sentences", 50, DEFAULT_THEME)
    assert screen._pace_insight_text() == ""
