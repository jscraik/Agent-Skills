import shutil
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.commands import skills as skills_commands  # noqa: E402


class TestAskSkillsSyncUserRuntime(TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ask-sync-user-runtime-")
        self.repo_root = Path(self.temp_dir) / "repo"
        (self.repo_root / ".agents" / "skills").mkdir(parents=True)
        (self.repo_root / "Skills" / "agent-ops" / "safe-skill").mkdir(parents=True)
        self.fake_home = Path(self.temp_dir) / "home"
        self.fake_home.mkdir()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_links_only_sync_preserves_plugin_mirrors(self) -> None:
        plugin_source = self.repo_root / "Plugins" / "harness-engineering"
        plugin_source.mkdir(parents=True)
        (self.repo_root / "Plugins" / "marketplace.json").write_text(
            '{"plugins":[{"name":"harness-engineering","source":{"source":"local","path":"./Plugins/harness-engineering"}}]}\n',
            encoding="utf-8",
        )
        marker = self.fake_home / ".codex" / "plugins" / "harness-engineering" / "preserve.txt"
        marker.parent.mkdir(parents=True)
        marker.write_text("keep\n", encoding="utf-8")

        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(Path, "home", return_value=self.fake_home),
        ):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "success")
        self.assertTrue((self.fake_home / ".agents" / "skills").is_symlink())
        self.assertTrue((self.fake_home / ".codex" / "skills").is_symlink())
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")
        self.assertEqual(result.data["plan"]["user_sync_mode"], "links-only")
        self.assertNotIn("runtime_plugin_mirrors", result.data["plan"])
        self.assertEqual(
            result.data["validation_commands"],
            [
                "./bin/ask skills sync --scope user --user-sync-mode links-only "
                "--json --robot"
            ],
        )

    def test_links_only_sync_rejects_invalid_mode(self) -> None:
        result = skills_commands.sync_skills(
            self.repo_root,
            scope="user",
            dry_run=True,
            plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="everything"),
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("links-only or full", result.errors[0].fix_suggestion)
