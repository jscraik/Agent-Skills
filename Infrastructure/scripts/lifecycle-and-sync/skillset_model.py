#!/usr/bin/env python3
"""Shared helpers for context-budgeted rooted skill-set projection."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from selection_policy import ROOT_SKILL_SET_NAMES, policy_identity
from skill_discovery import (
    REPO_ROOT,
    classify_skill_scope,
    iter_plugin_skill_dirs,
    iter_repo_skill_dirs,
    normalize_skill_description,
    parse_skill_frontmatter,
)

GENERATOR_NAME = "context-budgeted-skillsets.v1"
ROOT_SKILL_SETS = tuple(ROOT_SKILL_SET_NAMES)
LEVEL_CHOICES = {"atom", "molecule", "compound", "router", "reference"}

ROOT_SKILL_SET_METADATA: dict[str, dict[str, str]] = {
    "agent-ops": {
        "description": "Route agent operations, repo hygiene, validation, automation, and workflow support without loading individual operational skills by default.",
        "scope": "agent operations, repo workflow, validation, automation, and operator support",
        "exclusions": "frontend design, backend product implementation, mobile work, security reviews, and content publishing unless the task is operational",
    },
    "frontend-ui": {
        "description": "Route frontend interface, design-system, browser, and user-experience work while keeping component-level skills latent until selected.",
        "scope": "frontend UI, UX, design-system, browser-testing, and visual implementation work",
        "exclusions": "backend infrastructure, security operations, content strategy, mobile-native work, and generic repo hygiene",
    },
    "backend-platform": {
        "description": "Route backend, data, API, platform, and infrastructure implementation work without exposing every backend module up front.",
        "scope": "backend services, APIs, data models, infrastructure, and platform execution",
        "exclusions": "visual UI, marketing content, mobile-native implementation, and agent workflow maintenance",
    },
    "product-strategy": {
        "description": "Route product, planning, research synthesis, prioritization, and strategy work with latent specialist modules selected only as needed.",
        "scope": "product strategy, planning, research synthesis, prioritization, and product decision support",
        "exclusions": "direct code implementation, infrastructure operations, security incident response, and visual production work",
    },
    "security-ops": {
        "description": "Route security review, threat modeling, policy, secrets, and operational security work with bounded specialist loading.",
        "scope": "security review, threat modeling, secrets handling, policy, and operational security tasks",
        "exclusions": "ordinary feature implementation, frontend styling, content publishing, and product ideation without security risk",
    },
    "content-publishing": {
        "description": "Route writing, publishing, editorial, docs, and content operations work while keeping detailed content modules latent.",
        "scope": "writing, publishing, editorial workflows, documentation, and content operations",
        "exclusions": "backend architecture, security operations, mobile implementation, and general agent workflow tasks",
    },
    "mobile-native": {
        "description": "Route mobile-native app, platform, device, and app-store work without loading unrelated implementation skills.",
        "scope": "mobile-native development, device integration, app-store readiness, and platform-specific app work",
        "exclusions": "web frontend work, backend-only changes, product strategy, and generic repo operations",
    },
    "skill-factory": {
        "description": "Route skill creation, auditing, installation, refactoring, and skill lifecycle work while preserving local plugin browseability.",
        "scope": "skill creation, skill audits, skill installation, skill lifecycle governance, and skill refactors",
        "exclusions": "ordinary product implementation, plugin package authoring, and general repo maintenance unless skill-specific",
    },
    "plugin-factory": {
        "description": "Route plugin creation, plugin installation, scaffolding, packaging, and plugin lifecycle work through bounded modules.",
        "scope": "plugin authoring, plugin scaffolding, plugin packaging, plugin installation, and plugin lifecycle operations",
        "exclusions": "skill-only authoring, unrelated product code, security reviews, and general content publishing",
    },
    "harness-engineering": {
        "description": "Route Harness Engineering brainstorm, spec, plan, work, review, and fix stages without exposing every HE lane.",
        "scope": "Harness Engineering lifecycle stages, execution plans, reviews, implementation lanes, and fix loops",
        "exclusions": "non-HE plugin work, unrelated skill authoring, direct feature work without an HE artifact, and generic docs edits",
    },
}


def validate_root_skill_set_coverage() -> None:
    """Fail fast when policy skill-set names and metadata drift apart."""
    missing = sorted(set(ROOT_SKILL_SETS) - set(ROOT_SKILL_SET_METADATA))
    extra = sorted(set(ROOT_SKILL_SET_METADATA) - set(ROOT_SKILL_SETS))
    if missing or extra:
        raise RuntimeError(
            "ROOT_SKILL_SET_METADATA keys must match ROOT_SKILL_SETS; "
            f"missing={missing}, extra={extra}"
        )


validate_root_skill_set_coverage()


@dataclass(frozen=True)
class SkillModule:
    """Latent module metadata used by manifests and routers."""

    id: str
    skill_set: str
    level: str
    source_path: str
    triggers: list[str]
    exclusions: list[str]
    risk: str
    runtime_visibility: str
    metadata_status: str
    scope: str
    description: str
    provenance: dict[str, str]

    def to_manifest_row(self) -> dict[str, Any]:
        return asdict(self)


def repo_root() -> Path:
    return REPO_ROOT


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def source_revision() -> str:
    git_bin = shutil.which("git")
    if not git_bin:
        return "unknown"
    try:
        return subprocess.check_output(
            [git_bin, "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def listish(value: str | None) -> list[str]:
    if not value:
        return []
    cleaned = value.replace("\n", " ").strip()
    if not cleaned:
        return []
    if re.search(r"(?:^|\s)-\s+", cleaned):
        return [part.strip() for part in re.split(r"(?:^|\s)-\s+", cleaned) if part.strip()]
    if "," in cleaned:
        return [part.strip() for part in cleaned.split(",") if part.strip()]
    return [cleaned]


def infer_skill_set(source_dir: Path, frontmatter: dict[str, str]) -> tuple[str | None, str]:
    declared = (
        frontmatter.get("metadata.skill-set")
        or frontmatter.get("metadata.skill_set")
        or frontmatter.get("skill-set")
        or frontmatter.get("skill_set")
    )
    if declared:
        normalized = declared.strip().lower().replace("_", "-")
        return (normalized if normalized in ROOT_SKILL_SETS else None), "declared"

    try:
        parts = tuple(source_dir.relative_to(REPO_ROOT).parts)
    except ValueError:
        try:
            parts = tuple(source_dir.resolve().relative_to(REPO_ROOT).parts)
        except ValueError:
            return None, "untagged"
    lowered = tuple(part.lower() for part in parts)
    if len(lowered) >= 2 and lowered[0] == "skills":
        if lowered[1] == "project":
            return None, "untagged"
        if lowered[1] in ROOT_SKILL_SETS:
            return lowered[1], "inferred"
    if len(lowered) >= 3 and lowered[0] == "plugins" and "skills" in lowered:
        skills_index = lowered.index("skills")
        if skills_index >= 2:
            plugin_name = lowered[skills_index - 1]
            if plugin_name in ROOT_SKILL_SETS:
                return plugin_name, "inferred"
    return None, "untagged"


def infer_level(skill_id: str, frontmatter: dict[str, str], description: str) -> tuple[str, str]:
    declared = frontmatter.get("metadata.level") or frontmatter.get("level")
    if declared:
        normalized = declared.strip().lower().replace("_", "-")
        if normalized in LEVEL_CHOICES:
            return normalized, "declared"

    text = f"{skill_id} {description}".lower()
    if "router" in text:
        return "router", "inferred"
    if any(token in text for token in ("playbook", "orchestrator", "workflow", "lifecycle")):
        return "compound", "inferred"
    if any(token in text for token in ("factory", "builder", "review", "audit", "plan")):
        return "molecule", "inferred"
    if any(token in text for token in ("reference", "docs", "documentation")):
        return "reference", "inferred"
    return "atom", "inferred"


def triggers_for(skill_id: str, frontmatter: dict[str, str], description: str) -> list[str]:
    declared = listish(frontmatter.get("metadata.triggers") or frontmatter.get("triggers"))
    if declared:
        return declared[:8]
    trigger = skill_id.replace("-", " ")
    words = description.split()
    if len(words) >= 4:
        return [trigger, " ".join(words[:8]).strip()]
    return [trigger]


def exclusions_for(frontmatter: dict[str, str]) -> list[str]:
    return listish(frontmatter.get("metadata.exclusions") or frontmatter.get("exclusions"))[:8]


def risk_for(frontmatter: dict[str, str]) -> str:
    risk = (frontmatter.get("metadata.risk") or frontmatter.get("risk") or "low").strip().lower()
    return risk if risk in {"low", "medium", "high"} else "low"


def runtime_visibility_for(frontmatter: dict[str, str]) -> str:
    visibility = (
        frontmatter.get("metadata.runtime-visibility")
        or frontmatter.get("metadata.runtime_visibility")
        or frontmatter.get("runtime-visibility")
        or "latent"
    ).strip().lower().replace("_", "-")
    return visibility if visibility in {"latent", "root", "flat", "hidden"} else "latent"


def iter_candidate_skill_dirs() -> list[Path]:
    seen: set[tuple[int, int] | str] = set()
    dirs: list[Path] = []
    for skill_dir in [*iter_repo_skill_dirs(), *iter_plugin_skill_dirs()]:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        scope = classify_skill_scope(skill_dir)
        if scope in {"system", "primary-runtime", "external", "unknown"}:
            continue
        try:
            stat = skill_dir.stat()
            key: tuple[int, int] | str = (stat.st_dev, stat.st_ino)
        except OSError:
            key = skill_dir.resolve().as_posix()
        if key in seen:
            continue
        seen.add(key)
        dirs.append(skill_dir)
    return sorted(dirs, key=rel)


def build_skill_modules() -> tuple[list[SkillModule], list[dict[str, str]]]:
    modules: list[SkillModule] = []
    unmapped: list[dict[str, str]] = []
    revision = source_revision()
    current_policy_identity = policy_identity()
    for source_dir in iter_candidate_skill_dirs():
        skill_md = source_dir / "SKILL.md"
        frontmatter = parse_skill_frontmatter(skill_md)
        description = normalize_skill_description(
            frontmatter.get("metadata.short-description") or frontmatter.get("description", "")
        )
        skill_set, skill_set_status = infer_skill_set(source_dir, frontmatter)
        if not skill_set:
            unmapped.append({"id": source_dir.name, "source_path": rel(skill_md), "reason": skill_set_status})
            continue
        level, _level_status = infer_level(source_dir.name, frontmatter, description)
        metadata_status = "frontmatter" if frontmatter else "inferred"
        modules.append(
            SkillModule(
                id=source_dir.name,
                skill_set=skill_set,
                level=level,
                source_path=rel(skill_md),
                triggers=triggers_for(source_dir.name, frontmatter, description),
                exclusions=exclusions_for(frontmatter),
                risk=risk_for(frontmatter),
                runtime_visibility=runtime_visibility_for(frontmatter),
                metadata_status=metadata_status,
                scope=classify_skill_scope(source_dir),
                description=description,
                provenance={
                    "generator": GENERATOR_NAME,
                    "projection_mode": "rooted",
                    "policy_identity": current_policy_identity,
                    "source_revision": revision,
                    "source_sha256": file_hash(skill_md),
                },
            )
        )
    return sorted(modules, key=lambda module: (module.skill_set, module.id, module.source_path)), unmapped


def modules_by_skill_set(modules: Iterable[SkillModule]) -> dict[str, list[SkillModule]]:
    grouped: dict[str, list[SkillModule]] = {name: [] for name in ROOT_SKILL_SETS}
    for module in modules:
        grouped.setdefault(module.skill_set, []).append(module)
    return {name: sorted(rows, key=lambda row: (row.id, row.source_path)) for name, rows in grouped.items()}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
