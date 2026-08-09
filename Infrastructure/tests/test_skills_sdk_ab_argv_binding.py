from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_run import _codex_runner_env, _default_codex_runner  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_ab_run_receipt  # noqa: E402


class TestSkillsSdkAbArgvBinding(unittest.TestCase):
    def test_codex_runner_env_keeps_secret_names_out_of_skill_execution(self) -> None:
        env = _codex_runner_env(
            {
                "PATH": "/usr/bin",
                "HOME": "/tmp/home",
                "OLLAMA_API_KEY": "secret",
                "OPENAI_API_KEY": "secret",
                "SESSION_TOKEN": "secret",
                "CODEX_HOME": "/tmp/codex",
            }
        )
        self.assertEqual(env["PATH"], "/usr/bin")
        self.assertEqual(env["HOME"], "/tmp/home")
        self.assertEqual(env["CODEX_HOME"], "/tmp/codex")
        self.assertNotIn("OLLAMA_API_KEY", env)
        self.assertNotIn("OPENAI_API_KEY", env)
        self.assertNotIn("SESSION_TOKEN", env)

    def test_codex_runner_env_prefers_bound_executable_parent(self) -> None:
        env = _codex_runner_env(
            {
                "PATH": "/usr/bin",
                "CODEX_CLI_PATH": "/Applications/ChatGPT.app/Contents/Resources/codex",
            }
        )
        self.assertEqual(
            env["PATH"],
            "/Applications/ChatGPT.app/Contents/Resources:/usr/bin",
        )
        self.assertEqual(
            env["CODEX_CLI_PATH"],
            "/Applications/ChatGPT.app/Contents/Resources/codex",
        )

    def test_default_cloud_runner_uses_only_actual_home_fifo(self) -> None:
        captured: list[list[str]] = []
        command = [
            "codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request",
            "--sandbox", "read-only", "--cd", ".", "--json", "--output-last-message",
            ".harness/artifacts/last-message.json", "-",
        ]

        def fake_run(argv: list[str], **_kwargs: object) -> subprocess.CompletedProcess[str]:
            captured.append(argv)
            return subprocess.CompletedProcess(argv, 0, stdout='{"type":"item.completed","item":{"type":"agent_message"}}\n', stderr="")

        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".codex" / ".env"
            env_file.parent.mkdir()
            os.mkfifo(env_file)
            with (
                patch("ask.skills_sdk.eval_ab_run.subprocess.run", side_effect=fake_run),
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=Path(directory)),
                patch(
                    "ask.skills_sdk.ab_transport_contracts.configs_auth_wrapper",
                    return_value="/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh",
                ),
            ):
                result = _default_codex_runner(command, "prompt", REPO_ROOT, 1)
        self.assertEqual(captured[0][:7], [
            "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh",
            "--env-file", str(env_file), "--require-env", "OLLAMA_API_KEY", "--",
        ])
        self.assertEqual(result.executed_argv[:7], captured[0][:7])
        self.assertEqual(captured[0][7:13], [
            "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-codex-exec.sh",
            "--profile", "oss-cloud", "--model", "deepseek-v4-flash:0731-cloud",
        ])

    def test_default_cloud_runner_rejects_non_fifo_stream_before_subprocess(self) -> None:
        command = [
            "codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request",
            "--sandbox", "read-only", "--cd", ".", "--json", "--output-last-message",
            ".harness/artifacts/last-message.json", "-",
        ]
        with tempfile.TemporaryDirectory() as directory:
            env_file = Path(directory) / ".codex" / ".env"
            env_file.parent.mkdir()
            env_file.write_text("plaintext must not be read", encoding="utf-8")
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=Path(directory)),
            ):
                with self.assertRaisesRegex(ValueError, "opaque environment stream"):
                    _default_codex_runner(command, "prompt", REPO_ROOT, 1)

    def test_v1_reader_rejects_output_path_not_proven_by_argv(self) -> None:
        candidate = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        candidate["command_plan"][0]["output_last_message_path"] = "evidence/forged-last-message.json"

        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)

        candidate = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        result = candidate["runtime_profile_gates"][0]["variant_results"][0]
        result["command_argv"].extend(["--output-last-message", "evidence/forged-last-message.json"])

        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)

    def test_v1_reader_rejects_reversed_a_b_receipt_order(self) -> None:
        candidate = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        candidate["command_variant_labels"] = ["B", "A"]
        candidate["command_plan"].reverse()
        candidate["variant_results"].reverse()
        for gate in candidate["runtime_profile_gates"]:
            gate["command_plan"].reverse()
            gate["variant_results"].reverse()

        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)

    def test_v1_reader_rejects_reversed_blocked_a_b_labels(self) -> None:
        candidate = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        candidate["status"] = "blocked"
        candidate["blockers"] = ["B:cloud_auth_unavailable"]
        candidate["command_variant_labels"] = ["B", "A"]
        cloud_gate = candidate["runtime_profile_gates"][1]
        cloud_gate["status"] = "blocked"
        cloud_gate["blockers"] = ["cloud_auth_unavailable"]
        cloud_gate["command_plan"] = []
        cloud_gate["variant_results"] = []

        with self.assertRaises(ValueError):
            validate_ab_run_receipt(candidate)
