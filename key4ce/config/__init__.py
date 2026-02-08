"""Configuration management for Key4ce."""

from key4ce.config.manager import ConfigManager, get_config
from key4ce.config.defaults import DEFAULT_SETTINGS, DEFAULT_THEMES, DEFAULT_ANIMATIONS

__all__ = ["ConfigManager", "get_config", "DEFAULT_SETTINGS", "DEFAULT_THEMES", "DEFAULT_ANIMATIONS"]
