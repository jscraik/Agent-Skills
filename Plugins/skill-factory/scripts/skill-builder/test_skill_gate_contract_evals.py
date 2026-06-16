#!/usr/bin/env python3
"""Focused tests for skill_gate contract/eval readiness checks."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ["SKILL_GATE_DISABLE_CLI"] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_gate import Level, SkillDoc, check_contract_and_evals, check_required_sections


class SkillGateContractEvalTests(unittest.TestCase):
    def test_house_style_sections_do_not_fail_sdk_shaped_skill_body(self) -> None:
        doc = SkillDoc(
            path=Path("SKILL.md"),
            raw="""---
name: sample
description: Validate SDK-shaped skill metadata.
metadata:
  version: "1.0.0"
---
# Sample
""",
            frontmatter={
                "name": "sample",
                "description": "Validate SDK-shaped skill metadata.",
                "metadata": {"version": "1.0.0"},
            },
            body="# Sample\n\nUse repo-native validation.\n",
            fm_start_line=1,
            fm_end_line=6,
        )

        findings = check_required_sections(doc, require_philosophy=True)

        self.assertTrue(findings)
        self.assertFalse([finding for finding in findings if finding.level == Level.FAIL])

    def test_missing_gold_files_report_skill_local_references_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = check_contract_and_evals(Path(tmp), require_contract=True, require_evals=True)

        messages = {finding.code: finding.message for finding in findings}
        self.assertEqual(messages["CONTRACT_MISSING"], "Missing references/contract.yaml (required for gold).")
        self.assertEqual(messages["EVALS_MISSING"], "Missing references/evals.yaml (required for gold).")
        self.assertTrue(all("Infrastructure/references" not in message for message in messages.values()))

    def test_accepts_current_expected_signals_eval_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            refs = skill_dir / "references"
            refs.mkdir()
            (refs / "contract.yaml").write_text(
                """
purpose: Validate skill output quality.
triggers: [skill review]
inputs: [skill path]
outputs: [scorecard]
non_goals: [publishing]
risks: [stale evidence]
""".strip(),
                encoding="utf-8",
            )
            (refs / "evals.yaml").write_text(
                """
schema_version: 1
cases:
  - name: Discovery smoke
    prompt: Review this skill locally.
    acceptance:
      - {type: contains, value: scorecard}
    expected_signals:
      required_terms: [scorecard]
      required_output_fields: [quality]
      required_source_reads: [SKILL.md]
      forbidden_terms: [publish]
      forbidden_actions: [network upload]
      flow_steps: [read skill, score skill]
    budgets:
      min_expected_signal_score: 0.8
  - name: Edge case
    prompt: Review an incomplete skill.
    acceptance:
      - {type: contains, value: warnings}
  - name: Failure case
    prompt: Review a missing skill.
    acceptance:
      - {type: contains, value: blocked}
""".strip(),
                encoding="utf-8",
            )

            findings = check_contract_and_evals(skill_dir, require_contract=True, require_evals=True)

        self.assertFalse([finding for finding in findings if finding.level == Level.FAIL])

    def test_rejects_malformed_expected_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            refs = skill_dir / "references"
            refs.mkdir()
            (refs / "evals.yaml").write_text(
                """
cases:
  - name: Bad signals
    prompt: Review this skill locally.
    acceptance:
      - {type: contains, value: scorecard}
    expected_signals:
      required_terms: scorecard
  - name: Edge case
    prompt: Review an incomplete skill.
    acceptance:
      - {type: contains, value: warnings}
  - name: Failure case
    prompt: Review a missing skill.
    acceptance:
      - {type: contains, value: blocked}
""".strip(),
                encoding="utf-8",
            )

            findings = check_contract_and_evals(skill_dir, require_contract=False, require_evals=True)

        self.assertTrue(any(finding.code == "EVALS_EXPECTED_SIGNALS_LIST_SHAPE" for finding in findings))


if __name__ == "__main__":
    unittest.main()
