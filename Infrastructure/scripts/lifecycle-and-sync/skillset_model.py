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
        """
        Return a plain dictionary representation of the SkillModule suitable for writing to manifests.
        
        Returns:
            dict[str, Any]: Dictionary mapping each dataclass field name to its value.
        """
        return asdict(self)


def repo_root() -> Path:
    """
    Return the repository root path used for skill discovery.
    
    Returns:
        Path: The repository root directory (`REPO_ROOT`).
    """
    return REPO_ROOT


def rel(path: Path) -> str:
    """
    Compute the POSIX path string for `path` relative to the repository root when possible.
    
    Returns:
        A POSIX-formatted string: the path relative to `REPO_ROOT` if `path` is inside the repository, otherwise the absolute POSIX path.
    """
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def source_revision() -> str:
    """
    Get the current repository Git short revision hash.
    
    Returns:
        str: The short SHA-1 hash of HEAD (e.g., "abc1234"), or the literal string "unknown" if the `git` executable is not found or the revision cannot be determined.
    """
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
    """
    Compute the SHA-256 hexadecimal digest of the file at the given path.
    
    Returns:
        str: Hexadecimal SHA-256 digest of the file's contents.
    """
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def listish(value: str | None) -> list[str]:
    """
    Parse a free-form string into a list of trimmed items supporting bullet, comma, or single-value formats.
    
    Parameters:
        value (str | None): Input text which may be None, a newline- or dash-prefixed bullet list, a comma-separated list, or a single item.
    
    Returns:
        list[str]: Parsed list of items. Returns an empty list for None or empty/whitespace input. For inputs containing dash-style bullets (e.g., "- item"), splits on bullets; otherwise if commas are present splits on commas; otherwise returns a single-item list containing the trimmed input.
    """
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
    """
    Infer the root skill-set for a skill directory from declared frontmatter or by deriving it from the repository path.
    
    Checks frontmatter keys ("metadata.skill-set", "metadata.skill_set", "skill-set", "skill_set") first; if present the value is normalized (trimmed, lowercased, "_" → "-") and returned as the declared skill-set when it matches one of ROOT_SKILL_SETS. If no declaration is present, attempts to infer the skill-set from source_dir relative to REPO_ROOT:
    - skills/<name>/... → returns <name> when <name> is a known root skill-set; treats skills/project as untagged.
    - plugins/<name>/... → returns <name> when <name> is a known root skill-set.
    If neither declaration nor inference yields a known root skill-set, returns None with status "untagged".
    
    Parameters:
        source_dir (Path): Path to the skill directory to inspect; used for path-based inference relative to REPO_ROOT.
        frontmatter (dict[str, str]): Parsed SKILL.md frontmatter potentially containing declared skill-set keys.
    
    Returns:
        tuple[str | None, str]: A tuple of (skill_set, status) where `skill_set` is the normalized root skill-set name or `None`, and `status` is one of `"declared"`, `"inferred"`, or `"untagged"`.
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
    if len(lowered) >= 2 and lowered[0] == "skills":
        if lowered[1] == "project":
            return None, "untagged"
        if lowered[1] in ROOT_SKILL_SETS:
            return lowered[1], "inferred"
    if len(lowered) >= 2 and lowered[0] == "plugins":
        plugin_name = lowered[1]
        if plugin_name in ROOT_SKILL_SETS:
            return plugin_name, "inferred"
    return None, "untagged"


def infer_level(skill_id: str, frontmatter: dict[str, str], description: str) -> tuple[str, str]:
    """
    Infer a skill's normalized level from frontmatter or textual hints.
    
    If `frontmatter` contains `metadata.level` or `level` whose normalized value is one of the allowed LEVEL_CHOICES, that declared value is returned with status `"declared"`. Otherwise the function inspects `skill_id` and `description` for keywords to choose a level and returns that level with status `"inferred"`. Keywords map to levels as follows: presence of "router" → `"router"`; any of "playbook", "orchestrator", "workflow", "lifecycle" → `"compound"`; any of "factory", "builder", "review", "audit", "plan" → `"molecule"`; any of "reference", "docs", "documentation" → `"reference"`; otherwise `"atom"`.
    
    Parameters:
        skill_id (str): Identifier of the skill (used as part of the text inspected when inferring).
        frontmatter (dict[str, str]): Parsed frontmatter; the function checks `metadata.level` then `level` for a declared value.
        description (str): Skill description text used with `skill_id` when inferring from keywords.
    
    Returns:
        tuple[str, str]: A pair `(level, status)` where `level` is one of the normalized LEVEL_CHOICES and `status` is either `"declared"` if taken from frontmatter or `"inferred"` if derived from keywords.
    """
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
    """
    Produce a short list of search triggers for a skill.
    
    Parameters:
        skill_id (str): Skill identifier (e.g., "my-skill") used as a fallback trigger with hyphens replaced by spaces.
        frontmatter (dict[str, str]): Parsed frontmatter; if it contains `metadata.triggers` or `triggers`, those declared values are used.
        description (str): Skill description used to derive an additional phrase when no declared triggers exist.
    
    Returns:
        A list of trigger strings. If the frontmatter provides triggers, returns those (up to 8). Otherwise returns a list starting with the skill-id-derived trigger and, when the description is sufficiently long, an additional phrase composed of the first up to 8 words from the description.
    """
    declared = listish(frontmatter.get("metadata.triggers") or frontmatter.get("triggers"))
    if declared:
        return declared[:8]
    trigger = skill_id.replace("-", " ")
    words = description.split()
    if len(words) >= 4:
        return [trigger, " ".join(words[:8]).strip()]
    return [trigger]


def exclusions_for(frontmatter: dict[str, str]) -> list[str]:
    """
    Extract up to eight exclusion identifiers from parsed frontmatter.
    
    Parameters:
        frontmatter (dict[str, str]): Mapping of frontmatter keys; this function reads
            `metadata.exclusions` or `exclusions` if present.
    
    Returns:
        list[str]: A list (maximum length 8) of parsed exclusion strings. The input
            value is interpreted as a list-like string (supports bullet-style,
            comma-separated, or single-value formats) and normalized into elements.
    """
    return listish(frontmatter.get("metadata.exclusions") or frontmatter.get("exclusions"))[:8]


def risk_for(frontmatter: dict[str, str]) -> str:
    """
    Normalize and validate a risk level extracted from frontmatter.
    
    Parameters:
        frontmatter (dict[str, str]): Parsed frontmatter mapping (e.g., keys like "metadata.risk" or "risk").
    
    Returns:
        str: One of "low", "medium", or "high"; defaults to "low" for missing or unrecognized values.
    """
    risk = (frontmatter.get("metadata.risk") or frontmatter.get("risk") or "low").strip().lower()
    return risk if risk in {"low", "medium", "high"} else "low"


def runtime_visibility_for(frontmatter: dict[str, str]) -> str:
    """
    Determine the runtime visibility value for a skill from its frontmatter.
    
    Checks the frontmatter for `metadata.runtime-visibility`, `metadata.runtime_visibility`, or `runtime-visibility`, normalizes the value (lowercase, underscores to hyphens), and returns one of: `latent`, `root`, `flat`, or `hidden`. If none is present or the value is not one of the allowed choices, returns `latent`.
    
    Parameters:
        frontmatter (dict[str, str]): Parsed frontmatter key/value pairs from a SKILL.md file.
    
    Returns:
        str: One of `latent`, `root`, `flat`, or `hidden`.
    """
    visibility = (
        frontmatter.get("metadata.runtime-visibility")
        or frontmatter.get("metadata.runtime_visibility")
        or frontmatter.get("runtime-visibility")
        or "latent"
    ).strip().lower().replace("_", "-")
    return visibility if visibility in {"latent", "root", "flat", "hidden"} else "latent"


def iter_candidate_skill_dirs() -> list[Path]:
    """
    Yield a sorted list of candidate skill directories that contain a SKILL.md file and are eligible for projection.
    
    Scans repository and plugin skill directories, filters out entries missing a SKILL.md or whose scope is one of "system", "primary-runtime", "external", or "unknown", de-duplicates directories (preferring filesystem inode/device when available, falling back to resolved path), and returns the remaining directories sorted by their repository-relative path.
    
    Returns:
        list[Path]: Sorted list of unique candidate skill directory paths.
    """
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
    """
    Builds SkillModule objects for all discoverable skill directories and collects skills that cannot be mapped to a root skill set.
    
    Each constructed SkillModule captures identity, selection fields, inferred or declared metadata, scope, description, and provenance (including generator, projection_mode "rooted", policy identity, git short revision, and SHA-256 of the SKILL.md). Skills that lack a determinable root skill-set are returned in the unmapped list as dicts with keys 'id', 'source_path', and 'reason'.
    
    Returns:
        tuple[list[SkillModule], list[dict[str, str]]]: 
            - A list of SkillModule instances sorted by (skill_set, id, source_path).
            - A list of unmapped skill descriptors where each dict contains 'id', 'source_path', and 'reason'.
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
        level, level_status = infer_level(source_dir.name, frontmatter, description)
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
    """
    Group SkillModule objects by root skill-set name.
    
    Parameters:
        modules (Iterable[SkillModule]): Iterable of SkillModule instances to group.
    
    Returns:
        dict[str, list[SkillModule]]: A mapping from skill-set name to a list of modules belonging to that skill-set.
        The returned dictionary always includes keys for every name in `ROOT_SKILL_SETS` (each mapped to an empty list if no modules match).
        Each list is sorted by `(module.id, module.source_path)`. Modules whose `skill_set` is not in `ROOT_SKILL_SETS` are included under their declared `skill_set` key.
    """
    grouped: dict[str, list[SkillModule]] = {name: [] for name in ROOT_SKILL_SETS}
    for module in modules:
        grouped.setdefault(module.skill_set, []).append(module)
    return {name: sorted(rows, key=lambda row: (row.id, row.source_path)) for name, rows in grouped.items()}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """
    Write a mapping as pretty-printed JSON to the given file path, creating parent directories if needed.
    
    Parameters:
        path (Path): Destination file path to write the JSON payload to.
        payload (dict[str, Any]): JSON-serializable mapping to serialize and write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
