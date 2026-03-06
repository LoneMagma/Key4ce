"""Tests for profile preference helpers."""

from pathlib import Path

from key4ce.__main__ import _load_profile, _save_profile, _set_profile


def test_profile_defaults_when_missing(tmp_path: Path):
    p = tmp_path / "profile.json"
    data = _load_profile(p)
    assert data["preferred_mode"] == "sentences"
    assert data["preferred_words"] == 50


def test_profile_save_and_reload(tmp_path: Path):
    p = tmp_path / "profile.json"
    _save_profile({"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"}, p)
    data = _load_profile(p)
    assert data == {"preferred_mode": "words", "preferred_words": 25, "preferred_theme": "minimal"}


def test_set_profile_updates_values(tmp_path: Path, monkeypatch):
    p = tmp_path / "profile.json"
    monkeypatch.setattr("key4ce.__main__.PROFILE_PATH", p)
    out = _set_profile(preferred_mode="code", preferred_words=80, preferred_theme="nord")
    assert out["preferred_mode"] == "code"
    assert out["preferred_words"] == 80
    assert out["preferred_theme"] == "nord"
