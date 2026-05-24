#!/usr/bin/env python3
"""Validate HE skills expose stage arc boundaries and persona lenses."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_TERMS = (
    "stage_arc_boundary",
    "left_arc",
    "active_arc",
    "right_arc",
    "coding_lens",
    "testing_lens",
    "stage-arc-boundary-contract.md",
)


def skill_files(root: Path) -> list[Path]:
    skills_root = root / "skills"
    return sorted(skills_root.glob("*/SKILL.md"))


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    files = skill_files(root)
    if not files:
        return [f"no skill entrypoints found under {root / 'skills'}"]
    for path in files:
        text = path.read_text(encoding="utf-8")
        lower = text.lower()
        missing = [term for term in REQUIRED_TERMS if term.lower() not in lower]
        if missing:
            rel = path.relative_to(root)
            errors.append(f"{rel} missing stage arc coverage: {', '.join(missing)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "plugin_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.plugin_root.resolve()
    errors = validate(root)
    result = {
        "schema_version": 1,
        "plugin_root": str(root),
        "skills_checked": len(skill_files(root)),
        "status": "pass" if not errors else "fail",
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for error in errors:
            print(f"error: {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
