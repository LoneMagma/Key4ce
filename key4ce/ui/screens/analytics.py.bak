"""Analytics dashboard screen with Groq recommendation + local fallback."""
from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from typing import TYPE_CHECKING

import readchar
from rich.align import Align
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.text import Text

from key4ce.data.db import SessionRecord, StatsSnapshot
from key4ce.themes.themes import Theme

if TYPE_CHECKING:
    from key4ce.ui.app import ScreenAction


@dataclass
class _Overview:
    avg_wpm: float
    avg_accuracy: float
    total_sessions: int
    best_wpm: float
    best_accuracy: float
    lowest_error_run: int


def _build_overview(stats: StatsSnapshot, sessions: list[SessionRecord]) -> _Overview:
    best_acc = max((float(s.accuracy) for s in sessions), default=0.0)
    low_errors = min((len(s.errors) for s in sessions), default=0)
    return _Overview(
        avg_wpm=float(stats.avg_wpm),
        avg_accuracy=float(stats.avg_accuracy),
        total_sessions=int(stats.total_sessions),
        best_wpm=float(stats.best_wpm),
        best_accuracy=float(best_acc),
        lowest_error_run=int(low_errors),
    )


def _fallback_recommendation(overview: _Overview, sessions: list[SessionRecord]) -> str:
    if overview.total_sessions == 0:
        return "Start with three short runs and prioritize 95%+ accuracy before increasing pace."

    recent = sessions[:5]
    recent_wpm = [float(s.wpm) for s in recent]
    recent_acc = [float(s.accuracy) for s in recent]
    recent_errors = [len(s.errors) for s in recent]

    avg_recent_wpm = sum(recent_wpm) / max(1, len(recent_wpm))
    avg_recent_acc = sum(recent_acc) / max(1, len(recent_acc))
    avg_recent_err = sum(recent_errors) / max(1, len(recent_errors))

    if avg_recent_acc < 93:
        return "Run medium sessions at controlled pace and target 96% accuracy before pushing speed."
    if avg_recent_err >= 5:
        return "Use short precision runs and pause briefly at word boundaries to reduce recurring errors."
    if avg_recent_wpm >= max(55.0, overview.avg_wpm) and avg_recent_acc < overview.avg_accuracy:
        return "Your speed is rising; hold pace for two sessions and stabilize accuracy above your average."
    return "Accuracy is stable. Increase pace by 3-5 WPM in long runs while keeping errors under control."


