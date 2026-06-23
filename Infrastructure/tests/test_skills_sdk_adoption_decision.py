import json
import sys
import tempfile
import unittest
from pathlib import Path


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
        trust_receipt = {
            "schema_version": "skills-sdk.trust-decision-receipt.v0",
            "status": "preview",
            "decision": "trust",
            "package_digest": package["package_digest"],
        }
        harness_root = REPO_ROOT / ".harness" / "tmp"
        harness_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=harness_root) as temp_dir:
            trust_path = Path(temp_dir) / "trust-receipt.json"
            trust_path.write_text(json.dumps(trust_receipt), encoding="utf-8")

            receipt = build_adoption_decision_receipt(
                REPO_ROOT,
                source=VALID_SKILL,
                trust_receipt_path=str(trust_path.relative_to(REPO_ROOT)),
            )

        self.assertEqual(receipt["status"], "ready")
        self.assertEqual(receipt["blockers"], [])
        self.assertEqual(receipt["trust_decision"], "trust")
        self.assertFalse(receipt["command_execution_performed"])


if __name__ == "__main__":
    unittest.main()
