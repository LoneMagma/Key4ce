"""Entry point for key4ce — full argparse CLI."""
from __future__ import annotations

import sys


def _print_stats() -> None:
    """Print a stats summary table directly to stdout (no TUI)."""
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    t = DEFAULT_THEME
    db = Database()
    db.connect()
    stats = db.get_stats()
    db.close()

    console = Console()

    if stats.total_sessions == 0:
        console.print("[dim]No sessions recorded yet. Run key4ce and start typing![/dim]")
        return

    # Summary header
    console.print()
    console.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  stats", style="")
    console.print()
    console.print(f"  [bold]Best WPM[/bold]       {stats.best_wpm:.1f}")
    console.print(f"  [bold]Average WPM[/bold]    {stats.avg_wpm:.1f}")
    console.print(f"  [bold]Avg Accuracy[/bold]   {stats.avg_accuracy:.1f}%")
    console.print(f"  [bold]Sessions[/bold]       {stats.total_sessions}")
    console.print()

    if not stats.recent_sessions:
        return

    # Recent sessions table
    table = Table(
        "Date", "Source", "WPM", "Accuracy", "Duration",
        border_style=t.dim,
        header_style=f"bold {t.secondary}",
        show_edge=True,
    )

    for s in stats.recent_sessions:
        date_str = s.ts[:10]
        mins, secs = divmod(int(s.duration), 60)
        table.add_row(
            date_str,
            s.source,
            f"{s.wpm:.1f}",
            f"{s.accuracy:.1f}%",
            f"{mins}:{secs:02d}",
        )

    console.print(table)
    console.print()


def _print_stats_json() -> None:
    import json
    from key4ce.data.db import Database
    db = Database()
    db.connect()
    stats = db.get_stats()
    db.close()
    output = {
        "total_sessions": stats.total_sessions,
        "best_wpm": stats.best_wpm,
        "avg_wpm": stats.avg_wpm,
        "avg_accuracy": stats.avg_accuracy,
        "recent": [
            {
                "id": s.id,
                "ts": s.ts,
                "source": s.source,
                "wpm": s.wpm,
                "accuracy": s.accuracy,
                "duration": s.duration,
            }
            for s in stats.recent_sessions
        ],
    }
    print(json.dumps(output, indent=2))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="key4ce",
        description="A terminal typing trainer that actually makes you better.",
    )

    # -- Subcommands
    sub = parser.add_subparsers(dest="command")

    # stats subcommand
    stats_cmd = sub.add_parser("stats", help="Print session stats and exit (no TUI)")
    stats_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    # -- Global flags (for main TUI launch)
    parser.add_argument(
        "--theme",
        metavar="NAME",
        default=None,
        help="Colour theme: cyberpunk (default), nord, dracula, monokai, minimal",
    )
    parser.add_argument(
        "--zen",
        action="store_true",
        help="Zen mode — no stats during typing, stats shown only at end",
    )
    parser.add_argument(
        "--focus",
        action="store_true",
        help="Focus mode — generates text targeting your weak spots from recent sessions",
    )
    parser.add_argument(
        "--mode",
        metavar="CATEGORY",
        default=None,
        help="Skip menu and go straight to a session: words, sentences, quotes, code, numbers, wikipedia, quote",
    )
    parser.add_argument(
        "--words",
        type=int,
        default=50,
        metavar="N",
        help="Approximate word count for --mode / --focus sessions (default: 50)",
    )

    args = parser.parse_args()

    # ── stats subcommand (no TUI) ──────────────────────────────────────────────
    if args.command == "stats":
        if args.json:
            _print_stats_json()
        else:
            _print_stats()
        return

    # ── TUI launch ────────────────────────────────────────────────────────────
    from key4ce.themes.themes import get_theme, DEFAULT_THEME
    from key4ce.ui.app import App

    theme = get_theme(args.theme) if args.theme else DEFAULT_THEME

    skip_to: str | None = None
    if args.focus:
        skip_to = "focus"
    elif args.mode:
        skip_to = args.mode

    app = App(
        theme=theme,
        zen_mode=args.zen,
        skip_to_category=skip_to,
        word_target=args.words,
    )
    try:
        app.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
