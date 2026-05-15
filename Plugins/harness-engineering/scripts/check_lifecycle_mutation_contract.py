#!/usr/bin/env python3
"""Check HE lifecycle stages separate local proof from live mutation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TARGET_SKILLS = {"he-eval-report", "he-linear-plan", "he-reconcile", "he-router"}
REQUIRED_TERMS = {
    "closure": "closure state missing",
    "mutation": "mutation state missing",
    "live": "live state read missing",
    "readback": "targeted readback missing",
    "confirmation": "explicit confirmation missing",
}
REQUIRED_REFERENCE = "closure-mutation-contract.md"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def check_skill(skill_dir: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    files = [skill_dir / "SKILL.md", skill_dir / "references" / "contract.yaml"]
    text = "\n".join(path.read_text(encoding="utf-8") for path in files if path.exists()).lower()
    for term, message in REQUIRED_TERMS.items():
        if term not in text:
            findings.append({"path": rel(skill_dir), "code": "LIFECYCLE_MUTATION_TERM", "message": message})
    if REQUIRED_REFERENCE not in text:
        findings.append({
            "path": rel(skill_dir),
            "code": "LIFECYCLE_MUTATION_REFERENCE",
            "message": f"missing shared reference {REQUIRED_REFERENCE}",
        })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    checked = [root / "skills" / name for name in sorted(TARGET_SKILLS)]
    findings: list[dict[str, str]] = []
    for skill_dir in checked:
        findings.extend(check_skill(skill_dir))
    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not findings else "fail",
        "checked_skills": len(checked),
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
