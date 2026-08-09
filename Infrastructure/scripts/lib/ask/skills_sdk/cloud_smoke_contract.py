from __future__ import annotations

from datetime import datetime
from typing import Any

from ask.skills_sdk.ab_transport_contracts import (
    is_configs_auth_wrapper,
    is_configs_codex_exec_wrapper,
)


CLOUD_SMOKE_MARKER = "CODEX_OSS_CLOUD_OK"
REDACTED_AUTH_WRAPPER = "<configs-auth-wrapper>"
REDACTED_CODEX_EXEC_WRAPPER = "<configs-codex-exec-wrapper>"
FORBIDDEN_CLOUD_SMOKE_FLAGS = frozenset({
    "--dangerously-bypass-approvals-and-sandbox",
    "--no-sandbox",
    "--cd",
    "--enable",
})


def valid_cloud_smoke_receipt(payload: dict[str, Any]) -> bool:
    return not cloud_smoke_receipt_findings(payload)


def cloud_smoke_receipt_findings(payload: dict[str, Any]) -> list[str]:
    """Return stable, receipt-safe reasons a cloud smoke is not admissible."""
    required = {
        "schema_version", "observed_at", "status", "lane", "codex_profile", "model",
        "model_provider", "auth_source", "provider_invoked", "execution_argv", "exit_code",
        "marker", "warnings", "findings", "secret_value_observed",
        "secret_observation",
    }
    findings = [f"missing:{key}" for key in sorted(required - payload.keys())]
    if findings:
        return findings
    if payload.get("schema_version") != "skills-sdk.oss-cloud-smoke-run.v0":
        findings.append("schema_version_mismatch")
    if not _valid_identity(payload):
        findings.append("identity_mismatch")
    findings.extend(_execution_argv_findings(payload))
    if not _valid_outcome(payload, CLOUD_SMOKE_MARKER):
        findings.append("outcome_mismatch")
    return findings


def _valid_execution_argv(payload: dict[str, Any]) -> bool:
    return not _execution_argv_findings(payload)


def _child_wrapper_index(argv: list[str]) -> int | None:
    expected_index = 12
    return expected_index if len(argv) > expected_index and (
        is_configs_codex_exec_wrapper(argv[expected_index])
        or argv[expected_index] == REDACTED_CODEX_EXEC_WRAPPER
    ) else None


def _adjacent_pair(child: list[str], flag: str, expected: str) -> bool:
    positions = [index for index, value in enumerate(child[:-1]) if value == flag]
    return len(positions) == 1 and child[positions[0] + 1] == expected


def _child_contract_findings(child: list[str]) -> list[str]:
    expected_shape = [
        child[0] if child else "",
        "--profile", "oss-cloud",
        "--strict-config",
        "-c", 'approval_policy="on-request"',
        "--skip-git-repo-check",
        "--sandbox", "read-only",
        "--ephemeral",
        "--model", "deepseek-v4-flash:cloud",
        "Reply exactly CODEX_OSS_CLOUD_OK",
    ]
    findings = ["codex_exec_child_argv_shape"] if child != expected_shape else []
    required_pairs = {
        "--profile": "oss-cloud",
        "--sandbox": "read-only",
        "--model": "deepseek-v4-flash:cloud",
        "-c": 'approval_policy="on-request"',
    }
    findings.extend(
        f"missing_or_nonadjacent:{flag}"
        for flag, expected in required_pairs.items()
        if not _adjacent_pair(child, flag, expected)
    )
    findings.extend(
        f"missing:{flag}"
        for flag in ("--strict-config", "--ephemeral")
        if flag not in child
    )
    findings.extend(
        f"forbidden:{flag}" for flag in sorted(FORBIDDEN_CLOUD_SMOKE_FLAGS) if flag in child
    )
    return findings


def _child_chain_findings(argv: list[str]) -> list[str]:
    if len(argv) < 12:
        return ["codex_exec_child_chain_contract"]
    if argv[7] != "env" or argv[8:10] != ["-u", "CODEX_CONFIG_HOME"]:
        return ["codex_exec_child_chain_contract"]
    if argv[10] != "CODEX_HOME=<isolated-codex-home>" or argv[11] != "bash":
        return ["codex_exec_child_chain_contract"]
    return []


def _execution_argv_findings(payload: dict[str, Any]) -> list[str]:
    argv = payload.get("execution_argv")
    if not isinstance(argv, list) or len(argv) < 15 or not all(isinstance(item, str) for item in argv):
        return ["execution_argv_shape"]
    if (
        argv[0] != "bash"
        or not (is_configs_auth_wrapper(argv[1]) or argv[1] == REDACTED_AUTH_WRAPPER)
        or argv[2:7] != [
            "--env-file", "<operator-approved-opaque-env-stream>",
            "--require-env", "OLLAMA_API_KEY", "--",
        ]
    ):
        return ["auth_wrapper_contract"]
    wrapper_index = _child_wrapper_index(argv)
    if wrapper_index is None:
        return ["codex_exec_wrapper_contract"]
    chain_findings = _child_chain_findings(argv)
    if chain_findings:
        return chain_findings
    return _child_contract_findings(argv[wrapper_index:])


def _valid_identity(payload: dict[str, Any]) -> bool:
    return all((
        payload.get("lane") == "oss-cloud", payload.get("codex_profile") == "oss-cloud",
        payload.get("model") == "deepseek-v4-flash:cloud", payload.get("model_provider") == "ollama-cloud",
        payload.get("auth_source") == "1password_desktop_fifo",
        type(payload.get("provider_invoked")) is bool and payload.get("provider_invoked") is True,
    ))


def _valid_outcome(payload: dict[str, Any], marker: str) -> bool:
    observed_at = payload.get("observed_at")
    try:
        datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    except (AttributeError, TypeError, ValueError):
        return False
    observation = payload.get("secret_observation")
    valid_observation = isinstance(observation, dict) and observation == {
        "status": "clear", "source": "captured_output_scan", "redacted": True,
    }
    return all((
        payload.get("status") == "pass", payload.get("exit_code") == 0,
        payload.get("marker") == marker, payload.get("findings") == [],
        isinstance(payload.get("warnings"), list),
        type(payload.get("secret_value_observed")) is bool and payload["secret_value_observed"] is False,
        valid_observation,
    ))
