"""Base animation classes for Key4ce.

Provides a configurable animation system where all effects
can be enabled/disabled via YAML configuration.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from key4ce.config import get_config


T = TypeVar("T")


def ease_in_out_cubic(t: float) -> float:
    """Cubic easing function for smooth animations.
    
    Args:
        t: Progress value from 0.0 to 1.0
        
    Returns:
        Eased value from 0.0 to 1.0
    """
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_elastic(t: float) -> float:
    """Elastic easing for bouncy effects.
    
    Args:
        t: Progress value from 0.0 to 1.0
        
    Returns:
        Eased value (may exceed 1.0 slightly)
    """
    if t == 0 or t == 1:
        return t
    
    import math
    c4 = (2 * math.pi) / 3
    return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation between two values.
    
    Args:
        start: Start value
        end: End value
        t: Progress from 0.0 to 1.0
        
    Returns:
        Interpolated value
    """
    return start + (end - start) * t


@dataclass
class AnimationState:
    """Current state of an animation."""
    is_running: bool = False
    progress: float = 0.0
    current_value: Any = None
    start_time: float = 0.0
    duration_ms: float = 0.0


class Animation(ABC):
    """Base class for all animations.
    
    All animations check their enabled state from config before running.
    """
    
    def __init__(self, category: str) -> None:
        """Initialize animation.
        
        Args:
            category: The config category (e.g., 'cursor', 'loading')
        """
        self._category = category
        self._state = AnimationState()
        self._config = get_config()
    
    @property
    def is_enabled(self) -> bool:
        """Check if this animation is enabled in config."""
        return self._config.is_animation_enabled(self._category)
    
    @property
    def is_running(self) -> bool:
        """Check if animation is currently running."""
        return self._state.is_running and self.is_enabled
    
    @property
    def progress(self) -> float:
        """Get current animation progress (0.0 to 1.0)."""
        return self._state.progress
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value for this animation.
        
        Args:
            key: Config key within the category
            default: Default value if not found
            
        Returns:
            Config value or default
        """
        return self._config.get_animation(self._category, key) or default
    
    def start(self) -> None:
        """Start the animation."""
        if not self.is_enabled:
            return
        
        self._state.is_running = True
        self._state.start_time = time.time()
        self._state.progress = 0.0
        self._on_start()
    
    def stop(self) -> None:
        """Stop the animation."""
        self._state.is_running = False
        self._state.progress = 0.0
        self._on_stop()
    
    def update(self) -> Any:
        """Update animation state and return current value.
        
        Returns:
            Current animation value (type depends on animation)
        """
        if not self.is_running:
            return self._get_default_value()
        
        # Calculate progress
        elapsed = (time.time() - self._state.start_time) * 1000
        
        if self._state.duration_ms > 0:
            self._state.progress = min(1.0, elapsed / self._state.duration_ms)
        
        # Get current value
        self._state.current_value = self._calculate_value()
        return self._state.current_value
    
    @abstractmethod
    def _calculate_value(self) -> Any:
        """Calculate the current animation value.
        
        Returns:
            Current value based on progress
        """
        pass
    
    def _get_default_value(self) -> Any:
        """Get the default value when animation is not running.
        
        Returns:
            Default value (override in subclass)
        """
        return None
    
    def _on_start(self) -> None:
        """Called when animation starts (override in subclass)."""
        pass
    
    def _on_stop(self) -> None:
        """Called when animation stops (override in subclass)."""
        pass


class LoopingAnimation(Animation):
    """Animation that loops continuously."""
    
    def __init__(self, category: str, cycle_ms: float) -> None:
        """Initialize looping animation.
        
        Args:
            category: Config category
            cycle_ms: Duration of one cycle in milliseconds
        """
        super().__init__(category)
        self._cycle_ms = cycle_ms
    
    def update(self) -> Any:
        """Update and loop the animation."""
        if not self.is_running:
            return self._get_default_value()
        
        # Calculate looping progress
        elapsed = (time.time() - self._state.start_time) * 1000
        self._state.progress = (elapsed % self._cycle_ms) / self._cycle_ms
        
        self._state.current_value = self._calculate_value()
        return self._state.current_value


class AnimationManager:
    """Manages multiple animations and their lifecycle."""
    
    def __init__(self) -> None:
        self._animations: dict[str, Animation] = {}
        self._running: set[str] = set()
    
    def register(self, name: str, animation: Animation) -> None:
        """Register an animation.
        
        Args:
            name: Unique name for the animation
            animation: Animation instance
        """
        self._animations[name] = animation
    
    def get(self, name: str) -> Animation | None:
        """Get a registered animation.
        
        Args:
            name: Animation name
            
        Returns:
            Animation instance or None
        """
        return self._animations.get(name)
    
    def start(self, name: str) -> None:
        """Start an animation by name.
        
        Args:
            name: Animation name
        """
        if name in self._animations:
            self._animations[name].start()
            self._running.add(name)
    
    def stop(self, name: str) -> None:
        """Stop an animation by name.
        
        Args:
            name: Animation name
        """
        if name in self._animations:
            self._animations[name].stop()
            self._running.discard(name)
    
    def stop_all(self) -> None:
        """Stop all running animations."""
        for name in list(self._running):
            self.stop(name)
    
    def update_all(self) -> dict[str, Any]:
        """Update all running animations.
        
        Returns:
            Dictionary of animation name to current value
        """
        values = {}
        for name in self._running:
            if name in self._animations:
                values[name] = self._animations[name].update()
        return values
    
    def is_running(self, name: str) -> bool:
        """Check if an animation is running.
        
        Args:
            name: Animation name
            
        Returns:
            True if running
        """
        return name in self._running and self._animations.get(name, None) is not None
