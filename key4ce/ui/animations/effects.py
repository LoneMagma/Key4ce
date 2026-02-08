"""Built-in animation effects for Key4ce.

All effects are configurable via animations.yaml.
"""

from __future__ import annotations

import time
from typing import Any

from key4ce.ui.animations.base import Animation, LoopingAnimation, ease_in_out_cubic


class CursorBlink(LoopingAnimation):
    """Blinking cursor animation."""
    
    def __init__(self) -> None:
        cycle_ms = 530  # Default blink rate
        super().__init__("cursor", cycle_ms)
        
        # Update cycle from config
        config_rate = self.get_config_value("blink_rate_ms", 530)
        self._cycle_ms = config_rate
    
    def _calculate_value(self) -> bool:
        """Calculate if cursor should be visible.
        
        Returns:
            True if cursor should be shown
        """
        # Cursor visible for first half of cycle
        return self.progress < 0.5
    
    def _get_default_value(self) -> bool:
        """Default: cursor always visible."""
        return True
    
    def get_cursor_char(self) -> str:
        """Get the cursor character based on style config.
        
        Returns:
            Cursor character: block, underline, or bar
        """
        style = self.get_config_value("style", "block")
        
        if style == "block":
            return "\u2588"  # █
        elif style == "underline":
            return "_"
        elif style == "bar":
            return "|"
        else:
            return "\u2588"


class ProgressWave(LoopingAnimation):
    """Wave animation for progress bar."""
    
    def __init__(self) -> None:
        speed = 100  # Default animation speed
        super().__init__("progress_bar", speed * 10)  # Full cycle
        
        # Get config values
        config_speed = self.get_config_value("animation_speed_ms", 100)
        self._cycle_ms = config_speed * 10
        
        self._fill_char = self.get_config_value("fill_char", "\u2593")
        self._empty_char = self.get_config_value("empty_char", "\u2591")
    
    def _calculate_value(self) -> int:
        """Calculate the wave offset position.
        
        Returns:
            Offset for wave effect (0 to width)
        """
        # Wave position cycles through the bar
        return int(self.progress * 20)  # Assuming max width of 20
    
    def _get_default_value(self) -> int:
        """Default: no wave offset."""
        return 0
    
    def render(self, filled: int, total: int) -> str:
        """Render the progress bar with wave effect.
        
        Args:
            filled: Number of filled positions
            total: Total bar width
            
        Returns:
            Rendered progress bar string
        """
        style = self.get_config_value("style", "wave")
        
        if not self.is_enabled or style == "solid":
            # Simple solid bar
            return self._fill_char * filled + self._empty_char * (total - filled)
        
        # Wave/pulse effect
        result = []
        wave_offset = self.update()
        
        for i in range(total):
            if i < filled:
                # Filled section with wave brightness variation
                if style == "wave":
                    wave_pos = (i + wave_offset) % 4
                    chars = ["\u2588", "\u2593", "\u2592", "\u2591"]  # █▓▒░
                    result.append(chars[wave_pos])
                elif style == "pulse":
                    # Pulse between two chars
                    if self.progress < 0.5:
                        result.append("\u2588")
                    else:
                        result.append("\u2593")
                else:
                    result.append(self._fill_char)
            else:
                result.append(self._empty_char)
        
        return "".join(result)


class LoadingSpinner(LoopingAnimation):
    """Loading spinner animation."""
    
    # Built-in spinner styles
    STYLES = {
        "pipe_flow": ["\u2588", "\u2593", "\u2592", "\u2591"],  # █▓▒░
        "dots": [".", "..", "...", "...."],
        "spinner": ["|", "/", "-", "\\"],
        "braille": ["\u2801", "\u2803", "\u2807", "\u280f", "\u281f", "\u283f", "\u287f", "\u28ff"],
        "blocks": ["\u2596", "\u2598", "\u259d", "\u2597"],  # ▖▘▝▗
    }
    
    def __init__(self) -> None:
        speed = 80  # Default speed
        super().__init__("loading", speed * 4)
        
        config_speed = self.get_config_value("speed_ms", 80)
        self._cycle_ms = config_speed * 4
        
        # Get style
        style_name = self.get_config_value("style", "pipe_flow")
        self._chars = self.STYLES.get(style_name, self.STYLES["pipe_flow"])
        
        # Check for custom characters in config
        custom_chars = self.get_config_value("characters")
        if custom_chars:
            self._chars = custom_chars
    
    def _calculate_value(self) -> str:
        """Calculate current spinner character.
        
        Returns:
            Current character to display
        """
        idx = int(self.progress * len(self._chars)) % len(self._chars)
        return self._chars[idx]
    
    def _get_default_value(self) -> str:
        """Default: first character."""
        return self._chars[0] if self._chars else " "
    
    def render_with_text(self, text: str = "Loading") -> str:
        """Render spinner with optional text.
        
        Args:
            text: Text to display alongside spinner
            
        Returns:
            Formatted loading string
        """
        char = self.update()
        return f" {char} {text}..."


