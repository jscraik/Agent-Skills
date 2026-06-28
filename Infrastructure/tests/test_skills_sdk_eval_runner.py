from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.skills_sdk.eval_runner import internal_scorecard_quality_gates, run_deterministic_eval  # noqa: E402
from ask.skills_sdk.typed_contracts import validate_eval_run_receipt, validate_robot_envelope  # noqa: E402
from ask.commands.skills_impl import _load_release_scenario_sets, skills_sdk_eval_run  # noqa: E402
from ask.envelope import CallResult, ErrorObject  # noqa: E402


PASS_DATASET = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-pass.json"
FAIL_DATASET = "Infrastructure/tests/fixtures/skills_sdk/schema_spine/valid/deterministic-eval-fail.json"
TECHNICAL_WRITER_RELEASE_20 = [
    "smoke-discovery",
    "smoke-boundary-discovery",
    "reader-state-glossary-citations",
    "writer-gap-gathering",
    "happy-readme",
    "generated-boundary",
    "readme-first-run",
    "reader-testing",
    "prompt-injection",
    "risky-command",
    "wrong-domain",
    "docs-validation-ledger",
    "service-doc-reader-job",
    "answer-first-architecture-note",
    "visual-doc-standalone",
    "docs-to-x-routing-boundary",
    "pressure-unverified-badge",
    "pressure-generated-projection-edit",
    "regression-capsule-runtime-boundary",
    "regression-stale-command-example",
]


def _closeout_validation(status: str = "pass") -> dict[str, object]:
    checks = [
        {
            "id": "artifact_receipt_present",
            "status": "pass",
            "message": "eval closeout evidence was emitted",
            "evidence": ["mocked eval backend fixture"],
        }
    ]
    return {
        "schema_version": "skills-sdk.eval-closeout-validation.v1",
        "status": status,
        "checks": checks,
        "blockers": [] if status == "pass" else checks,
    }


