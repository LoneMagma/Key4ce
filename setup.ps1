<#
.SYNOPSIS
  Windows installer/bootstrap for Key4ce.

.DESCRIPTION
  - Detects Python 3.11+
  - Creates/uses local virtual environment (.venv)
  - Installs project dependencies in editable mode
  - Optionally installs dev dependencies

.USAGE
  powershell -ExecutionPolicy Bypass -File .\setup.ps1
  powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Dev
#>

[CmdletBinding()]
param(
    [switch]$Dev,
    [switch]$NoVenv
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Step([string]$Message) {
    Write-Host "[setup] $Message" -ForegroundColor Cyan
}

function Resolve-PythonCommand {
    # Prefer py launcher on Windows when available
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return @('py', '-3')
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return @('python')
    }
    throw "Python was not found. Install Python 3.11+ from https://python.org and retry."
}

function Invoke-Python([string[]]$PyCmd, [string[]]$Args) {
    $exe = $PyCmd[0]
    $base = @()
    if ($PyCmd.Length -gt 1) {
        $base = $PyCmd[1..($PyCmd.Length - 1)]
    }
    & $exe @base @Args
}

function Assert-PythonVersion([string[]]$PyCmd) {
    $versionOutput = Invoke-Python -PyCmd $PyCmd -Args @('-c', "import sys;print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    $parts = $versionOutput.Trim().Split('.')
    $major = [int]$parts[0]
    $minor = [int]$parts[1]
    if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 11)) {
        throw "Python 3.11+ is required. Detected: $versionOutput"
    }
}

$py = Resolve-PythonCommand
Assert-PythonVersion -PyCmd $py

if (-not $NoVenv) {
    Write-Step "Creating virtual environment (.venv)"
    Invoke-Python -PyCmd $py -Args @('-m', 'venv', '.venv')

    $venvPython = Join-Path '.venv' 'Scripts\python.exe'
    if (-not (Test-Path $venvPython)) {
        throw "Virtual environment python not found at $venvPython"
    }
    $py = @($venvPython)
}

Write-Step "Upgrading pip"
Invoke-Python -PyCmd $py -Args @('-m', 'pip', 'install', '--upgrade', 'pip')

if ($Dev) {
    Write-Step "Installing Key4ce with dev dependencies"
    Invoke-Python -PyCmd $py -Args @('-m', 'pip', 'install', '-e', '.[dev]')
} else {
    Write-Step "Installing Key4ce"
    Invoke-Python -PyCmd $py -Args @('-m', 'pip', 'install', '-e', '.')
}

Write-Step "Installation complete"
Write-Host ""
Write-Host "Run the app with one of:" -ForegroundColor Green
if (-not $NoVenv) {
    Write-Host "  .\.venv\Scripts\python.exe start.py"
    Write-Host "  .\.venv\Scripts\python.exe -m key4ce"
} else {
    Write-Host "  python start.py"
    Write-Host "  python -m key4ce"
}
