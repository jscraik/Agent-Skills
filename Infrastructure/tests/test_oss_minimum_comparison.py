from __future__ import annotations

import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
import json


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from build_oss_minimum_comparison import _parse_stage_maturity_expectations, build_comparison  # noqa: E402


def _proof_set(profile: str, statuses: dict[str, str], *, gate_status: str = "pass") -> dict[str, object]:
    return {
        "schema_version": "oss-minimum-proof-set/v1",
        "gate_status": gate_status,
        "skill": "Skills/agent-ops/improve-agent-native",
        "codex_profile": profile,
        "policy": "15-core-plus-5-regression",
        "shard_size_limit": 2,
        "cases": [
            {
                "case_id": case_id,
                "bucket": "core",
                "required": True,
                "latest_evidence": {
                    "status": status,
                    "scorecard_path": f"artifacts/{profile}/{case_id}/scorecard.json",
                },
            }
            for case_id, status in statuses.items()
        ],
    }


class OssMinimumComparisonTests(unittest.TestCase):
    def test_missing_cloud_evidence_blocks_comparison_before_oss_cloud_run(self) -> None:
        local = _proof_set("oss-local", {"case-a": "pass", "case-b": "pass"})

        receipt = build_comparison(local_proof_set=local, cloud_proof_set=None, delta_owners={})

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["summary"]["case_count"], 2)
        self.assertEqual(receipt["summary"]["missing_cloud_count"], 2)
        self.assertEqual(receipt["summary"]["missing_delta_owner_count"], 0)
        self.assertEqual(receipt["comparisons"][0]["owner_if_delta"], "missing_cloud_evidence")
        self.assertEqual(receipt["shard_size_limit"], 2)
        self.assertIn("oss-cloud-eval-run", receipt["blocked_next_gates"])
        self.assertIn("repair loop", receipt["stage_maturity_expectations"]["oss-local"])
        self.assertIn("uplift loop", receipt["stage_maturity_expectations"]["oss-cloud"])
        self.assertIn("confirmation loop", receipt["stage_maturity_expectations"]["tessl"])

    def test_matching_cloud_evidence_passes_comparison(self) -> None:
        local = _proof_set("oss-local", {"case-a": "pass", "case-b": "pass"})
        cloud = deepcopy(local)
        cloud["codex_profile"] = "oss-cloud"

        receipt = build_comparison(local_proof_set=local, cloud_proof_set=cloud, delta_owners={})

        self.assertEqual(receipt["status"], "pass")
        self.assertEqual(receipt["input_gate_status"], "pass")
        self.assertEqual(receipt["lane_scores"]["oss-local"]["schema_version"], "oss-lane-score/v1")
        self.assertEqual(receipt["lane_scores"]["oss-local"]["pass_rate"], 1.0)
        self.assertEqual(receipt["lane_scores"]["oss-cloud"]["pass_count"], 2)
        self.assertEqual(receipt["summary"]["parity_count"], 2)
        self.assertEqual(receipt["summary"]["delta_count"], 0)
        self.assertEqual(receipt["summary"]["missing_delta_owner_count"], 0)
        self.assertEqual({item["owner_if_delta"] for item in receipt["comparisons"]}, {"none"})
        self.assertNotIn("oss-cloud-eval-run", receipt["blocked_next_gates"])
        self.assertIn("tessl-dry-run", receipt["blocked_next_gates"])
        self.assertIn("tessl-live", receipt["blocked_next_gates"])

    def test_matching_blocked_inputs_do_not_pass_comparison_by_parity_only(self) -> None:
        local = _proof_set("oss-local", {"case-a": "blocked"}, gate_status="blocked")
        cloud = _proof_set("oss-cloud", {"case-a": "blocked"}, gate_status="blocked")

        receipt = build_comparison(local_proof_set=local, cloud_proof_set=cloud, delta_owners={})

        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["input_gate_status"], "blocked")
        self.assertEqual(receipt["summary"]["delta_count"], 0)
        self.assertEqual(receipt["input_gate_evidence"], {
            "oss_local_gate_status": "blocked",
            "oss_cloud_gate_status": "blocked",
        })
        self.assertIn("oss-cloud-eval-run", receipt["blocked_next_gates"])

    def test_non_parity_requires_owner_classification(self) -> None:
        local = _proof_set("oss-local", {"case-a": "pass"})
        cloud = _proof_set("oss-cloud", {"case-a": "fail"})

        receipt = build_comparison(local_proof_set=local, cloud_proof_set=cloud, delta_owners={})
        self.assertEqual(receipt["status"], "blocked")
        self.assertEqual(receipt["summary"]["missing_delta_owner_count"], 1)
        self.assertEqual(receipt["comparisons"][0]["owner_if_delta"], "unclassified_delta")

        classified = build_comparison(
            local_proof_set=local,
            cloud_proof_set=cloud,
            delta_owners={"case-a": "rubric"},
        )
        self.assertEqual(classified["status"], "blocked")
        self.assertEqual(classified["summary"]["missing_delta_owner_count"], 0)
        self.assertEqual(classified["comparisons"][0]["owner_if_delta"], "rubric")

    def test_policy_file_supplies_stage_maturity_expectations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "proof_sets": {
                            "fixture": {
                                "stage_maturity_expectations": {
                                    "oss-local": "local repair",
                                    "oss-cloud": "cloud uplift to near production",
                                    "tessl": "external confirmation",
                                }
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )

            expectations = _parse_stage_maturity_expectations(policy_path, "fixture")

        self.assertEqual(expectations["oss-local"], "local repair")
        self.assertEqual(expectations["oss-cloud"], "cloud uplift to near production")
        self.assertEqual(expectations["tessl"], "external confirmation")


if __name__ == "__main__":
    unittest.main()
