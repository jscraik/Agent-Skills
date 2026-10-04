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

    def _runtime_snapshot(self) -> dict[str, tuple[int, str | bytes]]:
        """Capture disposable home and source bytes, modes, and literal links."""
        root = Path(self.temp_dir)
        snapshot: dict[str, tuple[int, str | bytes]] = {}
        for path in root.rglob("*"):
            mode = path.lstat().st_mode
            value = str(path.readlink()) if path.is_symlink() else path.read_bytes() if path.is_file() else ""
            snapshot[str(path.relative_to(root))] = (mode, value)
        return snapshot

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_retired_user_sync_preserves_links_only_user_sync_dry_run_leaves_home_unchanged(self) -> None:
        before = self._runtime_snapshot()
        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=True,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_preserves_plugin_mirrors(self) -> None:
        plugin_source = self.repo_root / "Plugins" / "harness-engineering"
        plugin_source.mkdir(parents=True)
        (self.repo_root / "Plugins" / "marketplace.json").write_text(
            '{"plugins":[{"name":"harness-engineering","source":{"source":"local","path":"./Plugins/harness-engineering"}}]}\n',
            encoding="utf-8",
        )
        marker = self.fake_home / ".codex" / "plugins" / "harness-engineering" / "preserve.txt"
        marker.parent.mkdir(parents=True)
        marker.write_text("keep\n", encoding="utf-8")

        before = self._runtime_snapshot()
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

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_verifies_exact_runtime_link_targets(self) -> None:
        before = self._runtime_snapshot()
        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_rejects_foreign_or_stale_link_before_mutating(self) -> None:
        foreign_root = Path(self.temp_dir) / "foreign-worktree"
        foreign_skills = foreign_root / ".agents" / "skills"
        foreign_skills.mkdir(parents=True)
        foreign_link = self.fake_home / ".agents" / "skills"
        foreign_link.parent.mkdir(parents=True)
        foreign_link.symlink_to(foreign_skills)

        before = self._runtime_snapshot()
        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_rejects_stale_worktree_link_before_mutating(self) -> None:
        stale_skills = Path(self.temp_dir) / "retired-worktree" / ".agents" / "skills"
        stale_skills.mkdir(parents=True)
        stale_link = self.fake_home / ".agents" / "skills"
        stale_link.parent.mkdir(parents=True)
        stale_link.symlink_to(stale_skills)
        shutil.rmtree(stale_skills.parent)

        before = self._runtime_snapshot()
        with mock.patch.object(Path, "home", return_value=self.fake_home):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_rejects_uninspectable_link_before_mutating(self) -> None:
        target = self.fake_home / ".agents" / "skills"
        target.parent.mkdir(parents=True)
        target.symlink_to(self.repo_root / ".agents" / "skills")

        before = self._runtime_snapshot()
        with (
            mock.patch.object(Path, "home", return_value=self.fake_home),
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]),
            mock.patch.object(skills_commands.os, "readlink", side_effect=OSError("read denied")),
        ):
            result = skills_commands.sync_skills(
                self.repo_root,
                scope="user",
                dry_run=False,
                plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="links-only"),
            )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)

    def test_retired_user_sync_preserves_links_only_sync_rejects_invalid_mode(self) -> None:
        before = self._runtime_snapshot()
        result = skills_commands.sync_skills(
            self.repo_root,
            scope="user",
            dry_run=True,
            plugin_cache_refresh=skills_commands.SkillSyncOptions(user_sync_mode="everything"),
        )

        self.assertEqual(result.status, "error")
        self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
        self.assertIn("User sync is retired", result.errors[0].message)
        self.assertEqual(self._runtime_snapshot(), before)
