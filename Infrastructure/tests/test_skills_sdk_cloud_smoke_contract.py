from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.ab_transport_contracts import CONFIGS_AUTH_WRAPPER, CONFIGS_CODEX_EXEC_WRAPPER  # noqa: E402  # reason: local Infrastructure path bootstrap; issue: PR-386; expires: 2026-12-31; ADR: source-checkout imports
from ask.skills_sdk.cloud_smoke_contract import cloud_smoke_receipt_findings, valid_cloud_smoke_receipt  # noqa: E402  # reason: local Infrastructure path bootstrap; issue: PR-386; expires: 2026-12-31; ADR: source-checkout imports


def _valid_smoke_receipt() -> dict[str, object]:
    return {
        "schema_version": "skills-sdk.oss-cloud-smoke-run.v0", "observed_at": "2026-08-06T12:00:00+00:00",
        "status": "pass", "lane": "oss-cloud", "codex_profile": "oss-cloud",
        "model": "deepseek-v4-flash:0731-cloud", "model_provider": "ollama-cloud",
        "auth_source": "1password_desktop_fifo", "provider_invoked": True,
        "execution_argv": [
            "bash", str(CONFIGS_AUTH_WRAPPER), "--env-file", "<operator-approved-opaque-env-stream>",
            "--require-env", "OLLAMA_API_KEY", "--", "env", "-u", "CODEX_CONFIG_HOME",
            "CODEX_HOME=<isolated-codex-home>", "bash", str(CONFIGS_CODEX_EXEC_WRAPPER),
            "--profile", "oss-cloud", "--strict-config", "-c", 'approval_policy="on-request"',
            "--skip-git-repo-check", "--sandbox", "read-only", "--ephemeral", "--model",
            "deepseek-v4-flash:0731-cloud", "Reply exactly CODEX_OSS_CLOUD_OK",
        ],
        "exit_code": 0, "marker": "CODEX_OSS_CLOUD_OK", "warnings": [], "findings": [],
        "captured_output_safe": True,
        "captured_output_scan": {"status": "passed", "source": "captured_output_scan", "redacted": True},
    }


class TestCloudSmokeContract(unittest.TestCase):
    def test_rejects_raw_output_field_on_an_otherwise_valid_receipt(self) -> None:
        receipt = _valid_smoke_receipt()
        self.assertEqual(cloud_smoke_receipt_findings(receipt), [])

        receipt["stdout"] = "OPENAI_API_KEY=untrusted-child-claim"

        self.assertEqual(cloud_smoke_receipt_findings(receipt), ["unexpected:stdout"])
        self.assertFalse(valid_cloud_smoke_receipt(receipt))
