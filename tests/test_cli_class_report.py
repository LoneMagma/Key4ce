"""Tests for class-report helper."""

import json
from pathlib import Path

from key4ce.__main__ import _build_class_report


def test_class_report_aggregates_snapshots(tmp_path: Path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"sessions": [{"wpm": 50, "accuracy": 95}, {"wpm": 60, "accuracy": 96}]}), encoding="utf-8")
    b.write_text(json.dumps({"sessions": [{"wpm": 70, "accuracy": 97}]}), encoding="utf-8")

    out = _build_class_report([str(a), str(b)])
    assert out["students"] == 2
    assert out["total_sessions"] == 3
    assert out["class_avg_wpm"] > 0
