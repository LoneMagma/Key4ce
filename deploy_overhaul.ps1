#Requires -Version 5.1
<#
.SYNOPSIS
    Key4ce UI Overhaul — Windows Deploy Script

.DESCRIPTION
    Drop the overhaul files in the repo root, then run:

        powershell -ExecutionPolicy Bypass -File deploy_overhaul.ps1

    The script:
      1. Finds the repo root (directory containing pyproject.toml)
      2. Backs up every file it is about to overwrite  (.bak)
      3. Copies each file to its correct location
      4. Creates any missing __init__.py files
      5. Runs Python import smoke tests on all deployed modules
      6. Reports exactly what happened

    Safe to re-run. Existing .bak files are never overwritten.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── Console helpers ───────────────────────────────────────────────
function Write-Step  { param($msg) Write-Host "  " -NoNewline; Write-Host ">" -ForegroundColor Cyan -NoNewline;  Write-Host " $msg" }
function Write-Ok    { param($msg) Write-Host "  " -NoNewline; Write-Host "v" -ForegroundColor Green -NoNewline; Write-Host " $msg" }
function Write-Warn  { param($msg) Write-Host "  " -NoNewline; Write-Host "!" -ForegroundColor Yellow -NoNewline; Write-Host " $msg" }
function Write-Skip  { param($msg) Write-Host "  " -NoNewline; Write-Host "-" -ForegroundColor Cyan -NoNewline;  Write-Host " $msg" }
function Write-Fail  { param($msg) Write-Host "  " -NoNewline; Write-Host "x" -ForegroundColor Red -NoNewline;  Write-Host " $msg" }

function Write-Banner {
    Write-Host ""
    Write-Host "  Key4ce UI Overhaul" -ForegroundColor Cyan -NoNewline
    Write-Host " -- Deploy Script"
    Write-Host ""
}

# ── Find repo root ────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = $null

$dir = $ScriptDir
for ($i = 0; $i -lt 5; $i++) {
    if (Test-Path (Join-Path $dir "pyproject.toml")) {
        $RepoRoot = $dir
        break
    }
    $parent = Split-Path -Parent $dir
    if ($parent -eq $dir) { break }
    $dir = $parent
}

if (-not $RepoRoot) {
    # Fallback: assume script is already in repo root
    $RepoRoot = $ScriptDir
    if (-not (Test-Path (Join-Path $RepoRoot "pyproject.toml"))) {
        Write-Host ""
        Write-Host "  ERROR: Could not find repo root (no pyproject.toml found)." -ForegroundColor Red
        Write-Host "  Run this script from inside the Key4ce repository."
        Write-Host ""
        exit 1
    }
}

Write-Banner
Write-Host "  Repo root: $RepoRoot"
Write-Host ""

# ── File manifest ─────────────────────────────────────────────────
# Each entry: source filename in root => destination relative to repo root
$Manifest = [ordered]@{
    "menu.py"      = "key4ce\ui\screens\menu.py"
    "typing.py"    = "key4ce\ui\screens\typing.py"
    "results.py"   = "key4ce\ui\screens\results.py"
    "analytics.py" = "key4ce\ui\screens\analytics.py"
    "app.py"       = "key4ce\ui\app.py"
    "builtin.py"   = "key4ce\content\builtin.py"
}

$Moved    = 0
$Skipped  = 0
$BackedUp = 0
$Failed   = 0

