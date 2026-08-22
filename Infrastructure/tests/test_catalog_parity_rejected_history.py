"""Focused rejected-history corruption tests."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.catalog_parity import (  # noqa: E402
    _history_rates,
    _read_history_rows,
    _rejected_history_issue,
    rejected_history_path,
)


class TestRejectedHistoryEvidence(unittest.TestCase):
    """Classify corrupt rejected-history evidence without tracebacks."""

    def test_non_utf8_sidecar_is_invalid_history(self) -> None:
        """Non-UTF-8 rejected bytes produce the stable schema issue."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            history_path.write_text("{}\n", encoding="utf-8")
            rejected_history_path(history_path).write_bytes(b"\xff")

            self.assertEqual(
                _rejected_history_issue(history_path), "schema_invalid_history"
            )

    def test_non_utf8_canonical_history_is_invalid(self) -> None:
        """Invalid canonical bytes cannot be discarded before validation."""
        with TemporaryDirectory() as tmpdir:
            history_path = Path(tmpdir) / "history.jsonl"
            history_path.write_bytes(b"\xff")

            self.assertEqual(
                _read_history_rows(history_path), (None, "schema_invalid_history")
            )

    def test_boolean_history_metrics_are_invalid(self) -> None:
        """Boolean rates and counters cannot become numeric baseline evidence."""
        payloads = (
            {"unresolved_ambiguity_rate": True, "no_candidate_rate": 0.1},
            {
                "totals": {"fixtures": True},
                "status_counts": {
                    "unresolved_ambiguity": 0,
                    "degraded_no_candidates": 0,
                },
            },
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(
                    _history_rates(payload), (None, "schema_invalid_history")
                )

    def test_string_history_metrics_are_invalid(self) -> None:
        """Numeric-looking strings cannot become trusted baseline evidence."""
        payloads = (
            {"unresolved_ambiguity_rate": "0.1", "no_candidate_rate": 0.1},
            {
                "totals": {"fixtures": "10"},
                "status_counts": {
                    "unresolved_ambiguity": 0,
                    "degraded_no_candidates": 0,
                },
            },
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(
                    _history_rates(payload), (None, "schema_invalid_history")
                )

    def test_oversized_history_metrics_are_invalid(self) -> None:
        """Arbitrary-size JSON integers cannot crash history validation."""
        oversized = 10**1000
        payloads = (
            {
                "unresolved_ambiguity_rate": oversized,
                "no_candidate_rate": 0.1,
            },
            {
                "totals": {"fixtures": oversized},
                "status_counts": {
                    "unresolved_ambiguity": 0,
                    "degraded_no_candidates": 0,
                },
            },
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                self.assertEqual(
                    _history_rates(payload), (None, "schema_invalid_history")
                )


if __name__ == "__main__":
    unittest.main()