def _groq_recommendation(overview: _Overview, sessions: list[SessionRecord]) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return None

    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
        "temperature": 0.2,
        "max_tokens": 80,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a concise typing coach. Return exactly 1-2 lines, plain text, no bullets, "
                    "no emojis, actionable and specific."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(
                    {
                        "avg_wpm": overview.avg_wpm,
                        "avg_accuracy": overview.avg_accuracy,
                        "best_wpm": overview.best_wpm,
                        "best_accuracy": overview.best_accuracy,
                        "total_sessions": overview.total_sessions,
                        "recent": [
                            {
                                "wpm": float(s.wpm),
                                "accuracy": float(s.accuracy),
                                "errors": len(s.errors),
                                "duration": float(s.duration),
                            }
                            for s in sessions[:5]
                        ],
                    }
                ),
            },
        ],
    }

    req = urllib.request.Request(
        url="https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        content = body["choices"][0]["message"]["content"].strip()
        return " ".join(content.split())[:220]
    except Exception:
        return None


class AnalyticsScreen:
    """Performance analytics dashboard view."""

    def __init__(self, theme: Theme, stats: StatsSnapshot, sessions: list[SessionRecord]) -> None:
        self.theme = theme
        self.stats = stats
        self.sessions = sessions

    def render(self) -> object:
        t = self.theme
        overview = _build_overview(self.stats, self.sessions)
        rec = _groq_recommendation(overview, self.sessions) or _fallback_recommendation(overview, self.sessions)

        top = Text()
        top.append(" KEY4CE :: PERFORMANCE ANALYTICS", style=f"bold {t.primary}")
        top.append(f"    THEME: {t.name.upper()}", style=t.text_muted)

        overview_row = Columns(
            [
                Panel(f"{overview.avg_wpm:.1f}\nAverage WPM", title="Overview", border_style=t.dim, padding=(1, 2)),
                Panel(f"{overview.avg_accuracy:.1f}%\nAverage Accuracy", title="Overview", border_style=t.dim, padding=(1, 2)),
                Panel(f"{overview.total_sessions}\nTotal Sessions", title="Overview", border_style=t.dim, padding=(1, 2)),
            ],
            equal=True,
            expand=True,
        )

        highlights_row = Columns(
            [
                Panel(f"{overview.best_wpm:.1f}\nBest WPM", title="Highlights", border_style=t.dim, padding=(1, 2)),
                Panel(f"{overview.best_accuracy:.1f}%\nBest Accuracy", title="Highlights", border_style=t.dim, padding=(1, 2)),
                Panel(f"{overview.lowest_error_run} errors\nLowest Error Run", title="Highlights", border_style=t.dim, padding=(1, 2)),
            ],
            equal=True,
            expand=True,
        )

        trend_line = self._trend_line()

        recent_lines: list[Text] = []
        for i, s in enumerate(self.sessions[:5], start=1):
            line = Text()
            line.append(f" {i}. ", style=t.text_muted)
            line.append(f"WPM {float(s.wpm):.1f}   ", style=f"bold {t.primary}")
            line.append(f"Acc {float(s.accuracy):.1f}%   ", style=t.secondary)
            line.append(f"Errors {len(s.errors)}", style=t.text_muted)
            recent_lines.append(line)
        if not recent_lines:
            recent_lines.append(Text(" No sessions recorded yet.", style=t.text_muted))

        actions = Text()
        actions.append(" [R] ", style=f"bold {t.primary}")
        actions.append("Refresh   ", style=t.text_muted)
        actions.append("[B] ", style=f"bold {t.primary}")
        actions.append("Back   ", style=t.text_muted)
        actions.append("[Q] ", style=f"bold {t.primary}")
        actions.append("Quit", style=t.text_muted)

        content = Group(
            Align.left(top),
            Text(""),
            overview_row,
            Text(""),
            highlights_row,
            Text(""),
            Panel(Text(trend_line, style=t.text), title="Trend Summary", border_style=t.dim, padding=(1, 2)),
            Text(""),
            Panel(Text(rec, style=t.secondary), title="AI Recommendation", border_style=t.secondary, padding=(1, 2)),
            Text(""),
            Panel(Group(*recent_lines), title="Session Breakdown · Last 5 Runs", border_style=t.dim, padding=(1, 2)),
            Text(""),
            Align.center(actions),
        )

        return Panel(content, border_style=t.primary, padding=(1, 2), expand=True)

    def _trend_line(self) -> str:
        rows = self.sessions[:5]
        if len(rows) < 2:
            return "Build a baseline with at least two sessions to unlock trend analysis."

        wpm = [float(s.wpm) for s in rows]
        acc = [float(s.accuracy) for s in rows]
        dwpm = wpm[0] - wpm[-1]
        dacc = acc[0] - acc[-1]

        if dwpm > 3 and dacc < -0.5:
            return "Speed is improving, but accuracy is slipping slightly in faster runs."
        if dacc > 1 and abs(dwpm) < 2:
            return "Accuracy trend is improving with stable speed. You are building consistency."
        return "Recent sessions are stable. Increment pace carefully while maintaining error control."

    def handle_key(self, key: str) -> ScreenAction | None:
        from key4ce.ui.app import ScreenAction

        if key in ("b", "B", readchar.key.ESC):
            return ScreenAction.pop()
        if key in ("r", "R"):
            return ScreenAction.open_analytics()
        if key in ("q", "Q"):
            return ScreenAction.quit()
        return None
