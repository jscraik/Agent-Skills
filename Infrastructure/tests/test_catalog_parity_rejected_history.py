"""Focused rejected-history corruption tests."""

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from ask.catalog_parity import (  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
