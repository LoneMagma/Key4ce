"""Tests for assignment planning helper."""

from key4ce.__main__ import _build_assignment_plan


def test_build_assignment_plan_shape():
    plan = _build_assignment_plan(days=7)
    assert set(plan.keys()) == {"window_days", "profile", "coach_next_step", "assignment"}
    assert len(plan["assignment"]) == 3
    assert plan["assignment"][0]["step"] == 1
