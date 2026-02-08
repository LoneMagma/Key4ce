"""Default configuration values for Key4ce.

These are used when no config file exists or as fallback values.
All defaults can be overridden via YAML config files.
"""

DEFAULT_SETTINGS = {
    "app": {
        "name": "Key4ce",
        "version": "1.0.0",
    },
    "display": {
        "theme": "cyberpunk",
        "animations_enabled": True,
        "background_effects": True,
    },
    "typing": {
        "show_ghost_racer": True,
        "combo_enabled": True,
        "show_live_wpm": True,
        "show_progress_bar": True,
    },
    "content": {
        "default_source": "builtin",
        "custom_texts_path": "./texts",
    },
    "sound": {
        "enabled": False,
        "volume": 0.5,
    },
    "onboarding": {
        "completed": False,
        "show_tips": True,
    },
}

DEFAULT_THEMES = {
    "themes": {
        "cyberpunk": {
            "background": "#0a0e27",
            "surface": "#151b3d",
            "primary": "#00ff9f",
            "secondary": "#ff006a",
            "accent": "#00d4ff",
            "text": "#e0e0e0",
            "text_dim": "#6b7280",
            "error": "#ff4444",
            "success": "#00ff9f",
            "warning": "#ffaa00",
        },
        "nord": {
            "background": "#2e3440",
            "surface": "#3b4252",
            "primary": "#88c0d0",
            "secondary": "#81a1c1",
            "accent": "#a3be8c",
            "text": "#eceff4",
            "text_dim": "#4c566a",
            "error": "#bf616a",
            "success": "#a3be8c",
            "warning": "#ebcb8b",
        },
        "dracula": {
            "background": "#282a36",
            "surface": "#44475a",
            "primary": "#bd93f9",
            "secondary": "#ff79c6",
            "accent": "#50fa7b",
            "text": "#f8f8f2",
            "text_dim": "#6272a4",
            "error": "#ff5555",
            "success": "#50fa7b",
            "warning": "#ffb86c",
        },
        "monokai": {
            "background": "#272822",
            "surface": "#3e3d32",
            "primary": "#66d9ef",
            "secondary": "#a6e22e",
            "accent": "#f92672",
            "text": "#f8f8f2",
            "text_dim": "#75715e",
            "error": "#f92672",
            "success": "#a6e22e",
            "warning": "#fd971f",
        },
        "midnight": {
            "background": "#0d1117",
            "surface": "#161b22",
            "primary": "#58a6ff",
            "secondary": "#79c0ff",
            "accent": "#56d364",
            "text": "#c9d1d9",
            "text_dim": "#484f58",
            "error": "#f85149",
            "success": "#56d364",
            "warning": "#d29922",
        },
    }
}

DEFAULT_ANIMATIONS = {
    "cursor": {
        "enabled": True,
        "style": "block",  # block, underline, bar
        "blink_rate_ms": 530,
        "color": "primary",
    },
    "progress_bar": {
        "enabled": True,
        "style": "wave",  # solid, wave, pulse
        "fill_char": "\u2593",  # ▓
        "empty_char": "\u2591",  # ░
        "animation_speed_ms": 100,
    },
    "loading": {
        "enabled": True,
        "style": "pipe_flow",  # pipe_flow, dots, spinner
        "characters": ["\u2588", "\u2593", "\u2592", "\u2591"],  # █▓▒░
        "speed_ms": 80,
    },
    "transitions": {
        "enabled": True,
        "style": "fade",  # fade, slide, instant
        "duration_ms": 200,
    },
    "background": {
        "enabled": True,
        "style": "subtle_pulse",  # subtle_pulse, matrix_rain, particles, none
        "intensity": 0.2,  # 0.0 to 1.0
        "color": "primary",
    },
    "typing": {
        "correct_flash": True,
        "error_shake": True,
        "combo_glow": True,
    },
}
