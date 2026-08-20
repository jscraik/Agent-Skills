from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

_transport_contracts = importlib.import_module("ask.skills_sdk.ab_transport_contracts")
_cloud_smoke_contract = importlib.import_module("ask.skills_sdk.cloud_smoke_contract")

CONFIGS_AUTH_WRAPPER = _transport_contracts.CONFIGS_AUTH_WRAPPER
CONFIGS_CODEX_EXEC_WRAPPER = _transport_contracts.CONFIGS_CODEX_EXEC_WRAPPER
cloud_smoke_receipt_findings = _cloud_smoke_contract.cloud_smoke_receipt_findings
valid_cloud_smoke_receipt = _cloud_smoke_contract.valid_cloud_smoke_receipt


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

    def test_rejects_noncanonical_warning_contents(self) -> None:
        receipt = _valid_smoke_receipt()
        receipt["warnings"] = [{"code": "codex_runtime_metadata_fallback", "message": "OPENAI_API_KEY=untrusted"}]

        self.assertEqual(cloud_smoke_receipt_findings(receipt), ["warnings_not_value_blind"])
        self.assertFalse(valid_cloud_smoke_receipt(receipt))

    def test_rejects_unknown_warning_code_with_null_message(self) -> None:
        receipt = _valid_smoke_receipt()
        receipt["warnings"] = [{"code": "OPENAI_API_KEY=untrusted", "message": None}]

        self.assertEqual(cloud_smoke_receipt_findings(receipt), ["warnings_not_value_blind"])
        self.assertFalse(valid_cloud_smoke_receipt(receipt))

    def test_accepts_the_only_known_value_blind_warning(self) -> None:
        receipt = _valid_smoke_receipt()
        receipt["warnings"] = [{
            "code": "codex_runtime_metadata_fallback",
            "message": "Codex reported fallback metadata.",
        }]

        self.assertEqual(cloud_smoke_receipt_findings(receipt), [])
