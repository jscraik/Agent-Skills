#!/usr/bin/env python3
"""Keep retired historical review outputs out of tracked source."""

from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
RETIRED_ROOTS = (
    "artifacts/reviews/he-spec-plan-gap-hardening",
)
PRODUCER_ROOTS = (
    REPO_ROOT / ".github",
    REPO_ROOT / "Infrastructure/scripts",
    REPO_ROOT / "scripts",
)


def _producer_references(retired_root: str) -> list[Path]:
    return [
        path.relative_to(REPO_ROOT)
        for root in PRODUCER_ROOTS
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and path.resolve() != Path(__file__).resolve()
        and retired_root in path.read_text(encoding="utf-8", errors="ignore")
    ]


class RetiredHistoricalReviewRootTests(unittest.TestCase):
    def test_retired_roots_contain_no_files(self) -> None:
        for retired_root in RETIRED_ROOTS:
            with self.subTest(retired_root=retired_root):
                self.assertFalse(any((REPO_ROOT / retired_root).rglob("*")))

    def test_live_producers_do_not_reference_retired_roots(self) -> None:
        for retired_root in RETIRED_ROOTS:
            with self.subTest(retired_root=retired_root):
                self.assertEqual(_producer_references(retired_root), [])


if __name__ == "__main__":
    unittest.main()
