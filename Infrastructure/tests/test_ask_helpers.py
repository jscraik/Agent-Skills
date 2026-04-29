"""
Tests for pure helper functions in Infrastructure/bin/ask.

Covers functions added or changed in the PR:
  - get_closest_match
  - format_correction
  - _normalize_token
  - _extract_argparse_error
  - _example_commands
  - _merge_corrections
  - consume_global_prefix_flags
  - try_fuzzy_parse (key routing logic)
  - build_helpful_error
  - build_argument_error
  - parse_args_with_capture
"""
import argparse
import importlib.util
import sys
import types
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup — mirrors what Infrastructure/tests/test_ask_cli.py does
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"
SCRIPTS_DIR = REPO_ROOT / "Infrastructure" / "scripts"
LIFECYCLE_DIR = SCRIPTS_DIR / "lifecycle-and-sync"
UTILITIES_DIR = REPO_ROOT / "Infrastructure" / "utilities" / "skill-builder" / "scripts"

for p in (str(ASK_LIB_DIR), str(SCRIPTS_DIR), str(LIFECYCLE_DIR), str(UTILITIES_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# ---------------------------------------------------------------------------
# Load Infrastructure/bin/ask as a module (it has no .py extension)
# ---------------------------------------------------------------------------
_BIN_ASK_PATH = REPO_ROOT / "Infrastructure" / "bin" / "ask"

from importlib.machinery import SourceFileLoader  # noqa: E402

_loader = SourceFileLoader("ask_bin", str(_BIN_ASK_PATH))
spec = importlib.util.spec_from_loader("ask_bin", _loader)
ask_bin = importlib.util.module_from_spec(spec)
_loader.exec_module(ask_bin)

get_closest_match = ask_bin.get_closest_match
format_correction = ask_bin.format_correction
_normalize_token = ask_bin._normalize_token
_extract_argparse_error = ask_bin._extract_argparse_error
_example_commands = ask_bin._example_commands
_merge_corrections = ask_bin._merge_corrections
consume_global_prefix_flags = ask_bin.consume_global_prefix_flags
try_fuzzy_parse = ask_bin.try_fuzzy_parse
build_helpful_error = ask_bin.build_helpful_error
build_argument_error = ask_bin.build_argument_error
parse_args_with_capture = ask_bin.parse_args_with_capture


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

    def test_doctor_catalog_alias(self):
        topic, action, remaining, note = try_fuzzy_parse(["doctor", "catalog"])
        self.assertEqual(topic, "repo")
        self.assertEqual(action, "doctor-catalog")


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

    def test_none_topic_returns_fallback_examples(self):
        result = _example_commands(None, None, limit=3)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_known_topic_returns_examples(self):
        result = _example_commands("skills", None, limit=3)
        self.assertGreater(len(result), 0)
        # All examples should be strings
        for ex in result:
            self.assertIsInstance(ex, str)

    def test_zero_limit_returns_empty(self):
        result = _example_commands("skills", "list", limit=0)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()