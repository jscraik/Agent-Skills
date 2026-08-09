from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_lane_policy import build_eval_lane_policy_checks  # noqa: E402
from ask.skills_sdk.scenario_quality import _yaml_safe_load  # noqa: E402


RELEASE_IDS = [f"release-{index}" for index in range(8)]
LOCAL_EXTRAS = [f"growth-{index}" for index in range(12)]


def _payload(*, cloud_cases: list[str] | None = None, baseline_fields: list[str] | None = None) -> dict[str, object]:
    cloud = cloud_cases or [*RELEASE_IDS, *LOCAL_EXTRAS[:2]]
    return {
        "release_scenario_sets": [{"id": "release-8-v1", "default": True, "cases": RELEASE_IDS}],
        "evaluation_lane_policy": {
            "schema_version": "skills-sdk.evaluation-lane-policy.v1",
            "release_scenario_set_id": "release-8-v1",
            "baseline_identity_fields": baseline_fields
            or ["case_ids", "criteria_digest", "rubric_digest", "scorer_version", "package_digest", "execution_model_family"],
            "model_routing": {
                "oss-local": {"model": "qwen", "model_family": "qwen", "provider": "ollama", "identity_source": "profile-config"},
                "oss-cloud": {"model": "deepseek-v4-flash:0731-cloud", "model_family": "deepseek", "provider": "ollama-cloud", "identity_source": "profile-config"},
                "tessl-external": {"model": "deepseek", "model_family": "deepseek", "provider": "tessl", "identity_source": "operator-confirmed"},
            },
            "pools": {
                "oss-local-development": {"target_scenarios": 20, "cases": [*RELEASE_IDS, *LOCAL_EXTRAS]},
                "oss-cloud-challenge": {"target_scenarios": 10, "rotating_case_count": 2, "cases": cloud},
            },
        },
    }


def _cases() -> list[dict[str, str]]:
    return [{"id": case_id} for case_id in [*RELEASE_IDS, *LOCAL_EXTRAS]]


class EvalLanePolicyTests(unittest.TestCase):
    def test_technical_writer_policy_passes(self) -> None:
        evals_path = REPO_ROOT / "Skills" / "agent-ops" / "technical-writer" / "references" / "evals.yaml"
        payload = _yaml_safe_load(evals_path.read_text(encoding="utf-8"))
        checks = build_eval_lane_policy_checks(payload, payload["cases"])

        self.assertTrue(checks)
        self.assertEqual([row for row in checks if row["status"] == "blocker"], [])

    def test_valid_policy_passes(self) -> None:
        checks = build_eval_lane_policy_checks(_payload(), _cases())

        self.assertTrue(checks)
        self.assertEqual({row["status"] for row in checks}, {"pass"})

    def test_cloud_pool_must_be_release_eight_plus_two_local_growth_cases(self) -> None:
        checks = build_eval_lane_policy_checks(
            _payload(cloud_cases=[*RELEASE_IDS[:-1], *LOCAL_EXTRAS[:3]]),
            _cases(),
        )
        blockers = {row["id"] for row in checks if row["status"] == "blocker"}

        self.assertIn("eval_lane_cloud_challenge_contains_release_set", blockers)
        self.assertIn("eval_lane_cloud_rotating_count", blockers)

    def test_baseline_identity_fields_are_mandatory(self) -> None:
        checks = build_eval_lane_policy_checks(
            _payload(baseline_fields=["case_ids", "rubric_digest"]),
            _cases(),
        )

        blocker = next(row for row in checks if row["id"] == "eval_lane_baseline_identity_fields")
        self.assertEqual(blocker["status"], "blocker")
        self.assertIn("criteria_digest", blocker["evidence"])

    def test_oss_model_families_must_be_distinct(self) -> None:
        payload = _payload()
        payload["evaluation_lane_policy"]["model_routing"]["oss-cloud"]["model_family"] = "qwen"

        checks = build_eval_lane_policy_checks(payload, _cases())

        blocker = next(row for row in checks if row["id"] == "eval_lane_oss_model_families_distinct")
        self.assertEqual(blocker["status"], "blocker")

    def test_oss_model_family_comparison_is_case_insensitive(self) -> None:
        payload = _payload()
        payload["evaluation_lane_policy"]["model_routing"]["oss-cloud"]["model_family"] = "QWEN"

        checks = build_eval_lane_policy_checks(payload, _cases())

        blocker = next(row for row in checks if row["id"] == "eval_lane_oss_model_families_distinct")
        self.assertEqual(blocker["status"], "blocker")

    def test_tessl_may_share_the_cloud_model_family_when_provider_is_external(self) -> None:
        checks = build_eval_lane_policy_checks(_payload(), _cases())

        external = next(row for row in checks if row["id"] == "eval_lane_tessl_external_provider_distinct")
        self.assertEqual(external["status"], "pass")

    def test_tessl_provider_must_not_reuse_an_oss_execution_provider(self) -> None:
        payload = _payload()
        payload["evaluation_lane_policy"]["model_routing"]["tessl-external"]["provider"] = "ollama-cloud"

        checks = build_eval_lane_policy_checks(payload, _cases())

        external = next(row for row in checks if row["id"] == "eval_lane_tessl_external_provider_distinct")
        self.assertEqual(external["status"], "blocker")


if __name__ == "__main__":
    unittest.main()
