"""ASCII WPM-over-time graph component."""
from __future__ import annotations

from rich.text import Text


def render_wpm_graph(
    buckets: list[float],
    width: int = 50,
    height: int = 6,
    primary_colour: str = "#00d4ff",
    muted_colour: str = "#3a3a5c",
) -> list[Text]:
    """Return a list of rich Text lines forming an ASCII line graph.

    Args:
        buckets: WPM values per time bucket.
        width:   Horizontal character width of the plot area.
        height:  Number of rows in the plot area.
        primary_colour: colour for the graph line/points.
        muted_colour:   colour for axis chars.

    Returns:
        List of Text objects, one per row (axis + plot area).
    """
    if not buckets or all(v == 0 for v in buckets):
        placeholder = Text("  no data yet", style=muted_colour)
        return [placeholder] * height

    max_wpm = max(buckets) or 1
    min_wpm = max(0.0, min(b for b in buckets if b > 0) - 5)

    # Normalise to height rows
    def _row(val: float) -> int:
        norm = (val - min_wpm) / max(max_wpm - min_wpm, 1)
        return max(0, min(height - 1, int((1 - norm) * (height - 1))))

    # Build grid: grid[row][col] = True means a point here
    grid = [[False] * len(buckets) for _ in range(height)]
    for col, val in enumerate(buckets):
        r = _row(val)
        grid[r][col] = True
        # Connect to previous point with vertical fill
        if col > 0:
            prev_r = _row(buckets[col - 1])
            lo, hi = min(r, prev_r), max(r, prev_r)
            for fill_r in range(lo, hi + 1):
                grid[fill_r][col] = True

    lines: list[Text] = []
    for row_idx in range(height):
        line = Text()
        # Y-axis label on leftmost
        wpm_label = max_wpm - (row_idx / max(height - 1, 1)) * (max_wpm - min_wpm)
        label = f"{int(wpm_label):3d}│"
        line.append(label, style=muted_colour)
        for col in range(len(buckets)):
            ch = "█" if grid[row_idx][col] else " "
            line.append(ch, style=primary_colour if ch == "█" else " ")
        lines.append(line)

    # X-axis
    x_line = Text()
    x_line.append("   └" + "─" * len(buckets) + "→", style=muted_colour)
    lines.append(x_line)

    return lines
