#!/usr/bin/env python3
"""Tests for deterministic skill router and schema contracts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from router_controls import resolve_rollout_mode
from skill_catalog import discover_skills, load_catalog
from skill_router import build_route_event, route
from skill_router_schema import Candidate, build_router_result, validate_router_result


def _write_skill(path: Path, name: str, description: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {name}",
                f"description: {description}",
                "---",
                "",
                f"# {name}",
            ]
        ),
        encoding="utf-8",
    )


def _write_fixture_skills(root: Path) -> None:
    _write_skill(
        root / "security" / "security-threat-model",
        "security-threat-model",
        "Threat model repositories and identify abuse paths.",
    )
    _write_skill(
        root / "github" / "gh-workflow",
        "gh-workflow",
        "Manage GitHub pull requests and review workflow.",
    )
    _write_skill(
        root / "frontend" / "interface-craft",
        "interface-craft",
        "Build polished React UI with motion and interaction quality.",
    )
    _write_skill(
        root / "frontend" / "frontend-ui-design",
        "frontend-ui-design",
        "Create production-ready design systems and React UI components.",
    )
    _write_skill(
        root / "product" / "ui-ux-creative-coding",
        "ui-ux-creative-coding",
        "Create polished motion-rich UI implementation artifacts.",
    )
    _write_skill(
        root / "product" / "brainstorming",
        "brainstorming",
        "Explore feature scope and ambiguous product options.",
    )


class SkillRouterTests(unittest.TestCase):
    def test_explicit_mention_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "github" / "gh-workflow", "gh-workflow", "Manage GitHub lifecycle and CI diagnosis.")
            _write_skill(root / "product" / "brainstorming", "brainstorming", "Explore feature options before planning.")

            skills = discover_skills(root)
            candidates, _reasons = route("please run gh-workflow now", skills, top_k=3)

            self.assertGreaterEqual(len(candidates), 1)
            self.assertEqual(candidates[0].skill_name, "gh-workflow")

    def test_phrase_match_boosts_dashed_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(
                root / "harness-engineering",
                "harness-engineering",
                "Route Harness Engineering lifecycle and session-evidence requests.",
            )
            _write_skill(
                root / "github" / "gh-address-comments",
                "gh-address-comments",
                "Address actionable GitHub pull request review feedback.",
            )

            skills = discover_skills(root)
            candidates, _reasons = route(
                "plan a harness engineering change and then implement it",
                skills,
                top_k=2,
            )

            self.assertGreaterEqual(len(candidates), 1)
            self.assertEqual(candidates[0].skill_name, "harness-engineering")
            self.assertIn("skill phrase match", candidates[0].rationale)

    def test_routing_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "frontend" / "interface-craft", "interface-craft", "Build polished React interfaces.")
            _write_skill(root / "frontend" / "frontend-ui-design", "frontend-ui-design", "Create production ready UI systems.")

            skills = discover_skills(root)
            first, _reasons1 = route("help me build polished react ui", skills, top_k=3)
            second, _reasons2 = route("help me build polished react ui", skills, top_k=3)

            self.assertEqual(
                [c.skill_name for c in first],
                [c.skill_name for c in second],
            )
            self.assertEqual(
                [c.confidence for c in first],
                [c.confidence for c in second],
            )

    def test_schema_forbids_raw_prompt_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "github" / "gh-workflow", "gh-workflow", "Manage pull requests and issues.")

            skills = discover_skills(root)
            candidates, reasons = route("review github pull request comments", skills, top_k=3)
            payload = build_router_result(
                query="review github pull request comments",
                actor_type="human",
                policy_mode="observe_only",
                catalog_version="test",
                candidates=candidates,
                uncertainty_reasons=reasons,
            )

            issues = validate_router_result(payload, fail_on_sensitive_fields=True)
            self.assertEqual(issues, [])
            self.assertNotIn("prompt", payload)
            self.assertNotIn("prompt_text", payload)
            self.assertIn("prompt_hash", payload)

    def test_schema_rejects_case_variant_forbidden_fields(self) -> None:
        """Mixed-case forbidden keys like 'Prompt' must be caught."""
        base = {
            "schema_version": "1.0",
            "catalog_version": "abc123",
            "actor_type": "human",
            "policy_mode": "observe_only",
            "policy_decision": "suggest",
            "requires_clarification": False,
            "prompt_hash": "deadbeef",
            "uncertainty_reasons": [],
            "top_candidates": [],
        }
        for bad_key in ("Prompt", "PROMPT", "Raw_Prompt", "RAW_PROMPT", "Objective"):
            with self.subTest(bad_key=bad_key):
                payload = {**base, bad_key: "raw text that should be blocked"}
                issues = validate_router_result(payload, fail_on_sensitive_fields=True)
                self.assertIn("forbidden raw prompt/objective keys present", issues)

    def test_agent_observe_only_requires_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "misc" / "brainstorming", "brainstorming", "Explore ambiguous feature ideas.")
            skills = discover_skills(root)
            candidates, reasons = route("make this better", skills, top_k=3)
            payload = build_router_result(
                query="make this better",
                actor_type="agent",
                policy_mode="observe_only",
                catalog_version="test",
                candidates=candidates,
                uncertainty_reasons=reasons,
            )
            self.assertTrue(payload["requires_clarification"])
            self.assertEqual(payload["policy_decision"], "suggest_only")

    def test_agent_co_pilot_suggests_when_confident_low_risk(self) -> None:
        payload = build_router_result(
            query="help improve CI reliability",
            actor_type="agent",
            policy_mode="co_pilot",
            catalog_version="test",
            candidates=[
                Candidate(
                    skill_name="gh-workflow",
                    skill_path="github/gh-workflow",
                    confidence=0.75,
                    rationale=["keyword overlap=3"],
                    risk_tier="low",
                )
            ],
            uncertainty_reasons=[],
        )
        self.assertFalse(payload["requires_clarification"])
        self.assertEqual(payload["policy_decision"], "suggest")

    def test_uncertainty_reasons_present_for_multi_intent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "github" / "gh-workflow", "gh-workflow", "Manage pull requests and issues.")
            _write_skill(root / "product" / "brainstorming", "brainstorming", "Explore feature scope and options.")
            skills = discover_skills(root)
            candidates, reasons = route("review PR and brainstorm roadmap", skills, top_k=3)
            payload = build_router_result(
                query="review PR and brainstorm roadmap",
                actor_type="human",
                policy_mode="observe_only",
                catalog_version="test",
                candidates=candidates,
                uncertainty_reasons=reasons,
            )
            self.assertIn("possible_multi_intent", payload["uncertainty_reasons"])
            self.assertTrue(payload["requires_clarification"])

    def test_catalog_strict_mode_raises_on_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "a" / "dup", "same-skill", "First description long enough for quality checks.")
            _write_skill(root / "b" / "dup2", "same-skill", "Second description long enough for quality checks.")
            with self.assertRaises(ValueError):
                load_catalog(root, strict=True)

    def test_route_event_contains_guardrail_fields(self) -> None:
        payload = {
            "schema_version": "1.0",
            "catalog_version": "abc123",
            "actor_type": "agent",
            "policy_mode": "co_pilot",
            "policy_decision": "confirmation_required",
            "requires_clarification": True,
            "uncertainty_reasons": ["possible_multi_intent"],
            "prompt_hash": "deadbeef",
            "top_candidates": [
                {
                    "skill_name": "gh-workflow",
                    "skill_path": "github/gh-workflow",
                    "confidence": 0.9,
                    "confidence_band": "high",
                    "risk_tier": "medium",
                    "rationale": ["keyword overlap=3"],
                }
            ],
        }
        event = build_route_event(result=payload, selected_rank=2, correction_latency_ms=1800)
        self.assertEqual(event["top1_skill"], "gh-workflow")
        self.assertFalse(event["top1_chosen"])
        self.assertTrue(event["override_regret_flag"])

    def test_control_precedence_kill_switch_overrides_active(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            controls = Path(tmp)
            (controls / "rollout-mode.txt").write_text("active", encoding="utf-8")
            (controls / "kill-switch.txt").write_text("on", encoding="utf-8")
            resolution = resolve_rollout_mode(controls, "autopilot")
            self.assertEqual(resolution.effective_mode, "observe_only")
            self.assertEqual(resolution.reason, "kill_switch")

    def test_fixture_file_is_valid_json(self) -> None:
        fixture_path = Path(__file__).resolve().parent / "test_skill_router_fixtures.json"
        content = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertTrue(isinstance(content, list))
        self.assertGreaterEqual(len(content), 1)

    def test_fixture_cases_are_exercised(self) -> None:
        fixture_path = Path(__file__).resolve().parent / "test_skill_router_fixtures.json"
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_fixture_skills(root)
            skills = discover_skills(root)

            for fixture in fixtures:
                query = fixture["query"]
                candidates, reasons = route(query, skills, top_k=3)

                with self.subTest(fixture=fixture["id"]):
                    self.assertGreaterEqual(len(candidates), 1)

                    expected_top = fixture.get("expected_top")
                    if expected_top:
                        self.assertEqual(candidates[0].skill_name, expected_top)

                    expected_any_of = fixture.get("expected_any_of")
                    if expected_any_of:
                        self.assertIn(candidates[0].skill_name, expected_any_of)

                    if fixture.get("expect_requires_clarification_for_agent"):
                        payload = build_router_result(
                            query=query,
                            actor_type="agent",
                            policy_mode="observe_only",
                            catalog_version="test",
                            candidates=candidates,
                            uncertainty_reasons=reasons,
                        )
                        self.assertTrue(payload["requires_clarification"])

                    expected_uncertainty_reason = fixture.get("expect_uncertainty_reason")
                    if expected_uncertainty_reason:
                        self.assertIn(expected_uncertainty_reason, reasons)


if __name__ == "__main__":
    unittest.main()
