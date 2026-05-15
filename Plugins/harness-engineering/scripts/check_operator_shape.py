#!/usr/bin/env python3
"""Validate HE stage skills carry the Skill Factory operator shape."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_CONTRACT_MARKERS = {
    "operator_contract:": "missing operator_contract block",
    "description_contract:": "missing description contract",
    "immediate_operator_path:": "missing immediate operator path",
    "source_order:": "missing source order",
    "tool_resolution:": "missing tool resolution",
    "freshness_rule:": "missing freshness rule",
    "boundaries:": "missing boundaries",
    "retry_and_stop:": "missing retry/stop rule",
    "validation_tiers:": "missing validation tiers",
    "concise_output:": "missing concise output contract",
}

REQUIRED_EVAL_CASES = {
    "happy-operator-path": "missing happy operator-path eval",
    "edge-missing-inputs-proceed": "missing missing-input proceed eval",
    "pressure-no-governance-bloat": "missing governance-bloat pressure eval",
    "pressure-live-not-archive": "missing live-source pressure eval",
    "negative-neighboring-lane": "missing neighboring-lane negative eval",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def iter_skill_dirs(root: Path) -> list[Path]:
    skills_root = root / "skills"
    if not skills_root.exists():
        return []
    return sorted(path.parent for path in skills_root.glob("*/SKILL.md"))


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)


def check_skill(skill_dir: Path, _root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    contract = skill_dir / "references" / "contract.yaml"
    evals = skill_dir / "references" / "evals.yaml"

    if not contract.exists():
        findings.append({"path": rel(skill_dir), "code": "CONTRACT_MISSING", "message": "missing references/contract.yaml"})
    else:
        text = contract.read_text(encoding="utf-8")
        for marker, message in REQUIRED_CONTRACT_MARKERS.items():
            if marker not in text:
                findings.append({"path": rel(contract), "code": "CONTRACT_SHAPE", "message": message})

    if not evals.exists():
        findings.append({"path": rel(skill_dir), "code": "EVALS_MISSING", "message": "missing references/evals.yaml"})
    else:
        text = evals.read_text(encoding="utf-8")
        for case_id, message in REQUIRED_EVAL_CASES.items():
            if f"id: {case_id}" not in text:
                findings.append({"path": rel(evals), "code": "EVAL_SHAPE", "message": message})

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    skill_dirs = iter_skill_dirs(root)
    findings: list[dict[str, str]] = []
    for skill_dir in skill_dirs:
        findings.extend(check_skill(skill_dir, root))

    result = {
        "schema_version": 1,
        "root": str(root),
        "status": "pass" if not findings else "fail",
        "checked_skills": len(skill_dirs),
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
