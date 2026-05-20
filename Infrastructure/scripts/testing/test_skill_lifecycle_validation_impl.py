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
SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_skill_catalog_freshness.py"
SHADOW_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "check_plugin_skill_shadowing.sh"
SELECTION_POLICY_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "selection_policy.py"
SKILL_DISCOVERY_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "skill_discovery.py"
RUNTIME_SURFACE_POLICY_SCRIPT = (
    REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "runtime_surface_policy.py"
)
SYNC_SCRIPT = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills.sh"

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


def load_runtime_surface_policy_module():
    script_dir = str(RUNTIME_SURFACE_POLICY_SCRIPT.parent)
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
    spec = importlib.util.spec_from_file_location("runtime_surface_policy", RUNTIME_SURFACE_POLICY_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load runtime surface policy module from {RUNTIME_SURFACE_POLICY_SCRIPT}")
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

    def test_selection_policy_identity_matches_discovery_identity(self) -> None:
        """
        Assert selection policy identity matches skill discovery identity.

        Verifies that `selection_policy.policy_identity()` and `skill_discovery.get_policy_identity()`
        produce the same value, ensuring both modules expose a consistent policy identity used for selection.
        """
        selection_policy = load_selection_policy_module()
        skill_discovery = load_skill_discovery_module()
        self.assertEqual(selection_policy.policy_identity(), skill_discovery.get_policy_identity())

    def test_selection_policy_plugin_router_skills_exist_in_plugin_sources(self) -> None:
        """
        Ensure each policy-declared plugin router skill resolves to a real plugin SKILL.md directory.

        This guards policy drift where a skill name remains in selection policy lists
        after the corresponding plugin skill folder has been moved or removed.
        """
        selection_policy = load_selection_policy_module()
        skill_discovery = load_skill_discovery_module()
        discovered_plugin_skill_names = {
            path.name
            for path in skill_discovery._iter_plugin_skill_dirs()  # pylint: disable=protected-access
        }
        missing = sorted(
            name
            for name in selection_policy.PLUGIN_VISIBLE_ROUTER_SKILL_NAMES
            if name not in discovered_plugin_skill_names
        )
        self.assertEqual(missing, [])

    def test_catalog_default_surface_matches_default_discovery_surface(self) -> None:
        """
        Ensure catalog/default and discovery/default surfaces stay identical.

        This catches contract drift where `ask skills list` (catalog view) and
        `skill_discovery.py --visibility default` disagree on visible skill names.
        """
        skill_discovery = load_skill_discovery_module()
        default_entries = skill_discovery.discover_skill_entries(
            source="auto",
            visibility="default",
        )
        catalog_entries = skill_discovery.discover_catalog_entries(
            source="auto",
            advanced=False,
        )
        self.assertEqual(
            sorted(entry.name for entry in catalog_entries),
            sorted(entry.name for entry in default_entries),
        )

    def test_skill_discovery_visibility_respects_router_allowlist(self) -> None:
        """
        Verify default visibility only includes allowlisted plugin router skills.

        Creates flat SKILL.md entries for plugin-owned skills (`coderabbit`,
        `code-review`), then patches discovery to treat
        those dirs as plugin-owned. Default visibility should return only names
        present in `PLUGIN_VISIBLE_ROUTER_SKILL_NAMES`; advanced visibility
        should return all plugin-owned skills.
        """
        skill_discovery = load_skill_discovery_module()
        skill_names = ("coderabbit", "code-review")
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

    def test_skill_discovery_default_visibility_includes_rooted_runtime_roots(self) -> None:
        """Ensure rooted first-level runtime entries stay visible in the default catalog."""
        skill_discovery = load_skill_discovery_module()
        root_names = ("agent-ops", "harness-engineering", "skill-factory")
        latent_name = "hidden-latent-skill"
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            flat_root = repo_root / ".agents" / "skills"
            for name in (*root_names, latent_name):
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
            ):
                default_entries = skill_discovery.discover_skill_entries(
                    source="flat",
                    visibility="default",
                )
                advanced_entries = skill_discovery.discover_skill_entries(
                    source="flat",
                    visibility="advanced",
                )

        self.assertEqual(sorted(entry.name for entry in default_entries), sorted(root_names))
        self.assertEqual(sorted(entry.name for entry in advanced_entries), sorted([*root_names, latent_name]))

    def test_runtime_surface_policy_classifies_rooted_visibility(self) -> None:
        """Keep rooted runtime visibility in one policy module instead of discovery-only logic."""
        runtime_policy = load_runtime_surface_policy_module()

        self.assertEqual(runtime_policy.active_projection_mode(["agent-ops"]), "rooted")
        self.assertEqual(runtime_policy.active_projection_mode(["autofix"]), "flat")
        self.assertEqual(runtime_policy.active_projection_mode(["agent-ops", "autofix"]), "mixed")
        self.assertTrue(runtime_policy.is_default_visible_skill_name("agent-ops"))
        self.assertTrue(runtime_policy.is_default_visible_skill_name("autofix"))
        self.assertFalse(runtime_policy.is_default_visible_skill_name("hidden-latent-skill"))
        mixed_report = runtime_policy.runtime_surface_report(["agent-ops", "autofix"])
        self.assertEqual(mixed_report.projection_mode, "mixed")
        self.assertFalse(mixed_report.is_valid_projection)
        self.assertEqual(mixed_report.extra_first_level_names, ["autofix"])
        self.assertEqual(
            runtime_policy.rooted_runtime_name_drift(["agent-ops", "unexpected-skill"]),
            (
                ["unexpected-skill"],
                sorted(set(runtime_policy.ROOT_SKILL_SETS) - {"agent-ops"}),
            ),
        )

    def test_skill_discovery_visibility_predicate_uses_runtime_surface_policy(self) -> None:
        """Assert visibility policy can be tested without running full discovery."""
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            plugin_router = repo_root / "Plugins" / "cache" / "local" / "plugin" / "skills" / "plugin-router"
            plugin_lane = repo_root / "Plugins" / "cache" / "local" / "plugin" / "skills" / "code-review"
            project_skill = repo_root / ".agents" / "skills" / "agent-ops"
            hidden_skill = repo_root / ".agents" / "skills" / "not-a-default"
            for path in (plugin_router, plugin_lane, project_skill, hidden_skill):
                path.mkdir(parents=True, exist_ok=True)

            with mock.patch.object(skill_discovery, "REPO_ROOT", repo_root):
                self.assertTrue(skill_discovery.is_skill_visible("agent-ops", project_skill, "default"))
                self.assertFalse(skill_discovery.is_skill_visible("not-a-default", hidden_skill, "default"))
                self.assertFalse(skill_discovery.is_skill_visible("plugin-router", plugin_router, "default"))
                self.assertFalse(skill_discovery.is_skill_visible("code-review", plugin_lane, "default"))
                self.assertTrue(skill_discovery.is_skill_visible("plugin-router", plugin_router, "advanced"))
                self.assertTrue(skill_discovery.is_skill_visible("code-review", plugin_lane, "advanced"))

    def test_skill_discovery_advanced_merges_plugin_lanes_when_flat_missing_them(self) -> None:
        """
        Ensure advanced discovery can merge plugin lanes when flat projection is missing them.

        Sets up a repository where the runtime (flat) projection exposes only `coderabbit` while the
        plugin canonical source contains lane skills (`code-review`). Asserts that
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
            for lane in ("code-review",):
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
        self.assertEqual(default_names, [])
        self.assertEqual(advanced_names, ["code-review", "coderabbit"])

    def test_skill_discovery_advanced_includes_local_plugin_cache_skills(self) -> None:
        """Ensure operator catalogue discovery includes installed OpenAI plugin cache skills."""
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            flat_root = repo_root / ".agents" / "skills"
            cache_skill_root = (
                repo_root
                / "Plugins"
                / "cache"
                / "openai-curated"
                / "build-web-apps"
                / "version"
                / "skills"
            )
            local_cache_skill_root = (
                repo_root
                / "Plugins"
                / "cache"
                / "agent-skills-local"
                / "skill-factory"
                / "version"
                / "skills"
            )
            browser_cache_skill_root = (
                repo_root
                / "Plugins"
                / "cache"
                / "openai-bundled"
                / "browser-use"
                / "version"
                / "skills"
            )
            browser_source_skill_root = repo_root / "Plugins" / "browser-use" / "skills"

            write_text(
                flat_root / "agent-ops" / "SKILL.md",
                """
                ---
                name: agent-ops
                description: "root router"
                ---
                # agent-ops
                """,
            )
            write_text(
                cache_skill_root / "frontend-app-builder" / "SKILL.md",
                """
                ---
                name: frontend-app-builder
                description: "Build frontend apps from the local plugin cache."
                ---
                # frontend-app-builder
                """,
            )
            write_text(
                cache_skill_root.parent / "fixtures" / "example" / "skills" / "fixture-only" / "SKILL.md",
                """
                ---
                name: fixture-only
                description: "Fixture skill should not be catalogued."
                ---
                # fixture-only
                """,
            )
            write_text(
                local_cache_skill_root / "skill-factory-router" / "SKILL.md",
                """
                ---
                name: skill-factory-router
                description: "Local cache mirror should not shadow canonical plugin sources."
                ---
                # skill-factory-router
                """,
            )
            write_text(
                browser_cache_skill_root / "browser" / "SKILL.md",
                """
                ---
                name: browser
                description: "Cache mirror should not shadow canonical plugin source."
                ---
                # browser
                """,
            )
            write_text(
                browser_source_skill_root / "browser" / "SKILL.md",
                """
                ---
                name: browser
                description: "Canonical browser plugin source."
                ---
                # browser
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

        self.assertEqual(sorted(entry.name for entry in default_entries), ["agent-ops"])
        self.assertEqual(
            sorted(entry.name for entry in advanced_entries),
            ["agent-ops", "frontend-app-builder", "skill-factory-router"],
        )
        local_router_entry = next(entry for entry in advanced_entries if entry.name == "skill-factory-router")
        self.assertEqual(
            local_router_entry.source_dir.relative_to(repo_root).as_posix(),
            "Plugins/cache/agent-skills-local/skill-factory/version/skills/skill-factory-router",
        )

    def test_skill_discovery_auto_advanced_includes_repo_non_default_skills(self) -> None:
        """
        Ensure auto+advanced discovery keeps non-default repository skills visible.

        When flat runtime projection exists, default discovery should still follow
        flat policy, while advanced discovery must augment with canonical repo
        roots so non-default skills do not disappear after sync.
        """
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            flat_root = repo_root / ".agents" / "skills"
            system_root = flat_root / ".system"
            repo_skill_root = repo_root / "Skills" / "engineering" / "diagram-cli"

            write_text(
                flat_root / "autofix" / "SKILL.md",
                """
                ---
                name: autofix
                description: "default surface skill"
                ---
                # autofix
                """,
            )
            write_text(
                repo_skill_root / "SKILL.md",
                """
                ---
                name: diagram-cli
                description: "non-default repo skill"
                ---
                # diagram-cli
                """,
            )

            with (
                mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
                mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
                mock.patch.object(skill_discovery, "SYSTEM_LANE_DIR", system_root),
            ):
                default_entries = skill_discovery.discover_skill_entries(
                    source="auto",
                    visibility="default",
                )
                advanced_entries = skill_discovery.discover_skill_entries(
                    source="auto",
                    visibility="advanced",
                )

        self.assertEqual(sorted(entry.name for entry in default_entries), ["autofix"])
        self.assertEqual(
            sorted(entry.name for entry in advanced_entries),
            ["autofix", "diagram-cli"],
        )

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
        self.assertIn("SELECTION_POLICY_DEFAULT_VISIBLE_FLAT_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS", content)
        self.assertIn("projection_integrity.py", content)

    def test_sync_script_projects_profile_plugin_source_mirrors(self) -> None:
        """
        Verify the sync script mirrors plugin source directories into profile plugin roots so marketplace source paths remain resolvable.

        Asserts that sync_skills.sh invokes sync_home_plugin_mirrors with both the profile plugins root and individual profile plugins paths, ensuring copied marketplace.json entries like ./Plugins/<name> continue to point to valid plugin locations.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins_root"',
            content,
        )
        self.assertIn(
            'sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"',
            content,
        )

    def test_sync_script_prunes_only_repo_managed_stale_home_plugin_entries(self) -> None:
        """
        Ensure removed local-marketplace entries do not linger in profile homes.

        When vendored curated plugins are removed from the local marketplace,
        stale `~/.codex/Plugins/<name>` installs should be removed so the
        local runtime surface matches the declared marketplace set, but
        unrelated home plugins must not be deleted as collateral damage. The
        prune guard also needs a legacy fallback for repo-managed copies that
        were created before the marker file existed.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('local repo_plugin_marker=".codex-repo-plugin-source"', content)
        self.assertIn('keep_file="$state_dir/home-plugins.keep"', content)
        self.assertIn("is_repo_managed_home_plugin_copy()", content)
        self.assertIn('legacy_source_dir="$canonical_plugins_dir/$(basename "$existing_dir")"', content)
        self.assertIn('cmp -s -- "$source_manifest" "$existing_manifest"', content)
        self.assertIn('if ! is_repo_managed_home_plugin_copy "$existing_dir"; then', content)
        self.assertIn('Removed stale home plugin entry', content)

    def test_sync_script_repairs_repo_backed_home_plugin_root_symlinks(self) -> None:
        """
        Verify the sync script replaces repo-backed home plugin-root symlinks with real directories before mirroring profile plugin roots.

        Asserts the sync script contains the repair helper invocation `ensure_real_home_plugin_root()`, a replacement log message, and specific calls for profile plugin roots and subsequent `sync_home_plugin_mirrors` invocation.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("ensure_real_home_plugin_root()", content)
        self.assertIn("Replaced repo-backed symlinked", content)
        self.assertIn(
            'ensure_real_home_plugin_root "$profile_plugins" "$plugins_dir" "profile plugin root"',
            content,
        )
        self.assertIn(
            'ensure_real_home_plugin_root "$profile_plugins_root" "$plugins_dir" "profile Plugins root"',
            content,
        )
        self.assertIn(
            'ensure_real_home_plugin_root "$profile_agents_plugins" "$plugins_dir" "profile .agents plugin root"',
            content,
        )
        self.assertIn(
            'sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"',
            content,
        )

    def test_sync_script_installs_home_plugins_as_copied_directories(self) -> None:
        """
        Checks that the sync script installs home plugins as copied directories rather than symlinks.

        Asserts the script invokes the copy-based installer invocation, writes a marker file containing the source real path into the target, and contains the log message `Installed home plugin copy`.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('sync_user_skills "$source_dir" "$target_dir" 0 copy', content)
        self.assertIn('marker_file="$target_dir/$repo_plugin_marker"', content)
        self.assertIn('printf \'%s\\n\' "$source_real" > "$marker_file"', content)
        self.assertIn("Installed home plugin copy", content)

    def test_sync_script_materializes_visible_runtime_and_cache_skill_aliases(self) -> None:
        """
        Verify the sync script materializes plugin skill aliases for runtime and cache copies.

        Asserts that `normalize_plugin_copy()` includes top-level alias materialization
        logic that preserves nested symlinks during directory copies and that both
        runtime and cache flows
        invoke normalization.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("normalize_plugin_copy()", content)
        self.assertIn('find "$skills_dir" -mindepth 1 -maxdepth 1 -type l -print', content)
        self.assertIn('cp -R "$resolved" "$skill_entry"', content)
        self.assertIn('normalize_plugin_copy "$1" "runtime"', content)
        self.assertIn('normalize_plugin_copy "$1" "cached"', content)
        self.assertIn("whole_plugin_dir_symlinks_materialized=1", content)
        self.assertIn(
            'whole_plugin_dir_symlinks_materialized=$((whole_plugin_dir_symlinks_materialized + 1))',
            content,
        )
        self.assertIn("Refusing to materialize ${label} symlink whose destination is inside its source tree", content)

    def test_sync_script_skips_downstream_publication_when_sources_are_stale(self) -> None:
        """
        Ensure sync does not publish stale flat skills or runtime caches downstream.

        When sandbox or permission boundaries prevent regenerating a source
        projection, downstream home/profile copies should be skipped instead of
        republishing whatever stale content happens to be present.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("flat_projection_rebuilt=0", content)
        self.assertIn("runtime_cache_fresh=0", content)
        self.assertIn("runtime_cache_rebuild_blocked=0", content)
        self.assertIn("mark_runtime_cache_stale()", content)
        self.assertIn('if [ "$runtime_cache_rebuild_blocked" = "0" ]; then', content)
        self.assertIn("flat_projection_rebuilt=1", content)
        self.assertIn('if [ "$flat_projection_rebuilt" = "1" ]; then', content)
        self.assertIn('if [ "$runtime_cache_fresh" != "1" ]; then', content)
        self.assertIn("Skipping home skills sync because flat runtime skill projection was not rebuilt.", content)
        self.assertIn("Skipping profile cache publication because runtime cache rebuild was not fresh.", content)

    def test_sync_script_regenerates_versioned_visible_local_cache_roots(self) -> None:
        """
        Ensure sync regenerates versioned visible local cache roots.

        Some Codex builds still inspect
        `plugins/cache/agent-skills-local/<plugin>/<version>/skills`, so sync
        must materialize that cache from the canonical marketplace plugin
        source rather than deleting it as stale.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            "sync_versioned_local_marketplace_cache()",
            content,
        )
        self.assertIn(
            'sync_versioned_local_marketplace_cache "$plugins_dir/marketplace.json" "$plugins_dir/cache"',
            content,
        )
        self.assertIn(
            'cleanup_legacy_local_marketplace_cache "$plugins_dir/cache/local"',
            content,
        )
        self.assertIn(
            'cleanup_legacy_local_marketplace_cache "$runtime_cache_root/local"',
            content,
        )

    def test_sync_script_defaults_local_marketplace_to_agent_skills_identity(self) -> None:
        """
        Ensure local-source plugins default to the canonical local marketplace identity.

        Curated plugins are declared with `marketplace` metadata per entry and
        must stay under that cache family rather than inheriting the manifest
        top-level marketplace name.
        """
        content = SYNC_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            '(.name // "agent-skills-local" | tostring | trim) as $default_market',
            content,
        )
        self.assertIn(
            "(.marketplace // $source.marketplace // $default_market | tostring | trim) as $market",
            content,
        )


if __name__ == "__main__":
    unittest.main()
