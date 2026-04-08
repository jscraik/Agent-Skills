#!/usr/bin/env python3
"""Regression tests for family benchmark path canonicalization."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate_skill_authoring_family_benchmarks.py"


def load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_skill_authoring_family_benchmarks", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load validator module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FamilyBenchmarkCanonicalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_validator_module()

    def test_canonical_skill_rel_resolves_symlink_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../plugins/skill-factory/skills/skill-builder")

            with unittest.mock.patch.object(self.module, "REPO_ROOT", root):
                canonical = self.module._canonical_skill_rel("utilities/skill-builder")

            self.assertEqual(canonical, "plugins/skill-factory/skills/skill-builder")

    def test_dedupe_requested_skills_uses_canonical_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../plugins/skill-factory/skills/skill-builder")

            with unittest.mock.patch.object(self.module, "REPO_ROOT", root):
                deduped = self.module._dedupe_requested_skills(
                    ("utilities/skill-builder", "plugins/skill-factory/skills/skill-builder")
                )

            self.assertEqual(deduped, ("utilities/skill-builder",))

    def test_validate_skill_accepts_canonical_scope_for_alias_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill_rel = "plugins/skill-factory/skills/skill-builder"
            plugin_skill = root / plugin_skill_rel
            refs = plugin_skill / "references"
            refs.mkdir(parents=True, exist_ok=True)
            (plugin_skill / "SKILL.md").write_text("# skill-builder\n", encoding="utf-8")
            (refs / "task-profile.json").write_text(
                """{
  "schema_version": "1.0",
  "profile_id": "utilities-skill-builder",
  "scope_skill": "plugins/skill-factory/skills/skill-builder",
  "scope_profile": "utilities",
  "rubric_version": "2026-04-08",
  "evaluator_version": "v1",
  "persona_set_id": "default-v1",
  "thresholds": {},
  "criteria": [],
  "delegation": {},
  "learning_posture": {}
}
""",
                encoding="utf-8",
            )

            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../plugins/skill-factory/skills/skill-builder")

            with (
                unittest.mock.patch.object(self.module, "REPO_ROOT", root),
                unittest.mock.patch.object(self.module, "_validate_contract", return_value=[]),
                unittest.mock.patch.object(self.module, "_validate_evals", return_value=[]),
                unittest.mock.patch.object(self.module, "_validate_reference_pi", return_value=[]),
            ):
                findings = self.module._validate_skill("utilities/skill-builder")

            scope_failures = [f for f in findings if f.code == "TASK_PROFILE_SCOPE"]
            self.assertEqual(scope_failures, [])


if __name__ == "__main__":
    unittest.main()
