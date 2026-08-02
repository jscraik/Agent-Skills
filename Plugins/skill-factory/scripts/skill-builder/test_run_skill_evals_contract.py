#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

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
    EvalCase,
    _claim_to_evidence_summary,
    _load_evals_document,
    _weak_acceptance_reasons,
    load_evals,
    load_neutral_baseline_approvals,
)




class RunSkillEvalsContractTests(unittest.TestCase):
    def test_repo_evals_include_family_contract_cases(self) -> None:
        evals_path = SKILL_DIR / "references" / "evals.yaml"

        cases = load_evals(evals_path)
        case_map = {case.id: case for case in cases}

        for case_id in [
            "clarification-package-ambiguous",
            "plugin-only-handoff",
            "mixed-authoring-install-handoff",
            "audit-package-validation-first",
            "provenance-import-rollback",
            "builder-round-metadata-contract",
        ]:
            self.assertIn(case_id, case_map)
            self.assertEqual(case_map[case_id].eval_modes, ("smoke", "release"))
            self.assertEqual(case_map[case_id].timeout_profile, "codex-heavy")


    def test_builder_round_metadata_case_has_baseline_contract_fields(self) -> None:
        evals_path = SKILL_DIR / "references" / "evals.yaml"
        cases = load_evals(evals_path)
        case_map = {case.id: case for case in cases}
        target = case_map["builder-round-metadata-contract"]

        self.assertEqual(target.baseline_type, "neutral_repo_baseline")
        self.assertEqual(target.metric_availability, "unavailable")
        self.assertEqual(target.iteration_round_state, "reviewed")
        self.assertEqual(target.readiness_state, "comparison_incomplete")
        self.assertEqual(target.neutral_baseline_approval_id, "planner-approved-neutral-baseline-skill-builder")
        self.assertIsInstance(target.comparison_inputs, dict)
        self.assertEqual(target.comparison_inputs["prompt_set"], "frozen-first-response-contract")

        approvals = load_neutral_baseline_approvals(evals_path)
        self.assertIn("planner-approved-neutral-baseline-skill-builder", approvals)


    def test_load_evals_parses_expected_signals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: signal-case
                        name: Signal case
                        prompt: Check the skill.
                        acceptance:
                          - contains: done
                        expected_signals:
                          required_terms:
                            - canonical source
                          forbidden_terms:
                            - runtime projection
                        budgets:
                          min_expected_signal_score: 90
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            self.assertEqual(cases[0].expected_signals["required_terms"], ["canonical source"])
            self.assertEqual(cases[0].expected_signals["forbidden_terms"], ["runtime projection"])
            self.assertEqual(cases[0].budgets["min_expected_signal_score"], 90)



    def test_load_evals_parses_riteway_contract_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: report-shape
                        name: report shape
                        prompt: Check the report.
                        acceptance:
                          - contains: done
                        unit: eval report rendering
                        given: a failed agent-mediated assertion
                        should: show the bug-report shape
                        actual_artifact: actual.txt
                        expected_artifact: expected.txt
                        raw_response_artifact: .responses.md
                        judge_detail_artifact: judge.json
                        pass_rate_threshold: 0.75
                        reproduce: ./bin/ask evals run demo
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            cases = load_evals(evals_path)

        self.assertEqual(cases[0].unit, "eval report rendering")
        self.assertEqual(cases[0].given, "a failed agent-mediated assertion")
        self.assertEqual(cases[0].should, "show the bug-report shape")
        self.assertEqual(cases[0].actual_artifact, "actual.txt")
        self.assertEqual(cases[0].expected_artifact, "expected.txt")
        self.assertEqual(cases[0].raw_response_artifact, ".responses.md")
        self.assertEqual(cases[0].judge_detail_artifact, "judge.json")
        self.assertEqual(cases[0].pass_rate_threshold, 0.75)
        self.assertEqual(cases[0].reproduce, "./bin/ask evals run demo")


    def test_load_evals_rejects_non_finite_pass_rate_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: bad-threshold
                        name: bad threshold
                        prompt: Check this.
                        acceptance:
                          - contains: done
                        pass_rate_threshold: .nan
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "pass_rate_threshold.*finite"):
                load_evals(evals_path)


    def test_load_evals_rejects_boolean_pass_rate_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: bad-threshold
                        name: bad threshold
                        prompt: Check this.
                        acceptance:
                          - contains: done
                        pass_rate_threshold: true
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "pass_rate_threshold.*numeric"):
                load_evals(evals_path)


    def test_load_evals_rejects_absolute_case_artifact_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: bad-artifact
                        name: bad artifact
                        prompt: Check this.
                        acceptance:
                          - contains: done
                        raw_response_artifact: /tmp/raw-response.md
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "raw_response_artifact.*repo-relative"):
                load_evals(evals_path)


    def test_load_evals_parses_claim_coverage_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.activation
                        statement: Activates correctly.
                        source: SKILL.md:description
                        claim_type: activation
                        risk: high
                        hard_gate: true
                        evidence_required: [selected]
                    baselines:
                      - id: previous-release
                        baseline_type: previous_version
                    reporting:
                      preferred_source_format: mdx
                      report_template: Infrastructure/templates/eval-report.mdx
                    cases:
                      - id: explicit
                        name: Explicit
                        prompt: Use the skill.
                        claim_ids: [demo.activation]
                        baseline_id: previous-release
                        realistic: true
                        why_realistic: Direct user invocation.
                        hard_gates: [no_false_completion]
                        expected_evidence: [selection signal]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)

            self.assertEqual(cases[0].claim_ids, ("demo.activation",))
            self.assertEqual(cases[0].baseline_id, "previous-release")
            self.assertTrue(cases[0].realistic)
            self.assertEqual(cases[0].hard_gates, ("no_false_completion",))


    def test_release_claim_gate_blocks_missing_realism(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.execution
                        statement: Executes correctly.
                        source: SKILL.md:workflow
                        claim_type: execution
                        risk: high
                        hard_gate: true
                        evidence_required: [acceptance]
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="release",
                skill_dir=Path(tmp),
            )

            self.assertFalse(summary["passed"])
            self.assertIn(
                "missing_realism_evidence",
                {gap["type"] for gap in summary["blocking_gaps"]},
            )


    def test_release_claim_gate_blocks_missing_claim_registry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: unclaimed-release
                        name: Unclaimed release
                        prompt: Do the thing.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="release",
                skill_dir=Path(tmp),
            )

            self.assertFalse(summary["passed"])
            self.assertIn(
                "missing_claim_registry",
                {gap["type"] for gap in summary["blocking_gaps"]},
            )


    def test_load_evals_rejects_duplicate_baseline_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    baselines:
                      - id: previous-release
                        baseline_type: previous_version
                      - id: previous-release
                        baseline_type: human_reference
                    cases:
                      - id: demo
                        name: Demo
                        prompt: Do the thing.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate baseline id"):
                load_evals(evals_path)


    def test_claim_summary_flags_missing_riteway_shape_and_weak_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: weak-smoke
                        name: weak smoke
                        prompt: Check this.
                        eval_modes: [smoke]
                        realistic: true
                        acceptance:
                          - contains: done
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="smoke",
                skill_dir=Path(tmp),
            )

        gap_types = {gap["type"] for gap in summary["gaps"]}
        self.assertIn("missing_riteway_shape", gap_types)
        self.assertIn("weak_acceptance_shape", gap_types)
        self.assertEqual(summary["blocking_gaps"], [])


    def test_jsonpath_acceptance_counts_as_concrete_acceptance(self) -> None:
        case = EvalCase(
            id="jsonpath",
            name="jsonpath",
            prompt="Check JSON.",
            acceptance=[{"type": "jsonpath_exists", "path": "$.status"}],
        )

        self.assertEqual(_weak_acceptance_reasons(case), [])


    def test_neutral_baseline_approvals_reject_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    neutral_baseline_approvals:
                      - id: approved-baseline
                        rationale: first
                      - id: approved-baseline
                        rationale: second
                    cases:
                      - id: demo
                        name: Demo
                        prompt: Do the thing.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "duplicate neutral_baseline_approval id"):
                load_neutral_baseline_approvals(evals_path)


    def test_release_claim_gate_blocks_claim_without_evidence_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.execution
                        statement: Executes correctly.
                        source: SKILL.md:workflow
                        claim_type: execution
                        risk: high
                        hard_gate: true
                        evidence_required: [runner artifact]
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="release",
                skill_dir=Path(tmp),
            )

            self.assertFalse(summary["passed"])
            self.assertIn(
                "claim_without_evidence_surface",
                {gap["type"] for gap in summary["blocking_gaps"]},
            )


    def test_release_claim_gate_does_not_block_focused_subset_missing_evidence_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.execution
                        statement: Executes correctly.
                        source: SKILL.md:workflow
                        claim_type: execution
                        risk: high
                        hard_gate: true
                        evidence_required: [runner artifact]
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Focused diagnostic release run.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="release",
                skill_dir=Path(tmp),
                focused_subset=True,
            )

            self.assertTrue(summary["passed"])
            self.assertEqual(summary["blocking_gaps"], [])
            self.assertNotIn(
                "claim_without_evidence_surface",
                {gap["type"] for gap in summary["gaps"]},
            )


    def test_release_claim_gate_counts_expected_evidence_surface(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.execution
                        statement: Executes correctly.
                        source: SKILL.md:workflow
                        claim_type: execution
                        risk: high
                        hard_gate: true
                        evidence_required: [runner artifact]
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        expected_evidence: [runner artifact]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                cases,
                eval_mode="release",
                skill_dir=Path(tmp),
            )

            self.assertTrue(summary["passed"])
            self.assertEqual(summary["blocking_gaps"], [])
            self.assertEqual(
                summary["claims"][0]["evidence_surfaces"],
                ["expected_evidence"],
            )




if __name__ == "__main__":
    unittest.main()
