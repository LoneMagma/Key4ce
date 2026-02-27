"""App shell — Phase 2 (zen, focus, ghost racer, theme switching, external content)."""
from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

import readchar
from rich.console import Console
from rich.live import Live

from key4ce.core.analyzer import SessionAnalysis, analyse
from key4ce.core.engine import TypingEngine
from key4ce.content.builtin import get_text
from key4ce.data.db import Database, FocusData
from key4ce.themes.themes import Theme, DEFAULT_THEME, get_theme


# ── Screen action protocol ─────────────────────────────────────────────────────

class _Kind(Enum):
    POP = auto()
    START_SESSION = auto()
    SESSION_COMPLETE = auto()
    RETRY = auto()
    GO_MENU = auto()
    QUIT = auto()
    CHANGE_THEME = auto()
    FOCUS_FROM_RESULTS = auto()


@dataclass
class ScreenAction:
    kind: _Kind
    payload: dict = field(default_factory=dict)

    @staticmethod
    def pop() -> "ScreenAction":
        return ScreenAction(_Kind.POP)

    @staticmethod
    def quit() -> "ScreenAction":
        return ScreenAction(_Kind.QUIT)

    @staticmethod
    def start_session(category: str, word_target: int) -> "ScreenAction":
        return ScreenAction(_Kind.START_SESSION, {"category": category, "word_target": word_target})

    @staticmethod
    def session_complete(engine: TypingEngine, source: str) -> "ScreenAction":
        return ScreenAction(_Kind.SESSION_COMPLETE, {"engine": engine, "source": source})

    @staticmethod
    def retry() -> "ScreenAction":
        return ScreenAction(_Kind.RETRY)

    @staticmethod
    def go_menu() -> "ScreenAction":
        return ScreenAction(_Kind.GO_MENU)

    @staticmethod
    def change_theme(name: str) -> "ScreenAction":
        return ScreenAction(_Kind.CHANGE_THEME, {"theme_name": name})

    @staticmethod
    def focus_from_results(analysis: SessionAnalysis) -> "ScreenAction":
        return ScreenAction(_Kind.FOCUS_FROM_RESULTS, {"analysis": analysis})


# ── App ────────────────────────────────────────────────────────────────────────

