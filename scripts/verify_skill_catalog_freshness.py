#!/usr/bin/env python3
"""Verify skill catalog freshness and metadata quality constraints."""

from __future__ import annotations

import argparse
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKIP_DIRS = {
    '.git',
    'artifacts',
    'node_modules',
    'docs',
    'skills',
    'skills-antigravity',
    'skills-antigravity-test',
    'templates',
    'references',
    'skills-system',
    '.worktrees',
}

PILOT_SKILL_PROFILE_PATHS = {
    "utilities/skill-builder",
    "frontend/tools/agentation",
    "utilities/systematic-debugging",
    "interview/interview-me",
}
LEARNING_POSTURE_VALUES = {"learn", "guided", "execute"}
AUTOPILOT_DEGRADED_ACCEPTED = "degraded_pairings_acknowledged"
def parse_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def validate_learning_posture_profile(profile: Dict[str, Any], issues: List[str]) -> None:
    learning_posture = profile.get("learning_posture")
    if not isinstance(learning_posture, dict):
        issues.append("pilot skill missing required task-profile learning_posture block")
        return

    supported = learning_posture.get("supported")
    if not isinstance(supported, list) or not supported:
        issues.append("learning_posture.supported must be a non-empty list")
        return

    clean_supported = []
    for item in supported:
        posture = str(item).strip()
        if posture not in LEARNING_POSTURE_VALUES:
            issues.append(f"learning_posture.supported contains invalid value: `{posture}`")
        else:
            clean_supported.append(posture)

    default = str(learning_posture.get("default", "")).strip()
    if default not in LEARNING_POSTURE_VALUES:
        issues.append("learning_posture.default must be learn|guided|execute")
    elif default not in clean_supported:
        issues.append("learning_posture.default must be included in learning_posture.supported")

    delegation_mode = str(profile.get("delegation", {}).get("mode", "")).strip().lower()
    if delegation_mode == "autopilot":
        if "learn" in clean_supported:
            issues.append("invalid posture/mode pairing: autopilot cannot support learn")
        if "guided" in clean_supported:
            acknowledged = learning_posture.get(AUTOPILOT_DEGRADED_ACCEPTED)
            if not isinstance(acknowledged, list) or not acknowledged:
                issues.append(
                    "autopilot + guided is degraded and requires explicit "
                    "degraded_pairings_acknowledged entries"
                )
    elif delegation_mode in {"manual", "co-pilot"}:
        return
    elif delegation_mode:
        issues.append(f"delegation.mode must be autopilot | co-pilot | manual, found `{delegation_mode}`")
    else:
        issues.append("delegation.mode missing while validating pilot learning_posture constraints")


def discover_skill_files(repo_root: Path) -> List[Path]:
    files: List[Path] = []
    for p in sorted(repo_root.rglob('SKILL.md')):
        rel = p.relative_to(repo_root)
        if rel.as_posix() == 'SKILL.md':
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        files.append(p)
    return files


def parse_frontmatter(path: Path) -> Dict[str, str]:
    text = path.read_text(encoding='utf-8', errors='ignore')
    lines = text.splitlines()
    result: Dict[str, str] = {}

    if len(lines) < 3 or lines[0].strip() != '---':
        return result

    idx = 1
    while idx < len(lines) and lines[idx].strip() != '---':
        line = lines[idx]
        if ':' in line:
            key, value = line.split(':', 1)
            result[key.strip()] = value.strip().strip("\"'")
        idx += 1

    return result


def check_file(path: Path, repo_root: Path) -> List[str]:
    issues: List[str] = []
    fm = parse_frontmatter(path)
    if not fm:
        issues.append('missing or invalid YAML frontmatter')
        return issues

    if not fm.get('name'):
        issues.append('frontmatter missing name')
    if not fm.get('description'):
        issues.append('frontmatter missing description')

    desc = fm.get('description', '')
    if desc and len(desc) < 20:
        issues.append('description too short (<20 chars)')

    if desc and not re.search(r'[a-zA-Z]', desc):
        issues.append('description appears invalid')

    skill_dir = path.relative_to(repo_root).as_posix().removesuffix('/SKILL.md')
    if skill_dir in PILOT_SKILL_PROFILE_PATHS:
        profile_path_str = fm.get("knowledge_graph_profile", "").strip()
        if profile_path_str:
            profile_path = (path.parent / profile_path_str).resolve()
        else:
            profile_path = path.parent / "references/task-profile.json"
        if not profile_path.exists():
            issues.append("pilot skill missing references/task-profile.json")
        else:
            profile_payload = parse_json(profile_path)
            if profile_payload is None:
                issues.append(f"pilot task-profile parse failed: {profile_path}")
            else:
                validate_learning_posture_profile(profile_payload, issues)

    return issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Verify skill catalog freshness')
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--strict', action='store_true', help='Return non-zero when issues are found')
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root
    skill_files = discover_skill_files(repo_root)

    issues_found: List[Tuple[Path, List[str]]] = []
    names_seen: Dict[str, List[Path]] = {}

    for skill_file in skill_files:
        issues = check_file(skill_file, repo_root)
        if issues:
            issues_found.append((skill_file, issues))

        fm = parse_frontmatter(skill_file)
        name = fm.get('name')
        if name:
            names_seen.setdefault(name, []).append(skill_file)

    duplicate_names = {name: paths for name, paths in names_seen.items() if len(paths) > 1}

    if issues_found:
        print('Metadata quality issues:')
        for path, issues in issues_found:
            print(f'- {path.relative_to(repo_root)}')
            for issue in issues:
                print(f'  - {issue}')

    if duplicate_names:
        print('Duplicate skill names:')
        for name, paths in sorted(duplicate_names.items()):
            rendered = ', '.join(str(p.relative_to(repo_root)) for p in paths)
            print(f'- {name}: {rendered}')

    print(
        'Catalog check complete. '
        f'skills={len(skill_files)} quality_issues={len(issues_found)} duplicates={len(duplicate_names)}'
    )

    if args.strict and (issues_found or duplicate_names):
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
