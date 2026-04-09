import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import route_skills


class _RouterStub:
    def __init__(self, ranked, uncertainty):
        self._ranked = ranked
        self._uncertainty = uncertainty

    def route(self, query, skills, top_k=3):
        _ = (query, skills, top_k)
        return self._ranked, self._uncertainty


class TestAskSkillsRoute(unittest.TestCase):
    def test_route_resolved_contains_contract_fields(self):
        """
        Verify route_skills returns a resolved routing decision containing the expected contract fields when a single high-confidence candidate is available.
        
        Patches:
        - Replaces discovered skill entries with two entries including "reviewer".
        - Uses a router stub that ranks "reviewer" as the sole candidate.
        - Forces catalog parity to report no drift.
        
        Asserts that the result status is "success" and the decision includes:
        - decision_status "resolved"
        - failure_class `None`
        - considered_limit and considered_total equal to the supplied limit
        - considered_truncated `False` and truncated_count `0`
        - a single selected candidate named "reviewer"
        """
        entries = [
            SimpleNamespace(
                name="auth-check",
                source_dir=REPO_ROOT / "auth" / "auth-check",
                category="auth",
                description="Handle auth checks.",
            ),
            SimpleNamespace(
                name="reviewer",
                source_dir=REPO_ROOT / "product" / "reviewer",
                category="product",
                description="Review code changes.",
            ),
        ]
        ranked = [
            SimpleNamespace(
                skill_name="reviewer",
                skill_path="product/reviewer",
                confidence=0.94,
                rationale=["keyword overlap=2"],
                risk_tier="low",
            )
        ]

        with patch("ask.commands.skills.discover_skill_entries", return_value=entries):
            with patch("ask.commands.skills._load_builder_module", return_value=_RouterStub(ranked, [])):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "review this change", top_k=1, considered_limit=2)

        self.assertEqual(result.status, "success")
        decision = result.data["decision"]
        self.assertEqual(decision["decision_status"], "resolved")
        self.assertEqual(decision["failure_class"], None)
        self.assertEqual(decision["considered_limit"], 2)
        self.assertEqual(decision["considered_total"], 2)
        self.assertFalse(decision["considered_truncated"])
        self.assertEqual(decision["truncated_count"], 0)
        self.assertEqual(len(decision["selected_candidates"]), 1)
        self.assertEqual(decision["selected_candidates"][0]["name"], "reviewer")

    def test_route_reports_unresolved_ambiguity(self):
        """
        Verify that routing reports an unresolved ambiguity when two similarly scored low-risk candidates are returned.
        
        Patches discovery, router builder and catalog parity to produce two candidate entries with close confidence scores and an uncertainty marker `["top_candidates_close_score"]`. Asserts the result is an error with `decision_status` "unresolved_ambiguity", `failure_class` "AMBIGUITY_UNRESOLVED", an `ambiguity_set` containing both candidates, and that `operator_action` suggests narrowing the request.
        """
        entries = [
            SimpleNamespace(
                name="alpha",
                source_dir=REPO_ROOT / "auth" / "alpha",
                category="auth",
                description="Alpha route.",
            ),
            SimpleNamespace(
                name="beta",
                source_dir=REPO_ROOT / "backend" / "beta",
                category="backend",
                description="Beta route.",
            ),
        ]
        ranked = [
            SimpleNamespace(
                skill_name="alpha",
                skill_path="auth/alpha",
                confidence=0.81,
                rationale=["keyword overlap=1"],
                risk_tier="low",
            ),
            SimpleNamespace(
                skill_name="beta",
                skill_path="backend/beta",
                confidence=0.79,
                rationale=["keyword overlap=1"],
                risk_tier="low",
            ),
        ]
        with patch("ask.commands.skills.discover_skill_entries", return_value=entries):
            with patch(
                "ask.commands.skills._load_builder_module",
                return_value=_RouterStub(ranked, ["top_candidates_close_score"]),
            ):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "help me pick one", top_k=2, considered_limit=5)

        self.assertEqual(result.status, "error")
        decision = result.data["decision"]
        self.assertEqual(decision["decision_status"], "unresolved_ambiguity")
        self.assertEqual(decision["failure_class"], "AMBIGUITY_UNRESOLVED")
        self.assertEqual(len(decision["ambiguity_set"]), 2)
        self.assertIn("Narrow the request", decision["operator_action"])

    def test_route_reports_degraded_no_candidates(self):
        entries = [
            SimpleNamespace(
                name="alpha",
                source_dir=REPO_ROOT / "auth" / "alpha",
                category="auth",
                description="Alpha route.",
            )
        ]

        with patch("ask.commands.skills.discover_skill_entries", return_value=entries):
            with patch("ask.commands.skills._load_builder_module", return_value=_RouterStub([], [])):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "no match expected", top_k=1, considered_limit=5)

        self.assertEqual(result.status, "error")
        decision = result.data["decision"]
        self.assertEqual(decision["decision_status"], "degraded_no_candidates")
        self.assertEqual(decision["failure_class"], "NO_ELIGIBLE_CANDIDATES")


if __name__ == "__main__":
    unittest.main()