# ── Process each file ─────────────────────────────────────────────
foreach ($entry in $Manifest.GetEnumerator()) {
    $SrcName  = $entry.Key
    $DestRel  = $entry.Value

    $SrcPath  = Join-Path $RepoRoot $SrcName
    $DestPath = Join-Path $RepoRoot $DestRel
    $DestDir  = Split-Path -Parent $DestPath

    # Source file must exist in root
    if (-not (Test-Path $SrcPath)) {
        Write-Skip "$SrcName not found in root -- skipping"
        $Skipped++
        continue
    }

    # Create destination directory if needed
    if (-not (Test-Path $DestDir)) {
        Write-Step "Creating directory: $(Split-Path -Parent $DestRel)"
        New-Item -ItemType Directory -Path $DestDir -Force | Out-Null

        # Create __init__.py if missing
        $InitPath = Join-Path $DestDir "__init__.py"
        if (-not (Test-Path $InitPath)) {
            New-Item -ItemType File -Path $InitPath -Force | Out-Null
            Write-Ok "Created $(Split-Path -Parent $DestRel)\__init__.py"
        }
    }

    # Back up existing file
    if (Test-Path $DestPath) {
        $BakPath = "$DestPath.bak"
        if (-not (Test-Path $BakPath)) {
            Copy-Item $DestPath $BakPath
            $BackedUp++
            Write-Ok "Backed up: $DestRel -> $DestRel.bak"
        } else {
            Write-Warn "Backup already exists for $DestRel -- keeping existing .bak"
        }
    }

    # Deploy the file
    try {
        Copy-Item $SrcPath $DestPath -Force
        Remove-Item $SrcPath -Force
        Write-Ok "Deployed: $SrcName -> $DestRel"
        $Moved++
    } catch {
        Write-Fail "Failed to deploy $SrcName -> $DestRel : $_"
        $Failed++
    }
}

# ── Ensure __init__.py exists in all package dirs ─────────────────
$InitDirs = @(
    "key4ce\ui",
    "key4ce\ui\screens",
    "key4ce\content"
)

foreach ($d in $InitDirs) {
    $InitPath = Join-Path $RepoRoot "$d\__init__.py"
    if (-not (Test-Path $InitPath)) {
        New-Item -ItemType File -Path $InitPath -Force | Out-Null
        Write-Ok "Created missing __init__.py in $d"
    }
}

# ── Python import smoke tests ─────────────────────────────────────
Write-Host ""
Write-Step "Running import checks..."

$Python = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python") {
            $Python = $cmd
            break
        }
    } catch {}
}

if (-not $Python) {
    Write-Warn "Python not found -- skipping import checks"
} else {
    $Modules = @(
        "key4ce.ui.app",
        "key4ce.ui.screens.menu",
        "key4ce.ui.screens.typing",
        "key4ce.ui.screens.results",
        "key4ce.ui.screens.analytics",
        "key4ce.content.builtin"
    )
    Push-Location $RepoRoot
    foreach ($mod in $Modules) {
        try {
            $result = & $Python -c "import $mod" 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Ok "Import OK: $mod"
            } else {
                Write-Warn "Import issue: $mod"
                Write-Host "       $result" -ForegroundColor DarkGray
            }
        } catch {
            Write-Warn "Could not check: $mod"
        }
    }
    Pop-Location
}

# ── Summary ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "  Deploy complete" -ForegroundColor White -NoNewline
Write-Host ""
Write-Host "  $Moved files deployed  " -ForegroundColor Green -NoNewline
Write-Host "  $BackedUp backed up  " -ForegroundColor Cyan -NoNewline
Write-Host "  $Skipped skipped" -ForegroundColor Yellow

if ($Failed -gt 0) {
    Write-Host "  $Failed failed -- check errors above" -ForegroundColor Red
}

Write-Host ""
Write-Host "  Run the app:  " -NoNewline
Write-Host "key4ce" -ForegroundColor Cyan -NoNewline
Write-Host "   or   " -NoNewline
Write-Host "python -m key4ce" -ForegroundColor Cyan
Write-Host ""

# ── Restore instructions ──────────────────────────────────────────
if ($BackedUp -gt 0) {
    Write-Host "  To restore originals:" -ForegroundColor Yellow
    Write-Host '    Get-ChildItem -Recurse -Filter "*.bak" | ForEach-Object {'
    Write-Host '        Copy-Item $_.FullName ($_.FullName -replace "\.bak$", "") -Force'
    Write-Host '    }'
    Write-Host ""
}
