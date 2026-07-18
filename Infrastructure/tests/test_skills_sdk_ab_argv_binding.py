from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = REPO_ROOT / "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.typed_contracts import validate_ab_run_receipt  # noqa: E402


class TestSkillsSdkAbArgvBinding(unittest.TestCase):
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
