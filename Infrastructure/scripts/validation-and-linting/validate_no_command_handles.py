#!/usr/bin/env python3
"""Fail when active user-facing surfaces reintroduce command-handle guidance."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Rule:
    path: str
    pattern: re.Pattern[str]
    message: str


SKILL_DESCRIPTION_ROOTS = (
    "Skills",
    "Plugins",
)

AGENT_METADATA_ROOTS = (
    "Skills",
    "Plugins",
)

RUNTIME_IDENTIFIER_PLACEHOLDER_PATHS = (
    "AGENTS.md",
    "Docs/agents/19-high-signal-steering-feedback.md",
    "Docs/agents/README.md",
    "Infrastructure/scripts/README.md",
    ".harness/quality/steering-uptake.md",
)

RULES = [
    Rule(
        "Infrastructure/scripts/lib/ask/command_metadata.py",
        re.compile(r"\bhe-[a-z0-9-]+\b|\$he-|skill-factory-router|skills handles\b"),
        "Command metadata must use canonical source paths or discovery commands, not command handles.",
    ),
    Rule(
        "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
        re.compile(r"\b(?:he-brainstorm|he-spec|he-plan|he-work|he-technical-review|he-reliability-review|he-phase-work|he-fix-bugs)\b|skills handles --check|command[- ]surface handles?"),
        "Skill routing must use current skill targets, not retired command handles.",
    ),
    Rule(
        "Infrastructure/bin/ask",
        re.compile(r"skill handles?|skills handles --check|command[- ]surface handles?"),
        "CLI help must describe skill targets/source paths, not command handles.",
    ),
    Rule(
        "Infrastructure/scripts/lifecycle-and-sync/command_surface.py",
        re.compile(r"skills handles --check|command[- ]surface handles?"),
        "Command-surface recovery text must not direct agents back to command handles.",
    ),
    Rule(
        "Infrastructure/scripts/README.md",
        re.compile(r"skills handles --check|command[- ]surface handles?"),
        "Infrastructure docs must not advertise command-handle validation as active guidance.",
    ),
]

SKILL_DESCRIPTION_DOLLAR_PATTERN = re.compile(r"\$[A-Za-z][A-Za-z0-9_-]*")
SKILL_FRONTMATTER_HANDLE_KEY_PATTERN = re.compile(r"^\s*(handles|canonical_handle):\s*")
RUNTIME_IDENTIFIER_PLACEHOLDER_PATTERN = re.compile(
    r"\b(?:cell_id|session_id|tool_call_id|command_id|handle)\b\s*[:=]\s*"
    r"[\"'](?:noop|noop\d+|fake|dummy|placeholder|test|nonexistent\d*)[\"']",
    re.IGNORECASE,
)


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _is_plugin_cache_path(path: Path) -> bool:
    return "Plugins/cache" in _relative(path)


def _iter_findings(rules: Iterable[Rule]) -> Iterable[dict[str, object]]:
    for rule in rules:
        path = ROOT / rule.path
        if not path.exists():
            yield {"path": rule.path, "line": None, "message": "Expected active surface is missing."}
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = rule.pattern.search(line)
            if match:
                yield {
                    "path": _relative(path),
                    "line": line_number,
                    "match": match.group(0),
                    "message": rule.message,
                }


def _frontmatter_description_line(path: Path) -> tuple[int, str] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line_number, line in enumerate(text[:end].splitlines(), start=1):
        if line.strip().startswith("description:"):
            return line_number, line
    return None


def _frontmatter_lines(path: Path) -> Iterable[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return
    end = text.find("\n---", 4)
    if end == -1:
        return
    for line_number, line in enumerate(text[:end].splitlines(), start=1):
        yield line_number, line


def _iter_skill_description_findings() -> Iterable[dict[str, object]]:
    for root_name in SKILL_DESCRIPTION_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            if _is_plugin_cache_path(path):
                continue
            description = _frontmatter_description_line(path)
            if description is None:
                continue
            line_number, line = description
            match = SKILL_DESCRIPTION_DOLLAR_PATTERN.search(line)
            if match:
                yield {
                    "path": _relative(path),
                    "line": line_number,
                    "match": match.group(0),
                    "message": "Skill description metadata must use natural trigger language, not $skill trigger notation.",
                }


def _iter_skill_frontmatter_handle_findings() -> Iterable[dict[str, object]]:
    for root_name in SKILL_DESCRIPTION_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            if _is_plugin_cache_path(path):
                continue
            for line_number, line in _frontmatter_lines(path):
                match = SKILL_FRONTMATTER_HANDLE_KEY_PATTERN.search(line)
                if match:
                    yield {
                        "path": _relative(path),
                        "line": line_number,
                        "match": match.group(1),
                        "message": "Skill frontmatter must not carry legacy command-handle metadata.",
                    }


def _iter_agent_metadata_findings() -> Iterable[dict[str, object]]:
    for root_name in AGENT_METADATA_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for pattern in ("agents/*.yaml", "agents/*.yml"):
            for path in sorted(root.rglob(pattern)):
                if _is_plugin_cache_path(path):
                    continue
                for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                    match = SKILL_DESCRIPTION_DOLLAR_PATTERN.search(line)
                    if match:
                        yield {
                            "path": _relative(path),
                            "line": line_number,
                            "match": match.group(0),
                            "message": "Agent UI metadata must use natural language, not $skill trigger notation.",
                        }


def _iter_runtime_identifier_placeholder_findings() -> Iterable[dict[str, object]]:
    for path_text in RUNTIME_IDENTIFIER_PLACEHOLDER_PATHS:
        path = ROOT / path_text
        if not path.exists():
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = RUNTIME_IDENTIFIER_PLACEHOLDER_PATTERN.search(line)
            if match:
                yield {
                    "path": _relative(path),
                    "line": line_number,
                    "match": match.group(0),
                    "message": (
                        "Agent-facing guidance must not include fabricated runtime identifier "
                        "examples for wait, resume, retry, or closeout actions."
                    ),
                }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable output.")
    args = parser.parse_args()

    findings = [
        *_iter_findings(RULES),
        *_iter_skill_description_findings(),
        *_iter_skill_frontmatter_handle_findings(),
        *_iter_agent_metadata_findings(),
        *_iter_runtime_identifier_placeholder_findings(),
    ]
    payload = {
        "schema_version": "no-command-handles.v1",
        "status": "fail" if findings else "pass",
        "checked_paths": [
            *[rule.path for rule in RULES],
            *[f"{root}/**/SKILL.md frontmatter descriptions" for root in SKILL_DESCRIPTION_ROOTS],
            *[f"{root}/**/SKILL.md legacy handle metadata" for root in SKILL_DESCRIPTION_ROOTS],
            *[f"{root}/**/agents/*.yaml metadata" for root in AGENT_METADATA_ROOTS],
            *[f"{path} runtime placeholder identifiers" for path in RUNTIME_IDENTIFIER_PLACEHOLDER_PATHS],
        ],
        "findings": findings,
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif findings:
        print("Command-handle guard failed:")
        for finding in findings:
            print(f"- {finding['path']}:{finding['line']} {finding['message']} ({finding.get('match')})")
    else:
        print("Command-handle guard passed.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
