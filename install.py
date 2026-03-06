#!/usr/bin/env python3
"""Cross-platform bootstrap installer for Key4ce.

Usage:
  python install.py
  python install.py --dev
  python install.py --no-venv
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_DIR = ROOT / ".venv"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def version_ok() -> bool:
    return (sys.version_info.major, sys.version_info.minor) >= (3, 11)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Key4ce dependencies")
    parser.add_argument("--dev", action="store_true", help="Install dev dependencies")
    parser.add_argument("--no-venv", action="store_true", help="Install into current interpreter")
    args = parser.parse_args()

    if not version_ok():
        print(f"Python 3.11+ required. Detected {sys.version.split()[0]}")
        return 1

    python = sys.executable

    if not args.no_venv:
        run([python, "-m", "venv", str(VENV_DIR)])
        if sys.platform == "win32":
            python = str(VENV_DIR / "Scripts" / "python.exe")
        else:
            python = str(VENV_DIR / "bin" / "python")

    run([python, "-m", "pip", "install", "--upgrade", "pip"])
    if args.dev:
        run([python, "-m", "pip", "install", "-e", ".[dev]"])
    else:
        run([python, "-m", "pip", "install", "-e", "."])

    print("Installation complete.")
    if not args.no_venv:
        if sys.platform == "win32":
            print(r"Run: .\.venv\Scripts\python.exe start.py")
        else:
            print("Run: ./.venv/bin/python start.py")
    else:
        print("Run: python start.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
