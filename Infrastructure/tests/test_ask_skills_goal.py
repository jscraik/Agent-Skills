import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import _skill_audit_target, goal_skills, improve_skills  # noqa: E402
from ask.envelope import CallResult  # noqa: E402


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


def _proof_result(handle: str, status: str = "pass") -> CallResult:
    result = CallResult()
    result.status = "success" if status == "pass" else "error"
    result.data["proof"] = {
        "schema_version": "command-handle-proof.v1",
        "handle": handle,
        "status": status,
        "gates": {
            "resolver": True,
            "generated_command_handle_check": True,
            "workspace_command_handle_exists": True,
            "codex_user_link": False,
            "agents_user_link": True,
            "codex_user_command_handle_exists": False,
            "agents_user_command_handle_exists": True,
        },
        "gate_policy": {
            "required": [
                "resolver",
                "generated_command_handle_check",
                "workspace_command_handle_exists",
            ],
            "user_runtime_any_of": [
                "codex_user_link",
                "agents_user_link",
            ],
        },
    }
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

    def test_improve_resolved_returns_capability_and_proof_status(self) -> None:
        route_decision = {
            "decision_status": "resolved",
            "policy_identity": "abc123def4567890",
            "selected_candidates": [
                {
                    "candidate_id": "skill:autofix",
                    "candidate_type": "skill",
                    "name": "autofix",
                    "path": "Skills/agent-ops/autofix/SKILL.md",
                    "confidence": 0.91,
                    "rationale": ["Matches PR review feedback cleanup."],
                }
            ],
            "considered_candidates": [],
        }
        with (
            patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)),
            patch("ask.commands.skills.skills_proof", return_value=_proof_result("autofix")),
        ):
            result = improve_skills(REPO_ROOT, "fix PR review comments", top_k=3, considered_limit=20)

        self.assertEqual(result.status, "success")
        improvement = result.data["improvement"]
        self.assertEqual(improvement["schema_version"], "skill-improvement-recommendation.v1")
        self.assertEqual(improvement["status"], "resolved")
        self.assertEqual(improvement["recommended_capability"]["handle"], "autofix")
        self.assertEqual(improvement["reachability"]["status"], "pass")
        self.assertEqual(improvement["reachability"]["proof_status"], "pass")
        self.assertTrue(improvement["reachability"]["required_gates_passed"])
        self.assertTrue(improvement["reachability"]["user_runtime_ready"])
        self.assertEqual(
            improvement["next_command"],
            "./bin/ask skills proof autofix --json --robot",
        )

    def test_improve_unresolved_preserves_disambiguation(self) -> None:
        route_decision = {
            "decision_status": "unresolved_ambiguity",
            "policy_identity": "abc123def4567890",
            "failure_class": "AMBIGUITY_UNRESOLVED",
            "operator_action": "Narrow request.",
            "selected_candidates": [],
            "considered_candidates": [],
            "ambiguity_set": [
                {"name": "x", "path": "backend/x", "confidence": 0.81},
            ],
        }
        with patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)):
            result = improve_skills(REPO_ROOT, "help me pick", top_k=3, considered_limit=20)

        self.assertEqual(result.status, "error")
        improvement = result.data["improvement"]
        self.assertEqual(improvement["status"], "blocked")
        self.assertEqual(improvement["recommended_capability"], None)
        self.assertEqual(improvement["agent_summary"], "Narrow request.")
        self.assertIn("skills goal", improvement["next_command"])

    def test_improve_falls_back_to_command_handle_descriptions(self) -> None:
        route_decision = {
            "decision_status": "unresolved_ambiguity",
            "policy_identity": "abc123def4567890",
            "failure_class": "AMBIGUITY_UNRESOLVED",
            "operator_action": "Narrow request.",
            "selected_candidates": [],
            "considered_candidates": [],
            "ambiguity_set": [],
        }
        handles = {
            "handles": [
                {
                    "handle": "autofix",
                    "kind": "skill",
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                    "owner": "agent-ops",
                    "description": "Fix PR review feedback and unresolved review comments.",
                    "invoke_via": "agent-ops",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                }
            ]
        }
        with (
            patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)),
            patch("ask.commands.skills.handles_report", return_value=handles),
            patch("ask.commands.skills.skills_proof", return_value=_proof_result("autofix")),
        ):
            result = improve_skills(
                REPO_ROOT,
                "make agents better at fixing PR review comments",
                top_k=3,
                considered_limit=20,
            )

        self.assertEqual(result.status, "success")
        improvement = result.data["improvement"]
        self.assertEqual(improvement["status"], "resolved_with_fallback")
        self.assertEqual(improvement["recommended_capability"]["handle"], "autofix")
        self.assertIn("fallback command-handle description match", improvement["why"])

    def test_improve_fallback_accepts_exact_single_token_handle(self) -> None:
        route_decision = {
            "decision_status": "unresolved_ambiguity",
            "policy_identity": "abc123def4567890",
            "failure_class": "AMBIGUITY_UNRESOLVED",
            "operator_action": "Narrow request.",
            "selected_candidates": [],
            "considered_candidates": [],
            "ambiguity_set": [],
        }
        handles = {
            "handles": [
                {
                    "handle": "autofix",
                    "kind": "skill",
                    "command_handle_path": ".agents/skills/autofix/SKILL.md",
                    "owner": "agent-ops",
                    "description": "Fix PR review feedback and unresolved review comments.",
                    "invoke_via": "agent-ops",
                    "source_path": "Skills/agent-ops/autofix/SKILL.md",
                }
            ]
        }
        with (
            patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)),
            patch("ask.commands.skills.handles_report", return_value=handles),
            patch("ask.commands.skills.skills_proof", return_value=_proof_result("autofix")),
        ):
            result = improve_skills(REPO_ROOT, "autofix", top_k=3, considered_limit=20)

        self.assertEqual(result.status, "success")
        improvement = result.data["improvement"]
        self.assertEqual(improvement["status"], "resolved_with_fallback")
        self.assertEqual(improvement["recommended_capability"]["handle"], "autofix")
        self.assertIn("matched terms=autofix", improvement["why"])

    def test_skill_audit_target_normalizes_absolute_source_path(self) -> None:
        resolution = {
            "source_path": str(REPO_ROOT / "Skills" / "agent-ops" / "autofix" / "SKILL.md"),
        }

        self.assertEqual(
            _skill_audit_target(REPO_ROOT, resolution),
            "Skills/agent-ops/autofix",
        )

    def test_skill_audit_target_rejects_outside_repo_path(self) -> None:
        resolution = {"source_path": "/tmp/outside-repo/SKILL.md"}

        self.assertEqual(_skill_audit_target(REPO_ROOT, resolution), None)

    def test_improve_does_not_bypass_catalog_parity_block(self) -> None:
        route_decision = {
            "decision_status": "blocked_catalog_parity",
            "policy_identity": "abc123def4567890",
            "failure_class": "CATALOG_PARITY_DRIFT",
            "operator_action": "Run catalog doctor.",
            "selected_candidates": [],
            "considered_candidates": [],
        }
        handles = {
            "handles": [
                {
                    "handle": "autofix",
                    "description": "Fix PR review feedback and unresolved review comments.",
                }
            ]
        }
        with (
            patch("ask.commands.skills.route_skills", return_value=_route_result(route_decision)),
            patch("ask.commands.skills.handles_report", return_value=handles),
        ):
            result = improve_skills(
                REPO_ROOT,
                "make agents better at fixing PR review comments",
                top_k=3,
                considered_limit=20,
            )

        self.assertEqual(result.status, "error")
        improvement = result.data["improvement"]
        self.assertEqual(improvement["status"], "blocked")
        self.assertEqual(improvement["recommended_capability"], None)


if __name__ == "__main__":
    unittest.main()
