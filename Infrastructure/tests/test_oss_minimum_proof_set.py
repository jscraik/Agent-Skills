from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "validation-and-linting"))

from build_oss_minimum_proof_set import _load_policy_cases, _parse_args, build_proof_set, collect_case_evidence, default_blocked_next_gates  # noqa: E402


def _write_run(
    root: Path,
    run_id: str,
    cases: list[dict[str, object]],
    *,
    closeout_status: str = "fail",
    closeout_validation_status: str = "pass",
) -> None:
    run_dir = root / run_id
    run_dir.mkdir(parents=True)
    scorecard_cases = [_scorecard_case(run_dir, index, case) for index, case in enumerate(cases, start=1)]
    closeout_cases = [_closeout_case(run_dir, index, case) for index, case in enumerate(cases, start=1)]
    _write_scorecard(run_dir, run_id, closeout_status, scorecard_cases)
    _write_closeout(run_dir, closeout_status, closeout_validation_status, closeout_cases)


def _scorecard_case(run_dir: Path, index: int, case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["id"])
    status = str(case["status"])
    return {
        "id": case_id,
        "passed": status == "pass",
        "blocked": status == "blocked",
        "dir": str(run_dir / f"{index:02d}-{case_id}"),
        "tier1_failures": [] if status == "pass" else ["expected signal missing"],
        "runners": {"codex": {"exit_code": 0, "metrics": _trace_metrics(case)}},
    }


def _trace_metrics(case: dict[str, object]) -> dict[str, object]:
    return {"trace": {"token_usage": {"total_tokens": case.get("tokens", 1234)}}}


def _closeout_case(run_dir: Path, index: int, case: dict[str, object]) -> dict[str, object]:
    case_id = str(case["id"])
    return {"id": case_id, "status": str(case["status"]), "result_path": str(run_dir / f"{index:02d}-{case_id}")}


def _write_scorecard(run_dir: Path, run_id: str, closeout_status: str, cases: list[dict[str, object]]) -> None:
    (run_dir / "scorecard.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "decision": closeout_status,
                "cases": cases,
            }
        ),
        encoding="utf-8",
    )


def _write_closeout(
    run_dir: Path,
    closeout_status: str,
    closeout_validation_status: str,
    cases: list[dict[str, object]],
) -> None:
    (run_dir / "workflow-closeout.json").write_text(
        json.dumps(
            {
                "status": closeout_status,
                "closeout_validation": {"status": closeout_validation_status},
                "cases": cases,
            }
        ),
        encoding="utf-8",
    )


def _write_mixed_suite_run(artifacts: Path) -> None:
    _write_run(
        artifacts,
        "20260704-000001",
        [
            {"id": "core-one", "status": "pass", "tokens": 111},
            {"id": "core-two", "status": "pass", "tokens": 222},
            {"id": "unselected-failing-case", "status": "fail"},
        ],
        closeout_status="fail",
    )


