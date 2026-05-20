#!/usr/bin/env python3
"""Validate Skill Factory's system-skill extension contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
PLUGIN_ROOT = REPO_ROOT / "Plugins" / "skill-factory"
SYSTEM_ROOT = REPO_ROOT / "skills-system"
BRIDGES = {
    "skill-creator": PLUGIN_ROOT / "skills" / "scaffolding_templates" / "skill-creator",
    "skill-installer": PLUGIN_ROOT / "skills" / "infrastructure_ops" / "skill-installer",
}


def fail(message: str) -> int:
    print(f"[skill-factory-system-overlays] ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    errors: list[str] = []

    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    keywords = set(manifest.get("keywords", []))

    for name, extension_dir in BRIDGES.items():
        system_dir = SYSTEM_ROOT / name
        system_skill = system_dir / "SKILL.md"
        if system_dir.is_symlink():
            errors.append(f"{system_dir.relative_to(REPO_ROOT)} must be a real preserved .system skill directory, not a plugin alias")
        if not system_skill.is_file():
            errors.append(f"missing system skill body: {system_skill.relative_to(REPO_ROOT)}")
        plugin_skill = extension_dir / "SKILL.md"
        if plugin_skill.exists() or plugin_skill.is_symlink():
            errors.append(f"{plugin_skill.relative_to(REPO_ROOT)} must not exist; attach references to skills-system/{name} instead")
        attached_ref = system_dir / "references" / "skill-factory"
        if not attached_ref.is_dir():
            errors.append(f"missing attached Skill Factory references: {attached_ref.relative_to(REPO_ROOT)}")
        evals = attached_ref / "evals.yaml"
        if not evals.is_file():
            errors.append(f"missing attached evals: {evals.relative_to(REPO_ROOT)}")
        if name in keywords:
            errors.append(f"plugin manifest must not advertise hidden system bridge skill keyword: {name}")

    if errors:
        for error in errors:
            print(f"[skill-factory-system-overlays] ERROR: {error}", file=sys.stderr)
        return 1

    print("[skill-factory-system-overlays] pass: system skill overlays are additive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
