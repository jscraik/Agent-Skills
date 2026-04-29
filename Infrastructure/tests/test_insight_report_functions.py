"""
Tests for pure functions in run_insight_report.py.

Covers the functions added/changed in the PR:
  - is_meta_session
  - count_lines_in_diff
  - extract_message_text
  - categorize_tool_error
  - TOOL_ALIASES, LABEL_MAP, SATISFACTION_ORDER, OUTCOME_ORDER constants
  - parse_args (argument parsing)
"""
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Load the module under test from its absolute path so we don't rely on
# it being installed as a package.
# ---------------------------------------------------------------------------
_SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Infrastructure"
    / "references"
    / "deferred-skill-context"
    / "agent-ops-insight-report"
    / "scripts"
    / "run_insight_report.py"
)


def _load_insight_report():
    spec = importlib.util.spec_from_file_location("run_insight_report", _SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    # Prevent the module-level side-effects (Path.home() etc.) from raising
    # when the optional environment directories don't exist.
    spec.loader.exec_module(mod)
    return mod


_mod = _load_insight_report()

is_meta_session = _mod.is_meta_session
count_lines_in_diff = _mod.count_lines_in_diff
extract_message_text = _mod.extract_message_text
categorize_tool_error = _mod.categorize_tool_error
TOOL_ALIASES = _mod.TOOL_ALIASES
LABEL_MAP = _mod.LABEL_MAP
SATISFACTION_ORDER = _mod.SATISFACTION_ORDER
OUTCOME_ORDER = _mod.OUTCOME_ORDER


# ---------------------------------------------------------------------------
# is_meta_session
# ---------------------------------------------------------------------------

class TestIsMetaSession(unittest.TestCase):
    def _event_msg(self, msg_type, content):
        return {
            "type": "event_msg",
            "payload": {"type": msg_type, "message": content},
        }

    def test_returns_true_for_internal_insights_marker(self):
        events = [
            self._event_msg(
                "user_message",
                "Here is data. RESPOND WITH ONLY A VALID JSON OBJECT please.",
            )
        ]
        self.assertTrue(is_meta_session(events))

    def test_returns_false_for_normal_user_message(self):
        events = [self._event_msg("user_message", "Help me debug this code.")]
        self.assertFalse(is_meta_session(events))

    def test_returns_false_for_empty_events(self):
        self.assertFalse(is_meta_session([]))

    def test_only_checks_first_ten_events(self):
        """Marker appearing after the first 10 events must not trigger detection."""
        normal_events = [
            self._event_msg("user_message", f"message {i}") for i in range(10)
        ]
        late_marker = self._event_msg(
            "user_message", "RESPOND WITH ONLY A VALID JSON OBJECT"
        )
        self.assertFalse(is_meta_session(normal_events + [late_marker]))

    def test_returns_false_for_non_event_msg_types(self):
        events = [
            {"type": "session_meta", "payload": {"message": "RESPOND WITH ONLY A VALID JSON OBJECT"}}
        ]
        self.assertFalse(is_meta_session(events))

    def test_returns_false_when_type_is_not_user_message(self):
        events = [
            {
                "type": "event_msg",
                "payload": {
                    "type": "agent_message",
                    "message": "RESPOND WITH ONLY A VALID JSON OBJECT",
                },
            }
        ]
        self.assertFalse(is_meta_session(events))

    def test_uses_content_field_as_fallback(self):
        """The payload may use 'content' instead of 'message'."""
        events = [
            {
                "type": "event_msg",
                "payload": {
                    "type": "user_message",
                    "content": "RESPOND WITH ONLY A VALID JSON OBJECT here",
                },
            }
        ]
        self.assertTrue(is_meta_session(events))

    def test_returns_false_when_marker_absent(self):
        events = [
            self._event_msg("user_message", "Please analyze my code.")
            for _ in range(5)
        ]
        self.assertFalse(is_meta_session(events))


# ---------------------------------------------------------------------------
# count_lines_in_diff
# ---------------------------------------------------------------------------

class TestCountLinesInDiff(unittest.TestCase):
    def test_identical_texts_return_zero(self):
        added, removed = count_lines_in_diff("foo\nbar", "foo\nbar")
        self.assertEqual(added, 0)
        self.assertEqual(removed, 0)

    def test_added_lines(self):
        added, removed = count_lines_in_diff("line1", "line1\nline2\nline3")
        self.assertGreater(added, 0)
        self.assertEqual(removed, 0)

    def test_removed_lines(self):
        added, removed = count_lines_in_diff("line1\nline2\nline3", "line1")
        self.assertEqual(added, 0)
        self.assertGreater(removed, 0)

    def test_changed_line_counts_as_add_and_remove(self):
        added, removed = count_lines_in_diff("hello", "world")
        self.assertGreater(added, 0)
        self.assertGreater(removed, 0)

    def test_empty_old_returns_more_added_than_removed(self):
        # "" splits to [''], so there is 1 implicit line; going to 3 lines means
        # more lines added than removed.
        added, removed = count_lines_in_diff("", "a\nb\nc")
        self.assertGreater(added, 0)
        self.assertGreater(added, removed)

    def test_empty_new_returns_more_removed_than_added(self):
        # Inverse: going from 3 lines to '' means more lines removed than added.
        added, removed = count_lines_in_diff("a\nb\nc", "")
        self.assertGreater(removed, 0)
        self.assertGreater(removed, added)

    def test_returns_tuple_of_two_ints(self):
        result = count_lines_in_diff("x", "y")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], int)
        self.assertIsInstance(result[1], int)

    def test_multiline_replace_counts_correctly(self):
        old = "a\nb\nc"
        new = "a\nB\nc"
        added, removed = count_lines_in_diff(old, new)
        # One line changed → one added, one removed
        self.assertEqual(added, 1)
        self.assertEqual(removed, 1)


