import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import call, patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.skills import route_skills  # noqa: E402


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

        with patch(
            "ask.commands.skills.discover_catalog_entries",
            side_effect=lambda advanced=False: entries,
        ) as mocked_discover:
            with patch("ask.commands.skills._load_builder_module", return_value=_RouterStub(ranked, [])):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "review this change", top_k=1, considered_limit=2)

        self.assertEqual(
            mocked_discover.call_args_list,
            [call(), call(advanced=True)],
        )
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
        
        Patches discovery, router builder, and catalog parity to produce two candidates with close confidence and an uncertainty marker "top_candidates_close_score", then asserts the result has status "error" and that the decision contains decision_status "unresolved_ambiguity", failure_class "AMBIGUITY_UNRESOLVED", an ambiguity_set with both candidates, and an operator_action recommending narrowing the request.
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
        with patch(
            "ask.commands.skills.discover_catalog_entries",
            side_effect=lambda advanced=False: entries,
        ) as mocked_discover:
            with patch(
                "ask.commands.skills._load_builder_module",
                return_value=_RouterStub(ranked, ["top_candidates_close_score"]),
            ):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "help me pick one", top_k=2, considered_limit=5)

        self.assertEqual(
            mocked_discover.call_args_list,
            [call(), call(advanced=True)],
        )
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

        with patch(
            "ask.commands.skills.discover_catalog_entries",
            side_effect=lambda advanced=False: entries,
        ) as mocked_discover:
            with patch("ask.commands.skills._load_builder_module", return_value=_RouterStub([], [])):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "no match expected", top_k=1, considered_limit=5)

        self.assertEqual(
            mocked_discover.call_args_list,
            [call(), call(advanced=True)],
        )
        self.assertEqual(result.status, "error")
        decision = result.data["decision"]
        self.assertEqual(decision["decision_status"], "degraded_no_candidates")
        self.assertEqual(decision["failure_class"], "NO_ELIGIBLE_CANDIDATES")

    def test_route_uses_advanced_catalog_surface_for_hidden_lane_skills(self):
        entries = [
            SimpleNamespace(
                name="code-review",
                source_dir=REPO_ROOT / "plugins" / "coderabbit" / "skills" / "code-review",
                category="Plugins/coderabbit/skills",
                description="Hidden lane review skill.",
            )
        ]
        ranked = [
            SimpleNamespace(
                skill_name="code-review",
                skill_path="plugins/coderabbit/skills/code-review",
                confidence=0.93,
                rationale=["keyword overlap=2"],
                risk_tier="low",
            )
        ]

        with patch(
            "ask.commands.skills.discover_catalog_entries",
            side_effect=lambda advanced=False: entries,
        ) as mocked_discover:
            with patch("ask.commands.skills._load_builder_module", return_value=_RouterStub(ranked, [])):
                with patch("ask.commands.skills.compute_catalog_parity", return_value={"drift_detected": False}):
                    result = route_skills(REPO_ROOT, "run a code review", top_k=1, considered_limit=5)

        self.assertEqual(
            mocked_discover.call_args_list,
            [call(), call(advanced=True)],
        )
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["decision"]["selected_candidates"][0]["name"], "code-review")

    def test_route_preserves_default_window_while_adding_advanced_only_lanes(self):
        """
        Verifies that advanced-only (hidden-lane) skills are added to the total considered set while the router still receives the original default window of skills.
        
        Asserts that discover_catalog_entries is called for default and advanced surfaces, the selection is `docs-expert`, `considered_total` reflects inclusion of one advanced-only entry (21), and the router received both a default skill and a hidden-lane skill (`code-review`) in its routing input.
        """
        default_entries = [
            SimpleNamespace(
                name=f"skill-{index:02d}",
                source_dir=REPO_ROOT / "Skills" / "agent-ops" / f"skill-{index:02d}",
                category="Skills/agent-ops",
                description=f"Default skill {index}.",
            )
            for index in range(19)
        ]
        docs_expert = SimpleNamespace(
            name="docs-expert",
            source_dir=REPO_ROOT / "Skills" / "agent-ops" / "docs-expert",
            category="Skills/agent-ops",
            description="Audit and update repository documentation.",
        )
        default_entries.append(docs_expert)
        advanced_entries = list(default_entries) + [
            SimpleNamespace(
                name="code-review",
                source_dir=REPO_ROOT / "Plugins" / "coderabbit" / "skills" / "code-review",
                category="Plugins/coderabbit/skills",
                description="Hidden review lane.",
            ),
        ]

        class _CapturingRouterStub(_RouterStub):
            def __init__(self, ranked, uncertainty):
                """
                Initialize a capturing router stub that returns the provided ranked candidates and uncertainty while recording route calls.
                
                Parameters:
                    ranked (list): Pre-ranked candidate objects to be returned by route().
                    uncertainty (list): Uncertainty indicators to be returned by route().
                """
                super().__init__(ranked, uncertainty)
                self.calls = []

            def route(self, query, skills, top_k=3):
                """
                Capture the names of the provided skills and delegate routing to the parent implementation.
                
                Parameters:
                    query: The routing query object passed through to the parent router.
                    skills: An iterable of skill objects; each object must have a `name` attribute. The method records these names in `self.calls`.
                    top_k (int): Maximum number of top candidates to request from the parent router.
                
                Returns:
                    tuple: A pair (ranked_candidates, uncertainty_indicators) as returned by the superclass `route` method.
                """
                self.calls.append([skill.name for skill in skills])
                return super().route(query, skills, top_k=top_k)

        router_stub = _CapturingRouterStub(
            [
                SimpleNamespace(
                    skill_name="docs-expert",
                    skill_path="Skills/agent-ops/docs-expert",
                    confidence=0.95,
                    rationale=["keyword overlap=2"],
                    risk_tier="low",
                )
            ],
            [],
        )

        def _discover(*, advanced=False):
            """
            Selects which catalog entries list to return based on the `advanced` flag.
            
            Parameters:
                advanced (bool): If True, return the advanced catalog entries set; otherwise return the default set.
            
            Returns:
                list: `default_entries` when `advanced` is False, `advanced_entries` when `advanced` is True.
            """
            return advanced_entries if advanced else default_entries

        with patch("ask.commands.skills.discover_catalog_entries", side_effect=_discover) as mocked_discover:
            with patch("ask.commands.skills._load_builder_module", return_value=router_stub):
                with patch(
                    "ask.commands.skills.compute_catalog_parity",
                    return_value={"drift_detected": False},
                ) as mocked_parity:
                    result = route_skills(REPO_ROOT, "audit the README", top_k=1, considered_limit=20)

        self.assertEqual(
            mocked_discover.call_args_list,
            [call(), call(advanced=True)],
        )
        self.assertEqual(result.status, "success")
        self.assertEqual(result.data["decision"]["selected_candidates"][0]["name"], "docs-expert")
        self.assertEqual(result.data["decision"]["considered_total"], 21)
        self.assertNotIn("route_considered_total", mocked_parity.call_args.kwargs)
        self.assertIn("docs-expert", router_stub.calls[0])
        self.assertIn("code-review", router_stub.calls[0])


if __name__ == "__main__":
    unittest.main()
