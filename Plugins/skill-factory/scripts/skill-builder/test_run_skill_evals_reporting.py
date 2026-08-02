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
    _claim_to_evidence_summary,
    _load_evals_document,
    evaluate_expected_signals,
    load_evals,
    summarize_expected_signal_results,
)




class RunSkillEvalsReportingTests(unittest.TestCase):
    def test_release_mdx_reporting_requires_template_and_component_bundle(self) -> None:
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
                    reporting:
                      preferred_source_format: MDX
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        expected_signals:
                          required_terms: [done]
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
            gap_types = {gap["type"] for gap in summary["blocking_gaps"]}
            self.assertIn("missing_report_template", gap_types)
            self.assertIn("missing_report_component_bundle", gap_types)


    def test_reporting_rejects_non_string_preferred_source_format(self) -> None:
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
                    reporting:
                      preferred_source_format: [MDX]
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        expected_signals:
                          required_terms: [done]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            with self.assertRaisesRegex(ValueError, "preferred_source_format"):
                _claim_to_evidence_summary(
                    _load_evals_document(evals_path),
                    cases,
                    eval_mode="release",
                    skill_dir=Path(tmp),
                )


    def test_reporting_rejects_absolute_report_paths(self) -> None:
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
                    reporting:
                      preferred_source_format: mdx
                      report_template: /etc/hosts
                      component_bundle: Infrastructure/templates/components/eval-report.tsx
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        expected_signals:
                          required_terms: [done]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            with self.assertRaisesRegex(ValueError, "repo-relative"):
                _claim_to_evidence_summary(
                    _load_evals_document(evals_path),
                    cases,
                    eval_mode="release",
                    skill_dir=Path(tmp),
                )


    def test_reporting_rejects_path_traversal_report_paths(self) -> None:
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
                    reporting:
                      preferred_source_format: mdx
                      report_template: Infrastructure/templates/eval-report.mdx
                      component_bundle: ../components/eval-report.tsx
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        claim_ids: [demo.execution]
                        realistic: true
                        why_realistic: Normal release request.
                        expected_signals:
                          required_terms: [done]
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            cases = load_evals(evals_path)
            with self.assertRaisesRegex(ValueError, "path traversal"):
                _claim_to_evidence_summary(
                    _load_evals_document(evals_path),
                    cases,
                    eval_mode="release",
                    skill_dir=Path(tmp),
                )


    def test_release_mdx_reporting_requires_file_artifacts_not_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill"
            skill_dir.mkdir()
            (skill_dir / "report.mdx").mkdir()
            (skill_dir / "component.tsx").mkdir()
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    reporting:
                      preferred_source_format: mdx
                      report_template: report.mdx
                      component_bundle: component.tsx
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        realistic: true
                        why_realistic: Normal release request.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                load_evals(evals_path),
                eval_mode="release",
                skill_dir=skill_dir,
            )

            self.assertFalse(summary["report_template_exists"])
            self.assertFalse(summary["component_bundle_exists"])
            gap_types = {gap["type"] for gap in summary["blocking_gaps"]}
            self.assertIn("missing_report_template", gap_types)
            self.assertIn("missing_report_component_bundle", gap_types)


    def test_release_mdx_reporting_rejects_wrong_file_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill"
            skill_dir.mkdir()
            (skill_dir / "report.md").write_text("# report\n", encoding="utf-8")
            (skill_dir / "component.txt").write_text("component\n", encoding="utf-8")
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    reporting:
                      preferred_source_format: mdx
                      report_template: report.md
                      component_bundle: component.txt
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        realistic: true
                        why_realistic: Normal release request.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                load_evals(evals_path),
                eval_mode="release",
                skill_dir=skill_dir,
            )

            gap_types = {gap["type"] for gap in summary["blocking_gaps"]}
            self.assertIn("invalid_report_template_type", gap_types)
            self.assertIn("invalid_report_component_bundle_type", gap_types)


    def test_release_mdx_reporting_does_not_use_ambient_cwd_shadow_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill"
            shadow_root = Path(tmp) / "shadow-cwd"
            (shadow_root / "shadow").mkdir(parents=True)
            skill_dir.mkdir()
            (shadow_root / "shadow" / "report.mdx").write_text("# shadow\n", encoding="utf-8")
            (shadow_root / "shadow" / "component.tsx").write_text("export {}\n", encoding="utf-8")
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    reporting:
                      preferred_source_format: mdx
                      report_template: shadow/report.mdx
                      component_bundle: shadow/component.tsx
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        realistic: true
                        why_realistic: Normal release request.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            previous_cwd = Path.cwd()
            try:
                os.chdir(shadow_root)
                summary = _claim_to_evidence_summary(
                    _load_evals_document(evals_path),
                    load_evals(evals_path),
                    eval_mode="release",
                    skill_dir=skill_dir,
                )
            finally:
                os.chdir(previous_cwd)

            self.assertFalse(summary["report_template_exists"])
            self.assertFalse(summary["component_bundle_exists"])
            gap_types = {gap["type"] for gap in summary["blocking_gaps"]}
            self.assertIn("missing_report_template", gap_types)
            self.assertIn("missing_report_component_bundle", gap_types)


    def test_release_mdx_reporting_rejects_symlink_escape_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "skill"
            skill_dir.mkdir()
            outside_dir = Path(tmp) / "outside"
            outside_dir.mkdir()
            (outside_dir / "report.mdx").write_text("# outside\n", encoding="utf-8")
            (outside_dir / "component.tsx").write_text("export {}\n", encoding="utf-8")
            (skill_dir / "report.mdx").symlink_to(outside_dir / "report.mdx")
            (skill_dir / "component.tsx").symlink_to(outside_dir / "component.tsx")
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    reporting:
                      preferred_source_format: mdx
                      report_template: report.mdx
                      component_bundle: component.tsx
                    cases:
                      - id: execution
                        name: Execution
                        prompt: Do the thing.
                        realistic: true
                        why_realistic: Normal release request.
                        acceptance:
                          - type: contains
                            value: done
                    """
                ),
                encoding="utf-8",
            )

            summary = _claim_to_evidence_summary(
                _load_evals_document(evals_path),
                load_evals(evals_path),
                eval_mode="release",
                skill_dir=skill_dir,
            )

            self.assertFalse(summary["report_template_exists"])
            self.assertFalse(summary["component_bundle_exists"])
            gap_types = {gap["type"] for gap in summary["blocking_gaps"]}
            self.assertIn("missing_report_template", gap_types)
            self.assertIn("missing_report_component_bundle", gap_types)


    def test_mdx_eval_report_template_uses_report_binding_not_literal_placeholders(self) -> None:
        template = (REPO_ROOT / "Infrastructure/templates/eval-report.mdx").read_text(encoding="utf-8")

        self.assertIn("export const report", template)
        self.assertIn("skill={report.skill}", template)
        self.assertIn('from "./components/eval-report"', template)
        self.assertNotIn('"{skill_name}"', template)
        self.assertNotIn("{release_decision}", template)


    def test_expected_signals_score_missing_forbidden_and_flow_risk(self) -> None:
        result = evaluate_expected_signals(
            "Read SKILL.md, then edit the runtime projection, then run pytest.",
            {
                "required_terms": ["read SKILL.md", "record evidence"],
                "forbidden_terms": ["runtime projection"],
                "flow_steps": ["read SKILL.md", "record evidence", "run pytest"],
            },
        )

        self.assertIsNotNone(result)
        assert result is not None
        self.assertLess(result["composite"], 80)
        self.assertIn("required term: record evidence", result["missing_signals"])
        self.assertIn("forbidden term: runtime projection", result["forbidden_signals_found"])
        self.assertIn("forbidden signals present", result["risk_factors"])


    def test_expected_signal_summary_collects_risky_cases(self) -> None:
        summary = summarize_expected_signal_results(
            [
                {
                    "id": "case-a",
                    "runners": {
                        "discovery-smoke": {
                            "metrics": {
                                "expected_signals": {
                                    "composite": 75,
                                    "risk_factors": ["expected signal score below 80"],
                                }
                            }
                        }
                    },
                },
                {
                    "id": "case-b",
                    "runners": {
                        "discovery-smoke": {
                            "metrics": {"expected_signals": {"composite": 100, "risk_factors": []}}
                        }
                    },
                },
            ]
        )

        self.assertEqual(summary["runs"], 2)
        self.assertEqual(summary["average"], 88)
        self.assertEqual(summary["minimum"], 75)
        self.assertEqual(summary["risky_cases"][0]["case"], "case-a")




if __name__ == "__main__":
    unittest.main()
