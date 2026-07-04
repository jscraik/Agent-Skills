from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from build_oss_minimum_shard_plan import build_shard_plan  # noqa: E402


class OssMinimumShardPlanTests(unittest.TestCase):
    def test_policy_shard_limit_generates_max_two_case_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "proof_sets": {
                            "fixture": {
                                "policy": "15-core-plus-5-regression",
                                "skill": "Skills/fixture",
                                "shard_size_limit": 2,
                                "core_cases": ["case-a", "case-b", "case-c"],
                                "regression_cases": ["case-d", "case-e"],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            plan = build_shard_plan(
                policy_file=policy_path,
                proof_set_id="fixture",
                codex_profile="oss-cloud",
                mode="release",
                timeout_seconds=120,
            )

        self.assertEqual(plan["schema_version"], "oss-minimum-shard-plan/v1")
        self.assertEqual(plan["case_count"], 5)
        self.assertEqual(plan["shard_size_limit"], 2)
        self.assertEqual(plan["shard_count"], 3)
        self.assertEqual([shard["case_count"] for shard in plan["shards"]], [2, 2, 1])
        first_command = plan["shards"][0]["command"]
        self.assertIn("--codex-profile oss-cloud", first_command)
        self.assertIn("--case case-a --case case-b", first_command)
        self.assertNotIn("--case case-c", first_command)


if __name__ == "__main__":
    unittest.main()
