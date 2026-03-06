"""Tests for goals helpers in CLI."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from key4ce.__main__ import _compute_today_progress, _load_goals, _save_goals


@dataclass
class _Session:
    ts: str
    duration: float


def test_goals_load_defaults_when_missing(tmp_path: Path):
    p = tmp_path / "goals.json"
    goals = _load_goals(p)
    assert goals["daily_minutes"] == 15
    assert goals["daily_sessions"] == 1


def test_goals_save_and_reload(tmp_path: Path):
    p = tmp_path / "goals.json"
    _save_goals({"daily_minutes": 25, "daily_sessions": 2}, p)
    goals = _load_goals(p)
    assert goals["daily_minutes"] == 25
    assert goals["daily_sessions"] == 2


def test_compute_today_progress_filters_to_today():
    now = datetime.now()
    sessions = [
        _Session(ts=(now - timedelta(hours=1)).isoformat(), duration=120),
        _Session(ts=(now - timedelta(days=1)).isoformat(), duration=600),
    ]
    progress = _compute_today_progress(sessions)
    assert progress["today_sessions"] == 1
    assert progress["today_minutes"] == 2.0


def test_apply_goal_template_uses_expected_targets(monkeypatch):
    captured = {}

    def fake_set_goals(minutes, sessions):
        captured["minutes"] = minutes
        captured["sessions"] = sessions
        return {"daily_minutes": minutes, "daily_sessions": sessions}

    monkeypatch.setattr("key4ce.__main__._set_goals", fake_set_goals)

    from key4ce.__main__ import _apply_goal_template

    goals = _apply_goal_template("steady")
    assert captured == {"minutes": 20, "sessions": 2}
    assert goals == {"daily_minutes": 20, "daily_sessions": 2}