# ---------------------------------------------------------------------------
# extract_message_text
# ---------------------------------------------------------------------------

class TestExtractMessageText(unittest.TestCase):
    def test_string_passthrough(self):
        self.assertEqual(extract_message_text("hello"), "hello")

    def test_empty_string_passthrough(self):
        self.assertEqual(extract_message_text(""), "")

    def test_list_of_blocks_joins_text(self):
        content = [{"type": "text", "text": "foo"}, {"type": "text", "text": "bar"}]
        result = extract_message_text(content)
        self.assertIn("foo", result)
        self.assertIn("bar", result)

    def test_list_ignores_non_text_blocks(self):
        content = [{"type": "image"}, {"type": "text", "text": "only-text"}]
        result = extract_message_text(content)
        self.assertEqual(result, "only-text")

    def test_list_with_no_text_keys_returns_empty(self):
        content = [{"type": "image"}, {"type": "tool_use"}]
        result = extract_message_text(content)
        self.assertEqual(result, "")

    def test_non_string_non_list_returns_empty(self):
        self.assertEqual(extract_message_text(None), "")
        self.assertEqual(extract_message_text(42), "")
        self.assertEqual(extract_message_text({"text": "hi"}), "")

    def test_blocks_joined_with_newline(self):
        content = [{"text": "line1"}, {"text": "line2"}]
        result = extract_message_text(content)
        self.assertEqual(result, "line1\nline2")

    def test_list_skips_non_dict_items(self):
        content = ["plain string", {"text": "valid"}]
        result = extract_message_text(content)
        self.assertEqual(result, "valid")

    def test_list_skips_blocks_with_non_string_text(self):
        content = [{"text": 123}, {"text": "real"}]
        result = extract_message_text(content)
        self.assertEqual(result, "real")


# ---------------------------------------------------------------------------
# categorize_tool_error
# ---------------------------------------------------------------------------

