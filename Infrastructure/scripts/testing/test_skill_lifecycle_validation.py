#!/usr/bin/env python3
"""Regression tests for lifecycle readiness validation."""

from __future__ import annotations

import json
import importlib.util
import sys
from datetime import date, timedelta
import subprocess
import tempfile
import textwrap
import unittest
from unittest import mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "validation-and-linting" / "verify_skill_catalog_freshness.py"
SHADOW_SCRIPT = REPO_ROOT / "scripts" / "validation-and-linting" / "check_plugin_skill_shadowing.sh"
SELECTION_POLICY_SCRIPT = REPO_ROOT / "scripts" / "lifecycle-and-sync" / "selection_policy.py"
SKILL_DISCOVERY_SCRIPT = REPO_ROOT / "scripts" / "lifecycle-and-sync" / "skill_discovery.py"
SYNC_SCRIPT = REPO_ROOT / "scripts" / "lifecycle-and-sync" / "sync_skills.sh"

# macOS ships bash 3.2 which lacks features (mapfile, declare -A) used by
# shell scripts in this repo. Prefer a known bash 4+ path when available.
def _find_bash4() -> str:
    import shutil
    for candidate in ["/opt/homebrew/bin/bash", "/usr/local/bin/bash"]:
        if shutil.which(candidate):
            return candidate
    return "bash"

_BASH4 = _find_bash4()


