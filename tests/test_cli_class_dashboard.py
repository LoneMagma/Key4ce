"""Tests for class dashboard helper."""

import json
from pathlib import Path

from key4ce.__main__ import _build_class_dashboard


def test_class_dashboard_podium_and_at_risk(tmp_path: Path):
    a = tmp_path / "a.json"
    b = tmp_path / "b.json"
    a.write_text(json.dumps({"sessions": [{"wpm": 60, "accuracy": 96}, {"wpm": 58, "accuracy": 95}]}), encoding="utf-8")
    b.write_text(json.dumps({"sessions": [{"wpm": 35, "accuracy": 89}]}), encoding="utf-8")

    out = _build_class_dashboard([str(a), str(b)])
    assert out["students"] == 2
    assert out["podium"][0]["snapshot"] == "a.json"
    assert any(row["snapshot"] == "b.json" for row in out["at_risk"])