def _internal_result_with_scorecard(scorecard_path: Path) -> CallResult:
    scorecard_path.write_text(
        json.dumps(
            {
                "schema_version": "2.1",
                "decision": "fail",
                "passed": False,
                "blocked_cases": 0,
                "tier1_failures": 1,
                "tier2_findings": 0,
                "preflight_warnings": [],
                "readiness_summary": {"unknown": 2},
                "expected_signal_summary": {"runs": 1, "average": 1.0, "minimum": 1.0, "risky_cases": []},
                "security_dependency_screening": {"status": "skipped"},
                "cases": [
                    {"id": "case-pass", "passed": True, "blocked": False},
                    {
                        "id": "case-fail",
                        "passed": False,
                        "blocked": False,
                        "tier1_failures": ["expected signal missing"],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    internal_result = CallResult(status="success")
    internal_result.data.update(
        {
            "eval_status": "pass",
            "resolved_skill_path": "Skills/agent-ops/testing",
            "raw_output": f"Scorecard: {scorecard_path}\n",
            "tessl_eval": {"status": "skipped", "reason": "--skip-tessl"},
            "eval_closeout": {"closeout_validation": _closeout_validation("pass")},
        }
    )
    return internal_result


def _blocked_internal_result_with_passing_scorecard(scorecard_path: Path) -> CallResult:
    scorecard_path.write_text(
        json.dumps(
            {
                "schema_version": "2.1",
                "decision": "pass",
                "passed": True,
                "blocked_cases": 0,
                "tier1_failures": 0,
                "tier2_findings": 0,
                "preflight_warnings": [],
                "readiness_summary": {"unknown": 1},
                "expected_signal_summary": {"runs": 0, "average": None, "minimum": None, "risky_cases": []},
                "security_dependency_screening": {"status": "skipped"},
                "cases": [{"id": "case-pass", "passed": True, "blocked": False}],
            }
        ),
        encoding="utf-8",
    )
    internal_result = CallResult(status="error")
    internal_result.data.update(
        {
            "eval_status": "blocked_runtime",
            "resolved_skill_path": "Skills/agent-ops/testing",
            "raw_output": f"Scorecard: {scorecard_path}\n",
            "eval_closeout": {"closeout_validation": _closeout_validation("pass")},
        }
    )
    internal_result.errors.append(ErrorObject(code="ERR_RUNTIME", message="model unavailable"))
    return internal_result


def _successful_internal_result(codex_profile: str | None = None) -> CallResult:
    internal_result = CallResult(status="success")
    data = {
        "eval_status": "pass",
        "resolved_skill_path": "Skills/agent-ops/testing",
        "raw_output": "Scorecard: Infrastructure/artifacts/evals/testing.json",
        "tessl_eval": {"status": "skipped", "reason": "--skip-tessl"},
        "eval_closeout": {
            "schema_version": "skills-sdk.eval-closeout.v1",
            "status": "pass",
            "skill_path": "Skills/agent-ops/testing",
            "mode": "smoke",
            "runner": "codex",
            "cases": [{"id": "case-pass", "status": "pass"}],
            "mutation_allowed": True,
            "registry_update_allowed": True,
            "next_reproduce_command": "./bin/ask evals run Skills/agent-ops/testing --mode smoke --runner codex --json --robot",
        },
    }
    if codex_profile:
        data["profile_contract"] = {
            "codex_profile": codex_profile,
            "codex_exec_invoked": True,
            "codex_exec_command_shape": ["codex", "exec", "--profile", codex_profile],
        }
    internal_result.data.update(data)
    return internal_result


def _successful_internal_result_without_artifact_receipt() -> CallResult:
    internal_result = CallResult(status="success")
    internal_result.data.update(
        {
            "eval_status": "pass",
            "resolved_skill_path": "Skills/agent-ops/testing",
            "raw_output": "RESULT: PASS",
            "tessl_eval": {"status": "skipped", "reason": "--skip-tessl"},
        }
    )
    return internal_result


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


class TestSkillsSdkEvalRunner(unittest.TestCase):
    def test_runner_passes_exact_match_jsonl_dataset(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset=PASS_DATASET)
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "pass")
        self.assertEqual(model.case_count, 2)
        self.assertEqual(model.passed_count, 2)
        self.assertEqual(model.failed_count, 0)
        self.assertFalse(model.mutation_performed)

    def test_runner_reports_exact_match_failures(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset=FAIL_DATASET)
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "fail")
        self.assertEqual(model.case_count, 1)
        self.assertEqual(model.passed_count, 0)
        self.assertEqual(model.failed_count, 1)
        self.assertEqual(model.cases[0].status, "fail")

    def test_runner_blocks_missing_dataset(self) -> None:
        payload = run_deterministic_eval(REPO_ROOT, dataset="Infrastructure/tests/fixtures/skills_sdk/evals/missing.jsonl")
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "blocked")
        self.assertEqual(model.case_count, 0)
        self.assertIn("dataset not found", model.blockers[0])

    def test_runner_preserves_package_identity_on_blocked_dataset(self) -> None:
        payload = run_deterministic_eval(
            REPO_ROOT,
            dataset="Infrastructure/tests/fixtures/skills_sdk/evals/missing.jsonl",
            skill_ir_schema_version="skills-sdk.skill-ir.v0",
            package_id="skills-sdk-valid-fixture",
            package_digest="sha256:" + ("1" * 64),
        )
        model = validate_eval_run_receipt(payload)

        self.assertEqual(model.status, "blocked")
        self.assertEqual(model.skill_ir_schema_version, "skills-sdk.skill-ir.v0")
        self.assertEqual(model.package_id, "skills-sdk-valid-fixture")
        self.assertEqual(model.package_digest, "sha256:" + ("1" * 64))

    def test_public_cli_runs_deterministic_eval_dataset(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "eval",
                "run",
                "--dataset",
                PASS_DATASET,
                "--skill",
                "Infrastructure/tests/fixtures/skills_sdk/valid_skill",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_eval_run"]
        self.assertIsInstance(payload, dict)
        receipt = validate_eval_run_receipt(payload["receipt"])

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["passed_count"], 2)
        self.assertEqual(receipt.skill_ir_schema_version, "skills-sdk.skill-ir.v0")
        self.assertEqual(receipt.package_id, "skills-sdk-valid-fixture")
        self.assertIsNotNone(receipt.package_digest)
        self.assertFalse(payload["mutation_performed"])

    def test_public_cli_rejects_external_skill_path_for_package_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            external_skill = Path(tmpdir) / "SKILL.md"
            external_skill.write_text(
                "---\nname: external\ndescription: External fixture.\n---\n\n# External\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    "Infrastructure/bin/ask",
                    "sdk",
                    "eval",
                    "run",
                    "--dataset",
                    PASS_DATASET,
                    "--skill",
                    str(external_skill),
                    "--json",
                    "--robot",
                ],
                cwd=REPO_ROOT,
                env=_command_env(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

        self.assertEqual(completed.returncode, 2, completed.stderr)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_eval_run"]
        self.assertIsInstance(payload, dict)

        self.assertEqual(envelope.status, "error")
        self.assertEqual(envelope.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(payload["status"], "blocked")
        self.assertIsNone(payload["receipt"])
        self.assertIn("canonical SKILL.md source", envelope.errors[0].message)

    def test_public_cli_returns_validation_error_for_failing_dataset(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "Infrastructure/bin/ask",
                "sdk",
                "eval",
                "run",
                "--dataset",
                FAIL_DATASET,
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertNotEqual(completed.returncode, 0, completed.stdout)
        envelope = validate_robot_envelope(json.loads(completed.stdout))
        payload = envelope.data["skills_sdk_eval_run"]

        self.assertEqual(envelope.status, "error")
        self.assertEqual(envelope.errors[0].code, "ERR_VALIDATION")
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(payload["failed_count"], 1)

    def test_sdk_internal_runner_delegates_to_existing_eval_backend(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-cloud")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
            )

        run.assert_called_once_with(
            REPO_ROOT,
            "Skills/agent-ops/testing",
            mode="smoke",
            runner="codex",
            dashboard=True,
            skip_tessl=True,
            codex_profile=None,
            cases=None,
            timeout_seconds=None,
        )
        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "success")
        self.assertEqual(payload["runner"], "internal_skill_builder_v0")
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["receipt"]["runner"], "internal_skill_builder_v0")
        self.assertEqual(payload["receipt"]["target_path"], "Skills/agent-ops/testing")
        self.assertEqual(payload["receipt"]["package_id"], "testing")
        self.assertNotEqual(payload["receipt"]["package_digest"], "sha256:" + ("0" * 64))
        self.assertEqual(payload["receipt"]["case_count"], 1)
        self.assertEqual(payload["receipt"]["passed_count"], 1)
        self.assertEqual(payload["receipt"]["failed_count"], 0)
        self.assertIsNone(payload["receipt"]["quality_gates"])
        self.assertEqual(payload["internal_eval"]["tessl_eval"]["status"], "skipped")

    def test_sdk_internal_runner_blocks_synthetic_pass_without_scorecard_or_closeout(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result_without_artifact_receipt()):
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
            )

        payload = result.data["skills_sdk_eval_run"]

        self.assertEqual(result.status, "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(payload["receipt"]["status"], "blocked")
        self.assertIn("blocked_missing_artifact:no_scorecard_or_closeout", payload["receipt"]["blockers"])

    def test_sdk_internal_runner_passes_codex_profile_override(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-cloud")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="oss-cloud",
            )

        run.assert_called_once_with(
            REPO_ROOT,
            "Skills/agent-ops/testing",
            mode="smoke",
            runner="codex",
            dashboard=True,
            skip_tessl=True,
            codex_profile="oss-cloud",
            cases=None,
            timeout_seconds=None,
        )
        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "success")
        self.assertIn("--codex-profile oss-cloud", payload["validation_commands"][0])
        self.assertEqual(payload["receipt"]["lane"], "oss-cloud")
        self.assertEqual(payload["receipt"]["profile"], "oss-cloud")
        self.assertEqual(payload["receipt"]["codex_profile"], "oss-cloud")
        self.assertTrue(payload["receipt"]["codex_exec_invoked"])
        self.assertEqual(payload["receipt"]["codex_exec_command_shape"][:4], ["codex", "exec", "--profile", "oss-cloud"])

    def test_sdk_internal_runner_keeps_fast_profile_in_smoke_check_lane(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("fast")):
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="fast",
            )

        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "success")
        self.assertEqual(payload["receipt"]["lane"], "codex-fast-smoke")
        self.assertEqual(payload["receipt"]["profile"], "fast")
        self.assertEqual(payload["receipt"]["codex_profile"], "fast")

    def test_sdk_internal_runner_blocks_oss_lane_without_codex_exec_proof(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result()):
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="oss-local",
            )

        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "error")
        self.assertEqual(payload["receipt"]["status"], "blocked")
        self.assertIn("blocked_missing_artifact:codex_profile_exec_receipt_missing:oss-local", payload["receipt"]["blockers"])

    def test_sdk_internal_runner_passes_timeout_override(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-local")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="oss-local",
                timeout_seconds=45,
            )

        run.assert_called_once_with(
            REPO_ROOT,
            "Skills/agent-ops/testing",
            mode="smoke",
            runner="codex",
            dashboard=True,
            skip_tessl=True,
            codex_profile="oss-local",
            cases=None,
            timeout_seconds=45,
        )
        payload = result.data["skills_sdk_eval_run"]
        self.assertEqual(result.status, "success")
        self.assertIn("--timeout-seconds 45", payload["validation_commands"][0])

    def test_sdk_internal_runner_replay_command_includes_case_filters(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-local")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/testing",
                mode="smoke",
                runner="internal",
                codex_profile="oss-local",
                cases=["happy-path", "edge-case"],
            )

        run.assert_called_once()
        self.assertEqual(run.call_args.kwargs["cases"], ["happy-path", "edge-case"])
        payload = result.data["skills_sdk_eval_run"]
        command = payload["validation_commands"][0]
        self.assertIn("--case happy-path", command)
        self.assertIn("--case edge-case", command)

    def test_oss_release_lane_expands_default_release_scenario_set(self) -> None:
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-local")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/technical-writer",
                mode="release",
                runner="internal",
                codex_profile="oss-local",
            )

        run.assert_called_once()
        self.assertEqual(run.call_args.kwargs["cases"], TECHNICAL_WRITER_RELEASE_20)
        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])
        self.assertEqual(result.status, "success")
        self.assertEqual(receipt.lane_type, "release")
        self.assertEqual(receipt.scenario_set_id, "technical-writer-release-20-v1")
        self.assertEqual(receipt.scenario_set_case_ids, TECHNICAL_WRITER_RELEASE_20)
        self.assertEqual(receipt.selected_case_ids, TECHNICAL_WRITER_RELEASE_20)
        self.assertEqual(receipt.release_set_minimum, 20)

    def test_release_scenario_sets_load_without_pyyaml(self) -> None:
        evals_path = REPO_ROOT / "Skills/agent-ops/technical-writer/references/evals.yaml"
        with mock.patch.dict(sys.modules, {"yaml": None}):
            release_sets = _load_release_scenario_sets(evals_path)

        self.assertEqual(release_sets[0]["id"], "technical-writer-release-20-v1")
        self.assertEqual(release_sets[0]["case_ids"], TECHNICAL_WRITER_RELEASE_20)

    def test_oss_release_lane_blocks_filtered_debug_subset_before_runtime(self) -> None:
        with mock.patch("ask.commands.evals.run_evals") as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/technical-writer",
                mode="release",
                runner="internal",
                codex_profile="oss-local",
                cases=["smoke-discovery"],
            )

        run.assert_not_called()
        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])
        self.assertEqual(result.status, "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.lane_type, "focused-debug")
        self.assertEqual(receipt.case_count, 1)
        self.assertEqual(receipt.selected_case_ids, ["smoke-discovery"])
        self.assertEqual(receipt.scenario_set_case_ids, TECHNICAL_WRITER_RELEASE_20)
        self.assertIn("focused_debug_subset_not_release_evidence:selected:1:required:20:minimum:20", receipt.blockers)

    def test_release_lane_accepts_full_case_set_in_any_order(self) -> None:
        reversed_cases = list(reversed(TECHNICAL_WRITER_RELEASE_20))
        with mock.patch("ask.commands.evals.run_evals", return_value=_successful_internal_result("oss-local")) as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/technical-writer",
                mode="release",
                runner="internal",
                codex_profile="oss-local",
                cases=reversed_cases,
            )

        run.assert_called_once()
        self.assertEqual(run.call_args.kwargs["cases"], reversed_cases)
        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])
        self.assertEqual(result.status, "success")
        self.assertEqual(receipt.selected_case_ids, reversed_cases)
        self.assertEqual(receipt.scenario_set_case_ids, TECHNICAL_WRITER_RELEASE_20)

    def test_release_lane_enforces_release_set_without_profile(self) -> None:
        with mock.patch("ask.commands.evals.run_evals") as run:
            result = skills_sdk_eval_run(
                REPO_ROOT,
                target="Skills/agent-ops/technical-writer",
                mode="release",
                runner="internal",
                cases=["smoke-discovery"],
            )

        run.assert_not_called()
        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])
        self.assertEqual(result.status, "error")
        self.assertEqual(receipt.status, "blocked")
        self.assertIn("focused_debug_subset_not_release_evidence:selected:1:required:20:minimum:20", receipt.blockers)

    def test_sdk_internal_runner_binds_scorecard_case_counts_to_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scorecard_path = Path(temp_dir) / "scorecard.json"
            internal_result = _internal_result_with_scorecard(scorecard_path)
            with mock.patch("ask.commands.evals.run_evals", return_value=internal_result):
                result = skills_sdk_eval_run(
                    REPO_ROOT,
                    target="Skills/agent-ops/testing",
                    mode="smoke",
                    runner="internal",
                )

        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])

        self.assertEqual(result.status, "error")
        self.assertEqual(payload["status"], "fail")
        self.assertEqual(Path(receipt.dataset_path), scorecard_path.resolve())
        self.assertNotEqual(receipt.dataset_digest, "sha256:" + ("0" * 64))
        self.assertEqual(receipt.package_id, "testing")
        self.assertIsNotNone(receipt.package_digest)
        self.assertEqual(receipt.case_count, 2)
        self.assertEqual(receipt.passed_count, 1)
        self.assertEqual(receipt.failed_count, 1)
        self.assertEqual([case.case_id for case in receipt.cases], ["case-pass", "case-fail"])
        self.assertEqual([case.status for case in receipt.cases], ["pass", "fail"])
        self.assertIsNotNone(receipt.quality_gates)
        self.assertEqual(receipt.quality_gates.source, "internal_scorecard")
        self.assertEqual(receipt.quality_gates.decision, "fail")
        self.assertEqual(receipt.quality_gates.tier1_failures, 1)
        self.assertIn("scorecard_decision_passes", receipt.quality_gates.failed_assertions)
        self.assertIn("tier1_failures_zero", receipt.quality_gates.failed_assertions)
        self.assertIn("quality_gate_failed:scorecard_decision_passes", receipt.blockers)
        self.assertIn("expected signal missing", receipt.blockers)

    def test_internal_scorecard_quality_gates_ignore_isolated_codex_home_notice(self) -> None:
        gates = internal_scorecard_quality_gates(
            {
                "schema_version": "2.1",
                "decision": "pass",
                "passed": True,
                "blocked_cases": 0,
                "tier1_failures": 0,
                "tier2_findings": 0,
                "preflight_warnings": [
                    "Using isolated CODEX_HOME for live eval session writes: /private/tmp/skill-evals-codex-home-test"
                ],
                "readiness_summary": {"unknown": 1},
                "expected_signal_summary": {"runs": 0, "average": None, "minimum": None, "risky_cases": []},
                "security_dependency_screening": {"status": "skipped"},
            }
        )

        self.assertIsNotNone(gates)
        self.assertEqual(gates["preflight_warning_count"], 0)
        self.assertNotIn("preflight_warnings_zero", gates["failed_assertions"])

    def test_internal_scorecard_quality_gates_keep_actionable_preflight_warning(self) -> None:
        gates = internal_scorecard_quality_gates(
            {
                "schema_version": "2.1",
                "decision": "pass",
                "passed": True,
                "blocked_cases": 0,
                "tier1_failures": 0,
                "tier2_findings": 0,
                "preflight_warnings": ["missing required runtime profile"],
                "readiness_summary": {"unknown": 1},
                "expected_signal_summary": {"runs": 0, "average": None, "minimum": None, "risky_cases": []},
                "security_dependency_screening": {"status": "skipped"},
            }
        )

        self.assertIsNotNone(gates)
        self.assertEqual(gates["preflight_warning_count"], 1)
        self.assertIn("preflight_warnings_zero", gates["failed_assertions"])

    def test_sdk_internal_runner_does_not_upgrade_backend_blocker_to_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            scorecard_path = Path(temp_dir) / "scorecard.json"
            internal_result = _blocked_internal_result_with_passing_scorecard(scorecard_path)
            with mock.patch("ask.commands.evals.run_evals", return_value=internal_result):
                result = skills_sdk_eval_run(
                    REPO_ROOT,
                    target="Skills/agent-ops/testing",
                    mode="smoke",
                    runner="internal",
                )

        payload = result.data["skills_sdk_eval_run"]
        receipt = validate_eval_run_receipt(payload["receipt"])

        self.assertEqual(result.status, "error")
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(receipt.status, "blocked")
        self.assertEqual(receipt.case_count, 1)
        self.assertEqual(receipt.passed_count, 1)
        self.assertEqual(receipt.failed_count, 0)
        self.assertIsNotNone(receipt.quality_gates)
        self.assertEqual(receipt.quality_gates.failed_assertions, [])
        self.assertIn("model unavailable", receipt.blockers)


if __name__ == "__main__":
    unittest.main()
