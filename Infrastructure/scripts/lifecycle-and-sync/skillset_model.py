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
    SYSTEM_BRIDGE_SKILL_NAMES,
    iter_system_lane_skill_dirs,
    iter_plugin_skill_dirs,
    iter_repo_skill_dirs,
    normalize_skill_description,
    parse_skill_frontmatter,
)

GENERATOR_NAME = "context-budgeted-skillsets.v1"
ROOT_SKILL_SETS = tuple(ROOT_SKILL_SET_NAMES)
LEVEL_CHOICES = {"atom", "molecule", "compound", "router", "reference"}

ROOT_SKILL_SET_METADATA: dict[str, dict[str, Any]] = {
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
        "description": "Review, route, and audit security work. Use when tasks involve threat modeling, secrets, policy, or operational security risk.",
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
        "description": "Use when creating, auditing, installing, refactoring, or governing Codex skills while preserving local plugin browseability.",
        "scope": "skill creation, skill audits, skill installation, skill lifecycle governance, and skill refactors",
        "exclusions": "ordinary product implementation, plugin package authoring, and general repo maintenance unless skill-specific",
    },
    "plugin-factory": {
        "description": "Route plugin creation, plugin installation, scaffolding, packaging, and plugin lifecycle work through bounded modules.",
        "scope": "plugin authoring, plugin scaffolding, plugin packaging, plugin installation, and plugin lifecycle operations",
        "exclusions": "skill-only authoring, unrelated product code, security reviews, and general content publishing",
    },
    "harness-engineering": {
        "description": "Route Harness Engineering lifecycle and session-evidence requests when users need brainstorming, planning, implementation, review, fixes, heartbeats, or prior-run improvement.",
        "scope": "Harness Engineering lifecycle stages, reviews, fixes, heartbeats, and session-evidence improvements",
        "exclusions": "non-HE plugin work, unrelated skill authoring, direct feature work without an HE artifact, and generic docs edits",
        "examples": [
            "Can you route this Linear QA issue to the right HE stage?",
            "Please inspect this PR feedback and route it to the right HE review or fix lane.",
            "Can you scan archived Codex sessions and session collector data for repeated HE failures?",
        ],
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
        return [part.strip().strip("\"'") for part in re.split(r"(?:^|\s)-\s+", cleaned) if part.strip()]
    if "," in cleaned:
        return [part.strip().strip("\"'") for part in cleaned.split(",") if part.strip()]
    return [cleaned.strip().strip("\"'")]


def infer_skill_set(source_dir: Path, frontmatter: dict[str, str]) -> tuple[str | None, str]:
    """
    Infer the root skill-set for a skill directory using frontmatter declarations and repository path heuristics.

    Checks frontmatter for declared skill-set keys (multiple spellings accepted) and returns the normalized value when it matches a known root skill-set. When no declaration is present, infers the skill-set from the repository-relative path using canonical patterns (e.g., skills/<root_skill_set>/..., plugins/<plugin>/skills/..., skills-system/<name>) and special handling for system-bridge skills. If the path cannot be relativized to the repository or no rule matches, the result is treated as untagged.

    Parameters:
        source_dir (Path): Directory containing the skill (expected to contain SKILL.md).
        frontmatter (dict[str, str]): Parsed SKILL.md frontmatter keys and values.

    Returns:
        tuple[str | None, str]: (skill_set, status)
            - skill_set: a root skill-set name when determined, otherwise `None`.
            - status: one of "declared", "inferred", "system-bridge", or "untagged" indicating how the value was obtained.
    """
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
    scope = classify_skill_scope(source_dir)
    if scope == "system" and source_dir.name in SYSTEM_BRIDGE_SKILL_NAMES:
        return "agent-ops", "system-bridge"
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
    if lowered and lowered[0] == "skills-system" and source_dir.name in SYSTEM_BRIDGE_SKILL_NAMES:
        return "agent-ops", "system-bridge"
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
    first_sentence = re.split(r"(?<=[.!?])\s+", description.strip(), maxsplit=1)[0].strip()
    if first_sentence and first_sentence != description.strip():
        return [trigger, first_sentence]
    words = description.split()
    if 4 <= len(words) <= 12:
        return [trigger, description.strip()]
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
    """
    Collect candidate skill directories for projection.

    Scans repository, plugin, and system-lane skill locations and selects directories that contain a SKILL.md. Excludes directories whose classified scope is "primary-runtime", "external", or "unknown". For scope "system" only includes directories whose name appears in SYSTEM_BRIDGE_SKILL_NAMES. Results are deduplicated and returned sorted by the repository-relative path produced by rel().

    Returns:
        list[Path]: Unique candidate skill directory paths sorted by repository-relative path.
    """
    system_dirs = iter_system_lane_skill_dirs()
    canonical_system_dir = REPO_ROOT / "skills-system"
    if canonical_system_dir.is_dir():
        system_dirs = sorted(
            item
            for item in canonical_system_dir.iterdir()
            if item.is_dir() and (item / "SKILL.md").exists()
        )
    candidate_dirs = [*iter_repo_skill_dirs(), *iter_plugin_skill_dirs(), *system_dirs]
    canonical_names = {
        skill_dir.name
        for skill_dir in candidate_dirs
        if classify_skill_scope(skill_dir) != "system"
    }
    seen: set[tuple[int, int] | str] = set()
    dirs: list[Path] = []
    for skill_dir in candidate_dirs:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        scope = classify_skill_scope(skill_dir)
        if scope == "system":
            if skill_dir.name not in SYSTEM_BRIDGE_SKILL_NAMES:
                continue
            if skill_dir.name in canonical_names:
                continue
        elif scope in {"primary-runtime", "external", "unknown"}:
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

def canonical_source_path_for_row(source_dir: Path, scope: str, skill_set: str | None) -> str:
    """
    Produce a repo-relative canonical path to the SKILL.md used for manifest provenance.

    Returns a canonical virtual path mapping used solely for manifest provenance—not the actual
    filesystem location. When the skill is a system-scoped bridge entry (scope == "system",
    skill_set == "agent-ops", the directory name is in SYSTEM_BRIDGE_SKILL_NAMES, and its parent
    directory is ".system"), returns "skills-system/{skill_name}/SKILL.md". Otherwise returns the
    repo-relative path to source_dir / "SKILL.md".

    Note: The "skills-system/..." form is a canonical virtual path for manifest provenance. The actual
    source file may reside elsewhere in the filesystem. Downstream tooling reading manifests should
    use the source_path as a provenance identifier; to locate the real filesystem path, resolve via
    the skill discovery logic or the actual source_dir.

    Parameters:
        source_dir (Path): Directory containing the skill's SKILL.md.
        scope (str): Classified scope of the skill (e.g., "system").
        skill_set (str | None): Inferred or declared root skill set name.

    Returns:
        str: Repo-relative posix path to the canonical SKILL.md location (a virtual path for manifest
             provenance, may not correspond to the real filesystem location for system bridge skills).

    Helper references:
        - SYSTEM_BRIDGE_SKILL_NAMES: constant listing recognized system bridge skill names.
        - rel(): helper function to convert Path to repo-relative posix string.
    """
    if (
        scope == "system"
        and skill_set == "agent-ops"
        and source_dir.name in SYSTEM_BRIDGE_SKILL_NAMES
        and source_dir.parent.name == ".system"
    ):
        return f"skills-system/{source_dir.name}/SKILL.md"
    return rel(source_dir / "SKILL.md")


def build_skill_modules() -> tuple[list[SkillModule], list[dict[str, str]]]:
    """
    Builds SkillModule records for all discovered candidate skill directories and collects any unmapped candidates.

    Each discovered skill directory with a SKILL.md is parsed and normalized into a SkillModule (including inferred or declared skill_set, level, scope, triggers, exclusions, risk, runtime_visibility, description, metadata status, canonical source_path, and provenance). The returned modules are sorted by (skill_set, id, source_path).

    Returns:
        tuple[
            list[SkillModule],             # List of built SkillModule objects, sorted by (skill_set, id, source_path).
            list[dict[str, str]]           # List of unmapped candidate records; each dict contains:
                                           #   - "id": directory name,
                                           #   - "source_path": repository-relative path to SKILL.md,
                                           #   - "reason": short status explaining why it could not be assigned.
        ]
    """
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
        scope = classify_skill_scope(source_dir)
        source_path = canonical_source_path_for_row(
            source_dir=source_dir,
            scope=scope,
            skill_set=skill_set,
        )
        metadata_status = "frontmatter" if frontmatter else "inferred"
        modules.append(
            SkillModule(
                id=source_dir.name,
                skill_set=skill_set,
                level=level,
                source_path=source_path,
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
