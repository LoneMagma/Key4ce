"""Progress bar and stats bar components."""
from __future__ import annotations

from rich.text import Text


def render_progress_bar(
    progress: float,
    width: int = 40,
    fill_colour: str = "#00ff9f",
    empty_colour: str = "#2a2a4a",
) -> Text:
    """Render a simple progress bar (0.0 - 1.0)."""
    filled = int(progress * width)
    empty = width - filled
    bar = Text()
    bar.append("█" * filled, style=fill_colour)
    bar.append("░" * empty, style=empty_colour)
    return bar


def render_stats_bar(
    wpm: float,
    accuracy: float,
    elapsed: float,
    progress: float,
    primary: str = "#00ff9f",
    secondary: str = "#00d4ff",
    muted: str = "#5a5a7a",
) -> Text:
    """Render the inline stats bar shown during a typing session."""
    mins = int(elapsed) // 60
    secs = int(elapsed) % 60
    time_str = f"{mins}:{secs:02d}"

    bar = Text()
    bar.append("  ", style="")

    # WPM
    bar.append(f"{wpm:5.1f}", style=f"bold {primary}")
    bar.append(" wpm", style=muted)

    bar.append("   ·   ", style=muted)

    # Accuracy
    bar.append(f"{accuracy:5.1f}", style=f"bold {secondary}")
    bar.append("%", style=muted)

    bar.append("   ·   ", style=muted)

    # Time
    bar.append(time_str, style=muted)

    bar.append("   ·   ", style=muted)

    # Progress bar (mini, 20-wide)
    filled = int(progress * 20)
    empty = 20 - filled
    bar.append("▓" * filled, style=primary)
    bar.append("░" * empty, style=muted)
    bar.append(f"  {int(progress * 100):3d}%", style=muted)

    return bar
