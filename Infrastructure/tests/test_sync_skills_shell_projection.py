import os
import subprocess
import unittest
from pathlib import Path
from typing import Optional


SYNC_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh"
SYNC_IMPL_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh"
PATH_IDENTITY_SCRIPT = "Infrastructure/scripts/lifecycle-and-sync/path_identity.py"


def _read_sync_impl() -> str:
    with open(SYNC_IMPL_SCRIPT, encoding="utf-8") as script_file:
        return script_file.read()


def _run_sync_script(args: list[str], *, env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env or {})
    return subprocess.run(
        ["bash", SYNC_SCRIPT, *args],
        capture_output=True,
        text=True,
        timeout=30,
        env=merged_env,
        check=False,
    )


class TestSyncSkillsShellProjection(unittest.TestCase):
    def test_shell_entrypoint_delegates_runtime_mutation_to_ask_engine(self) -> None:
        script = _read_sync_impl()

        self.assertIn("ask_sync_args=(skills sync", script)
        self.assertIn('[[ "$dry_run" == "1" || "${SYNC_SKILLS_RESOLVED_PROJECTION_MODE:-flat}" != "flat" || "$plugin_cache_refresh" != "auto" ]]', script)
        self.assertIn('ask_sync_args+=(--plugin-cache-refresh "$plugin_cache_refresh")', script)
        self.assertIn("start_watchdog", script)
        self.assertIn("exit 124", script)

    def test_shell_entrypoint_keeps_flat_legacy_path_reachable(self) -> None:
        script = _read_sync_impl()

        delegated_block = script.split("ask_sync_args=(skills sync", 1)[0]
        self.assertNotIn('"$sync_scope" == "user"', delegated_block)
        self.assertNotIn('"$sync_scope" == "workspace"', delegated_block)

    def test_flat_sync_prunes_stale_plugin_owned_entries(self) -> None:
        script = _read_sync_impl()

        self.assertIn("Removed stale plugin-owned flat skill", script)
        self.assertIn('rm -rf -- "${skills_dir:?}/${skill_name:?}"', script)
        self.assertLess(
            script.index("Removed stale plugin-owned flat skill"),
            script.index("Skipping plugin-owned skill from flat projection"),
        )

    def test_rooted_projection_delegates_to_ask_engine_in_dry_run(self) -> None:
        result = _run_sync_script(["--workspace", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)
        self.assertIn("Dry-run rooted projection", result.stdout)

    def test_project_local_is_legacy_workspace_alias(self) -> None:
        result = _run_sync_script(["--project-local", "--projection", "rooted", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("rooted", result.stdout)

    def test_invalid_scope_fails_before_projection_policy(self) -> None:
        result = _run_sync_script(["--projection", "rooted"], env={"SYNC_SKILLS_SCOPE": "elsewhere"})

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid sync scope: elsewhere", result.stderr)
        self.assertNotIn("Projection mode 'rooted' is parsed", result.stderr)

    def test_user_scope_reaches_legacy_shell_path(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_home:
            result = _run_sync_script(
                ["--user", "--dry-run"],
                env={"HOME": tmp_home},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("user", result.stdout.lower())

    def test_plugin_cache_only_delegates_to_ask_engine(self) -> None:
        result = _run_sync_script(["--workspace", "--plugin-cache-refresh", "only", "--dry-run"])

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("plugin runtime cache refresh only", result.stdout)
        self.assertIn(".agents/plugins-runtime/cache", result.stdout)

    def test_user_plugin_mirror_repairs_symlinks_before_copying(self) -> None:
        script = _read_sync_impl()

        self.assertIn(
            'rm -f -- "$target_dir" || echo "[WARN] Could not replace symlink target',
            script,
        )
        self.assertIn('profile*|home\\ plugin\\ root)', script)
        self.assertIn('echo "[OK] Replaced symlinked $label with directory: $target_dir"', script)
        self.assertIn(
            'path_identity.py" is-same-or-child "$canonical_plugins_real" "$link_target_real"',
            script,
        )
        self.assertNotIn("python3 - \"$canonical_plugins_real\" \"$link_target_real\"", script)
        self.assertIn(
            'echo "[OK] Replaced repo-backed symlinked $label with directory: $target_dir"',
            script,
        )

    def test_path_identity_helper_detects_same_child_and_unrelated_paths(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "root"
            child = root / "child"
            sibling = Path(tmp_dir) / "sibling"
            child.mkdir(parents=True)
            sibling.mkdir()

            same = subprocess.run(
                ["python3", PATH_IDENTITY_SCRIPT, "is-same-or-child", str(root), str(root)],
                check=False,
            )
            nested = subprocess.run(
                ["python3", PATH_IDENTITY_SCRIPT, "is-same-or-child", str(root), str(child)],
                check=False,
            )
            unrelated = subprocess.run(
                [
                    "python3",
                    PATH_IDENTITY_SCRIPT,
                    "is-same-or-child",
                    str(root),
                    str(sibling),
                ],
                check=False,
            )

        self.assertEqual(0, same.returncode)
        self.assertEqual(0, nested.returncode)
        self.assertEqual(1, unrelated.returncode)

    def test_versioned_cache_replaces_existing_version_before_rsync(self) -> None:
        script = _read_sync_impl()

        versioned_sync = script.split("sync_versioned_local_marketplace_cache()", 1)[1]
        setup_block = versioned_sync.split('rsync -a --delete --force \\', 1)[0]
        self.assertIn('if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then', setup_block)
        self.assertIn('rm -rf -- "$target_dir"', setup_block)
        self.assertIn('mkdir -p "$target_dir"', setup_block)

    def test_unwritable_profile_plugin_mirrors_are_skipped(self) -> None:
        script = _read_sync_impl()

        profile_sync = script.split("sync_codex_profile_homes()", 1)[1]
        self.assertIn('if ensure_real_home_plugin_root "$profile_plugins" "$plugins_dir" "profile plugin root"; then', profile_sync)
        self.assertIn('if ensure_real_home_plugin_root "$profile_plugins_root" "$plugins_dir" "profile Plugins root"; then', profile_sync)
        self.assertIn('if ensure_real_home_plugin_root "$profile_agents_plugins" "$plugins_dir" "profile .agents plugin root"; then', profile_sync)
        self.assertIn(
            'skip_unwritable_sync_phase "profile plugin mirror publication" "$profile_plugins"',
            profile_sync,
        )
        self.assertIn(
            'skip_unwritable_sync_phase "profile Plugins mirror publication" "$profile_plugins_root"',
            profile_sync,
        )
        self.assertIn('if [ "$profile_agents_plugins_ready" = "1" ] && can_mutate_sync_dir "$profile_agents_plugins"; then', profile_sync)
        self.assertIn('sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"', profile_sync)
        self.assertIn(
            'skip_unwritable_sync_phase "profile .agents plugin mirror publication" "$profile_agents_plugins"',
            profile_sync,
        )

    def test_profile_plugin_mirrors_refresh_when_runtime_cache_is_stale(self) -> None:
        script = _read_sync_impl()

        stale_cache_branch = script.split(
            'echo "[INFO] Skipping profile marketplace publication because runtime cache rebuild was not fresh."',
            1,
        )[1].split('elif [ -f "$marketplace_file" ]; then', 1)[0]
        self.assertIn('sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins_root"', stale_cache_branch)
        self.assertIn('prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins_root"', stale_cache_branch)
        self.assertIn('sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"', stale_cache_branch)
        self.assertIn('prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins"', stale_cache_branch)
        self.assertIn('sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"', stale_cache_branch)
        self.assertIn('prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_agents_plugins"', stale_cache_branch)

    def test_shell_profile_plugin_prune_uses_command_surface_handles(self) -> None:
        script = _read_sync_impl()

        prune_function = script.split("prune_profile_command_handle_plugin_skills() {", 1)[1].split(
            "# Keep repo-local plugin caches aligned",
            1,
        )[0]
        self.assertIn('command_surface_file="$repo_root/.skillsets/command-surface.json"', prune_function)
        self.assertIn('jq -r --arg plugin_name "$plugin_name"', prune_function)
        self.assertIn('((.handles // []) + (.hidden_handles // []))[]', prune_function)
        self.assertIn('startswith(".agents/skills/")', prune_function)
        self.assertIn('rm -rf -- "$target_dir"', prune_function)

    def test_shell_preserves_only_generated_command_handle_dirs(self) -> None:
        script = _read_sync_impl()

        self.assertIn("is_generated_command_handle_dir() {", script)
        self.assertIn("Internal activation entrypoint for a child skill under", script)
        self.assertIn("Removed stale plugin-owned runtime entry before regenerating command handle", script)
        preserve_block = script.split('if is_generated_command_handle_name "$skill_name"; then', 1)[1].split(
            'if [ -e "$skills_dir/$skill_name" ] || [ -L "$skills_dir/$skill_name" ]; then',
            1,
        )[0]
        self.assertIn('if is_generated_command_handle_dir "$skill_name"; then', preserve_block)
        self.assertIn("continue", preserve_block)

    def test_invalid_plugin_cache_refresh_mode_fails(self) -> None:
        result = _run_sync_script(["--workspace", "--plugin-cache-refresh", "sometimes", "--dry-run"])

        self.assertEqual(result.returncode, 2)
        self.assertIn("Invalid --plugin-cache-refresh value: sometimes", result.stderr)


if __name__ == "__main__":
    unittest.main()