class TestCategorizeToolError(unittest.TestCase):
    def test_non_string_returns_other(self):
        self.assertEqual(categorize_tool_error(None), "Other")
        self.assertEqual(categorize_tool_error(42), "Other")
        self.assertEqual(categorize_tool_error([]), "Other")

    def test_exit_code_detected(self):
        self.assertEqual(categorize_tool_error("Process exit code 1"), "Command Failed")

    def test_rejected_detected(self):
        self.assertEqual(categorize_tool_error("Operation rejected by user"), "User Rejected")

    def test_doesnt_want_detected(self):
        self.assertEqual(categorize_tool_error("user doesn't want this"), "User Rejected")

    def test_string_to_replace_not_found(self):
        self.assertEqual(
            categorize_tool_error("Error: string to replace not found in file"),
            "Edit Failed",
        )

    def test_no_changes_detected(self):
        self.assertEqual(categorize_tool_error("no changes were made"), "Edit Failed")

    def test_modified_since_read(self):
        self.assertEqual(categorize_tool_error("file modified since read"), "File Changed")

    def test_exceeds_maximum(self):
        self.assertEqual(categorize_tool_error("content exceeds maximum size limit"), "File Too Large")

    def test_too_large(self):
        self.assertEqual(categorize_tool_error("file too large to process"), "File Too Large")

    def test_file_not_found(self):
        self.assertEqual(categorize_tool_error("file not found at path"), "File Not Found")

    def test_does_not_exist(self):
        self.assertEqual(categorize_tool_error("path does not exist"), "File Not Found")

    def test_unknown_returns_other(self):
        self.assertEqual(categorize_tool_error("some random error message"), "Other")

    def test_case_insensitive_matching(self):
        self.assertEqual(categorize_tool_error("EXIT CODE encountered"), "Command Failed")
        self.assertEqual(categorize_tool_error("REJECTED"), "User Rejected")


# ---------------------------------------------------------------------------
# Constants: TOOL_ALIASES
# ---------------------------------------------------------------------------

class TestToolAliases(unittest.TestCase):
    def test_bash_normalizes_to_shell(self):
        self.assertEqual(TOOL_ALIASES.get("bash"), "Shell")

    def test_shell_normalizes_to_shell(self):
        self.assertEqual(TOOL_ALIASES.get("shell"), "Shell")

    def test_read_file_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("read_file"), "ReadFile")

    def test_str_replace_file_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("str_replace_file"), "StrReplaceFile")

    def test_write_file_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("write_file"), "WriteFile")

    def test_agent_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("agent"), "Agent")

    def test_web_search_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("web_search"), "WebSearch")

    def test_web_fetch_normalizes(self):
        self.assertEqual(TOOL_ALIASES.get("web_fetch"), "WebFetch")

    def test_all_aliases_are_strings(self):
        for key, val in TOOL_ALIASES.items():
            with self.subTest(key=key):
                self.assertIsInstance(key, str)
                self.assertIsInstance(val, str)


# ---------------------------------------------------------------------------
# Constants: LABEL_MAP
# ---------------------------------------------------------------------------

class TestLabelMap(unittest.TestCase):
    def test_known_keys_present(self):
        expected_keys = [
            "debug_investigate",
            "implement_feature",
            "fix_bug",
            "write_script_tool",
            "refactor_code",
            "configure_system",
            "create_pr_commit",
            "analyze_data",
            "understand_codebase",
            "write_tests",
            "write_docs",
        ]
        for key in expected_keys:
            with self.subTest(key=key):
                self.assertIn(key, LABEL_MAP)

    def test_all_values_are_non_empty_strings(self):
        for key, val in LABEL_MAP.items():
            with self.subTest(key=key):
                self.assertIsInstance(val, str)
                self.assertTrue(val.strip(), f"Empty label for key '{key}'")

    def test_satisfaction_labels_present(self):
        for key in ("frustrated", "dissatisfied", "satisfied", "happy"):
            self.assertIn(key, LABEL_MAP)

    def test_outcome_labels_present(self):
        for key in ("not_achieved", "partially_achieved", "mostly_achieved", "fully_achieved"):
            self.assertIn(key, LABEL_MAP)


