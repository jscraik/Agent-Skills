import json
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
from ask.envelope import ErrorObject  # noqa: E402
from ask.services import plugin_cache  # noqa: E402

sys.path.append(str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))
from check_context_budget import DEFAULTS  # noqa: E402


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

    def test_local_plugin_runtime_sync_prunes_stale_marked_plugins(self) -> None:
        plugin_a = self.repo_root / "Plugins" / "plugin-a"
        plugin_a.mkdir(parents=True)
        (plugin_a / "SKILL.md").write_text("plugin-a\n", encoding="utf-8")
        plugin_b = self.repo_root / "Plugins" / "plugin-b"
        plugin_b.mkdir(parents=True)
        (plugin_b / "SKILL.md").write_text("plugin-b\n", encoding="utf-8")
        marketplace_path = self.repo_root / "Plugins" / "marketplace.json"
        marketplace_path.write_text(
            '{"plugins":['
            '{"name":"plugin-a","source":{"source":"local","path":"./Plugins/plugin-a"}},'
            '{"name":"plugin-b","source":{"source":"local","path":"./Plugins/plugin-b"}}'
            ']}\n',
            encoding="utf-8",
        )
        runtime_root = self.fake_home / ".codex" / "Plugins"

        # Initial sync with both plugins
        plugins_commands._sync_one_runtime_root(
            runtime_root=runtime_root,
            repo_root=self.repo_root,
            marketplace_path=marketplace_path,
            marketplace_entries=[
                {"name": "plugin-a", "path": "./Plugins/plugin-a"},
                {"name": "plugin-b", "path": "./Plugins/plugin-b"},
            ],
            dry_run=False,
        )
        self.assertTrue((runtime_root / "plugin-a" / "SKILL.md").is_file())
        self.assertTrue((runtime_root / "plugin-b" / "SKILL.md").is_file())

        # Update marketplace to remove plugin-b
        marketplace_path.write_text(
            '{"plugins":['
            '{"name":"plugin-a","source":{"source":"local","path":"./Plugins/plugin-a"}}'
            ']}\n',
            encoding="utf-8",
        )
        report = plugins_commands._sync_one_runtime_root(
            runtime_root=runtime_root,
            repo_root=self.repo_root,
            marketplace_path=marketplace_path,
            marketplace_entries=[{"name": "plugin-a", "path": "./Plugins/plugin-a"}],
            dry_run=False,
        )

        self.assertEqual(report["planned_plugins"], ["plugin-a"])
        self.assertEqual(report["pruned_plugins"], ["plugin-b"])
        self.assertTrue((runtime_root / "plugin-a" / "SKILL.md").is_file())
        self.assertFalse((runtime_root / "plugin-b").exists())

    def test_local_plugin_runtime_sync_dry_run_does_not_prune_stale_plugins(self) -> None:
        plugin_source = self.repo_root / "Plugins" / "plugin-a"
        plugin_source.mkdir(parents=True)
        (plugin_source / "SKILL.md").write_text("plugin-a\n", encoding="utf-8")
        marketplace_path = self.repo_root / "Plugins" / "marketplace.json"
        marketplace_path.write_text(
            '{"plugins":['
            '{"name":"plugin-a","source":{"source":"local","path":"./Plugins/plugin-a"}}'
            ']}\n',
            encoding="utf-8",
        )
        runtime_root = self.fake_home / ".codex" / "Plugins"
        stale_plugin = runtime_root / "plugin-b"
        stale_plugin.mkdir(parents=True)
        (stale_plugin / ".codex-repo-plugin-source").write_text("/old/path\n", encoding="utf-8")
        (stale_plugin / "SKILL.md").write_text("stale\n", encoding="utf-8")

        report = plugins_commands._sync_one_runtime_root(
            runtime_root=runtime_root,
            repo_root=self.repo_root,
            marketplace_path=marketplace_path,
            marketplace_entries=[{"name": "plugin-a", "path": "./Plugins/plugin-a"}],
            dry_run=True,
        )

        self.assertEqual(report["planned_plugins"], ["plugin-a"])
        self.assertEqual(report["pruned_plugins"], ["plugin-b"])
        self.assertTrue((stale_plugin / "SKILL.md").is_file())

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
        self.assertLessEqual(root_count, DEFAULTS["runtime_projection"]["max_root_skill_sets"])

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
        he_source = self.repo_root / "Skills" / "harness-engineering" / "he-heartbeat"
        he_source.mkdir(parents=True)
        (he_source / "SKILL.md").write_text("# HE Heartbeat\n", encoding="utf-8")

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
        self.assertIn(
            "Internal activation entrypoint",
            (runtime_handle / "SKILL.md").read_text(encoding="utf-8"),
        )
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

    def test_sync_skills_rooted_user_scope_allows_generated_folded_handles(self) -> None:
        brainstorm_source = self.repo_root / "Plugins" / "harness-engineering" / "skills" / "he-brainstorm"
        brainstorm_source.mkdir(parents=True)
        (brainstorm_source / "SKILL.md").write_text(
            "---\nname: he-brainstorm\n---\n# HE Brainstorm\n",
            encoding="utf-8",
        )

        workspace_result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )
        self.assertEqual(workspace_result.status, "success")

        folded_handle = self.repo_root / ".agents" / "skills" / "he-ideate" / "SKILL.md"
        self.assertTrue(folded_handle.is_file())

        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                projection="rooted",
            )

        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["projection_mode"], "rooted")
        self.assertTrue((self.fake_home / ".agents" / "skills").is_symlink())
        self.assertNotIn("ROOTED_WORKSPACE_MIXED_PROJECTION", result.data["plan"]["warnings"])

    def test_sync_skills_rooted_prunes_first_level_system_bridge_aliases(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        bridge_skill_dir = system_skills_dir / "imagegen"
        bridge_skill_dir.mkdir(parents=True)
        (bridge_skill_dir / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        (skills_dir / ".system").symlink_to(Path("../../skills-system"))
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

    def test_sync_skills_rooted_prunes_first_level_system_bridge_directories(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        bridge_skill_dir = system_skills_dir / "imagegen"
        bridge_skill_dir.mkdir(parents=True)
        (bridge_skill_dir / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        stale_first_level_bridge = skills_dir / "imagegen"
        stale_first_level_bridge.mkdir()
        (stale_first_level_bridge / "SKILL.md").write_text("# Stale Imagegen\n", encoding="utf-8")
        (stale_first_level_bridge / ".agent-skills-system-bridge-alias.json").write_text(
            json.dumps({"kind": "system_bridge_alias", "target": "imagegen"}),
            encoding="utf-8",
        )

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertFalse(
            stale_first_level_bridge.exists(),
            "rooted projection should prune real first-level system bridge directories",
        )
        self.assertTrue((skills_dir / ".system").exists())
        self.assertTrue(
            any(
                "Removed first-level system bridge alias" in item and "imagegen" in item
                for item in result.data["logs"]
            ),
            result.data["logs"],
        )

    def test_sync_skills_rooted_prunes_first_level_system_bridge_files(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        bridge_skill_dir = system_skills_dir / "imagegen"
        bridge_skill_dir.mkdir(parents=True)
        (bridge_skill_dir / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        stale_first_level_bridge = skills_dir / "imagegen"
        stale_first_level_bridge.write_text("# Stale Imagegen\n", encoding="utf-8")
        (skills_dir / ".imagegen-.agent-skills-system-bridge-alias.json").write_text(
            json.dumps({"kind": "system_bridge_alias", "target": "imagegen"}),
            encoding="utf-8",
        )

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertFalse(
            stale_first_level_bridge.exists(),
            "rooted projection should prune file-shaped first-level system bridge aliases",
        )
        self.assertTrue((skills_dir / ".system").exists())
        self.assertTrue(
            any(
                "Removed first-level system bridge alias" in item and "imagegen" in item
                for item in result.data["logs"]
            ),
            result.data["logs"],
        )

    def test_sync_skills_rooted_preserves_unmarked_first_level_system_bridge_directory(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_skills_dir = self.repo_root / "skills-system"
        bridge_skill_dir = system_skills_dir / "imagegen"
        bridge_skill_dir.mkdir(parents=True)
        (bridge_skill_dir / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        user_owned_bridge = skills_dir / "imagegen"
        user_owned_bridge.mkdir()
        (user_owned_bridge / "SKILL.md").write_text("# User-owned Imagegen\n", encoding="utf-8")

        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=False,
            projection="rooted",
        )

        self.assertEqual(result.status, "success")
        self.assertTrue(user_owned_bridge.exists())
        self.assertTrue(
            any(
                "Skipped first-level system bridge alias without generated provenance" in item
                and "imagegen" in item
                for item in result.data["logs"]
            ),
            result.data["logs"],
        )

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

    def test_sync_skills_workspace_skips_system_bridge_entries_from_flat_projection(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        generated_handle = skills_dir / "imagegen"
        generated_handle.mkdir()
        (generated_handle / "SKILL.md").write_text("# Generated Imagegen Handle\n", encoding="utf-8")

        system_source = self.repo_root / "skills-system" / "imagegen"
        system_source.mkdir(parents=True)
        (system_source / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")

        fake_entry = SimpleNamespace(
            name="imagegen",
            source_dir=system_source,
            category="skills-system",
            description="Generate images.",
        )
        with mock.patch("ask.commands.skills_impl.discover_skill_entries", return_value=[fake_entry]):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                projection="flat",
            )

        self.assertEqual(result.status, "success")
        self.assertTrue(generated_handle.is_dir())
        self.assertFalse(generated_handle.is_symlink())
        self.assertEqual(
            (generated_handle / "SKILL.md").read_text(encoding="utf-8"),
            "# Generated Imagegen Handle\n",
        )
        self.assertIn(
            "Skipped hidden system bridge from flat projection: imagegen",
            result.data["logs"],
        )

    def test_sync_skills_workspace_prunes_first_level_system_bridge_symlinks(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        system_source = self.repo_root / "skills-system" / "imagegen"
        system_source.mkdir(parents=True)
        (system_source / "SKILL.md").write_text("# Imagegen\n", encoding="utf-8")
        (skills_dir / ".system").symlink_to(Path("../../skills-system"))
        bridge_link = skills_dir / "imagegen"
        bridge_link.symlink_to(Path("../../skills-system/imagegen"))

        fake_entry = SimpleNamespace(
            name="imagegen",
            source_dir=system_source,
            category="skills-system",
            description="Generate images.",
        )
        with mock.patch("ask.commands.skills_impl.discover_skill_entries", return_value=[fake_entry]):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                projection="flat",
            )

        self.assertEqual(result.status, "success")
        self.assertFalse(bridge_link.exists())
        self.assertTrue((skills_dir / ".system").is_symlink())
        self.assertTrue(
            any("Removed first-level system bridge alias" in item and "imagegen" in item for item in result.data["logs"]),
            result.data["logs"],
        )

    def test_create_symlink_preserves_current_target_without_unlinking(self) -> None:
        target = self.repo_root / ".agents" / "skills" / ".system"
        target.symlink_to(Path("../../skills-system"))

        with mock.patch.object(Path, "unlink", side_effect=AssertionError("should not unlink current symlink")):
            result = skills_commands._create_symlink(Path("../../skills-system"), target)

        self.assertEqual(result, f"Symlink already current: {target} -> ../../skills-system")
        self.assertTrue(target.is_symlink())
        self.assertEqual(os.readlink(target), "../../skills-system")

    def test_plugin_cache_refresh_preserves_existing_directory_root(self) -> None:
        source = self.repo_root / "Plugins" / "harness-engineering"
        source.mkdir(parents=True)
        (source / "README.md").write_text("fresh\n", encoding="utf-8")
        target = self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / "harness-engineering"
        target.mkdir(parents=True)
        (target / "README.md").write_text("stale\n", encoding="utf-8")

        with mock.patch.object(plugin_cache.shutil, "rmtree", side_effect=AssertionError("should not remove cache root")):
            report = plugin_cache.replace_plugin_cache_copy(self.repo_root, "harness-engineering", source, target)

        self.assertEqual((target / "README.md").read_text(encoding="utf-8"), "fresh\n")
        self.assertIn(str(target / "README.md"), report.deletes)

    def test_plugin_cache_prune_keeps_skill_when_command_handle_file_is_missing(self) -> None:
        plugin_root = self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / "harness-engineering"
        skill_dir = plugin_root / "skills" / "he-work"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# HE Work\n", encoding="utf-8")

        with mock.patch.object(
            plugin_cache,
            "handles_report",
            return_value={
                "handles": [
                    {
                        "owner": "harness-engineering",
                        "handle": "he-work",
                        "command_handle_path": ".agents/skills/he-work/SKILL.md",
                    }
                ]
            },
        ):
            logs, deletes = plugin_cache.prune_command_handle_skill_entries(
                self.repo_root,
                "harness-engineering",
                plugin_root,
            )

        self.assertEqual([], logs)
        self.assertEqual([], deletes)
        self.assertTrue((skill_dir / "SKILL.md").exists())

    def test_plugin_cache_prune_removes_skill_when_command_handle_file_exists(self) -> None:
        plugin_root = self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / "harness-engineering"
        skill_dir = plugin_root / "skills" / "he-work"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# HE Work\n", encoding="utf-8")
        command_handle = self.repo_root / ".agents" / "skills" / "he-work" / "SKILL.md"
        command_handle.parent.mkdir(parents=True, exist_ok=True)
        command_handle.write_text("# Generated HE Work Handle\n", encoding="utf-8")

        with mock.patch.object(
            plugin_cache,
            "handles_report",
            return_value={
                "handles": [
                    {
                        "owner": "harness-engineering",
                        "handle": "he-work",
                        "command_handle_path": ".agents/skills/he-work/SKILL.md",
                    }
                ]
            },
        ):
            logs, deletes = plugin_cache.prune_command_handle_skill_entries(
                self.repo_root,
                "harness-engineering",
                plugin_root,
            )

        self.assertTrue(any("he-work" in log for log in logs))
        self.assertEqual([str(skill_dir)], deletes)
        self.assertFalse(skill_dir.exists())

    def test_plugin_cache_prune_removes_internal_skill_category_dirs(self) -> None:
        plugin_root = self.repo_root / ".agents" / "plugins-runtime" / "cache" / "agent-skills-local" / "skill-factory"
        skill_builder = plugin_root / "skills" / "skill-builder"
        archived_skill_builder = plugin_root / "fixtures" / "budget-archive" / "skills" / "skill-builder"
        internal_skill_builder = plugin_root / "skills" / "code_quality_review" / "skill-builder"
        internal_skill_refactor = plugin_root / "skills" / "data_fetch_analysis" / "skill-refactor"
        skill_builder.mkdir(parents=True)
        archived_skill_builder.mkdir(parents=True)
        internal_skill_builder.mkdir(parents=True)
        internal_skill_refactor.mkdir(parents=True)
        (skill_builder / "SKILL.md").write_text("# Skill Builder\n", encoding="utf-8")
        (archived_skill_builder / "SKILL.md").write_text("# Archived Skill Builder\n", encoding="utf-8")
        (internal_skill_builder / "SKILL.md").write_text("# Internal Skill Builder\n", encoding="utf-8")
        (internal_skill_refactor / "SKILL.md").write_text("# Internal Skill Refactor\n", encoding="utf-8")

        logs, deletes = plugin_cache.prune_picker_internal_skill_dirs(plugin_root)

        self.assertTrue((skill_builder / "SKILL.md").exists())
        self.assertFalse(archived_skill_builder.exists())
        self.assertFalse(internal_skill_builder.exists())
        self.assertFalse(internal_skill_refactor.exists())
        self.assertIn(str(plugin_root / "fixtures"), deletes)
        self.assertIn(str(plugin_root / "skills" / "code_quality_review"), deletes)
        self.assertIn(str(plugin_root / "skills" / "data_fetch_analysis"), deletes)
        self.assertTrue(any("picker-internal" in log for log in logs))

    def test_plugin_cache_permission_failure_returns_error(self) -> None:
        marketplace = self.repo_root / "Plugins" / "marketplace.json"
        marketplace.parent.mkdir(parents=True)
        marketplace.write_text(
            '{"name":"agent-skills-local","plugins":[{"name":"harness-engineering","source":{"source":"local","path":"./Plugins/harness-engineering"}}]}',
            encoding="utf-8",
        )
        source = self.repo_root / "Plugins" / "harness-engineering"
        source.mkdir(parents=True)

        plan: dict[str, list[str]] = {}
        logs: list[str] = []
        with mock.patch.object(plugin_cache, "copy_directory_contents", side_effect=PermissionError("blocked")):
            error = plugin_cache.refresh_workspace_plugin_caches(plan, logs, self.repo_root, dry_run=False)

        self.assertIsNotNone(error)
        self.assertEqual(error.code, "ERR_RUNTIME")
        self.assertIn("blocked by permissions", error.message)
        self.assertIn("PLUGIN_CACHE_REFRESH_PERMISSION_BLOCKED", plan["warnings"])
        self.assertEqual(plan["plugin_cache_refresh"]["status"], "blocked")
        self.assertTrue(any("Skipped workspace plugin cache refresh after permission failure" in log for log in logs))
        self.assertTrue(any("rerun with write access to .agents/plugins-runtime/cache." in log for log in logs))

    def test_sync_skills_can_skip_plugin_runtime_cache_refresh(self) -> None:
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(skills_commands, "discover_catalog_entries", return_value=[]),
            mock.patch.object(skills_commands, "refresh_workspace_plugin_caches", side_effect=AssertionError("should not refresh cache")),
        ):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                plugin_cache_refresh="skip",
            )

        self.assertEqual(result.status, "success")
        plan = result.data["plan"]
        self.assertEqual(plan["plugin_cache_refresh"]["mode"], "skip")
        self.assertEqual(plan["plugin_cache_refresh"]["status"], "skipped")
        self.assertTrue(any("rerun with write access to .agents/plugins-runtime/cache." in log for log in result.data["logs"]))

    def test_sync_skills_can_refresh_plugin_runtime_cache_only(self) -> None:
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", side_effect=AssertionError("should not sync skills")),
            mock.patch.object(skills_commands, "refresh_workspace_plugin_caches") as refresh_mock,
        ):
            refresh_mock.side_effect = lambda plan, logs, repo_root, dry_run: (
                plan["plugin_cache_refresh"].__setitem__("status", "refreshed")
                or logs.append("cache only refresh")
                or None
            )
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                plugin_cache_refresh="only",
            )

        self.assertEqual(result.status, "success")
        refresh_mock.assert_called_once()
        plan = result.data["plan"]
        self.assertEqual(plan["validation_status"], "pass")
        self.assertEqual(plan["plugin_cache_refresh"]["mode"], "only")
        self.assertEqual(plan["plugin_cache_refresh"]["status"], "refreshed")
        self.assertIn("cache only refresh", result.data["logs"])

    def test_sync_skills_plugin_cache_refresh_only_fails_on_permission_denial(self) -> None:
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", side_effect=AssertionError("should not sync skills")),
            mock.patch.object(skills_commands, "refresh_workspace_plugin_caches") as refresh_mock,
        ):
            refresh_mock.return_value = ErrorObject(
                code="ERR_RUNTIME",
                message="Workspace plugin cache refresh blocked by permissions: blocked",
                fix_suggestion="rerun with write access",
            )
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                plugin_cache_refresh="only",
            )

        self.assertEqual(result.status, "error")
        refresh_mock.assert_called_once()
        self.assertEqual(len(result.errors), 1)
        self.assertEqual(result.errors[0].code, "ERR_RUNTIME")
        plan = result.data["plan"]
        self.assertEqual(plan["plugin_cache_refresh"]["mode"], "only")
        self.assertEqual(plan["validation_status"], "not_run")

    def test_sync_skills_rejects_invalid_plugin_cache_refresh_mode(self) -> None:
        result = skills_commands.sync_skills(
            self.repo_root,
            scope="workspace",
            dry_run=True,
            plugin_cache_refresh="sometimes",
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")

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
            "# Agent Skills\n\nA governed repository of AI coding skills. Built around ask.\n",
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

    def test_sync_skills_rooted_workspace_refreshes_catalog_projections(self) -> None:
        readme_path = self.repo_root / "README.md"
        skill_index_path = self.repo_root / "SKILL.md"
        readme_path.write_text(
            "# Agent Skills\n\nA governed repository of AI coding skills. Built around ask.\n",
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
        with mock.patch.object(skills_commands, "discover_catalog_entries", return_value=[fake_entry]):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="workspace",
                dry_run=False,
                projection="rooted",
            )

        self.assertEqual(result.status, "success")
        self.assertIn("**1 skills**", readme_path.read_text(encoding="utf-8"))
        self.assertIn("`total_skills`: 1", skill_index_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
