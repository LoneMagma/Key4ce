"""Entry point for key4ce — full argparse CLI."""
from __future__ import annotations

import json
from pathlib import Path


def _summarize_recent_sessions(recent_sessions: list, days: int = 7) -> dict:
    """Build a compact summary for sessions in the last `days` days."""
    from datetime import datetime, timedelta

    cutoff = datetime.now() - timedelta(days=days)
    in_window = []
    for s in recent_sessions:
        try:
            ts = datetime.fromisoformat(s.ts)
        except Exception:
            continue
        if ts >= cutoff:
            in_window.append(s)

    if not in_window:
        return {
            "days": days,
            "sessions": 0,
            "avg_wpm": 0.0,
            "avg_accuracy": 0.0,
            "best_wpm": 0.0,
            "total_minutes": 0.0,
        }

    sessions = len(in_window)
    avg_wpm = sum(s.wpm for s in in_window) / sessions
    avg_accuracy = sum(s.accuracy for s in in_window) / sessions
    best_wpm = max(s.wpm for s in in_window)
    total_minutes = sum(s.duration for s in in_window) / 60

    return {
        "days": days,
        "sessions": sessions,
        "avg_wpm": round(avg_wpm, 1),
        "avg_accuracy": round(avg_accuracy, 1),
        "best_wpm": round(best_wpm, 1),
        "total_minutes": round(total_minutes, 1),
    }




def _sessions_to_jsonable(records: list) -> list[dict]:
    """Convert session records to serialisable dicts."""
    return [
        {
            "id": s.id,
            "ts": s.ts,
            "source": s.source,
            "wpm": s.wpm,
            "accuracy": s.accuracy,
            "duration": s.duration,
            "chars_typed": s.chars_typed,
            "errors": s.errors,
            "timings": s.timings,
        }
        for s in records
    ]


def _print_export_json(limit: int | None = None) -> None:
    """Export session history as JSON for backup/portability."""
    from key4ce.data.db import Database

    db = Database()
    db.connect()
    sessions = db.list_sessions(limit=limit)
    db.close()

    output = {
        "exported_at": __import__("datetime").datetime.now().isoformat(),
        "count": len(sessions),
        "sessions": _sessions_to_jsonable(sessions),
    }
    print(json.dumps(output, indent=2))



def _import_sessions_from_file(path: str) -> int:
    """Import sessions from an export JSON file and return inserted count."""
    from key4ce.data.db import Database

    data = json.loads(Path(path).read_text(encoding="utf-8"))
    sessions = data.get("sessions", []) if isinstance(data, dict) else []
    if not isinstance(sessions, list):
        sessions = []

    db = Database()
    db.connect()
    inserted = db.import_sessions(sessions)
    db.close()
    return inserted


def _print_stats() -> None:
    """Print a stats summary table directly to stdout (no TUI)."""
    from rich.console import Console
    from rich.table import Table
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
        "recent": _sessions_to_jsonable(stats.recent_sessions),
    }
    print(json.dumps(output, indent=2))


def _print_weekly_summary(days: int = 7, as_json: bool = False) -> None:
    """Print progress summary over the recent window."""
    from rich.console import Console
    from key4ce.data.db import Database
    from key4ce.themes.themes import DEFAULT_THEME

    t = DEFAULT_THEME
    db = Database()
    db.connect()
    stats = db.get_stats()
    db.close()

    summary = _summarize_recent_sessions(stats.recent_sessions, days=days)

    if as_json:
        print(json.dumps(summary, indent=2))
        return

    console = Console()
    console.print()
    console.print(f"  [bold {t.primary}]key4ce[/bold {t.primary}]  {days}-day summary")
    console.print()
    if summary["sessions"] == 0:
        console.print("  [dim]No sessions in this period yet.[/dim]")
        console.print()
        return

    console.print(f"  [bold]Sessions[/bold]       {summary['sessions']}")
    console.print(f"  [bold]Average WPM[/bold]    {summary['avg_wpm']:.1f}")
    console.print(f"  [bold]Avg Accuracy[/bold]   {summary['avg_accuracy']:.1f}%")
    console.print(f"  [bold]Best WPM[/bold]       {summary['best_wpm']:.1f}")
    console.print(f"  [bold]Practice Time[/bold]  {summary['total_minutes']:.1f} min")
    console.print()


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="key4ce",
        description="A terminal typing trainer that actually makes you better.",
    )

    sub = parser.add_subparsers(dest="command")

    stats_cmd = sub.add_parser("stats", help="Print session stats and exit (no TUI)")
    stats_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    weekly_cmd = sub.add_parser("weekly", help="Print recent progress summary and exit")
    weekly_cmd.add_argument("--days", type=int, default=7, metavar="N", help="Window size in days (default: 7)")
    weekly_cmd.add_argument("--json", action="store_true", help="Output as JSON")

    export_cmd = sub.add_parser("export", help="Export session history as JSON")
    export_cmd.add_argument("--limit", type=int, default=None, metavar="N", help="Optional max number of sessions to export")

    import_cmd = sub.add_parser("import", help="Import session history from exported JSON")
    import_cmd.add_argument("path", help="Path to exported JSON file")

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

    if args.command == "stats":
        if args.json:
            _print_stats_json()
        else:
            _print_stats()
        return

    if args.command == "weekly":
        days = max(1, int(args.days))
        _print_weekly_summary(days=days, as_json=args.json)
        return

    if args.command == "export":
        limit = None if args.limit is None else max(1, int(args.limit))
        _print_export_json(limit=limit)
        return

    if args.command == "import":
        inserted = _import_sessions_from_file(args.path)
        print(f"Imported {inserted} session(s).")
        return

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
