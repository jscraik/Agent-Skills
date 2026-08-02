from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_ab_judge import (  # noqa: E402
    _judge_prompt,
    build_ab_judge_preview_receipt,
    build_ab_judge_score_receipt,
)
from ask.skills_sdk.eval_ab_rubric import AB_RUBRIC_ID, canonical_ab_rubric_digest  # noqa: E402
from ask.skills_sdk.typed_contracts import (  # noqa: E402
    validate_ab_judge_preview_receipt,
    validate_ab_run_receipt,
)


RUN_RECEIPT = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.json"
RUN_RECEIPT_V1 = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-run-receipt.v1.json"


class TestSkillsSdkAbJudgePreview(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence_root = REPO_ROOT / ".harness/test-sdk-ab-judge"
        shutil.rmtree(self.evidence_root, ignore_errors=True)
        self.evidence_root.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        shutil.rmtree(self.evidence_root, ignore_errors=True)

    def _preview_for_payload(self, payload: dict[str, object], label: str) -> dict[str, object]:
        receipt_path = self.evidence_root / f"{label}.json"
        receipt_path.write_text(json.dumps(payload), encoding="utf-8")
        return build_ab_judge_preview_receipt(
            REPO_ROOT,
            run_receipt=receipt_path.relative_to(REPO_ROOT).as_posix(),
        )

    def test_builder_creates_sanitized_judge_input_without_provider_invocation(self) -> None:
        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT_V1)

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["operation"], "ab_judge_preview")
        self.assertEqual(receipt["judge_profile"]["id"], "oss-local")
        self.assertEqual(receipt["judge_profile"]["model"], "qwen3.5:9b-mlx")
        self.assertEqual(receipt["rubric_id"], AB_RUBRIC_ID)
        self.assertEqual(receipt["rubric_digest"], canonical_ab_rubric_digest())
        self.assertEqual(receipt["allowed_winners"], ["skill_a", "skill_b", "inconclusive"])
        self.assertTrue(receipt["calibration_required"])
        self.assertFalse(receipt["provider_invoked"])
        self.assertFalse(receipt["network_accessed"])
        self.assertFalse(receipt["mutation_performed"])

        comparison = receipt["comparison_payload"]
        self.assertEqual(comparison["schema_version"], "skills-sdk.ab-judge-decision.v0")
        self.assertEqual(comparison["rubric"]["rubric_id"], AB_RUBRIC_ID)
        self.assertEqual(comparison["rubric_digest"], canonical_ab_rubric_digest())
        self.assertTrue(comparison["rubric"]["judge_output_contract"]["unvalidated_judges_are_advisory"])
        self.assertEqual({row["variant_label"] for row in comparison["variant_results"]}, {"A", "B"})
        self.assertNotIn("output_last_message_path", comparison["variant_results"][0])
        self.assertNotIn("command_argv", comparison["variant_results"][0])
        validate_ab_judge_preview_receipt(receipt)

    def test_judge_prompt_binds_winner_to_normalized_policy_delta(self) -> None:
        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT_V1)

        prompt = _judge_prompt(receipt["comparison_payload"])

        self.assertIn("normalized_score_b - normalized_score_a", prompt)
        self.assertIn("do not use the raw 0-to-5 score gap", prompt)
        self.assertIn("set winner to\ninconclusive", prompt)

    def test_builder_blocks_non_completed_run_receipt(self) -> None:
        receipt = build_ab_judge_preview_receipt(
            REPO_ROOT,
            run_receipt="Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/ab-plan-receipt.json",
        )

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
        validate_ab_judge_preview_receipt(receipt)

    def test_builder_accepts_ab_run_robot_envelope(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        envelope_path = self.evidence_root / "ab-run-envelope.json"
        envelope_path.write_text(
            json.dumps({"status": "success", "data": {"skills_sdk_eval_ab_run": {"receipt": run_receipt}}}),
            encoding="utf-8",
        )

        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=envelope_path.relative_to(REPO_ROOT).as_posix())

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["comparison_payload"]["experiment_id"], run_receipt["experiment_id"])
        validate_ab_judge_preview_receipt(receipt)

    def test_builder_blocks_incomplete_nested_run_receipt_identities(self) -> None:
        run_receipt = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        del run_receipt["skill_a"]["package_digest"]
        receipt_path = self.evidence_root / "ab-run-missing-package-digest.json"
        receipt_path.write_text(json.dumps(run_receipt), encoding="utf-8")

        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=receipt_path.relative_to(REPO_ROOT).as_posix())

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
        self.assertIsNone(receipt["comparison_payload"])
        validate_ab_judge_preview_receipt(receipt)

    def test_v0_remains_readable_but_cannot_admit_judge_runtime_proof(self) -> None:
        parsed = validate_ab_run_receipt(
            json.loads((REPO_ROOT / RUN_RECEIPT).read_text(encoding="utf-8"))
        )
        self.assertEqual(parsed.schema_version, "skills-sdk.ab-run-receipt.v0")

        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT)

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("v1_runtime_profile_proof_required", receipt["blockers"])
        self.assertIsNone(receipt["comparison_payload"])
        validate_ab_judge_preview_receipt(receipt)

    def test_v1_completed_receipt_admits_judge_preview(self) -> None:
        receipt = build_ab_judge_preview_receipt(REPO_ROOT, run_receipt=RUN_RECEIPT_V1)

        self.assertEqual(receipt["status"], "preview")
        self.assertEqual(receipt["blockers"], [])
        validate_ab_judge_preview_receipt(receipt)

    def test_required_fact_not_applicable_cannot_admit_judge_preview(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        fixture["runtime_profile_gates"][0]["preflight"]["runtime"]["status"] = "not_applicable"

        receipt = self._preview_for_payload(fixture, "required-fact-not-applicable")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
        self.assertIsNone(receipt["comparison_payload"])
        validate_ab_judge_preview_receipt(receipt)

    def test_judge_rejects_v1_receipts_without_ordered_runtime_proof(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        mutations = {
            "missing-gates": lambda row: row.pop("runtime_profile_gates"),
            "empty-gates": lambda row: row.__setitem__("runtime_profile_gates", []),
            "reordered-gates": lambda row: row.__setitem__(
                "runtime_profile_gates", list(reversed(row["runtime_profile_gates"]))
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate = deepcopy(fixture)
                mutate(candidate)
                receipt = self._preview_for_payload(candidate, label)
                self.assertEqual(receipt["status"], "blocked")
                self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
                self.assertIsNone(receipt["comparison_payload"])

    def test_judge_rejects_substituted_duplicated_or_misplaced_profiles(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        prefixes = {
            "fast-substitution": ["codex", "exec", "--profile", "fast"],
            "profile-omitted": ["codex", "exec", "--sandbox", "read-only"],
            "profile-duplicated": [
                "codex", "exec", "--profile", "oss-local", "--profile", "oss-local"
            ],
            "profile-misplaced": ["codex", "--profile", "oss-local", "exec"],
            "profile-delayed": [
                "codex", "exec", "--sandbox", "read-only", "--profile", "oss-local"
            ],
        }
        for label, prefix in prefixes.items():
            with self.subTest(label=label):
                candidate = deepcopy(fixture)
                result = candidate["runtime_profile_gates"][0]["variant_results"][0]
                result["command_argv"] = prefix + result["command_argv"][4:]
                candidate["variant_results"][0]["command_argv"] = deepcopy(result["command_argv"])
                receipt = self._preview_for_payload(candidate, label)
                self.assertEqual(receipt["status"], "blocked")
                self.assertIn("run_receipt_contract_invalid", receipt["blockers"])

    def test_judge_metadata_alone_cannot_claim_runtime_profile_proof(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        fixture["runtime_profile_gates"] = []
        for result in fixture["variant_results"]:
            result["command_argv"][3] = "fast"
        self.assertEqual(fixture["judge_profile"]["codex_profile"], "oss-local")

        receipt = self._preview_for_payload(fixture, "judge-metadata-only")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
        self.assertIsNone(receipt["comparison_payload"])

    def test_judge_rejects_top_level_and_gate_result_mismatch(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        fixture["variant_results"][0]["runner_stdout_digest"] = f"sha256:{'f' * 64}"

        receipt = self._preview_for_payload(fixture, "top-level-gate-mismatch")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])

    def test_completed_v1_requires_successful_variants_and_passing_preflight(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        mutations = {
            "blocked-variants": lambda row: _mutate_all_gate_results(
                row, status="blocked", blockers=["execution_failed"]
            ),
            "failed-variants": lambda row: _mutate_all_gate_results(
                row, status="pass", exit_code=1
            ),
            "missing-preflight-admission": lambda row: row["runtime_profile_gates"][0]["preflight"].pop(
                "admission"
            ),
            "nonzero-gate-blocker": lambda row: row["runtime_profile_gates"][0].update(
                blockers=["execution_failed"]
            ),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                candidate = deepcopy(fixture)
                mutate(candidate)
                receipt = self._preview_for_payload(candidate, f"completed-invariant-{label}")
                self.assertEqual(receipt["status"], "blocked")
                self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
                self.assertIsNone(receipt["comparison_payload"])

    def test_completed_v1_binds_profile_provider_and_model_to_each_lane(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        cases: dict[str, dict[str, object]] = {}

        for fact_name in ("profile_config", "model_catalog", "runtime", "auth", "catalog"):
            candidate = deepcopy(fixture)
            local = candidate["runtime_profile_gates"][0]["preflight"]
            cloud = candidate["runtime_profile_gates"][1]["preflight"]
            local[fact_name], cloud[fact_name] = cloud[fact_name], local[fact_name]
            cases[f"cross-swapped-{fact_name}"] = candidate

        for field_name in ("configured_model_id", "configured_provider_id"):
            candidate = deepcopy(fixture)
            candidate["runtime_profile_gates"][0]["preflight"]["profile_config"].pop(field_name)
            cases[f"missing-{field_name}"] = candidate

        candidate = deepcopy(fixture)
        candidate["runtime_profile_gates"][0]["preflight"]["profile_config"][
            "configured_provider_id"
        ] = "ollama-cloud"
        cases["substituted-provider"] = candidate

        candidate = deepcopy(fixture)
        candidate["runtime_profile_gates"][0]["preflight"]["profile_config"][
            "configured_model_id"
        ] = "substituted-local-model"
        cases["substituted-configured-model"] = candidate

        for label, payload in cases.items():
            with self.subTest(label=label):
                receipt = self._preview_for_payload(payload, f"authority-{label}")
                self.assertEqual(receipt["status"], "blocked")
                self.assertIn("run_receipt_contract_invalid", receipt["blockers"])
                self.assertIsNone(receipt["comparison_payload"])

    def test_completed_v1_rejects_result_evidence_mismatch_before_runner(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        fixture["variant_results"][0]["command_argv"] = list(
            reversed(fixture["variant_results"][0]["command_argv"])
        )
        receipt_path = self.evidence_root / "completed-result-evidence-mismatch.json"
        receipt_path.write_text(json.dumps(fixture), encoding="utf-8")
        runner_called = False

        def forbidden_runner(*_args: object, **_kwargs: object) -> object:
            nonlocal runner_called
            runner_called = True
            raise AssertionError("judge runner must not be called for an invalid run receipt")

        score = build_ab_judge_score_receipt(
            REPO_ROOT,
            run_receipt=receipt_path.relative_to(REPO_ROOT).as_posix(),
            evidence_root=(self.evidence_root / "result-evidence-score").relative_to(REPO_ROOT).as_posix(),
            runner=forbidden_runner,
        )
        self.assertEqual(score["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", score["blockers"])
        self.assertFalse(runner_called)

    def test_judge_rejects_unknown_run_receipt_schema(self) -> None:
        fixture = json.loads((REPO_ROOT / RUN_RECEIPT_V1).read_text(encoding="utf-8"))
        fixture["schema_version"] = "skills-sdk.ab-run-receipt.v999"

        receipt = self._preview_for_payload(fixture, "unknown-schema")

        self.assertEqual(receipt["status"], "blocked")
        self.assertIn("run_receipt_contract_invalid", receipt["blockers"])

    def test_cli_requires_preview_gate(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                RUN_RECEIPT_V1,
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertNotEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertIn("requires --preview", payload["errors"][0]["message"])

    def test_cli_preview_returns_judge_input_receipt(self) -> None:
        proc = subprocess.run(
            [
                str(REPO_ROOT / "bin/ask"),
                "sdk",
                "eval",
                "ab-judge-preview",
                "--run-receipt",
                RUN_RECEIPT_V1,
                "--preview",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            check=False,
            text=True,
            capture_output=True,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        receipt = payload["data"]["skills_sdk_eval_ab_judge_preview"]["receipt"]
        self.assertEqual(receipt["status"], "preview")
        self.assertFalse(receipt["provider_invoked"])
        validate_ab_judge_preview_receipt(receipt)


def _mutate_all_gate_results(
    payload: dict[str, object],
    *,
    status: str,
    blockers: list[str] | None = None,
    exit_code: int = 0,
) -> None:
    for gate in payload["runtime_profile_gates"]:
        for result in gate["variant_results"]:
            result["status"] = status
            result["exit_code"] = exit_code
            result["blockers"] = [] if blockers is None else list(blockers)
    payload["variant_results"] = deepcopy(payload["runtime_profile_gates"][0]["variant_results"])


if __name__ == "__main__":
    unittest.main()