class App:
    FPS = 24

    def __init__(
        self,
        theme: Theme = DEFAULT_THEME,
        zen_mode: bool = False,
        skip_to_category: str | None = None,
        word_target: int = 50,
    ) -> None:
        self.theme = theme
        self._zen = zen_mode
        self._skip_to = skip_to_category
        self._skip_word_target = word_target

        self.console = Console()
        self.db = Database()

        self._stack: list[Any] = []
        self._key_queue: queue.Queue[str] = queue.Queue()
        self._running = False

        self._last_category = "sentences"
        self._last_word_target = 50
        self._last_text: str | None = None

    # ── Entry point ───────────────────────────────────────────────────────────

    def run(self) -> None:
        self.db.connect()
        try:
            self._running = True

            if self._skip_to:
                # CLI --mode flag: jump straight to typing
                self._last_category = self._skip_to
                self._last_word_target = self._skip_word_target
                text = self._load_text(self._skip_to, self._skip_word_target)
                self._push_typing(text, self._skip_to, zen=self._zen)
            else:
                self._push_menu()

            t = threading.Thread(target=self._input_loop, daemon=True)
            t.start()

            with Live(
                console=self.console,
                refresh_per_second=self.FPS,
                screen=True,
                transient=True,
            ) as live:
                while self._running and self._stack:
                    while not self._key_queue.empty():
                        try:
                            key = self._key_queue.get_nowait()
                        except queue.Empty:
                            break
                        self._dispatch_key(key)
                        if not self._running:
                            break

                    if self._stack:
                        try:
                            live.update(self._stack[-1].render())
                        except Exception:
                            pass

                    time.sleep(1 / self.FPS)
        finally:
            self.db.close()

    # ── Input thread ──────────────────────────────────────────────────────────

    def _input_loop(self) -> None:
        while self._running:
            try:
                key = readchar.readkey()
                if self._running:
                    self._key_queue.put(key)
            except Exception:
                break

    # ── Dispatch ──────────────────────────────────────────────────────────────

    def _dispatch_key(self, key: str) -> None:
        if not self._stack:
            return
        action: Optional[ScreenAction] = self._stack[-1].handle_key(key)
        if action:
            self._handle_action(action)

    def _handle_action(self, action: ScreenAction) -> None:
        k = action.kind

        if k == _Kind.QUIT:
            self._running = False

        elif k == _Kind.POP:
            if len(self._stack) > 1:
                self._stack.pop()

        elif k == _Kind.GO_MENU:
            self._stack.clear()
            self._push_menu()

        elif k == _Kind.CHANGE_THEME:
            self.theme = get_theme(action.payload["theme_name"])
            # Rebuild menu with new theme
            self._stack.clear()
            self._push_menu()

        elif k == _Kind.START_SESSION:
            cat = action.payload["category"]
            wt = action.payload["word_target"]
            self._last_category = cat
            self._last_word_target = wt
            text = self._load_text(cat, wt)
            self._last_text = text
            self._push_typing(text, cat)

        elif k == _Kind.SESSION_COMPLETE:
            self._finish_session(action.payload["engine"], action.payload["source"])

        elif k == _Kind.RETRY:
            text = self._last_text or self._load_text(self._last_category, self._last_word_target)
            while len(self._stack) > 1:
                self._stack.pop()
            self._push_typing(text, self._last_category)

        elif k == _Kind.FOCUS_FROM_RESULTS:
            analysis: SessionAnalysis = action.payload["analysis"]
            weak_dgs = [d.digraph for d in analysis.slow_digraphs[:3]]
            prob_keys = analysis.problem_keys[:3]
            from key4ce.content.focus import generate_focus_text
            text = generate_focus_text(weak_dgs, prob_keys, self._last_word_target)
            self._last_category = "focus"
            self._last_text = text
            while len(self._stack) > 1:
                self._stack.pop()
            self._push_typing(text, "focus")

    # ── Screen constructors ───────────────────────────────────────────────────

    def _push_menu(self) -> None:
        from key4ce.ui.screens.menu import MenuScreen
        stats = self.db.get_stats()
        stats_line = ""
        if stats.total_sessions > 0:
            stats_line = (
                f"best {stats.best_wpm:.0f} wpm  ·  "
                f"{stats.avg_wpm:.0f} avg  ·  "
                f"{stats.total_sessions} sessions"
            )

        focus_data = self.db.get_focus_data()
        focus_hint = ""
        if focus_data.weak_digraphs or focus_data.problem_chars:
            parts = []
            if focus_data.weak_digraphs:
                parts.append("digraphs: " + ", ".join(f"'{d}'" for d in focus_data.weak_digraphs[:2]))
            if focus_data.problem_chars:
                parts.append("keys: " + ", ".join(f"'{c}'" for c in focus_data.problem_chars[:2]))
            focus_hint = "  ·  ".join(parts)

        self._stack.append(MenuScreen(self.theme, stats_line, focus_hint))

    def _push_typing(self, text: str, source: str, zen: bool = False) -> None:
        from key4ce.ui.screens.typing import TypingScreen
        ghost = self.db.get_ghost_timings(source)
        self._stack.append(
            TypingScreen(text, source, self.theme, zen_mode=zen or self._zen, ghost_timings=ghost)
        )

    def _finish_session(self, engine: TypingEngine, source: str) -> None:
        from key4ce.ui.screens.results import ResultsScreen

        analysis = analyse(engine.timeline)

        # Build timings list from timeline
        prev_ts: float | None = None
        timings: list[int] = []
        for k in engine.timeline.keystrokes:
            if k.is_correct:
                if prev_ts is not None:
                    timings.append(max(0, int((k.timestamp - prev_ts) * 1000)))
                prev_ts = k.timestamp

        self.db.save_session(
            source=source,
            wpm=analysis.wpm,
            accuracy=analysis.accuracy,
            duration=analysis.duration_sec,
            chars_typed=analysis.chars_typed,
            errors=analysis.error_log,
            timings=timings,
        )

        pb = self.db.get_best_wpm_for_source(source)
        actual_pb = max(pb, analysis.wpm)

        self._stack.append(
            ResultsScreen(
                analysis,
                source,
                actual_pb,
                self.theme,
                keystrokes=engine.timeline.keystrokes,
            )
        )

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_text(self, category: str, word_target: int) -> str:
        """Load text for category, falling back to builtin on network failure."""
        from key4ce.content.loader import EXTERNAL_CATEGORIES, get_external_text
        from key4ce.content.focus import generate_focus_text

        if category == "focus":
            focus_data = self.db.get_focus_data()
            return generate_focus_text(
                focus_data.weak_digraphs, focus_data.problem_chars, word_target
            )
        if category in EXTERNAL_CATEGORIES:
            text = get_external_text(category, bust_cache=True)
            if text:
                return text
            # Fallback: use sentences
            return get_text("sentences", word_target)
        return get_text(category, word_target)
