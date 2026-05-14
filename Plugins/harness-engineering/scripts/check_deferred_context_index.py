#!/usr/bin/env python3
"""Detect stale active-procedure snapshots in the HE deferred context index.

The index should route meaningful moved context, not preserve every line removed
from compacted SKILL.md files. Stale, duplicated, unsafe, inappropriate,
superseded, or low-signal text should be dispositioned outside this index rather
than pasted here.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROCEDURE_PATTERNS = [
    re.compile(r"(?mi)^Return schema_version when structured\."),
    re.compile(r"(?mi)^Inspect session-collector evidence"),
    re.compile(r"(?mi)^Explore first, ask second"),
    re.compile(r"(?mi)^Mark current active state"),
    re.compile(r"(?mi)^Route with `route_skillset\.py`"),
]

REFERENCE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])(?:`|\()?\s*(references/[A-Za-z0-9._/-]+\.md)(?:`|\))?")


def validate(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    plugin_root = path.resolve().parents[1]
    if "```" in text:
        errors.append(
            "deferred context index must not contain copied code fences; route "
            "meaningful moved context to references and discard stale or "
            "inappropriate fragments instead of preserving them here"
        )
    if re.search(r"(?i)exact retired lines are preserved", text):
        errors.append(
            "deferred context index must not preserve exact retired lines; use "
            "moved-to-reference, superseded, intentionally-discarded, or "
            "not-context disposition notes"
        )
    for pattern in PROCEDURE_PATTERNS:
        if pattern.search(text):
            errors.append(f"deferred context index contains active procedure text: {pattern.pattern}")
    if text.count("references/goal-continuity.md") > 1:
        errors.append("goal-continuity reference appears more than once")
    seen_references: set[str] = set()
    for match in REFERENCE_PATH_RE.finditer(text):
        reference = match.group(1)
        if reference in seen_references:
            continue
        seen_references.add(reference)
        if not (plugin_root / reference).is_file():
            errors.append(f"deferred context index references missing file: {reference}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "references" / "deferred-context-index.md",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    errors = validate(args.path)
    result = {
        "schema_version": 1,
        "path": str(args.path),
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
