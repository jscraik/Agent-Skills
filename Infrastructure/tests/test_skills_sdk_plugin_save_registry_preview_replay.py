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
                "capability_id": "plugin_save_registry_preview",
                "command": command,
                "argv": shlex.split(command),
            }
        ]
    }


class TestSkillsSdkPluginSaveRegistryPreviewReplay:
    def test_registry_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = (
            "./bin/ask sdk plugin save-registry --kind plugin --target Plugins/plugin-factory "
            "--preview --json --robot"
        )
        completed = mock.Mock(returncode=0, stdout='{"status":"success","metadata":{},"data":{}}', stderr="")
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch(
            "ask.skills_sdk.stabilization_replay.subprocess.run", return_value=completed
        ) as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "executed_pass"
        assert "robot_receipt:valid_envelope" in row["evidence"]
        run.assert_called_once()

    def test_registry_apply_form_remains_deny_by_default(self) -> None:
        command = (
            "./bin/ask sdk plugin save-registry --kind plugin --target Plugins/plugin-factory "
            "--apply --json --robot"
        )
        with mock.patch(
            "ask.skills_sdk.stabilization_replay.build_command_evidence_plan_receipt",
            return_value=_plan(command),
        ), mock.patch("ask.skills_sdk.stabilization_replay.subprocess.run") as run:
            receipt = build_private_stabilization_replay(REPO_ROOT)

        row = receipt["rows"][0]
        assert row["status"] == "blocked_unsafe"
        assert row["evidence"] == ["deny_by_default"]
        run.assert_not_called()
