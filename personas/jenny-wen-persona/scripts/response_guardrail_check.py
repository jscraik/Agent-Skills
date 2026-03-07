#!/usr/bin/env python3
"""
Quick guardrail checker for draft jenny-wen-persona responses.

Usage:
  python3 scripts/response_guardrail_check.py --file /path/to/draft.md
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Jenny persona response guardrails.")
    parser.add_argument("--file", required=True, help="Path to draft response text/markdown file.")
    args = parser.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[FAIL] file not found: {p}")
        return 2

    text = p.read_text(encoding="utf-8")
    t = text.lower()

    checks = [
        ("user value framing", any(k in t for k in ("user value", "value", "adoption", "trust"))),
        ("explicit tradeoff", any(k in t for k in ("tradeoff", "parity", "differentiation", "alternative"))),
        ("cross-functional execution", any(k in t for k in ("owner", "handoff", "feedback loop", "checkpoint"))),
        ("ai constraints", any(k in t for k in ("constraint", "limitation", "non-deterministic", "preview"))),
        ("clear next step", any(k in t for k in ("next step", "next action", "decide", "decision"))),
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
