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


if __name__ == "__main__":
    unittest.main()
