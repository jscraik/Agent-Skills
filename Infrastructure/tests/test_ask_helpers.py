"""
Tests for pure helper functions in ask.cli_errors.

Covers extracted CLI recovery helpers:
  - get_closest_match
  - format_correction
  - _normalize_token
  - _extract_argparse_error
  - _example_commands
  - _merge_corrections
  - consume_global_prefix_flags
  - try_fuzzy_parse (key routing logic)
  - build_unknown_action_result
  - build_helpful_error
  - build_argument_error
  - parse_args_with_capture
"""
import argparse
import unittest

from ask_test_paths import ensure_ask_support_paths


ensure_ask_support_paths()

from ask.cli_errors import (  # noqa: E402
    _ambiguous_action_fix_suggestion,
    _closest_action_fix_suggestion,
    _closest_topic_fix_suggestion,
    _example_commands,
    _extract_argparse_error,
    _fallback_topic_fix_suggestion,
    _merge_corrections,
    _normalize_token,
    build_argument_error,
    build_helpful_error,
    build_unknown_action_result,
    consume_global_prefix_flags,
    format_correction,
    get_closest_match,
    parse_args_with_capture,
    try_fuzzy_parse,
)


# ---------------------------------------------------------------------------
# get_closest_match
# ---------------------------------------------------------------------------

class TestGetClosestMatch(unittest.TestCase):
    def test_exact_match_found(self):
        result = get_closest_match("skills", ["repo", "skills", "evals"])
        self.assertEqual(result, "skills")

    def test_close_match_found(self):
        result = get_closest_match("sklls", ["repo", "skills", "evals"])
        self.assertEqual(result, "skills")

    def test_no_match_returns_none(self):
        result = get_closest_match("zzz", ["repo", "skills", "evals"])
        self.assertIsNone(result)

    def test_empty_options_returns_none(self):
        result = get_closest_match("skills", [])
        self.assertIsNone(result)

    def test_custom_cutoff_restricts_matches(self):
        # With a very high cutoff the typo should not match
        result = get_closest_match("xkills", ["skills"], cutoff=0.99)
        self.assertIsNone(result)

    def test_returns_string_when_found(self):
        result = get_closest_match("repo", ["repo", "evals"])
        self.assertIsInstance(result, str)


# ---------------------------------------------------------------------------
# format_correction
# ---------------------------------------------------------------------------

class TestFormatCorrection(unittest.TestCase):
    def test_human_mode_suggests_correction(self):
        msg = format_correction("sklls", "skills")
        self.assertIn("skills", msg)
        self.assertNotIn("Robot mode", msg)

    def test_robot_mode_shows_robot_prefix(self):
        msg = format_correction("sklls", "skills", robot_mode=True)
        self.assertIn("Robot mode", msg)
        self.assertIn("skills", msg)

    def test_human_mode_suggests_using_corrected(self):
        msg = format_correction("sklls", "skills")
        self.assertIn("Did you mean", msg)

    def test_robot_mode_includes_tip(self):
        msg = format_correction("old", "new", robot_mode=True)
        self.assertIn("Tip", msg)

    def test_corrected_token_appears_in_human_output(self):
        # Human mode shows the corrected token in a "Did you mean" suggestion.
        msg = format_correction("typo-topic", "real-topic")
        self.assertIn("real-topic", msg)

    def test_original_token_appears_in_robot_output(self):
        msg = format_correction("typo-topic", "real-topic", robot_mode=True)
        self.assertIn("typo-topic", msg)


# ---------------------------------------------------------------------------
# _normalize_token
# ---------------------------------------------------------------------------

class TestNormalizeToken(unittest.TestCase):
    def test_lowercase(self):
        self.assertEqual(_normalize_token("SKILLS"), "skills")

    def test_strips_whitespace(self):
        self.assertEqual(_normalize_token("  repo  "), "repo")

    def test_replaces_underscore_with_dash(self):
        self.assertEqual(_normalize_token("doctor_catalog"), "doctor-catalog")

    def test_mixed_case_underscore_whitespace(self):
        self.assertEqual(_normalize_token("  FIX_Mise  "), "fix-mise")

    def test_empty_string(self):
        self.assertEqual(_normalize_token(""), "")

    def test_already_normalized(self):
        self.assertEqual(_normalize_token("skills"), "skills")


# ---------------------------------------------------------------------------
# _extract_argparse_error
# ---------------------------------------------------------------------------

