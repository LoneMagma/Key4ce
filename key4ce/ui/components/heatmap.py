"""ASCII keyboard heatmap component."""
from __future__ import annotations

from rich.text import Text

from key4ce.themes.themes import Theme

# Standard keyboard rows (lowercase)
_ROWS = [
    list("qwertyuiop"),
    list("asdfghjkl"),
    list("zxcvbnm"),
]
_ROW_INDENT = ["", " ", "  "]  # left-pad per row


def _brightness(count: int, max_count: int) -> str:
    """Return a block character based on relative frequency."""
    if max_count == 0 or count == 0:
        return "░"
    ratio = count / max_count
    if ratio >= 0.75:
        return "█"
    if ratio >= 0.5:
        return "▓"
    if ratio >= 0.25:
        return "▒"
    return "░"


def render_heatmap(
    key_counts: dict[str, int],
    theme: Theme,
    show_keys: bool = True,
) -> list[Text]:
    """Render an ASCII keyboard heatmap.

    Args:
        key_counts: Mapping of lowercase char → hit count.
        theme: Active colour theme.
        show_keys: If True show alpha labels; if False show only heat blocks.

    Returns:
        List of rich Text lines (one per keyboard row + legend).
    """
    counts = {k.lower(): v for k, v in key_counts.items() if k.isalpha()}
    max_count = max(counts.values()) if counts else 1

    lines: list[Text] = []

    for row_idx, row in enumerate(_ROWS):
        line = Text()
        line.append("  " + _ROW_INDENT[row_idx], style="")

        for key in row:
            cnt = counts.get(key, 0)
            block = _brightness(cnt, max_count)

            if cnt == 0:
                colour = theme.dim
            elif cnt / max_count >= 0.75:
                colour = theme.primary
            elif cnt / max_count >= 0.4:
                colour = theme.secondary
            else:
                colour = theme.text_muted

            if show_keys:
                # e.g. "e " with background block indication via colour
                line.append(f"{key.upper()} ", style=f"bold {colour}")
            else:
                line.append(f"{block} ", style=colour)

        lines.append(line)

    # Legend row
    legend = Text()
    legend.append("  ", style="")
    legend.append("░ ", style=theme.dim)
    legend.append("rare  ", style=theme.text_muted)
    legend.append("▒ ", style=theme.text_muted)
    legend.append("medium  ", style=theme.text_muted)
    legend.append("▓ ", style=theme.secondary)
    legend.append("frequent  ", style=theme.text_muted)
    legend.append("█ ", style=theme.primary)
    legend.append("dominant", style=theme.text_muted)
    lines.append(Text(""))
    lines.append(legend)

    return lines


def counts_from_timeline(keystrokes: list) -> dict[str, int]:
    """Derive key_counts from a list of Keystroke objects."""
    counts: dict[str, int] = {}
    for k in keystrokes:
        if k.is_correct and len(k.char) == 1 and k.char.isalpha():
            counts[k.char.lower()] = counts.get(k.char.lower(), 0) + 1
    return counts
