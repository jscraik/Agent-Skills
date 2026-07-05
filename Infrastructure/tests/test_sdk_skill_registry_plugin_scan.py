#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from sdk_skill_registry import resolve_sdk_skill_handle  # noqa: E402


def test_resolves_canonical_plugin_skill_source_path() -> None:
    result = resolve_sdk_skill_handle(
        "Plugins/skill-factory/skills/code_quality_review/skill-builder",
        repo_root_path=REPO_ROOT,
    )

    assert result["status"] == "ok"
    assert result["handle"] == "skill-builder"
    assert (
        result["source_path"]
        == "Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md"
    )
