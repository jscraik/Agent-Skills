from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.evidence_status import (  # noqa: E402
    EvidenceStatusError,
    QaDispatchRequest,
    build_evidence_status_receipt,
    build_qa_dispatch_record,
)
from helpers.schema_validator import _validate_schema_subset  # noqa: E402


SCHEMA_PATH = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/evidence-status.v1.schema.json"


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


class TestSkillsSdkEvidenceStatus(unittest.TestCase):
    def test_local_build_isolated_from_downstream_blockers(self) -> None:
        blocked_lane = {
            "id": "acceptance",
            "status": "blocked",
            "blockers": [{"id": "receipt_missing", "message": "receipt is missing", "evidence": []}],
            "evidence": [],
        }
        integration_lane = {
            "id": "integration",
            "status": "blocked",
            "blockers": [{"id": "hosted_not_run", "message": "hosted lane not run", "evidence": []}],
            "evidence": [],
        }
        with (
            mock.patch("ask.skills_sdk.evidence_status._build_acceptance_lane", return_value=blocked_lane),
            mock.patch("ask.skills_sdk.evidence_status._build_integration_lane", return_value=integration_lane),
        ):
            receipt = build_evidence_status_receipt(REPO_ROOT, mode="local-build")

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["selected_lane"], "local-build")
        self.assertEqual(receipt["lanes"][0]["status"], "pass")
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(len(receipt["ignored_blockers"]), 2)

    def test_required_acceptance_mode_is_fail_closed_when_receipt_is_missing(self) -> None:
        receipt = build_evidence_status_receipt(REPO_ROOT, mode="all", required_mode="acceptance")

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["selected_lane"], "acceptance")
        self.assertEqual(receipt["blockers"][0]["id"], "stabilization_receipt_missing")

    def test_acceptance_receipt_cannot_escape_source_worktree(self) -> None:
        receipt = build_evidence_status_receipt(
            REPO_ROOT,
            mode="acceptance",
            stabilization_receipt_path="/private/tmp/external-receipt.json",
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["blockers"][0]["id"], "stabilization_receipt_outside_source")

    def test_qa_dispatch_record_is_controller_owned_and_revision_bound(self) -> None:
        record = build_qa_dispatch_record(REPO_ROOT, QaDispatchRequest(source_revision="a" * 40))

        self.assertEqual(record["schema_version"], "skills-sdk.qa-dispatch-record.v1")
        self.assertTrue(record["controller_owned"])
        self.assertFalse(record["dispatch_performed"])
        self.assertEqual(record["state"], "not_requested")
        self.assertEqual(record["source_revision"], "a" * 40)

        with self.assertRaisesRegex(EvidenceStatusError, "source_revision"):
            build_qa_dispatch_record(
                REPO_ROOT,
                QaDispatchRequest(source_revision="b" * 40, expected_revision="a" * 40),
            )

    def test_status_receipt_matches_schema_and_cli_envelope(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        receipt = build_evidence_status_receipt(REPO_ROOT, mode="local-build")
        _validate_schema_subset(schema, receipt, {"evidence-status": schema})

        process = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "evidence",
                "status",
                "--mode",
                "local-build",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["data"]["skills_sdk_evidence_status"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
