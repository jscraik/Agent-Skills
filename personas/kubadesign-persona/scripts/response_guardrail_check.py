#!/usr/bin/env python3
"""
Quick guardrail checker for draft kubadesign-persona responses.

Usage:
  python3 scripts/response_guardrail_check.py --file draft.md
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check kubadesign persona response guardrails.")
    parser.add_argument("--file", required=True, help="Path to draft response text/markdown file.")
    args = parser.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[FAIL] file not found: {p}")
        return 2

    text = p.read_text(encoding="utf-8")
    t = text.lower()

    checks = [
        ("conversion framing", any(k in t for k in ("conversion", "signup", "demo", "trust", "outcome"))),
        ("explicit tradeoff", any(k in t for k in ("tradeoff", "alternative", "defer", "speed vs", "clarity vs"))),
        ("implementation detail", any(k in t for k in ("layout", "hierarchy", "experiment", "metric", "iteration"))),
        ("assumption boundary", any(k in t for k in ("assumption", "depends", "if true", "evidence"))),
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
