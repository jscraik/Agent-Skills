from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.scorer_quality import build_scorer_quality_receipt  # noqa: E402


FIXTURE_SKILL = "Skills/agent-ops/sdk-scenario-generator"
NO_SCORER_FIXTURE = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"
LLM_WEAK_SCORER_YAML = """schema_version: '2.0'
skill_name: sample
scorer_quality:
  scorer_id: weak.release-scorer
  scorer_type: hybrid
  scope: suite
  scorer_version_or_digest: weak-local
  pass_threshold: 0.8
  deterministic_checks_first: true
  rationale_audit:
    required: false
    sampled_count: 1
  bias_probes:
  - short_correct_vs_verbose_wrong
  segmentation_fields:
  - category
  - claim_ids
  - eval_modes
  calibration_cases:
  - id: obvious-correct
    probe_type: obvious_correct
    expected_score: 1
  - id: obvious-wrong
    probe_type: obvious_wrong
    expected_score: 0
  - id: short-correct-vs-verbose-wrong
    probe_type: short_correct_vs_verbose_wrong
    expected_direction: short_correct_wins
  - id: copied-rubric-text-rejected
    probe_type: rubric_copying_rejected
    expected_score: 0
  - id: skill-name-mention-not-enough
    probe_type: skill_name_mention_not_enough
    expected_score: 0
  - id: evidence-lane-overclaim-rejected
    probe_type: evidence_lane_overclaim_rejected
    expected_score: 0
cases: []
"""


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


def _write_skill_with_evals(root: Path, evals_text: str) -> Path:
    skill_dir = root / "sample_skill"
    references_dir = skill_dir / "references"
    references_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: sample\n---\n# Sample\n", encoding="utf-8")
    (references_dir / "evals.yaml").write_text(evals_text, encoding="utf-8")
    return skill_dir


class TestSkillsSdkScorerQuality(unittest.TestCase):
    def test_scorer_quality_command_builds_preview(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-quality", FIXTURE_SKILL, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scorer_quality"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["blocked_count"], 0)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_scorer_quality_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-quality", FIXTURE_SKILL, "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_missing_scorer_metadata_is_advisory_blocked_receipt(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-quality", NO_SCORER_FIXTURE, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scorer_quality"]
        blocker_ids = {check["id"] for check in payload["receipt"]["blockers"]}

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["ready"])
        self.assertIn("scorer_quality_declared", blocker_ids)

    def test_builder_blocks_missing_calibration_probes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(
                Path(temp_dir),
                """schema_version: '2.0'
skill_name: sample
scorer_quality:
  scorer_id: weak.release-scorer
  scorer_type: deterministic
  scope: suite
  scorer_version_or_digest: weak-local
  pass_threshold: 0.8
  deterministic_checks_first: true
  calibration_cases:
  - id: obvious-correct
    probe_type: obvious_correct
    expected_score: 1
  segmentation_fields:
  - category
  - claim_ids
  - eval_modes
cases: []
""",
            )

            receipt = build_scorer_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("calibration_probe_coverage", blocker_ids)
        self.assertIn("verbosity_bias_probe_present", blocker_ids)

    def test_llm_like_scorers_require_parameters_and_rationale_audit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), LLM_WEAK_SCORER_YAML)

            receipt = build_scorer_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("judge_parameters_versioned", blocker_ids)
        self.assertIn("rationale_audit_required", blocker_ids)
        self.assertIn("rationale_audit_sampled", blocker_ids)


if __name__ == "__main__":
    unittest.main()
