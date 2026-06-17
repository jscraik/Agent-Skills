#!/usr/bin/env python3
"""Unit tests for command-surface metadata behavior."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch


SCRIPT_DIR = Path(__file__).resolve().parent.parent / "lifecycle-and-sync"
SCRIPT = SCRIPT_DIR / "command_surface.py"


def _load_module() -> ModuleType:
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("command_surface", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load command_surface module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[misc]
    return module


COMMAND_SURFACE = _load_module()


class CommandSurfaceTests(unittest.TestCase):
    def test_wrapper_generation_api_is_absent(self) -> None:
        self.assertFalse(hasattr(COMMAND_SURFACE, "write_command_handles"))
        self.assertFalse(hasattr(COMMAND_SURFACE, "check_command_handles"))
        self.assertFalse(hasattr(COMMAND_SURFACE, "render_skill_command_handle"))
        self.assertFalse(hasattr(COMMAND_SURFACE, "render_openai_yaml"))
        self.assertFalse(hasattr(COMMAND_SURFACE, "_validate_command_handle_payload"))

    def test_reviewer_role_serializes_without_removed_wrapper_path(self) -> None:
        reviewer_role = COMMAND_SURFACE.ReviewerRole

        role = reviewer_role(
            handle="skill-inspector",
            kind="reviewer",
            source_path="agents/skill-inspector.toml",
            owner="harness-engineering",
            description="Review skill quality.",
        )

        payload = role.to_dict()
        self.assertEqual(
            payload["source_path"],
            "agents/skill-inspector.toml",
        )
        self.assertNotIn("command_handle_path", payload)
        self.assertNotIn("command_visibility", payload)

    def test_parse_sdk_references_resolves_skills_and_reviewers(self) -> None:
        parse_sdk_references = COMMAND_SURFACE.parse_sdk_references
        original_skill_resolver = COMMAND_SURFACE.resolve_skill_handle
        original_reviewer_resolver = COMMAND_SURFACE.resolve_reviewer_handle

        def fake_skill_resolver(handle: str, **_: object) -> dict[str, object]:
            return {
                "status": "ok",
                "handle": handle,
                "kind": "skill",
                "handle_source": "sdk_flat_registry",
            }

        def fake_reviewer_resolver(handle: str, **_: object) -> dict[str, object]:
            return {
                "status": "ok",
                "handle": "skill-inspector",
                "canonical_handle": "skill-inspector",
                "kind": "reviewer",
                "command_visibility": "reviewer",
            }

        with patch.object(COMMAND_SURFACE, "resolve_skill_handle", fake_skill_resolver), \
             patch.object(COMMAND_SURFACE, "resolve_reviewer_handle", fake_reviewer_resolver):
            parsed = parse_sdk_references(
                "use $skill-builder to validate $he-phase-heartbeat with @skillinspector",
                repo_root_path=Path("."),
            )

        self.assertEqual(parsed["status"], "pass")
        self.assertEqual(parsed["reviewer_mentions"][0]["mention"], "skillinspector")
        self.assertEqual(
            parsed["mention_counts"],
            {"skills": 2, "reviewers": 1, "unresolved": 0},
        )
        self.assertEqual(parsed["skill_mentions"][0]["role"], "sdk_skill")
        self.assertEqual(parsed["skill_mentions"][1]["role"], "sdk_skill")
        self.assertEqual(
            parsed["reviewer_mentions"][0]["resolution"]["canonical_handle"],
            "skill-inspector",
        )

    def test_reviewer_role_metadata_allows_unresolved_source(self) -> None:
        reviewer_role = COMMAND_SURFACE.ReviewerRole

        role = reviewer_role(
            handle="he-work",
            kind="reviewer",
            source_path=None,
            owner="harness-engineering",
            description="Execute a plan.",
        )

        payload = role.to_dict()
        self.assertNotIn("source_path", payload)
        self.assertNotIn("command_handle_path", payload)


if __name__ == "__main__":
    unittest.main()
