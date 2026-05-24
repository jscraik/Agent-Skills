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
    """
    Finds SKILL.md entrypoint files under the plugin's skills directory.
    
    Parameters:
        root (Path): Path to the plugin repository root; the function looks for files under root / "skills".
    
    Returns:
        list[Path]: Sorted list of matching SKILL.md file paths (one per immediate subdirectory of skills).
    """
    skills_root = root / "skills"
    return sorted(skills_root.glob("*/SKILL.md"))


def validate(root: Path) -> list[str]:
    """
    Check each SKILL.md under the plugin root's skills directory for required stage-arc and persona-lens terms.
    
    Parameters:
        root (Path): Plugin repository root; the function searches for SKILL.md files directly under the immediate subdirectories of <root>/skills.
    
    Returns:
        list[str]: A list of error messages. Returns an empty list when all SKILL.md files contain the required terms. If no SKILL.md files are found, returns a single-item list: "no skill entrypoints found under <root>/skills". For files missing terms, each message is formatted as "<relative path> missing stage arc coverage: term1, term2".
    """
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
    """
    CLI entry point that validates SKILL.md files under a plugin root and prints the results.
    
    Parses command-line arguments to determine the plugin root and output mode, runs validation of discovered SKILL.md files for required stage-arc and persona-lens terms, and emits either JSON or human-readable output.
    
    Returns:
        int: Exit status code — 0 when all checked skills contain the required terms, 1 when any validation errors were found.
    """
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
