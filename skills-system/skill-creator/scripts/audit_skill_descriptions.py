#!/usr/bin/env python3
"""Audit SKILL.md descriptions for agent-routing quality.

By default this is report-only so existing skills can be migrated before the
description contract becomes a hard package gate. Use --strict to fail when any
skill description does not satisfy the scaffold-time description rules.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from init_skill import validate_description


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _load_frontmatter(skill_md: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        return None, f"read_error: {exc}"

    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, "missing_or_invalid_frontmatter"

    frontmatter: dict[str, Any] = {}
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if not key or value.strip() == "":
            continue
        frontmatter[key] = _parse_scalar(value)
    return frontmatter, None


def _iter_skill_files(paths: list[Path]) -> list[Path]:
    skill_files: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved.is_file() and resolved.name == "SKILL.md":
            skill_files.append(resolved)
        elif resolved.is_dir():
            if (resolved / "SKILL.md").is_file():
                skill_files.append((resolved / "SKILL.md").resolve())
            else:
                skill_files.extend(sorted(resolved.rglob("SKILL.md")))
    return sorted(dict.fromkeys(skill_files))


def audit_skill(skill_md: Path, repo_root: Path | None = None) -> dict[str, Any]:
    frontmatter, load_error = _load_frontmatter(skill_md)
    rel_path = str(skill_md)
    if repo_root is not None:
        try:
            rel_path = str(skill_md.relative_to(repo_root))
        except ValueError:
            rel_path = str(skill_md)

    if load_error:
        return {
            "path": rel_path,
            "status": "fail",
            "description": None,
            "reason": load_error,
        }

    description = frontmatter.get("description") if frontmatter else None
    if not isinstance(description, str):
        return {
            "path": rel_path,
            "status": "fail",
            "description": description,
            "reason": "description_missing_or_not_string",
        }

    reason = validate_description(description)
    return {
        "path": rel_path,
        "status": "pass" if reason is None else "fail",
        "description": description.strip(),
        "reason": reason,
    }


def build_report(paths: list[Path], repo_root: Path | None = None) -> dict[str, Any]:
    skill_files = _iter_skill_files(paths)
    results = [audit_skill(skill_md, repo_root=repo_root) for skill_md in skill_files]
    failures = [result for result in results if result["status"] != "pass"]
    return {
        "schema_version": "1.0",
        "check": "skill_description_routing_quality",
        "status": "pass" if not failures else "warn",
        "summary": {
            "skills_checked": len(results),
            "pass": len(results) - len(failures),
            "fail": len(failures),
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit SKILL.md descriptions for agent-routing quality."
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Skill directories, SKILL.md files, or roots containing skills.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Optional repository root used to shorten reported paths.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero when any description fails the routing-quality contract.",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).expanduser().resolve() if args.repo_root else None
    report = build_report([Path(path) for path in args.paths], repo_root=repo_root)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "skill-description audit: "
            f"{summary['pass']} passed, {summary['fail']} flagged, "
            f"{summary['skills_checked']} checked"
        )
        for result in report["results"]:
            if result["status"] != "pass":
                print(f"- {result['path']}: {result['reason']}")

    if args.strict and report["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
