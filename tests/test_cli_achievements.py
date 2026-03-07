"""Tests for achievements CLI helper."""

from dataclasses import dataclass

from key4ce.__main__ import _compute_achievements


@dataclass
class _Session:
    wpm: float
    accuracy: float
    duration: float


def test_compute_achievements_empty():
    assert _compute_achievements([]) == []


def test_compute_achievements_unlocks_expected_milestones():
    records = [_Session(wpm=62, accuracy=96, duration=400) for _ in range(10)]
    unlocked = _compute_achievements(records)
    ids = {a["id"] for a in unlocked}

    assert "first_run" in ids
    assert "ten_sessions" in ids
    assert "speed_60" in ids
    assert "accuracy_95" in ids
    assert "one_hour" in ids