def run_validator(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), "--repo-root", str(repo_root), "--strict"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_shadow_check(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [_BASH4, str(SHADOW_SCRIPT), "--repo-root", str(repo_root)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


def iso_days_ago(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


def load_validator_module():
    spec = importlib.util.spec_from_file_location("verify_skill_catalog_freshness", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load validator module from {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_selection_policy_module():
    script_dir = str(SELECTION_POLICY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("selection_policy", SELECTION_POLICY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load selection policy module from {SELECTION_POLICY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_skill_discovery_module():
    script_dir = str(SKILL_DISCOVERY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("skill_discovery", SKILL_DISCOVERY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load skill discovery module from {SKILL_DISCOVERY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillLifecycleValidationTests(unittest.TestCase):
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

    def test_governed_symlink_alias_is_enforced_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical_dir = repo_root / "plugins" / "plugin-factory" / "skills" / "plugin-builder"
            canonical_dir.mkdir(parents=True, exist_ok=True)
            write_text(
                canonical_dir / "SKILL.md",
                """
                ---
                name: plugin-builder
                description: "Canonical plugin-builder skill missing lifecycle metadata."
                ---

                # Plugin Builder
                """,
            )

            alias = repo_root / "utilities" / "plugin-builder"
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to("../Plugins/plugin-factory/skills/code_quality_review/plugin-builder", target_is_directory=True)

            result = run_validator(repo_root)
            self.assertNotEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md [skill]", result.stdout)
            self.assertIn("missing_metadata: governed skill missing `lifecycle_state`", result.stdout)

    def test_cached_and_fixture_skills_are_skipped_from_catalog_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical = f"""
                ---
                name: shared-skill
                description: "Use when a repo needs the canonical shared skill."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: {iso_days_ago(7)}
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
                repo_root / "utilities" / "plugin-builder" / "fixtures" / "sample" / "skills" / "fixture-skill" / "SKILL.md",
                fixture_copy,
            )

            result = run_validator(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("healthy=1", result.stdout)
            self.assertIn("duplicates=0", result.stdout)
            self.assertNotIn("shared-skill", result.stdout)
            self.assertNotIn("fixture-skill", result.stdout)

    def test_plugin_shadow_skill_trees_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            canonical = f"""
                ---
                name: canonical-skill
                description: "Use when a repo needs the canonical skill record."
                lifecycle_state: incubating
                maturity: experimental
                owner: Agent Skills Team
                review_cadence: monthly
                last_reviewed: {iso_days_ago(7)}
                metadata_source: frontmatter
                ---

                # Canonical Skill

                ## Workflow
                1. Execute canonical behavior.
            """
            shadow_copy = """
                ---
                name: canonical-skill
                description: "Shadow mirror that should be ignored by catalog freshness."
                ---

                # Shadow Skill

                [TODO: placeholder content]
            """

            write_text(repo_root / "utilities" / "canonical-skill" / "SKILL.md", canonical)
            write_text(
                repo_root / ".codex" / ".tmp" / "plugins" / ".agents" / "skills" / "canonical-skill" / "SKILL.md",
                shadow_copy,
            )
            write_text(
                repo_root / ".codex" / "skills" / ".system" / "canonical-skill" / "SKILL.md",
                shadow_copy,
            )

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
            module.should_skip_skill_path(Path(".codex/skills/.system/canonical-skill/SKILL.md"))
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
            packaged_skill = f"""
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

    def test_plugin_shadowing_check_allows_allowlisted_overlap(self) -> None:
        selection_policy = load_selection_policy_module()
        allowlisted = tuple(
            selection_policy.PLUGIN_VISIBLE_ROUTER_SKILL_NAMES
        ) or tuple(selection_policy.SYSTEM_BRIDGE_SKILL_NAMES)
        if not allowlisted:
            self.skipTest("No overlap allowlist configured in selection policy.")

        router_skill = allowlisted[0]
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            write_text(
                repo_root / "plugins" / "demo-plugin" / "skills" / router_skill / "SKILL.md",
                "# plugin skill",
            )
            if router_skill in selection_policy.SYSTEM_BRIDGE_SKILL_NAMES:
                system_skill_dir = repo_root / "skills-system" / router_skill
                write_text(system_skill_dir / "SKILL.md", "# bridge skill")
                flat_root = repo_root / ".agents" / "skills"
                flat_root.mkdir(parents=True, exist_ok=True)
                (flat_root / ".system").symlink_to(
                    "../../skills-system", target_is_directory=True
                )
                (flat_root / router_skill).symlink_to(f".system/{router_skill}")
            else:
                write_text(
                    repo_root / ".agents" / "skills" / router_skill / "SKILL.md",
                    "# flat skill",
                )

            result = run_shadow_check(repo_root)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertIn("Plugin-shadowing check passed", result.stdout)

    def test_selection_policy_identity_matches_discovery_identity(self) -> None:
        """
        Assert selection policy identity matches skill discovery identity.
        
        Verifies that `selection_policy.policy_identity()` and `skill_discovery.get_policy_identity()`
        produce the same value, ensuring both modules expose a consistent policy identity used for selection.
        """
        selection_policy = load_selection_policy_module()
        skill_discovery = load_skill_discovery_module()
        self.assertEqual(selection_policy.policy_identity(), skill_discovery.get_policy_identity())

    def test_skill_discovery_visibility_respects_router_allowlist(self) -> None:
        """
        Verify default visibility only includes allowlisted plugin router skills.

        Creates flat SKILL.md entries for plugin-owned skills (`coderabbit`,
        `autofix`, `code-review`, `simplify`), then patches discovery to treat
        those dirs as plugin-owned. Default visibility should return only names
        present in `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES`; advanced visibility
        should return all plugin-owned skills.
        """
        skill_discovery = load_skill_discovery_module()
        skill_names = ("coderabbit", "autofix", "code-review", "simplify")
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            flat_root = repo_root / ".agents" / "skills"
            for name in skill_names:
                write_text(
                    flat_root / name / "SKILL.md",
                    f"""
                    ---
                    name: {name}
                    description: "{name} test skill"
                    ---

                    # {name}
                    """,
                )

            with (
                mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
                mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
                mock.patch.object(
                    skill_discovery,
                    "_is_plugin_owned_skill_dir",
                    side_effect=lambda skill_dir: skill_dir.name in set(skill_names),
                ),
            ):
                default_entries = skill_discovery.discover_skill_entries(
                    source="flat",
                    visibility="default",
                )
                advanced_entries = skill_discovery.discover_skill_entries(
                    source="flat",
                    visibility="advanced",
                )

        default_names = sorted(entry.name for entry in default_entries)
        advanced_names = sorted(entry.name for entry in advanced_entries)
        expected_default = sorted(
            name for name in skill_names if name in skill_discovery.PLUGIN_VISIBLE_ROUTER_SKILL_NAMES
        )
        self.assertEqual(default_names, expected_default)
        self.assertEqual(advanced_names, sorted(skill_names))

    def test_skill_discovery_advanced_merges_plugin_lanes_when_flat_missing_them(self) -> None:
        """
        Ensure advanced discovery can merge plugin lanes when flat projection is missing them.
        
        Sets up a repository where the runtime (flat) projection exposes only `coderabbit` while the
        plugin canonical source contains lane skills (`autofix`, `code-review`, `simplify`). Asserts that
        default visibility returns what flat projects and advanced visibility merges in plugin lanes.
        """
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            flat_root = repo_root / ".agents" / "skills"
            plugin_root = repo_root / "plugins" / "coderabbit" / "skills"

            # Runtime projection keeps only router skill.
            write_text(
                flat_root / "coderabbit" / "SKILL.md",
                """
                ---
                name: coderabbit
                description: "router"
                ---
                # coderabbit
                """,
            )

            # Canonical plugin source still contains lane skills.
            for lane in ("autofix", "code-review", "simplify"):
                write_text(
                    plugin_root / lane / "SKILL.md",
                    f"""
                    ---
                    name: {lane}
                    description: "{lane}"
                    ---
                    # {lane}
                    """,
                )

            with (
                mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
                mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
            ):
                default_entries = skill_discovery.discover_skill_entries(
                    source="auto",
                    visibility="default",
                )
                advanced_entries = skill_discovery.discover_skill_entries(
                    source="auto",
                    visibility="advanced",
                )

        default_names = sorted(entry.name for entry in default_entries)
        advanced_names = sorted(entry.name for entry in advanced_entries)
        self.assertEqual(default_names, ["coderabbit"])
        self.assertEqual(advanced_names, ["autofix", "code-review", "coderabbit", "simplify"])

    def test_sync_script_consumes_selection_policy_exports(self) -> None:
        """
        Ensure the sync script references the selection policy and its exported constants required for skill syncing.
        
        Asserts that Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh contains `selection_policy.py` and the exports:
        `SELECTION_POLICY_REPO_SCAN_ROOTS`, `SELECTION_POLICY_EXCLUDED_SEGMENTS`,
        `SELECTION_POLICY_HIDDEN_FLAT_SKILLS`, `SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS`,
        and `SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS`.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("selection_policy.py", content)
        self.assertIn("SELECTION_POLICY_REPO_SCAN_ROOTS", content)
        self.assertIn("SELECTION_POLICY_EXCLUDED_SEGMENTS", content)
        self.assertIn("SELECTION_POLICY_HIDDEN_FLAT_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS", content)
        self.assertIn("projection_integrity.py", content)

    def test_sync_script_projects_profile_plugin_source_mirrors(self) -> None:
        """
        Ensure profile-home sync keeps marketplace source paths resolvable.

        Codex profile homes (for example ~/.codex-red) receive a copied
        marketplace.json. This test enforces that sync_skills also mirrors
        plugin source dirs into <profile>/Plugins/<name> so marketplace
        source.path entries like ./Plugins/<name> remain valid.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"',
            content,
        )


if __name__ == "__main__":
    unittest.main()
