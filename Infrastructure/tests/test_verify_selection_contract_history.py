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

from ask.catalog_parity import (  # noqa: E402
    _history_trend_drift,
    _latest_history_metrics,
    _rejected_history_path,
)


SPEC = importlib.util.spec_from_file_location(
    "verify_selection_contract_history", SCRIPT_PATH
)
assert SPEC is not None
assert SPEC.loader is not None
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

            rows = [
                json.loads(line)
                for line in history_path.read_text(encoding="utf-8").splitlines()
            ]
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

    def test_rejected_candidate_remains_visible_to_strict_diagnostics(self) -> None:
        """Strict diagnostics consume rejection evidence without polluting baseline."""
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            history_path = repo_root / MODULE.catalog_parity_module.HISTORY_PATH
            baseline = [
                {"unresolved_ambiguity_rate": 0.1, "no_candidate_rate": 0.1}
                for _ in range(7)
            ]
            history_path.parent.mkdir(parents=True)
            history_path.write_text(
                "".join(json.dumps(row) + "\n" for row in baseline), encoding="utf-8"
            )
            candidate = {"unresolved_ambiguity_rate": 0.3, "no_candidate_rate": 0.1}

            self.assertEqual(
                MODULE._append_history(history_path, candidate, max_runs=200),
                "trend_deterioration",
            )
            status, blocker = _history_trend_drift(repo_root)
            self.assertEqual(status, "trend_deterioration")
            self.assertEqual(blocker[0] if blocker else None, "trend_deterioration")

    def test_history_retention_never_drops_below_trend_window(self) -> None:
        """Direct callers retain the minimum complete eight-sample window."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            for index in range(9):
                row = {
                    "unresolved_ambiguity_rate": 0.1,
                    "no_candidate_rate": 0.1,
                    "generated_at": str(index),
                }
                self.assertIsNone(MODULE._append_history(history_path, row, max_runs=1))
            self.assertEqual(len(history_path.read_text().splitlines()), 8)

    def test_history_rejection_is_bound_into_artifact(self) -> None:
        """The emitted artifact cannot claim success when history is rejected."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            history_path.write_text("not-json\n", encoding="utf-8")
            args = MODULE.argparse.Namespace(
                history_path=history_path, history_max_runs=200
            )
            artifact = {
                "run_id": "run",
                "generated_at": "now",
                "decision_status_counts": {},
                "parity_status": "pass",
                "unresolved_ambiguity_rate": 0.0,
                "no_candidate_rate": 0.0,
                "gate_outcomes": {"hard": {}},
            }

            issue = MODULE._apply_history_outcome(args, [], artifact, "policy")

            self.assertEqual(issue, "schema_invalid_history")
            self.assertEqual(artifact["history_status"], "schema_invalid_history")
            self.assertEqual(
                artifact["gate_outcomes"]["hard"]["history_persistence"], "fail"
            )
            self.assertTrue(_rejected_history_path(history_path).exists())


if __name__ == "__main__":
    unittest.main()
