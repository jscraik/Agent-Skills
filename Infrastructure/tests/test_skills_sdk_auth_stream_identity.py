from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_preflight import _approved_cloud_auth_fact, _cloud_catalog_fact  # noqa: E402
from ask.skills_sdk.eval_ab_run import _execution_argv_for_run, _validated_recorded_execution_argv  # noqa: E402
from ask.skills_sdk.ab_transport_contracts import (  # noqa: E402
    configs_auth_backed_invocation,
    is_actual_opaque_env_reference,
    is_opaque_env_reference,
)


class TestSkillsSdkAuthStreamIdentity(unittest.TestCase):
    @staticmethod
    def _catalog_payload() -> dict[str, object]:
        return {
            "result_class": "pass",
            "network_accessed": True,
            "http_status": 200,
            "catalog_digest": f"sha256:{'a' * 64}",
            "matched_model": "deepseek-v4-flash:cloud",
            "match_count": 1,
            "secret_value_observed": False,
            "secret_not_observed": True,
            "generation_performed": False,
            "provider_invoked": False,
            "codex_exec_invoked": False,
        }

    def test_catalog_probe_blocks_same_path_fifo_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            env_file = home / ".codex" / ".env"
            env_file.parent.mkdir()
            os.mkfifo(env_file)
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}, clear=True),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=home),
                patch(
                    "ask.skills_sdk.eval_ab_preflight.configs_auth_wrapper",
                    return_value="/mock/configs/run-auth-backed.sh",
                ),
            ):
                auth = _approved_cloud_auth_fact("deepseek-v4-flash:cloud")
                env_file.unlink()
                os.mkfifo(env_file)
                fact = _cloud_catalog_fact(
                    "deepseek-v4-flash:cloud", Path("/mock/oss-cloud.config.toml"), auth,
                    lambda _command: subprocess.CompletedProcess(
                        ["bash", "/mock/configs/run-auth-backed.sh"], 0,
                        stdout=json.dumps(self._catalog_payload()), stderr="",
                    ),
                )
        self.assertEqual(fact["status"], "blocked")
        self.assertEqual(fact["blocker"]["blocker_class"], "cloud_auth_unavailable")

    def test_catalog_probe_rejects_arbitrary_fifo_before_runner_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / "unapproved-cloud-env"
            os.mkfifo(env_file)
            auth = {
                "status": "pass",
                "auth_source": "1password_desktop_fifo",
                "auth_stream_identity_digest": "sha256:" + "a" * 64,
            }
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}, clear=True),
                patch(
                    "ask.skills_sdk.eval_ab_preflight.configs_auth_wrapper",
                    return_value="/mock/configs/run-auth-backed.sh",
                ),
            ):
                fact = _cloud_catalog_fact(
                    "deepseek-v4-flash:cloud",
                    Path("/mock/oss-cloud.config.toml"),
                    auth,
                    lambda _command: self.fail("unapproved FIFO must not reach the catalog runner"),
                )
        self.assertEqual(fact["status"], "blocked")
        self.assertEqual(fact["blocker"]["blocker_class"], "cloud_auth_unavailable")

    def test_auth_rejects_another_home_codex_fifo_before_catalog_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "actual-home"
            approved_env = home / ".codex" / ".env"
            unapproved_env = Path(temp_dir) / "other-home" / ".codex" / ".env"
            approved_env.parent.mkdir(parents=True)
            unapproved_env.parent.mkdir(parents=True)
            os.mkfifo(approved_env)
            os.mkfifo(unapproved_env)
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(unapproved_env)}, clear=True),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=home),
                patch(
                    "ask.skills_sdk.eval_ab_preflight.configs_auth_wrapper",
                    return_value="/mock/configs/run-auth-backed.sh",
                ),
            ):
                auth = _approved_cloud_auth_fact("deepseek-v4-flash:cloud")
                fact = _cloud_catalog_fact(
                    "deepseek-v4-flash:cloud",
                    Path("/mock/oss-cloud.config.toml"),
                    auth,
                    lambda _command: self.fail("unapproved home FIFO must not reach the catalog runner"),
                )
        self.assertEqual(auth["status"], "blocked")
        self.assertEqual(fact["status"], "blocked")

    def test_runtime_entrypoints_reject_receipt_only_stream_marker(self) -> None:
        command = ["codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request", "-"]
        with (
            patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": "<operator-approved-opaque-env-stream>"}, clear=True),
            patch("ask.skills_sdk.eval_ab_preflight.configs_auth_wrapper", return_value="/mock/configs/run-auth-backed.sh"),
            patch("ask.skills_sdk.eval_ab_run.configs_auth_wrapper", return_value="/mock/configs/run-auth-backed.sh"),
        ):
            auth = _approved_cloud_auth_fact("deepseek-v4-flash:cloud")
            with self.assertRaisesRegex(ValueError, "operator-approved opaque environment stream"):
                _execution_argv_for_run(command)
        self.assertEqual(auth["status"], "blocked")

    def test_receipt_only_stream_marker_is_never_a_runtime_path(self) -> None:
        marker = "<operator-approved-opaque-env-stream>"
        self.assertTrue(is_opaque_env_reference(marker))
        self.assertFalse(is_actual_opaque_env_reference(marker))

    def test_recorded_runner_argv_rejects_receipt_only_stream_marker(self) -> None:
        command = ["codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request", "-"]
        execution = [
            "bash", "/Users/jamiecraik/dev/configs/codex/scripts/run-auth-backed.sh",
            "--env-file", "<operator-approved-opaque-env-stream>",
            "--require-env", "OLLAMA_API_KEY", "--", *command,
        ]
        with self.assertRaisesRegex(ValueError, "operator-approved opaque environment stream"):
            _validated_recorded_execution_argv(execution, command, "oss-cloud")

    @unittest.skipIf(not hasattr(os, "symlink"), "symlink support unavailable")
    def test_runtime_stream_rejects_symlinked_codex_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir) / "home"
            external = Path(temp_dir) / "external"
            stream = external / ".env"
            home.mkdir()
            external.mkdir()
            os.mkfifo(stream)
            os.symlink(external, home / ".codex")
            with patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=home):
                self.assertFalse(is_actual_opaque_env_reference(str(home / ".codex" / ".env")))

    @unittest.skipIf(not hasattr(os, "symlink"), "symlink support unavailable")
    def test_runtime_stream_rejects_symlinked_account_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            real_home = root / "real-home"
            linked_home = root / "linked-home"
            env_file = real_home / ".codex" / ".env"
            env_file.parent.mkdir(parents=True)
            os.mkfifo(env_file)
            os.symlink(real_home, linked_home)
            with patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=linked_home):
                self.assertFalse(is_actual_opaque_env_reference(str(linked_home / ".codex" / ".env")))

    def test_configs_wrapper_invocation_binds_fifo_identity_without_opening_stream(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            env_file = home / ".codex" / ".env"
            env_file.parent.mkdir()
            os.mkfifo(env_file)
            with (
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=home),
                patch(
                    "ask.skills_sdk.ab_transport_contracts.configs_auth_wrapper",
                    return_value="/mock/configs/run-auth-backed.sh",
                ),
            ):
                with configs_auth_backed_invocation(env_file) as invocation:
                    runtime = invocation.runtime_argv(["child"])
                    self.assertEqual(runtime, [
                        "bash", "/mock/configs/run-auth-backed.sh", "--env-file", str(env_file),
                        "--require-env", "OLLAMA_API_KEY", "--", "child",
                    ])
                    self.assertEqual(invocation.receipt_argv(["child"]), runtime)
                    self.assertNotIn("/dev/fd/", " ".join(runtime))

    def test_default_catalog_runner_hands_fifo_only_to_configs_wrapper(self) -> None:
        captured: list[tuple[list[str], dict[str, object]]] = []

        def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            captured.append((argv, kwargs))
            return subprocess.CompletedProcess(
                argv, 0, stdout=json.dumps(self._catalog_payload()), stderr="",
            )

        with tempfile.TemporaryDirectory() as temp_dir:
            home = Path(temp_dir)
            env_file = home / ".codex" / ".env"
            env_file.parent.mkdir()
            os.mkfifo(env_file)
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}, clear=True),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=home),
                patch(
                    "ask.skills_sdk.eval_ab_preflight.configs_auth_wrapper",
                    return_value="/mock/configs/run-auth-backed.sh",
                ),
                patch("ask.skills_sdk.eval_ab_preflight.subprocess.run", side_effect=fake_run),
            ):
                auth = _approved_cloud_auth_fact("deepseek-v4-flash:cloud")
                fact = _cloud_catalog_fact(
                    "deepseek-v4-flash:cloud", Path("/mock/oss-cloud.config.toml"), auth,
                )
        self.assertEqual(fact["status"], "pass")
        self.assertEqual(captured[0][0][:7], [
            "bash", "/mock/configs/run-auth-backed.sh", "--env-file", str(env_file),
            "--require-env", "OLLAMA_API_KEY", "--",
        ])
        self.assertNotIn("pass_fds", captured[0][1])

    def test_runtime_stream_ignores_ambient_home_override(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            actual_home = Path(temp_dir) / "account-home"
            attacker_home = Path(temp_dir) / "attacker-home"
            actual_stream = actual_home / ".codex" / ".env"
            attacker_stream = attacker_home / ".codex" / ".env"
            actual_stream.parent.mkdir(parents=True)
            attacker_stream.parent.mkdir(parents=True)
            os.mkfifo(actual_stream)
            os.mkfifo(attacker_stream)
            command = ["codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request", "-"]
            with (
                patch.dict(
                    os.environ,
                    {"HOME": str(attacker_home), "SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(attacker_stream)},
                    clear=False,
                ),
                patch("ask.skills_sdk.ab_transport_contracts.operator_account_home", return_value=actual_home),
            ):
                self.assertTrue(is_actual_opaque_env_reference(str(actual_stream)))
                self.assertFalse(is_actual_opaque_env_reference(str(attacker_stream)))
                with self.assertRaisesRegex(ValueError, "operator-approved opaque environment stream"):
                    _execution_argv_for_run(command)


if __name__ == "__main__":
    unittest.main()
