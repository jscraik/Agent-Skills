from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
import unittest.mock
from pathlib import Path
from types import ModuleType, SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_ENTRYPOINT = REPO_ROOT / "Infrastructure" / "bin" / "ask"
SYNC_WRAPPER = REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync" / "sync_skills.sh"
VALIDATOR_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_ask_cli_modularity.py"
MAX_ENTRYPOINT_LINES = 1900


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_ask_cli_modularity", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ask CLI modularity validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestAskCliShape(unittest.TestCase):
    def test_entrypoint_line_budget_does_not_grow(self) -> None:
        line_count = len(ASK_ENTRYPOINT.read_text(encoding="utf-8").splitlines())

        self.assertLessEqual(
            line_count,
            MAX_ENTRYPOINT_LINES,
            (
                "Infrastructure/bin/ask is already at the decomposition limit; "
                "move parser, dispatch, output, or prompt behavior into ask.* modules "
                "before adding more entrypoint code."
            ),
        )

    def test_entrypoint_keeps_output_and_prompt_helpers_extracted(self) -> None:
        content = ASK_ENTRYPOINT.read_text(encoding="utf-8")

        self.assertIn("from ask.cli_output import", content)
        self.assertIn("from ask.cli_prompts import", content)
        self.assertNotIn("def print_first_validation_command", content)
        self.assertNotIn("def prompt_nonempty", content)

    def test_evals_run_exposes_timeout_seconds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ASK_ENTRYPOINT), "evals", "run", "--help"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        self.assertIn("--timeout-seconds", result.stdout)

    def test_evals_run_passes_timeout_seconds_to_runner(self) -> None:
        content = ASK_ENTRYPOINT.read_text(encoding="utf-8")

        self.assertIn("evals_run_parser.add_argument(\"--timeout-seconds\"", content)
        self.assertIn("timeout_seconds=args.timeout_seconds", content)

    def test_sync_wrapper_delegates_without_command_surface_fossils(self) -> None:
        content = SYNC_WRAPPER.read_text(encoding="utf-8")

        self.assertIn('exec bash "$SCRIPT_DIR/sync_skills_impl.sh" "$@"', content)
        self.assertNotIn("Keep legacy lifecycle command-surface text", content)
        self.assertNotIn("selection_policy.py", content)

    def test_function_shape_metrics_include_length_and_complexity(self) -> None:
        validator = _load_validator()
        metrics = validator._function_metrics(
            """
def sample(value):
    if value:
        return 1
    return 0
"""
        )

        self.assertEqual(metrics["sample"], (4, 2))

    def test_function_metrics_preserve_qualified_identity_for_moved_methods(self) -> None:
        validator = _load_validator()
        metrics = validator._function_metrics(
            """
class Runner:
    def execute(self, value):
        if value:
            return 1
        return 0
"""
        )

        self.assertIn("Runner.execute", metrics)
        self.assertNotIn("execute", metrics)

    def test_skills_sdk_evidence_status_and_hook_fixture_fit_shape_budget(self) -> None:
        validator = _load_validator()
        targets = {
            "Infrastructure/scripts/lib/ask/skills_sdk/evidence_status.py": {
                "build_evidence_status_receipt": (40, 12),
                "_build_acceptance_lane": (40, 12),
                "_load_or_build_qa_dispatch_record": (40, 12),
            },
            "Infrastructure/scripts/testing/test_validation_execution_environment.py": {
                "test_prek_reinstalls_when_expected_hooks_path_is_already_configured": (40, 12),
            },
        }

        for relative_path, functions in targets.items():
            metrics = validator._function_metrics(
                (REPO_ROOT / relative_path).read_text(encoding="utf-8")
            )
            for name, (max_lines, max_complexity) in functions.items():
                line_count, complexity = metrics[name]
                self.assertLessEqual(line_count, max_lines, f"{relative_path}:{name}")
                self.assertLessEqual(complexity, max_complexity, f"{relative_path}:{name}")

    def test_file_size_ratchet_allows_existing_oversized_file_only_when_it_shrinks(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_file_lines=3)
        issues: list[str] = []

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(issues, [])

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n5\n6\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(len(issues), 1)

    def test_unchanged_oversized_function_is_allowed_by_ratchet(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        source = "def sample(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        validator._check_function_shape(VALIDATOR_PATH, source, source, args, issues)

        self.assertEqual(issues, [])

    def test_growing_function_is_blocked_by_ratchet(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def sample(value):\n    if value:\n        return 1\n    return 0\n"
        baseline = "def sample(value):\n    return 0\n"
        issues: list[str] = []

        validator._check_function_shape(VALIDATOR_PATH, current, baseline, args, issues)

        self.assertEqual(len(issues), 2)
        self.assertIn("function line budget", issues[0])
        self.assertIn("complexity budget", issues[1])

    def test_changed_file_mode_defers_unrelated_expired_waivers(self) -> None:
        validator = _load_validator()
        original_debt = validator.LEGACY_SHAPE_DEBT
        try:
            validator.LEGACY_SHAPE_DEBT = {
                "test/expired.py": {
                    "owner": "test",
                    "rule_id": "ask-cli-shape-budget",
                    "ticket": "JSC-TEST",
                    "reason": "test reason",
                    "expires": "2020-01-01",
                }
            }
            args = SimpleNamespace(changed_files=("README.md",))
            self.assertEqual(validator._check_python_shape(args), [])
        finally:
            validator.LEGACY_SHAPE_DEBT = original_debt
    def test_moved_function_uses_deleted_sibling_as_shape_baseline(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def moved(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        with unittest.mock.patch.object(
            validator,
            "_moved_function_metrics",
            return_value={"moved": (4, 2)},
        ):
            validator._check_function_shape(VALIDATOR_PATH, current, None, args, issues)

        self.assertEqual(issues, [])

    def test_new_function_still_fails_without_a_move_baseline(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_function_lines=1, max_complexity=1)
        current = "def fresh(value):\n    if value:\n        return 1\n    return 0\n"
        issues: list[str] = []

        with unittest.mock.patch.object(validator, "_moved_function_metrics", return_value={}):
            validator._check_function_shape(VALIDATOR_PATH, current, None, args, issues)

        self.assertEqual(len(issues), 2)
        self.assertIn("function line budget", issues[0])
        self.assertIn("complexity budget", issues[1])

    def test_shape_baseline_failure_is_reported_and_stops_changed_file_scan(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(changed_files=("Infrastructure/scripts/validation-and-linting/verify_ask_cli_modularity.py",))
        with unittest.mock.patch.object(
            validator,
            "_shape_baseline",
            side_effect=RuntimeError("wrapper unavailable"),
        ):
            issues = validator._check_python_shape(args)

        self.assertEqual(len(issues), 1)
        self.assertIn("shape baseline unavailable", issues[0])

    def test_shape_baseline_requests_payload_for_repository_wide_lookup(self) -> None:
        validator = _load_validator()
        payload = {
            "data": {
                "shape_baseline": {
                    "deleted_python_paths": [],
                    "head_text": {},
                    "sibling_python_paths": [],
                }
            }
        }
        completed = SimpleNamespace(returncode=0, stdout=json.dumps(payload), stderr="")
        with unittest.mock.patch.object(validator.subprocess, "run", return_value=completed) as run:
            baseline = validator._shape_baseline()

        self.assertEqual(baseline, payload["data"]["shape_baseline"])
        command = run.call_args.args[0]
        self.assertIn("--baseline-path", command)
        self.assertIn("Infrastructure/bin/.shape-baseline.py", command)


if __name__ == "__main__":
    unittest.main()
