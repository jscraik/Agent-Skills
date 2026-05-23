#!/usr/bin/env python3
"""Verify repo-wide question lifecycle contract hygiene."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    message: str


REPO_ROOT = Path(__file__).resolve().parents[3]

FORBIDDEN_SKILL_PHRASES = (
    "collect user feedback before closing the run",
    "collect user feedback via request_user_input before closing the run",
    "collect user feedback via askquestion parity before closing the run",
)

REQUIRED_FILES = (
    REPO_ROOT / "Docs/skill-graphs/question-lifecycle.md",
    REPO_ROOT / "Docs/skill-graphs/schemas/question-event.schema.md",
)

REQUIRED_LINKS = (
    (
        REPO_ROOT / "Docs/skill-graphs/index.md",
        "/Docs/skill-graphs/question-lifecycle.md",
        "skill-graphs index must link to question lifecycle contract",
    ),
    (
        REPO_ROOT / "Docs/skill-graphs/schemas/index.md",
        "/Docs/skill-graphs/schemas/question-event.schema.md",
        "schema index must link to question event schema",
    ),
    (
        REPO_ROOT / "Docs/skill-graphs/question-lifecycle.md",
        "/Users/jamiecraik/dev/agent-skills/Docs/skill-graphs/schemas/question-event.schema.md",
        "question lifecycle contract must reference the machine-readable schema path",
    ),
)


EXCLUDED_SCAN_ROOTS = (
    REPO_ROOT / ".agents",
    REPO_ROOT / ".skillsets",
    REPO_ROOT / "Plugins" / "cache",
    REPO_ROOT / "plugins" / "cache",
)


def should_scan_path(path: Path) -> bool:
    """Return whether a path belongs to a canonical source tree."""
    # Check lexical path first
    for root in EXCLUDED_SCAN_ROOTS:
        try:
            path.relative_to(root)
            return False
        except ValueError:
            continue
    # Check resolved path
    try:
        resolved = path.resolve(strict=False)
    except OSError:
        resolved = path
    for root in EXCLUDED_SCAN_ROOTS:
        try:
            resolved.relative_to(root)
            return False
        except ValueError:
            continue
    return True


def find_forbidden_skill_phrases() -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(REPO_ROOT.rglob("SKILL.md")):
        if not should_scan_path(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            findings.append(Finding(path, 1, f"unable to read file: {exc}"))
            continue
        for idx, line in enumerate(lines, start=1):
            lower = line.lower()
            for phrase in FORBIDDEN_SKILL_PHRASES:
                if phrase in lower:
                    findings.append(
                        Finding(
                            path,
                            idx,
                            f"forbidden question-timing phrase found in SKILL.md: {phrase}",
                        )
                    )
    return findings


def find_stale_graph_references() -> list[Finding]:
    findings: list[Finding] = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if not should_scan_path(path):
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            findings.append(Finding(path, 1, f"unable to read file: {exc}"))
            continue
        for idx, line in enumerate(lines, start=1):
            if "Infrastructure/references/skill-knowledge-graph.md" in line:
                findings.append(
                    Finding(
                        path,
                        idx,
                        "stale skill knowledge graph reference found; use canonical skill-graphs docs instead",
                    )
                )
    return findings


def find_missing_files_and_links() -> list[Finding]:
    findings: list[Finding] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            findings.append(Finding(path, 1, "required question lifecycle contract file is missing"))

    for path, needle, message in REQUIRED_LINKS:
        if not path.exists():
            findings.append(Finding(path, 1, f"required file missing for link check: {message}"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            findings.append(Finding(path, 1, f"unable to read file: {exc}"))
            continue
        if needle.lower() not in text.lower():
            findings.append(Finding(path, 1, message))

    return findings


def main() -> int:
    findings = [
        *find_forbidden_skill_phrases(),
        *find_stale_graph_references(),
        *find_missing_files_and_links(),
    ]

    if findings:
        print("FAIL verify_question_lifecycle_contract")
        for finding in findings:
            rel = finding.path.relative_to(REPO_ROOT)
            print(f"{rel}:{finding.line}: {finding.message}")
        return 2

    print("PASS verify_question_lifecycle_contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
