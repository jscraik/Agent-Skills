#!/usr/bin/env python3
"""
Quick guardrail checker for draft benjitaylor-persona responses.

Usage:
  python3 scripts/response_guardrail_check.py --file draft.md
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Benji persona response guardrails.")
    parser.add_argument("--file", required=True, help="Path to draft response text/markdown file.")
    args = parser.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[FAIL] file not found: {p}")
        return 2

    text = p.read_text(encoding="utf-8")
    t = text.lower()

    checks = [
        ("implementation detail present", any(k in t for k in ("selector", "component", "state", "canvas", "requestanimationframe"))),
        ("continuity language", any(k in t for k in ("continuity", "fly", "teleport", "transition", "morph"))),
        ("explicit tradeoff", any(k in t for k in ("tradeoff", "alternative", "defer", "why now"))),
        ("safety boundary language", any(k in t for k in ("safe", "risk", "boundary", "validate"))),
        ("clear next step", any(k in t for k in ("next step", "next action", "decision"))),
    ]

    missing = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"[{'OK' if ok else 'WARN'}] {name}")

    if missing:
        print(f"\nResult: WARN ({len(missing)} missing signal(s))")
        return 1

    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
