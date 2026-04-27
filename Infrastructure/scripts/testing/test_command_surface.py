#!/usr/bin/env python3
"""Unit tests for generated command-handle rendering."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


SCRIPT_DIR = Path(__file__).resolve().parent.parent / "lifecycle-and-sync"
SCRIPT = SCRIPT_DIR / "command_surface.py"


def _load_module():
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("command_surface", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load command_surface module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)  # type: ignore[misc]
    return module


class CommandSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = _load_module()

    def test_generated_handle_includes_portable_source_path_fallback(self) -> None:
        handle = self.mod.CommandHandle(
            handle="he-work",
            kind="skill",
            command_visibility="target",
            runtime_visibility="latent",
            source_path="Plugins/harness-engineering/skills/team_automation/he-work/SKILL.md",
            command_handle_path=".agents/skills/he-work/SKILL.md",
            owner="harness-engineering",
            description="Execute a plan.",
            invoke_via="harness-engineering",
            level="atom",
        )

        body = self.mod.render_skill_command_handle(handle)

        self.assertIn(
            "Canonical source path: `Plugins/harness-engineering/skills/team_automation/he-work/SKILL.md`.",
            body,
        )
        self.assertIn("If `./bin/ask` exists", body)
        self.assertIn("If `./bin/ask` is unavailable", body)
        self.assertIn("search only the owner skill tree", body)
        self.assertEqual(self.mod._validate_command_handle_payload(handle, body), [])


if __name__ == "__main__":
    unittest.main()
