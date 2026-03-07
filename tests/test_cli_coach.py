"""Tests for coach plan helper."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from key4ce.__main__ import _build_coach_plan


@dataclass
class _Session:
    ts: str
    wpm: float
    accuracy: float
    duration: float


@dataclass
class _Focus:
    weak_digraphs: list[str]
    problem_chars: list[str]


def test_build_coach_plan_includes_drills_and_next_step():
    now = datetime.now()
    sessions = [
        _Session(ts=(now - timedelta(days=1)).isoformat(), wpm=40, accuracy=90, duration=120),
        _Session(ts=(now - timedelta(days=2)).isoformat(), wpm=42, accuracy=91, duration=140),
    ]
    plan = _build_coach_plan(sessions, _Focus(["th", "ng"], ["e", "i"]), days=7)
    assert plan["summary"]["sessions"] == 2
    assert len(plan["drills"]) >= 1
    assert isinstance(plan["next_step"], str)


def test_build_coach_plan_empty_sessions():
    plan = _build_coach_plan([], _Focus([], []), days=7)
    assert plan["summary"]["sessions"] == 0
    assert "Start" in plan["next_step"]
