"""Tests for HTTP remote sync helper."""

import json
from pathlib import Path

from key4ce.__main__ import _sync_remote_snapshot


class _Resp:
    def __init__(self, payload: str, status: int = 200):
        self._payload = payload.encode("utf-8")
        self.status = status

    def read(self):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_sync_remote_pull(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: _Resp('{"sessions": []}'))
    out_path = tmp_path / "snap.json"
    out = _sync_remote_snapshot("https://example.org/snapshot", mode="pull", path=str(out_path))
    assert out["ok"] is True
    assert json.loads(out_path.read_text(encoding="utf-8"))["sessions"] == []


def test_sync_remote_push(monkeypatch, tmp_path: Path):
    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: _Resp("{}", status=204))
    out_path = tmp_path / "snap.json"
    out_path.write_text(json.dumps({"sessions": []}), encoding="utf-8")
    out = _sync_remote_snapshot("https://example.org/snapshot", mode="push", path=str(out_path))
    assert out["ok"] is True
    assert out["status"] == 204