class TestExtractArgparseError(unittest.TestCase):
    def test_none_input_returns_none(self):
        self.assertIsNone(_extract_argparse_error(None))

    def test_empty_string_returns_none(self):
        self.assertIsNone(_extract_argparse_error(""))

    def test_extracts_ask_error_line(self):
        stderr = "usage: ask ...\nask: error: invalid choice 'foo'\n"
        result = _extract_argparse_error(stderr)
        self.assertIsNotNone(result)
        self.assertIn("invalid choice", result)
        self.assertNotIn("ask: error:", result)

    def test_falls_back_to_last_line_when_no_ask_error_prefix(self):
        stderr = "line one\nline two\nfinal line"
        result = _extract_argparse_error(stderr)
        self.assertEqual(result, "final line")

    def test_strips_whitespace_from_extracted_line(self):
        stderr = "ask: error:   extra spaces   \n"
        result = _extract_argparse_error(stderr)
        self.assertEqual(result, "extra spaces")

    def test_whitespace_only_lines_are_skipped(self):
        stderr = "   \nask: error: real error\n   "
        result = _extract_argparse_error(stderr)
        self.assertIn("real error", result)


# ---------------------------------------------------------------------------
# _merge_corrections
# ---------------------------------------------------------------------------

class TestMergeCorrections(unittest.TestCase):
    def test_none_existing_returns_new(self):
        self.assertEqual(_merge_corrections(None, "new note"), "new note")

    def test_none_new_returns_existing(self):
        self.assertEqual(_merge_corrections("existing", None), "existing")

    def test_both_none_returns_none(self):
        self.assertIsNone(_merge_corrections(None, None))

    def test_duplicate_new_note_not_added(self):
        result = _merge_corrections("existing note", "existing note")
        self.assertEqual(result, "existing note")

    def test_substring_note_is_not_treated_as_duplicate(self):
        result = _merge_corrections("existing note with detail", "existing note")

        self.assertEqual(result, "existing note with detail\nexisting note")

    def test_distinct_notes_are_merged(self):
        result = _merge_corrections("note A", "note B")
        self.assertIn("note A", result)
        self.assertIn("note B", result)

    def test_merged_output_contains_newline(self):
        result = _merge_corrections("note A", "note B")
        self.assertIn("\n", result)


# ---------------------------------------------------------------------------
# consume_global_prefix_flags
# ---------------------------------------------------------------------------

class TestConsumeGlobalPrefixFlags(unittest.TestCase):
    def test_no_flags_returns_empty_prefix(self):
        prefix, rest = consume_global_prefix_flags(["skills", "list"])
        self.assertEqual(prefix, [])
        self.assertEqual(rest, ["skills", "list"])

    def test_json_flag_extracted(self):
        prefix, rest = consume_global_prefix_flags(["--json", "skills", "list"])
        self.assertIn("--json", prefix)
        self.assertEqual(rest, ["skills", "list"])

    def test_robot_flag_extracted(self):
        prefix, rest = consume_global_prefix_flags(["--robot", "skills", "list"])
        self.assertIn("--robot", prefix)
        self.assertEqual(rest, ["skills", "list"])

    def test_agent_mode_flag_extracted(self):
        prefix, rest = consume_global_prefix_flags(["--agent-mode", "repo", "status"])
        self.assertIn("--agent-mode", prefix)
        self.assertEqual(rest, ["repo", "status"])

    def test_short_r_flag_extracted(self):
        prefix, rest = consume_global_prefix_flags(["-r", "skills", "list"])
        self.assertIn("-r", prefix)
        self.assertEqual(rest, ["skills", "list"])

    def test_trace_id_consumes_value(self):
        prefix, rest = consume_global_prefix_flags(["--trace-id", "abc123", "skills", "list"])
        self.assertIn("--trace-id", prefix)
        self.assertIn("abc123", prefix)
        self.assertEqual(rest, ["skills", "list"])

    def test_trace_id_equals_form_extracted(self):
        prefix, rest = consume_global_prefix_flags(["--trace-id=abc123", "skills", "list"])
        self.assertEqual(prefix, ["--trace-id=abc123"])
        self.assertEqual(rest, ["skills", "list"])

    def test_unknown_flag_stops_extraction(self):
        prefix, rest = consume_global_prefix_flags(["--unknown-flag", "skills"])
        self.assertEqual(prefix, [])
        self.assertIn("--unknown-flag", rest)

    def test_empty_args(self):
        prefix, rest = consume_global_prefix_flags([])
        self.assertEqual(prefix, [])
        self.assertEqual(rest, [])

    def test_multiple_known_flags(self):
        prefix, rest = consume_global_prefix_flags(["--json", "--robot", "skills", "list"])
        self.assertIn("--json", prefix)
        self.assertIn("--robot", prefix)
        self.assertEqual(rest, ["skills", "list"])


