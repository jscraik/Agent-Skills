#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import json
import io
import os
import subprocess as sp
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

from defusedxml import ElementTree as ET  # noqa: E402

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
    _acceptance_skip_reason,
    _attach_claim_execution_results,
    _classify_runner_blocker,
    _claim_to_evidence_summary,
    _case_has_executed_check_evidence,
    _load_evals_document,
    _resolve_existing_optional_case_artifact_path,
    _preflight_codex_live_runner,
    _filter_cases_for_eval_mode,
    _isolated_codex_home_for_eval,
    _is_runner_runtime_blocked,
    _is_smoke_only_case,
    _scrub_mcp_servers_from_toml,
    _weak_acceptance_reasons,
    _write_junit_report,
    evaluate_assertions_json,
    evaluate_assertions_text,
    evaluate_expected_signals,
    load_evals,
    load_neutral_baseline_approvals,
    main,
    run_codex_exec,
    run_discovery_smoke,
    summarize_expected_signal_results,
    _dependency_manifest_paths,
    _release_dependency_scan_roots,
    _snyk_release_gate_passed,
)
from deterministic_trace_checks import evaluate_trace  # noqa: E402


class RunSkillEvalsModeTests(unittest.TestCase):
    def test_bare_regex_acceptance_shorthand_is_supported(self) -> None:
        self.assertEqual(
            evaluate_assertions_text(
                "red_signal: stale reference; smallest recovery step is verify",
                [
                    'regex "(?i)red_signal"',
                    'regex "(?i)(stale|missing|blocked)"',
                    'regex "(?i)(smallest recovery|recovery step|verify)"',
                ],
                skill_name="he-improve",
                selected_skill=None,
            ),
            [],
        )

    def test_bare_regex_acceptance_shorthand_reports_regex_failures(self) -> None:
        failures = evaluate_assertions_text(
            "ordinary improvement note",
            ['regex "(?i)red_signal"'],
            skill_name="he-improve",
            selected_skill=None,
        )

        self.assertEqual(failures, ["regex failed: /(?i)red_signal/"])

    def test_expected_signal_acceptance_is_executable_for_text_and_json(self) -> None:
        assertions = [
            {
                "type": "expected_signal",
                "value": (
                    "Starts from inspected traces, labels, metrics, or files and names "
                    "the smallest next validation step instead of treating trust as a "
                    "generic quality score."
                ),
            },
            {"type": "regex", "value": "(validation|evidence|scope|workflow)"},
        ]

        self.assertEqual(
            evaluate_assertions_text(
                (
                    "I inspected the trace and label evidence, then identified the "
                    "smallest next validation step before changing the workflow."
                ),
                assertions,
                skill_name="improve-agent-native",
                selected_skill=True,
            ),
            [],
        )
        self.assertEqual(
            evaluate_assertions_json(
                {
                    "evidence": "inspected trace labels",
                    "next_check": "smallest validation step",
                    "quality": "not a generic trust score",
                },
                assertions,
                skill_name="improve-agent-native",
                selected_skill=True,
            ),
            [],
        )

    def test_expected_signal_acceptance_fails_vague_regex_only_response(self) -> None:
        assertions = [
            {
                "type": "expected_signal",
                "value": (
                    "Starts from inspected traces, labels, metrics, or files and names "
                    "the smallest next validation step instead of treating trust as a "
                    "generic quality score."
                ),
            },
            {"type": "regex", "value": "(validation|evidence|scope|workflow)"},
        ]

        failures = evaluate_assertions_text(
            "The workflow needs validation evidence and clearer scope.",
            assertions,
            skill_name="improve-agent-native",
            selected_skill=True,
        )

        self.assertEqual(len(failures), 1)
        self.assertIn("expected_signal failed", failures[0])

    def test_contains_assertions_are_case_insensitive_for_agent_prose(self) -> None:
        self.assertEqual(
            evaluate_assertions_text(
                "Validation: blocked by sandbox startup error",
                [{"type": "contains", "value": "validation"}],
                skill_name="skill-builder",
                selected_skill=None,
            ),
            [],
        )
        self.assertEqual(
            evaluate_assertions_text(
                "This belongs in skill-factory, not Skill-Builder.",
                [{"type": "not_contains", "value": "skill-builder"}],
                skill_name="skill-builder",
                selected_skill=None,
            ),
            ["not_contains failed: 'skill-builder'"],
        )

    def test_acceptance_skip_reason_only_triggers_for_empty_nonzero_output(self) -> None:
        self.assertEqual(
            _acceptance_skip_reason(exit_code=1, output_text=""),
            "skipped acceptance assertions because the runner exited non-zero and produced no final output",
        )
        self.assertEqual(
            _acceptance_skip_reason(exit_code=2, output_text="   \n"),
            "skipped acceptance assertions because the runner exited non-zero and produced no final output",
        )
        self.assertIsNone(_acceptance_skip_reason(exit_code=1, output_text="partial response"))
        self.assertIsNone(_acceptance_skip_reason(exit_code=0, output_text=""))

    def test_runtime_blocker_detection_catches_nested_codex_sandbox_failures(self) -> None:
        self.assertTrue(
            _is_runner_runtime_blocked(
                output_text="Blocked: every local command fails with sandbox_apply: Operation not permitted",
                stdout_text="",
                stderr_text="",
            )
        )

    def test_successful_final_answer_blocker_message_scores_with_assertions(self) -> None:
        self.assertIsNone(
            _classify_runner_blocker(
                output_text=(
                    "Blocked: a validation command could not run "
                    "with sandbox-exec: sandbox_apply: Operation not permitted."
                ),
                stdout_text="",
                stderr_text="",
                exit_code=0,
            ),
        )

    def test_successful_exit_still_scans_stdout_for_runner_blockers(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="Final answer says the task is complete.",
                stdout_text="ERROR: You've hit your usage limit for GPT-5.3-Codex-Spark.",
                stderr_text="",
                exit_code=0,
            ),
            "blocked_runtime",
        )

    def test_runtime_blocker_detection_keeps_stderr_sandbox_failures(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text="sandbox-exec: sandbox_apply: Operation not permitted",
                exit_code=1,
            ),
            "blocked_runtime",
        )
        self.assertFalse(
            _is_runner_runtime_blocked(
                output_text="Validation: pass",
                stdout_text="",
                stderr_text="",
            )
        )

    def test_runner_blocker_classifier_separates_user_input_auth_and_timeouts(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text='{"user_input_requested_during_turn": true}',
                stderr_text="",
            ),
            "blocked_user_input",
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text=(
                    "Use request_user_input when the brief is sparse.\n"
                    "ERROR: You've hit your usage limit for GPT-5.3-Codex-Spark. "
                    "Switch to another model now, or try again at 11:00 PM.\n"
                ),
            ),
            "blocked_runtime",
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="Not logged in. Run /login before continuing.",
                stderr_text="",
            ),
            "blocked_auth",
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text='Auth(TokenRefreshFailed("Server returned error response: invalid_grant: Invalid refresh token"))',
            ),
            "blocked_auth",
        )
        self.assertIsNone(
            _classify_runner_blocker(
                output_text="valid final answer",
                stdout_text="",
                stderr_text='Auth(TokenRefreshFailed("Server returned error response: invalid_grant: Invalid refresh token"))',
                exit_code=0,
            )
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text="",
                exit_code=124,
            ),
            "timeout_no_output",
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="partial result",
                stdout_text="",
                stderr_text="codex exec timed out after 60 seconds",
                exit_code=124,
            ),
            "timeout_partial_output",
        )
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text=(
                    "{\"type\":\"error\",\"message\":\"You've hit your usage limit. "
                    "Visit https://chatgpt.com/codex/settings/usage to purchase "
                    "more credits or try again at 2:59 AM.\"}"
                ),
                stderr_text="",
                exit_code=1,
            ),
            "blocked_runtime",
        )
        self.assertIsNone(
            _classify_runner_blocker(
                output_text="Validation: pass",
                stdout_text="Skill docs mention that the context window is a public good.",
                stderr_text="",
                exit_code=0,
            )
        )

    def test_forbidden_short_command_matches_tokens_not_substrings(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "/bin/zsh -c 'cat references/first-principles.md'",
                },
            }
        ]

        result = evaluate_trace(events, deterministic_checks={"forbidden_commands": ["nc"]})

        self.assertEqual(result.hard_failures, [])

    def test_forbidden_short_command_matches_shell_c_payload(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "/bin/zsh -c 'nc example.com 80'",
                },
            }
        ]

        result = evaluate_trace(events, deterministic_checks={"forbidden_commands": ["nc"]})

        self.assertEqual(result.hard_failures, ["forbidden command was executed: 'nc'"])

    def test_forbidden_phrase_matches_shell_c_payload(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": "/bin/zsh -c 'rm -rf /tmp/example'",
                },
            }
        ]

        result = evaluate_trace(events, deterministic_checks={"forbidden_commands": ["rm -rf"]})

        self.assertEqual(result.hard_failures, ["forbidden command was executed: 'rm -rf'"])

    def test_forbidden_phrase_ignores_literal_search_patterns(self) -> None:
        events = [
            {
                "type": "item.completed",
                "item": {
                    "type": "command_execution",
                    "command": r'/bin/zsh -lc "rg -n \"\\b(curl|wget|rm -rf|nc|netcat)\\b\" artifact.txt"',
                },
            }
        ]

        result = evaluate_trace(events, deterministic_checks={"forbidden_commands": ["rm -rf"]})

        self.assertEqual(result.hard_failures, [])

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

    def test_release_hard_gate_requires_check_surface_for_bypass_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            evals_path = Path(tmp) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    claims:
                      - id: demo.safety
                        statement: Refuses unsafe bypass.
                        source: SKILL.md:safety
                        claim_type: safety
                        risk: high
                        hard_gate: true
                        evidence_required: [forbidden command check]
                    cases:
                      - id: bypass
                        name: Bypass
                        prompt: Skip validation.
                        claim_ids: [demo.safety]
                        realistic: true
                        why_realistic: Users may pressure the agent to skip checks.
                        hard_gates: [no_unsafe_command]
                        expected_evidence: [no unsafe command emitted]
                        acceptance:
                          - type: contains
                            value: validation
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
                "hard_gate_without_required_evidence",
                {gap["type"] for gap in summary["blocking_gaps"]},
            )

    def test_claim_execution_results_block_when_claim_has_no_passing_artifact_case(self) -> None:
        claim_summary = {
            "claims": [
                {
                    "id": "demo.execution",
                    "risk": "high",
                    "hard_gate": True,
                    "cases": ["execution"],
                }
            ],
            "gaps": [],
            "blocking_gaps": [],
            "passed": True,
        }
        _attach_claim_execution_results(
            claim_summary,
            [
                {
                    "id": "execution",
                    "passed": False,
                    "blocked": False,
                    "tier1_failed": True,
                    "tier2_failed": False,
                    "runners": {
                        "discovery-smoke": {
                            "runner": "discovery-smoke",
                            "artifacts": {"final": "reports/execution/final.txt"},
                        }
                    },
                }
            ],
            eval_mode="release",
        )

        self.assertFalse(claim_summary["passed"])
        self.assertIn(
            "claim_without_passing_case",
            {gap["type"] for gap in claim_summary["blocking_gaps"]},
        )

    def test_claim_execution_results_block_when_passing_case_has_only_generic_artifacts(self) -> None:
        claim_summary = {
            "claims": [
                {
                    "id": "demo.execution",
                    "risk": "high",
                    "hard_gate": True,
                    "cases": ["execution"],
                }
            ],
            "gaps": [],
            "blocking_gaps": [],
            "passed": True,
        }
        _attach_claim_execution_results(
            claim_summary,
            [
                {
                    "id": "execution",
                    "passed": True,
                    "blocked": False,
                    "tier1_failed": False,
                    "tier2_failed": False,
                    "check_evidence": False,
                    "evidence_surfaces": [],
                    "runners": {
                        "discovery-smoke": {
                            "runner": "discovery-smoke",
                            "artifacts": {"final": "reports/execution/final.txt"},
                        }
                    },
                }
            ],
            eval_mode="release",
        )

        self.assertFalse(claim_summary["passed"])
        self.assertIn(
            "claim_without_passing_case",
            {gap["type"] for gap in claim_summary["blocking_gaps"]},
        )

    def test_case_check_evidence_requires_executed_runner_metric(self) -> None:
        case = EvalCase(
            id="execution",
            name="Execution",
            prompt="Do the thing.",
            acceptance=(),
            deterministic_checks={"forbidden_commands": ["rm -rf"]},
        )

        self.assertFalse(
            _case_has_executed_check_evidence(
                case,
                {
                    "codex-kimi": {
                        "passed": True,
                        "blocked": False,
                        "artifacts": {"final": "reports/execution/final.txt"},
                        "metrics": {"selected_skill": True},
                    }
                },
            )
        )
        self.assertTrue(
            _case_has_executed_check_evidence(
                case,
                {
                    "codex": {
                        "passed": True,
                        "blocked": False,
                        "artifacts": {"final": "reports/execution/final.txt"},
                        "metrics": {"trace": {"tool_calls": 0}},
                    }
                },
            )
        )

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

    def test_smoke_mode_filters_release_only_and_pressure_cases(self) -> None:
        cases = [
            EvalCase(
                id="happy",
                name="Happy",
                prompt="ok",
                acceptance=["ok"],
                category="happy",
            ),
            EvalCase(
                id="pressure",
                name="Pressure",
                prompt="bad",
                acceptance=["bad"],
                category="pressure",
            ),
            EvalCase(
                id="explicit-release",
                name="Explicit release",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
            EvalCase(
                id="explicit-smoke",
                name="Explicit smoke",
                prompt="smoke",
                acceptance=["smoke"],
                eval_modes=("smoke",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="smoke")
        self.assertEqual([case.id for case in selected], ["happy", "explicit-smoke"])

    def test_release_mode_keeps_all_cases_by_default(self) -> None:
        cases = [
            EvalCase(id="happy", name="Happy", prompt="ok", acceptance=["ok"], category="happy"),
            EvalCase(
                id="explicit-smoke",
                name="Explicit smoke",
                prompt="smoke",
                acceptance=["smoke"],
                eval_modes=("smoke",),
            ),
            EvalCase(
                id="explicit-release",
                name="Explicit release",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="release")
        self.assertEqual([case.id for case in selected], ["happy", "explicit-release"])

    def test_release_mode_keeps_dual_tagged_smoke_cases_for_live_runners(self) -> None:
        cases = [
            EvalCase(
                id="discovery-round-one",
                name="Discovery round one",
                prompt="discover",
                acceptance=["discover"],
                smoke_mode="discovery-round-one",
                eval_modes=("smoke", "release"),
            ),
            EvalCase(
                id="smoke-only-discovery",
                name="Smoke only discovery",
                prompt="smoke",
                acceptance=["smoke"],
                smoke_mode="discovery-round-six",
                eval_modes=("smoke",),
            ),
            EvalCase(
                id="release-only",
                name="Release only",
                prompt="release",
                acceptance=["release"],
                eval_modes=("release",),
            ),
        ]

        selected = _filter_cases_for_eval_mode(cases, eval_mode="release")
        routed = [case for case in selected if not _is_smoke_only_case(case)]
        self.assertEqual([case.id for case in routed], ["discovery-round-one", "release-only"])

    def test_load_evals_parses_eval_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            evals_path = Path(tmpdir) / "evals.yaml"
            evals_path.write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: sample
                        name: sample
                        prompt: hi
                        acceptance: ["ok"]
                        eval_modes: [smoke, release]
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            cases = load_evals(evals_path)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0].eval_modes, ("smoke", "release"))

    def test_new_family_contract_cases_survive_smoke_filter(self) -> None:
        evals_path = SKILL_DIR / "references" / "evals.yaml"

        cases = load_evals(evals_path)
        selected = _filter_cases_for_eval_mode(cases, eval_mode="smoke")
        selected_ids = {case.id for case in selected}

        self.assertTrue(
            {
                "clarification-package-ambiguous",
                "plugin-only-handoff",
                "mixed-authoring-install-handoff",
                "audit-package-validation-first",
                "provenance-import-rollback",
                "builder-round-metadata-contract",
            }.issubset(selected_ids)
        )

    def test_preflight_codex_live_runner_rejects_repo_local_home_without_auth(self) -> None:
        """
        Verifies that _preflight_codex_live_runner rejects a repository-local `.codex` directory when the user's default Codex home is unauthenticated.

        Asserts that no warnings are returned, exactly one error is produced, and that the error message includes:
        - the phrase "missing authenticated Codex state",
        - guidance that a repo-local `.codex` is suitable only for discovery/static smoke, and
        - the filesystem path to the default home `.codex`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            repo_home = workspace_root / ".codex"
            repo_home.mkdir()
            home_root = workspace_root / "home-root"
            default_home = home_root / ".codex"
            default_home.mkdir(parents=True)
            (default_home / "auth.json").write_text("{}", encoding="utf-8")

            with unittest.mock.patch("run_skill_evals.Path.home", return_value=home_root):
                errors, warnings = _preflight_codex_live_runner(
                    workspace_root=workspace_root,
                    codex_bin=None,
                    codex_home=repo_home,
                )

        self.assertEqual(warnings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("missing authenticated Codex state", errors[0])
        self.assertIn("Repo-local `.codex` is suitable for discovery/static smoke", errors[0])
        self.assertIn(str(default_home), errors[0])

    def test_preflight_codex_live_runner_accepts_logged_in_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            codex_home = workspace_root / ".codex"
            codex_home.mkdir()
            (codex_home / "auth.json").write_text("{}", encoding="utf-8")
            fake_proc = unittest.mock.Mock(returncode=0, stdout="Logged in using ChatGPT\n", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                errors, warnings = _preflight_codex_live_runner(
                    workspace_root=workspace_root,
                    codex_bin=None,
                    codex_home=codex_home,
                )

        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        mocked_run.assert_called_once()

    def test_preflight_codex_live_runner_warns_when_env_auth_is_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            codex_home = workspace_root / ".codex"
            codex_home.mkdir()
            fake_proc = unittest.mock.Mock(returncode=1, stdout="Not logged in\n", stderr="")

            with unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc):
                with unittest.mock.patch.dict("run_skill_evals.os.environ", {"OPENAI_API_KEY": "sk-test"}, clear=False):
                    errors, warnings = _preflight_codex_live_runner(
                        workspace_root=workspace_root,
                        codex_bin=None,
                        codex_home=codex_home,
                    )

        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("auth environment variables are present", warnings[0])

    def test_isolated_codex_home_copies_auth_config_and_keeps_sessions_private(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            home_root = Path(tmpdir) / "home-root"
            default_home = home_root / ".codex"
            default_home.mkdir(parents=True)
            (default_home / "auth.json").write_text('{"token":"test"}', encoding="utf-8")
            (default_home / "config.toml").write_text("[profiles.test]\nmodel = \"gpt-test\"\n", encoding="utf-8")

            with unittest.mock.patch("run_skill_evals.Path.home", return_value=home_root):
                with unittest.mock.patch.dict("run_skill_evals.os.environ", {}, clear=True):
                    isolated_home, warnings = _isolated_codex_home_for_eval()

        self.assertNotEqual(isolated_home, default_home)
        self.assertTrue((isolated_home / "auth.json").exists())
        self.assertTrue((isolated_home / "config.toml").exists())
        self.assertTrue((isolated_home / "sessions").is_dir())
        self.assertTrue((isolated_home / "logs").is_dir())
        self.assertIn("Using isolated CODEX_HOME", "\n".join(warnings))

    def test_isolated_codex_config_drops_mcp_servers(self) -> None:
        source = textwrap.dedent(
            """
            model = "gpt-test"

            [profiles.test]
            model = "gpt-profile"

            [mcp_servers.linear]
            url = "https://mcp.linear.app/mcp"

            [mcp_servers.linear.tools.save_comment]
            enabled = false

            [tools]
            web_search = true
            """
        ).lstrip()

        scrubbed = _scrub_mcp_servers_from_toml(source)

        self.assertIn("[profiles.test]", scrubbed)
        self.assertIn("[tools]", scrubbed)
        self.assertNotIn("[mcp_servers.linear]", scrubbed)
        self.assertNotIn("save_comment", scrubbed)

    def test_run_codex_exec_ignores_user_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr, warnings), (0, "", "", []))
        cmd = mocked_run.call_args.args[0]
        self.assertIn("--ignore-user-config", cmd)
        self.assertLess(cmd.index("--ignore-user-config"), cmd.index("--sandbox"))

    def test_run_codex_exec_skips_ignore_user_config_when_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=False,
            ), unittest.mock.patch("run_skill_evals.sp.run", return_value=fake_proc) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr), (0, "", ""))
        self.assertTrue(any("--ignore-user-config" in warning for warning in warnings))
        cmd = mocked_run.call_args.args[0]
        self.assertNotIn("--ignore-user-config", cmd)

    def test_run_codex_exec_retries_no_output_timeout_once(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            fake_proc = unittest.mock.Mock(returncode=0, stdout="done", stderr="")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=[
                    sp.TimeoutExpired(cmd=["codex"], timeout=1),
                    fake_proc,
                ],
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

        self.assertEqual((rc, stdout, stderr), (0, "done", ""))
        self.assertEqual(mocked_run.call_count, 2)
        self.assertTrue(any("retrying once" in warning for warning in warnings))

    def test_run_codex_exec_preserves_timeout_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            jsonl_path = workspace_root / "trace.jsonl"

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=sp.TimeoutExpired(
                    cmd=["codex"],
                    timeout=1,
                    output="partial stdout",
                    stderr="partial stderr",
                ),
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=jsonl_path,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

            persisted_jsonl = jsonl_path.read_text(encoding="utf-8")

        self.assertEqual(rc, 124)
        self.assertEqual(stdout, "partial stdout")
        self.assertIn("partial stderr", stderr)
        self.assertIn("codex exec timed out after 1.0 seconds.", stderr)
        self.assertEqual(mocked_run.call_count, 1)
        self.assertEqual(warnings, [])
        self.assertEqual(persisted_jsonl, "partial stdout")

    def test_run_codex_exec_keeps_last_message_artifact_on_timeout(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace_root = Path(tmpdir)
            output_last_message_path = workspace_root / "last.txt"
            output_last_message_path.write_text("partial final message", encoding="utf-8")

            with unittest.mock.patch(
                "run_skill_evals._codex_supports_exec_flag",
                return_value=True,
            ), unittest.mock.patch(
                "run_skill_evals.sp.run",
                side_effect=sp.TimeoutExpired(cmd=["codex"], timeout=1),
            ) as mocked_run:
                rc, stdout, stderr, warnings = run_codex_exec(
                    workspace_root=workspace_root,
                    prompt="Route only.",
                    output_last_message_path=output_last_message_path,
                    output_schema_path=None,
                    sandbox="read-only",
                    ask_for_approval=None,
                    model=None,
                    profile=None,
                    codex_home=workspace_root / ".codex",
                    jsonl_path=None,
                    codex_bin=None,
                    timeout_sec=1,
                    timeout_profile="default",
                )

            last_message = output_last_message_path.read_text(encoding="utf-8")

        self.assertEqual((rc, stdout), (124, ""))
        self.assertIn("codex exec timed out after 1.0 seconds.", stderr)
        self.assertEqual(mocked_run.call_count, 1)
        self.assertEqual(last_message, "partial final message")
        self.assertEqual(warnings, [])

    def test_timeout_with_only_subprocess_stderr_is_no_output(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text="Command timed out after 10 seconds",
                exit_code=124,
            ),
            "timeout_no_output",
        )

    def test_write_junit_report_outputs_failures(self) -> None:
        summary = {
            "skill": "skill-builder",
            "generated_at": "2026-03-21T00:00:00Z",
            "run_id": "run-1",
            "tier2_mode": "warn",
            "tier1_failures": 1,
            "cases": [
                {
                    "id": "good",
                    "name": "good",
                    "timeout_sec": 10,
                    "tier1_failed": False,
                    "tier2_failed": False,
                    "tier1_failures": [],
                    "tier2_findings": [],
                    "warnings": [],
                    "dir": "/tmp/good",
                },
                {
                    "id": "bad",
                    "name": "bad",
                    "timeout_sec": 20,
                    "tier1_failed": True,
                    "tier2_failed": False,
                    "tier1_failures": ["runner failed"],
                    "tier2_findings": [],
                    "warnings": ["warned"],
                    "dir": "/tmp/bad",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "junit.xml"
            _write_junit_report(summary, out)
            tree = ET.parse(out)

        suite = tree.getroot()
        self.assertEqual(suite.tag, "testsuite")
        self.assertEqual(suite.attrib["tests"], "2")
        self.assertEqual(suite.attrib["failures"], "1")
        cases = suite.findall("testcase")
        self.assertEqual(len(cases), 2)
        self.assertIsNotNone(cases[1].find("failure"))

    def test_write_junit_report_marks_tier2_fail_mode_cases_as_failures(self) -> None:
        summary = {
            "skill": "skill-builder",
            "generated_at": "2026-03-21T00:00:00Z",
            "run_id": "run-2",
            "tier2_mode": "fail",
            "tier1_failures": 0,
            "cases": [
                {
                    "id": "tier2-only",
                    "name": "tier2-only",
                    "timeout_sec": 15,
                    "tier1_failed": False,
                    "tier2_failed": True,
                    "tier1_failures": [],
                    "tier2_findings": ["rubric score below threshold"],
                    "warnings": [],
                    "dir": "/tmp/tier2-only",
                }
            ],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "junit.xml"
            _write_junit_report(summary, out)
            tree = ET.parse(out)

        suite = tree.getroot()
        self.assertEqual(suite.attrib["failures"], "1")
        case_el = suite.find("testcase")
        assert case_el is not None
        self.assertIsNotNone(case_el.find("failure"))
        self.assertIsNone(case_el.find("skipped"))

    def test_release_manifest_includes_final_artifact_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: demo-skill
                    version: "1.2.3"
                    compatibility: codex
                    release_channel: stable
                    schema_version: 1
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

                    ## Round 6: Confirmation

                    Does this capture it well enough for me to build?
                    Anything to add or change before I build it?
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
                      - id: discovery-round-one
                        name: discovery smoke
                        prompt: Help define the skill.
                        smoke_mode: discovery-round-one
                        should_trigger: true
                        acceptance:
                          - contains: "Round 1 question:"
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

        self.assertIn("junit", summary["artifacts"])
        self.assertEqual(summary["cases"][0]["warnings"], [])
        self.assertTrue(summary["cases"][0]["runners"]["discovery-smoke"]["metrics"]["selected_skill"])
        self.assertEqual(summary["cases"][0]["riteway"]["unit"], "discovery smoke")
        self.assertIn("eval_contract_migration", summary)
        self.assertIn("release_manifest", summary["artifacts"])
        self.assertEqual(release_manifest["artifacts"]["junit"], summary["artifacts"]["junit"])
        self.assertEqual(
            release_manifest["artifacts"]["release_manifest"],
            summary["artifacts"]["release_manifest"],
        )

    def test_pass_rate_policy_calibrates_only_when_artifact_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            case_dir = Path(tmpdir) / "reports" / "demo-skill" / "01-calibrated"
            case_dir.mkdir(parents=True)
            (case_dir / "calibration.json").write_text('{"baseline": 0.9}\n', encoding="utf-8")

            self.assertEqual(
                _resolve_existing_optional_case_artifact_path(case_dir, "calibration.json"),
                str((case_dir / "calibration.json").resolve()),
            )
            self.assertIsNone(
                _resolve_existing_optional_case_artifact_path(case_dir, "missing-calibration.json")
            )

    def test_snyk_release_gate_is_not_required_for_skill_md_only_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")

            self.assertEqual(_dependency_manifest_paths(skill_dir), [])
            self.assertTrue(_snyk_release_gate_passed({"required": False, "status": "not_applicable"}))

    def test_snyk_release_gate_requires_success_for_manifest_backed_packages(self) -> None:
        self.assertTrue(_snyk_release_gate_passed({"required": True, "status": "success"}))
        blocking_statuses = [
            "not_applicable",
            "blocked_auth",
            "blocked_missing_binary",
            "blocked_no_supported_projects",
            "advisory",
            "error",
        ]
        for status in blocking_statuses:
            self.assertFalse(_snyk_release_gate_passed({"required": True, "status": status}))

    def test_dependency_manifest_detection_ignores_generated_dependency_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            (skill_dir / "node_modules" / "left-pad").mkdir(parents=True)
            (skill_dir / "package.json").write_text("{}", encoding="utf-8")
            (skill_dir / "node_modules" / "left-pad" / "package.json").write_text("{}", encoding="utf-8")

            manifests = _dependency_manifest_paths(skill_dir)

        self.assertEqual([path.name for path in manifests], ["package.json"])

    def test_dependency_manifest_detection_includes_plugin_root_package(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            plugin_root = Path(tmpdir) / "Plugins" / "demo-plugin"
            skill_dir = plugin_root / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            (plugin_root / "package.json").write_text("{}", encoding="utf-8")

            manifests = _dependency_manifest_paths(skill_dir)
            scan_roots = _release_dependency_scan_roots(skill_dir)

        self.assertEqual([path.name for path in manifests], ["package.json"])
        self.assertEqual(scan_roots[-1].name, "demo-plugin")

    @unittest.mock.patch("run_skill_evals.shutil.which", return_value="/usr/local/bin/snyk")
    @unittest.mock.patch("run_skill_evals.sp.run")
    def test_release_mode_blocks_manifest_backed_package_without_snyk_auth(self, mock_run, _mock_which) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\nversion: '1.0.0'\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            (skill_dir / "package.json").write_text('{"name":"demo-skill"}\n', encoding="utf-8")
            (refs_dir / "discovery-interview.md").write_text(
                "## Request user input mini-templates\n\nWhat should this skill do?\n\n## Copy-paste payload examples\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: discovery-round-one
                        name: discovery smoke
                        prompt: Help define the skill.
                        smoke_mode: discovery-round-one
                        eval_modes: [release]
                        should_trigger: true
                        acceptance:
                          - contains: "Round 1 question:"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            mock_run.side_effect = [
                unittest.mock.Mock(returncode=0, stdout="abc123\n", stderr=""),
                unittest.mock.Mock(returncode=0, stdout="main\n", stderr=""),
                unittest.mock.Mock(returncode=2, stdout="", stderr="Use snyk auth to authenticate."),
            ]

            reports_dir = Path(tmpdir) / "reports"
            exit_code = main(
                [
                    str(skill_dir),
                    "--runner",
                    "discovery-smoke",
                    "--eval-mode",
                    "release",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))
            release_manifest = json.loads((report_dirs[-1] / "release_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["decision"], "blocked")
        self.assertEqual(summary["security_dependency_screening"]["status"], "blocked_auth")
        self.assertEqual(
            release_manifest["run"]["security_dependency_screening"]["status"],
            "blocked_auth",
        )

    def test_runner_capacity_blocker_marks_summary_decision_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir, unittest.mock.patch(
            "run_skill_evals._preflight_codex_live_runner",
            return_value=([], []),
        ), unittest.mock.patch(
            "run_skill_evals.run_codex_exec",
            return_value=(
                1,
                (
                    '{"type":"error","message":"You\'ve hit your usage limit for '
                    'GPT-5.3-Codex-Spark. Switch to another model now."}'
                ),
                "",
                [],
            ),
        ):
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text("---\nname: demo-skill\n---\n", encoding="utf-8")
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    cases:
                      - id: capacity-case
                        name: capacity case
                        prompt: Use the skill.
                        eval_modes: [smoke]
                        should_trigger: true
                        acceptance:
                          - contains: "done"
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
                    "codex",
                    "--eval-mode",
                    "smoke",
                    "--reports-dir",
                    str(reports_dir),
                    "--format",
                    "json",
                ]
            )
            report_dirs = sorted((reports_dir / "demo-skill").glob("*"))
            summary = json.loads((report_dirs[-1] / "summary.json").read_text(encoding="utf-8"))

        self.assertEqual(exit_code, 2)
        self.assertEqual(summary["decision"], "blocked")
        self.assertEqual(summary["blocked_cases"], 1)
        self.assertEqual(summary["blocked_class_summary"]["blocked_runtime"], 1)

    def test_discovery_smoke_requires_explicit_smoke_mode_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "behavior-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """
                    ---
                    name: behavior-skill
                    ---

                    ## Workflow
                    Do behavior work.
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
                      - id: behavior
                        name: behavior
                        prompt: Review this skill behavior.
                        acceptance:
                          - contains: "validation"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            reports_dir = Path(tmpdir) / "reports"
            with unittest.mock.patch("sys.stderr") as stderr:
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

            self.assertEqual(exit_code, 1)
            self.assertIn("requires eval cases with `smoke_mode`", "".join(call.args[0] for call in stderr.write.call_args_list if call.args))

    def test_main_reports_invalid_reporting_metadata_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "demo-skill"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: demo-skill\n---\n\n# Demo\n",
                encoding="utf-8",
            )
            (refs_dir / "evals.yaml").write_text(
                textwrap.dedent(
                    """
                    schema_version: "2.0"
                    reporting:
                      preferred_source_format: [MDX]
                    cases:
                      - id: discovery-round-one
                        name: discovery smoke
                        prompt: Help define the skill.
                        smoke_mode: discovery-round-one
                        should_trigger: true
                        acceptance:
                          - contains: "Round 1 question:"
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            stderr = io.StringIO()
            with unittest.mock.patch("sys.stderr", stderr):
                exit_code = main(
                    [
                        str(skill_dir),
                        "--runner",
                        "discovery-smoke",
                        "--reports-dir",
                        str(Path(tmpdir) / "reports"),
                        "--format",
                        "json",
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertIn("ERROR:", stderr.getvalue())
        self.assertIn("preferred_source_format", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_discovery_smoke_uses_skill_specific_questions_and_canonical_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "docs-expert"
            refs_dir = skill_dir / "references"
            refs_dir.mkdir(parents=True)
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                textwrap.dedent(
                    """
                    ---
                    name: docs-expert
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

                    Which documentation surface should this update target first?

                    ## Copy-paste payload examples

                    ## Round 6: Confirmation

                    Does this capture the docs work well enough for me to implement?
                    Anything to add or change before I implement it?
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            round_one_case = EvalCase(
                id="round-one",
                name="round-one",
                prompt="discover",
                acceptance=[],
                smoke_mode="discovery-round-one",
            )
            round_six_case = EvalCase(
                id="round-six",
                name="round-six",
                prompt="discover",
                acceptance=[],
                smoke_mode="discovery-round-six",
            )
            round_one_path = skill_dir / "round-one.txt"
            round_six_path = skill_dir / "round-six.txt"

            round_one_exit, round_one_response, _, _ = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=round_one_case,
                output_last_message_path=round_one_path,
            )
            round_six_exit, round_six_response, _, _ = run_discovery_smoke(
                skill_md_path=skill_md,
                skill_dir=skill_dir,
                case=round_six_case,
                output_last_message_path=round_six_path,
            )
            self.assertEqual(round_one_exit, 0)
            self.assertIn("## Inputs", round_one_response)
            self.assertIn("## Outputs", round_one_response)
            self.assertIn("Which documentation surface should this update target first?", round_one_response)
            self.assertEqual(round_one_path.read_text(encoding="utf-8"), round_one_response)

            self.assertEqual(round_six_exit, 0)
            self.assertIn("## Outputs", round_six_response)
            self.assertIn("Does this capture the docs work well enough for me to implement?", round_six_response)
            self.assertIn("Anything to add or change before I implement it?", round_six_response)
            self.assertEqual(round_six_path.read_text(encoding="utf-8"), round_six_response)

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