class OssMinimumProofSetTests(unittest.TestCase):
    def test_selected_cases_can_pass_inside_mixed_failed_suite(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            _write_mixed_suite_run(artifacts)

            receipt = build_proof_set(
                skill="Skills/agent-ops/improve-agent-native",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=["core-two"],
                codex_profile="oss-local",
                model="qwen3.5:9b-mlx",
                policy="15-core-plus-5-regression",
                blocked_next_gates=["oss-cloud"],
                shard_size_limit=2,
            )

        self.assertEqual(receipt["gate_status"], "pass")
        self.assertEqual(receipt["summary"], {
            "case_count": 2,
            "pass_count": 2,
            "blocked_count": 0,
            "fail_count": 0,
            "missing_count": 0,
        })
        first = receipt["cases"][0]["latest_evidence"]
        self.assertEqual(first["workflow_closeout_status"], "fail")
        self.assertEqual(first["workflow_closeout_validation_status"], "pass")
        self.assertIs(first["codex_exec_invoked"], True)
        self.assertEqual(first["trace_total_tokens"], 111)
        self.assertEqual(receipt["shard_size_limit"], 2)
        self.assertEqual(receipt["cache_contract"]["schema_version"], "skills-sdk.eval-cache-index.v1")
        self.assertEqual(len(receipt["cache_contract"]["criteria_hash"]), 64)
        self.assertEqual(len(receipt["cache_contract"]["runner_hash"]), 64)
        self.assertEqual(receipt["cases"][0]["cache_key"]["case_id"], "core-one")

    def test_prompt_bytes_are_recorded_for_case_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            _write_run(artifacts, "20260704-000021", [{"id": "core-one", "status": "pass"}], closeout_status="pass")
            prompt_path = artifacts / "20260704-000021" / "01-core-one" / "prompt.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text("short prompt", encoding="utf-8")

            receipt = build_proof_set(
                skill="Skills/agent-ops/improve-agent-native",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=[],
                codex_profile="oss-local",
                model="qwen3.5:9b-mlx",
                policy="9-core-plus-3-regression",
                blocked_next_gates=["oss-cloud"],
            )

        evidence = receipt["cases"][0]["latest_evidence"]
        self.assertEqual(evidence["prompt_path"], str(prompt_path))
        self.assertEqual(evidence["prompt_bytes"], len("short prompt"))

    def test_missing_selected_case_blocks_proof_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            _write_run(artifacts, "20260704-000002", [{"id": "core-one", "status": "pass"}])

            receipt = build_proof_set(
                skill="Skills/agent-ops/improve-agent-native",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=["missing-regression"],
                codex_profile="oss-cloud",
                model=None,
                policy="15-core-plus-5-regression",
                blocked_next_gates=["tessl-dry-run"],
            )

        self.assertEqual(receipt["gate_status"], "blocked")
        self.assertEqual(receipt["summary"]["missing_count"], 1)
        missing = receipt["cases"][1]["latest_evidence"]
        self.assertEqual(missing["status"], "missing")
        self.assertEqual(missing["blocker_class"], "missing_case_evidence")

    def test_pass_case_blocks_when_closeout_validation_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            _write_run(
                artifacts,
                "20260704-000020",
                [{"id": "core-one", "status": "pass"}],
                closeout_status="pass",
                closeout_validation_status="fail",
            )

            receipt = build_proof_set(
                skill="Skills/agent-ops/improve-agent-native",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=[],
                codex_profile="oss-cloud",
                model=None,
                policy="15-core-plus-5-regression",
                blocked_next_gates=["tessl-dry-run"],
            )

        self.assertEqual(receipt["gate_status"], "blocked")
        self.assertEqual(receipt["summary"]["blocked_count"], 1)
        evidence = receipt["cases"][0]["latest_evidence"]
        self.assertEqual(evidence["status"], "blocked")
        self.assertEqual(evidence["workflow_closeout_validation_status"], "fail")

    def test_blocked_next_gate_overrides_do_not_duplicate_defaults(self) -> None:
        with mock.patch(
            "sys.argv",
            [
                "build_oss_minimum_proof_set.py",
                "Skills/example",
                "--artifacts-root",
                "/tmp/example",
                "--blocked-next-gate",
                "oss-cloud",
            ],
        ):
            args = _parse_args()

        self.assertEqual(args.blocked_next_gate, ["oss-cloud"])

    def test_default_blocked_next_gates_are_profile_aware(self) -> None:
        self.assertIn("oss-cloud", default_blocked_next_gates("oss-local"))
        self.assertNotIn("oss-cloud", default_blocked_next_gates("oss-cloud"))
        self.assertIn("tessl-dry-run", default_blocked_next_gates("oss-cloud"))
        self.assertIn("tessl-live", default_blocked_next_gates("oss-cloud"))

    def test_proof_set_notes_are_profile_aware(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            _write_run(artifacts, "20260704-000003", [{"id": "core-one", "status": "pass"}])

            local_receipt = build_proof_set(
                skill="Skills/fixture",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=[],
                codex_profile="oss-local",
                model="qwen3.5:9b-mlx",
                policy="15-core-plus-5-regression",
                blocked_next_gates=["oss-cloud"],
            )
            cloud_receipt = build_proof_set(
                skill="Skills/fixture",
                artifacts_root=artifacts,
                core_cases=["core-one"],
                regression_cases=[],
                codex_profile="oss-cloud",
                model="oss-cloud",
                policy="15-core-plus-5-regression",
                blocked_next_gates=["tessl-dry-run"],
            )

        self.assertTrue(any("oss-cloud" in note for note in local_receipt["notes"]))
        self.assertFalse(any("does not prove the full release lane, oss-cloud" in note for note in cloud_receipt["notes"]))
        self.assertTrue(any("Tessl dry-run" in note for note in cloud_receipt["notes"]))

    def test_policy_file_supplies_selected_case_set(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            policy_path = Path(temp_dir) / "policy.json"
            policy_path.write_text(
                json.dumps(
                    {
                        "schema_version": "skills-sdk.oss-minimum-proof-sets.v1",
                "proof_sets": {
                    "fixture": {
                        "skill": "Skills/fixture",
                        "shard_size_limit": 2,
                        "policy": "custom-2-case-policy",
                        "core_cases": ["core-one"],
                        "regression_cases": ["regression-one"],
                    }
                        },
                    }
                ),
                encoding="utf-8",
            )

            skill, policy, core_cases, regression_cases, shard_size_limit = _load_policy_cases(policy_path, "fixture")

        self.assertEqual(skill, "Skills/fixture")
        self.assertEqual(policy, "custom-2-case-policy")
        self.assertEqual(core_cases, ["core-one"])
        self.assertEqual(regression_cases, ["regression-one"])
        self.assertEqual(shard_size_limit, 2)

    def test_improve_agent_native_policy_has_local_and_cloud_case_counts(self) -> None:
        policy_path = REPO_ROOT / "Infrastructure/config/skills-sdk/oss-minimum-proof-sets.v1.json"

        local_skill, local_policy, local_core, local_regression, local_shard_size = _load_policy_cases(
            policy_path,
            "improve-agent-native-oss-local-9-plus-3",
        )
        cloud_skill, cloud_policy, cloud_core, cloud_regression, cloud_shard_size = _load_policy_cases(
            policy_path,
            "improve-agent-native-15-plus-5",
        )

        self.assertEqual(local_skill, "Skills/agent-ops/improve-agent-native")
        self.assertEqual(local_policy, "9-core-plus-3-regression")
        self.assertEqual(len(local_core), 9)
        self.assertEqual(len(local_regression), 3)
        self.assertEqual(local_shard_size, 2)
        self.assertEqual(cloud_skill, "Skills/agent-ops/improve-agent-native")
        self.assertEqual(cloud_policy, "15-core-plus-5-regression")
        self.assertEqual(len(cloud_core), 15)
        self.assertEqual(len(cloud_regression), 5)
        self.assertEqual(cloud_shard_size, 2)

    def test_missing_result_path_stays_null(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            run_dir = artifacts / "20260704-000004"
            run_dir.mkdir()
            (run_dir / "scorecard.json").write_text(
                json.dumps({"run_id": "20260704-000004", "cases": [{"id": "core-one", "passed": True}]}),
                encoding="utf-8",
            )

            evidence = collect_case_evidence(artifacts, "core-one", "core")

        self.assertEqual(evidence.status, "blocked")
        self.assertIsNone(evidence.result_path)
        self.assertIsNone(evidence.workflow_closeout_validation_status)

    def test_malformed_scorecard_raises_contextual_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            artifacts = Path(temp_dir)
            run_dir = artifacts / "20260704-000005"
            run_dir.mkdir()
            (run_dir / "scorecard.json").write_text("{not json", encoding="utf-8")

            with self.assertRaisesRegex(RuntimeError, "failed to parse JSON file"):
                collect_case_evidence(artifacts, "core-one", "core")


if __name__ == "__main__":
    unittest.main()
