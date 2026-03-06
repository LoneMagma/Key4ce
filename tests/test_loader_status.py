"""Tests for external provider availability helper."""

from key4ce.content import loader


def test_external_provider_status_uses_fetch_json(monkeypatch):
    calls = []

    def fake_fetch(url: str):
        calls.append(url)
        return {"ok": True}

    monkeypatch.setattr(loader, "_fetch_json", fake_fetch)
    status = loader.external_provider_status()

    assert status == {"wikipedia": True, "quote": True}
    assert len(calls) == 2
