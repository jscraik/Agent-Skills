from __future__ import annotations

from typing import Any


EVAL_PROFILE_PREVIEW_SCHEMA_VERSION = "skills-sdk.eval-profile-preview-receipt.v0"
EVAL_PROFILE_PREVIEW_SCHEMA_URI = (
    "https://jscraik.local/agent-skills/schemas/skills-sdk/eval-profile-preview-receipt.v0.schema.json"
)
EVAL_PROFILE_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]


def _codex_execution_profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "codex-read-only",
            "runner": "codex_exec",
            "sandbox_mode": "read-only",
            "approval_policy": "on-request",
            "codex_json_events_required": True,
            "output_schema_supported": True,
            "mutation_allowed": False,
        },
        {
            "id": "codex-workspace-write",
            "runner": "codex_exec",
            "sandbox_mode": "workspace-write",
            "approval_policy": "on-request",
            "codex_json_events_required": True,
            "output_schema_supported": True,
            "mutation_allowed": True,
        },
    ]


def _judge_profiles() -> list[dict[str, Any]]:
    return [
        {
            "id": "oss-local",
            "provider": "codex",
            "mode": "local",
            "host": "codex-cli-profile",
            "model": "qwen3.5:latest",
            "network_required": True,
            "secret_env_names": [],
            "auth_boundary": "none",
            "receives_sanitized_outputs_only": True,
        },
        {
            "id": "oss-cloud",
            "provider": "codex",
            "mode": "cloud",
            "host": "codex-cli-profile",
            "model": "deepseek-v4-flash:cloud",
            "network_required": True,
            "secret_env_names": ["OLLAMA_API_KEY"],
            "auth_boundary": "codex_cli_auth",
            "receives_sanitized_outputs_only": True,
        },
        {
            "id": "codex-fast",
            "provider": "codex",
            "mode": "codex-fast",
            "host": "codex-cli-authenticated-session",
            "model": "gpt-5.3-codex-spark",
            "network_required": True,
            "secret_env_names": [],
            "auth_boundary": "codex_cli_auth",
            "receives_sanitized_outputs_only": True,
        },
    ]


def _profile_by_id(profiles: list[dict[str, Any]], profile_id: str, profile_kind: str) -> dict[str, Any]:
    for profile in profiles:
        if profile["id"] == profile_id:
            return dict(profile)
    known = ", ".join(str(profile["id"]) for profile in profiles)
    raise ValueError(f"Unknown {profile_kind} profile {profile_id!r}; expected one of: {known}")


def select_execution_profile(profile_id: str) -> dict[str, Any]:
    return _profile_by_id(_codex_execution_profiles(), profile_id, "execution")


def select_judge_profile(profile_id: str) -> dict[str, Any]:
    return _profile_by_id(_judge_profiles(), profile_id, "judge")


def build_eval_profile_preview_receipt() -> dict[str, Any]:
    judge_secret_names = sorted(
        {
            secret
            for profile in _judge_profiles()
            for secret in profile["secret_env_names"]
        }
    )
    return {
        "schema_version": EVAL_PROFILE_PREVIEW_SCHEMA_VERSION,
        "schema_uri": EVAL_PROFILE_PREVIEW_SCHEMA_URI,
        "status": "preview",
        "operation": "eval_profile_preview",
        "execution_profiles": _codex_execution_profiles(),
        "judge_profiles": _judge_profiles(),
        "secret_boundary": {
            "skill_execution_env_secret_names": [],
            "judge_env_secret_names": judge_secret_names,
            "skill_execution_receives_judge_secrets": False,
        },
        "execution_boundary": "codex_exec_sandbox",
        "external_intake_boundary": "sdk_quarantine_only",
        "mutation_performed": False,
        "network_accessed": False,
        "provider_invoked": False,
        "blockers": [],
        "acceptance_trace": EVAL_PROFILE_ACCEPTANCE_TRACE,
        "agent_summary": (
            "eval profile preview declares Codex sandbox execution profiles and isolated "
            "Codex-profile judge profiles without invoking providers."
        ),
    }
