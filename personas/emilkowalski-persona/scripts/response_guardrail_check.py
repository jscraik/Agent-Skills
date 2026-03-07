#!/usr/bin/env python3
"""
Lightweight guardrail checker for draft emilkowalski-persona responses.

Usage:
  python3 scripts/response_guardrail_check.py --file /path/to/draft.md
"""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check persona response guardrails.")
    parser.add_argument("--file", required=True, help="Path to draft response text/markdown file.")
    args = parser.parse_args()

    draft_path = Path(args.file)
    if not draft_path.exists():
        print(f"[FAIL] File not found: {draft_path}")
        return 2

    text = draft_path.read_text(encoding="utf-8")
    text_lc = text.lower()

    checks = [
        ("purpose/constraints framing", any(k in text_lc for k in ("goal", "constraint", "constraints"))),
        (
            "implementation detail",
            any(k in text_lc for k in ("snippet", "```", "css", "transform", "opacity", "clip-path")),
        ),
        ("accessibility mention", any(k in text_lc for k in ("reduced motion", "prefers-reduced-motion", "accessibility"))),
        ("performance mention", any(k in text_lc for k in ("performance", "60fps", "frame", "compositor"))),
        ("clear next step", any(k in text_lc for k in ("next step", "next decision", "choose", "decide"))),
    ]

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"[{'OK' if ok else 'WARN'}] {name}")

    if failed:
        print(f"\nResult: WARN ({len(failed)} missing signal(s))")
        return 1

    print("\nResult: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
