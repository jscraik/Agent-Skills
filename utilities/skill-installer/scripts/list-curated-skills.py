#!/usr/bin/env python3
"""Backward-compatible wrapper for list-skills.py.

Deprecated: prefer invoking `list-skills.py` directly.
"""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def main() -> int:
    target = Path(__file__).with_name("list-skills.py")
    if not target.exists():
        print(f"Error: missing target script: {target}", file=sys.stderr)
        return 1

    sys.argv = [str(target), *sys.argv[1:]]
    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
