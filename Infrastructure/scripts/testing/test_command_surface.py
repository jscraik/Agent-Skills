#!/usr/bin/env python3
"""Unit tests for generated command-handle rendering."""

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
    def test_generated_handle_includes_portable_source_path_fallback(self) -> None:
        command_handle = getattr(COMMAND_SURFACE, "CommandHandle")
        render_skill_command_handle = getattr(COMMAND_SURFACE, "render_skill_command_handle")
        validate_command_handle_payload = getattr(COMMAND_SURFACE, "_validate_command_handle_payload")

        handle = command_handle(
            handle="he-work",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path="Plugins/harness-engineering/skills/he-work/SKILL.md",
            command_handle_path=".agents/skills/he-work/SKILL.md",
            owner="harness-engineering",
            description="Execute a plan.",
            invoke_via="harness-engineering",
            level="atom",
        )

        body = render_skill_command_handle(handle)

        self.assertIn(
            "Canonical source path: `Plugins/harness-engineering/skills/he-work/SKILL.md`.",
            body,
        )
        self.assertIn("If this is the Agent Skills Kit repo and `./bin/ask` exists", body)
        self.assertIn("Otherwise, load", body)
        self.assertIn("search only the owner skill tree", body)
        self.assertEqual(validate_command_handle_payload(handle, body), [])

    def test_parse_command_handles_resolves_skills_and_reviewers(self) -> None:
        parse_command_handles = getattr(COMMAND_SURFACE, "parse_command_handles")
        original_skill_resolver = getattr(COMMAND_SURFACE, "resolve_skill_handle")
        original_reviewer_resolver = getattr(COMMAND_SURFACE, "resolve_reviewer_handle")

        def fake_skill_resolver(handle: str, **_: object) -> dict[str, object]:
            visibilities = {
                "skill-builder": "orchestrator",
                "he-heartbeat": "target",
            }
            return {
                "status": "ok",
                "handle": handle,
                "kind": "skill",
                "command_visibility": visibilities[handle],
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
            parsed = parse_command_handles(
                "use $skill-builder to validate $he-heartbeat with @skillinspector",
                repo_root_path=Path("."),
            )

        self.assertEqual(parsed["status"], "pass")
        self.assertEqual(parsed["reviewer_mentions"][0]["mention"], "skillinspector")
        self.assertEqual(
            parsed["mention_counts"],
            {"skills": 2, "reviewers": 1, "unresolved": 0},
        )
        self.assertEqual(parsed["skill_mentions"][0]["role"], "active_orchestrator")
        self.assertEqual(parsed["skill_mentions"][1]["role"], "target")
        self.assertEqual(
            parsed["reviewer_mentions"][0]["resolution"]["canonical_handle"],
            "skill-inspector",
        )

    def test_generated_handle_uses_unresolved_placeholder_when_source_missing(self) -> None:
        command_handle = getattr(COMMAND_SURFACE, "CommandHandle")
        render_skill_command_handle = getattr(COMMAND_SURFACE, "render_skill_command_handle")
        validate_command_handle_payload = getattr(COMMAND_SURFACE, "_validate_command_handle_payload")

        handle = command_handle(
            handle="he-work",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path=None,
            command_handle_path=".agents/skills/he-work/SKILL.md",
            owner="harness-engineering",
            description="Execute a plan.",
            invoke_via="harness-engineering",
            level="atom",
        )

        body = render_skill_command_handle(handle)
        self.assertIn("Canonical source path: `UNRESOLVED_SOURCE_PATH`.", body)
        self.assertIn("search only the owner skill tree", body)
        self.assertEqual(validate_command_handle_payload(handle, body), [])


if __name__ == "__main__":
    unittest.main()