# ---------------------------------------------------------------------------
# Constants: SATISFACTION_ORDER and OUTCOME_ORDER
# ---------------------------------------------------------------------------

class TestOrderConstants(unittest.TestCase):
    def test_satisfaction_order_is_list(self):
        self.assertIsInstance(SATISFACTION_ORDER, list)

    def test_satisfaction_order_contains_frustrated_first(self):
        self.assertEqual(SATISFACTION_ORDER[0], "frustrated")

    def test_satisfaction_order_has_positive_sentiments(self):
        self.assertIn("satisfied", SATISFACTION_ORDER)
        self.assertIn("happy", SATISFACTION_ORDER)

    def test_outcome_order_is_list(self):
        self.assertIsInstance(OUTCOME_ORDER, list)

    def test_outcome_order_starts_with_not_achieved(self):
        self.assertEqual(OUTCOME_ORDER[0], "not_achieved")

    def test_outcome_order_ends_with_fully_achieved_or_unclear(self):
        self.assertIn(OUTCOME_ORDER[-1], ("fully_achieved", "unclear_from_transcript"))

    def test_satisfaction_order_no_duplicates(self):
        self.assertEqual(len(SATISFACTION_ORDER), len(set(SATISFACTION_ORDER)))

    def test_outcome_order_no_duplicates(self):
        self.assertEqual(len(OUTCOME_ORDER), len(set(OUTCOME_ORDER)))


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs(unittest.TestCase):
    def _parse(self, argv):
        with patch("sys.argv", ["run_insight_report.py"] + argv):
            return _mod.parse_args()

    def test_default_days_is_seven(self):
        args = self._parse([])
        self.assertEqual(args.days, 7)

    def test_custom_days(self):
        args = self._parse(["--days", "14"])
        self.assertEqual(args.days, 14)

    def test_no_open_defaults_false(self):
        args = self._parse([])
        self.assertFalse(args.no_open)

    def test_no_open_flag(self):
        args = self._parse(["--no-open"])
        self.assertTrue(args.no_open)

    def test_verbose_defaults_false(self):
        args = self._parse([])
        self.assertFalse(args.verbose)

    def test_verbose_short_flag(self):
        args = self._parse(["-v"])
        self.assertTrue(args.verbose)

    def test_prepare_only_flag(self):
        args = self._parse(["--prepare-only"])
        self.assertTrue(args.prepare_only)

    def test_render_only_flag(self):
        args = self._parse(["--render-only"])
        self.assertTrue(args.render_only)

    def test_mutually_exclusive_flags_raise_system_exit(self):
        with patch("sys.argv", ["run_insight_report.py", "--prepare-only", "--render-only"]):
            with self.assertRaises(SystemExit):
                _mod.parse_args()

    def test_max_sessions_default(self):
        args = self._parse([])
        self.assertEqual(args.max_sessions, 200)

    def test_max_sessions_custom(self):
        args = self._parse(["--max-sessions", "50"])
        self.assertEqual(args.max_sessions, 50)

    def test_max_evidence_sessions_default(self):
        args = self._parse([])
        self.assertEqual(args.max_evidence_sessions, 30)

    def test_evidence_out_is_string(self):
        args = self._parse([])
        self.assertIsInstance(args.evidence_out, str)

    def test_custom_evidence_out(self):
        args = self._parse(["--evidence-out", "/tmp/evidence.json"])
        self.assertEqual(args.evidence_out, "/tmp/evidence.json")

    def test_insights_in_defaults_to_same_as_insights_out(self):
        args = self._parse([])
        self.assertEqual(args.insights_in, args.insights_out)


if __name__ == "__main__":
    unittest.main()