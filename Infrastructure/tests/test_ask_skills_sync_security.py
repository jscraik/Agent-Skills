import os
import shutil
import sys
import tempfile
from unittest import TestCase, main
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.append(str(REPO_ROOT / "scripts"))

from ask.commands import skills as skills_commands


class TestAskSkillsSyncSecurity(TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp(prefix="ask-sync-security-")
        self.repo_root = Path(self.temp_dir) / "repo"
        self.repo_root.mkdir(parents=True)
        (self.repo_root / ".agents" / "skills").mkdir(parents=True)
        self.antigravity = self.repo_root / "skills-antigravity"
        self.antigravity.mkdir(parents=True)
        self.fake_home = Path(self.temp_dir) / "home"
        self.fake_home.mkdir(parents=True)

        safe_skill = self.antigravity / "safe-skill"
        safe_skill.mkdir(parents=True)
        (safe_skill / "SKILL.md").write_text("# Safe Skill\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_sync_dir_copy_rejects_symlink_payload(self) -> None:
        secret = Path(self.temp_dir) / "secret.txt"
        secret.write_text("TOPSECRET", encoding="utf-8")
        os.symlink(secret, self.antigravity / "safe-skill" / "leak.txt")

        with self.assertRaises(ValueError) as ctx:
            skills_commands._sync_dir_copy(self.antigravity, self.fake_home / "dst", dry_run=False)

        self.assertIn("symlink", str(ctx.exception).lower())

    def test_sync_skills_user_scope_blocks_symlink_before_mutation(self) -> None:
        secret = Path(self.temp_dir) / "secret.txt"
        secret.write_text("TOPSECRET", encoding="utf-8")
        os.symlink(secret, self.antigravity / "safe-skill" / "leak.txt")

        with mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]):
            with mock.patch.object(Path, "home", return_value=self.fake_home):
                result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "error")
        self.assertTrue(result.errors)
        self.assertEqual(result.errors[0].code, "ERR_VALIDATION")
        self.assertIn("symlink", result.errors[0].message.lower())
        self.assertFalse((self.fake_home / ".gemini" / "antigravity" / "skills").exists())
        self.assertFalse((self.fake_home / ".claude" / "skills").exists())
        self.assertFalse((self.fake_home / ".agents" / "skills").exists())
        self.assertFalse((self.fake_home / ".codex" / "skills").exists())
        self.assertFalse((self.fake_home / ".antigravity" / "skills").exists())

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
        with mock.patch.object(skills_commands, "discover_skill_entries", return_value=[]):
            with mock.patch.object(Path, "home", return_value=self.fake_home):
                result = skills_commands.sync_skills(self.repo_root, scope="user", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertFalse((self.repo_root / "skills").exists())
        self.assertTrue((self.fake_home / ".codex" / "skills").is_symlink())

    def test_sync_skills_workspace_refreshes_catalog_projections(self) -> None:
        skills_dir = self.repo_root / ".agents" / "skills"
        antigravity_dir = self.repo_root / "skills-antigravity"
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
        stale_antigravity_dir = antigravity_dir / "stale-skill"
        stale_antigravity_dir.mkdir()
        (stale_antigravity_dir / "SKILL.md").write_text("# Stale Skill\n", encoding="utf-8")
        with (
            mock.patch.object(skills_commands, "discover_skill_entries", return_value=[fake_entry]),
            mock.patch.object(skills_commands, "discover_catalog_entries", return_value=[fake_entry]),
        ):
            result = skills_commands.sync_skills(self.repo_root, scope="workspace", dry_run=False)

        self.assertEqual(result.status, "success")
        self.assertTrue((skills_dir / "valid-skill").is_symlink())
        antigravity_skill = antigravity_dir / "valid-skill"
        self.assertTrue(antigravity_skill.is_dir())
        self.assertFalse((antigravity_skill / "SKILL.md").is_symlink())
        self.assertFalse(stale_antigravity_dir.exists())
        self.assertIn("**1 skills**", readme_path.read_text(encoding="utf-8"))
        self.assertIn("`total_skills`: 1", skill_index_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
