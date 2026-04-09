import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import goal_skills
from ask.envelope import CallResult


def _route_result(decision: dict) -> CallResult:
    result = CallResult()
    result.status = "success" if decision.get("decision_status") == "resolved" else "error"
    result.data["decision"] = decision
    return result


class TestAskSkillsGoal(unittest.TestCase):
    def test_goal_resolved_returns_recommendation_and_alternatives(self) -> None:
        route_decision = {
            "decision_status": "resolved",
            "policy_identity": "abc123def4567890",
            "selected_candidates": [
                {"candidate_id": "skill:a", "candidate_type": "skill", "name": "a", "path": "auth/a", "confidence": 0.9, "rationale": ["best"]},
                {"candidate_id": "skill:b", "candidate_type": "skill", "name": "b", "path": "auth/b", "confidence": 0.8, "rationale": ["alt1"]},
                {"candidate_id": "skill:c", "candidate_type": "skill", "name": "c", "path": "auth/c", "confidence": 0.7, "rationale": ["alt2"]},
            ],
            "considered_candidates": [],
        }
        with patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)):
            result = goal_skills(REPO_ROOT, "build auth flow", top_k=3, considered_limit=20)

        self.assertEqual(result.status, "success")
        goal = result.data["goal_decision"]
        self.assertEqual(goal["schema_version"], "goal-decision.v1")
        self.assertEqual(goal["decision_status"], "resolved")
        self.assertEqual(goal["recommended_candidate"]["name"], "a")
        self.assertEqual([c["name"] for c in goal["alternative_candidates"]], ["b", "c"])
        self.assertEqual(goal["failure_class"], None)
        self.assertEqual(goal["operator_action"], None)

    def test_goal_non_success_maps_to_intent_unresolved(self) -> None:
        route_decision = {
            "decision_status": "unresolved_ambiguity",
            "policy_identity": "abc123def4567890",
            "failure_class": "AMBIGUITY_UNRESOLVED",
            "operator_action": "Narrow request.",
            "selected_candidates": [],
            "considered_candidates": [],
            "ambiguity_set": [
                {"name": "x", "path": "backend/x", "confidence": 0.81},
                {"name": "y", "path": "backend/y", "confidence": 0.79},
            ],
        }
        with patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)):
            result = goal_skills(REPO_ROOT, "help me pick", top_k=3, considered_limit=20)

        self.assertEqual(result.status, "error")
        goal = result.data["goal_decision"]
        self.assertEqual(goal["decision_status"], "intent_unresolved")
        self.assertEqual(goal["failure_class"], "INTENT_UNRESOLVED")
        self.assertTrue(goal["disambiguation_prompts"])
        self.assertEqual(goal["operator_action"], "Narrow request.")


if __name__ == "__main__":
    unittest.main()
