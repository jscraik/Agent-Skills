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
SURFACE_PATHS = (
    "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md",
    "skills-system/skill-creator/SKILL.md",
    "skills-system/skill-installer/SKILL.md",
    "Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md",
    "Plugins/skill-factory/skills/scaffolding_templates/skillify/references/skill-template.md",
    "Plugins/skill-factory/skills/skill-refactor/SKILL.md",
)
SDK_LADDER_FRAGMENTS = (
    "./bin/ask sdk start",
    "package verify",
    "reference_heading_invocable",
    "scenario-quality",
    "scorer-quality",
    "scorer-calibration",
    "oss-local",
    "oss-cloud",
    "tessl-local-proof",
    "handoff-readiness",
)
SDK_LADDER_VARIANTS = {
    "tessl-local-proof": ("tessl-local-proof", "Tessl local proof"),
}
CONSTRUCTION_CONTRACT = "Docs/reference/skills-sdk-skill-construction-contract.md"
GOLD_RUBRIC = "Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json"


def fail(message: str) -> int:
    print(f"[skill-factory-system-overlays] ERROR: {message}", file=sys.stderr)
    return 1


def _surface_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _missing_ladder_fragments(relative_path: str) -> list[str]:
    text = _surface_text(relative_path).lower()
    missing: list[str] = []
    for fragment in SDK_LADDER_FRAGMENTS:
        accepted = SDK_LADDER_VARIANTS.get(fragment, (fragment,))
        if not any(candidate.lower() in text for candidate in accepted):
            missing.append(fragment)
    return missing


def _assert_order(errors: list[str], relative_path: str, fragments: tuple[str, ...]) -> None:
    text = _surface_text(relative_path).lower()
    cursor = 0
    for fragment in fragments:
        position = text.find(fragment.lower(), cursor)
        if position == -1:
            errors.append(f"{relative_path} has gate-order drift: {' -> '.join(fragments)}")
            return
        cursor = position + len(fragment)


def _validate_semantic_surfaces(errors: list[str]) -> None:
    for relative_path in SURFACE_PATHS:
        path = REPO_ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing Skill Factory surface: {relative_path}")
            continue
        missing = _missing_ladder_fragments(relative_path)
        if missing:
            errors.append(f"{relative_path} missing SDK ladder fragments: {', '.join(missing)}")

    for relative_path in (
        "Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md",
        "Plugins/skill-factory/skills/scaffolding_templates/skillify/references/skill-template.md",
    ):
        _assert_order(
            errors,
            relative_path,
            (
                "skills audit",
                "skills package verify",
                "scenario-quality",
                "sdk security risk-modes",
            ),
        )

    construction = _surface_text(CONSTRUCTION_CONTRACT)
    for fragment in ("Invocation", "Information Hierarchy", "Steering", "Pruning"):
        if fragment not in construction:
            errors.append(f"{CONSTRUCTION_CONTRACT} missing construction axis: {fragment}")
    rubric = _surface_text(GOLD_RUBRIC)
    for fragment in ("construction_structure_steering_pruning", "reference_invocation"):
        if fragment not in rubric:
            errors.append(f"{GOLD_RUBRIC} missing rubric criterion: {fragment}")


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

    _validate_semantic_surfaces(errors)

    if errors:
        for error in errors:
            print(f"[skill-factory-system-overlays] ERROR: {error}", file=sys.stderr)
        return 1

    print("[skill-factory-system-overlays] pass: system skill overlays are additive")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
