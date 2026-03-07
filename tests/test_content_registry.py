"""Tests for provider registry."""

from key4ce.content.base import ProviderRegistry
from key4ce.content.builtin import BuiltinContent


def test_registry_register_and_get():
    reg = ProviderRegistry()
    p = BuiltinContent()
    reg.register(p)
    assert reg.get("builtin") is p


def test_registry_availability_snapshot_contains_provider():
    reg = ProviderRegistry()
    reg.register(BuiltinContent())
    rows = reg.availability_snapshot()
    assert any(r["source_type"] == "builtin" for r in rows)
