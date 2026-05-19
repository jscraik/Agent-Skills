#!/usr/bin/env python3
"""Validate active HE skill references resolve to canonical plugin files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REFERENCE_RE = re.compile(r"`([^`\n]+\.(?:md|yaml|yml|json|py))`")
FORBIDDEN_ACTIVE_PATH_PARTS = ("/archive/", "budget-archive", "deferred-store", "/cache/", ".agents/")
IGNORED_PREFIXES = ("http://", "https://", "~/.codex/", "~/.agents/", ".harness/")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def iter_checked_files(root: Path) -> list[Path]:
    files = list((root / "skills").glob("*/SKILL.md"))
    files.extend((root / "skills").glob("*/references/*.yaml"))
    files.extend((root / "skills").glob("*/references/*.md"))
    return sorted(path for path in files if path.is_file())


def resolve_reference(source: Path, reference: str, root: Path) -> Path | None:
    if reference.startswith(IGNORED_PREFIXES):
        return None
    if reference.startswith("Plugins/harness-engineering/"):
        return repo_root() / reference
    if reference.startswith("../../references/"):
        return root / "references" / reference.removeprefix("../../references/")
    if reference.startswith("references/"):
        if source.parent.name == "references":
            return source.parent.parent / reference
        return source.parent / reference
    if reference.startswith("./"):
        return source.parent / reference.removeprefix("./")
    if reference.startswith("../"):
        return source.parent / reference
    return None


def check_file(path: Path, root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("prompt:"):
            continue
        for match in REFERENCE_RE.finditer(line):
            reference = match.group(1)
            lowered = reference.lower()
            if any(part in lowered for part in FORBIDDEN_ACTIVE_PATH_PARTS):
                findings.append({
                    "path": rel(path),
                    "code": "REFERENCE_FORBIDDEN_ACTIVE_AUTHORITY",
                    "message": f"active reference uses generated/archive/cache path: {reference}",
                })
                continue
            target = resolve_reference(path, reference, root)
            if target is None:
                continue
            if not target.exists():
                findings.append({
                    "path": rel(path),
                    "code": "REFERENCE_MISSING",
                    "message": f"referenced file does not exist: {reference}",
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    checked = iter_checked_files(root)
    findings: list[dict[str, str]] = []
    for path in checked:
        findings.extend(check_file(path, root))

    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not findings else "fail",
        "checked_files": len(checked),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"status: {result['status']}")
        for finding in findings:
            print(f"{finding['code']}: {finding['path']}: {finding['message']}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
