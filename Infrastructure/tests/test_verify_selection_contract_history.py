import importlib.util
import json
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
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
    rejected_history_path,
)


SPEC = importlib.util.spec_from_file_location(
    "verify_selection_contract_history", SCRIPT_PATH
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestVerifySelectionContractHistory(unittest.TestCase):
    def test_negative_fixture_count_is_invalid_history(self) -> None:
        """Corrupt negative totals cannot be downgraded to absent history."""
        rates, issue = MODULE.catalog_parity_module._history_rates(
            {
                "totals": {"fixtures": -1},
                "status_counts": {
                    "unresolved_ambiguity": 0,
                    "degraded_no_candidates": 0,
                },
            }
        )

        self.assertIsNone(rates)
        self.assertEqual(issue, "schema_invalid_history")

    def test_concurrent_history_writers_preserve_every_sample(self) -> None:
        """Serialized atomic updates do not lose accepted concurrent rows."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"

            def append(index: int) -> str | None:
                return MODULE._append_history(
                    history_path,
                    {
                        "generated_at": str(index),
                        "no_candidate_rate": 0.0,
                        "unresolved_ambiguity_rate": 0.0,
                    },
                    max_runs=32,
                )

            with ThreadPoolExecutor(max_workers=8) as executor:
                issues = list(executor.map(append, range(16)))

            rows = [
                json.loads(line)
                for line in history_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(issues, [None] * 16)
            self.assertEqual(
                {row["generated_at"] for row in rows}, {str(i) for i in range(16)}
            )

    def test_route_fixture_loader_rejects_malformed_json(self) -> None:
        """Malformed route input returns the stable invalid-fixture result."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "routes.json"
            path.write_text("not-json", encoding="utf-8")

            self.assertIsNone(MODULE._load_routes(path))
            fixtures, issue = MODULE._read_fixture_objects(path)
            self.assertIsNone(fixtures)
            self.assertEqual(issue, "fixture_read_error:JSONDecodeError")

    def test_route_fixture_loader_rejects_non_object_entries(self) -> None:
        """Route evaluation never receives scalar fixture entries."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "routes.json"
            path.write_text('{"fixtures": [1]}', encoding="utf-8")

            self.assertIsNone(MODULE._load_routes(path))
            fixtures, issue = MODULE._read_fixture_objects(path)
            self.assertIsNone(fixtures)
            self.assertEqual(issue, "fixture_entries_must_be_objects")

    def test_goal_fixture_loader_reports_invalid_root(self) -> None:
        """Optional goal input records a failed result instead of raising."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "goals.json"
            path.write_text("[]", encoding="utf-8")

            results, statuses, failures, mapping_failures = MODULE._evaluate_goals(
                path, "policy"
            )

            self.assertEqual(results[0]["id"], "goal-fixtures")
            self.assertEqual(results[0]["issues"], ["fixture_root_must_be_object"])
            self.assertFalse(results[0]["passed"])
            self.assertFalse(statuses)
            self.assertFalse(failures)
            self.assertEqual(mapping_failures, 0)

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

    def test_repaired_history_revalidates_preserved_candidate(self) -> None:
        """A repaired baseline unblocks a preserved candidate that now validates."""
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            history_path = repo_root / MODULE.catalog_parity_module.HISTORY_PATH
            history_path.parent.mkdir(parents=True)
            candidate = {
                "unresolved_ambiguity_rate": 0.1,
                "no_candidate_rate": 0.1,
            }
            MODULE._write_rejected_history(
                history_path, candidate, "schema_invalid_history"
            )
            history_path.write_text(
                "".join(json.dumps(candidate) + "\n" for _ in range(8)),
                encoding="utf-8",
            )

            status, blocker = _history_trend_drift(repo_root)

            self.assertEqual(status, "available")
            self.assertIsNone(blocker)

    def test_invalid_rejected_sidecar_names_repository_relative_repair_path(
        self,
    ) -> None:
        """Strict remediation identifies the actual rejected evidence path."""
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            history_path = repo_root / MODULE.catalog_parity_module.HISTORY_PATH
            history_path.parent.mkdir(parents=True)
            history_path.write_text(
                json.dumps(
                    {
                        "unresolved_ambiguity_rate": 0.1,
                        "no_candidate_rate": 0.1,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rejected_history_path(history_path).write_text(
                "not-json\n", encoding="utf-8"
            )

            status, blocker = _history_trend_drift(repo_root)

            self.assertEqual(status, "schema_invalid_history")
            self.assertIsNotNone(blocker)
            self.assertIn(
                rejected_history_path(
                    MODULE.catalog_parity_module.HISTORY_PATH
                ).as_posix(),
                blocker[2] if blocker else "",
            )

    def test_orphaned_rejection_sidecar_is_not_collected(self) -> None:
        """Rejected evidence alone does not invent canonical history telemetry."""
        with TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            history_path = repo_root / MODULE.catalog_parity_module.HISTORY_PATH
            MODULE._write_rejected_history(
                history_path,
                {"unresolved_ambiguity_rate": 0.3, "no_candidate_rate": 0.1},
                "trend_deterioration",
            )

            status, blocker = _history_trend_drift(repo_root)

            self.assertEqual(status, "not_collected")
            self.assertIsNone(blocker)

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

    def test_accepted_append_clears_rejected_sidecar(self) -> None:
        """A successful append removes stale rejection evidence."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            row = {"unresolved_ambiguity_rate": 0.1, "no_candidate_rate": 0.1}
            MODULE._write_rejected_history(history_path, row, "trend_deterioration")
            self.assertTrue(rejected_history_path(history_path).exists())

            self.assertIsNone(MODULE._append_history(history_path, row, max_runs=200))

            self.assertFalse(rejected_history_path(history_path).exists())

    def test_not_recorded_history_is_not_a_passing_gate(self) -> None:
        """Skipped persistence is explicit for absent paths and failed fixtures."""
        artifact = {
            "run_id": "run",
            "generated_at": "now",
            "decision_status_counts": {},
            "parity_status": "pass",
            "unresolved_ambiguity_rate": 0.0,
            "no_candidate_rate": 0.0,
            "gate_outcomes": {"hard": {}},
        }
        args = MODULE.argparse.Namespace(history_path=None, history_max_runs=200)

        self.assertIsNone(MODULE._apply_history_outcome(args, [], artifact, "policy"))
        self.assertEqual(artifact["history_status"], "not_recorded")
        self.assertEqual(
            artifact["gate_outcomes"]["hard"]["history_persistence"],
            "not_applicable",
        )

        args.history_path = Path("unused.jsonl")
        failed = [{"passed": False}]
        self.assertIsNone(
            MODULE._apply_history_outcome(args, failed, artifact, "policy")
        )
        self.assertEqual(artifact["history_status"], "not_recorded")
        self.assertEqual(
            artifact["gate_outcomes"]["hard"]["history_persistence"],
            "not_applicable",
        )

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
            self.assertTrue(rejected_history_path(history_path).exists())

    def test_artifact_write_failure_rolls_back_history_mutation(self) -> None:
        """A failed required receipt cannot advance the accepted baseline."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            history_path = root / "history.jsonl"
            artifact_path = root / "artifact-as-directory"
            artifact_path.mkdir()
            args = MODULE.argparse.Namespace(
                artifact=artifact_path,
                history_path=history_path,
                history_max_runs=200,
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

            with self.assertRaises(OSError):
                MODULE._persist_artifact_and_history(args, [], artifact, "policy")

            self.assertFalse(history_path.exists())
            self.assertFalse(rejected_history_path(history_path).exists())


if __name__ == "__main__":
    unittest.main()
