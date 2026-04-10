#!/usr/bin/env python3
"""Regression tests for family benchmark path canonicalization."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock


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
        """
        Verify that _canonical_skill_rel resolves a symlinked skill alias to the canonical repository-relative skill path.
        
        Creates a temporary repository layout with a real skill at plugins/skill-factory/skills/skill-builder and a symlink alias at utilities/skill-builder, patches REPO_ROOT to the temp root, and asserts the canonicalised result equals plugins/skill-factory/skills/skill-builder.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../plugins/skill-factory/skills/skill-builder")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                canonical = self.module._canonical_skill_rel("utilities/skill-builder")

            self.assertEqual(canonical, "plugins/skill-factory/skills/skill-builder")

    def test_dedupe_requested_skills_uses_canonical_target(self) -> None:
        """
        Verifies deduplication prefers a symlink alias path over its canonical target.
        
        Creates a temporary repository where `utilities/skill-builder` is a symlink to
        `plugins/skill-factory/skills/skill-builder` and asserts that passing both the
        alias and the canonical path to `_dedupe_requested_skills` yields only the
        alias entry, protecting against duplicate validations of the same skill.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../plugins/skill-factory/skills/skill-builder")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                deduped = self.module._dedupe_requested_skills(
                    ("utilities/skill-builder", "plugins/skill-factory/skills/skill-builder")
                )

            self.assertEqual(deduped, ("utilities/skill-builder",))

    def test_validate_skill_accepts_canonical_scope_for_alias_invocation(self) -> None:
        """
        Ensure the validator accepts a task-profile that names the canonical skill path when the skill is invoked via a symlink alias.
        
        Creates a canonical skill directory containing SKILL.md and a references/task-profile.json whose `scope_skill` is the canonical path and `scope_profile` is "utilities", then places a symlink alias at `utilities/skill-builder` pointing to the canonical directory. Patches repository root and internal validators to isolate scope-check behaviour, invokes `_validate_skill` on the alias, and asserts there are no findings with code `TASK_PROFILE_SCOPE`.
        """
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
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "_validate_contract", return_value=[]),
                mock.patch.object(self.module, "_validate_evals", return_value=[]),
                mock.patch.object(self.module, "_validate_reference_pi", return_value=[]),
            ):
                findings = self.module._validate_skill("utilities/skill-builder")

            scope_failures = [f for f in findings if f.code == "TASK_PROFILE_SCOPE"]
            self.assertEqual(scope_failures, [])

    def test_canonical_skill_rel_resolves_skillify_symlink_alias(self) -> None:
        """
        Verifies that a 'skillify' symlink under utilities is resolved to the canonical plugins/skill-factory/skills/skillify path.
        
        Creates a temporary repository layout where utilities/skillify is a symlink to plugins/skill-factory/skills/skillify, patches the module's REPO_ROOT to that repository, and asserts that _canonical_skill_rel("utilities/skillify") returns "plugins/skill-factory/skills/skillify".
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skillify"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skillify").symlink_to("../plugins/skill-factory/skills/skillify")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                canonical = self.module._canonical_skill_rel("utilities/skillify")

            self.assertEqual(canonical, "plugins/skill-factory/skills/skillify")

    def test_dedupe_requested_skills_uses_skillify_canonical_target(self) -> None:
        """
        Verifies deduplication prefers the aliased invocation when the canonical target is the `skillify` skill.
        
        Creates a temporary repository where `utilities/skillify` is a symlink to `plugins/skill-factory/skills/skillify`, calls `_dedupe_requested_skills` with both paths, and asserts only the alias (`utilities/skillify`) is retained.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "plugins" / "skill-factory" / "skills" / "skillify"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "utilities"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skillify").symlink_to("../plugins/skill-factory/skills/skillify")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                deduped = self.module._dedupe_requested_skills(
                    ("utilities/skillify", "plugins/skill-factory/skills/skillify")
                )

            self.assertEqual(deduped, ("utilities/skillify",))


if __name__ == "__main__":
    unittest.main()
