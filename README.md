# Key4ce

Key4ce is a terminal typing trainer focused on measurable improvement through structured practice, local-first progress tracking, and post-session feedback.

## Current Product State

Key4ce is functional and usable today as a beta terminal application.

Implemented capabilities:

- Real-time typing sessions with terminal UI flow.
- Session persistence in local SQLite storage.
- Session analytics: WPM, accuracy, errors, streak-oriented summaries.
- CLI reporting commands for weekly summaries, goals, exports/imports, brag cards, pace-drop insights, leaderboard, challenge, achievements, coaching, and profile preferences.
- Focus-oriented drill hooks powered by error and timing data.

## Universal Start Command

From a fresh clone, the simplest start command is:

```bash
python start.py
```

This launches the app through a repository-local entrypoint and avoids requiring users to remember module paths.

If dependencies are not installed yet:

```bash
pip install -e .
python start.py
```

## Installation

```bash
git clone https://github.com/LoneMagma/Key4ce.git
cd Key4ce
pip install -e .
```

Optional development dependencies:

```bash
pip install -e ".[dev]"
```

Universal one-command setup (Linux/macOS/Windows with Python 3.11+):

```bash
python install.py
```

Windows PowerShell setup (native):

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Truly universal install + run (no git required, stdlib-only bootstrap):

```bash
python -c "import io,zipfile,tempfile,urllib.request,subprocess,sys,pathlib; u='https://github.com/LoneMagma/Key4ce/archive/refs/heads/main.zip'; d=pathlib.Path(tempfile.mkdtemp()); z=d/'k.zip'; z.write_bytes(urllib.request.urlopen(u).read()); zipfile.ZipFile(z).extractall(d); r=next(d.glob('Key4ce-*')); subprocess.check_call([sys.executable,'install.py'],cwd=r); subprocess.check_call([sys.executable,'start.py'],cwd=r)"
```


## Usage

Primary launch methods:

```bash
python start.py
key4ce
python -m key4ce
```

Selected CLI commands:

```bash
python -m key4ce stats
python -m key4ce weekly --days 14
python -m key4ce goals --preset steady
python -m key4ce brag --days 7
python -m key4ce drops --top 5
python -m key4ce leaderboard --limit 10
python -m key4ce challenge
python -m key4ce achievements
python -m key4ce coach --days 7
python -m key4ce profile --mode sentences --words 50 --theme cyberpunk
python -m key4ce providers --days 30  # includes external availability checks
python -m key4ce providers-validate --json
python -m key4ce report --days 7
python -m key4ce assign --days 7
python -m key4ce kpi --days 30
python -m key4ce sync-plan --target key4ce-snapshot.json
python -m key4ce sync key4ce-snapshot.json --mode safe
python -m key4ce class-report class/*.json
python -m key4ce class-dashboard class/*.json
python -m key4ce telemetry --days 30 --out key4ce-telemetry.json
python -m key4ce sync-remote --url https://example.org/key4ce/snapshot --mode pull --path key4ce-remote.json
python -m key4ce export --limit 200 > sessions.json
python -m key4ce import sessions.json
python -m key4ce snapshot > key4ce-snapshot.json
python -m key4ce restore key4ce-snapshot.json
```

Session length labels in the menu/challenge flow are now:

- `Short` (~25 words)
- `Medium` (~50 words)
- `Long` (~100 words)

## Data Locations

Key4ce stores local files in:

- `~/.key4ce/sessions.db`
- `~/.key4ce/goals.json`
- `~/.key4ce/profile.json`

## Roadmap Phases

The roadmap source of truth is `PRODUCT_AUDIT.md`.

### Completed / In Progress

- Phase 0 (foundation): completed for day-to-day local usage; architecture cleanup remains as technical debt.
- Phase 1 (cohesive core loop): completed baseline (session flow, stats, persistence, import/export).
- Phase 2 (product differentiation): completed baseline with adaptive coaching command, goals/streak workflows, pace-drop insights, daily challenge, leaderboard, and achievements.

### Phase 3 Status

Phase 3 baseline is now complete in the CLI-first product surface:

1. Plugin/provider framework: `providers` health and `providers-validate` contract checks.
2. Cross-device sync: local dry-run/apply sync (`sync-plan`, `sync`) and optional HTTP transport (`sync-remote`).
3. Team/education mode: assignment planning (`assign`), class aggregate (`class-report`), and dashboard view (`class-dashboard`).
4. Product analytics pipeline baseline: KPI (`kpi`) and privacy-safe telemetry export (`telemetry`).

Remaining future enhancements are now depth/scale upgrades (not baseline gaps):

- richer plugin lifecycle hooks (auth, retries, provider-specific adapters),
- hosted sync account flows with conflict resolution UX,
- richer education dashboards/UI over the CLI baseline.

## Development

Run tests:

```bash
pytest -q
```

Recommended quick checks:

```bash
python -m key4ce weekly --json
python -m key4ce goals --json
python -m key4ce drops --json
python -m key4ce coach --json
python -m key4ce achievements --json
python -m key4ce providers --json
python -m key4ce providers-validate --json
python -m key4ce report --json
python -m key4ce assign --json
python -m key4ce kpi --json
python -m key4ce sync-plan --json
python -m key4ce class-dashboard class/*.json --json
python -m key4ce sync-remote --url https://example.org/key4ce/snapshot --mode pull --path key4ce-remote.json
python -m key4ce telemetry --days 30
```

## Contributing

Contributions are welcome. Keep changes focused, test-backed, and documented.

## License

MIT. See `LICENSE`.