# ---------------------------------------------------------------------------
# try_fuzzy_parse
# ---------------------------------------------------------------------------

class TestTryFuzzyParse(unittest.TestCase):
    """Tests for the routing/fuzzy-parse logic in try_fuzzy_parse."""

    def test_empty_args(self):
        topic, action, _remaining, note = try_fuzzy_parse([])
        self.assertIsNone(topic)
        self.assertIsNone(action)
        self.assertIsNone(note)

    def test_only_global_flags(self):
        topic, action, _remaining, _note = try_fuzzy_parse(["--json"])
        self.assertIsNone(topic)
        self.assertIsNone(action)

    def test_valid_topic_action_parsed(self):
        topic, action, _remaining, _note = try_fuzzy_parse(["skills", "list"])
        self.assertEqual(topic, "skills")
        self.assertEqual(action, "list")

    def test_alias_goal_maps_to_skills_goal(self):
        topic, action, _remaining, _note = try_fuzzy_parse(["goal", "build a feature"])
        self.assertEqual(topic, "skills")
        self.assertEqual(action, "goal")

    def test_swapped_order_recovered(self):
        """ask list skills → ask skills list"""
        topic, action, _remaining, _note = try_fuzzy_parse(["list", "skills"])
        self.assertEqual(topic, "skills")
        self.assertEqual(action, "list")

    def test_typo_topic_recovered(self):
        """ask skils list → ask skills list"""
        topic, action, _remaining, note = try_fuzzy_parse(["skils", "list"])
        self.assertEqual(topic, "skills")
        self.assertIsNotNone(note)

    def test_correction_note_set_for_typo(self):
        _, _, _, note = try_fuzzy_parse(["skils", "list"])
        self.assertIsNotNone(note)

    def test_robot_mode_uses_robot_prefix(self):
        _, _, _, note = try_fuzzy_parse(["skils", "list"], robot_mode=True)
        self.assertIsNotNone(note)
        self.assertIn("Robot mode", note)

    def test_human_mode_uses_did_you_mean(self):
        _, _, _, note = try_fuzzy_parse(["skils", "list"], robot_mode=False)
        self.assertIsNotNone(note)
        self.assertIn("Did you mean", note)

    def test_prefix_flags_preserved_in_remaining(self):
        _, _, remaining, _ = try_fuzzy_parse(["--json", "skills", "list"])
        self.assertIn("--json", remaining)

    def test_trace_id_equals_form_preserved_in_remaining(self):
        topic, action, remaining, _ = try_fuzzy_parse(["--trace-id=abc123", "skills", "list"])

        self.assertEqual(topic, "skills")
        self.assertEqual(action, "list")
        self.assertIn("--trace-id=abc123", remaining)

    def test_doctor_catalog_alias(self):
        topic, action, remaining, note = try_fuzzy_parse(["doctor", "catalog"])
        self.assertEqual(topic, "repo")
        self.assertEqual(action, "doctor-catalog")


# ---------------------------------------------------------------------------
# recovery result builders
# ---------------------------------------------------------------------------

