from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.scorer_calibration import build_scorer_calibration_receipt  # noqa: E402


FIXTURE_SKILL = "Skills/agent-ops/sdk-scenario-generator"
NO_CALIBRATION_FIXTURE = "Infrastructure/tests/fixtures/skills_sdk/scenario_quality_skill"


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


def _write_skill(root: Path) -> Path:
    skill_dir = root / "sample_skill"
    (skill_dir / "references" / "scorer-calibration" / "raw").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: sample\n---\n# Sample\n", encoding="utf-8")
    return skill_dir


def _write_bundle(
    skill_dir: Path,
    rows: list[dict[str, Any]],
    *,
    manifest_overrides: dict[str, Any] | None = None,
    write_raw: bool = True,
) -> None:
    bundle_dir = skill_dir / "references" / "scorer-calibration"
    raw_dir = bundle_dir / "raw"
    manifest = _default_manifest()
    if manifest_overrides:
        manifest.update(manifest_overrides)
    _write_manifest(bundle_dir, manifest)
    _write_examples(bundle_dir, rows)
    if write_raw:
        _write_raw_artifacts(bundle_dir, manifest, rows)
    raw_dir.mkdir(exist_ok=True)


def _default_manifest() -> dict[str, Any]:
    return {
        "schema_version": "skills-sdk.scorer-calibration-bundle.v1",
        "scorer_id": "sample.release-scorer",
        "scorer_version_or_digest": "sample-local",
        "prompt_version": "sample-release-scorer.v1",
        "threshold": 0.9,
        "split": "held_out",
        "parameters": {"model": "local-test", "temperature": 0, "trial_count": 1},
        "examples_path": "examples.jsonl",
        "raw_artifacts_dir": "raw",
        "minimum_examples": 1,
        "minimum_true_positives": 0,
        "minimum_true_negatives": 0,
        "max_false_positives": 0,
        "max_false_negatives": 0,
    }


def _write_manifest(bundle_dir: Path, manifest: dict[str, Any]) -> None:
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _write_examples(bundle_dir: Path, rows: list[dict[str, Any]]) -> None:
    (bundle_dir / "examples.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )


def _write_raw_artifacts(bundle_dir: Path, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    for row in rows:
        raw_path = bundle_dir / str(row["raw_artifact"])
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_text(json.dumps(_raw_artifact_payload(manifest, row), indent=2), encoding="utf-8")


def _raw_artifact_payload(manifest: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "scorer_id": manifest["scorer_id"],
        "predicted_label": row["predicted_label"],
        "score": row["score"],
        "rationale": "test artifact",
    }


class TestSkillsSdkScorerCalibration(unittest.TestCase):
    def test_scorer_calibration_command_builds_preview(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-calibration", FIXTURE_SKILL, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scorer_calibration"]
        receipt = payload["receipt"]

        self.assertEqual(payload["status"], "preview")
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["blocked_count"], 0)
        self.assertEqual(receipt["confusion_matrix"], {"tp": 3, "tn": 3, "fp": 0, "fn": 0})
        self.assertEqual(receipt["metrics"]["tpr"], 1.0)
        self.assertEqual(receipt["metrics"]["tnr"], 1.0)
        self.assertFalse(receipt["mutation_performed"])
        self.assertFalse(receipt["promotion_performed"])

    def test_scorer_calibration_requires_preview_flag(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-calibration", FIXTURE_SKILL, "--json", "--robot")

        self.assertNotEqual(process.returncode, 0)
        envelope = json.loads(process.stdout)
        self.assertEqual(envelope["status"], "error")
        self.assertIn("requires --preview", envelope["errors"][0]["message"])

    def test_missing_calibration_bundle_is_advisory_blocked_receipt(self) -> None:
        process = _run_ask("sdk", "eval", "scorer-calibration", NO_CALIBRATION_FIXTURE, "--preview", "--json", "--robot")

        self.assertEqual(process.returncode, 0, process.stderr)
        envelope = json.loads(process.stdout)
        payload = envelope["data"]["skills_sdk_eval_scorer_calibration"]
        blocker_ids = {check["id"] for check in payload["receipt"]["blockers"]}

        self.assertEqual(payload["status"], "blocked")
        self.assertFalse(payload["ready"])
        self.assertIn("calibration_bundle_present", blocker_ids)

    def test_builder_blocks_false_positive(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill(Path(temp_dir))
            _write_bundle(
                skill_dir,
                [
                    {
                        "id": "known-fail-overclaim",
                        "probe_type": "evidence_lane_overclaim_rejected",
                        "expected_label": "fail",
                        "predicted_label": "pass",
                        "score": 0.95,
                        "raw_artifact": "raw/known-fail-overclaim.json",
                    }
                ],
            )

            receipt = build_scorer_calibration_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["confusion_matrix"]["fp"], 1)
        self.assertIn("false_positive_limit", blocker_ids)

    def test_builder_blocks_missing_raw_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill(Path(temp_dir))
            _write_bundle(
                skill_dir,
                [
                    {
                        "id": "known-pass",
                        "probe_type": "obvious_correct",
                        "expected_label": "pass",
                        "predicted_label": "pass",
                        "score": 0.95,
                        "raw_artifact": "raw/missing.json",
                    }
                ],
                write_raw=False,
            )

            receipt = build_scorer_calibration_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("raw_artifacts_present", blocker_ids)

    def test_builder_blocks_threshold_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = _write_skill(Path(temp_dir))
            _write_bundle(
                skill_dir,
                [
                    {
                        "id": "low-score-pass",
                        "probe_type": "obvious_correct",
                        "expected_label": "pass",
                        "predicted_label": "pass",
                        "score": 0.5,
                        "raw_artifact": "raw/low-score-pass.json",
                    }
                ],
            )

            receipt = build_scorer_calibration_receipt(Path(temp_dir), source_path=skill_dir, query="sample_skill")

        blocker_ids = {check["id"] for check in receipt["blockers"]}
        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("score_threshold_consistent", blocker_ids)


if __name__ == "__main__":
    unittest.main()
