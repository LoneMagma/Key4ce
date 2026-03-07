"""Tests for provider-health CLI helper."""

from dataclasses import dataclass
from datetime import datetime, timedelta

from key4ce.__main__ import _compute_provider_health


@dataclass
class _Session:
    ts: str
    source: str
    wpm: float
    accuracy: float


def test_provider_health_includes_builtin_and_external():
    now = datetime.now()
    rows = _compute_provider_health(
        [
            _Session(ts=(now - timedelta(days=1)).isoformat(), source="sentences", wpm=55, accuracy=95),
            _Session(ts=(now - timedelta(days=1)).isoformat(), source="wikipedia", wpm=48, accuracy=92),
        ],
        days=30,
    )
    providers = {r["provider"] for r in rows}
    assert "builtin" in providers
    assert "external" in providers


def test_provider_health_window_filtering():
    now = datetime.now()
    rows = _compute_provider_health(
        [
            _Session(ts=(now - timedelta(days=60)).isoformat(), source="sentences", wpm=55, accuracy=95),
        ],
        days=7,
    )
    builtin = next(r for r in rows if r["provider"] == "builtin")
    assert builtin["sessions"] == 0


def test_provider_health_marks_external_unavailable(monkeypatch):
    now = datetime.now()
    monkeypatch.setattr("key4ce.content.loader.external_provider_status", lambda: {"wikipedia": False, "quote": False})
    rows = _compute_provider_health(
        [_Session(ts=(now - timedelta(days=1)).isoformat(), source="wikipedia", wpm=48, accuracy=92)],
        days=30,
    )
    external = next(r for r in rows if r["provider"] == "external")
    assert external["available"] is False


def test_provider_health_includes_plugin_rows(monkeypatch):
    now = datetime.now()
    monkeypatch.setattr("key4ce.__main__._load_provider_plugins", lambda: [{"source_type": "custom", "available": True}])
    rows = _compute_provider_health(
        [_Session(ts=(now - timedelta(days=1)).isoformat(), source="sentences", wpm=55, accuracy=95)],
        days=30,
    )
    providers = {r["provider"] for r in rows}
    assert "custom" in providers
