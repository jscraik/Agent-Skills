#!/usr/bin/env python3
"""Skill catalog discovery and metadata quality checks for router usage."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

SKIP_DIRS = {
    ".git",
    "artifacts",
    "node_modules",
    "docs",
    "templates",
    "references",
    "skills",
    "skills-codex",
    "skills-system",
    ".worktrees",
}


@dataclass
class SkillMeta:
    name: str
    description: str
    skill_path: str


@dataclass
class CatalogLoadResult:
    skills: List[SkillMeta]
    catalog_version: str
    quality_issues: List[str]
    duplicate_names: Dict[str, List[str]]


def parse_frontmatter(skill_file: Path) -> Tuple[str, str]:
    content = skill_file.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    name = skill_file.parent.name
    description = ""

    if len(lines) > 2 and lines[0].strip() == "---":
        idx = 1
        while idx < len(lines) and lines[idx].strip() != "---":
            line = lines[idx]
            if line.startswith("name:"):
                value = line.split(":", 1)[1].strip()
                if value:
                    name = value.strip("\"'")
            if line.startswith("description:"):
                value = line.split(":", 1)[1].strip()
                description = value.strip("\"'")
            idx += 1

    if not description:
        body = "\n".join(lines[10:40])
        match = re.search(r"\n\s*[-*]?\s*(.+)", body)
        if match:
            description = match.group(1).strip()

    return name, description


def discover_skills(repo_root: Path) -> List[SkillMeta]:
    skills: List[SkillMeta] = []
    for skill_file in sorted(repo_root.rglob("SKILL.md")):
        rel = skill_file.relative_to(repo_root)
        if rel.as_posix() == "SKILL.md":
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue

        name, description = parse_frontmatter(skill_file)
        skills.append(
            SkillMeta(
                name=name,
                description=description,
                skill_path=str(skill_file.parent.relative_to(repo_root)),
            )
        )
    return skills


def _quality_issues(skills: List[SkillMeta]) -> Tuple[List[str], Dict[str, List[str]]]:
    issues: List[str] = []
    names_seen: Dict[str, List[str]] = {}

    for skill in skills:
        if not skill.name.strip():
            issues.append(f"{skill.skill_path}: missing name")
        if len(skill.description.strip()) < 20:
            issues.append(f"{skill.skill_path}: description too short (<20 chars)")
        names_seen.setdefault(skill.name, []).append(skill.skill_path)

    duplicates = {name: paths for name, paths in names_seen.items() if len(paths) > 1}
    if duplicates:
        for name, paths in sorted(duplicates.items()):
            rendered = ", ".join(paths)
            issues.append(f"duplicate skill name '{name}' in {rendered}")

    return issues, duplicates


def _catalog_version(skills: List[SkillMeta]) -> str:
    canonical = [
        {
            "name": s.name,
            "description": s.description,
            "skill_path": s.skill_path,
        }
        for s in sorted(skills, key=lambda x: (x.name.lower(), x.skill_path.lower()))
    ]
    blob = json.dumps(canonical, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def load_catalog(repo_root: Path, *, strict: bool = True) -> CatalogLoadResult:
    skills = discover_skills(repo_root)
    issues, duplicates = _quality_issues(skills)
    version = _catalog_version(skills)

    if strict and issues:
        raise ValueError("; ".join(issues))

    return CatalogLoadResult(
        skills=skills,
        catalog_version=version,
        quality_issues=issues,
        duplicate_names=duplicates,
    )
