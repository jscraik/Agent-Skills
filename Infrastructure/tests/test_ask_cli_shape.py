from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import ModuleType, SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_ENTRYPOINT = REPO_ROOT / "Infrastructure" / "bin" / "ask"
VALIDATOR_PATH = REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting" / "verify_ask_cli_modularity.py"


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_ask_cli_modularity", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load ask CLI modularity validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestAskCliShape(unittest.TestCase):
    def test_evals_run_exposes_timeout_seconds(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ASK_ENTRYPOINT), "evals", "run", "--help"],
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )

        self.assertIn("--timeout-seconds", result.stdout)

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

    def test_file_size_ratchet_allows_existing_oversized_file_only_when_it_shrinks(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_file_lines=3)
        issues: list[str] = []

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(issues, [])

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n5\n6\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(len(issues), 1)

    def test_legacy_shape_debt_exempts_registered_paths_from_shape_ratchets(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_file_lines=1, max_function_lines=1, max_complexity=1)
        path = REPO_ROOT / "Infrastructure/scripts/lib/ask/commands/evals.py"
        current = "def sample(value):\n    if value:\n        return 1\n    return 0\n"
        baseline = "def sample(value):\n    return 0\n"
        issues: list[str] = []

        validator._check_file_size(path, current, baseline, args, issues)
        validator._check_function_shape(path, current, baseline, args, issues)

        self.assertEqual(issues, [])

    def test_legacy_shape_debt_registry_is_explicit(self) -> None:
        validator = _load_validator()

        self.assertEqual(validator.LEGACY_SHAPE_DEBT_PATHS, frozenset(validator.LEGACY_SHAPE_DEBT))
        self.assertGreaterEqual(len(validator.LEGACY_SHAPE_DEBT), 2)
        for metadata in validator.LEGACY_SHAPE_DEBT.values():
            self.assertTrue(metadata["owner"])
            self.assertTrue(metadata["rule_id"])
            self.assertTrue(metadata["ticket"])
            self.assertTrue(metadata["reason"])
            self.assertRegex(metadata["expires"], r"^20\d{2}-\d{2}-\d{2}$")

    def test_legacy_shape_debt_metadata_validation_detects_missing_fields(self) -> None:
        validator = _load_validator()
        original_debt = validator.LEGACY_SHAPE_DEBT
        try:
            validator.LEGACY_SHAPE_DEBT = {
                "test/missing_ticket.py": {
                    "owner": "test",
                    "rule_id": "ask-cli-shape-budget",
                    "reason": "test reason",
                    "expires": "2026-12-31",
                }
            }

            issues = validator._check_legacy_shape_debt_metadata()

            self.assertEqual(len(issues), 1)
            self.assertIn("missing waiver field(s): ticket", issues[0])
        finally:
            validator.LEGACY_SHAPE_DEBT = original_debt

    def test_legacy_shape_debt_metadata_validation_detects_expired_waivers(self) -> None:
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

            issues = validator._check_legacy_shape_debt_metadata()

            self.assertEqual(len(issues), 1)
            self.assertIn("expired on 2020-01-01", issues[0])
        finally:
            validator.LEGACY_SHAPE_DEBT = original_debt

    def test_legacy_shape_debt_metadata_validation_detects_invalid_dates(self) -> None:
        validator = _load_validator()
        original_debt = validator.LEGACY_SHAPE_DEBT
        try:
            validator.LEGACY_SHAPE_DEBT = {
                "test/invalid_date.py": {
                    "owner": "test",
                    "rule_id": "ask-cli-shape-budget",
                    "ticket": "JSC-TEST",
                    "reason": "test reason",
                    "expires": "not-a-date",
                }
            }

            issues = validator._check_legacy_shape_debt_metadata()

            self.assertEqual(len(issues), 1)
            self.assertIn("invalid expires date: not-a-date", issues[0])
        finally:
            validator.LEGACY_SHAPE_DEBT = original_debt

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


if __name__ == "__main__":
    unittest.main()
