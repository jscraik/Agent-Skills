from __future__ import annotations

from datetime import datetime
from typing import Any


CLOUD_SMOKE_MARKER = "CODEX_OSS_CLOUD_OK"


def valid_cloud_smoke_receipt(payload: dict[str, Any]) -> bool:
    required = {
        "schema_version", "observed_at", "status", "lane", "codex_profile", "model",
        "model_provider", "auth_source", "provider_invoked", "execution_argv", "exit_code",
        "marker", "warnings", "findings",
    }
    return (
        required.issubset(payload)
        and payload.get("schema_version") == "skills-sdk.oss-cloud-smoke-run.v0"
        and _valid_identity(payload)
        and _valid_execution_argv(payload)
        and _valid_outcome(payload, CLOUD_SMOKE_MARKER)
    )


def _valid_execution_argv(payload: dict[str, Any]) -> bool:
    argv = payload.get("execution_argv")
    if not isinstance(argv, list) or len(argv) < 15 or not all(isinstance(item, str) for item in argv):
        return False
    if (
        argv[0] != "bash"
        or not argv[1].endswith("/run-auth-backed.sh")
        or argv[2:7] != [
            "--env-file", "<operator-approved-opaque-env-stream>",
            "--require-env", "OLLAMA_API_KEY", "--",
        ]
    ):
        return False
    try:
        child = argv[next(index for index, value in enumerate(argv) if value.endswith("/run-codex-exec.sh")):]
    except StopIteration:
        return False
    return all(token in child for token in (
        "--profile", "oss-cloud", "--strict-config", "--sandbox", "read-only",
        "--ephemeral", "--model", "deepseek-v4-flash:cloud",
    ))


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
    return all((
        payload.get("status") == "pass", payload.get("exit_code") == 0,
        payload.get("marker") == marker, payload.get("findings") == [],
        isinstance(payload.get("warnings"), list), payload.get("secret_value_observed", False) is False,
    ))
