import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.adoption_decision import build_adoption_decision_receipt  # noqa: E402
from ask.skills_sdk.package_build import build_package_digest_receipt  # noqa: E402

VALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


class TestSkillsSdkAdoptionDecision(unittest.TestCase):
    def test_blocks_without_local_trust_receipt(self) -> None:
        receipt = build_adoption_decision_receipt(REPO_ROOT, source=VALID_SKILL)

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("local_trust_decision", {item["id"] for item in receipt["blockers"]})
        self.assertFalse(receipt["mutation_performed"])

    def test_ready_when_trust_receipt_matches_package_digest(self) -> None:
        package = build_package_digest_receipt(REPO_ROOT, source_path=REPO_ROOT / VALID_SKILL, query=VALID_SKILL)
        local_decision_receipt = {
            "schema_version": "skills-sdk.trust-decision-receipt.v0",
            "status": "preview",
            "decision": "trust",
            "package_digest": package["package_digest"],
            "expires_at": "2999-01-01T00:00:00Z",
        }
        with patch(
            "ask.skills_sdk.adoption_decision._load_trust_receipt",
            return_value=(local_decision_receipt, None),
        ), patch(
            "ask.skills_sdk.adoption_decision._build_intake_review_receipt",
            return_value={"status": "pass", "review_items": []},
        ):
            receipt = build_adoption_decision_receipt(
                REPO_ROOT,
                source=VALID_SKILL,
                trust_receipt_path="local-decision-receipt.json",
            )

        self.assertEqual(receipt["status"], "ready")
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["trust_decision"], "trust")
        self.assertFalse(receipt["command_execution_performed"])

    def test_matching_trust_does_not_bypass_human_review(self) -> None:
        package = build_package_digest_receipt(REPO_ROOT, source_path=REPO_ROOT / VALID_SKILL, query=VALID_SKILL)
        local_decision_receipt = {
            "schema_version": "skills-sdk.trust-decision-receipt.v0",
            "status": "preview",
            "decision": "trust",
            "package_digest": package["package_digest"],
            "expires_at": "2999-01-01T00:00:00Z",
        }
        with patch(
            "ask.skills_sdk.adoption_decision._load_trust_receipt",
            return_value=(local_decision_receipt, None),
        ):
            receipt = build_adoption_decision_receipt(
                REPO_ROOT,
                source=VALID_SKILL,
                trust_receipt_path="local-decision-receipt.json",
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("intake_review_preview", {item["id"] for item in receipt["blockers"]})

    def test_review_status_items_block_even_without_block_items(self) -> None:
        package = build_package_digest_receipt(REPO_ROOT, source_path=REPO_ROOT / VALID_SKILL, query=VALID_SKILL)
        local_decision_receipt = {
            "schema_version": "skills-sdk.trust-decision-receipt.v0",
            "status": "preview",
            "decision": "trust",
            "package_digest": package["package_digest"],
            "expires_at": "2999-01-01T00:00:00Z",
        }
        review_receipt = {
            "status": "pass",
            "review_items": [{"id": "permissions", "status": "review"}],
        }
        with patch(
            "ask.skills_sdk.adoption_decision._load_trust_receipt",
            return_value=(local_decision_receipt, None),
        ), patch(
            "ask.skills_sdk.adoption_decision._build_intake_review_receipt",
            return_value=review_receipt,
        ):
            receipt = build_adoption_decision_receipt(
                REPO_ROOT,
                source=VALID_SKILL,
                trust_receipt_path="local-decision-receipt.json",
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("intake_review_preview", {item["id"] for item in receipt["blockers"]})

    def test_expired_trust_receipt_blocks_adoption(self) -> None:
        package = build_package_digest_receipt(REPO_ROOT, source_path=REPO_ROOT / VALID_SKILL, query=VALID_SKILL)
        local_decision_receipt = {
            "schema_version": "skills-sdk.trust-decision-receipt.v0",
            "status": "preview",
            "decision": "trust",
            "package_digest": package["package_digest"],
            "expires_at": "2000-01-01T00:00:00Z",
        }
        with patch(
            "ask.skills_sdk.adoption_decision._load_trust_receipt",
            return_value=(local_decision_receipt, None),
        ), patch(
            "ask.skills_sdk.adoption_decision._build_intake_review_receipt",
            return_value={"status": "pass", "review_items": []},
        ):
            receipt = build_adoption_decision_receipt(
                REPO_ROOT,
                source=VALID_SKILL,
                trust_receipt_path="local-decision-receipt.json",
            )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("local_trust_decision", {item["id"] for item in receipt["blockers"]})

    def test_bad_source_returns_blocked_receipt_without_digest_crash(self) -> None:
        receipt = build_adoption_decision_receipt(REPO_ROOT, source="Infrastructure/tests/fixtures/skills_sdk/no-such-skill")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIsNone(receipt["package_id"])
        self.assertIsNone(receipt["package_digest"])
        self.assertIn("package_identity_built", {item["id"] for item in receipt["blockers"]})
        self.assertTrue(
            all(isinstance(evidence, str) for check in receipt["checks"] for evidence in check["evidence"])
        )


if __name__ == "__main__":
    unittest.main()
