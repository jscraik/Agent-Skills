#!/usr/bin/env python3
"""Verify skill catalog freshness and metadata quality constraints."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple

SKIP_DIRS = {
    '.git',
    'artifacts',
    'node_modules',
    'docs',
    'skills',
    'skills-antigravity',
    'templates',
    'references',
    'skills-system',
    '.worktrees',
}


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


def check_file(path: Path) -> List[str]:
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
        issues = check_file(skill_file)
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
