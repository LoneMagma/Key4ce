"""Tests for install.py helper logic."""

import importlib.util
from pathlib import Path


def _load_install_module():
    path = Path(__file__).resolve().parents[1] / "install.py"
    spec = importlib.util.spec_from_file_location("key4ce_install", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_install_version_ok_returns_bool():
    mod = _load_install_module()
    assert isinstance(mod.version_ok(), bool)
