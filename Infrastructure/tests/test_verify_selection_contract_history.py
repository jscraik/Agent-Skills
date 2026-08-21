import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validation-and-linting"
    / "verify_selection_contract.py"
)
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.catalog_parity import _latest_history_metrics  # noqa: E402


SPEC = importlib.util.spec_from_file_location("verify_selection_contract_history", SCRIPT_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestVerifySelectionContractHistory(unittest.TestCase):
    def test_consecutive_unchanged_runs_append_distinct_history_rows(self) -> None:
        """Every completed persistent run contributes one bounded history sample."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            first = {
                "generated_at": "2026-08-22T00:00:00+00:00",
                "no_candidate_rate": 0.0,
                "unresolved_ambiguity_rate": 0.0,
            }
            second = {**first, "generated_at": "2026-08-22T00:00:01+00:00"}

            MODULE._append_history(history_path, first, max_runs=200)
            MODULE._append_history(history_path, second, max_runs=200)

            rows = [json.loads(line) for line in history_path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(rows, [first, second])

    def test_partial_history_remains_explicit_without_blocking(self) -> None:
        """Consecutive early runs remain collecting until the trend window is complete."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            row = {
                "generated_at": "2026-08-22T00:00:00+00:00",
                "no_candidate_rate": 0.0,
                "unresolved_ambiguity_rate": 0.0,
            }
            MODULE._append_history(history_path, row, max_runs=200)
            MODULE._append_history(history_path, row, max_runs=200)

            metrics, issue = _latest_history_metrics(history_path)
            self.assertIsNone(metrics)
            self.assertEqual(issue, "insufficient_history")

    def test_malformed_history_is_preserved_and_rejected(self) -> None:
        """A producer run cannot erase corruption before strict diagnostics see it."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            history_path.write_text("not-json\n", encoding="utf-8")
            row = {"unresolved_ambiguity_rate": 0.0, "no_candidate_rate": 0.0}

            issue = MODULE._append_history(history_path, row, max_runs=200)

            self.assertEqual(issue, "schema_invalid_history")
            self.assertEqual(history_path.read_text(encoding="utf-8"), "not-json\n")

    def test_deteriorating_candidate_is_not_added_to_baseline(self) -> None:
        """Repeated failed candidates cannot age a healthy baseline out of the window."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            baseline = [
                {"unresolved_ambiguity_rate": 0.1, "no_candidate_rate": 0.1}
                for _ in range(7)
            ]
            original = "".join(json.dumps(row) + "\n" for row in baseline)
            history_path.write_text(original, encoding="utf-8")
            candidate = {"unresolved_ambiguity_rate": 0.3, "no_candidate_rate": 0.1}

            for _ in range(5):
                issue = MODULE._append_history(history_path, candidate, max_runs=200)
                self.assertEqual(issue, "trend_deterioration")

            self.assertEqual(history_path.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
