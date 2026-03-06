#!/usr/bin/env python3
"""Universal startup entrypoint for Key4ce.

Usage:
    python start.py
"""

from __future__ import annotations

import sys


def main() -> int:
    try:
        from key4ce.__main__ import main as key4ce_main
    except ModuleNotFoundError as exc:
        missing = exc.name or "dependency"
        print(
            f"Missing dependency: {missing}\n"
            "Install project dependencies, then retry:\n"
            "  pip install -e ."
        )
        return 1

    key4ce_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
