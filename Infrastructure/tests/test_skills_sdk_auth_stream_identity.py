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
from ask.skills_sdk.ab_transport_contracts import is_actual_opaque_env_reference, is_opaque_env_reference  # noqa: E402


class TestSkillsSdkAuthStreamIdentity(unittest.TestCase):
    @staticmethod
    def _catalog_payload() -> dict[str, object]:
        return {
            "result_class": "pass",
            "network_accessed": True,
            "http_status": 200,
            "catalog_digest": f"sha256:{'a' * 64}",
            "matched_model": "minimax-m2.7:cloud",
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
                patch("ask.skills_sdk.ab_transport_contracts.Path.home", return_value=home),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"),
            ):
                auth = _approved_cloud_auth_fact("minimax-m2.7:cloud")
                env_file.unlink()
                os.mkfifo(env_file)
                fact = _cloud_catalog_fact(
                    "minimax-m2.7:cloud", Path("/mock/oss-cloud.config.toml"), auth,
                    lambda _command: subprocess.CompletedProcess(
                        ["op", "run"], 0, stdout=json.dumps(self._catalog_payload()), stderr="",
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
                "auth_source": "op_fifo",
                "auth_stream_identity_digest": "sha256:" + "a" * 64,
            }
            with (
                patch.dict(os.environ, {"SKILLS_SDK_OSS_CLOUD_ENV_FILE": str(env_file)}, clear=True),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"),
            ):
                fact = _cloud_catalog_fact(
                    "minimax-m2.7:cloud",
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
                patch("ask.skills_sdk.ab_transport_contracts.Path.home", return_value=home),
                patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"),
            ):
                auth = _approved_cloud_auth_fact("minimax-m2.7:cloud")
                fact = _cloud_catalog_fact(
                    "minimax-m2.7:cloud",
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
            patch("ask.skills_sdk.eval_ab_preflight.shutil.which", return_value="/mock/bin/op"),
        ):
            auth = _approved_cloud_auth_fact("minimax-m2.7:cloud")
            with self.assertRaisesRegex(ValueError, "operator-approved opaque environment stream"):
                _execution_argv_for_run(command)
        self.assertEqual(auth["status"], "blocked")

    def test_receipt_only_stream_marker_is_never_a_runtime_path(self) -> None:
        marker = "<operator-approved-opaque-env-stream>"
        self.assertTrue(is_opaque_env_reference(marker))
        self.assertFalse(is_actual_opaque_env_reference(marker))

    def test_recorded_runner_argv_rejects_receipt_only_stream_marker(self) -> None:
        command = ["codex", "exec", "--profile", "oss-cloud", "--ask-for-approval", "on-request", "-"]
        execution = ["op", "run", "--env-file", "<operator-approved-opaque-env-stream>", "--", *command]
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
            with patch("ask.skills_sdk.ab_transport_contracts.Path.home", return_value=home):
                self.assertFalse(is_actual_opaque_env_reference(str(home / ".codex" / ".env")))


if __name__ == "__main__":
    unittest.main()
