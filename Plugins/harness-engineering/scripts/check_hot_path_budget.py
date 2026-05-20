#!/usr/bin/env python3
"""Check HE skill entrypoints stay compact and free of obvious prompt rot."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SOFT_LINE_BUDGET = 140
HARD_LINE_BUDGET = 240
MAX_REFERENCE_MENTIONS = 30
MAX_BLOCKER_WORDS = 55
BLOCKER_RE = re.compile(r"\b(must|required|fail fast|stop|blocked|forbidden|do not|never)\b", re.IGNORECASE)
REFERENCE_RE = re.compile(r"(?:references/|\.\./\.\./references/|Plugins/harness-engineering/references/)")
FRAGMENT_RE = re.compile(r"^references with a clear route\.$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def iter_skill_files(root: Path) -> list[Path]:
    return sorted((root / "skills").glob("*/SKILL.md"))


def duplicate_paragraphs(text: str) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        normalized = " ".join(paragraph.split())
        if len(normalized) < 80:
            continue
        if normalized in seen:
            duplicates.append(normalized[:120])
        seen.add(normalized)
    return duplicates


def check_skill(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    findings: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    line_count = len(lines)
    reference_mentions = len(REFERENCE_RE.findall(text))
    blocker_words = len(BLOCKER_RE.findall(text))

    def add(target: list[dict[str, str]], code: str, message: str) -> None:
        target.append({"path": rel(path), "code": code, "message": message})

    if line_count > HARD_LINE_BUDGET:
        add(findings, "HOT_PATH_HARD_BUDGET", f"SKILL.md has {line_count} lines; hard budget is {HARD_LINE_BUDGET}")
    elif line_count > SOFT_LINE_BUDGET:
        add(warnings, "HOT_PATH_SOFT_BUDGET", f"SKILL.md has {line_count} lines; consider moving bulky detail to references")

    if reference_mentions > MAX_REFERENCE_MENTIONS:
        add(warnings, "HOT_PATH_REFERENCE_DENSITY", f"{reference_mentions} reference mentions; entrypoint may be acting as an index")
    if blocker_words > MAX_BLOCKER_WORDS:
        add(warnings, "HOT_PATH_BLOCKER_DENSITY", f"{blocker_words} blocker words; entrypoint may be over-blocking")

    for index, line in enumerate(lines, start=1):
        if FRAGMENT_RE.match(line.strip()):
            findings.append({"path": f"{rel(path)}:{index}", "code": "HOT_PATH_FRAGMENT", "message": "dangling context-disposition fragment"})

    for duplicate in duplicate_paragraphs(text):
        add(findings, "HOT_PATH_DUPLICATE_PARAGRAPH", f"duplicated paragraph starts: {duplicate}")

    return findings, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    findings: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    for skill_file in iter_skill_files(root):
        skill_findings, skill_warnings = check_skill(skill_file)
        findings.extend(skill_findings)
        warnings.extend(skill_warnings)

    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not findings else "fail",
        "checked_skills": len(iter_skill_files(root)),
        "findings": findings,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for finding in findings:
            print(f"{finding['code']}: {finding['path']}: {finding['message']}")
        for warning in warnings:
            print(f"warning {warning['code']}: {warning['path']}: {warning['message']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
