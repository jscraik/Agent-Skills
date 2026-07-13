from __future__ import annotations

import shlex
from pathlib import Path
from unittest import mock

import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.stabilization_replay import build_private_stabilization_replay  # noqa: E402
from ask.commands.skills_impl import skills_sdk_plugin_create  # noqa: E402


def _plan(command: str) -> dict[str, list[dict[str, object]]]:
    return {
        "commands": [
            {
                "capability_id": "plugin_create_plugin_preview",
                "command": command,
                "argv": shlex.split(command),
            }
        ]
    }


class TestSkillsSdkPluginCreatePluginPreviewReplay:
    def test_plugin_preview_preserves_requested_companion_folder(self) -> None:
        result = skills_sdk_plugin_create(
            REPO_ROOT,
            kind="plugin",
            name="demo-plugin",
            category="third-party",
            with_registry=True,
            companion_folders=["references"],
            apply=False,
        )

        payload = result.data["skills_sdk_plugin_create"]
        assert result.status == "success"
        assert any("--with-references" in command for command in payload["planned_commands"])

    def test_plugin_preview_is_allowlisted_for_command_receipt(self) -> None:
        command = (
            "./bin/ask sdk plugin create demo-plugin --kind plugin --category third-party "
            "--with-registry --with-references --preview --json --robot"
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

    def test_plugin_preview_without_preview_remains_deny_by_default(self) -> None:
        command = (
            "./bin/ask sdk plugin create demo-plugin --kind plugin --category third-party "
            "--with-registry --with-references --json --robot"
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
