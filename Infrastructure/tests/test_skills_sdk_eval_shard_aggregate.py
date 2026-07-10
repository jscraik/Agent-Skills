from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_shard_aggregate import EvalShardAggregateError, build_eval_shard_aggregate_receipt  # noqa: E402
from helpers.schema_validator import _validate_schema_subset  # noqa: E402


CASE_IDS = [f"case-{index}" for index in range(1, 9)]
DIGEST_A = "sha256:" + ("a" * 64)
DIGEST_B = "sha256:" + ("b" * 64)
DIGEST_C = "sha256:" + ("c" * 64)


def _write_skill(root: Path) -> Path:
    skill = root / "Skills" / "sample"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: sample\ndescription: sample\n---\n", encoding="utf-8")
    cases = "\n".join(f"- id: {case_id}" for case_id in CASE_IDS)
    selected = "\n".join(f"        - {case_id}" for case_id in CASE_IDS)
    (skill / "references" / "evals.yaml").write_text(
        f"""schema_version: '2.0'
release_scenario_sets:
  - id: sample-release-8-v1
    default: true
    minimum_scenarios: 5
    target_scenarios: 8
    maximum_scenarios: 10
    groups:
      release:
{selected}
cases:
{cases}
""",
        encoding="utf-8",
    )
    return skill


def _write_shards(root: Path, *, profile: str = "oss-local", duplicate: bool = False, mismatch_digest: bool = False, failed: bool = False) -> list[Path]:
    execution_identity = _execution_identity(profile)
    paths: list[Path] = []
    for shard_index in range(4):
        selected = CASE_IDS[shard_index * 2:shard_index * 2 + 2]
        if duplicate and shard_index == 3:
            selected[1] = CASE_IDS[0]
        cases = [
            {"case_id": case_id, "status": "fail" if failed and shard_index == 0 else "pass", "oracle": "eval_closeout", "expected": "pass", "actual": "pass"}
            for case_id in selected
        ]
        payload = {
            "schema_version": "skills-sdk.eval-run-receipt.v0",
            "status": "fail" if failed and shard_index == 0 else "pass",
            "lane": profile,
            "lane_type": "release-shard",
            "profile": profile,
            "codex_profile": profile,
            "codex_exec_invoked": True,
            **execution_identity,
            "execution_identity_source": "codex-profile-config",
            "package_id": "sample",
            "package_digest": DIGEST_A if not mismatch_digest or shard_index != 3 else DIGEST_B,
            "dataset_digest": f"sha256:{shard_index:064x}",
            "rubric_digest": DIGEST_C,
            "scenario_set_id": "sample-release-8-v1",
            "selected_case_ids": selected,
            "cases": cases,
        }
        path = root / "receipts" / f"shard-{shard_index + 1}.json"
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths.append(path.relative_to(root))
    return paths


def _execution_identity(profile: str) -> dict[str, str]:
    if profile == "oss-local":
        return {
            "execution_model": "qwen3.5:9b-mlx",
            "execution_model_family": "qwen",
            "execution_model_provider": "ollama",
        }
    return {
        "execution_model": "minimax-m2.7:cloud",
        "execution_model_family": "minimax",
        "execution_model_provider": "ollama-cloud",
    }


class TestEvalShardAggregate(unittest.TestCase):
    def test_non_object_receipt_is_reported_as_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            path = root / "receipt.json"
            path.write_text("[]", encoding="utf-8")

            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(
                    root,
                    skill_path=skill,
                    scenario_set="sample-release-8-v1",
                    receipt_paths=[path.relative_to(root)],
                )

        evidence = [item for check in raised.exception.receipt["checks"] for item in check["evidence"]]
        self.assertTrue(any("receipt payload must be a JSON object" in item for item in evidence))

    def test_missing_dataset_digest_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            paths = _write_shards(root)
            first = root / paths[0]
            payload = json.loads(first.read_text(encoding="utf-8"))
            payload["dataset_digest"] = ""
            first.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(
                    root,
                    skill_path=skill,
                    scenario_set="sample-release-8-v1",
                    receipt_paths=paths,
                )

        blocker_ids = {check["id"] for check in raised.exception.receipt["blockers"]}
        self.assertIn("dataset_digests_present", blocker_ids)

    def test_exact_four_shard_coverage_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            receipt = build_eval_shard_aggregate_receipt(
                root,
                skill_path=skill,
                scenario_set="sample-release-8-v1",
                receipt_paths=_write_shards(root),
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["shard_count"], 4)
        self.assertEqual(receipt["case_count"], 8)
        self.assertEqual(receipt["scenario_set_case_ids"], CASE_IDS)
        self.assertEqual(len(receipt["shard_dataset_digests"]), 4)
        schema = json.loads((REPO_ROOT / "Infrastructure/config/schemas/skills-sdk/eval-shard-aggregate-receipt.v0.schema.json").read_text(encoding="utf-8"))
        _validate_schema_subset(schema, receipt, {"eval-shard-aggregate-receipt": schema})

    def test_duplicate_case_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(root, skill_path=skill, scenario_set="sample-release-8-v1", receipt_paths=_write_shards(root, duplicate=True))

        self.assertIn("selected_cases_exactly_cover_release_set", {row["id"] for row in raised.exception.receipt["blockers"]})

    def test_cloud_shards_pass_only_for_cloud_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            receipt = build_eval_shard_aggregate_receipt(
                root, skill_path=skill, scenario_set="sample-release-8-v1",
                receipt_paths=_write_shards(root, profile="oss-cloud"), profile="oss-cloud",
            )

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["lane"], "oss-cloud")
        self.assertEqual(receipt["profile"], "oss-cloud")

    def test_identity_mismatch_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(root, skill_path=skill, scenario_set="sample-release-8-v1", receipt_paths=_write_shards(root, mismatch_digest=True))

        self.assertIn("identity_fields_match", {row["id"] for row in raised.exception.receipt["blockers"]})

    def test_stale_shards_are_blocked_against_current_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(
                    root,
                    skill_path=skill,
                    scenario_set="sample-release-8-v1",
                    receipt_paths=_write_shards(root),
                    expected_package_digest=DIGEST_B,
                )

        self.assertIn("shards_match_current_package", {row["id"] for row in raised.exception.receipt["blockers"]})

    def test_failed_shard_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            skill = _write_skill(root)
            with self.assertRaises(EvalShardAggregateError) as raised:
                build_eval_shard_aggregate_receipt(root, skill_path=skill, scenario_set="sample-release-8-v1", receipt_paths=_write_shards(root, failed=True))

        blocker_ids = {row["id"] for row in raised.exception.receipt["blockers"]}
        self.assertIn("shards_pass", blocker_ids)
        self.assertIn("all_case_results_pass", blocker_ids)


if __name__ == "__main__":
    unittest.main()
