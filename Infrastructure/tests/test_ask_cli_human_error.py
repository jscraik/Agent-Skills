"""Direct rendering contracts for human-facing ask CLI errors."""

from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace

from ask_test_paths import ensure_ask_lib_path


ensure_ask_lib_path()

from ask.cli_human_error import render_error  # noqa: E402
from ask.envelope import CallResult, ErrorCode, ErrorObject  # noqa: E402


def _args(topic: str, action: str, *, verbose: bool = False) -> SimpleNamespace:
    return SimpleNamespace(topic=topic, action=action, verbose=verbose)


def _result(message: str, *, suggestion: str | None = None) -> CallResult:
    return CallResult(
        status="error",
        errors=[ErrorObject(ErrorCode.ERR_VALIDATION, message, suggestion)],
    )


def _render(args: SimpleNamespace, result: CallResult) -> str:
    with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
        render_error(args, result)
        return buffer.getvalue()


class TestRenderError(unittest.TestCase):
    def test_renders_route_context_before_error_and_suggestion(self) -> None:
        result = _result("route failed", suggestion="Choose one candidate")
        result.data["decision"] = {
            "decision_status": "ambiguous",
            "failure_class": "multiple_matches",
            "operator_action": "choose a path",
            "ambiguity_set": [
                {"name": "alpha", "path": "Skills/alpha", "confidence": 0.5},
            ],
            "validation_commands": ["./bin/ask skills route alpha --json --robot"],
        }

        output = _render(_args("skills", "route"), result)

        self.assertEqual(
            output,
            "🧭 Route decision: ambiguous\n"
            "Failure class: multiple_matches\n"
            "Operator action: choose a path\n"
            "Ambiguity set:\n"
            "  - alpha (Skills/alpha) confidence=0.5000\n"
            "Validation: ./bin/ask skills route alpha --json --robot\n\n"
            "❌ Error: route failed\n\n💡 Choose one candidate\n",
        )

    def test_renders_audit_diagnostics_without_first_failure_suffix(self) -> None:
        result = _result("audit failed First failures: stale check")
        result.data.update(
            {
                "diagnostics": {"stdout": "diagnostics output"},
                "security_gate": {"stdout": "security output"},
            }
        )

        output = _render(_args("skills", "audit"), result)

        self.assertIn("❌ Error: audit failed\n", output)
        self.assertNotIn("First failures", output)
        self.assertIn("diagnostics output\n", output)
        self.assertIn("security output\n", output)
        self.assertIn(
            "ask skills audit backend-platform/cli-spec --level strict", output
        )

    def test_renders_goal_context_with_prompts_before_error(self) -> None:
        result = _result("goal failed")
        result.data["goal_decision"] = {
            "decision_status": "needs_input",
            "failure_class": "ambiguous_goal",
            "operator_action": "pick a review scope",
            "disambiguation_prompts": ["Which changed files are in scope?"],
            "validation_commands": ["./bin/ask skills goal simplify --json --robot"],
        }

        output = _render(_args("skills", "goal"), result)

        self.assertEqual(
            output,
            "🎯 Goal decision: needs_input\n"
            "Failure class: ambiguous_goal\n"
            "Operator action: pick a review scope\n"
            "Disambiguation prompts:\n"
            "  - Which changed files are in scope?\n"
            "Validation: ./bin/ask skills goal simplify --json --robot\n\n"
            "❌ Error: goal failed\n",
        )

    def test_elides_plugin_command_output_without_verbose_flag(self) -> None:
        result = _result("plugin failed")
        result.data.update(
            {
                "raw_output": "runner output",
                "raw_error": "runner error",
                "validation_commands": [
                    "./bin/ask plugins install example --json --robot"
                ],
                "command_runs": [
                    {
                        "step": "install",
                        "command": "plugin install",
                        "returncode": 1,
                        "stdout": "hidden stdout",
                        "stderr": "hidden stderr",
                    },
                ],
            }
        )

        output = _render(_args("plugins", "install"), result)

        self.assertIn("runner output\nrunner error\n", output)
        self.assertIn(
            "Validation: ./bin/ask plugins install example --json --robot", output
        )
        self.assertIn("  (Stdout elided. Use --verbose to view)", output)
        self.assertIn("  (Stderr elided. Use --verbose to view)", output)
        self.assertNotIn("hidden stdout", output)
        self.assertNotIn("hidden stderr", output)

    def test_renders_plugin_command_output_with_verbose_flag(self) -> None:
        result = _result("plugin failed")
        result.data["command_runs"] = [
            {
                "step": "install",
                "command": "plugin install",
                "returncode": 1,
                "stdout": "shown stdout",
                "stderr": "shown stderr",
            },
        ]

        output = _render(_args("plugins", "install", verbose=True), result)

        self.assertIn("  Stdout:\n'shown stdout'", output)
        self.assertIn("  Stderr:\n'shown stderr'", output)

    def test_limits_family_benchmark_output_to_three_failures(self) -> None:
        result = _result("audit failed")
        result.data["family_benchmarks"] = {
            "exit_code": 1,
            "stdout": "\n".join(f"FAIL case {number}" for number in range(4)),
        }

        output = _render(_args("skills", "audit"), result)

        self.assertIn("🔎 Family benchmark failures (first 3):", output)
        self.assertIn("   ... and 1 more (use --json for full details)", output)

    def test_renders_repo_validation_before_raw_output(self) -> None:
        result = _result("validation failed")
        result.data.update(
            {
                "validation_commands": ["./bin/ask repo validate --json --robot"],
                "raw_output": "validator details",
            }
        )

        output = _render(_args("repo", "validate"), result)

        self.assertLess(output.index("Validation:"), output.index("validator details"))
        self.assertIn("ask repo check-stability --changed-files", output)


if __name__ == "__main__":
    unittest.main()
