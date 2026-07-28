#!/usr/bin/env python3
"""Discovery regression tests for lifecycle readiness validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from test_skill_lifecycle_validation_impl import (
    load_runtime_surface_policy_module,
    load_selection_policy_module,
    load_skill_discovery_module,
    write_text,
)

__test__ = False


def _write_discovery_skill(path: Path, name: str, description: str) -> None:
    write_text(
        path / "SKILL.md",
        f"""
        ---
        name: {name}
        description: "{description}"
        ---

        # {name}
        """,
    )


def _discover_plugin_visibility(
    skill_discovery, repo_root: Path, skill_names: tuple[str, ...]
) -> tuple[list[Any], list[Any]]:
    flat_root = repo_root / ".agents" / "skills"
    for name in skill_names:
        _write_discovery_skill(flat_root / name, name, f"{name} test skill")
    with (
        mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
        mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
        mock.patch.object(
            skill_discovery,
            "_is_plugin_owned_skill_dir",
            side_effect=lambda skill_dir: skill_dir.name in set(skill_names),
        ),
    ):
        return (
            skill_discovery.discover_skill_entries(source="flat", visibility="default"),
            skill_discovery.discover_skill_entries(source="flat", visibility="advanced"),
        )


def _discover_advanced_plugin_lanes(skill_discovery, repo_root: Path) -> tuple[list[Any], list[Any]]:
    flat_root = repo_root / ".agents" / "skills"
    _write_discovery_skill(flat_root / "coderabbit", "coderabbit", "router")
    _write_discovery_skill(
        repo_root / "plugins" / "coderabbit" / "skills" / "code-review",
        "code-review",
        "code-review",
    )
    with (
        mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
        mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
    ):
        return (
            skill_discovery.discover_skill_entries(source="auto", visibility="default"),
            skill_discovery.discover_skill_entries(source="auto", visibility="advanced"),
        )


def _write_local_cache_fixture(repo_root: Path) -> None:
    flat_root = repo_root / ".agents" / "skills"
    _write_discovery_skill(flat_root / "agent-ops", "agent-ops", "root router")
    _write_discovery_skill(
        repo_root / "Plugins" / "cache" / "openai-curated" / "build-web-apps" / "version" / "skills" / "frontend-app-builder",
        "frontend-app-builder",
        "Build frontend apps from the local plugin cache.",
    )
    _write_discovery_skill(
        repo_root / "Plugins" / "cache" / "openai-curated" / "build-web-apps" / "version" / "fixtures" / "example" / "skills" / "fixture-only",
        "fixture-only",
        "Fixture skill should not be catalogued.",
    )
    _write_discovery_skill(
        repo_root / "Plugins" / "cache" / "agent-skills-local" / "skill-factory" / "version" / "skills" / "skill-factory-router",
        "skill-factory-router",
        "Local cache mirror should not shadow canonical plugin sources.",
    )
    _write_discovery_skill(
        repo_root / "Plugins" / "cache" / "openai-bundled" / "browser-use" / "version" / "skills" / "browser",
        "browser",
        "Cache mirror should not shadow canonical plugin source.",
    )
    _write_discovery_skill(
        repo_root / "Plugins" / "browser-use" / "skills" / "browser",
        "browser",
        "Canonical browser plugin source.",
    )


def _discover_local_cache_entries(skill_discovery, repo_root: Path) -> tuple[list[Any], list[Any]]:
    flat_root = repo_root / ".agents" / "skills"
    with (
        mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
        mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
    ):
        return (
            skill_discovery.discover_skill_entries(source="auto", visibility="default"),
            skill_discovery.discover_skill_entries(source="auto", visibility="advanced"),
        )


def _discover_auto_default_entries(skill_discovery, repo_root: Path) -> tuple[list[Any], list[Any]]:
    flat_root = repo_root / ".agents" / "skills"
    _write_discovery_skill(flat_root / "autofix", "autofix", "default surface skill")
    _write_discovery_skill(
        repo_root / "Skills" / "engineering" / "autofix",
        "autofix",
        "default source skill",
    )
    _write_discovery_skill(
        repo_root / "Skills" / "engineering" / "diagram-cli",
        "diagram-cli",
        "source-only repo skill",
    )
    with (
        mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
        mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", flat_root),
        mock.patch.object(skill_discovery, "SYSTEM_LANE_DIR", flat_root / ".system"),
    ):
        return (
            skill_discovery.discover_skill_entries(source="auto", visibility="default"),
            skill_discovery.discover_skill_entries(source="auto", visibility="advanced"),
        )

class SkillLifecycleDiscoveryValidationTests(unittest.TestCase):
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

    def test_first_party_skills_are_default_visible_for_picker_routing(self) -> None:
        """
        Keep first-party canonical skills available on the default picker surface.

        Command handles no longer carry the broad skill surface. The deterministic
        SDK projection therefore exposes repo-owned canonical skills by default
        unless the policy explicitly hides them.
        """
        selection_policy = load_selection_policy_module()
        repo_root = Path(__file__).resolve().parents[3]
        skill_path = repo_root / "Skills" / "agent-ops" / "prek-pro" / "SKILL.md"

        self.assertTrue(selection_policy.DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS)
        self.assertTrue(skill_path.is_file())
        skill_text = skill_path.read_text(encoding="utf-8")
        self.assertIn("lifecycle_state: active", skill_text)

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
        skill_discovery = load_skill_discovery_module()
        skill_names = ("coderabbit", "code-review")
        with tempfile.TemporaryDirectory() as tmpdir:
            default_entries, advanced_entries = _discover_plugin_visibility(
                skill_discovery,
                Path(tmpdir).resolve(),
                skill_names,
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
                mock.patch.object(skill_discovery, "SYSTEM_LANE_DIR", flat_root / ".system"),
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
        self.assertFalse(runtime_policy.is_default_visible_skill_name("browser"))
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
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            default_entries, advanced_entries = _discover_advanced_plugin_lanes(
                skill_discovery,
                Path(tmpdir).resolve(),
            )

        self.assertEqual(sorted(entry.name for entry in default_entries), [])
        self.assertEqual(
            sorted(entry.name for entry in advanced_entries),
            ["code-review", "coderabbit"],
        )

    def test_skill_discovery_advanced_includes_local_plugin_cache_skills(self) -> None:
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            _write_local_cache_fixture(repo_root)
            default_entries, advanced_entries = _discover_local_cache_entries(
                skill_discovery,
                repo_root,
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

    def test_skill_discovery_auto_default_includes_first_party_repo_skills(self) -> None:
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            default_entries, advanced_entries = _discover_auto_default_entries(
                skill_discovery,
                Path(tmpdir).resolve(),
            )

        self.assertEqual(sorted(entry.name for entry in default_entries), ["autofix"])
        self.assertEqual(
            sorted(entry.name for entry in advanced_entries),
            ["autofix", "diagram-cli"],
        )

    def test_repo_discovery_uses_tracked_system_skills_without_runtime_bridge(self) -> None:
        """
        Ensure clean CI checkouts keep tracked system skills in repo discovery.

        Local worktrees often have .agents/skills/.system populated, but GitHub
        Actions checks out only tracked sources. Repo-mode discovery must not
        drop system skills when that runtime bridge is absent.
        """
        skill_discovery = load_skill_discovery_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir).resolve()
            write_text(
                repo_root / "skills-system" / "imagegen" / "SKILL.md",
                """
                ---
                name: imagegen
                description: "Generate or edit raster images for project assets."
                ---

                # Imagegen
                """,
            )

            with (
                mock.patch.object(skill_discovery, "REPO_ROOT", repo_root),
                mock.patch.object(skill_discovery, "FLAT_SKILLS_DIR", repo_root / ".agents" / "skills"),
                mock.patch.object(skill_discovery, "SYSTEM_LANE_DIR", repo_root / ".agents" / "skills" / ".system"),
            ):
                entries = skill_discovery.discover_catalog_entries(source="repo")

        self.assertEqual([entry.name for entry in entries], ["imagegen"])
