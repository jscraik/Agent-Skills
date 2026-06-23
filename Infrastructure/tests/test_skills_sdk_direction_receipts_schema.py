import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from helpers.schema_validator import _validate_schema_subset  # noqa: E402

from ask.skills_sdk.adoption_decision import build_adoption_decision_receipt  # noqa: E402
from ask.skills_sdk.command_evidence_plan import build_command_evidence_plan_receipt  # noqa: E402
from ask.skills_sdk.knowledge_durability import build_knowledge_durability_receipt  # noqa: E402
from ask.skills_sdk.lifecycle_route_map import build_lifecycle_route_map_receipt  # noqa: E402
from ask.skills_sdk.tessl_score_receipt import build_tessl_score_receipt  # noqa: E402

SCHEMA_DIR = REPO_ROOT / "Infrastructure/config/schemas/skills-sdk"
VALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


class TestSkillsSdkDirectionReceiptsSchema(unittest.TestCase):
    def test_direction_receipts_validate_against_schemas(self) -> None:
        cases = {
            "adoption-decision-receipt.v0.schema.json": build_adoption_decision_receipt(REPO_ROOT, source=VALID_SKILL),
            "command-evidence-plan-receipt.v0.schema.json": build_command_evidence_plan_receipt(REPO_ROOT),
            "lifecycle-route-map-receipt.v0.schema.json": build_lifecycle_route_map_receipt(REPO_ROOT),
            "knowledge-durability-receipt.v0.schema.json": self._knowledge_receipt(),
            "tessl-score-receipt.v0.schema.json": self._tessl_score_receipt(),
        }
        schemas = {name: json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8")) for name in cases}

        for schema_name, payload in cases.items():
            with self.subTest(schema=schema_name):
                _validate_schema_subset(schemas[schema_name], payload, schemas)

    def _knowledge_receipt(self) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            skill_dir = repo_root / "Skills/example"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("# Example\n", encoding="utf-8")
            return build_knowledge_durability_receipt(repo_root, skill=str(skill_dir))

    def _tessl_score_receipt(self) -> dict:
        with tempfile.TemporaryDirectory() as temp_dir:
            view_json = Path(temp_dir) / "view.json"
            view_json.write_text(
                json.dumps({
                    "data": {
                        "id": "test-run-id",
                        "attributes": {
                            "status": "completed",
                            "scenarios": [
                                {
                                    "id": "scenario-0",
                                    "path": "scenario-0",
                                    "solutions": [
                                        {"variant": "usage-spec", "assessmentResults": [{"score": 1.0, "max_score": 1.0}]},
                                        {"variant": "baseline", "assessmentResults": [{"score": 0.5, "max_score": 1.0}]},
                                    ],
                                }
                            ],
                        },
                    }
                }),
                encoding="utf-8",
            )
            return build_tessl_score_receipt(REPO_ROOT, view_json=view_json, skill="Skills/test")


if __name__ == "__main__":
    unittest.main()
