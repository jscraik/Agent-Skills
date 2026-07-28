#!/usr/bin/env python3
"""Catalog and policy regression tests for lifecycle readiness validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from test_skill_lifecycle_validation_impl import (
    iso_days_ago,
    load_selection_policy_module,
    load_validator_module,
    run_shadow_check,
    run_validator,
    write_text,
)



def _write_catalog_duplicate_fixture(repo_root: Path, *, reviewed_on: str) -> None:
    write_text(
        repo_root / "utilities" / "shared-skill" / "SKILL.md",
        f"""
        ---
        name: shared-skill
        description: "Canonical shared skill."
        lifecycle_state: incubating
        maturity: experimental
        owner: Agent Skills Team
        review_cadence: monthly
        last_reviewed: {reviewed_on}
        metadata_source: frontmatter
        ---
        # Shared Skill
        """,
    )
    write_text(
        repo_root / "plugins" / "cache" / "openai-curated" / "sample" / "skills" / "shared-skill" / "SKILL.md",
        """
        ---
        name: shared-skill
        description: |
          Cached plugin copy
          with multiline description.
        ---
        # Cached Shared Skill
        """,
    )
    write_text(
        repo_root / "utilities" / "plugin-builder" / "fixtures" / "sample" / "skills" / "fixture-skill" / "SKILL.md",
        """
        ---
        name: fixture-skill
        description: "Fixture-only skill."
        ---

        # Fixture Skill
        """,
    )


def _write_plugin_shadow_fixture(repo_root: Path, *, reviewed_on: str) -> None:
    write_text(
        repo_root / "utilities" / "canonical-skill" / "SKILL.md",
        f"""
        ---
        name: canonical-skill
        description: "Use when a repository needs the canonical skill record."
        lifecycle_state: incubating
        maturity: experimental
        owner: Agent Skills Team
        review_cadence: monthly
        last_reviewed: {reviewed_on}
        metadata_source: frontmatter
        ---

        # Canonical Skill

        ## Workflow
        1. Execute canonical behavior.
        """,
    )
    shadow = """
        ---
        name: canonical-skill
        description: "Ignored shadow."
        ---

        # Shadow Skill

        [TODO: placeholder content]
    """
    for path in (
        repo_root / ".codex" / ".tmp" / "plugins" / ".agents" / "skills" / "canonical-skill" / "SKILL.md",
        repo_root / ".codex" / "skills" / ".system" / "canonical-skill" / "SKILL.md",
    ):
        write_text(path, shadow)


def _write_command_surface_overlap_fixture(repo_root: Path) -> None:
    write_text(
        repo_root / "plugins" / "demo-plugin" / "skills" / "demo-command" / "SKILL.md",
        "# plugin skill",
    )
    write_text(
        repo_root / ".agents" / "skills" / "demo-command" / "SKILL.md",
        """
        ---
        name: demo-command
        ---

        # Demo Command

        Source: Plugins/demo-plugin/skills/demo-command/SKILL.md
        """,
    )
    write_text(
        repo_root / ".skillsets" / "command-surface.json",
        json.dumps(
            {
                "handles": [{"kind": "skill", "handle": "demo-command", "source_path": "Plugins/demo-plugin/skills/demo-command/SKILL.md"}],
                "hidden_handles": [{"kind": "skill", "handle": "demo-hidden", "source_path": "Plugins/demo-plugin/skills/demo-hidden/SKILL.md"}],
            }
        ),
    )

class SkillLifecycleCatalogValidationTests(unittest.TestCase):
    def test_governed_skill_is_healthy_when_required_fields_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "utilities" / "healthy-skill" / "SKILL.md",
                f"""
                ---
                name: healthy-skill
                description: "Use when a repo needs a healthy governed skill example."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: {iso_days_ago(7)}
                metadata_source: frontmatter
                ---

                # Healthy Skill

                ## Workflow
                1. Do the real thing.
                """,
            )

            result = run_validator(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("healthy=1", result.stdout)
            self.assertIn("degraded=0", result.stdout)
            self.assertIn("blocked=0", result.stdout)

    def test_overdue_review_cadence_is_reported_as_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "utilities" / "stale-skill" / "SKILL.md",
                f"""
                ---
                name: stale-skill
                description: "Use when a repo needs a stale governed skill example."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: weekly
                last_reviewed: {iso_days_ago(45)}
                metadata_source: frontmatter
                ---

                # Stale Skill

                ## Workflow
                1. Do the real thing.
                """,
            )

            result = run_validator(repo_root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("stale_review_cadence", result.stdout)
            self.assertIn("degraded=1", result.stdout)

    def test_solution_entries_require_linkage_and_freshness_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "docs" / "solutions" / "missing-link.md",
                f"""
                ---
                title: Missing link example
                owner: Agent Skills Team
                freshness_reviewed_on: {iso_days_ago(3)}
                review_after_days: 30
                source_artifact: Docs/specs/example.md
                ---

                ## Problem
                This is a reusable problem pattern.

                ## Resolution
                This is a reusable resolution.
                """,
            )

            result = run_validator(repo_root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("orphaned_solution_link", result.stdout)
            self.assertIn("blocked=1", result.stdout)

    def test_governed_plugin_manifest_requires_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            plugin_manifest = repo_root / "plugins" / "example-plugin" / ".codex-plugin" / "plugin.json"
            plugin_manifest.parent.mkdir(parents=True, exist_ok=True)
            plugin_manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "name": "example-plugin",
                        "description": "Plugin for lifecycle validation tests.",
                        "governance": {
                            "lifecycle_state": "incubating",
                            "maturity": "experimental",
                            "review_cadence": "monthly",
                            "last_reviewed": iso_days_ago(7),
                            "metadata_source": "plugin_manifest",
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_validator(repo_root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("governed plugin manifest missing `governance.owner`", result.stdout)
            self.assertIn("blocked=1", result.stdout)

    def test_governed_skill_is_enforced_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical_dir = repo_root / "Plugins" / "skill-factory" / "skills" / "skill-factory-router"
            canonical_dir.mkdir(parents=True, exist_ok=True)
            write_text(
                canonical_dir / "SKILL.md",
                """
                ---
                name: skill-factory-router
                description: "Canonical skill-factory-router skill missing lifecycle metadata."
                ---

                # Skill Factory Router
                """,
            )

            result = run_validator(repo_root)
            self.assertNotEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugins/skill-factory/skills/skill-factory-router/SKILL.md [packaged_skill]", result.stdout)
            self.assertIn("pilot skill missing Infrastructure/references/task-profile.json", result.stdout)

    def test_cached_and_fixture_skills_are_skipped_from_catalog_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            _write_catalog_duplicate_fixture(repo_root, reviewed_on=iso_days_ago(7))

            result = run_validator(repo_root)

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("healthy=1", result.stdout)
        self.assertIn("duplicates=0", result.stdout)
        self.assertNotIn("shared-skill", result.stdout)
        self.assertNotIn("fixture-skill", result.stdout)

    def test_plugin_shadow_skill_trees_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            _write_plugin_shadow_fixture(repo_root, reviewed_on=iso_days_ago(7))

            result = run_validator(repo_root)

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("healthy=1", result.stdout)
        self.assertIn("degraded=0", result.stdout)
        self.assertIn("duplicates=0", result.stdout)
        self.assertNotIn("scaffold_quality_gap", result.stdout)

    def test_should_skip_skill_path_uses_granular_codex_prefixes(self) -> None:
        module = load_validator_module()

        self.assertTrue(
            module.should_skip_skill_path(Path(".codex/.tmp/Plugins/.agents/skills/canonical-skill/SKILL.md"))
        )
        self.assertTrue(
            module.should_skip_skill_path(Path(".agents/skills/.system/canonical-skill/SKILL.md"))
        )
        self.assertTrue(
            module.should_skip_skill_path(Path(".codex/skills/.system/canonical-skill/SKILL.md"))
        )
        self.assertTrue(
            module.should_skip_skill_path(Path("Plugins/cache/openai-curated/cloudflare/skills/cache-skill/SKILL.md"))
        )
        self.assertFalse(module.should_skip_skill_path(Path(".codex/skills/custom-skill/SKILL.md")))

    def test_packaged_representation_does_not_count_as_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical = f"""
                ---
                name: shared-catalog-skill
                description: "Canonical shared skill for duplicate accounting tests."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: {iso_days_ago(7)}
                metadata_source: frontmatter
                ---

                # Shared Catalog Skill
            """
            packaged = """
                ---
                name: shared-catalog-skill
                description: "Packaged representation mirrored from canonical skill."
                ---

                # Packaged Shared Catalog Skill
            """

            write_text(repo_root / "utilities" / "shared-catalog-skill" / "SKILL.md", canonical)
            write_text(
                repo_root / "plugins" / "example-plugin" / "skills" / "shared-catalog-skill" / "SKILL.md",
                packaged,
            )

            result = run_validator(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("duplicates=0", result.stdout)
            self.assertNotIn("Duplicate skill names", result.stdout)

    def test_packaged_representation_uses_symlinked_canonical_skill_alias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            packaged_skill = """
                ---
                name: skill-builder
                description: "Packaged skill representation mirrored from canonical source."
                metadata:
                  owner: Agent Skills Team
                ---

                # Skill Builder
            """

            write_text(
                repo_root / "plugins" / "skill-factory" / "skills" / "skill-builder" / "SKILL.md",
                packaged_skill,
            )

            utilities_dir = repo_root / "utilities"
            utilities_dir.mkdir(parents=True, exist_ok=True)
            try:
                (utilities_dir / "skill-builder").symlink_to(
                    Path("../Plugins/skill-factory/skills/code_quality_review/skill-builder"),
                    target_is_directory=True,
                )
            except (OSError, NotImplementedError):
                self.skipTest("Filesystem does not support directory symlinks in this environment.")

            result = run_validator(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertNotIn("representation_split_brain", result.stdout)

    def test_plugin_shadowing_check_passes_without_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "plugins" / "coderabbit" / "skills" / "coderabbit" / "SKILL.md",
                "# plugin skill",
            )
            write_text(
                repo_root / ".agents" / "skills" / "other-skill" / "SKILL.md",
                "# flat skill",
            )

            result = run_shadow_check(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugin-shadowing check passed", result.stdout)

    def test_plugin_shadowing_check_fails_with_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "plugins" / "demo-plugin" / "skills" / "demo-shadow" / "SKILL.md",
                "# plugin skill",
            )
            write_text(
                repo_root / ".agents" / "skills" / "demo-shadow" / "SKILL.md",
                "# flat skill",
            )

            result = run_shadow_check(repo_root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Plugin-shadowing check failed", result.stderr)
            self.assertIn("- demo-shadow", result.stderr)

    def test_plugin_shadowing_check_allows_command_surface_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            _write_command_surface_overlap_fixture(repo_root)

            result = run_shadow_check(repo_root)

        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("Plugin-shadowing check passed", result.stdout)

    def test_plugin_shadowing_check_ignores_plugin_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root
                / "Plugins"
                / "demo-plugin"
                / "fixtures"
                / "archive"
                / "skills"
                / "archived-lane"
                / "SKILL.md",
                "# archived fixture skill",
            )
            write_text(
                repo_root / ".agents" / "skills" / "archived-lane" / "SKILL.md",
                "# flat skill",
            )

            result = run_shadow_check(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugin-shadowing check passed", result.stdout)

    def test_plugin_shadowing_check_allows_system_bridge_overlap(self) -> None:
        selection_policy = load_selection_policy_module()
        allowlisted = tuple(selection_policy.SYSTEM_BRIDGE_SKILL_NAMES)
        if not allowlisted:
            self.skipTest("No system bridge overlap allowlist configured in selection policy.")

        router_skill = allowlisted[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "plugins" / "demo-plugin" / "skills" / router_skill / "SKILL.md",
                "# plugin skill",
            )
            system_skill_dir = repo_root / "skills-system" / router_skill
            write_text(system_skill_dir / "SKILL.md", "# bridge skill")
            flat_root = repo_root / ".agents" / "skills"
            flat_root.mkdir(parents=True, exist_ok=True)
            (flat_root / ".system").symlink_to(
                "../../skills-system", target_is_directory=True
            )

            result = run_shadow_check(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugin-shadowing check passed", result.stdout)
