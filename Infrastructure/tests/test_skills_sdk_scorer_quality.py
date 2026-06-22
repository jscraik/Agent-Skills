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

from ask.skills_sdk.scorer_quality import (  # noqa: E402
    _fallback_scorer_metadata_contract_errors,
    build_scorer_quality_receipt,
)
from ask.skills_sdk.scorer_quality_contracts import validate_scorer_quality_receipt  # noqa: E402


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
UNKNOWN_FIELD_SCORER_YAML = """schema_version: '2.0'
skill_name: sample
scorer_quality:
  schema_version: skills-sdk.scorer-quality.v1
  scorer_id: strict.release-scorer
  scorer_type: deterministic
  scope: suite
  scorer_version_or_digest: strict-local
  pass_threshold: 0.8
  deterministic_checks_first: true
  unexpected_field: should-block
  segmentation_fields: [category, claim_ids, eval_modes]
  calibration_cases:
  - {id: obvious-correct, probe_type: obvious_correct, expected_score: 1}
  - {id: obvious-wrong, probe_type: obvious_wrong, expected_score: 0}
  - {id: short-correct-vs-verbose-wrong, probe_type: short_correct_vs_verbose_wrong, expected_direction: short_correct_wins}
  - {id: copied-rubric-text-rejected, probe_type: rubric_copying_rejected, expected_score: 0}
  - {id: skill-name-mention-not-enough, probe_type: skill_name_mention_not_enough, expected_score: 0}
  - {id: evidence-lane-overclaim-rejected, probe_type: evidence_lane_overclaim_rejected, expected_score: 0}
cases: []
"""
TYPE_COERCION_SCORER_YAML = UNKNOWN_FIELD_SCORER_YAML.replace(
    "  unexpected_field: should-block\n  segmentation_fields:",
    '  segmentation_fields:',
).replace("  pass_threshold: 0.8", '  pass_threshold: "0.8"')


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

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
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

    def test_metadata_contract_blocks_unknown_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), UNKNOWN_FIELD_SCORER_YAML)

            receipt = build_scorer_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scorer_quality_contract_valid", blockers)
        self.assertTrue(any("unexpected_field" in item for item in blockers["scorer_quality_contract_valid"]["evidence"]))

    def test_metadata_contract_blocks_type_coercion(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), TYPE_COERCION_SCORER_YAML)

            receipt = build_scorer_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertIn("scorer_quality_contract_valid", blockers)
        self.assertTrue(any("pass_threshold" in item for item in blockers["scorer_quality_contract_valid"]["evidence"]))

    def test_malformed_evals_yaml_returns_blocked_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill_with_evals(Path(temp_dir), "scorer_quality:\n  - [\n")

            receipt = build_scorer_quality_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blockers = {check["id"]: check for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("evals_yaml_parse", blockers)
        self.assertTrue(blockers["evals_yaml_parse"]["evidence"])

    def test_builder_receipt_loads_through_pydantic_contract(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-quality", FIXTURE_SKILL, "--preview", "--json", "--robot")
        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)

        model = validate_scorer_quality_receipt(envelope["data"]["skills_sdk_eval_scorer_quality"]["receipt"])

        self.assertTrue(model.ready)
        self.assertEqual(model.operation, "scorer_quality_preview")

    def test_typed_contract_rejects_non_blocker_entries_in_blockers(self) -> None:
        receipt = build_scorer_quality_receipt(REPO_ROOT, source_path=REPO_ROOT / FIXTURE_SKILL, query=FIXTURE_SKILL)
        receipt["status"] = "blocked"
        receipt["ready"] = False
        receipt["blockers"] = [
            {
                "id": "not_a_blocker",
                "status": "pass",
                "severity": "blocker",
                "message": "This entry should not be accepted as a blocker.",
                "evidence": ["status:pass"],
            }
        ]

        with self.assertRaises(ValueError):
            validate_scorer_quality_receipt(receipt)

    def test_typed_contract_rejects_empty_check_evidence(self) -> None:
        receipt = build_scorer_quality_receipt(REPO_ROOT, source_path=REPO_ROOT / FIXTURE_SKILL, query=FIXTURE_SKILL)
        receipt["quality_checks"][0]["evidence"] = [""]

        with self.assertRaises(ValueError):
            validate_scorer_quality_receipt(receipt)

    def test_fallback_metadata_contract_checks_judge_parameter_types(self) -> None:
        errors = _fallback_scorer_metadata_contract_errors(
            {
                "schema_version": "skills-sdk.scorer-quality.v1",
                "scorer_id": "strict.release-scorer",
                "scorer_type": "llm_judge",
                "scope": "suite",
                "scorer_version_or_digest": "strict-local",
                "pass_threshold": 0.8,
                "deterministic_checks_first": True,
                "parameters": {"model": "local-test", "temperature": "cold", "trial_count": 0},
                "rationale_audit": {"required": "yes", "sampled_count": -1},
                "bias_probes": ["short_correct_vs_verbose_wrong"],
                "segmentation_fields": ["category", "claim_ids", "eval_modes"],
                "calibration_cases": [
                    {"id": "obvious-correct", "probe_type": "obvious_correct", "expected_score": 1},
                    {"id": "obvious-wrong", "probe_type": "obvious_wrong", "expected_score": 0},
                    {
                        "id": "short-correct-vs-verbose-wrong",
                        "probe_type": "short_correct_vs_verbose_wrong",
                        "expected_direction": "short_correct_wins",
                    },
                    {"id": "copied-rubric-text-rejected", "probe_type": "rubric_copying_rejected", "expected_score": 0},
                    {"id": "skill-name-mention-not-enough", "probe_type": "skill_name_mention_not_enough", "expected_score": 0},
                    {
                        "id": "evidence-lane-overclaim-rejected",
                        "probe_type": "evidence_lane_overclaim_rejected",
                        "expected_score": 0,
                    },
                ],
            }
        )

        self.assertIn("parameters.temperature:float_type", errors)
        self.assertIn("parameters.trial_count:greater_than_equal", errors)
        self.assertIn("rationale_audit.required:bool_type", errors)
        self.assertIn("rationale_audit.sampled_count:greater_than_equal", errors)

    def test_command_uses_fallback_parser_without_pyyaml(self) -> None:
        script = f"""
import importlib.abc
import json
import sys
from pathlib import Path

class BlockYaml(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "yaml" or fullname.startswith("yaml."):
            raise ModuleNotFoundError("No module named 'yaml'")
        return None

repo_root = Path({str(REPO_ROOT)!r})
sys.path.insert(0, str(repo_root / "Infrastructure" / "scripts" / "lib"))
sys.meta_path.insert(0, BlockYaml())
from ask.skills_sdk.scorer_quality import build_scorer_quality_receipt

receipt = build_scorer_quality_receipt(
    repo_root,
    source_path=repo_root / {FIXTURE_SKILL!r},
    query={FIXTURE_SKILL!r},
)
print(json.dumps({{"status": receipt["status"], "ready": receipt["ready"]}}))
"""
        process = subprocess.run(
            [sys.executable, "-c", script],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready"])


if __name__ == "__main__":
    unittest.main()
