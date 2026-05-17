"""Tests for extracted ask CLI prompt helpers."""

import contextlib
import io
import unittest
from unittest.mock import patch

from ask_test_paths import ensure_ask_lib_path


ensure_ask_lib_path()

from ask.cli_prompts import prompt_choice, prompt_nonempty, prompt_optional, safe_input  # noqa: E402


class TestSafeInput(unittest.TestCase):
    def test_returns_input_value(self):
        with patch("builtins.input", return_value="value"):
            self.assertEqual(safe_input("Prompt: "), "value")

    def test_eof_exits_with_cancel_code(self):
        with patch("builtins.input", side_effect=EOFError), io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            with self.assertRaises(SystemExit) as raised:
                safe_input("Prompt: ")

            self.assertEqual(raised.exception.code, 130)
            self.assertIn("Interactive input cancelled by user.", buffer.getvalue())

    def test_keyboard_interrupt_exits_with_cancel_code(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt), io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            with self.assertRaises(SystemExit) as raised:
                safe_input("Prompt: ")

            self.assertEqual(raised.exception.code, 130)
            self.assertIn("Interactive input cancelled by user.", buffer.getvalue())


class TestPromptChoice(unittest.TestCase):
    def test_empty_options_raise_clear_error(self):
        with self.assertRaisesRegex(ValueError, "requires at least one option"):
            prompt_choice("Pick one", [])

    def test_numeric_choice_uses_one_based_index(self):
        with patch("ask.cli_prompts.safe_input", return_value="2"), io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            result = prompt_choice("Pick one", ["alpha", "beta"])
            output = buffer.getvalue()

        self.assertEqual(result, "beta")
        self.assertIn("1. alpha", output)
        self.assertIn("2. beta", output)

    def test_exact_option_value_is_accepted(self):
        with patch("ask.cli_prompts.safe_input", return_value="beta"), contextlib.redirect_stdout(io.StringIO()):
            result = prompt_choice("Pick one", ["alpha", "beta"])

        self.assertEqual(result, "beta")

    def test_invalid_choice_reprompts(self):
        with patch("ask.cli_prompts.safe_input", side_effect=["9", "alpha"]), io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            result = prompt_choice("Pick one", ["alpha", "beta"])
            output = buffer.getvalue()

        self.assertEqual(result, "alpha")
        self.assertIn("Please choose 1-2 or type an exact option value.", output)


class TestPromptText(unittest.TestCase):
    def test_prompt_nonempty_reprompts_until_value(self):
        with patch("ask.cli_prompts.safe_input", side_effect=[" ", "answer"]), io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            result = prompt_nonempty("Value: ")
            output = buffer.getvalue()

        self.assertEqual(result, "answer")
        self.assertIn("This value cannot be empty.", output)

    def test_prompt_optional_strips_value(self):
        with patch("ask.cli_prompts.safe_input", return_value="  optional value  "):
            self.assertEqual(prompt_optional("Value: "), "optional value")

    def test_prompt_optional_treats_none_as_empty(self):
        with patch("ask.cli_prompts.safe_input", return_value=None):
            self.assertEqual(prompt_optional("Value: "), "")


if __name__ == "__main__":
    unittest.main()
