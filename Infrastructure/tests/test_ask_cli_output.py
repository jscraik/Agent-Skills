"""Tests for extracted ask CLI output and exit helpers."""

import contextlib
import io
import unittest

from ask_test_paths import ensure_ask_lib_path


ensure_ask_lib_path()

from ask.cli_exit import exit_code_for_errors  # noqa: E402
from ask.cli_output import (  # noqa: E402
    print_first_validation_command,
    print_readiness_overview,
    replay_command,
)
from ask.envelope import ErrorCode, ErrorObject, ExitCode  # noqa: E402


class TestPrintReadinessOverview(unittest.TestCase):
    def test_prints_contract_status_and_sections(self):
        payload = {
            "readiness_overview": {
                "contract_status": "ready",
                "contract_gap_count": 0,
                "ready_contract_sections": ["profiles", "events"],
                "blocked_contract_sections": ["memory"],
            }
        }

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_readiness_overview(payload)
            output = buffer.getvalue()

        self.assertIn("Readiness: ready (0 gaps)", output)
        self.assertIn("Ready sections: profiles, events", output)
        self.assertIn("Blocked sections: memory", output)

    def test_skips_payload_without_complete_overview(self):
        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_readiness_overview({"readiness_overview": {"contract_status": "ready"}})
            output = buffer.getvalue()

        self.assertEqual(output, "")

    def test_skips_malformed_section_values(self):
        payload = {
            "readiness_overview": {
                "contract_status": "blocked",
                "contract_gap_count": 1,
                "ready_contract_sections": "profiles",
                "blocked_contract_sections": [None, 42],
            }
        }

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_readiness_overview(payload)
            output = buffer.getvalue()

        self.assertEqual(output, "Readiness: blocked (1 gaps)\n")

    def test_filters_mixed_section_values(self):
        payload = {
            "readiness_overview": {
                "contract_status": "ready",
                "contract_gap_count": 0,
                "ready_contract_sections": ["profiles", None, "", "events"],
                "blocked_contract_sections": ("memory", 7),
            }
        }

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_readiness_overview(payload)
            output = buffer.getvalue()

        self.assertIn("Ready sections: profiles, events", output)
        self.assertIn("Blocked sections: memory", output)


class TestPrintFirstValidationCommand(unittest.TestCase):
    def test_prefers_top_level_validation_commands(self):
        payload = {
            "validation_commands": ["./bin/ask skills list --json --robot"],
            "operation_context": {"validation_commands": ["fallback"]},
        }

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output.strip(), "Validation: ./bin/ask skills list --json --robot")

    def test_uses_operation_context_fallback(self):
        payload = {"operation_context": {"validation_commands": ["./bin/ask repo status --json --robot"]}}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output.strip(), "Validation: ./bin/ask repo status --json --robot")

    def test_skips_missing_validation_commands(self):
        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command({})
            output = buffer.getvalue()

        self.assertEqual(output, "")

    def test_skips_non_dict_operation_context(self):
        payload = {"operation_context": ["not", "a", "mapping"]}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output, "")

    def test_skips_non_sequence_validation_commands(self):
        payload = {"validation_commands": "./bin/ask repo status --json --robot"}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output, "")

    def test_skips_non_sequence_operation_context_validation_commands(self):
        payload = {"operation_context": {"validation_commands": "./bin/ask repo status --json --robot"}}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output, "")

    def test_uses_first_string_validation_command(self):
        payload = {"validation_commands": [None, "", "./bin/ask repo doctor --json --robot"]}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output.strip(), "Validation: ./bin/ask repo doctor --json --robot")

    def test_skips_validation_commands_without_string_values(self):
        payload = {"validation_commands": [None, 7]}

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            print_first_validation_command(payload)
            output = buffer.getvalue()

        self.assertEqual(output, "")


class TestReplayCommand(unittest.TestCase):
    def test_quotes_shell_sensitive_parts(self):
        command = replay_command("./bin/ask", "skills", "improve", "fix PR review comments faster", None)

        self.assertEqual(command, "./bin/ask skills improve 'fix PR review comments faster'")


class TestExitCodeForErrors(unittest.TestCase):
    def test_maps_validation_to_validation_exit_code(self):
        errors = [ErrorObject(code=ErrorCode.ERR_VALIDATION, message="invalid")]

        self.assertEqual(exit_code_for_errors(errors), int(ExitCode.ERR_VALIDATION))

    def test_maps_auth_to_auth_exit_code(self):
        errors = [ErrorObject(code=ErrorCode.ERR_AUTH, message="auth failed")]

        self.assertEqual(exit_code_for_errors(errors), int(ExitCode.ERR_AUTH))

    def test_empty_errors_default_to_runtime_exit_code(self):
        self.assertEqual(exit_code_for_errors([]), int(ExitCode.ERR_RUNTIME))

    def test_unknown_error_code_defaults_to_runtime_exit_code(self):
        errors = [ErrorObject(code="ERR_NEW_KIND", message="unknown")]

        self.assertEqual(exit_code_for_errors(errors), int(ExitCode.ERR_RUNTIME))


if __name__ == "__main__":
    unittest.main()
