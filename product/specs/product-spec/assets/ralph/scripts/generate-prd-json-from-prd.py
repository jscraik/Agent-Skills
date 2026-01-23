#!/usr/bin/env python3
"""
Generate a Ralph loop prd.json from a PRD markdown file (spec-output.md).

What it does:
- Extracts user stories written as:
    1) **Story:** As a <persona>, I want <action> so that <benefit>.
    **Acceptance criteria:**
    - [ ] ...
    - [ ] ...
- Produces prd.json containing story tasks with acceptance criteria.

Usage:
  python3 scripts/generate-prd-json-from-prd.py spec-output.md prd.json
  # Optional: set branch name used by your Ralph policy
  python3 scripts/generate-prd-json-from-prd.py spec-output.md prd.json --branch ralph
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


STORY_START_RE = re.compile(
    r"(?im)^\s*(?:\d+[\)\.]|[-*])\s*(?:\*\*Story:\*\*|Story:)\s*(.+?)\s*$"
)
ACCEPTANCE_HEADING_RE = re.compile(
    r"(?im)^\s*\*\*Acceptance criteria:\*\*\s*$|^\s*Acceptance criteria:\s*$"
)
ACCEPTANCE_ITEM_RE = re.compile(r"(?im)^\s*[-*]\s*\[\s*\]\s+(.+?)\s*$")


@dataclass
class Story:
    raw_line: str
    as_i_want_so_that: str
    acceptance: List[str]


def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")


def extract_story_blocks(text: str) -> List[tuple[int, int, int, str]]:
    """
    Returns list of (start_idx, end_idx, start_line, story_line_content)
    """
    starts = []
    for m in STORY_START_RE.finditer(text):
        starts.append((m.start(), m.end(), m.group(1).strip()))

    blocks = []
    for i, (s_idx, s_end, story_line) in enumerate(starts):
        # End at next story start or next H2+ heading or EOF
        end_candidates = []

        if i + 1 < len(starts):
            end_candidates.append(starts[i + 1][0])

        # Stop before next heading level 2 or higher
        h = re.search(r"(?m)^#{2,6}\s+", text[s_end:])
        if h:
            end_candidates.append(s_end + h.start())

        e_idx = min(end_candidates) if end_candidates else len(text)
        start_line = text.count("\n", 0, s_idx) + 1
        blocks.append((s_idx, e_idx, start_line, story_line))
    return blocks


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def validate_story_format(line: str) -> Optional[str]:
    """
    Ensure it contains "As a..., I want..., so that..."
    """
    if re.search(r"(?i)\bAs an?\b.*?\bI want\b.*?\bso that\b", line):
        return normalize_whitespace(line)
    return None


def extract_acceptance(block: str) -> List[str]:
    """
    Find acceptance criteria items inside a block.
    """
    items = [normalize_whitespace(m.group(1)) for m in ACCEPTANCE_ITEM_RE.finditer(block)]
    return [i for i in items if i]


def build_prd_json(stories: List[Story], branch: str) -> dict:
    """
    Produce a prd.json structure usable by your Ralph harness.
    Since Ralph variants differ, we keep it conservative:
    - include `branchName`
    - include `stories` list with `title`, `prompt`, `acceptanceCriteria`
    """
    out = {
        "schemaVersion": 1,
        "branchName": branch,
        "stories": [],
    }

    for idx, s in enumerate(stories, start=1):
        title = f"Story {idx}"
        out["stories"].append(
            {
                "id": f"S-{idx:03d}",
                "title": title,
                "userStory": s.as_i_want_so_that,
                "acceptanceCriteria": s.acceptance,
            }
        )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate prd.json from a PRD markdown file.")
    ap.add_argument("input_md", help="Input PRD markdown (e.g., spec-output.md)")
    ap.add_argument("output_json", help="Output JSON path (e.g., prd.json)")
    ap.add_argument("--branch", default="ralph", help="Branch name to embed (default: ralph)")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Fail if any story is malformed or missing acceptance criteria.",
    )
    args = ap.parse_args()

    in_path = Path(args.input_md)
    out_path = Path(args.output_json)

    if not in_path.exists():
        print(f"ERROR: Input file not found: {in_path}", file=sys.stderr)
        return 1

    text = read_text(in_path)
    blocks = extract_story_blocks(text)

    if not blocks:
        print("ERROR: No 'Story:' blocks found. Use '1) **Story:** ...' format.", file=sys.stderr)
        return 1

    stories: List[Story] = []
    errors = 0

    for s_idx, e_idx, line_no, story_line in blocks:
        block = text[s_idx:e_idx]
        formatted = validate_story_format(story_line)

        if not formatted:
            msg = f"Story at L{line_no} is not in 'As a..., I want..., so that...' format."
            if args.strict:
                print(f"ERROR: {msg}", file=sys.stderr)
                errors += 1
                continue
            else:
                print(f"WARN: {msg}", file=sys.stderr)
                formatted = normalize_whitespace(story_line)

        acceptance = extract_acceptance(block)
        if not acceptance:
            msg = f"Story at L{line_no} has no acceptance criteria items '- [ ] ...'."
            if args.strict:
                print(f"ERROR: {msg}", file=sys.stderr)
                errors += 1
                continue
            else:
                print(f"WARN: {msg}", file=sys.stderr)

        stories.append(Story(raw_line=story_line, as_i_want_so_that=formatted, acceptance=acceptance))

    if errors:
        print(f"\nERROR: {errors} strict error(s); prd.json not written.", file=sys.stderr)
        return 1

    prd = build_prd_json(stories, branch=args.branch)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(prd, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} with {len(stories)} storie(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
