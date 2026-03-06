"""Tests for shareable brag card output."""

from key4ce.__main__ import _build_brag_card


def test_brag_card_with_sessions():
    card = _build_brag_card(
        {
            "days": 7,
            "sessions": 3,
            "avg_wpm": 61.2,
            "avg_accuracy": 95.4,
            "best_wpm": 78.0,
            "current_streak_days": 2,
        }
    )
    assert "Key4ce 7-day check-in" in card
    assert "Avg WPM: 61.2" in card
    assert "Current Streak: 2" in card


def test_brag_card_empty_window():
    card = _build_brag_card({"days": 7, "sessions": 0})
    assert "No sessions yet" in card
