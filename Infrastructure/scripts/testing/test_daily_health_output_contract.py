"""Regression checks for generated recursive daily-health evidence."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE_PATH = ".harness/evidence/skill-graphs/telemetry/daily-skill-health.md"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


shadow_report = _load_module(
    "daily_health_shadow_report",
    REPO_ROOT / "Plugins/skill-factory/scripts/skill-builder/build_recursive_skill_shadow_report.py",
)
state_map = _load_module(
    "daily_health_state_map",
    REPO_ROOT / "Infrastructure/scripts/lifecycle-and-sync/build_skill_state_map_impl.py",
)


class DailyHealthOutputContractTests(unittest.TestCase):
    def test_live_consumers_default_to_generated_evidence(self) -> None:
        with mock.patch.object(sys, "argv", ["build_recursive_skill_shadow_report.py"]):
            shadow_args = shadow_report.parse_args()
        with mock.patch.object(sys, "argv", ["build_skill_state_map_impl.py"]):
            state_args = state_map.parse_args()

        self.assertEqual(shadow_report.CANONICAL_DAILY_HEALTH_DOC, EVIDENCE_PATH)
        self.assertEqual(state_map.CANONICAL_DAILY_HEALTH, EVIDENCE_PATH)
        self.assertEqual(shadow_args.daily_health_md, EVIDENCE_PATH)
        self.assertEqual(state_args.daily_health_md, EVIDENCE_PATH)
        self.assertEqual(state_args.runs_root, ".tmp/agent-skills-artifacts/skill-graphs/runs")

    def test_path_contract_rejects_a_tracked_docs_output(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            evidence = root / EVIDENCE_PATH
            evidence.parent.mkdir(parents=True)
            evidence.write_text("# Daily health\n", encoding="utf-8")
            docs_output = (root / "Docs/skill-graphs/telemetry/daily-skill-health.md").resolve()

            shadow_report.enforce_daily_health_path_contract(root, evidence.resolve())
            state_map.enforce_daily_health_contract(root, evidence.resolve())
            with self.assertRaisesRegex(RuntimeError, "must resolve"):
                shadow_report.enforce_daily_health_path_contract(root, docs_output)
            with self.assertRaisesRegex(RuntimeError, "must resolve"):
                state_map.enforce_daily_health_contract(root, docs_output)

    def test_workflow_uploads_evidence_without_committing_it(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/recursive-skill-shadow.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("contents: read", workflow)
        self.assertIn(EVIDENCE_PATH, workflow)
        self.assertIn(
            "bash Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle.sh",
            workflow,
        )
        self.assertIn("Docs lint (block mode)", workflow)
        self.assertIn("--mode block", workflow)
        self.assertIn("Docs/skill-graphs/pilots/ui-skills-shadow-results.md", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("Commit telemetry artifacts", workflow)
        self.assertNotIn("git push origin HEAD", workflow)
        self.assertNotIn("bash Infrastructure/scripts/run_recursive_skill_shadow_cycle.sh", workflow)
        self.assertNotIn("docs/skill-graphs/telemetry/daily-skill-health.md", workflow)

    def test_repository_does_not_track_a_generated_docs_copy(self) -> None:
        tracked_copy = REPO_ROOT / "Docs/skill-graphs/telemetry/daily-skill-health.md"

        self.assertFalse(tracked_copy.exists())


if __name__ == "__main__":
    unittest.main()
