#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import json
import sys
import tempfile
import textwrap
import unittest
import unittest.mock
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
REPO_ROOT = SCRIPT_DIR.parents[3]
repo_root_str = str(REPO_ROOT)
if repo_root_str not in sys.path:
    sys.path.insert(0, repo_root_str)
SKILL_DIR = SCRIPT_DIR.parents[1] / "skills" / "code_quality_review" / "skill-builder"


existing_runner = sys.modules.get("run_skill_evals")
if existing_runner is not None:
    existing_path = Path(str(getattr(existing_runner, "__file__", ""))).resolve()
    if existing_path.parent != SCRIPT_DIR:
        del sys.modules["run_skill_evals"]

existing_trace_checks = sys.modules.get("deterministic_trace_checks")
if existing_trace_checks is not None:
    existing_path = Path(str(getattr(existing_trace_checks, "__file__", ""))).resolve()
    if existing_path.parent != SCRIPT_DIR:
        del sys.modules["deterministic_trace_checks"]

from run_skill_evals import (  # noqa: E402
    main,
)




class RunSkillEvalsLiftTests(unittest.TestCase):
    def test_summary_and_manifest_include_iteration_round_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    ---

                    ## Discovery interview
                    - ask one round at a time
                    - use a plain-language question
                    - explain why the round matters
                    - avoid dumping the whole interview plan at once
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "discovery-interview.md").write_text(
                textwrap.dedent(
                    """
                    ## Request user input mini-templates

                    What should this skill help you do?

                    ## Copy-paste payload examples
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    neutral_baseline_approvals:
                      - id: planner-approved-neutral-baseline-skill-builder
                        rationale: approved for this synthetic regression test
                        approved_by: test
                    cases:
                      - id: builder-round-metadata-contract
                        name: builder round metadata contract
                        prompt: Define one explicit iteration contract.
                        smoke_mode: discovery-round-one
                        baseline_type: neutral_repo_baseline
                        neutral_baseline_approval_id: planner-approved-neutral-baseline-skill-builder
                        comparison_inputs:
                          prompt_set: frozen-first-response-contract
                        iteration_round_state: reviewed
                        metric_availability: unavailable
                        readiness_state: comparison_incomplete
                        comparison_review_artifact: comparison_review.md
                        acceptance:
                          - contains: "## Inputs"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            exit_code = main(
                [
                    str(skill_dir),
                    "--runner",
                    "discovery-smoke",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(exit_code, 0)
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            self.assertTrue(report_dirs)
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))
            release_manifest = json.loads((report_dirs[-1] / "release_manifest.json").read_text(encoding="utf-8"))

        case = summary["cases"][0]
        self.assertEqual(case["baseline_type"], "neutral_repo_baseline")
        self.assertEqual(case["iteration_round_state"], "reviewed")
        self.assertEqual(case["metric_availability"], "unavailable")
        self.assertEqual(case["readiness_state"], "comparison_incomplete")
        self.assertIn("comparison_review.md", case["comparison_review_artifact"])
        self.assertEqual(case["neutral_baseline_approval"]["id"], "planner-approved-neutral-baseline-skill-builder")
        self.assertEqual(summary["readiness_summary"]["comparison_incomplete"], 1)
        self.assertEqual(summary["round_state_summary"]["reviewed"], 1)
        self.assertIn("planner-approved-neutral-baseline-skill-builder", summary["neutral_baseline_approvals_used"])
        self.assertEqual(
            release_manifest["run"]["readiness_summary"]["comparison_incomplete"],
            1,
        )


    def test_discovery_smoke_executes_no_skill_baseline_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    ---

                    ## Discovery interview
                    - ask one round at a time
                    - ask a plain-language question
                    - explain why the round matters
                    - avoid dumping the whole interview plan at once
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "discovery-interview.md").write_text(
                textwrap.dedent(
                    """
                    ## Request user input mini-templates

                    What should this skill help you do?

                    ## Copy-paste payload examples
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: no-skill-baseline-lift
                        name: no skill baseline lift
                        prompt: Start discovery for an underspecified docs request.
                        smoke_mode: discovery-round-one
                        baseline_type: no_skill
                        prepend_skill: true
                        acceptance:
                          - skill_selected: demo-skill
                          - contains: "## Inputs"
                          - contains: "Round 1 question"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            exit_code = main(
                [
                    str(skill_dir),
                    "--runner",
                    "discovery-smoke",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )

            self.assertEqual(exit_code, 0)
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            self.assertTrue(report_dirs)
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))
            baseline_final_path = (
                report_dirs[-1]
                / "01-no-skill-baseline-lift"
                / "discovery-smoke"
                / "baseline-no-skill"
                / "final.txt"
            )
            self.assertTrue(baseline_final_path.exists())
            baseline_final_text = baseline_final_path.read_text(encoding="utf-8")

        case = summary["cases"][0]
        self.assertEqual(case["baseline_type"], "no_skill")
        self.assertEqual(case["skill_lift"], 1)
        self.assertTrue(case["is_beneficial"])
        self.assertFalse(case["baseline_regression"])

        comparison = case["baseline_comparisons"]["discovery-smoke"]
        self.assertEqual(comparison["status"], "compared")
        self.assertTrue(comparison["with_skill_passed"])
        self.assertFalse(comparison["baseline_passed"])

        runner = case["runners"]["discovery-smoke"]
        self.assertEqual(runner["baseline"]["status"], "executed")
        self.assertFalse(runner["baseline"]["passed"])
        self.assertIn("skill_selected failed", runner["baseline"]["tier1_failures"][0])
        self.assertIn("Skill context was intentionally withheld", baseline_final_text)


    def test_live_runner_executes_no_skill_baseline_with_raw_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    ---

                    Use a discovery response that includes the exact first question.
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: live-no-skill-baseline-lift
                        name: live no skill baseline lift
                        prompt: Start discovery.
                        baseline_type: no_skill
                        prepend_skill: true
                        budgets:
                          require_skill_lift: true
                          min_skill_lift: 1
                        acceptance:
                          - contains: "Round 1 question"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            prompts: list[str] = []

            def fake_openai_exec(**kwargs):
                prompt = kwargs["prompt"]
                output_path = kwargs["output_last_message_path"]
                prompts.append(prompt)
                if "SKILL.md" in prompt:
                    output = "## Next step\n- Round 1 question: What should this skill help you do?\n"
                else:
                    output = "Generic response without the discovery contract.\n"
                output_path.write_text(output, encoding="utf-8")
                return 0, output, ""

            reports_dir = Path(tmpdir) / "reports"
            with unittest.mock.patch("run_skill_evals.run_openai_exec", side_effect=fake_openai_exec):
                exit_code = main(
                    [
                        str(skill_dir),
                        "--runner",
                        "openai",
                        "--reports-dir",
                        str(reports_dir),
                        "--format",
                        "json",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertEqual(len(prompts), 2)
            self.assertIn("SKILL.md", prompts[0])
            self.assertNotIn("SKILL.md", prompts[1])
            self.assertEqual(prompts[1].strip(), "Start discovery.")

            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            self.assertTrue(report_dirs)
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))

        case = summary["cases"][0]
        self.assertEqual(case["skill_lift"], 1)
        self.assertTrue(case["is_beneficial"])
        comparison = case["baseline_comparisons"]["openai"]
        self.assertEqual(comparison["status"], "compared")
        self.assertTrue(comparison["with_skill_passed"])
        self.assertFalse(comparison["baseline_passed"])
        runner = case["runners"]["openai"]
        self.assertEqual(runner["baseline"]["status"], "executed")
        self.assertFalse(runner["baseline"]["passed"])
        self.assertIn("contains failed", runner["baseline"]["tier1_failures"][0])


    def test_skill_lift_budget_fails_when_baseline_also_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    ---

                    Use a discovery response that includes the exact first question.
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: live-no-lift
                        name: live no lift
                        prompt: Start discovery.
                        baseline_type: no_skill
                        prepend_skill: true
                        budgets:
                          require_skill_lift: true
                          min_skill_lift: 1
                        acceptance:
                          - contains: "Round 1 question"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            def fake_openai_exec(**kwargs):
                output = "## Next step\n- Round 1 question: What should this skill help you do?\n"
                kwargs["output_last_message_path"].write_text(output, encoding="utf-8")
                return 0, output, ""

            reports_dir = Path(tmpdir) / "reports"
            with unittest.mock.patch("run_skill_evals.run_openai_exec", side_effect=fake_openai_exec):
                exit_code = main(
                    [
                        str(skill_dir),
                        "--runner",
                        "openai",
                        "--reports-dir",
                        str(reports_dir),
                        "--format",
                        "json",
                    ]
                )

            self.assertEqual(exit_code, 2)
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            self.assertTrue(report_dirs)
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))

        case = summary["cases"][0]
        self.assertFalse(case["passed"])
        self.assertEqual(case["skill_lift"], 0)
        self.assertFalse(case["is_beneficial"])
        self.assertIn(
            "require_skill_lift failed",
            "\n".join(case["tier1_failures"]),
        )
        self.assertIn(
            "min_skill_lift failed",
            "\n".join(case["tier1_failures"]),
        )





if __name__ == "__main__":
    unittest.main()