class TestRecoveryResultBuilders(unittest.TestCase):
    def assert_recovery_data(self, result, validation_commands, candidate_commands=None, fix_suggestion=None):
        self.assertEqual(result.data["validation_commands"], validation_commands)
        if candidate_commands is not None:
            self.assertEqual(result.data["candidate_commands"], candidate_commands)
        if fix_suggestion is not None:
            self.assertEqual(result.errors[0].fix_suggestion, fix_suggestion)

    def test_unknown_action_includes_recovery_and_candidates(self):
        result = build_unknown_action_result("repo", "missing")

        self.assert_recovery_data(
            result,
            ["./bin/ask repo status --json --robot"],
            [
                "ask repo doctor --json --robot",
                "ask repo closeout --changed --json --robot",
                "ask repo validate --ephemeral",
            ],
        )

    def test_unknown_action_uses_closest_action_examples(self):
        result = build_unknown_action_result("skills", "reslove")

        self.assert_recovery_data(
            result,
            ["./bin/ask skills list --json --robot"],
            ["ask skills resolve he-phase-work --json"],
            "Closest action guess: 'ask skills resolve'.",
        )

    def test_sdk_unknown_action_recovers_only_author_facing_routes(self):
        result = build_unknown_action_result("sdk", "unsupported-action")

        self.assertEqual(
            result.data["candidate_commands"],
            [
                "ask sdk start Skills/agent-ops/simplify --json --robot",
                "ask sdk check Skills/agent-ops/simplify --json --robot",
            ],
        )
        self.assertEqual(result.errors[0].fix_suggestion, "Valid actions: start, check")

    def test_helpful_error_includes_recovery_and_candidates(self):
        result = build_helpful_error("skills", "missing", ["skills", "missing"])

        self.assertEqual(result.data["validation_commands"], ["./bin/ask skills list --json --robot"])
        self.assertEqual(
            result.data["candidate_commands"],
            [
                'ask skills improve "fix PR review comments faster" --json --robot',
                "ask skills explain he-phase-work --json --robot",
                "ask skills doctor he-phase-work --json --robot",
            ],
        )

    def test_helpful_error_uses_inferred_topic_for_recovery(self):
        result = build_helpful_error(None, None, ["prove"])

        self.assertEqual(result.data["validation_commands"], ["./bin/ask skills list --json --robot"])
        self.assertEqual(result.data["candidate_commands"], ["ask skills prove he-phase-work --json"])

    def test_helpful_error_uses_ambiguous_recovery_commands(self):
        for args in ((None, None, ["list"]), ("list", None, ["list"])):
            with self.subTest(args=args):
                result = build_helpful_error(*args)

                self.assert_recovery_data(
                    result,
                    [
                        "./bin/ask skills list --json --robot",
                        "./bin/ask plugins list --json --robot",
                        "./bin/ask graph list --json --robot",
                    ],
                    [
                        "ask skills list",
                        "ask plugins list",
                        "ask graph list",
                    ],
                    "Use an explicit topic: 'ask skills list', 'ask plugins list', 'ask graph list'.",
                )
    def test_ambiguous_fix_suggestion_uses_same_commands_as_candidates(self):
        result = build_helpful_error(None, None, ["list"])
        expected_topics = [command.split()[1] for command in result.data["candidate_commands"]]

        self.assertEqual(
            _ambiguous_action_fix_suggestion("list", expected_topics),
            "Use an explicit topic: 'ask skills list', 'ask plugins list', 'ask graph list'.",
        )

    def test_helpful_error_uses_closest_topic_for_recovery(self):
        result = build_helpful_error("skils", None, ["skils"])

        self.assertEqual(result.data["validation_commands"], ["./bin/ask skills list --json --robot"])
        self.assertEqual(
            result.data["candidate_commands"],
            [
                'ask skills improve "fix PR review comments faster" --json --robot',
                "ask skills explain he-phase-work --json --robot",
                "ask skills doctor he-phase-work --json --robot",
            ],
        )
        self.assertEqual(result.errors[0].fix_suggestion, "Closest topic guess: 'ask skills'.")

    def test_helpful_error_uses_raw_closest_topic_for_recovery(self):
        result = build_helpful_error(None, None, ["skils"])

        self.assertEqual(result.data["validation_commands"], ["./bin/ask skills list --json --robot"])
        self.assertEqual(
            result.data["candidate_commands"],
            [
                'ask skills improve "fix PR review comments faster" --json --robot',
                "ask skills explain he-phase-work --json --robot",
                "ask skills doctor he-phase-work --json --robot",
            ],
        )
        self.assertEqual(result.errors[0].fix_suggestion, "Closest topic guess: 'ask skills'.")

    def test_closest_topic_fix_suggestion_matches_helpful_error(self):
        result = build_helpful_error(None, None, ["skils"])

        self.assertEqual(result.errors[0].fix_suggestion, _closest_topic_fix_suggestion("skills"))

    def test_helpful_error_uses_fallback_recovery_for_unknown_topic(self):
        for args, expected_candidates in (
            (
                ("zzz", None, ["zzz"]),
                [
                    'ask skills improve "fix PR review comments faster" --json --robot',
                    "ask skills explain he-phase-work --json --robot",
                    "ask skills doctor he-phase-work --json --robot",
                ],
            ),
            ((None, None, ["zzz"]), None),
        ):
            with self.subTest(args=args):
                result = build_helpful_error(*args)

                self.assert_recovery_data(
                    result,
                    [
                        "./bin/ask skills list --json --robot",
                        "./bin/ask repo status --json --robot",
                        "./bin/ask graph list --json --robot",
                    ],
                    expected_candidates,
                    (
                        "Run a valid topic recovery command: './bin/ask skills list --json --robot', "
                        "'./bin/ask repo status --json --robot', './bin/ask graph list --json --robot'."
                    ),
                )

    def test_fallback_fix_suggestion_uses_same_commands_as_fallback_recovery(self):
        result = build_helpful_error(None, None, ["zzz"])

        self.assertEqual(
            _fallback_topic_fix_suggestion(),
            result.errors[0].fix_suggestion,
        )

    def test_helpful_error_uses_closest_action_fix_suggestion(self):
        result = build_helpful_error("skills", "reslove", ["skills", "reslove"])

        self.assert_recovery_data(
            result,
            ["./bin/ask skills list --json --robot"],
            ["ask skills resolve he-phase-work --json"],
            "Closest action guess: 'ask skills resolve'.",
        )

    def test_closest_action_fix_suggestion_matches_unknown_action_builders(self):
        helpful = build_helpful_error("skills", "reslove", ["skills", "reslove"])
        unknown = build_unknown_action_result("skills", "reslove")

        self.assertEqual(helpful.errors[0].fix_suggestion, _closest_action_fix_suggestion("skills", "resolve"))
        self.assertEqual(unknown.errors[0].fix_suggestion, _closest_action_fix_suggestion("skills", "resolve"))

    def test_argument_error_includes_recovery_and_candidates(self):
        result = build_argument_error("skills", "resolve", ["skills", "resolve"])

        self.assert_recovery_data(
            result,
            ["./bin/ask skills list --json --robot"],
            ["ask skills resolve he-phase-work --json"],
        )


