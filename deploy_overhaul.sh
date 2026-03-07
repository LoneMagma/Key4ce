#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
#  Key4ce UI Overhaul — Deploy Script
#
#  Drop all overhaul files in the repo root, then run:
#
#      bash deploy_overhaul.sh
#
#  The script:
#    1. Detects the repo root (directory containing pyproject.toml)
#    2. Backs up every file it is about to overwrite  (.bak)
#    3. Moves each file to its correct location
#    4. Reports what was moved / what was skipped
#    5. Verifies Python can import each overwritten module
#
#  Safe to re-run. Backups are not overwritten on re-run.
# ─────────────────────────────────────────────────────────────────
set -euo pipefail

# ── Colours ──────────────────────────────────────────────────────
CYAN='\033[0;36m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
RED='\033[0;31m';  BOLD='\033[1m';    RESET='\033[0m'

step()   { echo -e "  ${CYAN}▸${RESET} $*"; }
ok()     { echo -e "  ${GREEN}✓${RESET} $*"; }
warn()   { echo -e "  ${YELLOW}⚠${RESET} $*"; }
skip()   { echo -e "  ${CYAN}-${RESET} $*"; }
fail()   { echo -e "  ${RED}✗${RESET} $*"; }

# ── Find repo root ────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT=""

# Walk up from script location looking for pyproject.toml
dir="$SCRIPT_DIR"
for _ in $(seq 1 5); do
    if [[ -f "$dir/pyproject.toml" ]]; then
        REPO_ROOT="$dir"
        break
    fi
    dir="$(dirname "$dir")"
done

if [[ -z "$REPO_ROOT" ]]; then
    # Fallback: assume script is in repo root
    REPO_ROOT="$SCRIPT_DIR"
    if [[ ! -f "$REPO_ROOT/pyproject.toml" ]]; then
        echo -e "${RED}Could not find repo root (no pyproject.toml found).${RESET}"
        echo "Run this script from inside the Key4ce repository."
        exit 1
    fi
fi

echo ""
echo -e "${BOLD}${CYAN}Key4ce UI Overhaul — Deploy${RESET}"
echo -e "  Repo root: ${REPO_ROOT}"
echo ""

# ── File manifest ─────────────────────────────────────────────────
# Format: "source_filename_in_root:destination_relative_to_repo_root"
declare -a MANIFEST=(
    "menu.py:key4ce/ui/screens/menu.py"
    "typing.py:key4ce/ui/screens/typing.py"
    "results.py:key4ce/ui/screens/results.py"
    "analytics.py:key4ce/ui/screens/analytics.py"
    "app.py:key4ce/ui/app.py"
    "builtin.py:key4ce/content/builtin.py"
)

MOVED=0
SKIPPED=0
BACKED_UP=0
FAILED=0

# ── Process each file ─────────────────────────────────────────────
for entry in "${MANIFEST[@]}"; do
    src_name="${entry%%:*}"
    dest_rel="${entry##*:}"

    src_path="${REPO_ROOT}/${src_name}"
    dest_path="${REPO_ROOT}/${dest_rel}"
    dest_dir="$(dirname "$dest_path")"

    # Does the source file exist in root?
    if [[ ! -f "$src_path" ]]; then
        skip "${src_name} not found in root — skipping"
        (( SKIPPED++ )) || true
        continue
    fi

    # Ensure destination directory exists
    if [[ ! -d "$dest_dir" ]]; then
        step "Creating directory: ${dest_rel%/*}"
        mkdir -p "$dest_dir"
        # Also create __init__.py if missing
        if [[ ! -f "$dest_dir/__init__.py" ]]; then
            touch "$dest_dir/__init__.py"
            ok "Created ${dest_rel%/*}/__init__.py"
        fi
    fi

    # Back up existing file
    if [[ -f "$dest_path" ]]; then
        bak="${dest_path}.bak"
        if [[ ! -f "$bak" ]]; then
            cp "$dest_path" "$bak"
            (( BACKED_UP++ )) || true
            ok "Backed up: ${dest_rel} → ${dest_rel}.bak"
        else
            warn "Backup already exists for ${dest_rel} — keeping existing .bak"
        fi
    fi

    # Move the file
    if cp "$src_path" "$dest_path"; then
        rm "$src_path"
        ok "Deployed: ${src_name} → ${dest_rel}"
        (( MOVED++ )) || true
    else
        fail "Failed to deploy ${src_name} → ${dest_rel}"
        (( FAILED++ )) || true
    fi
done

# ── Ensure __init__.py files exist in all package dirs ────────────
INIT_DIRS=(
    "key4ce/ui"
    "key4ce/ui/screens"
    "key4ce/content"
)

for d in "${INIT_DIRS[@]}"; do
    full="${REPO_ROOT}/${d}/__init__.py"
    if [[ ! -f "$full" ]]; then
        touch "$full"
        ok "Created missing __init__.py in ${d}"
    fi
done

# ── Python import smoke test ──────────────────────────────────────
echo ""
step "Running import checks..."

PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [[ -z "$PYTHON" ]]; then
    warn "Python not found — skipping import checks"
else
    MODULES=(
        "key4ce.ui.app"
        "key4ce.ui.screens.menu"
        "key4ce.ui.screens.typing"
        "key4ce.ui.screens.results"
        "key4ce.ui.screens.analytics"
        "key4ce.content.builtin"
    )
    for mod in "${MODULES[@]}"; do
        result=$(cd "$REPO_ROOT" && "$PYTHON" -c "import $mod" 2>&1 || true)
        if [[ -z "$result" ]]; then
            ok "Import OK: ${mod}"
        else
            warn "Import issue: ${mod}"
            echo "       ${result}" | head -3
        fi
    done
fi

# ── Summary ───────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}Deploy complete${RESET}"
echo -e "  ${GREEN}${MOVED} files deployed${RESET}   ${CYAN}${BACKED_UP} backed up${RESET}   ${YELLOW}${SKIPPED} skipped${RESET}"
if (( FAILED > 0 )); then
    echo -e "  ${RED}${FAILED} failed — check errors above${RESET}"
fi
echo ""
echo -e "  Run the app:  ${CYAN}key4ce${RESET}   or   ${CYAN}python -m key4ce${RESET}"
echo ""

# ── Restore instructions ──────────────────────────────────────────
if (( BACKED_UP > 0 )); then
    echo -e "  ${YELLOW}To restore originals:${RESET}"
    echo "    for f in \$(find ${REPO_ROOT}/key4ce -name '*.bak'); do"
    echo "      cp \"\$f\" \"\${f%.bak}\""
    echo "    done"
    echo ""
fi
