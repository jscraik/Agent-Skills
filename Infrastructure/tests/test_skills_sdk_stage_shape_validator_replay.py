from __future__ import annotations

import shlex
from pathlib import Path
from unittest import mock

import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import build_private_stabilization_replay  # noqa: E402


def _plan(command: str) -> dict[str, list[dict[str, object]]]:
    return {
        "commands": [
            {
                "capability_id": "review_execution",
                "command": command,
                "argv": shlex.split(command),
            }
        ]
    }


class TestSkillsSdkStageShapeValidatorReplay:
    def test_stage_shape_unittest_exact_argv_accepts_bounded_combined_output(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_sdk_stage_skill_shape_validator -v"
        completed = mock.Mock(
            returncode=0,
            stdout="",
            stderr=(
                "test_accepts_bounded_composite_runbook (...) ... ok\n"
                "test_accepts_bounded_local_markdown_reference (...) ... ok\n"
                "test_allows_upstream_pack_export_without_runtime_dependency (...) ... ok\n"
                "test_load_yaml_classifies_ruby_shim_failure_as_tooling_unavailable (...) ... ok\n"
                "test_load_yaml_uses_ruby_fallback_when_pyyaml_missing (...) ... ok\n"
                "test_rejects_unbounded_mixed_markdown_dossier (...) ... ok\n"
                "----------------------------------------------------------------------\n"
                "Ran 6 tests in 0.005s\n\n"
                "OK\n"
            ),
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_pass"
        assert "stage_shape_unittest_receipt:valid_marker" in row["evidence"]
        assert "stage_shape_unittest_test_count:6" in row["evidence"]
        run.assert_called_once()

    def test_stage_shape_unittest_near_miss_remains_deny_by_default(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_sdk_stage_skill_shape_validator"
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch("ask.skills_sdk.stabilization_replay.subprocess.run") as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "blocked_unsafe"
        assert row["evidence"] == ["deny_by_default"]
        run.assert_not_called()

    def test_stage_shape_unittest_rejects_malformed_success_marker(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_sdk_stage_skill_shape_validator -v"
        completed = mock.Mock(returncode=0, stdout="Ran 5 tests in 0.005s\nOK\n", stderr="")
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_fail"
        assert row["evidence"] == ["stage_shape_unittest_receipt:invalid_marker"]

    def test_stage_shape_unittest_rejects_oversized_output(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_sdk_stage_skill_shape_validator -v"
        completed = mock.Mock(
            returncode=0,
            stdout="",
            stderr=("x" * 5000) + "\nRan 6 tests in 0.005s\nOK\n",
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_fail"
        assert row["evidence"] == ["stage_shape_unittest_receipt:oversize"]

    def test_stage_shape_unittest_rejects_ambiguous_success_transcripts(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_sdk_stage_skill_shape_validator -v"
        transcripts = (
            "Ran 6 tests in 1.s\nOK\n",
            "Ran 6 tests in .5s\nOK\n",
            "Ran 6 tests in 0.005s\nFAILED (failures=1)\nOK\n",
            "Ran 6 tests in 0.005s\nOK\ntrailing output\n",
        )
        for transcript in transcripts:
            completed = mock.Mock(returncode=0, stdout="", stderr=transcript)
            with mock.patch(
                "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
                return_value=_plan(command),
            ), mock.patch(
                "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
            ):
                receipt = build_private_stabilization_replay(REPO_ROOT)

            row = receipt["rows"][0]
            assert row["status"] == "executed_fail"
            assert row["evidence"] == ["stage_shape_unittest_receipt:invalid_marker"]

    def test_stage_shape_validator_marker_is_allowlisted(self) -> None:
        command = "bash Infrastructure/scripts/run-infrastructure-python.sh scripts/validation-and-linting/check_sdk_stage_skill_shape.py"
        completed = mock.Mock(
            returncode=0,
            stdout="[sdk-stage-shape] SDK stage skill shape passed (11 skill(s))\n",
            stderr="",
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_pass"
        assert "stage_shape_receipt:valid_marker" in row["evidence"]
        run.assert_called_once()

    def test_stage_shape_validator_near_miss_remains_deny_by_default(self) -> None:
        command = "bash Infrastructure/scripts/run-infrastructure-python.sh scripts/validation-and-linting/check_sdk_stage_shape.py"
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch("ask.skills_sdk.stabilization_replay.subprocess.run") as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "blocked_unsafe"
        assert row["evidence"] == ["deny_by_default"]
        run.assert_not_called()

    def test_stage_shape_validator_rejects_non_ascii_digit_marker(self) -> None:
        command = "bash Infrastructure/scripts/run-infrastructure-python.sh scripts/validation-and-linting/check_sdk_stage_skill_shape.py"
        completed = mock.Mock(
            returncode=0,
            stdout="[sdk-stage-shape] SDK stage skill shape passed (² skill(s))\n",
            stderr="",
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_fail"
        assert row["evidence"] == ["stage_shape_receipt:invalid_marker"]
