#!/usr/bin/env python3
"""Reject generated clutter in the Harness Engineering plugin tree."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


BLOCKED_NAMES = {".DS_Store", "__pycache__"}
BLOCKED_SUFFIXES = {".pyc", ".pyo"}


def find_blockers(root: Path) -> list[str]:
    blockers: list[str] = []
    for path in root.rglob("*"):
        if path.name in BLOCKED_NAMES or path.suffix in BLOCKED_SUFFIXES:
            blockers.append(str(path.relative_to(root)))
    return sorted(blockers)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    blockers = find_blockers(root)
    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not blockers else "fail",
        "blocked_paths": blockers,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for blocker in blockers:
            print(f"blocked: {blocker}")
    return 0 if not blockers else 1


if __name__ == "__main__":
    sys.exit(main())
