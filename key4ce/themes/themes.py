"""Colour theme definitions for key4ce."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    name: str

    # Background layers
    bg: str          # main background
    bg_alt: str      # slightly lighter bg (panels, borders)

    # Accent colours (rich markup compatible)
    primary: str     # main accent (cursor highlight, selected items)
    secondary: str   # secondary accent (stats, labels)
    error: str       # errors
    dim: str         # already-typed text, hints

    # Text
    text: str        # normal text
    text_muted: str  # upcoming text in typing view

    # Graph / progress
    progress: str    # progress bar fill
    graph_line: str  # WPM graph line colour


# ── Default themes ────────────────────────────────────────────────────────────

CYBERPUNK = Theme(
    name="cyberpunk",
    bg="#0a0e27",
    bg_alt="#151b3d",
    primary="#00ff9f",
    secondary="#00d4ff",
    error="#ff4466",
    dim="#3a3a5c",
    text="#e0e0f0",
    text_muted="#555577",
    progress="#00ff9f",
    graph_line="#00d4ff",
)

NORD = Theme(
    name="nord",
    bg="#2e3440",
    bg_alt="#3b4252",
    primary="#88c0d0",
    secondary="#81a1c1",
    error="#bf616a",
    dim="#4c566a",
    text="#eceff4",
    text_muted="#4c566a",
    progress="#88c0d0",
    graph_line="#81a1c1",
)

DRACULA = Theme(
    name="dracula",
    bg="#282a36",
    bg_alt="#383a47",
    primary="#bd93f9",
    secondary="#ff79c6",
    error="#ff5555",
    dim="#44475a",
    text="#f8f8f2",
    text_muted="#6272a4",
    progress="#bd93f9",
    graph_line="#ff79c6",
)

MONOKAI = Theme(
    name="monokai",
    bg="#272822",
    bg_alt="#3e3d32",
    primary="#a6e22e",
    secondary="#66d9ef",
    error="#f92672",
    dim="#49483e",
    text="#f8f8f2",
    text_muted="#75715e",
    progress="#a6e22e",
    graph_line="#66d9ef",
)

MINIMAL = Theme(
    name="minimal",
    bg="#000000",
    bg_alt="#111111",
    primary="#ffffff",
    secondary="#aaaaaa",
    error="#ff4444",
    dim="#333333",
    text="#ffffff",
    text_muted="#444444",
    progress="#ffffff",
    graph_line="#888888",
)

ALL_THEMES: dict[str, Theme] = {
    t.name: t for t in [CYBERPUNK, NORD, DRACULA, MONOKAI, MINIMAL]
}

DEFAULT_THEME = CYBERPUNK


def get_theme(name: str) -> Theme:
    return ALL_THEMES.get(name, DEFAULT_THEME)
