from __future__ import annotations

import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check-skill-projection-parity.sh"


class CheckSkillProjectionParityTests(unittest.TestCase):
    def _make_ask_stub(self, directory: Path, *, missing_skill: str | None = None) -> Path:
        ask_stub = directory / "ask"
        runtime_skills = [
            {"name": "chronicle"},
            {"name": "desktop-commander-guide"},
            {"name": "find-skills"},
            {"name": "simplify"},
        ]
        if missing_skill is not None:
            runtime_skills = [skill for skill in runtime_skills if skill["name"] != missing_skill]
        script = """#!/usr/bin/env python3
import json
import sys

if sys.argv[1:] == ["skills", "sync", "--scope", "workspace", "--projection", "rooted", "--dry-run", "--json"]:
    print(json.dumps({"status": "success", "data": {"operation": "preview"}}))
    raise SystemExit(0)
if sys.argv[1:] == ["skills", "list", "--json", "--robot"]:
    print(json.dumps({"status": "success", "data": {"skills": %s, "validation_commands": ["./bin/ask skills list --json --robot"]}}))
    raise SystemExit(0)
raise SystemExit(2)
""" % json.dumps(runtime_skills)
        ask_stub.write_text(script, encoding="utf-8")
        ask_stub.chmod(ask_stub.stat().st_mode | stat.S_IEXEC)
        return ask_stub

    def test_help_shows_usage(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT), "--help"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("skill projection parity", result.stdout)

    def test_parity_checker_passes_with_expected_targets_and_runtime_list(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-parity-") as temp_dir:
            temp_root = Path(temp_dir)
            fake_home = temp_root / "home"
            fake_home.mkdir()
            agents_root = fake_home / ".agents"
            codex_root = fake_home / ".codex"
            agents_root.mkdir()
            codex_root.mkdir()
            (agents_root / "skills").symlink_to(REPO_ROOT / ".agents" / "skills")
            (codex_root / "skills").symlink_to(REPO_ROOT / ".agents" / "skills")
            ask_stub = self._make_ask_stub(temp_root)

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--json",
                    "--home",
                    str(fake_home),
                    "--ask-bin",
                    str(ask_stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["target_report"]["status"], "pass")
        self.assertEqual(payload["preview_report"]["status"], "pass")
        self.assertEqual(payload["runtime_report"]["status"], "pass")

    def test_parity_checker_blocks_when_representative_skill_is_missing(self) -> None:
        with tempfile.TemporaryDirectory(prefix="skill-parity-") as temp_dir:
            temp_root = Path(temp_dir)
            fake_home = temp_root / "home"
            fake_home.mkdir()
            agents_root = fake_home / ".agents"
            codex_root = fake_home / ".codex"
            agents_root.mkdir()
            codex_root.mkdir()
            (agents_root / "skills").symlink_to(REPO_ROOT / ".agents" / "skills")
            (codex_root / "skills").symlink_to(REPO_ROOT / ".agents" / "skills")
            ask_stub = self._make_ask_stub(temp_root, missing_skill="find-skills")

            result = subprocess.run(
                [
                    "bash",
                    str(SCRIPT),
                    "--json",
                    "--home",
                    str(fake_home),
                    "--ask-bin",
                    str(ask_stub),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("runtime skill list is missing representative skills", payload["reasons"])
        self.assertIn("find-skills", payload["runtime_report"]["missing"])


if __name__ == "__main__":
    unittest.main()
