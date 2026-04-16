#!/usr/bin/env python3
"""Regression tests for family benchmark path canonicalization."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
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
        
        Creates a temporary repository layout with a real skill at Plugins/skill-factory/skills/code_quality_review/skill-builder and a symlink alias at Skills/skill-builder, patches REPO_ROOT to the temp root, and asserts the canonicalised result equals Plugins/skill-factory/skills/code_quality_review/skill-builder.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "Plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "Skills"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../Plugins/skill-factory/skills/code_quality_review/skill-builder")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                canonical = self.module._canonical_skill_rel("Skills/skill-builder")

            self.assertEqual(canonical, "Plugins/skill-factory/skills/code_quality_review/skill-builder")

    def test_dedupe_requested_skills_uses_canonical_target(self) -> None:
        """
        Verifies deduplication prefers a symlink alias path over its canonical target.
        
        Creates a temporary repository where `Skills/skill-builder` is a symlink to
        `Plugins/skill-factory/skills/code_quality_review/skill-builder` and asserts that passing both the
        alias and the canonical path to `_dedupe_requested_skills` yields only the
        alias entry, protecting against duplicate validations of the same skill.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "Plugins" / "skill-factory" / "skills" / "skill-builder"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "Skills"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../Plugins/skill-factory/skills/code_quality_review/skill-builder")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                deduped = self.module._dedupe_requested_skills(
                    ("Skills/skill-builder", "Plugins/skill-factory/skills/code_quality_review/skill-builder")
                )

            self.assertEqual(deduped, ("Skills/skill-builder",))

    def test_validate_skill_accepts_canonical_scope_for_alias_invocation(self) -> None:
        """
        Ensure the validator accepts a task-profile that names the canonical skill path when the skill is invoked via a symlink alias.
        
        Creates a canonical skill directory containing SKILL.md and a Infrastructure/references/task-profile.json whose `scope_skill` is the canonical path and `scope_profile` is "utilities", then places a symlink alias at `Skills/skill-builder` pointing to the canonical directory. Patches repository root and internal validators to isolate scope-check behaviour, invokes `_validate_skill` on the alias, and asserts there are no findings with code `TASK_PROFILE_SCOPE`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill_rel = "Plugins/skill-factory/skills/code_quality_review/skill-builder"
            plugin_skill = root / plugin_skill_rel
            refs = plugin_skill / "references"
            refs.mkdir(parents=True, exist_ok=True)
            (plugin_skill / "SKILL.md").write_text("# skill-builder\n", encoding="utf-8")
            (refs / "task-profile.json").write_text(
                """{
  "schema_version": "1.0",
  "profile_id": "utilities-skill-builder",
  "scope_skill": "Plugins/skill-factory/skills/code_quality_review/skill-builder",
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

            alias_parent = root / "Skills"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skill-builder").symlink_to("../Plugins/skill-factory/skills/code_quality_review/skill-builder")

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "_validate_contract", return_value=[]),
                mock.patch.object(self.module, "_validate_evals", return_value=[]),
                mock.patch.object(self.module, "_validate_reference_pi", return_value=[]),
            ):
                findings = self.module._validate_skill("Skills/skill-builder")

            scope_failures = [f for f in findings if f.code == "TASK_PROFILE_SCOPE"]
            self.assertEqual(scope_failures, [])

    def test_canonical_skill_rel_resolves_skillify_symlink_alias(self) -> None:
        """
        Verifies that a 'skillify' symlink under utilities is resolved to the canonical Plugins/skill-factory/skills/scaffolding_templates/skillify path.
        
        Creates a temporary repository layout where Skills/skillify is a symlink to Plugins/skill-factory/skills/scaffolding_templates/skillify, patches the module's REPO_ROOT to that repository, and asserts that _canonical_skill_rel("Skills/skillify") returns "Plugins/skill-factory/skills/scaffolding_templates/skillify".
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "Plugins" / "skill-factory" / "skills" / "skillify"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "Skills"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skillify").symlink_to("../Plugins/skill-factory/skills/scaffolding_templates/skillify")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                canonical = self.module._canonical_skill_rel("Skills/skillify")

            self.assertEqual(canonical, "Plugins/skill-factory/skills/scaffolding_templates/skillify")

    def test_dedupe_requested_skills_uses_skillify_canonical_target(self) -> None:
        """
        Verifies deduplication prefers the aliased invocation when the canonical target is the `skillify` skill.
        
        Creates a temporary repository where `Skills/skillify` is a symlink to `Plugins/skill-factory/skills/scaffolding_templates/skillify`, calls `_dedupe_requested_skills` with both paths, and asserts only the alias (`Skills/skillify`) is retained.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            plugin_skill = root / "Plugins" / "skill-factory" / "skills" / "skillify"
            plugin_skill.mkdir(parents=True, exist_ok=True)
            alias_parent = root / "Skills"
            alias_parent.mkdir(parents=True, exist_ok=True)
            (alias_parent / "skillify").symlink_to("../Plugins/skill-factory/skills/scaffolding_templates/skillify")

            with mock.patch.object(self.module, "REPO_ROOT", root):
                deduped = self.module._dedupe_requested_skills(
                    ("Skills/skillify", "Plugins/skill-factory/skills/scaffolding_templates/skillify")
                )

            self.assertEqual(deduped, ("Skills/skillify",))

    def test_validate_skill_reports_scope_resolver_failures(self) -> None:
        """
        Ensures resolver execution errors surface as explicit FAIL findings.

        Creates a minimal skill fixture and patches the shared scope resolver to raise.
        The benchmark validator must emit TASK_PROFILE_SCOPE_RESOLVER instead of silently
        accepting the fallback path.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            skill_rel = "plugins/skill-factory/skills/code_quality_review/skill-builder"
            skill_dir = root / skill_rel
            refs = skill_dir / "references"
            refs.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text("# skill-builder\n", encoding="utf-8")
            (refs / "task-profile.json").write_text(
                """{
  "schema_version": "1.0",
  "profile_id": "plugins-skill-factory-skills-code-quality-review-skill-builder",
  "scope_skill": "plugins/skill-factory/skills/code_quality_review/skill-builder",
  "scope_profile": "plugins",
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

            with (
                mock.patch.object(self.module, "REPO_ROOT", root),
                mock.patch.object(self.module, "_validate_contract", return_value=[]),
                mock.patch.object(self.module, "_validate_evals", return_value=[]),
                mock.patch.object(self.module, "_validate_reference_pi", return_value=[]),
                mock.patch.object(self.module, "_load_scope_skill_resolver", return_value=lambda _p: (_ for _ in ()).throw(ValueError("boom"))),
            ):
                findings = self.module._validate_skill(skill_rel)

            resolver_failures = [f for f in findings if f.code == "TASK_PROFILE_SCOPE_RESOLVER"]
            self.assertEqual(len(resolver_failures), 1)

    def test_scope_resolver_supports_versioned_harness_cache_paths(self) -> None:
        """
        Ensures harness cache aliases resolve regardless of cache plugin version segment.
        """
        resolved = self.module._resolve_scope_skill_for_path(
            "plugins/cache/agent-skills-local/harness-engineering/9.9.9/skills/ce-spec"
        )
        self.assertEqual(resolved, "product/ops/ce-spec")


if __name__ == "__main__":
    unittest.main()
