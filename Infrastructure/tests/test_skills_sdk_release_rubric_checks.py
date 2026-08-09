from __future__ import annotations

from pathlib import Path
import sys
import unittest

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.release_rubric_checks import evaluate_semantic_requirements  # noqa: E402


def _efficiency_requirements() -> dict[str, object]:
    payload = yaml.safe_load(
        (REPO_ROOT / "Skills" / "agent-ops" / "simplify" / "references" / "evals.yaml").read_text()
    )
    case = next(item for item in payload["cases"] if item["id"] == "edge-efficiency-rubric")
    return next(item for item in case["acceptance"] if item["type"] == "semantic_requirements")


class TestSkillsSdkReleaseRubricChecks(unittest.TestCase):
    def test_efficiency_rubric_accepts_explicit_checked_read_evidence(self) -> None:
        output = (
            "The supplied diff replaces two `store.get(key)` calls with one cached read. "
            "Add a focused test with a call-count assertion."
        )

        self.assertIsNone(evaluate_semantic_requirements(output, _efficiency_requirements()))

    def test_efficiency_rubric_rejects_a_vague_read_claim(self) -> None:
        output = "The store.get call is safe. Add a focused test."

        self.assertEqual(
            evaluate_semantic_requirements(output, _efficiency_requirements()),
            "semantic_requirements failed: reuse_checked_value",
        )


if __name__ == "__main__":
    unittest.main()
