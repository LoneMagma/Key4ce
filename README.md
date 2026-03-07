# Key4ce

A terminal typing trainer focused on measurable improvement through structured practice, local-first progress tracking, and post-session analytics.

```
 ██╗  ██╗███████╗██╗   ██╗██╗  ██╗ ██████╗███████╗
 ██║ ██╔╝██╔════╝╚██╗ ██╔╝██║  ██║██╔════╝██╔════╝
 █████╔╝ █████╗   ╚████╔╝ ███████║██║     █████╗
 ██╔═██╗ ██╔══╝    ╚██╔╝  ╚════██║██║     ██╔══╝
 ██║  ██╗███████╗   ██║        ██║╚██████╗███████╗
 ╚═╝  ╚═╝╚══════╝   ╚═╝        ╚═╝ ╚═════╝╚══════╝
```

---

## What Key4ce Actually Is

Key4ce is a **terminal-first** typing trainer. The app runs entirely in your terminal with no browser, no Electron, no account required. Everything — sessions, stats, goals, achievements — is stored locally in a SQLite database under `~/.key4ce/`.

The active app stack is **Rich + readchar**. You interact via a fullscreen terminal UI with a live typing screen, post-session report, analytics dashboard, and a menu system for picking content and session length.

A separate CLI surface (`python -m key4ce <command>`) gives you scriptable access to stats, goals, exports, coaching plans, and more — designed for automation, daily check-ins, and team/education use.

---

## Requirements

- Python 3.11 or higher
- `pip install -e .` installs the two runtime dependencies: `rich` and `readchar`
- **Note:** The config system also requires `pyyaml`. Install it manually if you use config file features:
  ```bash
  pip install pyyaml
  ```

---

## Installation

```bash
git clone https://github.com/LoneMagma/Key4ce.git
cd Key4ce
pip install -e .
```

With dev dependencies (includes pytest):

```bash
pip install -e ".[dev]"
```

Guided install script (creates a `.venv` automatically):

