"""Tests for progress report helper."""

from key4ce.__main__ import _build_progress_report


def test_build_progress_report_shape():
    report = _build_progress_report(days=7)
    assert set(report.keys()) == {"window_days", "summary", "leaderboard", "achievements", "coach"}
    assert "next_step" in report["coach"]
