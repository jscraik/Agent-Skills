from __future__ import annotations

import sys
import subprocess
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import build_private_stabilization_replay  # noqa: E402


class TestPrivateStabilizationReplay(unittest.TestCase):
    def test_replay_is_terminal_and_deny_by_default(self) -> None:
        plan = {
            "commands": [
                {"capability_id": "safe", "command": "./bin/ask sdk lenses validate --json --robot", "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"]},
                {"capability_id": "unsafe", "command": "./bin/ask sdk install demo", "argv": ["./bin/ask", "sdk", "install", "demo"]},
            ]
        }
        completed = mock.Mock(returncode=0, stdout="{}", stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["unclassified_count"], 0)
        self.assertEqual([row["status"] for row in receipt["rows"]], ["executed_pass", "blocked_unsafe"])
        run.assert_called_once()

    def test_allowlisted_failure_is_explicit(self) -> None:
        plan = {
            "commands": [
                {"capability_id": "safe", "command": "./bin/ask sdk lenses validate --json --robot", "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"]}
            ]
        }
        completed = mock.Mock(returncode=7, stdout="", stderr="failed")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_fail")
        self.assertEqual(receipt["rows"][0]["exit_code"], 7)

    def test_duplicate_argv_executes_once_and_links_each_occurrence(self) -> None:
        command = {"command": "./bin/ask sdk lenses validate --json --robot", "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"]}
        plan = {"commands": [{"capability_id": "one", **command}, {"capability_id": "two", **command}]}
        completed = mock.Mock(returncode=0, stdout="{}", stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        run.assert_called_once()
        self.assertEqual(receipt["unique_execution_count"], 1)
        self.assertEqual(receipt["rows"][0]["execution_id"], receipt["rows"][1]["execution_id"])

    def test_timeout_and_os_error_are_terminal_and_replay_continues(self) -> None:
        commands = [
            {"capability_id": "timeout", "command": "./bin/ask sdk lenses validate --json --robot", "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"]},
            {"capability_id": "os-error", "command": "./bin/ask sdk eval profiles --preview --json --robot", "argv": ["./bin/ask", "sdk", "eval", "profiles", "--preview", "--json", "--robot"]},
        ]
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value={"commands": commands}), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run",
            side_effect=[subprocess.TimeoutExpired(commands[0]["argv"], 30), FileNotFoundError(2, "missing")],
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual([row["status"] for row in receipt["rows"]], ["executed_fail", "executed_fail"])
        self.assertIn("timed out", receipt["rows"][0]["reason"])
        self.assertIn("FileNotFoundError", receipt["rows"][1]["reason"])


if __name__ == "__main__":
    unittest.main()
