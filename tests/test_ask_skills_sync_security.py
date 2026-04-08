import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(REPO_ROOT / "scripts" / "lib"))
sys.path.append(str(REPO_ROOT / "scripts"))

from ask.commands import skills as skills_commands


class TestAskSkillsSyncSecurity(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
