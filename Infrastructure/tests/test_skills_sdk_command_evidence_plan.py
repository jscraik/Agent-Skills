import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt  # noqa: E402


class TestSkillsSdkCommandEvidencePlan(unittest.TestCase):
    def test_plans_capability_matrix_commands_without_execution(self) -> None:
        receipt = build_command_evidence_plan_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "planned")
        self.assertGreater(receipt["command_count"], 0)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["command_execution_performed"])
        self.assertTrue(all(command["receipt_required"] for command in receipt["commands"]))
        self.assertTrue(all(command["status"] == "planned" for command in receipt["commands"]))

    def test_blocks_unparseable_command_evidence_refs(self) -> None:
        capability_receipt = {
            "evidence_rows": [
                {
                    "kind": "command",
                    "capability_id": "bad_command",
                    "ref": "./bin/ask sdk status 'unterminated",
                    "reason": "fixture",
                }
            ]
        }

        with patch(
            "ask.skills_sdk.command_evidence_plan.build_capability_evidence_receipt",
            return_value=capability_receipt,
        ):
            receipt = build_command_evidence_plan_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["command_count"], 0)
        self.assertIn("invalid_command_evidence_ref", {item["id"] for item in receipt["blockers"]})

    def test_blocks_non_string_command_evidence_refs(self) -> None:
        capability_receipt = {
            "evidence_rows": [
                {
                    "kind": "command",
                    "capability_id": "bad_command",
                    "ref": None,
                    "reason": "fixture",
                }
            ]
        }

        with patch(
            "ask.skills_sdk.command_evidence_plan.build_capability_evidence_receipt",
            return_value=capability_receipt,
        ):
            receipt = build_command_evidence_plan_receipt(REPO_ROOT)

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["command_count"], 0)
        self.assertIn("invalid_command_evidence_ref", {item["id"] for item in receipt["blockers"]})


if __name__ == "__main__":
    unittest.main()
