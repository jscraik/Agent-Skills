#!/usr/bin/env python3
"""Sync and runtime regression tests for lifecycle readiness validation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest import mock

from test_skill_lifecycle_validation_impl import (
    REPO_ROOT,
    SYNC_IMPL_SCRIPT,
    load_codex_preview_module,
    load_skills_impl_module,
    write_text,
)

__test__ = False


def _write_preview_projection_fixture(repo: Path) -> None:
    for name in ("prek-pro", "improve-codebase-architecture"):
        write_text(
            repo / "Skills" / "agent-ops" / name / "SKILL.md",
            f"""
            ---
            name: {name}
            description: Review {name} configuration.
            ---

            # {name}
            """,
        )
    (repo / ".agents" / "skills").mkdir(parents=True)


def _identified_runtime_source() -> dict[str, object]:
    return {
        "schema_version": "codex-runtime-source-identity.v1",
        "source_repo": "openai/codex",
        "source_files": [],
        "modeled_rule_version": "test",
        "status": "identified",
        "revision": "test",
        "relevant_source_dirty": False,
        "unavailable_reason": None,
    }


def _eligible_candidate(candidate_type: type[Any], name: str, path: str, scope_rank: int) -> Any:
    return candidate_type(
        name=name,
        path=path,
        description="canonical candidate",
        scope_rank=scope_rank,
    )

class SkillLifecycleRuntimeValidationTests(unittest.TestCase):
    def test_sync_script_consumes_selection_policy_exports(self) -> None:
        """
        Ensure the sync script references the selection policy and its exported constants required for skill syncing.

        Asserts that Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh contains `selection_policy.py` and the exports:
        `SELECTION_POLICY_REPO_SCAN_ROOTS`, `SELECTION_POLICY_EXCLUDED_SEGMENTS`,
        `SELECTION_POLICY_HIDDEN_FLAT_SKILLS`, `SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS`,
        and `SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS`.
        """
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("selection_policy.py", content)
        self.assertIn("SELECTION_POLICY_REPO_SCAN_ROOTS", content)
        self.assertIn("SELECTION_POLICY_EXCLUDED_SEGMENTS", content)
        self.assertIn("SELECTION_POLICY_HIDDEN_FLAT_SKILLS", content)
        self.assertIn("SELECTION_POLICY_DEFAULT_INCLUDE_FIRST_PARTY_REPO_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS", content)
        self.assertIn("SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS", content)
        self.assertIn("projection_integrity.py", content)

    def test_sync_script_projects_profile_plugin_source_mirrors(self) -> None:
        """
        Verify the sync script mirrors plugin source directories into profile plugin roots so marketplace source paths remain resolvable.

        Asserts that sync_skills.sh invokes sync_home_plugin_mirrors with both the profile plugins root and individual profile plugins paths, ensuring copied marketplace.json entries like ./Plugins/<name> continue to point to valid plugin locations.
        """
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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

    def test_sync_script_relinks_both_home_skill_roots(self) -> None:
        """
        Ensure user sync updates both interoperable and Codex-native home skill roots.

        Codex can read from ~/.agents/skills and ~/.codex/skills. Both must
        point at the same regenerated projection so stale links cannot make
        skills appear in one project/profile but disappear in another.
        """
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('sync_user_skills "$skills_dir" "$HOME/.agents/skills"', content)
        self.assertIn('sync_user_skills "$skills_dir" "$HOME/.codex/skills"', content)

    def test_user_runtime_relink_postcondition_rejects_case_drift(self) -> None:
        """
        User sync must not report success when a home skill root points at a stale casing variant.

        On macOS, a path like agent-skills and Agent-Skills may resolve to the
        same checkout on a case-insensitive volume, but Codex picker state is
        path-string sensitive. The postcondition therefore requires the literal
        symlink target to match the active checkout path, not only a permissive
        filesystem identity.
        """
        skills_impl = load_skills_impl_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            skills_dir = root / "dev" / "agent-skills" / ".agents" / "skills"
            repo_root = skills_dir.parents[1]
            stale_dir = root / "dev" / "Agent-Skills" / ".agents" / "skills"
            skills_dir.mkdir(parents=True)
            (home / ".agents").mkdir(parents=True)
            (home / ".codex").mkdir(parents=True)
            (home / ".agents" / "agent-skills").symlink_to(repo_root)
            (home / ".agents" / "skills").symlink_to(skills_dir)
            (home / ".codex" / "skills").symlink_to(stale_dir)
            plan: dict[str, object] = {}

            errors = skills_impl._verify_user_runtime_relinks(plan, repo_root, home, skills_dir, dry_run=False)

            self.assertEqual(1, len(errors))
            checks = plan["user_runtime_link_checks"]["checks"]
            codex_check = next(check for check in checks if check["label"] == "codex_user_runtime")
            self.assertEqual("fail", codex_check["status"])
            self.assertFalse(codex_check["literal_target_matches"])
            self.assertIn("USER_RUNTIME_LINK", errors[0].message.upper().replace(" ", "_"))

    def test_user_runtime_relink_postcondition_accepts_exact_targets(self) -> None:
        """User sync postcondition passes when both runtime links target the active projection exactly."""
        skills_impl = load_skills_impl_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            home = root / "home"
            skills_dir = root / "dev" / "agent-skills" / ".agents" / "skills"
            repo_root = skills_dir.parents[1]
            skills_dir.mkdir(parents=True)
            (home / ".agents").mkdir(parents=True)
            (home / ".codex").mkdir(parents=True)
            (home / ".agents" / "agent-skills").symlink_to(repo_root)
            (home / ".agents" / "skills").symlink_to(skills_dir)
            (home / ".codex" / "skills").symlink_to(skills_dir)
            plan: dict[str, object] = {}

            errors = skills_impl._verify_user_runtime_relinks(plan, repo_root, home, skills_dir, dry_run=False)

            self.assertEqual([], errors)
            self.assertEqual("pass", plan["user_runtime_link_checks"]["status"])

    def test_codex_load_preview_blocks_missing_first_party_projection(self) -> None:
        module = load_codex_preview_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            _write_preview_projection_fixture(repo)
            with mock.patch.object(module, "_codex_runtime_source_identity") as source_identity:
                source_identity.return_value = _identified_runtime_source()
                preview = module.build_codex_load_preview(repo)

        projection = preview["first_party_projection"]
        blocker_ids = {check["id"] for check in preview["blocked_checks"]}
        missing_names = {skill["name"] for skill in projection["missing_skills"]}
        self.assertEqual("blocked", projection["status"])
        self.assertEqual(2, projection["missing_count"])
        self.assertEqual({"prek-pro", "improve-codebase-architecture"}, missing_names)
        self.assertIn("first_party_runtime_projection", blocker_ids)
        self.assertEqual("partial", preview["status"])

    def test_sync_script_regenerates_versioned_visible_local_cache_roots(self) -> None:
        """
        Ensure sync regenerates versioned visible local cache roots.

        Some Codex builds still inspect
        `plugins/cache/agent-skills-local/<plugin>/<version>/skills`, so sync
        must materialize that cache from the canonical marketplace plugin
        source rather than deleting it as stale.
        """
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
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
        content = SYNC_IMPL_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            '(.name // "agent-skills-local" | tostring | trim) as $default_market',
            content,
        )
        self.assertIn(
            "(.marketplace // $source.marketplace // $default_market | tostring | trim) as $market",
            content,
        )

    def test_exact_handle_sort_prefers_canonical_source_over_runtime_bridge(self) -> None:
        skills_impl = load_skills_impl_module()
        candidate = skills_impl.EligibleCandidate
        bridge_copy = _eligible_candidate(candidate, "plugin-creator", ".agents/skills/plugin-creator", 2)
        plugin_source = _eligible_candidate(
            candidate,
            "plugin-creator",
            "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator",
            skills_impl._scope_rank_for_path(
                REPO_ROOT,
                "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator",
            ),
        )
        global_source = _eligible_candidate(
            candidate,
            "plugin-creator",
            "Skills/plugin-creator",
            skills_impl._scope_rank_for_path(REPO_ROOT, "Skills/plugin-creator"),
        )
        system_source = _eligible_candidate(
            candidate,
            "plugin-creator",
            "skills-system/plugin-creator",
            skills_impl._scope_rank_for_path(REPO_ROOT, "skills-system/plugin-creator"),
        )
        project_source = _eligible_candidate(
            candidate,
            "plugin-creator",
            "Skills/project/plugin-creator",
            skills_impl._scope_rank_for_path(REPO_ROOT, "Skills/project/plugin-creator"),
        )

        self.assertIs(min([bridge_copy, plugin_source], key=skills_impl._exact_handle_sort_key), plugin_source)
        self.assertIs(min([global_source, plugin_source], key=skills_impl._exact_handle_sort_key), plugin_source)
        self.assertIs(min([system_source, plugin_source], key=skills_impl._exact_handle_sort_key), plugin_source)
        self.assertIs(min([system_source, global_source], key=skills_impl._exact_handle_sort_key), global_source)
        self.assertIs(
            min([bridge_copy, plugin_source, global_source, project_source], key=skills_impl._exact_handle_sort_key),
            project_source,
        )

    def test_route_exact_handle_prefers_canonical_plugin_source(self) -> None:
        skills_impl = load_skills_impl_module()

        with mock.patch.object(
            skills_impl,
            "compute_catalog_parity",
            return_value={"drift_detected": False},
        ):
            result = skills_impl.route_skills(REPO_ROOT, "plugin-creator")

        self.assertEqual(result.status, "success")
        selected = result.data["decision"]["selected_candidates"][0]
        self.assertEqual(selected["path"], "Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator")