```bash
python install.py
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

One-liner bootstrap (no git required):

```bash
python -c "import io,zipfile,tempfile,urllib.request,subprocess,sys,pathlib; u='https://github.com/LoneMagma/Key4ce/archive/refs/heads/main.zip'; d=pathlib.Path(tempfile.mkdtemp()); z=d/'k.zip'; z.write_bytes(urllib.request.urlopen(u).read()); zipfile.ZipFile(z).extractall(d); r=next(d.glob('Key4ce-*')); subprocess.check_call([sys.executable,'install.py'],cwd=r); subprocess.check_call([sys.executable,'start.py'],cwd=r)"
```

---

## Running the App

```bash
python start.py        # recommended universal entrypoint
python -m key4ce       # equivalent
key4ce                 # if installed via pip
```

### Launch Flags

| Flag | Effect |
|------|--------|
| `--mode <category>` | Skip the menu, go straight to a session |
| `--words <n>` | Set approximate word count (default: 50) |
| `--zen` | Hide stats during typing; show only at end |
| `--focus` | Generate a session targeting your weakest keys/digraphs |
| `--theme <name>` | Override the colour theme: `cyberpunk` `nord` `dracula` `monokai` `minimal` |

Examples:

```bash
python -m key4ce --mode code --words 100
python -m key4ce --zen --mode sentences
python -m key4ce --focus --words 50
python -m key4ce --theme dracula
```

---

## Typing Session

Once inside a session:

| Key | Action |
|-----|--------|
| Type normally | Advance through the text |
| `Backspace` | Correct the previous character |
| `Tab` | Restart the same session immediately |
| `Esc` | Exit back to menu |

Content categories available:

| Category | Description |
|----------|-------------|
| `words` | Top 200 common English words |
| `sentences` | Natural prose sentences |
| `quotes` | Famous quotes |
| `code` | Python code snippets with symbols |
| `numbers` | Numeric sequences for data-entry focus |
| `wikipedia` | Live random Wikipedia article extract |
| `quote` (live) | Fresh random quote from quotable.io |
| `focus` | Auto-generated text targeting your weakest keys/digraphs |

Session lengths: **Short** (~25 words), **Medium** (~50 words), **Long** (~100 words).

---

## Post-Session Report

After every session you get a full breakdown:

- Final WPM and accuracy with personal-best delta
- Coaching hint for the next session
- Pace insight (where you peaked and where you slowed)
- WPM-over-time graph (ASCII)
- Keyboard heatmap
- Top error pairs (e.g. typed `r` expected `e`, ×4)
- Slowest digraph transitions with deviation from your average
- Problem keys ranked by error rate
- Focus practice suggestion linking directly to the `f` key

From the results screen: `r` retry · `f` focus drill · `m` menu · `q` quit.

---

## Analytics

Press `a` from the main menu to open the analytics dashboard. It shows:

- Average and best WPM and accuracy across all sessions
- Session count
- Recent 5-run breakdown
- Trend summary (speed vs. accuracy direction)
- AI recommendation — uses Groq if `GROQ_API_KEY` is set, falls back to a deterministic local rule engine

---

## CLI Commands

All commands output plain text by default. Add `--json` for machine-readable output.

### Stats & Progress

```bash
python -m key4ce stats                      # session history table
python -m key4ce stats --json
python -m key4ce weekly                     # 7-day summary
python -m key4ce weekly --days 14
python -m key4ce brag --days 7             # shareable one-paragraph card
```

### Goals

```bash
python -m key4ce goals                      # show targets and today's progress
python -m key4ce goals --set-minutes 20
python -m key4ce goals --set-sessions 2
python -m key4ce goals --preset steady      # starter / steady / intense
```

### Coaching & Analysis

```bash
python -m key4ce coach                      # adaptive drill plan from recent data
python -m key4ce coach --days 14
python -m key4ce drops                      # where pace dropped in the last session
python -m key4ce drops --top 10
```

### Achievements & Leaderboard

```bash
python -m key4ce achievements               # unlocked milestones
python -m key4ce leaderboard               # local top runs
python -m key4ce leaderboard --source code
python -m key4ce challenge                 # today's deterministic daily challenge
```

### Profile

```bash
python -m key4ce profile
python -m key4ce profile --mode sentences --words 50 --theme cyberpunk
```

### Data Portability

```bash
python -m key4ce export                    # session history JSON
python -m key4ce export --limit 100
python -m key4ce import sessions.json
python -m key4ce snapshot                  # full snapshot: sessions + goals + profile
python -m key4ce restore key4ce-snapshot.json
```

### Sync

```bash
python -m key4ce sync-plan                             # dry-run diff vs a snapshot file
python -m key4ce sync-plan --target remote.json
python -m key4ce sync remote.json                      # apply sync (safe mode)
python -m key4ce sync remote.json --mode force
python -m key4ce sync-remote --url https://... --mode pull --path snap.json
python -m key4ce sync-remote --url https://... --mode push --path snap.json
```

### Team / Education

```bash
python -m key4ce report --days 7           # progress report (shareable)
python -m key4ce assign --days 7           # 3-step assignment plan
python -m key4ce class-report a.json b.json c.json
python -m key4ce class-dashboard a.json b.json c.json
```

### Operations

```bash
python -m key4ce kpi --days 30             # KPI snapshot
python -m key4ce providers --days 30       # content provider reliability
python -m key4ce providers-validate        # validate providers.json plugin config
python -m key4ce telemetry --days 30       # privacy-safe aggregated payload
python -m key4ce telemetry --out out.json
```

---

## Data Storage

| File | Contents |
|------|----------|
| `~/.key4ce/sessions.db` | SQLite — all session records, timings, errors |
| `~/.key4ce/goals.json` | Daily minutes and sessions targets |
| `~/.key4ce/profile.json` | Preferred mode, word count, theme |
| `~/.key4ce/cache/` | Cached external content (Wikipedia, quotes) |
| `~/.key4ce/providers.json` | Optional third-party content plugin declarations |

---

## AI Recommendation (Optional)

The analytics screen includes a 1–2 line coaching note. If `GROQ_API_KEY` is set it calls the Groq API; otherwise a deterministic local fallback runs.

```bash
export GROQ_API_KEY="gsk_..."
export GROQ_MODEL="llama-3.1-8b-instant"   # optional, this is the default
```

---

## Themes

| Name | Description |
|------|-------------|
| `cyberpunk` | Default — dark navy, neon green and cyan |
| `nord` | Muted blues, Scandinavian calm |
| `dracula` | Purple and pink on dark grey |
| `monokai` | Classic editor palette |
| `minimal` | Black and white only |

Change via flag: `python -m key4ce --theme nord`  
Change permanently: `python -m key4ce profile --theme nord`

---

## Development

```bash
pip install -e ".[dev]"
pytest -q
```

Quick smoke-test the CLI surface:

```bash
python -m key4ce stats --json
python -m key4ce weekly --json
python -m key4ce coach --json
python -m key4ce achievements --json
python -m key4ce kpi --json
```

### Project Layout

```
key4ce/
├── __main__.py          # Full CLI — all subcommands live here
├── ui/
│   ├── app.py           # Active app shell (Rich + readchar)
│   └── screens/
│       ├── menu.py      # Main menu and category/length picker
│       ├── typing.py    # Typing session screen
│       ├── results.py   # Post-session report
│       └── analytics.py # Analytics dashboard
├── core/
│   ├── engine.py        # Typing state machine
│   ├── recorder.py      # Keystroke timeline
│   └── analyzer.py      # Post-session analysis
├── content/
│   ├── builtin.py       # Built-in word/sentence/code pools
│   ├── loader.py        # External providers (Wikipedia, quotes)
│   └── focus.py         # Focus drill text generator
├── data/
│   └── db.py            # SQLite persistence layer
└── themes/
    └── themes.py        # Theme dataclasses
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version:

- Keep changes focused and backed by a test
- Follow PEP 8, use black for formatting
- Update CHANGELOG.md for user-facing changes
- Write docstrings on public functions

---

## License

MIT — see [LICENSE](LICENSE).
