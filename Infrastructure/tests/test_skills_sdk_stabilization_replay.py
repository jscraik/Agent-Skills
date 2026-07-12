from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import (  # noqa: E402
    _safe_output_path,
    build_private_stabilization_replay,
)


class TestPrivateStabilizationReplay(unittest.TestCase):
    def test_read_only_ab_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk eval ab-preview --skill-a Infrastructure/tests/fixtures/skills_sdk/valid_skill --skill-b Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill --fixture Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "eval_ab_preview",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_read_only_ab_rubric_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk eval ab-rubric --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "eval_ab_rubric",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_read_only_intake_review_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk intake review Infrastructure/tests/fixtures/skills_sdk/valid_skill --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "intake_review",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_read_only_scenario_quality_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk eval scenario-quality Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "eval_scenario_quality",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_read_only_package_signature_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk security package-signature Infrastructure/tests/fixtures/skills_sdk/valid_skill --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "package_security_signature",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_read_only_package_build_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk package build Infrastructure/tests/fixtures/skills_sdk/valid_skill --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "package_identity",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        run.assert_called_once()

    def test_replay_is_terminal_and_deny_by_default(self) -> None:
        plan = {
            "commands": [
                {"capability_id": "safe", "command": "./bin/ask sdk lenses validate --json --robot", "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"]},
                {"capability_id": "unsafe", "command": "./bin/ask sdk install demo", "argv": ["./bin/ask", "sdk", "install", "demo"]},
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["unclassified_count"], 0)
        self.assertEqual([row["status"] for row in receipt["rows"]], ["executed_pass", "blocked_unsafe"])
        self.assertTrue(all("bytes" not in evidence for evidence in receipt["rows"][0]["evidence"]))
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
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        run.assert_called_once()
        self.assertEqual(receipt["unique_execution_count"], 1)
        self.assertEqual(receipt["rows"][0]["execution_id"], receipt["rows"][1]["execution_id"])

    def test_zero_exit_without_success_receipt_is_an_explicit_failure(self) -> None:
        plan = {
            "commands": [
                {
                    "capability_id": "safe",
                    "command": "./bin/ask sdk lenses validate --json --robot",
                    "argv": ["./bin/ask", "sdk", "lenses", "validate", "--json", "--robot"],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout="not-json", stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_fail")
        self.assertIn("robot_receipt:invalid_json", receipt["rows"][0]["evidence"])

    def test_output_path_must_stay_in_repo_and_avoid_symlinks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outside = Path(tmp) / "outside.json"
            with self.assertRaisesRegex(ValueError, "inside repo root"):
                _safe_output_path(REPO_ROOT, outside)

            link = REPO_ROOT / ".harness" / "evidence" / "skills-sdk-stabilization" / "test-output-link.json"
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(outside)
            try:
                with self.assertRaisesRegex(ValueError, "must not be symlinks"):
                    _safe_output_path(REPO_ROOT, link)
            finally:
                link.unlink()

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
