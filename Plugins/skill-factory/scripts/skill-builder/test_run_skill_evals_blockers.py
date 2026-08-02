#!/usr/bin/env python3
"""Regression tests for run_skill_evals eval-mode behavior."""

from __future__ import annotations

import sys
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
    _acceptance_skip_reason,
    _classify_runner_blocker,
    _load_evals_document,
    _is_runner_runtime_blocked,
    evaluate_assertions_json,
    evaluate_assertions_text,
)
from deterministic_trace_checks import evaluate_trace  # noqa: E402




class RunSkillEvalsBlockerTests(unittest.TestCase):
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
        assertions = [{"type": "expected_signal", "value": "Starts from inspected traces, labels, metrics, or files and names the smallest next validation step instead of treating trust as a generic quality score."}, {"type": "regex", "value": "(validation|evidence|scope|workflow)"}]
        for runner, output in [
            (evaluate_assertions_text, "I inspected the trace and label evidence, then identified the smallest next validation step before changing the workflow."),
            (evaluate_assertions_json, {"evidence": "inspected trace labels", "next_check": "smallest validation step", "quality": "not a generic trust score"}),
        ]:
            self.assertEqual(runner(output, assertions, skill_name="improve-agent-native", selected_skill=True), [])

        semantic = [{"type": "semantic_requirements", "requirements": [
            {"id": "stable_read", "all_of": ["stable", "side-effect-free"]},
            {"id": "single_read", "all_of": ["two calls", "one read"]},
            {"id": "both_branches", "all_of": ["validation", "enabled", "disabled"]},
        ]}]
        passing = "stable and side-effect-free; two calls become one read; validation covers enabled and disabled branches"
        self.assertEqual(evaluate_assertions_text(passing, semantic, skill_name="simplify", selected_skill=True), [])
        for requirement_id, output in {"stable_read": "two calls become one read; validation covers enabled and disabled branches", "single_read": "stable and side-effect-free; validation covers enabled and disabled branches", "both_branches": "stable and side-effect-free; two calls become one read"}.items():
            failure = evaluate_assertions_text(output, semantic, skill_name="simplify", selected_skill=True)
            self.assertEqual(failure[0], f"semantic_requirements failed: {requirement_id}")
        for requirements, message in [([], "missing non-empty requirements list"), ([{"id": "bad", "all_of": []}], "requirement 'bad' needs non-empty any_of and/or all_of strings")]:
            failure = evaluate_assertions_text("evidence", [{"type": "semantic_requirements", "requirements": requirements}], skill_name="simplify", selected_skill=True)
            self.assertEqual(failure[0], f"semantic_requirements {message}")
        self.assertEqual(evaluate_assertions_text("**Outcome:** `no_justified_edit`", [{"type": "text_field_equals", "field": "Outcome", "value": "no_justified_edit"}], skill_name="simplify", selected_skill=True), [])
        case = next(item for item in _load_evals_document(REPO_ROOT / "Skills/agent-ops/simplify/references/evals.yaml")["cases"] if item["id"] == "edge-efficiency-rubric")
        self.assertEqual(case["acceptance"][1]["type"], "semantic_requirements")


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


    def test_discovery_question_assertion_accepts_scope_question_before_edits(self) -> None:
        failures = evaluate_assertions_text(
            (
                "Before making edits, which documentation path or surface should I inspect first: "
                "canonical docs, generated projections, publication surfaces, or audit-only?"
            ),
            [{"type": "discovery_question", "value": "ask for scope before edits"}],
            skill_name="technical-writer",
            selected_skill=True,
        )

        self.assertEqual(failures, [])


    def test_discovery_question_assertion_rejects_edit_claims(self) -> None:
        failures = evaluate_assertions_text(
            "I updated the README. Which docs should I inspect next?",
            [{"type": "discovery_question", "value": "ask for scope before edits"}],
            skill_name="technical-writer",
            selected_skill=True,
        )

        self.assertEqual(failures, ["discovery_question failed: response claimed an edit before discovery"])


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


    def test_empty_successful_exit_with_tool_schema_error_is_runtime_blocker(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text='{"type":"turn.completed"}',
                stderr_text=(
                    "failed to parse function arguments: invalid type: string "
                    "'500', expected usize\n"
                    "Warning: no last agent message; wrote empty content to final.txt"
                ),
                exit_code=0,
            ),
            "blocked_runtime",
        )
        self.assertIsNone(
            _classify_runner_blocker(
                output_text="Projection report: canonical source is editable.",
                stdout_text='{"type":"turn.completed"}',
                stderr_text="failed to parse function arguments: invalid type: string '500', expected usize",
                exit_code=0,
            )
        )


    def test_local_model_refresh_failure_is_runtime_blocker(self) -> None:
        self.assertEqual(
            _classify_runner_blocker(
                output_text="",
                stdout_text="",
                stderr_text=(
                    "ERROR codex_models_manager::manager: failed to refresh available models: "
                    "stream disconnected before completion: error sending request for url "
                    "(http://localhost:11434/v1/models?client_version=0.141.0)"
                ),
                exit_code=1,
            ),
            "blocked_runtime",
        )


    def test_local_model_refresh_warning_with_final_output_is_scored(self) -> None:
        self.assertIsNone(
            _classify_runner_blocker(
                output_text="Which document in the repository would you like me to review first?",
                stdout_text="",
                stderr_text=(
                    "ERROR codex_models_manager::manager: failed to refresh available models: "
                    "stream disconnected before completion: failed to decode models response: "
                    "missing field models at line 1 column 527"
                ),
                exit_code=0,
            )
        )


    def test_sandbox_noise_with_final_output_is_scored(self) -> None:
        self.assertIsNone(
            _classify_runner_blocker(
                output_text="Validation: blocked because the command needs approval.",
                stdout_text="",
                stderr_text=(
                    "exec_command failed: sandbox-exec: sandbox_apply: Operation not permitted"
                ),
                exit_code=0,
            )
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




if __name__ == "__main__":
    unittest.main()
