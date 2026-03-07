"""Tests for provider config validation."""

import json
from pathlib import Path

from key4ce.__main__ import _validate_provider_plugins


def test_validate_plugins_success(tmp_path: Path):
    p = tmp_path / "providers.json"
    p.write_text(json.dumps({"providers": [{"source_type": "school", "name": "School Feed", "enabled": True, "endpoint": "https://example.org/feed"}]}), encoding="utf-8")
    out = _validate_provider_plugins(p)
    assert out["exists"] is True
    assert len(out["valid"]) == 1
    assert out["errors"] == []


def test_validate_plugins_invalid_endpoint(tmp_path: Path):
    p = tmp_path / "providers.json"
    p.write_text(json.dumps([{"source_type": "x", "endpoint": "ftp://bad"}]), encoding="utf-8")
    out = _validate_provider_plugins(p)
    assert len(out["valid"]) == 0
    assert out["errors"][0]["reason"].startswith("endpoint")
