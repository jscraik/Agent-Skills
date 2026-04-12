#!/usr/bin/env python3
"""Shared skill-lane ownership contract for scaffold and validation workflows."""

from __future__ import annotations

import json
from pathlib import Path


CANONICAL_STANDALONE_SKILL_ROOTS: tuple[str, ...] = (
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
    return isinstance(value, str) and value.startswith("./") and len(value) > 2


def resolve_declared_plugin_skill_root(plugin_root: Path) -> Path | None:
    """Return the plugin-owned skills directory declared by plugin.json, when valid."""
    declared_relative = _DEFAULT_PLUGIN_SKILLS_RELATIVE
    manifest_path = plugin_root / _PLUGIN_MANIFEST
    if manifest_path.exists():
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = None
        if isinstance(payload, dict):
            skills_value = payload.get("skills")
            if _is_relative_plugin_path(skills_value):
                declared_relative = skills_value[2:]

    candidate = (plugin_root / declared_relative).resolve()
    if candidate.is_dir():
        return candidate
    return None


def iter_declared_plugin_skill_roots(repo_root: Path) -> list[Path]:
    """Return all plugin-owned skill roots declared by plugin manifests."""
    plugins_root = repo_root / "plugins"
    if not plugins_root.is_dir():
        return []

    roots: list[Path] = []
    seen: set[Path] = set()
    for plugin_root in sorted(plugins_root.iterdir()):
        if not plugin_root.is_dir():
            continue
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
