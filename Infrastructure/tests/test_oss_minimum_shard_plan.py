from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from build_oss_minimum_shard_plan import build_shard_plan  # noqa: E402


def _write_policy(path: Path, *, shard_size: int = 2, cases: list[str] | None = None) -> None:
    path.write_text(json.dumps(_policy_payload(shard_size=shard_size, cases=cases)), encoding="utf-8")


def _policy_payload(*, shard_size: int, cases: list[str] | None) -> dict[str, object]:
    return {
        "proof_sets": {
            "fixture": {
                "policy": "9-core-plus-3-regression",
                "skill": "Skills/fixture",
                "shard_size_limit": shard_size,
                "timeout_profiles": {"oss-cloud": "cloud-rehearsal-180s"},
                "core_cases": cases or ["case-a", "case-b", "case-c"],
                "regression_cases": ["case-d", "case-e"] if cases is None else [],
            }
        }
    }


def _write_proof(path: Path) -> None:
    path.write_text(json.dumps({"schema_version": "oss-minimum-proof-set/v1", "cases": _proof_cases()}), encoding="utf-8")


def _proof_cases() -> list[dict[str, object]]:
    return [
        {"case_id": "case-a", "latest_evidence": {"status": "pass", "workflow_closeout_validation_status": "pass"}},
        {"case_id": "case-b", "latest_evidence": {"status": "blocked", "workflow_closeout_validation_status": "blocked"}},
    ]


class OssMinimumShardPlanTests(unittest.TestCase):
    def test_policy_shard_limit_generates_max_two_case_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            _write_policy(policy_path)

            plan = build_shard_plan(
                policy_file=policy_path,
                proof_set_id="fixture",
                codex_profile="oss-cloud",
                mode="release",
                timeout_seconds=120,
            )

        self.assertEqual(plan["schema_version"], "oss-minimum-shard-plan/v1")
        self.assertEqual(plan["case_count"], 5)
        self.assertEqual(plan["policy_case_count"], 5)
        self.assertEqual(plan["shard_size_limit"], 2)
        self.assertEqual(plan["timeout_profile"], "cloud-rehearsal-180s")
        self.assertEqual(plan["shard_count"], 3)
        self.assertEqual(plan["cost_projection"]["expected_model_tasks"], 5)
        self.assertEqual([shard["case_count"] for shard in plan["shards"]], [2, 2, 1])
        self.assertEqual(plan["shards"][0]["timeout_profile"], "cloud-rehearsal-180s")
        first_command = plan["shards"][0]["command"]
        self.assertIn("--codex-profile oss-cloud", first_command)
        self.assertIn("--case case-a --case case-b", first_command)
        self.assertNotIn("--case case-c", first_command)

    def test_policy_can_skip_pass_valid_cases_from_existing_proof_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            proof_path = Path(temp_dir) / "proof.json"
            _write_policy(policy_path, cases=["case-a", "case-b", "case-c"])
            _write_proof(proof_path)

            plan = build_shard_plan(
                policy_file=policy_path,
                proof_set_id="fixture",
                codex_profile="oss-local",
                mode="release",
                timeout_seconds=60,
                proof_set_receipt=proof_path,
            )

        self.assertEqual(plan["policy_case_count"], 3)
        self.assertEqual(plan["case_count"], 2)
        self.assertEqual(plan["skipped_pass_case_ids"], ["case-a"])
        self.assertEqual(plan["shards"][0]["case_ids"], ["case-b", "case-c"])


if __name__ == "__main__":
    unittest.main()
