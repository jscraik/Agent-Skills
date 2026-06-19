from __future__ import annotations

import importlib.util
import sys
import unittest
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

    def test_file_size_ratchet_allows_existing_oversized_file_only_when_it_shrinks(self) -> None:
        validator = _load_validator()
        args = SimpleNamespace(max_file_lines=3)
        issues: list[str] = []

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(issues, [])

        validator._check_file_size(VALIDATOR_PATH, "1\n2\n3\n4\n5\n6\n", "1\n2\n3\n4\n5\n", args, issues)
        self.assertEqual(len(issues), 1)

    def test_legacy_shape_debt_registry_is_explicit(self) -> None:
        validator = _load_validator()

        self.assertEqual(validator.LEGACY_SHAPE_DEBT_PATHS, frozenset(validator.LEGACY_SHAPE_DEBT))
        self.assertGreaterEqual(len(validator.LEGACY_SHAPE_DEBT), 2)
        for metadata in validator.LEGACY_SHAPE_DEBT.values():
            self.assertTrue(metadata["owner"])
            self.assertTrue(metadata["reason"])
            self.assertRegex(metadata["expires"], r"^20\d{2}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
