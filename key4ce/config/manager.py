"""Configuration manager for Key4ce.

Handles loading, saving, and merging configuration from YAML files.
Supports platform-appropriate config locations and hot-reload.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

import yaml

from key4ce.config.defaults import (
    DEFAULT_SETTINGS,
    DEFAULT_THEMES,
    DEFAULT_ANIMATIONS,
)


def get_config_dir() -> Path:
    """Get the platform-appropriate configuration directory.
    
    Returns:
        Path to the config directory:
        - Windows: %APPDATA%/Key4ce
        - macOS: ~/Library/Application Support/Key4ce
        - Linux: ~/.config/key4ce
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / "Key4ce"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Key4ce"
    else:
        # Linux and other Unix-like systems
        xdg_config = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        return Path(xdg_config) / "key4ce"


def get_data_dir() -> Path:
    """Get the platform-appropriate data directory.
    
    Returns:
        Path to the data directory (for database, sessions, etc.)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Key4ce"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Key4ce"
    else:
        xdg_data = os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        return Path(xdg_data) / "key4ce"


def deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries, with override taking precedence.
    
    Args:
        base: Base dictionary with defaults
        override: Dictionary with overrides
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """Manages application configuration with YAML file support."""
    
    def __init__(self) -> None:
        self._config_dir = get_config_dir()
        self._data_dir = get_data_dir()
        
        # Ensure directories exist
        self._config_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        
        # Config file paths
        self._settings_file = self._config_dir / "settings.yaml"
        self._themes_file = self._config_dir / "themes.yaml"
        self._animations_file = self._config_dir / "animations.yaml"
        
        # Loaded configuration (with defaults merged)
        self._settings: dict[str, Any] = {}
        self._themes: dict[str, Any] = {}
        self._animations: dict[str, Any] = {}
        
        # Load on init
        self.reload()
    
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return self._data_dir
    
    @property
    def database_path(self) -> Path:
        """Get the database file path."""
        return self._data_dir / "key4ce.db"
    
    @property
    def settings(self) -> dict[str, Any]:
        """Get current settings."""
        return self._settings
    
    @property
    def themes(self) -> dict[str, Any]:
        """Get available themes."""
        return self._themes
    
    @property
    def animations(self) -> dict[str, Any]:
        """Get animation configuration."""
        return self._animations
    
    def get_current_theme(self) -> dict[str, str]:
        """Get the currently selected theme colors."""
        theme_name = self._settings.get("display", {}).get("theme", "cyberpunk")
        themes_dict = self._themes.get("themes", {})
        return themes_dict.get(theme_name, themes_dict.get("cyberpunk", {}))
    
    def reload(self) -> None:
        """Reload all configuration from files."""
        self._settings = self._load_yaml(self._settings_file, DEFAULT_SETTINGS)
        self._themes = self._load_yaml(self._themes_file, DEFAULT_THEMES)
        self._animations = self._load_yaml(self._animations_file, DEFAULT_ANIMATIONS)
    
    def _load_yaml(self, path: Path, defaults: dict) -> dict:
        """Load a YAML file and merge with defaults.
        
        Args:
            path: Path to the YAML file
            defaults: Default values to use
            
        Returns:
            Merged configuration dictionary
        """
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                return deep_merge(defaults, user_config)
            except (yaml.YAMLError, OSError):
                # If there's an error, use defaults
                return defaults.copy()
        return defaults.copy()
    
    def save_settings(self) -> None:
        """Save current settings to YAML file."""
        self._save_yaml(self._settings_file, self._settings)
    
    def save_all(self) -> None:
        """Save all configuration files."""
        self._save_yaml(self._settings_file, self._settings)
        self._save_yaml(self._themes_file, self._themes)
        self._save_yaml(self._animations_file, self._animations)
    
    def _save_yaml(self, path: Path, data: dict) -> None:
        """Save dictionary to YAML file.
        
        Args:
            path: Path to save to
            data: Dictionary to save
        """
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True)
    
    def create_default_configs(self) -> None:
        """Create default config files if they don't exist."""
        if not self._settings_file.exists():
            self._save_yaml(self._settings_file, DEFAULT_SETTINGS)
        if not self._themes_file.exists():
            self._save_yaml(self._themes_file, DEFAULT_THEMES)
        if not self._animations_file.exists():
            self._save_yaml(self._animations_file, DEFAULT_ANIMATIONS)
    
    def get_animation(self, category: str, key: str | None = None) -> Any:
        """Get animation configuration value.
        
        Args:
            category: Animation category (e.g., 'cursor', 'loading')
            key: Optional specific key within category
            
        Returns:
            Animation configuration value or category dict
        """
        category_config = self._animations.get(category, {})
        if key is None:
            return category_config
        return category_config.get(key)
    
    def is_animation_enabled(self, category: str) -> bool:
        """Check if a specific animation category is enabled.
        
        Args:
            category: Animation category name
            
        Returns:
            True if animations are enabled globally and for this category
        """
        global_enabled = self._settings.get("display", {}).get("animations_enabled", True)
        category_enabled = self._animations.get(category, {}).get("enabled", True)
        return global_enabled and category_enabled
    
    def update_setting(self, *path: str, value: Any) -> None:
        """Update a nested setting value.
        
        Args:
            *path: Path to the setting (e.g., 'display', 'theme')
            value: New value to set
        """
        if len(path) < 1:
            return
        
        current = self._settings
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value


# Global config instance
_config: ConfigManager | None = None


def get_config() -> ConfigManager:
    """Get the global configuration manager instance.
    
    Returns:
        The ConfigManager singleton
    """
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
