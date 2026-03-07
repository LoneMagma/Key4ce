"""
key4ce/ui/app.py
─────────────────
Main application shell.

Orchestrates: menu -> content load -> typing session -> results -> loop

__main__.py calls:
    App(theme=..., mode=..., zen=..., word_target=...).run()

All kwargs are optional with safe defaults so the app also works when
launched bare (App().run()) or from the menu directly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rich.console import Console

# ── Screen imports ────────────────────────────────────────────────
from key4ce.ui.screens.menu      import run_menu, get_palette, _load, _save, PROFILE_F
from key4ce.ui.screens.typing    import run_typing_session
from key4ce.ui.screens.results   import run_results
from key4ce.ui.screens.analytics import run_analytics

# ── Content loader (defensive) ────────────────────────────────────
try:
    from key4ce.content.loader  import load_content
    _LOADER_AVAILABLE = True
except ImportError:
    _LOADER_AVAILABLE = False

try:
    from key4ce.content.builtin import get_builtin_text
    _BUILTIN_AVAILABLE = True
except ImportError:
    _BUILTIN_AVAILABLE = False

try:
    from key4ce.content.focus import generate_focus_text
    _FOCUS_AVAILABLE = True
except ImportError:
    _FOCUS_AVAILABLE = False


# ── Text loader ───────────────────────────────────────────────────

def _load_text(profile: dict) -> str:
    mode   = profile.get("mode", "words")
    length = int(profile.get("words", 50))

    # Focus drill
    if mode == "focus" and _FOCUS_AVAILABLE:
        try:
            return generate_focus_text(length)
        except Exception:
            pass

    # External loader (wikipedia, live quotes, etc.)
    if _LOADER_AVAILABLE:
        try:
            text = load_content(mode, length)
            if text and len(text.strip()) > 10:
                return text
        except Exception:
            pass

    # Built-in pools
    if _BUILTIN_AVAILABLE:
        return get_builtin_text(mode, length)

    # Emergency fallback — no imports needed
    import random
    FALLBACK = (
        "the quick brown fox jumps over the lazy dog "
        "pack my box with five dozen liquor jugs "
        "how vexingly quick daft zebras jump "
        "the five boxing wizards jump quickly "
        "sphinx of black quartz judge my vow "
    )
    words = FALLBACK.split()
    return " ".join(random.choices(words, k=length))


# ═════════════════════════════════════════════════════════════════
#  App class
# ═════════════════════════════════════════════════════════════════

class App:
    """
    Main application class.

    Accepts all keyword arguments that __main__.py may pass so that
    CLI flags (--theme, --mode, --zen, --words) are honoured without
    requiring the user to go through the menu first.

    Parameters
    ----------
    theme       : colour theme name  (e.g. "cyberpunk", "nord")
    mode        : content mode       (e.g. "words", "sentences", "code")
    zen         : hide live stats during the session
    word_target : approximate number of words per session
    """

    def __init__(
        self,
        theme:       str  = "",
        mode:        str  = "",
        zen:         bool = False,
        word_target: int  = 0,
        # legacy / alternative kwarg names __main__.py might use
        words:       int  = 0,
        content:     str  = "",
        **_extra,           # absorb any future kwargs silently
    ) -> None:
        self.console = Console()

        # Load saved profile as base
        profile = _load(PROFILE_F, {
            "mode": "words", "words": 50, "theme": "cyberpunk", "zen": False,
        })

        # CLI flags override saved profile
        # theme may arrive as a Theme object or a plain string
        if theme:
            theme_name = getattr(theme, "name", None) or getattr(theme, "value", None) or str(theme)
            profile["theme"] = theme_name.lower()
        if mode:
            profile["mode"]  = mode.lower() if isinstance(mode, str) else str(mode).lower()
        if content:
            profile["mode"]  = content.lower() if isinstance(content, str) else str(content).lower()
        if zen:
            profile["zen"]   = True
        if word_target:
            profile["words"] = int(word_target)
        if words:
            profile["words"] = int(words)

        self._initial_profile = profile

        # Persist any CLI overrides back to profile file
        _save(PROFILE_F, profile)

    # ── Public entry point ────────────────────────────────────────

    def run(self) -> None:
        try:
            self._main_loop()
        except KeyboardInterrupt:
            self.console.clear()
            self.console.print("\n  Exiting Key4ce.\n")
            sys.exit(0)

    # ── Internal loop ─────────────────────────────────────────────

    def _main_loop(self) -> None:
        first_run = True

        while True:
            # On first run: if CLI gave us a mode, skip straight to session.
            # On subsequent loops: always go through menu.
            if first_run and self._initial_profile.get("mode") not in ("", "words"):
                config    = self._initial_profile.copy()
                first_run = False
            else:
                first_run = False
                config = run_menu(self.console)

            if config is None:
                self.console.clear()
                self.console.print("\n  Exiting Key4ce.\n")
                sys.exit(0)

            # Analytics shortcut from menu
            if config.get("_action") == "analytics":
                run_analytics(config, self.console)
                continue

            # Settings shortcut from menu
            if config.get("_action") == "settings":
                try:
                    from key4ce.ui.screens.settings import run_settings
                    run_settings(self.console)
                except ImportError:
                    pass
                continue

            # ── Session loop ──────────────────────────────────────
            profile = config
            action  = "start"

            while action not in ("menu", "quit"):
                if action == "focus":
                    profile = {**profile, "mode": "focus"}

                text  = _load_text(profile)
                state = run_typing_session(text, profile, self.console)

                if state is None:
                    break

                action = run_results(state, profile, self.console)

                if action == "quit":
                    self.console.clear()
                    self.console.print("\n  Exiting Key4ce.\n")
                    sys.exit(0)


# ── Module-level entry point ──────────────────────────────────────

def main() -> None:
    """Called by __main__.py when launching the UI directly."""
    App().run()
