"""Home skill installation belongs to the selected runtime, not this repository."""

from __future__ import annotations

import importlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_TESTING_DIR = Path(__file__).resolve().parent
if str(_TESTING_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTING_DIR))

_HELPERS = importlib.import_module("test_skill_lifecycle_validation_impl")
SYNC_IMPL_SCRIPT = _HELPERS.SYNC_IMPL_SCRIPT
load_skills_impl_module = _HELPERS.load_skills_impl_module


class UserSkillSyncRetirementTests(unittest.TestCase):
    def test_python_user_modes_reject_before_touching_home(self) -> None:
        skills = load_skills_impl_module()
        for mode in ("full", "links-only"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                installed = root / "home" / ".agents" / "skills" / "retained"
                installed.mkdir(parents=True)
                sentinel = installed / "SKILL.md"
                sentinel.write_text("owner content\n", encoding="utf-8")
                with mock.patch.object(Path, "home", return_value=root / "home"):
                    result = skills.sync_skills(
                        root / "source", scope="user",
                        plugin_cache_refresh=skills.SkillSyncOptions(
                            plugin_cache_refresh="skip", user_sync_mode=mode,
                        ),
                    )
                self.assertEqual(result.status, "error")
                self.assertEqual(result.errors[0].code, "ERR_RETIRED_USER_SYNC")
                self.assertIn("User sync is retired", result.errors[0].message)
                self.assertEqual(sentinel.read_text(encoding="utf-8"), "owner content\n")
                self.assertFalse((root / "home" / ".codex" / "skills").exists())
                self.assertFalse((root / "source").exists())

    def test_shell_user_scope_rejects_before_lock_or_projection(self) -> None:
        for arguments, scope in ((["--user"], "workspace"), ([], "user")):
            with self.subTest(arguments=arguments), tempfile.TemporaryDirectory() as temporary:
                environment = dict(os.environ, SYNC_SKILLS_SCOPE=scope, TMPDIR=temporary)
                result = subprocess.run(
                    ["bash", str(SYNC_IMPL_SCRIPT), *arguments],
                    env=environment, text=True, capture_output=True, check=False,
                )
                self.assertEqual(result.returncode, 2)
                self.assertIn("ERR_RETIRED_USER_SYNC", result.stderr)
                self.assertEqual(list(Path(temporary).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
