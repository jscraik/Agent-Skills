#!/usr/bin/env python3
"""Keep consistency-gate output out of the tracked repository surface."""

from __future__ import annotations

from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
RETIRED_TRACKED_ROOT = REPO_ROOT / "artifacts/consistency-gate"
RETIRED_ROOT_TEXT = "artifacts/consistency-gate"
RUNTIME_ROOT_TEXT = ".tmp/agent-skills-artifacts/consistency-gate"
PRODUCER_ROOTS = (
    REPO_ROOT / ".github",
    REPO_ROOT / "Infrastructure/scripts",
    REPO_ROOT / "scripts",
)


class ConsistencyGateOutputRootContractTests(unittest.TestCase):
    def test_retired_tracked_root_is_absent(self) -> None:
        self.assertFalse(RETIRED_TRACKED_ROOT.exists())

    def test_live_producers_do_not_reference_retired_tracked_root(self) -> None:
        offenders = [
            path.relative_to(REPO_ROOT)
            for root in PRODUCER_ROOTS
            if root.exists()
            for path in root.rglob("*")
            if path.is_file()
            and not path.is_symlink()
            and path.resolve() != Path(__file__).resolve()
            and re.search(
                rf"(?<!agent-skills-){re.escape(RETIRED_ROOT_TEXT)}",
                path.read_text(encoding="utf-8", errors="ignore"),
            )
        ]
        self.assertEqual(offenders, [])

    def test_pr_pipeline_writes_consistency_output_to_runtime_root(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/pr-pipeline.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn(RUNTIME_ROOT_TEXT, workflow)


if __name__ == "__main__":
    unittest.main()
