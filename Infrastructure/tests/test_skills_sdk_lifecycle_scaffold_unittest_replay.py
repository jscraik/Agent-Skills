from __future__ import annotations

import shlex
from pathlib import Path
from unittest import mock

import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import build_private_stabilization_replay  # noqa: E402


COMMAND = "python3 -m unittest Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold -v"


def _plan(command: str) -> dict[str, list[dict[str, object]]]:
    return {
        "commands": [
            {
                "capability_id": "skill_creator_lifecycle_scaffold",
                "command": command,
                "argv": shlex.split(command),
            }
        ]
    }


class TestSkillsSdkLifecycleScaffoldUnittestReplay:
    def test_exact_argv_accepts_bounded_four_test_transcript(self) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout="",
            stderr=(
                "test_creates_skill_with_lifecycle_metadata_and_honest_starter_copy (...) ... ok\n"
                "test_description_audit_reports_without_breaking_migration (...) ... ok\n"
                "test_rejects_waffly_or_non_trigger_description (...) ... ok\n"
                "test_requires_owner_for_governed_scaffold (...) ... ok\n"
                "----------------------------------------------------------------------\n"
                "Ran 4 tests in 0.134s\n\n"
                "OK\n"
            ),
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(COMMAND),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_pass"
        assert "lifecycle_scaffold_unittest_receipt:valid_marker" in row["evidence"]
        assert "lifecycle_scaffold_unittest_test_count:4" in row["evidence"]
        run.assert_called_once()

    def test_near_miss_without_verbose_flag_remains_deny_by_default(self) -> None:
        command = "python3 -m unittest Infrastructure.scripts.testing.test_skill_creator_lifecycle_scaffold"
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch("ask.skills_sdk.stabilization_replay.subprocess.run") as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "blocked_unsafe"
        assert row["evidence"] == ["deny_by_default"]
        run.assert_not_called()

    def test_malformed_or_ambiguous_transcripts_fail_closed(self) -> None:
        transcripts = (
            "Ran 3 tests in 0.134s\nOK\n",
            "Ran 4 tests in .134s\nOK\n",
            "Ran 4 tests in 0.134s\nFAILED (failures=1)\nOK\n",
            "Ran 4 tests in 0.134s\nOK\ntrailing output\n",
            "Ran 4 tests in 0.134s\nRan 4 tests in 0.135s\nOK\n",
        )
        for transcript in transcripts:
            completed = mock.Mock(returncode=0, stdout="", stderr=transcript)
            with mock.patch(
                "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
                return_value=_plan(COMMAND),
            ), mock.patch(
                "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
            ):
                receipt = build_private_stabilization_replay(REPO_ROOT)

            row = receipt["rows"][0]
            assert row["status"] == "executed_fail"
            assert row["evidence"] == ["lifecycle_scaffold_unittest_receipt:invalid_marker"]

    def test_oversized_transcript_fails_closed(self) -> None:
        completed = mock.Mock(
            returncode=0,
            stdout="",
            stderr=("x" * 5000) + "\nRan 4 tests in 0.134s\nOK\n",
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(COMMAND),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ):
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_fail"
        assert row["evidence"] == ["lifecycle_scaffold_unittest_receipt:oversize"]
