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

from skill_gate import (
    Level,
    SkillDoc,
    check_canonical_header_order,
    check_contract_and_evals,
    check_research_eval_prompt_realism,
    check_required_sections,
    check_workflow_fail_fast,
)


class SkillGateContractEvalTests(unittest.TestCase):
    def test_required_sections_do_not_warn_for_removed_house_style_headers(self) -> None:
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
            body=(
                "# Sample\n\n"
                "## When To Use\n\nUse when testing.\n"
                "## Inputs\n\nTarget.\n"
                "## Outputs\n\nReport.\n"
                "## Workflow\n\nInspect.\n"
                "## Failure Mode\n\nStop with blocker.\n"
                "## Validation\n\nRun package gates.\n"
                "## References\n\nNo references.\n"
            ),
            fm_start_line=1,
            fm_end_line=6,
        )

        findings = check_required_sections(doc, require_philosophy=True)

        codes = {finding.code for finding in findings}
        self.assertNotIn("SEC_PHILOSOPHY_MISSING", codes)
        self.assertNotIn("SEC_ANTIPATTERNS_MISSING", codes)
        self.assertNotIn("SEC_CONSTRAINTS_MISSING", codes)
        self.assertNotIn("SEC_EXECUTION_BOUNDARIES_MISSING", codes)
        self.assertNotIn("SEC_EXAMPLES_MISSING", codes)
        self.assertNotIn("SEC_GOTCHAS_MISSING", codes)
        self.assertFalse([finding for finding in findings if finding.level == Level.FAIL])

    def test_canonical_header_order_accepts_sdk_order(self) -> None:
        doc = SkillDoc(
            path=Path("SKILL.md"),
            raw="",
            frontmatter={},
            body=(
                "# Sample\n\n"
                "## When To Use\n\nB.\n"
                "## Inputs\n\nD.\n"
                "## Outputs\n\nE.\n"
                "## Workflow\n\nF.\n"
                "## Failure Mode\n\nI.\n"
                "## Validation\n\nJ.\n"
                "## References\n\nK.\n"
            ),
            fm_start_line=1,
            fm_end_line=1,
        )

        self.assertEqual(check_canonical_header_order(doc), [])

    def test_canonical_header_order_flags_inputs_before_when_to_use(self) -> None:
        doc = SkillDoc(
            path=Path("SKILL.md"),
            raw="",
            frontmatter={},
            body=(
                "# Sample\n\n"
                "## Inputs\n\nD.\n"
                "## When To Use\n\nB.\n"
                "## Outputs\n\nE.\n"
                "## Workflow\n\nF.\n"
            ),
            fm_start_line=1,
            fm_end_line=1,
        )

        findings = check_canonical_header_order(doc)

        self.assertEqual([finding.code for finding in findings], ["SEC_CANONICAL_HEADER_ORDER"])
        self.assertEqual(findings[0].level, Level.FAIL)

    def test_require_fail_fast_fails_when_validation_section_absent(self) -> None:
        doc = SkillDoc(
            path=Path("SKILL.md"),
            raw="""---
name: sample
description: Validate strict fail-fast behavior.
metadata:
  version: "1.0.0"
---
# Sample

## Workflow

Run the focused gate.
""",
            frontmatter={
                "name": "sample",
                "description": "Validate strict fail-fast behavior.",
                "metadata": {"version": "1.0.0"},
            },
            body="# Sample\n\n## Workflow\n\nRun the focused gate.\n",
            fm_start_line=1,
            fm_end_line=6,
        )

        findings = check_workflow_fail_fast(doc, require_fail_fast=True)

        self.assertEqual([finding.code for finding in findings], ["WF_FAIL_FAST_REQUIRED"])
        self.assertEqual(findings[0].level, Level.FAIL)

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

    def test_declared_realistic_eval_accepts_structured_scenario_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            refs = skill_dir / "references"
            refs.mkdir()
            (refs / "evals.yaml").write_text(
                """
cases:
  - id: pr-sweep
    name: PR sweep
    category: edge
    should_trigger: true
    realistic: true
    unit: PR closeout rotation
    given: A maintainer asks the agent to sweep open PRs until they are green.
    should: The agent reports heartbeat status, blocks unsafe merge paths, and proves latest-head checks.
    prompt: Sweep this repo's PRs until green, merged, and cleaned up.
  - id: create-lesson
    name: Create lesson
    category: edge
    should_trigger: true
    realistic: true
    unit: lesson creation
    given: A learner asks the agent to create a first lesson from a clear mission and level.
    should: The agent creates a compact lesson artifact with source notes and retrieval practice.
    prompt: Create lesson 0001 for pytest assertions from my current mission.
  - id: weak
    name: Weak placeholder
    category: edge
    should_trigger: true
    realistic: true
    prompt: TODO example prompt.
""".strip(),
                encoding="utf-8",
            )
            doc = SkillDoc(
                path=skill_dir / "SKILL.md",
                raw="",
                frontmatter={"name": "sample"},
                body="",
                fm_start_line=1,
                fm_end_line=1,
            )

            findings = check_research_eval_prompt_realism(doc)

        weak_findings = [
            finding for finding in findings if finding.code == "RESEARCH_EVALS_DECLARED_REALISTIC_WEAK"
        ]
        self.assertEqual(len(weak_findings), 1)
        self.assertIn("weak", weak_findings[0].evidence)
        self.assertNotIn("pr-sweep", weak_findings[0].evidence)
        self.assertNotIn("create-lesson", weak_findings[0].evidence)


if __name__ == "__main__":
    unittest.main()
