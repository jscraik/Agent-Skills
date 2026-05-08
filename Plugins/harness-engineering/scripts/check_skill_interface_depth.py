#!/usr/bin/env python3
"""Check HE skill entrypoints stay deep, compact, and procedure-oriented."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


MAX_PROCEDURE_LINE_LENGTH = 420
MAX_UNNUMBERED_PROCEDURE_LINES = 1


def section_body(text: str, section: str) -> str:
    pattern = rf"(?ms)^##\s+{re.escape(section)}\s*$\n(?P<body>.*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text)
    return match.group("body").strip() if match else ""


def validate_skill(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    procedure = section_body(text, "Procedure")
    if not procedure:
        return [f"{path}: missing Procedure section"]

    raw_lines = [line for line in procedure.splitlines() if line.strip()]
    lines = [line.strip() for line in raw_lines]
    numbered = [line for line in lines if re.match(r"^\d+\.\s+", line)]
    unnumbered = [
        raw_line.strip()
        for raw_line in raw_lines
        if not re.match(r"^\d+\.\s+", raw_line.strip()) and not raw_line.startswith((" ", "\t"))
    ]

    if numbered and len(unnumbered) > MAX_UNNUMBERED_PROCEDURE_LINES:
        errors.append(f"{path}: Procedure mixes numbered flow with too many unnumbered lines")
    if not numbered and len(lines) > MAX_UNNUMBERED_PROCEDURE_LINES:
        errors.append(f"{path}: Procedure should use numbered steps or a single compact directive")

    for line in lines:
        if len(line) > MAX_PROCEDURE_LINE_LENGTH:
            errors.append(f"{path}: Procedure line exceeds {MAX_PROCEDURE_LINE_LENGTH} characters")

    if "stage-context-contract.md" in text and "Stage context:" not in text:
        errors.append(f"{path}: references stage context contract without a named References entry")

    return errors


def validate(root: Path) -> list[str]:
    skill_paths = sorted((root / "skills").glob("he-*/SKILL.md"))
    errors: list[str] = []
    for path in skill_paths:
        errors.extend(validate_skill(path))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    errors = validate(root)
    result = {
        "schema_version": 1,
        "root": str(root),
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
