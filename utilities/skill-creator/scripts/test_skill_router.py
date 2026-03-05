#!/usr/bin/env python3
"""Tests for deterministic skill router and schema contracts."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skill_router import discover_skills, route
from skill_router_schema import build_router_result, validate_router_result


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


class SkillRouterTests(unittest.TestCase):
    def test_explicit_mention_wins(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "github" / "gh-fix-ci", "gh-fix-ci", "Fix failing GitHub Actions CI checks.")
            _write_skill(root / "product" / "brainstorming", "brainstorming", "Explore feature options before planning.")

            skills = discover_skills(root)
            candidates = route("please run gh-fix-ci now", skills, top_k=3)

            self.assertGreaterEqual(len(candidates), 1)
            self.assertEqual(candidates[0].skill_name, "gh-fix-ci")

    def test_routing_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "frontend" / "interface-craft", "interface-craft", "Build polished React interfaces.")
            _write_skill(root / "frontend" / "frontend-ui-design", "frontend-ui-design", "Create production ready UI systems.")

            skills = discover_skills(root)
            first = route("help me build polished react ui", skills, top_k=3)
            second = route("help me build polished react ui", skills, top_k=3)

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
            candidates = route("review github pull request comments", skills, top_k=3)
            payload = build_router_result(
                query="review github pull request comments",
                actor_type="human",
                policy_mode="observe_only",
                catalog_version="test",
                candidates=candidates,
            )

            issues = validate_router_result(payload, fail_on_sensitive_fields=True)
            self.assertEqual(issues, [])
            self.assertNotIn("prompt", payload)
            self.assertNotIn("prompt_text", payload)
            self.assertIn("prompt_hash", payload)

    def test_agent_observe_only_requires_clarification(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(root / "misc" / "brainstorming", "brainstorming", "Explore ambiguous feature ideas.")
            skills = discover_skills(root)
            candidates = route("make this better", skills, top_k=3)
            payload = build_router_result(
                query="make this better",
                actor_type="agent",
                policy_mode="observe_only",
                catalog_version="test",
                candidates=candidates,
            )
            self.assertTrue(payload["requires_clarification"])
            self.assertEqual(payload["policy_decision"], "suggest_only")

    def test_fixture_file_is_valid_json(self) -> None:
        fixture_path = Path(__file__).resolve().parent / "test_skill_router_fixtures.json"
        content = json.loads(fixture_path.read_text(encoding="utf-8"))
        self.assertTrue(isinstance(content, list))
        self.assertGreaterEqual(len(content), 1)


if __name__ == "__main__":
    unittest.main()
