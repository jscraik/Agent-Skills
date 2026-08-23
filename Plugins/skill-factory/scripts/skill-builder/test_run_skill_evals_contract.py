#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import os
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
    _render_case_references,
    _weak_acceptance_reasons,
    load_evals,
    load_neutral_baseline_approvals,
)
from run_skill_evals_references import (  # noqa: E402
    MAX_CASE_REFERENCE_BYTES,
    MAX_REFERENCE_BYTES,
)




class RunSkillEvalsContractTests(unittest.TestCase):
    def test_render_case_references_embeds_only_declared_package_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (references / "operational.md").write_text("# Operational\n", encoding="utf-8")

            rendered = _render_case_references(skill_dir, ("references/operational.md",))

            self.assertIn('<REFERENCE path="references/operational.md">', rendered)
            self.assertIn("# Operational", rendered)

    def test_render_case_references_rejects_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "must stay under references"):
                _render_case_references(Path(tmp), ("../outside.md",))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_render_case_references_rejects_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            outside = Path(tmp) / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            (references / "linked.md").symlink_to(outside)

            with self.assertRaisesRegex(ValueError, "package-local regular file"):
                _render_case_references(skill_dir, ("references/linked.md",))

    def test_render_case_references_reports_unreadable_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (references / "invalid.md").write_bytes(b"\xff")

            with self.assertRaisesRegex(ValueError, "could not be read"):
                _render_case_references(skill_dir, ("references/invalid.md",))

    def test_render_case_references_rejects_oversized_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            oversized = references / "oversized.md"
            oversized.write_bytes(b"x" * (MAX_REFERENCE_BYTES + 1))

            with self.assertRaisesRegex(ValueError, "oversized.md"):
                _render_case_references(skill_dir, ("references/oversized.md",))

    def test_render_case_references_rejects_cumulative_overflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            reference_paths = []
            file_size = MAX_REFERENCE_BYTES
            for index in range((MAX_CASE_REFERENCE_BYTES // file_size) + 1):
                relative = f"references/part-{index}.md"
                (skill_dir / relative).write_bytes(b"x" * file_size)
                reference_paths.append(relative)

            with self.assertRaisesRegex(ValueError, reference_paths[-1]):
                _render_case_references(skill_dir, tuple(reference_paths))

    def test_load_evals_parses_reference_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "demo-skill"
            references = skill_dir / "references"
            references.mkdir(parents=True)
            (references / "operational.md").write_text("# Operational\n", encoding="utf-8")
            evals_path = references / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: reference-case
                        name: Reference case
                        prompt: Use the declared reference.
                        acceptance:
                          - contains: done
                        reference_paths:
                          - references/operational.md
                    """
                ),
                encoding="utf-8",
            )

            case = load_evals(evals_path)[0]

            self.assertEqual(case.reference_paths, ("references/operational.md",))
            self.assertIn('<REFERENCE path="references/operational.md">', case.prompt)
            self.assertIn("User task:\nUse the declared reference.", case.prompt)

    def test_load_evals_without_references_preserves_prompt_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            prompt = "Keep  spacing, punctuation—and Unicode.\n"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    cases:
                      - id: plain-case
                        name: Plain case
                        prompt: "Keep  spacing, punctuation—and Unicode.\\n"
                        acceptance:
                          - contains: done
                    """
                ),
                encoding="utf-8",
            )

            case = load_evals(evals_path)[0]

            self.assertEqual(case.prompt, prompt)
            self.assertEqual(case.reference_paths, ())

    def test_load_evals_parses_document_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                "cases:\n  - name: once\n    prompt: once\n    acceptance: []\n",
                encoding="utf-8",
            )
            with unittest.mock.patch(
                "run_skill_evals._load_evals_document",
                wraps=_load_evals_document,
            ) as loader:
                load_evals(evals_path)

            loader.assert_called_once_with(evals_path)

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
