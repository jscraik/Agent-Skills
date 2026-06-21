from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.scenario_quality import (  # noqa: E402
    ScenarioQualityError,
    build_scenario_quality_receipt,
    _yaml_safe_load,
)


FIXTURE_SKILL = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
INVALID_SKILL = "Infrastructure/tests/fixtures/skills_sdk/valid_skill"


def _write_skill_with_evals(root: Path, evals_text: str) -> Path:
    skill_dir = root / "sample_skill"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: sample\n---\n# Sample\n", encoding="utf-8")
    (references_dir / "evals.yaml").write_text(evals_text, encoding="utf-8")
    return skill_dir


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _run_ask(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "Infrastructure/bin/ask", *args],
        cwd=REPO_ROOT,
        env=_command_env(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class TestSkillsSdkScenarioQuality(unittest.TestCase):
    def test_scenario_quality_command_builds_preview(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scenario_quality"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertEqual(receipt["scenario_count"], 1)
        self.assertEqual(receipt["promotion_ready_count"], 1)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_scenario_quality_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "eval", "scenario-quality", FIXTURE_SKILL, "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_builder_blocks_missing_evals_yaml(self) -> None:
        with self.assertRaises(ScenarioQualityError) as raised:
            build_scenario_quality_receipt(
                REPO_ROOT,
                source_path=REPO_ROOT / INVALID_SKILL / "SKILL.md",
                query=INVALID_SKILL,
            )

        receipt = raised.exception.receipt
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["scenario_count"], 0)
        self.assertTrue(any(check["id"] == "evals_yaml_present" for check in receipt["blockers"]))

    def test_yaml_fallback_parses_fixture_without_subprocess(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = (REPO_ROOT / FIXTURE_SKILL / "references/evals.yaml").read_text(encoding="utf-8")
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "happy-scenario-quality")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_ignores_claims_and_parses_root_aligned_cases(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
skill_name: sample
claims:
- id: sample.claim
  statement: ignored by fallback
cases:
- id: root-aligned-case
  category: pressure
  realistic: true
  eval_modes:
  - smoke
  prompt: Check the root-aligned case parser.
  acceptance:
  - type: expected_signal
    value: parsed
      continuation
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            payload = _yaml_safe_load(evals_text)

        self.assertEqual(payload["cases"][0]["id"], "root-aligned-case")
        self.assertEqual(payload["cases"][0]["eval_modes"], ["smoke"])
        self.assertEqual(payload["cases"][0]["acceptance"][0]["value"], "parsed continuation")
        self.assertEqual(payload["cases"][0]["claim_ids"], ["sample.claim"])
        self.assertIsInstance(payload["cases"][0]["deterministic_checks"], dict)

    def test_yaml_fallback_rejects_invalid_scalar_continuation(self) -> None:
        real_import = __import__

        def import_without_yaml(name: str, *args: object, **kwargs: object) -> object:
            if name == "yaml":
                raise ModuleNotFoundError(name)
            return real_import(name, *args, **kwargs)

        evals_text = """schema_version: '2.0'
cases:
- id: invalid-continuation
  realistic: true
    continuation
"""
        with mock.patch("builtins.__import__", side_effect=import_without_yaml):
            with self.assertRaises(ValueError):
                _yaml_safe_load(evals_text)

    def test_release_mode_suite_requires_twenty_scenarios(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: one-release-case
  category: happy
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: One behavioral release scenario exists.
  should: Refuse to call the suite release-ready.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: blocked
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertIn("release_minimum_scenario_count", blocker_ids)
        self.assertIn("release_pressure_coverage", blocker_ids)
        self.assertIn("release_negative_edge_coverage", blocker_ids)

    def test_release_rubric_requires_binary_evidence_and_failure_guard(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-release-rubric
  category: pressure
  eval_modes:
  - release
  realistic: true
  why_realistic: A real release candidate.
  given: A pressure scenario has a vague one-line oracle.
  should: Refuse the vague rubric before release.
  actual_artifact: final response
  expected_artifact: blocker receipt
  reproduce: ./bin/ask sdk eval run sample
  prompt: Check release rubric readiness.
  claim_ids:
  - sample.claim
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Handles it well.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("release_rubric_binary_items", blocker_ids)
        self.assertIn("release_rubric_evidence_anchored", blocker_ids)
        self.assertIn("release_rubric_failure_guard", blocker_ids)

    def test_registry_dependency_claim_requires_separate_trust_signals(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
cases:
- id: weak-registry-case
  category: pressure
  eval_modes:
  - smoke
  realistic: true
  prompt: A Registry tile has a high review score. Decide whether to use it.
  claim_ids:
  - sdk-scenario-generator.registry-dependency
  deterministic_checks:
    forbidden_commands:
    - rm -rf
  acceptance:
  - type: expected_signal
    value: Uses the review score.
""",
            )

            with self.assertRaises(ScenarioQualityError) as raised:
                build_scenario_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        receipt = raised.exception.receipt
        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("registry_dependency_intake_complete", blockers)
        self.assertIn("registry_security_warning_blocks_use", blockers)
        self.assertIn("weak-registry-case:security", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:version_or_pin", blockers["registry_dependency_intake_complete"]["evidence"])
        self.assertIn("weak-registry-case:local_validation", blockers["registry_dependency_intake_complete"]["evidence"])


if __name__ == "__main__":
    unittest.main()
