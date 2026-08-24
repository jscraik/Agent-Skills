#!/usr/bin/env python3
"""Keep recursive skill-graph producers and consumers on their owned roots."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNS_ROOT = Path(".tmp/agent-skills-artifacts/skill-graphs/runs")
CONTROLS_ROOT = Path(".harness/evidence/skill-graphs/controls")
LESSONS_ROOT = Path(".harness/evidence/skill-graphs/lessons")
RETIRED_PILOT_ROOT = (REPO_ROOT / "Infrastructure/artifacts/skill-graphs/pilot").resolve()
RETIRED_TRACKED_RUNS_ROOT = (REPO_ROOT / "artifacts/skill-graphs/runs").resolve()


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _normalized_repo_path(value: str | Path) -> Path:
    return (REPO_ROOT / Path(value)).resolve()


def _quoted_assignment(path: Path, name: str) -> Path:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf'^{re.escape(name)}=["\']([^"\']+)["\']$', source, re.MULTILINE)
    assert match is not None, f"missing {name} assignment in {path.relative_to(REPO_ROOT)}"
    return _normalized_repo_path(match.group(1))


def _shell_default(path: Path, name: str) -> Path:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        rf'^{re.escape(name)}=["\']\$\{{[A-Z0-9_]+:-([^}}]+)\}}["\']$',
        source,
        re.MULTILINE,
    )
    assert match is not None, f"missing {name} default in {path.relative_to(REPO_ROOT)}"
    return _normalized_repo_path(match.group(1))


def _python_default(path: Path, option: str) -> Path:
    source = path.read_text(encoding="utf-8")
    match = re.search(
        rf'["\']{re.escape(option)}["\'][\s\S]*?default\s*=\s*["\']([^"\']+)["\']',
        source,
    )
    assert match is not None, f"missing {option} default in {path.relative_to(REPO_ROOT)}"
    return _normalized_repo_path(match.group(1))


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
    def test_retired_tracked_run_root_is_absent(self) -> None:
        self.assertFalse(RETIRED_TRACKED_RUNS_ROOT.exists())

    def test_retired_tracked_pilot_root_is_absent(self) -> None:
        self.assertFalse((REPO_ROOT / "Infrastructure/artifacts/skill-graphs/pilot").exists())

    def test_live_scripts_do_not_write_the_retired_tracked_pilot_root(self) -> None:
        scripts_root = REPO_ROOT / "Infrastructure/scripts"
        retired_root = "Infrastructure/artifacts/skill-graphs/pilot"
        offenders = [
            path.relative_to(REPO_ROOT)
            for directory in (scripts_root / "lifecycle-and-sync", scripts_root / "skill-graph")
            for pattern in ("*.py", "*.sh")
            for path in directory.rglob(pattern)
            if retired_root in path.read_text(encoding="utf-8")
        ]
        self.assertEqual(offenders, [])

    def test_live_pilot_producer_destinations_resolve_outside_retired_root(self) -> None:
        lifecycle_root = REPO_ROOT / "Infrastructure/scripts/lifecycle-and-sync"
        skill_graph_root = REPO_ROOT / "Infrastructure/scripts/skill-graph"
        shadow_cycle = lifecycle_root / "run_recursive_skill_shadow_cycle_impl.sh"
        rollout_drill = lifecycle_root / "run_recursive_rollout_drill_impl.sh"
        promotion = lifecycle_root / "validate_recursive_promotions_impl.sh"
        state_map = lifecycle_root / "build_skill_state_map_impl.py"

        destinations = {
            "bootstrap manifest": _python_default(
                skill_graph_root / "bootstrap_recursive_skill_graph_artifacts.py",
                "--manifest",
            ),
            "verifier manifest": _normalized_repo_path(verifier.DEFAULT_MANIFEST),
            "shadow dashboard": _quoted_assignment(shadow_cycle, "dashboard_json"),
            "shadow baseline": _quoted_assignment(shadow_cycle, "baseline_snapshot_json"),
            "rollback report": _shell_default(rollout_drill, "report_json"),
            "promotion report": _quoted_assignment(promotion, "report_json"),
            "promotion manifest": _quoted_assignment(promotion, "parity_manifest"),
            "state-map dashboard": _python_default(state_map, "--shadow-dashboard"),
            "state-map promotion": _python_default(state_map, "--promotion-validation"),
            "state-map manifest": _python_default(state_map, "--parity-manifest"),
        }

        for label, destination in destinations.items():
            with self.subTest(label=label):
                self.assertFalse(destination.is_relative_to(RETIRED_PILOT_ROOT), destination)

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
