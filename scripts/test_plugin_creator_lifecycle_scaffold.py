#!/usr/bin/env python3
"""Regression tests for lifecycle-aware plugin scaffolding."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills-system" / "plugin-creator" / "scripts" / "create_basic_plugin.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


class PluginCreatorLifecycleScaffoldTests(unittest.TestCase):
    def test_creates_plugin_with_governance_block_and_without_todo_debt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-plugin",
                "--path",
                tmpdir,
                "--description",
                "Plugin for testing lifecycle-aware scaffolds.",
                "--owner",
                "Agent Skills Team",
                "--review-cadence",
                "monthly",
                "--with-skills",
                "--with-mcp",
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

            manifest_path = Path(tmpdir) / "example-plugin" / ".codex-plugin" / "plugin.json"
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["schema_version"], 1)
            self.assertEqual(payload["description"], "Plugin for testing lifecycle-aware scaffolds.")
            self.assertEqual(payload["governance"]["lifecycle_state"], "incubating")
            self.assertEqual(payload["governance"]["maturity"], "experimental")
            self.assertEqual(payload["governance"]["owner"], "Agent Skills Team")
            self.assertEqual(payload["governance"]["review_cadence"], "monthly")
            self.assertIn("last_reviewed", payload["governance"])
            self.assertEqual(payload["governance"]["metadata_source"], "plugin_manifest")
            self.assertEqual(payload["skills"], "./skills/")
            self.assertEqual(payload["mcpServers"], "./.mcp.json")
            self.assertNotIn("[TODO:", manifest_path.read_text(encoding="utf-8"))

    def test_requires_review_cadence_for_governed_plugin_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            result = _run(
                "example-plugin",
                "--path",
                tmpdir,
                "--description",
                "Plugin for testing lifecycle-aware scaffolds.",
                "--owner",
                "Agent Skills Team",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--review-cadence", result.stderr)


if __name__ == "__main__":
    unittest.main()
