#!/usr/bin/env python3
"""Validate asymmetric ideation markdown output for required structure.

Usage:
  python scripts/validate_ideation_output.py <ideas.md>
"""

from __future__ import annotations

import re
import argparse
from pathlib import Path

REQUIRED_FIELDS = [
    "Core Concept",
    "Why It’s Asymmetric",
    "Why It Would Surprise the Founder",
    "30-Day Launch Path",
    "Long-Term Optionality",
]


def fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate asymmetric ideation markdown output for required structure."
    )
    parser.add_argument("ideas_markdown", help="Path to ideas markdown file")
    args = parser.parse_args()

    path = Path(args.ideas_markdown)
    if not path.exists():
        return fail(f"file not found: {path}")

    text = path.read_text(encoding="utf-8")
    ideas = re.findall(r"^# Idea\s+\d+\s+—\s+.+$", text, flags=re.MULTILINE)
    if len(ideas) != 10:
        return fail(f"expected 10 ideas, found {len(ideas)}")

    blocks = re.split(r"^# Idea\s+\d+\s+—\s+.+$", text, flags=re.MULTILINE)[1:]
    for idx, block in enumerate(blocks, start=1):
        for field in REQUIRED_FIELDS:
            if field not in block:
                return fail(f"idea {idx} missing field: {field}")

    print("PASS: output structure valid (10 ideas, required fields present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
