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
