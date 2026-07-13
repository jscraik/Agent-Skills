from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "tests"))

from ask.skills_sdk.stabilization_replay import (  # noqa: E402
    _safe_output_path,
    build_private_stabilization_replay,
)
from helpers.schema_validator import _validate_schema_subset  # noqa: E402


class TestPrivateStabilizationReplay(unittest.TestCase):
    def test_determinism_selection_receipt_is_schema_valid_and_revision_bound(self) -> None:
        artifact_path = REPO_ROOT / ".harness/evidence/skills-sdk-stabilization/phase2-determinism-audit-replay-receipt.v1.json"
        schema_path = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/phase2-read-only-replay-receipt.v1.schema.json"
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        _validate_schema_subset(schema, artifact, {schema_path.name: schema})

        self.assertTrue(_is_ancestor(artifact["base_commit"], _git_head()))
        self.assertEqual(artifact["selected"]["command"], "./bin/ask sdk determinism audit --scope skills --limit 10 --json --robot")
        self.assertEqual(artifact["selected"]["registration_owner"], "Infrastructure/scripts/lib/ask/commands/sdk.py")
        if artifact["status"] != "bounded_local_pass":
            self.assertEqual(artifact["status"], "selected")
            return

        self.assertEqual(artifact["execution"]["candidate_count"], 10)
        self.assertEqual(artifact["remaining_deny_by_default_count"], 24)
        self.assertFalse(_source_files_dirty(artifact["source_files"]))
        self.assertEqual(
            artifact["source_tree_digest"],
            _immutable_source_tree_digest(artifact["base_commit"], artifact["source_files"]),
        )

    def test_read_only_plugin_help_accepts_bounded_text_receipt(self) -> None:
        command = "./bin/ask sdk plugin --help"
        plan = {
            "commands": [
                {
                    "capability_id": "sdk_plugin_lifecycle",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout="usage: ask sdk plugin [-h]\noptions:\n  -h, --help  show this help message and exit\n", stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("help_receipt:valid_text", receipt["rows"][0]["evidence"])
        self.assertIn("help_nonempty_line_count:3", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_plugin_help_rejects_oversized_text_receipt(self) -> None:
        command = "./bin/ask sdk plugin --help"
        plan = {
            "commands": [
                {
                    "capability_id": "sdk_plugin_lifecycle",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout="usage: ask sdk plugin\n" + ("x" * 4096), stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_fail")
        self.assertIn("help_receipt:oversize", receipt["rows"][0]["evidence"])

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

    def test_read_only_receipt_rejects_nested_mutation_flag(self) -> None:
        command = "./bin/ask sdk eval ab-preview --skill-a Infrastructure/tests/fixtures/skills_sdk/valid_skill --skill-b Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill --fixture Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json --preview --json --robot"
        plan = {"commands": [{"capability_id": "eval_ab_preview", "command": command, "argv": command.split(" ")}]}
        completed = mock.Mock(
            returncode=0,
            stdout='{"status":"success","metadata":{},"data":{"receipt":{"status":"preview","mutation_performed":true}}}',
            stderr="",
        )
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_fail")
        self.assertIn("robot_receipt:$.data.receipt.mutation_performed:true", receipt["rows"][0]["evidence"])

    def test_read_only_trust_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk trust decide Infrastructure/tests/fixtures/skills_sdk/valid_skill --decision trust --reason 'fixture passed local checks' --owner skills-sdk-tests --preview --json --robot"
        argv = [
            "./bin/ask",
            "sdk",
            "trust",
            "decide",
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
            "--decision",
            "trust",
            "--reason",
            "fixture passed local checks",
            "--owner",
            "skills-sdk-tests",
            "--preview",
            "--json",
            "--robot",
        ]
        plan = {"commands": [{"capability_id": "trust_store", "command": command, "argv": argv}]}
        completed = mock.Mock(
            returncode=0,
            stdout=(
                '{"status":"success","metadata":{},"data":{'
                '"skills_sdk_trust_decide":{"status":"preview",'
                '"mutation_performed":false,"trust_store_mutated":false}}}'
            ),
            stderr="",
        )
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_trust_preview_missing_source_remains_deny_by_default(self) -> None:
        command = "./bin/ask sdk trust decide Infrastructure/tests/fixtures/skills_sdk/missing_skill --decision trust --reason 'fixture passed local checks' --owner skills-sdk-tests --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "trust_store",
                    "command": command,
                    "argv": [
                        "./bin/ask",
                        "sdk",
                        "trust",
                        "decide",
                        "Infrastructure/tests/fixtures/skills_sdk/missing_skill",
                        "--decision",
                        "trust",
                        "--reason",
                        "fixture passed local checks",
                        "--owner",
                        "skills-sdk-tests",
                        "--preview",
                        "--json",
                        "--robot",
                    ],
                }
            ]
        }
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run"
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        self.assertEqual(row["status"], "blocked_unsafe")
        self.assertEqual(row["evidence"], ["deny_by_default"])
        run.assert_not_called()

    def test_read_only_sandbox_validate_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk sandbox validate --profile Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/sandbox-profile.json --json --robot"
        argv = command.split(" ")
        plan = {"commands": [{"capability_id": "sandbox", "command": command, "argv": argv}]}
        completed = mock.Mock(
            returncode=0,
            stdout=(
                '{"status":"success","metadata":{},"data":{'
                '"skills_sdk_sandbox_validate":{"status":"pass",'
                '"mutation_performed":false,"execution_performed":false}}}'
            ),
            stderr="",
        )
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_sandbox_validate_unsafe_profile_remains_deny_by_default(self) -> None:
        command = "./bin/ask sdk sandbox validate --profile Infrastructure/tests/fixtures/skills_sdk/schema_spine/invalid/sandbox-profile-allow-default.json --json --robot"
        plan = {"commands": [{"capability_id": "sandbox", "command": command, "argv": command.split(" ")}]}
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run"
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        self.assertEqual(row["status"], "blocked_unsafe")
        self.assertEqual(row["evidence"], ["deny_by_default"])
        run.assert_not_called()

    def test_read_only_skills_doctor_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask skills doctor Skills/agent-ops/simplify --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "skills_doctor",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        completed = mock.Mock(
            returncode=0,
            stdout=(
                '{"status":"success","metadata":{},"data":{'
                '"schema_version":"skill-doctor.v1","status":"warning",'
                '"findings":[{"code":"capability_contract_incomplete"},'
                '{"code":"outcome_proof_missing"}],"blockers":[],"errors":[]}}'
            ),
            stderr="",
        )
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_read_only_sdk_check_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk check Skills/agent-ops/simplify --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "check",
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

    def test_read_only_sdk_ir_build_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk ir build Infrastructure/tests/fixtures/skills_sdk/valid_skill --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "skill_ir",
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
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_read_only_sdk_install_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk install Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "install_preview",
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
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_read_only_sdk_lenses_select_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk lenses select --prompt 'review a skill for validation confidence' --intent validation_review --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "sdk_lenses",
                    "command": command,
                    "argv": ["./bin/ask", "sdk", "lenses", "select", "--prompt", "review a skill for validation confidence", "--intent", "validation_review", "--json", "--robot"],
                }
            ]
        }
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_read_only_sdk_review_plan_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "review_plan",
                    "command": command,
                    "argv": [
                        "./bin/ask",
                        "sdk",
                        "review",
                        "plan",
                        "--target",
                        "Skills/agent-ops/simplify",
                        "--intent",
                        "validation_review",
                        "--json",
                        "--robot",
                    ],
                }
            ]
        }
        completed = mock.Mock(
            returncode=0,
            stdout='{"status":"success","metadata":{},"data":{"review_plan":{"status":"pass","mutation_performed":false}}}',
            stderr="",
        )
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        self.assertEqual(receipt["rows"][0]["status"], "executed_pass")
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
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

    def test_read_only_determinism_audit_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk determinism audit --scope skills --limit 10 --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "determinism_audit",
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
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once()

    def test_read_only_capability_evidence_verify_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk evidence verify --scope capability-matrix --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "capability_evidence",
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
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once_with(
            command.split(" "),
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )

    def test_read_only_static_explorer_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = "./bin/ask sdk explorer static --preview --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "skill_explorer",
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
        self.assertIn("robot_receipt:valid_envelope", receipt["rows"][0]["evidence"])
        run.assert_called_once_with(
            command.split(" "),
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )

    def test_static_explorer_preview_missing_preview_remains_deny_by_default(self) -> None:
        command = "./bin/ask sdk explorer static --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "skill_explorer",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run"
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        self.assertEqual(row["status"], "blocked_unsafe")
        self.assertEqual(row["evidence"], ["deny_by_default"])
        run.assert_not_called()

    def test_capability_evidence_verify_altered_scope_remains_deny_by_default(self) -> None:
        command = "./bin/ask sdk evidence verify --scope package --json --robot"
        plan = {
            "commands": [
                {
                    "capability_id": "capability_evidence",
                    "command": command,
                    "argv": [*command.split(" ")],
                }
            ]
        }
        with mock.patch("ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt", return_value=plan), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run"
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        self.assertEqual(row["status"], "blocked_unsafe")
        self.assertEqual(row["evidence"], ["deny_by_default"])
        run.assert_not_called()

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
            link.unlink(missing_ok=True)
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


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def _is_ancestor(base: str, head: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", base, head], cwd=REPO_ROOT, check=False
    ).returncode == 0


def _source_tree_digest(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update((REPO_ROOT / path).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _source_files_dirty(paths: list[str]) -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", *paths], cwd=REPO_ROOT, check=False
    )
    staged = subprocess.run(
        ["git", "diff", "--cached", "--quiet", "HEAD", "--", *paths], cwd=REPO_ROOT, check=False
    )
    return result.returncode != 0 or staged.returncode != 0


def _immutable_source_tree_digest(base_commit: str, paths: list[str]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        content = subprocess.run(
            ["git", "show", f"{base_commit}:{path}"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        ).stdout
        digest.update(path.encode())
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


if __name__ == "__main__":
    unittest.main()
