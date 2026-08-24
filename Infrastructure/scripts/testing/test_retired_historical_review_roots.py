#!/usr/bin/env python3
"""Keep retired historical review outputs out of tracked source."""

from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
RETIRED_ROOTS = (
    "artifacts/reviews/adversarial-reviewer.md",
    "artifacts/reviews/he-spec-plan-gap-hardening",
    "artifacts/reviews/jsc-351-pr192-triage-lane",
    "artifacts/reviews/jsc-351-pr193-review-stack",
    "artifacts/reviews/jsc-351-pr193-triage-lane",
    "artifacts/reviews/jsc-351-pu001",
    "artifacts/reviews/jsc-351-pu002",
    "artifacts/reviews/jsc-351-pu003",
    "artifacts/reviews/jsc-351-pu004",
    "artifacts/reviews/jsc-351-pu005",
    "artifacts/reviews/jsc-351-pu006",
    "artifacts/reviews/jsc-351-pu006-service-boundary",
    "artifacts/reviews/jsc-351-pu006-triage-lane",
    "artifacts/reviews/jsc-351-pu007-conformance",
    "artifacts/reviews/jsc-351-pu008-closeout",
    "artifacts/reviews/jsc-351-pu011",
    "artifacts/reviews/jsc-364-runtime-proof-plane",
    "artifacts/reviews/jsc-391-agent-first-skills-sdk-scaffold-refactor",
    "artifacts/reviews/pr215-post-review-pass-synthesis.md",
    "artifacts/reviews/skills-sdk-v1-0-product-implementation",
    "artifacts/reviews/skills-sdk-pu-015-review-handoff",
)
PRODUCER_ROOTS = (
    REPO_ROOT / ".github",
    REPO_ROOT / "Infrastructure/scripts",
    REPO_ROOT / "scripts",
)
VALIDATE_ALL = REPO_ROOT / "Infrastructure/scripts/validate_all_impl.sh"


def _is_scannable_producer(path: Path) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and "__pycache__" not in path.parts
        and path.suffix != ".pyc"
        and path.resolve() != Path(__file__).resolve()
    )


def _producer_references(retired_root: str) -> list[Path]:
    return [
        path.relative_to(REPO_ROOT)
        for root in PRODUCER_ROOTS
        if root.exists()
        for path in root.rglob("*")
        if _is_scannable_producer(path)
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

    def test_repo_test_scope_schedules_this_contract(self) -> None:
        validation_source = VALIDATE_ALL.read_text(encoding="utf-8")
        self.assertIn("test)\n      case \"$slug\" in\n        retired-review-roots|", validation_source)
        self.assertIn("schedule_check required retired-review-roots", validation_source)


if __name__ == "__main__":
    unittest.main()