# ---------------------------------------------------------------------------
# parse_args_with_capture
# ---------------------------------------------------------------------------

class TestParseArgsWithCapture(unittest.TestCase):
    def _make_parser(self):
        p = argparse.ArgumentParser(prog="test")
        p.add_argument("--count", type=int)
        return p

    def test_valid_args_parse_successfully(self):
        parser = self._make_parser()
        ns, code, stderr = parse_args_with_capture(parser, ["--count", "5"])
        self.assertIsNotNone(ns)
        self.assertIsNone(code)
        self.assertEqual(ns.count, 5)

    def test_invalid_args_return_exit_code(self):
        parser = self._make_parser()
        ns, code, stderr = parse_args_with_capture(parser, ["--count", "not-a-number"])
        self.assertIsNone(ns)
        self.assertIsNotNone(code)
        self.assertNotEqual(code, 0)

    def test_invalid_args_capture_stderr(self):
        parser = self._make_parser()
        _, code, stderr = parse_args_with_capture(parser, ["--count", "not-a-number"])
        self.assertIsInstance(stderr, str)
        self.assertTrue(len(stderr) > 0)

    def test_valid_args_return_none_exit_code(self):
        parser = self._make_parser()
        _, code, _ = parse_args_with_capture(parser, [])
        self.assertIsNone(code)

    def test_returns_three_tuple(self):
        parser = self._make_parser()
        result = parse_args_with_capture(parser, [])
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 3)


# ---------------------------------------------------------------------------
# _example_commands
# ---------------------------------------------------------------------------

class TestExampleCommands(unittest.TestCase):
    def test_returns_list(self):
        result = _example_commands("skills", "list")
        self.assertIsInstance(result, list)

    def test_limit_respected(self):
        result = _example_commands("skills", "list", limit=2)
        self.assertLessEqual(len(result), 2)

    def test_none_topic_fallback_examples_start_with_recovery_topic_examples(self):
        result = _example_commands(None, None, limit=3)

        self.assertEqual(
            result,
            [
                'ask skills improve "fix PR review comments faster" --json --robot',
                "ask skills explain he-phase-work --json --robot",
                "ask skills doctor he-phase-work --json --robot",
            ],
        )

    def test_known_topic_returns_examples(self):
        result = _example_commands("skills", None, limit=3)
        self.assertGreater(len(result), 0)
        # All examples should be strings
        for ex in result:
            self.assertIsInstance(ex, str)

    def test_zero_limit_returns_empty(self):
        result = _example_commands("skills", "list", limit=0)
        self.assertEqual(result, [])

    def test_negative_limit_returns_empty(self):
        result = _example_commands("skills", "list", limit=-1)
        self.assertEqual(result, [])

    def test_skills_doctor_returns_command_specific_examples(self):
        result = _example_commands("skills", "doctor", limit=2)

        self.assertEqual(result[0], "ask skills doctor he-phase-work --json")
        self.assertIn("Skills/agent-ops/autofix", result[1])

    def test_skills_events_returns_command_specific_examples(self):
        result = _example_commands("skills", "events", limit=2)

        self.assertEqual(result[0], "ask skills events --json")
        self.assertEqual(result[1], "ask skills events eval_blocked --json")


if __name__ == "__main__":
    unittest.main()
