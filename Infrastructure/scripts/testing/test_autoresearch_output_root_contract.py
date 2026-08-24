#!/usr/bin/env python3
"""Keep autoresearch run output out of the tracked repository surface."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
SKILL_ROOT = (
    REPO_ROOT
    / "Infrastructure/references/deferred-skill-context/agent-ops-autoresearch"
)
INIT_RUN = SKILL_ROOT / "scripts/init_run.sh"
LOG_RESULT = SKILL_ROOT / "scripts/log_result.py"
RUNTIME_ROOT = Path(".tmp/agent-skills-artifacts/autoresearch")
RETIRED_TRACKED_ROOT = REPO_ROOT / "artifacts/autoresearch"


def _load_log_result():
    spec = importlib.util.spec_from_file_location("autoresearch_log_result", LOG_RESULT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AutoresearchOutputRootContractTests(unittest.TestCase):
    def test_retired_tracked_root_is_absent(self) -> None:
        self.assertFalse(RETIRED_TRACKED_ROOT.exists())

    def test_log_result_uses_repo_scoped_runtime_root(self) -> None:
        module = _load_log_result()
        self.assertEqual(module.REPO_ROOT, REPO_ROOT)
        self.assertEqual(module.AUTORESEARCH_ROOT, REPO_ROOT / RUNTIME_ROOT)

    def test_initializer_defaults_to_ignored_runtime_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            checkout = Path(temp_dir)
            subprocess.run(["git", "init", "-q"], cwd=checkout, check=True)
            target = checkout / "target.txt"
            target.write_text("fixture\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    "bash",
                    str(INIT_RUN),
                    "--tag",
                    "contract-test",
                    "--targets",
                    "target.txt",
                ],
                cwd=checkout,
                check=True,
                capture_output=True,
                text=True,
            )

            run_dir = Path(completed.stdout.strip()).resolve()
            self.assertTrue(run_dir.is_relative_to((checkout / RUNTIME_ROOT).resolve()))
            self.assertTrue((run_dir / "results.tsv").is_file())
            self.assertTrue((run_dir / "journal.md").is_file())
            self.assertTrue((run_dir / "targets.txt").is_file())


if __name__ == "__main__":
    unittest.main()
