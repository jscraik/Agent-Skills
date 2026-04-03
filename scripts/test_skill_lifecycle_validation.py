#!/usr/bin/env python3
"""Regression tests for lifecycle readiness validation."""

from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "verify_skill_catalog_freshness.py"


def run_validator(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo_root), "--strict"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


class SkillLifecycleValidationTests(unittest.TestCase):
    def test_governed_skill_is_healthy_when_required_fields_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "utilities" / "healthy-skill" / "SKILL.md",
                """
                ---
                name: healthy-skill
                description: "Use when a repo needs a healthy governed skill example."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: 2026-03-24
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
                """
                ---
                name: stale-skill
                description: "Use when a repo needs a stale governed skill example."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: weekly
                last_reviewed: 2026-01-01
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
                """
                ---
                title: Missing link example
                owner: Agent Skills Team
                freshness_reviewed_on: 2026-03-24
                review_after_days: 30
                source_artifact: docs/specs/example.md
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
                            "last_reviewed": "2026-03-24",
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

    def test_cached_and_fixture_skills_are_skipped_from_catalog_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical = """
                ---
                name: shared-skill
                description: "Use when a repo needs the canonical shared skill."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: 2026-03-24
                metadata_source: frontmatter
                ---

                # Shared Skill

                ## Workflow
                1. Do the canonical thing.
            """
            cached_copy = """
                ---
                name: shared-skill
                description: |
                  Cached plugin copy with a multiline description block that
                  should not affect canonical catalog freshness checks.
                ---

                # Cached Shared Skill
            """
            fixture_copy = """
                ---
                name: fixture-skill
                description: "Fixture skill used only for tests."
                ---

                # Fixture Skill
            """

            write_text(repo_root / "utilities" / "shared-skill" / "SKILL.md", canonical)
            write_text(
                repo_root / "plugins" / "cache" / "openai-curated" / "sample" / "skills" / "shared-skill" / "SKILL.md",
                cached_copy,
            )
            write_text(
                repo_root / "utilities" / "codex-plugin-builder" / "fixtures" / "sample" / "skills" / "fixture-skill" / "SKILL.md",
                fixture_copy,
            )

            result = run_validator(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("healthy=1", result.stdout)
            self.assertIn("duplicates=0", result.stdout)
            self.assertNotIn("shared-skill", result.stdout)
            self.assertNotIn("fixture-skill", result.stdout)


if __name__ == "__main__":
    unittest.main()
