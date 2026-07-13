from __future__ import annotations

from pathlib import Path
from unittest import mock

import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import build_private_stabilization_replay  # noqa: E402


def _plan(command: str, capability_id: str) -> dict[str, list[dict[str, object]]]:
    return {
        "commands": [
            {
                "capability_id": capability_id,
                "command": command,
                "argv": command.split(" "),
            }
        ]
    }


class TestSkillsSdkSigningIntentReplay:
    def test_read_only_signing_intent_is_allowlisted_for_command_receipt(self) -> None:
        command = (
            "./bin/ask sdk package signing-intent "
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill "
            "--policy Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/signing-policy.json "
            "--json --robot"
        )
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command, "package_signing_intent"),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        assert receipt["rows"][0]["status"] == "executed_pass"
        run.assert_called_once()

    def test_signing_intent_policy_path_variant_remains_deny_by_default(self) -> None:
        command = (
            "./bin/ask sdk package signing-intent "
            "Infrastructure/tests/fixtures/skills_sdk/valid_skill "
            "--policy /tmp/alternate-signing-policy.json --json --robot"
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command, "package_signing_intent_variant"),
        ), mock.patch("ask.skills_sdk.stabilization_replay.subprocess.run") as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        assert receipt["rows"][0]["status"] == "blocked_unsafe"
        assert receipt["rows"][0]["evidence"] == ["deny_by_default"]
        run.assert_not_called()
