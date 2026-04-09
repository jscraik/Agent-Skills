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
    """
    Create a CallResult that wraps a routing decision and sets status based on the decision outcome.
    
    Parameters:
        decision (dict): A routing decision payload containing at least a `decision_status` key.
    
    Returns:
        CallResult: An instance whose `status` is `"success"` when `decision["decision_status"] == "resolved"`, otherwise `"error"`. The original `decision` is stored under `result.data["decision"]`.
    """
    result = CallResult()
    result.status = "success" if decision.get("decision_status") == "resolved" else "error"
    result.data["decision"] = decision
    return result


class TestAskSkillsGoal(unittest.TestCase):
    def test_goal_resolved_returns_recommendation_and_alternatives(self) -> None:
        """
        Verifies that a resolved routing decision yields a goal decision recommending the top candidate and listing the remaining candidates as alternatives.
        
        Patches `route_skills` to return a decision with three selected candidates, calls `goal_skills`, and asserts:
        - `result.status` is `"success"`.
        - `goal_decision.schema_version` is `"goal-decision.v1"` and `decision_status` is `"resolved"`.
        - the first selected candidate is set as `recommended_candidate`.
        - the remaining selected candidates appear in `alternative_candidates` in order.
        - `failure_class` and `operator_action` are `None`.
        """
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
        """
        Verify that a non-resolved routing decision is mapped to an intent-level unresolved goal decision.
        
        The test supplies a routed decision with `decision_status` set to "unresolved_ambiguity" and an ambiguity set. It asserts the produced `CallResult` has status "error", the goal decision's `decision_status` is "intent_unresolved", `failure_class` is remapped to "INTENT_UNRESOLVED", `disambiguation_prompts` is non-empty, and `operator_action` is preserved.
        """
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
