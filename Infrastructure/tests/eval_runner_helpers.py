from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from ask.envelope import CallResult, ErrorObject


REPO_ROOT = Path(__file__).resolve().parents[2]


def closeout_validation(status: str = "pass") -> dict[str, object]:
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


def internal_result_with_scorecard(scorecard_path: Path) -> CallResult:
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
                    {"id": "case-fail", "passed": False, "blocked": False, "tier1_failures": ["expected signal missing"]},
                ],
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
            "eval_closeout": {"closeout_validation": closeout_validation("pass")},
        }
    )
    return internal_result


def blocked_internal_result_with_passing_scorecard(scorecard_path: Path) -> CallResult:
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
            "eval_closeout": {"closeout_validation": closeout_validation("pass")},
        }
    )
    internal_result.errors.append(ErrorObject(code="ERR_RUNTIME", message="model unavailable"))
    return internal_result


def successful_internal_result(codex_profile: str | None = None) -> CallResult:
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


def successful_internal_result_with_blocked_closeout_validation() -> CallResult:
    internal_result = CallResult(status="success")
    internal_result.data.update(
        {
            "eval_status": "pass",
            "resolved_skill_path": "Skills/agent-ops/testing",
            "raw_output": "RESULT: PASS",
            "tessl_eval": {"status": "skipped", "reason": "--skip-tessl"},
            "eval_closeout": {
                "schema_version": "skills-sdk.eval-closeout.v1",
                "status": "pass",
                "skill_path": "Skills/agent-ops/testing",
                "mode": "smoke",
                "runner": "codex",
                "cases": [],
                "mutation_allowed": True,
                "registry_update_allowed": False,
                "next_reproduce_command": "./bin/ask evals run Skills/agent-ops/testing --mode smoke --runner codex --json --robot",
                "closeout_validation": closeout_validation("blocked"),
            },
            "profile_contract": {
                "codex_profile": "oss-local",
                "codex_exec_invoked": True,
                "codex_exec_command_shape": ["codex", "exec", "--profile", "oss-local"],
            },
        }
    )
    return internal_result


def successful_internal_result_without_artifact_receipt() -> CallResult:
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


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("MISE_STATE_DIR", str(temp_base / "mise-state"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env
