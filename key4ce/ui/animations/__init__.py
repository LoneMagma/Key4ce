"""Animation system for Key4ce."""

from key4ce.ui.animations.base import Animation, AnimationManager
from key4ce.ui.animations.effects import CursorBlink, ProgressWave, LoadingSpinner

__all__ = ["Animation", "AnimationManager", "CursorBlink", "ProgressWave", "LoadingSpinner"]
