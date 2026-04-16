#!/usr/bin/env python3
"""Shared skill-lane ownership contract for scaffold and validation workflows."""

from __future__ import annotations

import json
from pathlib import Path


CANONICAL_STANDALONE_SKILL_ROOTS: tuple[str, ...] = (
    "Skills",
    "utilities",
    "product",
    "frontend",
    "backend",
    "auth",
    "design",
    "github",
    "interview",
    "ops",
    "personas",
    "skills-system",
)

_PLUGIN_MANIFEST = ".codex-plugin/plugin.json"
_DEFAULT_PLUGIN_SKILLS_RELATIVE = "skills"


def _is_relative_plugin_path(value: object) -> bool:
    if not isinstance(value, str) or not value.startswith("./") or len(value) <= 2:
        return False
    relative = value[2:]
    if relative.startswith("/") or "//" in relative:
        return False
    segments = relative.rstrip("/").split("/")
    if not segments:
        return False
    return all(segment not in {"", ".", ".."} for segment in segments)


def _normalize_relative_plugin_path(value: str) -> str:
    # Accept plugin manifests that spell the skills surface as "./skills/".
    # The trailing slash is layout noise, not a different root.
    return value[2:].rstrip("/")


def resolve_declared_plugin_skill_root(plugin_root: Path) -> Path | None:
    """Return the plugin-owned skills directory declared by plugin.json, when valid."""
    manifest_path = plugin_root / _PLUGIN_MANIFEST
    if not manifest_path.exists():
        return None
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None

    skills_value = payload.get("skills")
    if skills_value is None:
        declared_relative = _DEFAULT_PLUGIN_SKILLS_RELATIVE
    elif _is_relative_plugin_path(skills_value):
        declared_relative = _normalize_relative_plugin_path(skills_value)
    else:
        return None

    candidate = (plugin_root / declared_relative).resolve()
    try:
        candidate.relative_to(plugin_root.resolve())
    except ValueError:
        return None
    if candidate.is_dir():
        return candidate
    return None


def iter_canonical_standalone_skill_roots(repo_root: Path) -> list[Path]:
    """Return existing canonical standalone roots under repo_root."""
    roots: list[Path] = []
    for root_name in CANONICAL_STANDALONE_SKILL_ROOTS:
        root_path = (repo_root / root_name).resolve()
        if root_path.is_dir():
            roots.append(root_path)
    return roots


def iter_declared_plugin_skill_roots(repo_root: Path) -> list[Path]:
    """Return all plugin-owned skill roots declared by plugin manifests."""
    roots: list[Path] = []
    manifest_patterns = (
        "plugins/*/.codex-plugin/plugin.json",
        "Plugins/*/.codex-plugin/plugin.json",
        "plugins/*/*/.codex-plugin/plugin.json",
        "Plugins/*/*/.codex-plugin/plugin.json",
    )
    seen: set[Path] = set()
    for pattern in manifest_patterns:
        for manifest_path in sorted(repo_root.glob(pattern)):
            plugin_root = manifest_path.parent.parent
            skills_root = resolve_declared_plugin_skill_root(plugin_root)
            if skills_root is None or skills_root in seen:
                continue
            seen.add(skills_root)
            roots.append(skills_root)
    return roots


def find_plugin_skill_root_for_output(out_dir: Path, repo_root: Path) -> Path | None:
    """Return the plugin-owned skill root containing out_dir, if any."""
    resolved_out_dir = out_dir.resolve()
    for skills_root in iter_declared_plugin_skill_roots(repo_root):
        try:
            resolved_out_dir.relative_to(skills_root)
            return skills_root
        except ValueError:
            continue
    return None
