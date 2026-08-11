#!/usr/bin/env python3
"""Regression tests for JSON serialization at the eval-runner boundary."""

from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from run_skill_evals import main  # noqa: E402


def _write_discovery_skill(root: Path) -> Path:
    skill_dir = root / "demo-skill"
    references = skill_dir / "references"
    references.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo-skill\n---\n## Discovery interview\n"
        "- ask one round at a time\n- use a plain-language question\n"
        "- explain why the round matters\n- avoid dumping the whole interview plan at once\n",
        encoding="utf-8",
    )
    (references / "discovery-interview.md").write_text(
        "## Request user input mini-templates\nWhat should this skill help you do?\n"
        "## Copy-paste payload examples\n## Round 1\nWhat should this skill help you do?\n",
        encoding="utf-8",
    )
    (references / "evals.yaml").write_text(
        textwrap.dedent("""
        schema_version: "2.0"
        cases:
          - id: discovery-round-one
            name: discovery smoke
            prompt: Help define the skill.
            smoke_mode: discovery-round-one
            should_trigger: true
            acceptance:
              - contains: "Round 1 question:"
        """).strip() + "\n",
        encoding="utf-8",
    )
    return skill_dir


class RunSkillEvalsSerializationTests(unittest.TestCase):
    def test_summary_serializes_blocker_taxonomy_as_a_plain_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir) / "reports"
            exit_code = main([str(_write_discovery_skill(Path(tmpdir))), "--runner", "discovery-smoke", "--reports-dir", str(reports_dir), "--format", "json"])
            summary_path = next((reports_dir / "demo-skill").glob("*/summary.json"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 0)
        self.assertIsInstance(summary["blocker_taxonomy"], dict)
        json.dumps(summary, sort_keys=True)
