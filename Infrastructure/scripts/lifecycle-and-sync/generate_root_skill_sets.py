#!/usr/bin/env python3
"""Generate rooted runtime skill-set entrypoints."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skillset_model import ROOT_SKILL_SET_METADATA, modules_by_skill_set, build_skill_modules, rel, repo_root

TEMPLATE = repo_root() / "Infrastructure" / "templates" / "root-skill-set" / "SKILL.md.j2"
DEFAULT_OUTPUT_DIR = repo_root() / ".agents" / "skills"
MAX_DESCRIPTION_WORDS = 35
MAX_BODY_WORDS = 250


def word_count(text: str) -> int:
    return len([word for word in text.split() if word.strip()])


def render_template(skill_set_name: str, metadata: dict[str, str]) -> str:
    title = skill_set_name.replace("-", " ").title()
    template = TEMPLATE.read_text(encoding="utf-8")
    replacements = {
        "{{ skill_set_name }}": skill_set_name,
        "{{ short_mutually_exclusive_description }}": metadata["description"],
        "{{ title }}": title,
        "{{ scope }}": metadata["scope"],
        "{{ exclusions }}": metadata["exclusions"],
    }
    rendered = template
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    return rendered


def build_roots(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    modules, unmapped = build_skill_modules()
    grouped = modules_by_skill_set(modules)
    roots = []
    violations: list[dict[str, Any]] = []
    for name in ROOT_SKILL_SET_NAMES:
        metadata = ROOT_SKILL_SET_METADATA[name]
        body = render_template(name, metadata)
        description_words = word_count(metadata["description"])
        body_words = word_count(body)
        root_path = output_dir / name / "SKILL.md"
        root = {
            "name": name,
            "path": rel(root_path),
            "description_words": description_words,
            "body_words": body_words,
            "module_count": len(grouped.get(name, [])),
            "content": body,
        }
        roots.append(root)
        if description_words > MAX_DESCRIPTION_WORDS:
            violations.append({"code": "ROOT_DESCRIPTION_TOO_LONG", "name": name, "words": description_words})
        if body_words > MAX_BODY_WORDS:
            violations.append({"code": "ROOT_BODY_TOO_LONG", "name": name, "words": body_words})
    return {
        "status": "pass" if not violations else "fail",
        "projection_mode": "rooted",
        "policy_identity": policy_identity(),
        "root_count": len(roots),
        "roots": roots,
        "unmapped": unmapped,
        "violations": violations,
    }


def write_roots(report: dict[str, Any], output_dir: Path) -> list[dict[str, str]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    writes: list[dict[str, str]] = []
    for root in report["roots"]:
        root_dir = output_dir / root["name"]
        if root_dir.exists() or root_dir.is_symlink():
            if root_dir.is_symlink() or root_dir.is_file():
                root_dir.unlink()
            elif root_dir.is_dir():
                shutil.rmtree(root_dir)
        root_dir.mkdir(parents=True, exist_ok=True)
        target = root_dir / "SKILL.md"
        target.write_text(root["content"], encoding="utf-8")
        writes.append({"path": rel(target), "action": "write"})
    return writes


def public_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        **report,
        "roots": [
            {key: value for key, value in root.items() if key != "content"}
            for root in report["roots"]
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_roots(args.output_dir)
    writes: list[dict[str, str]] = []
    if args.write and not args.dry_run:
        if report["status"] != "pass":
            if args.json:
                print(json.dumps(public_report(report), indent=2, sort_keys=True))
            return 1
        writes = write_roots(report, args.output_dir)
    payload = {**public_report(report), "writes": writes, "dry_run": bool(args.dry_run or not args.write)}
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"root skill sets: {payload['status']} ({payload['root_count']} roots)")
        for violation in payload["violations"]:
            print(f"- {violation['code']}: {violation.get('name')}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
