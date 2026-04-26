import os
import shutil
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main, mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.append(str(REPO_ROOT / "scripts"))

from ask.commands import plugins as plugins_commands  # noqa: E402
from ask.commands import skills as skills_commands  # noqa: E402


class TestAskSkillsSyncSecurity(TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ask-sync-security-")
        self.repo_root = Path(self.temp_dir) / "repo"
        self.repo_root.mkdir(parents=True)
        (self.repo_root / ".agents" / "skills").mkdir(parents=True)
        self.source_dir = self.repo_root / "Skills" / "agent-ops" / "safe-skill"
        self.source_dir.mkdir(parents=True)
        self.fake_home = Path(self.temp_dir) / "home"
        self.fake_home.mkdir(parents=True)

        (self.source_dir / "SKILL.md").write_text("# Safe Skill\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sync_dir_copy_rejects_symlink_payload(self) -> None:
        secret = Path(self.temp_dir) / "secret.txt"
        secret.write_text("TOPSECRET", encoding="utf-8")
        os.symlink(secret, self.source_dir / "leak.txt")

        with self.assertRaises(ValueError) as ctx:
            skills_commands._sync_dir_copy(self.source_dir, self.fake_home / "dst", dry_run=False)

        self.assertIn("symlink", str(ctx.exception).lower())

    def test_sync_skills_user_scope_writes_codex_and_agents_links(self) -> None:
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue((self.fake_home / ".agents" / "skills").is_symlink())
        self.assertTrue((self.fake_home / ".codex" / "skills").is_symlink())
        self.assertTrue((self.fake_home / ".agents" / "agent-skills").is_symlink())
        self.assertTrue((self.fake_home / ".agents" / "plugins").is_symlink())
        self.assertTrue((self.fake_home / "plugins").is_dir())
        self.assertFalse((self.fake_home / "plugins").is_symlink())
        self.assertEqual(result.data["projection_mode"], "flat")

    def test_sync_skills_user_scope_preserves_existing_agents_plugins_directory(self) -> None:
        user_plugins = self.fake_home / ".agents" / "plugins"
        user_plugins.mkdir(parents=True)
        (user_plugins / "README.md").write_text("user owned\n", encoding="utf-8")

        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue(user_plugins.is_dir())
        self.assertFalse(user_plugins.is_symlink())
        self.assertEqual((user_plugins / "README.md").read_text(encoding="utf-8"), "user owned\n")
        self.assertIn(
            f"Skipped existing non-symlink path: {user_plugins}",
            result.data["logs"],
        )

    def test_sync_skills_user_scope_preserves_existing_plugins_directory(self) -> None:
        user_plugins = self.fake_home / "plugins"
        user_plugins.mkdir()
        (user_plugins / "README.md").write_text("user owned\n", encoding="utf-8")

        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue(user_plugins.is_dir())
        self.assertFalse(user_plugins.is_symlink())
        self.assertTrue((user_plugins / "README.md").is_file())
        self.assertIn(
            f"Ensured plugin mirror directory: {user_plugins}",
            result.data["logs"],
        )

    def test_sync_skills_user_scope_replaces_local_plugin_mirror_copies(self) -> None:
        plugin_source = self.repo_root / "Plugins" / "harness-engineering"
        plugin_source.mkdir(parents=True)
        (plugin_source / ".codex-plugin").mkdir()
        (plugin_source / ".codex-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
        (plugin_source / "skills").mkdir()
        (plugin_source / "skills" / "he-heartbeat").mkdir()
        (plugin_source / "skills" / "he-heartbeat" / "SKILL.md").write_text("fresh\n", encoding="utf-8")
        (self.repo_root / "Plugins" / "marketplace.json").write_text(
            '{"plugins":[{"name":"harness-engineering","source":{"source":"local","path":"./Plugins/harness-engineering"}}]}\n',
            encoding="utf-8",
        )
        stale_target = self.fake_home / "plugins" / "harness-engineering"
        stale_target.mkdir(parents=True)
        (stale_target / "stale.txt").write_text("stale\n", encoding="utf-8")

        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertFalse((stale_target / "stale.txt").exists())
        self.assertEqual((stale_target / "skills" / "he-heartbeat" / "SKILL.md").read_text(encoding="utf-8"), "fresh\n")
        self.assertTrue((stale_target / ".codex-repo-plugin-source").is_file())
        self.assertTrue(
            any("Replaced home plugin mirror" in item for item in result.data["logs"]),
            result.data["logs"],
        )

    def test_local_plugin_runtime_sync_preserves_non_local_plugin_entries(self) -> None:
        plugin_source = self.repo_root / "Plugins" / "harness-engineering"
        plugin_source.mkdir(parents=True)
        (plugin_source / "skills").mkdir()
        (plugin_source / "skills" / "he-heartbeat").mkdir()
        (plugin_source / "skills" / "he-heartbeat" / "SKILL.md").write_text("fresh\n", encoding="utf-8")
        marketplace_path = self.repo_root / "Plugins" / "marketplace.json"
        marketplace_path.write_text(
            '{"plugins":[{"name":"harness-engineering","source":{"source":"local","path":"./Plugins/harness-engineering"}}]}\n',
            encoding="utf-8",
        )
        runtime_root = self.fake_home / ".codex" / "Plugins"
        curated_plugin = runtime_root / "linear"
        curated_plugin.mkdir(parents=True)
        (curated_plugin / "marker.txt").write_text("keep\n", encoding="utf-8")
        stale_local = runtime_root / "harness-engineering"
        stale_local.mkdir()
        (stale_local / "stale.txt").write_text("stale\n", encoding="utf-8")

        report = plugins_commands._sync_one_runtime_root(
            runtime_root=runtime_root,
            repo_root=self.repo_root,
            marketplace_path=marketplace_path,
            marketplace_entries=[{"name": "harness-engineering", "path": "./Plugins/harness-engineering"}],
            dry_run=False,
        )

        self.assertEqual(report["copied_plugins"], ["harness-engineering"])
        self.assertEqual(report["removed_entries"], ["harness-engineering"])
        self.assertTrue((curated_plugin / "marker.txt").is_file())
        self.assertFalse((stale_local / "stale.txt").exists())
        self.assertEqual((stale_local / "skills" / "he-heartbeat" / "SKILL.md").read_text(encoding="utf-8"), "fresh\n")

    def test_sync_skills_user_scope_relinks_managed_runtime_directories(self) -> None:
        managed_skills = self.fake_home / ".agents" / "skills"
        managed_skills.mkdir(parents=True)
        (managed_skills / "stale.md").write_text("stale\n", encoding="utf-8")

        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue(managed_skills.is_symlink())
        self.assertFalse((managed_skills / "stale.md").exists())

    def test_sync_skills_projection_env_reaches_engine(self) -> None:
        with mock.patch.dict(os.environ, {"SYNC_SKILLS_PROJECTION_MODE": "rooted"}):
            result = skills_commands.sync_skills(self.repo_root, scope="workspace", dry_run=True)

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["projection_mode"], "rooted")
        self.assertEqual(result.data["projection"]["mode_source"], "env")
        self.assertEqual(result.data["plan"]["validation_status"], "pass")
        root_count = result.data["plan"]["root_skill_sets"]["root_count"]
        self.assertGreater(root_count, 0)
        self.assertLessEqual(root_count, 10)

    def test_sync_skills_projection_cli_wins_over_env(self) -> None:
        with (
            mock.patch.dict(os.environ, {"SYNC_SKILLS_PROJECTION_MODE": "rooted"}),
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
        ):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=True,
                projection="flat",
            )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["projection_mode"], "flat")
        self.assertEqual(result.data["projection"]["mode_source"], "cli")

    def test_sync_skills_rooted_non_dry_run_writes_generated_surface(self) -> None:
        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["projection_mode"], "rooted")
        self.assertTrue((self.repo_root / ".agents" / "skills" / "agent-ops" / "SKILL.md").is_file())
        self.assertTrue((self.repo_root / ".skillsets" / "agent-ops" / "manifest.jsonl").is_file())
        self.assertTrue((self.repo_root / ".skillsets" / "command-surface.json").is_file())
        self.assertTrue((self.repo_root / ".agents" / "skills" / "he-heartbeat" / "SKILL.md").is_file())
        self.assertTrue((self.repo_root / ".agents" / "skills" / "he-heartbeat" / "agents" / "openai.yaml").is_file())
        self.assertEqual(result.data["plan"]["command_handles"]["status"], "pass")

    def test_sync_skills_rooted_prunes_flat_symlink_before_command_handle_write(self) -> None:
        canonical_skill = self.repo_root / "Skills" / "harness-engineering" / "he-heartbeat"
        canonical_skill.mkdir(parents=True)
        source_skill_md = canonical_skill / "SKILL.md"
        source_skill_md.write_text("# Canonical Source\n", encoding="utf-8")
        runtime_handle = self.repo_root / ".agents" / "skills" / "he-heartbeat"
        runtime_handle.parent.mkdir(parents=True, exist_ok=True)
        runtime_handle.symlink_to(canonical_skill)

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertFalse(runtime_handle.is_symlink())
        self.assertIn("Generated command handle", (runtime_handle / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(source_skill_md.read_text(encoding="utf-8"), "# Canonical Source\n")
        self.assertTrue(
            any("Removed stale symlink" in item and "he-heartbeat" in item for item in result.data["logs"]),
            result.data["logs"],
        )

    def test_sync_skills_rooted_prunes_unowned_skillset_files(self) -> None:
        stale_file = self.repo_root / ".skillsets" / "stale" / "manifest.jsonl"
        stale_file.parent.mkdir(parents=True)
        stale_file.write_text("{}\n", encoding="utf-8")
        command_surface = self.repo_root / ".skillsets" / "command-surface.json"
        command_surface.parent.mkdir(parents=True, exist_ok=True)
        command_surface.write_text("{}\n", encoding="utf-8")

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertFalse(stale_file.exists())
        self.assertTrue(command_surface.exists())
        self.assertTrue(
            any("Removed unowned skill-set file" in item for item in result.data["plan"]["deletes"]),
            result.data["plan"],
        )

    def test_sync_skills_rooted_dry_run_reports_unowned_skillset_files(self) -> None:
        stale_file = self.repo_root / ".skillsets" / "stale" / "manifest.jsonl"
        stale_file.parent.mkdir(parents=True)
        stale_file.write_text("{}\n", encoding="utf-8")

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=True,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertTrue(stale_file.exists())
        self.assertTrue(
            any("Removed unowned skill-set file" in item for item in result.data["plan"]["deletes"]),
            result.data["plan"],
        )

    def test_sync_skills_rooted_reports_skillset_prune_failures(self) -> None:
        with mock.patch.object(
            skills_commands,
            "prune_unowned_skillset_files",
            side_effect=OSError("permission denied"),
        ):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                projection="rooted",
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        self.assertIn("permission denied", result.errors[0].message)
        self.assertIn("ROOTED_PROJECTION_WRITE_FAILED", result.data["plan"]["warnings"])

    def test_sync_skills_rooted_user_scope_validates_workspace_before_relink(self) -> None:
        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                projection="rooted",
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("ROOTED_WORKSPACE", result.data["plan"]["warnings"][0])
        self.assertFalse((self.fake_home / ".agents" / "skills").exists())

    def test_sync_skills_rooted_user_scope_relinks_after_workspace_validation(self) -> None:
        workspace_result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )
        self.assertEqual(workspace_result.status, "success")

        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                projection="rooted",
            )

        self.assertEqual(result.status, "success")
        self.assertTrue((self.fake_home / ".agents" / "skills").is_symlink())
        self.assertTrue((self.fake_home / ".codex" / "skills").is_symlink())
        self.assertTrue((self.fake_home / ".agents" / "agent-skills").is_symlink())
        self.assertTrue((self.fake_home / ".agents" / "plugins").is_symlink())
        self.assertTrue((self.fake_home / "plugins").is_dir())
        self.assertFalse((self.fake_home / "plugins").is_symlink())
        self.assertEqual(result.data["projection_mode"], "rooted")

    def test_sync_skills_rooted_prunes_first_level_system_bridge_aliases(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        bridge_skill_dir = system_skills_dir / "imagegen"
        bridge_skill_dir.mkdir(parents=True)
        (bridge_skill_dir / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        bridge_link = skills_dir / "imagegen"
        bridge_link.symlink_to(Path(".system/imagegen"))

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=True,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertTrue(
            any("imagegen" in delete for delete in result.data["plan"]["deletes"]),
            "rooted projection should prune first-level system bridge aliases",
        )
        self.assertIn("imagegen", result.data["plan"]["system_bridge_skill_names"])
        self.assertNotIn("imagegen", result.data["plan"]["preserved_bridge_lane_entries"])

    def test_sync_skills_projection_does_not_mask_invalid_scope(self) -> None:
        result = skills_commands.sync_skills(
            self.repo_root,
            scope="unknown",
            dry_run=True,
            projection="rooted",
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_INVALID_SCOPE")

    def test_sync_skills_workspace_prunes_stale_symlinks_only(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        valid_source = self.repo_root / "Skills" / "agent-ops" / "valid-skill"
        valid_source.mkdir(parents=True)
        (valid_source / "SKILL.md").write_text("# Valid Skill\n", encoding="utf-8")
        real_dir = skills_dir / "manual-skill"
        real_dir.mkdir()
        stale = skills_dir / "stale-skill"
        stale.symlink_to(Path("../../Skills/missing/stale-skill"))

        fake_entry = SimpleNamespace(
            name="valid-skill",
            source_dir=valid_source,
            category="Skills/agent-ops",
            description="Valid skill.",
        )
        with mock.patch.object(skills_commands, "discover_skill_entries", return_value=[fake_entry]):
            result = skills_commands.sync_skills(self.repo_root, scope="workspace", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertFalse(stale.exists())
        self.assertFalse(stale.is_symlink())
        self.assertTrue(real_dir.is_dir())
        self.assertTrue((skills_dir / "valid-skill").is_symlink())

    def test_sync_skills_workspace_preserves_reserved_system_lane_symlink(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        system_skills_dir.mkdir()
        (system_skills_dir / "skill-creator").mkdir()
        (system_skills_dir / "skill-creator" / "SKILL.md").write_text("# Skill Creator\n", encoding="utf-8")
        system_link = skills_dir / ".system"
        system_link.symlink_to(Path("../../skills-system"))

        valid_source = self.repo_root / "Skills" / "agent-ops" / "valid-skill"
        valid_source.mkdir(parents=True)
        (valid_source / "SKILL.md").write_text("# Valid Skill\n", encoding="utf-8")

        fake_entry = SimpleNamespace(
            name="valid-skill",
            source_dir=valid_source,
            category="Skills/agent-ops",
            description="Valid skill.",
        )
        with mock.patch.object(skills_commands, "discover_skill_entries", return_value=[fake_entry]):
            result = skills_commands.sync_skills(self.repo_root, scope="workspace", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue(system_link.is_symlink())
        self.assertEqual(os.readlink(system_link), "../../skills-system")

    def test_sync_skills_user_scope_does_not_write_repo_local_lowercase_skills(self) -> None:
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue((self.fake_home / ".codex" / "skills").is_symlink())

    def test_sync_skills_workspace_refreshes_catalog_projections(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        readme_path = self.repo_root / "README.md"
        skill_index_path = self.repo_root / "SKILL.md"
        readme_path.write_text(
            "# Agent Skills\n\nA governed repository of **120 canonical skills** for AI coding agents.\n",
            encoding="utf-8",
        )
        skill_index_path.write_text(
            "# Agent Skills Index\n\n## Summary\n- `total_skills`: 120\n- `policy_identity`: stale\n",
            encoding="utf-8",
        )
        valid_source = self.repo_root / "Skills" / "agent-ops" / "valid-skill"
        valid_source.mkdir(parents=True)
        (valid_source / "SKILL.md").write_text(
            "---\nname: valid-skill\ndescription: Valid skill description.\n---\n",
            encoding="utf-8",
        )

        fake_entry = SimpleNamespace(
            name="valid-skill",
            source_dir=valid_source,
            category="Skills/agent-ops",
            description="Valid skill description.",
        )
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[fake_entry]),
            mock.patch.object(skills_commands, "discover_catalog_entries", return_value=[fake_entry]),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="workspace", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue((skills_dir / "valid-skill").is_symlink())
        self.assertIn("**1 skills**", readme_path.read_text(encoding="utf-8"))
        self.assertIn("`total_skills`: 1", skill_index_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
