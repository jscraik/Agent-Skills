#!/usr/bin/env python3
"""Validate opening BLUF structure in durable HE Markdown artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FIELD_RE = re.compile(r"(?m)^(BLUF|Decision Needed|Top Risks|Next Action):\s*\S")
BLUF_RE = re.compile(r"(?m)^BLUF:\s*(\S.+)$")
BLUF_ONLY_SUMMARY_RE = re.compile(r"(?m)^##\s+BLUF-Only Summary\s*$")
BLUF_HEADING_RE = re.compile(r"(?m)^#{2,6}\s+BLUF\b")
VAGUE_BLUF_RE = re.compile(
    r"\b(explores|considerations|various|potentially|range of|aims to|seeks to)\b",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(approve|block|revise|split|build|plan|implement|handoff|route|stop|next|must|should|needs?)\b",
    re.IGNORECASE,
)
RISK_RE = re.compile(
    r"\b(risk|blocked|blocker|unsafe|unclear|missing|fails?|failure|drift|consequence|because|until)\b",
    re.IGNORECASE,
)


def strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        parts = text.split("---\n", 2)
        if len(parts) == 3:
            return parts[2]
    return text


def validate(path: Path, *, compact: bool) -> list[str]:
    _ = compact
    text = strip_frontmatter(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if "## Command Summary" not in text:
        errors.append("missing ## Command Summary")
    else:
        command_summary = text.split("## Command Summary", 1)[1].split("\n## ", 1)[0]
        found_fields = {match.group(1) for match in FIELD_RE.finditer(command_summary)}
        for field in ("BLUF", "Decision Needed", "Top Risks", "Next Action"):
            if field not in found_fields:
                errors.append(f"Command Summary missing non-empty {field}:")

    if BLUF_ONLY_SUMMARY_RE.search(text):
        errors.append("BLUF-Only Summary is no longer allowed; use one opening BLUF paragraph")
    if BLUF_HEADING_RE.search(text):
        errors.append("BLUF must be a single opening field, not a repeated heading")

    bluf_matches = list(BLUF_RE.finditer(text))
    blufs = [match.group(1).strip() for match in bluf_matches]
    if not blufs:
        errors.append("missing non-empty opening BLUF line")
    if len(blufs) > 1:
        errors.append(f"expected exactly one BLUF line, found {len(blufs)}")
    if bluf_matches and "## Command Summary" in text:
        command_summary = text.split("## Command Summary", 1)[1].split("\n## ", 1)[0]
        if bluf_matches[0].group(0) not in command_summary:
            errors.append("BLUF must appear inside the opening Command Summary")
    for index, bluf in enumerate(blufs, start=1):
        word_count = len(bluf.split())
        if word_count < 12:
            errors.append(f"BLUF {index} is too short ({word_count} words)")
        if word_count > 120:
            errors.append(f"BLUF {index} is too long ({word_count} words)")
        if bluf.endswith(":"):
            errors.append(f"BLUF {index} ends like a label instead of a sentence")
        if VAGUE_BLUF_RE.search(bluf):
            errors.append(f"BLUF {index} uses vague review prose instead of a bottom line")
        if not ACTION_RE.search(bluf):
            errors.append(f"BLUF {index} does not state a decision, action, or next step")
        if not RISK_RE.search(bluf):
            errors.append(f"BLUF {index} does not state a risk, blocker, consequence, or reason")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Accepted for compatibility; BLUF-Only Summary is not required",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = []
    failed = False
    for path in args.paths:
        errors = validate(path, compact=args.compact)
        failed = failed or bool(errors)
        results.append({"path": str(path), "status": "pass" if not errors else "fail", "errors": errors})

    result = {"schema_version": 1, "status": "fail" if failed else "pass", "results": results}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for item in results:
            print(f"{item['path']}: {item['status']}")
            for error in item["errors"]:
                print(f"  error: {error}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
