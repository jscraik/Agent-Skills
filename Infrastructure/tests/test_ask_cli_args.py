"""Tests for extracted ask CLI argument preparation helpers."""

import unittest
from unittest import mock

from ask_test_paths import ensure_ask_lib_path


ensure_ask_lib_path()

from ask.cli_args import build_global_parser, prepare_args  # noqa: E402


class TestPrepareArgs(unittest.TestCase):
    def test_goal_alias_preserves_prefix_flags(self):
        prepared = prepare_args(["--json", "goal", "ship capability readiness"])

        self.assertEqual(prepared.raw_args, ["--json", "skills", "goal", "ship capability readiness"])
        self.assertEqual(prepared.filtered_args, ["--json", "skills", "goal", "ship capability readiness"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertIn("'ask goal' maps to 'ask skills goal'", prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)

    def test_goal_alias_preserves_trace_id_pair(self):
        prepared = prepare_args(["--trace-id", "trace-123", "goal", "ship capability readiness"])

        self.assertEqual(
            prepared.raw_args,
            ["--trace-id", "trace-123", "skills", "goal", "ship capability readiness"],
        )
        self.assertEqual(
            prepared.filtered_args,
            ["--trace-id", "trace-123", "skills", "goal", "ship capability readiness"],
        )
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)

    def test_goal_alias_preserves_trace_id_equals_form(self):
        prepared = prepare_args(["--trace-id=trace-123", "goal", "ship capability readiness"])

        self.assertEqual(
            prepared.raw_args,
            ["--trace-id=trace-123", "skills", "goal", "ship capability readiness"],
        )
        self.assertEqual(
            prepared.filtered_args,
            ["--trace-id=trace-123", "skills", "goal", "ship capability readiness"],
        )
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)

    def test_goal_alias_filters_robot_flag_after_rewrite(self):
        prepared = prepare_args(["--robot", "goal", "ship capability readiness"])

        self.assertEqual(prepared.raw_args, ["--robot", "skills", "goal", "ship capability readiness"])
        self.assertEqual(prepared.filtered_args, ["skills", "goal", "ship capability readiness"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_goal_alias_filters_short_robot_flag_after_rewrite(self):
        prepared = prepare_args(["-r", "goal", "ship capability readiness"])

        self.assertEqual(prepared.raw_args, ["-r", "skills", "goal", "ship capability readiness"])
        self.assertEqual(prepared.filtered_args, ["skills", "goal", "ship capability readiness"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_goal_alias_preserves_stacked_prefix_flags(self):
        prepared = prepare_args(
            ["--json", "--trace-id", "trace-123", "--agent-mode", "goal", "ship capability readiness"]
        )

        self.assertEqual(
            prepared.raw_args,
            ["--json", "--trace-id", "trace-123", "--agent-mode", "skills", "goal", "ship capability readiness"],
        )
        self.assertEqual(
            prepared.filtered_args,
            ["--json", "--trace-id", "trace-123", "skills", "goal", "ship capability readiness"],
        )
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_doctor_catalog_alias_preserves_suffix_args(self):
        prepared = prepare_args(["doctor", "catalog", "--strict"])

        self.assertEqual(prepared.raw_args, ["repo", "doctor-catalog", "--strict"])
        self.assertEqual(prepared.filtered_args, ["repo", "doctor-catalog", "--strict"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertIn(
            "'ask doctor catalog' maps to 'ask repo doctor-catalog'",
            prepared.alias_correction_note,
        )

    def test_doctor_catalog_alias_preserves_trace_id_pair(self):
        prepared = prepare_args(["--trace-id", "trace-123", "doctor", "catalog", "--strict"])

        self.assertEqual(
            prepared.raw_args,
            ["--trace-id", "trace-123", "repo", "doctor-catalog", "--strict"],
        )
        self.assertEqual(
            prepared.filtered_args,
            ["--trace-id", "trace-123", "repo", "doctor-catalog", "--strict"],
        )
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)

    def test_doctor_catalog_alias_filters_robot_flag_after_rewrite(self):
        prepared = prepare_args(["--robot", "doctor", "catalog", "--strict"])

        self.assertEqual(prepared.raw_args, ["--robot", "repo", "doctor-catalog", "--strict"])
        self.assertEqual(prepared.filtered_args, ["repo", "doctor-catalog", "--strict"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_doctor_catalog_alias_filters_short_robot_flag_after_rewrite(self):
        prepared = prepare_args(["-r", "doctor", "catalog", "--strict"])

        self.assertEqual(prepared.raw_args, ["-r", "repo", "doctor-catalog", "--strict"])
        self.assertEqual(prepared.filtered_args, ["repo", "doctor-catalog", "--strict"])
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_doctor_catalog_alias_preserves_stacked_prefix_flags(self):
        prepared = prepare_args(["--json", "--trace-id", "trace-123", "--agent-mode", "doctor", "catalog"])

        self.assertEqual(
            prepared.raw_args,
            ["--json", "--trace-id", "trace-123", "--agent-mode", "repo", "doctor-catalog"],
        )
        self.assertEqual(
            prepared.filtered_args,
            ["--json", "--trace-id", "trace-123", "repo", "doctor-catalog"],
        )
        self.assertIsNotNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_robot_aliases_are_filtered_and_detected(self):
        prepared = prepare_args(["--agent-mode", "skills", "list", "-r", "--robot"])

        self.assertEqual(prepared.raw_args, ["--agent-mode", "skills", "list", "-r", "--robot"])
        self.assertEqual(prepared.filtered_args, ["skills", "list"])
        self.assertIsNone(prepared.alias_correction_note)
        self.assertTrue(prepared.robot_mode)

    def test_unknown_leading_option_does_not_trigger_alias_rewrite(self):
        prepared = prepare_args(["--strict", "doctor", "catalog"])

        self.assertEqual(prepared.raw_args, ["--strict", "doctor", "catalog"])
        self.assertEqual(prepared.filtered_args, ["--strict", "doctor", "catalog"])
        self.assertIsNone(prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)

    def test_unaliased_args_pass_through(self):
        prepared = prepare_args(["skills", "resolve", "simplify", "--json"])

        self.assertEqual(prepared.raw_args, ["skills", "resolve", "simplify", "--json"])
        self.assertEqual(prepared.filtered_args, ["skills", "resolve", "simplify", "--json"])
        self.assertIsNone(prepared.alias_correction_note)
        self.assertFalse(prepared.robot_mode)


class TestBuildGlobalParser(unittest.TestCase):
    def test_trace_id_defaults_from_environment(self):
        with mock.patch.dict("os.environ", {"ASK_TRACE_ID": "trace-from-env"}):
            parser = build_global_parser()

        args = parser.parse_args([])

        self.assertEqual(args.trace_id, "trace-from-env")

    def test_trace_id_cli_value_overrides_environment_default(self):
        with mock.patch.dict("os.environ", {"ASK_TRACE_ID": "trace-from-env"}):
            parser = build_global_parser()

        args = parser.parse_args(["--trace-id", "trace-from-cli"])

        self.assertEqual(args.trace_id, "trace-from-cli")

    def test_robot_aliases_share_robot_mode_destination(self):
        parser = build_global_parser()

        for robot_flag in ("--robot", "--agent-mode", "-r"):
            with self.subTest(robot_flag=robot_flag):
                args = parser.parse_args([robot_flag])

                self.assertTrue(args.robot_mode)


if __name__ == "__main__":
    unittest.main()
