#!/usr/bin/env python3
"""Keep recursive skill-graph producers and consumers on their owned roots."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_ROOT = Path(".tmp/agent-skills-artifacts/skill-graphs/runs")
CONTROLS_ROOT = Path(".harness/evidence/skill-graphs/controls")
LESSONS_ROOT = Path(".harness/evidence/skill-graphs/lessons")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


bootstrap = _load_module(
    "recursive_artifact_bootstrap",
    REPO_ROOT / "Infrastructure/scripts/skill-graph/bootstrap_recursive_skill_graph_artifacts.py",
)
genome_loop = _load_module(
    "recursive_artifact_genome_loop",
    REPO_ROOT / "Infrastructure/scripts/lifecycle-and-sync/run_skill_genome_loop.py",
)
spotlight = _load_module(
    "recursive_artifact_spotlight",
    REPO_ROOT / "Infrastructure/scripts/lifecycle-and-sync/skill_spotlight.py",
)
verifier = _load_module(
    "recursive_artifact_verifier",
    REPO_ROOT / "Infrastructure/scripts/skill-graph/verify_recursive_skill_graph_artifacts.py",
)


class RecursiveArtifactRootContractTests(unittest.TestCase):
    def test_run_consumers_share_the_shadow_cycle_output_root(self) -> None:
        self.assertEqual(Path(verifier.RUNNER), RUNS_ROOT)
        self.assertEqual(genome_loop.RUNS_ROOT, RUNS_ROOT)
        self.assertEqual(spotlight.RUNS_ROOT, RUNS_ROOT)

        promotion_script = (
            REPO_ROOT
            / "Infrastructure/scripts/lifecycle-and-sync/human_promote_recursive_run_impl.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(str(RUNS_ROOT), promotion_script)
        self.assertNotIn(".harness/evidence/skill-graphs/runs", promotion_script)

        producer = (
            REPO_ROOT
            / "Infrastructure/scripts/lifecycle-and-sync/run_recursive_skill_shadow_cycle_impl.sh"
        ).read_text(encoding="utf-8")
        promotion_validator = (
            REPO_ROOT
            / "Infrastructure/scripts/lifecycle-and-sync/validate_recursive_promotions_impl.sh"
        ).read_text(encoding="utf-8")
        self.assertIn(f'out_root="{RUNS_ROOT}"', producer)
        self.assertIn(f'runs_root="{RUNS_ROOT}"', promotion_validator)

    def test_live_scripts_do_not_reference_the_retired_run_root(self) -> None:
        scripts_root = REPO_ROOT / "Infrastructure/scripts"
        retired_root = ".harness/evidence/skill-graphs/runs"
        offenders = [
            path.relative_to(REPO_ROOT)
            for directory in (scripts_root / "lifecycle-and-sync", scripts_root / "skill-graph")
            for pattern in ("*.py", "*.sh")
            for path in directory.rglob(pattern)
            if retired_root in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_bootstrap_initializes_the_runtime_control_and_lesson_roots(self) -> None:
        self.assertEqual(bootstrap.DEFAULT_CONTROL_ROOT, CONTROLS_ROOT)
        self.assertEqual(bootstrap.DEFAULT_LESSONS_ROOT, LESSONS_ROOT)

    def test_shadow_workflow_uploads_dot_prefixed_evidence(self) -> None:
        workflow = (REPO_ROOT / ".github/workflows/recursive-skill-shadow.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("include-hidden-files: true", workflow)


if __name__ == "__main__":
    unittest.main()