class FadeTransition(Animation):
    """Fade transition effect."""
    
    def __init__(self) -> None:
        super().__init__("transitions")
        self._state.duration_ms = self.get_config_value("duration_ms", 200)
        self._direction: str = "in"  # "in" or "out"
    
    def fade_in(self) -> None:
        """Start a fade-in transition."""
        self._direction = "in"
        self.start()
    
    def fade_out(self) -> None:
        """Start a fade-out transition."""
        self._direction = "out"
        self.start()
    
    def _calculate_value(self) -> float:
        """Calculate current opacity.
        
        Returns:
            Opacity from 0.0 to 1.0
        """
        eased = ease_in_out_cubic(self.progress)
        
        if self._direction == "out":
            return 1.0 - eased
        else:
            return eased
    
    def _get_default_value(self) -> float:
        """Default: fully visible."""
        return 1.0
    
    def get_visible_chars(self, text: str) -> str:
        """Get visible portion of text based on fade progress.
        
        For terminal-style fading, we reveal/hide characters.
        
        Args:
            text: Full text
            
        Returns:
            Visible portion of text
        """
        if not self.is_enabled:
            return text
        
        opacity = self.update()
        visible_count = int(len(text) * opacity)
        
        if self._direction == "in":
            return text[:visible_count]
        else:
            return text[:visible_count]


class BackgroundPulse(LoopingAnimation):
    """Subtle background pulse animation."""
    
    def __init__(self) -> None:
        super().__init__("background", 3000)  # 3 second cycle
        
        self._intensity = self.get_config_value("intensity", 0.2)
    
    def _calculate_value(self) -> float:
        """Calculate current background intensity.
        
        Returns:
            Intensity multiplier (around 1.0)
        """
        import math
        
        # Smooth sine wave oscillation
        wave = math.sin(self.progress * math.pi * 2)
        
        # Map to intensity range
        return 1.0 + (wave * self._intensity * 0.5)
    
    def _get_default_value(self) -> float:
        """Default: normal intensity."""
        return 1.0


class TypewriterEffect(Animation):
    """Typewriter reveal effect for text."""
    
    def __init__(self, text: str = "", chars_per_second: float = 30) -> None:
        super().__init__("typing")
        self._text = text
        self._chars_per_second = chars_per_second
        
        if text:
            self._state.duration_ms = (len(text) / chars_per_second) * 1000
    
    def set_text(self, text: str) -> None:
        """Set the text to reveal.
        
        Args:
            text: Text to animate
        """
        self._text = text
        self._state.duration_ms = (len(text) / self._chars_per_second) * 1000
    
    def _calculate_value(self) -> str:
        """Calculate visible text.
        
        Returns:
            Currently visible portion of text
        """
        char_count = int(len(self._text) * ease_in_out_cubic(self.progress))
        return self._text[:char_count]
    
    def _get_default_value(self) -> str:
        """Default: full text."""
        return self._text


class ComboFlash(Animation):
    """Flash effect for combo milestones."""
    
    def __init__(self) -> None:
        super().__init__("typing")
        self._state.duration_ms = 300
    
    def _calculate_value(self) -> bool:
        """Calculate if flash should be visible.
        
        Returns:
            True if currently flashing
        """
        # Quick flash pattern
        return self.progress < 0.3 or (0.4 < self.progress < 0.6)
    
    def _get_default_value(self) -> bool:
        """Default: not flashing."""
        return False
