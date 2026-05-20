"""Smoke tests for extracted ask CLI helper module surfaces."""

import importlib
import sys
import unittest

from ask_test_paths import (
    ASK_LIB_DIR,
    LIFECYCLE_DIR,
    SCRIPTS_DIR,
    UTILITIES_DIR,
    ensure_ask_lib_path,
    ensure_ask_support_paths,
)


ensure_ask_lib_path()


EXPECTED_HELPERS = {
    "ask.cli_args": ["build_global_parser", "prepare_args"],
    "ask.cli_errors": [
        "build_argument_error",
        "build_helpful_error",
        "build_unknown_action_result",
        "consume_global_prefix_flags",
        "parse_args_with_capture",
        "try_fuzzy_parse",
    ],
    "ask.cli_exit": ["exit_code_for_errors"],
    "ask.cli_output": [
        "print_first_validation_command",
        "print_readiness_overview",
        "replay_command",
    ],
    "ask.cli_prompts": ["prompt_choice", "prompt_nonempty", "prompt_optional", "safe_input"],
}


class TestCliModuleSurfaces(unittest.TestCase):
    def test_extracted_cli_helper_modules_import_expected_helpers(self):
        for module_name, helper_names in EXPECTED_HELPERS.items():
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)

                for helper_name in helper_names:
                    self.assertTrue(callable(getattr(module, helper_name, None)), helper_name)


class TestAskTestPaths(unittest.TestCase):
    def test_ensure_ask_lib_path_inserts_library_path(self):
        ensure_ask_lib_path()

        self.assertIn(str(ASK_LIB_DIR), sys.path)

    def test_ensure_ask_support_paths_inserts_support_paths_once(self):
        ensure_ask_support_paths()
        before_counts = {str(path): sys.path.count(str(path)) for path in (ASK_LIB_DIR, SCRIPTS_DIR, LIFECYCLE_DIR, UTILITIES_DIR)}

        ensure_ask_support_paths()

        for path in (ASK_LIB_DIR, SCRIPTS_DIR, LIFECYCLE_DIR, UTILITIES_DIR):
            path_text = str(path)
            self.assertIn(path_text, sys.path)
            self.assertEqual(sys.path.count(path_text), before_counts[path_text])


if __name__ == "__main__":
    unittest.main()
