from __future__ import annotations

from typing import Any


EVAL_PROFILE_PREVIEW_SCHEMA_VERSION = "skills-sdk.eval-profile-preview-receipt.v0"
EVAL_PROFILE_PREVIEW_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/eval-profile-preview-receipt.v0.schema.json"
)
EVAL_PROFILE_ACCEPTANCE_TRACE = ["FR-003", "FR-008", "SA-003", "SA-004", "VP-021", "VP-022", "VP-030"]
LOCAL_SANDBOX_DEFAULT_SETTINGS = {"num_ctx": 8192, "num_predict": 1024, "temperature": 0.1, "top_p": 0.9}
LOCAL_SANDBOX_LARGE_TRANSCRIPT_SETTINGS = {
    "num_ctx": 16384,
    "num_predict": 1536,
    "temperature": 0.1,
    "top_p": 0.9,
}
LOCAL_SECURITY_SPECIALIST_SETTINGS = {
    "num_ctx": 8192,
    "num_predict": 1024,
    "repeat_penalty": 1.15,
    "temperature": 0.35,
    "top_k": 40,
    "top_p": 0.9,
}
LOCAL_QWEN35_MLX_RUNTIME_METADATA = {
    "model_id": "203e30078279",
    "size_gb": 8.9,
    "architecture": "qwen3_5",
    "parameters": "9.4B",
    "quantization": "nvfp4",
    "context_length": 262144,
    "metadata_source": "ollama_show",
}
LOCAL_QWEN35_SMOKE_GUARD = {
    "max_tokens_used": 5000,
    "forbid_visible_thinking": True,
    "forbid_fallback_metadata": True,
}
_LOCAL_JUDGE_PROFILE_SPECS = (
    ("oss-local", "oss-local", "qwen3.5:9b-mlx", "local_sandbox_eval_default", LOCAL_SANDBOX_DEFAULT_SETTINGS),
    (
        "oss-local-large-transcript",
        "oss-local",
        "qwen3.5:9b-mlx",
        "larger_local_transcript_trial",
        LOCAL_SANDBOX_LARGE_TRANSCRIPT_SETTINGS,
    ),
    ("oss-local-code", "oss-local-code", "qwen3-coder:30b", "code_heavy_specialist", LOCAL_SANDBOX_DEFAULT_SETTINGS),
    ("oss-local-fallback", "oss-local-fallback", "qwen3.5:latest", "fast_fallback", LOCAL_SANDBOX_DEFAULT_SETTINGS),
    (
        "oss-security",
        "oss-security",
        "CyberCrew/notmythos-8b",
        "local_security_specialist",
        LOCAL_SECURITY_SPECIALIST_SETTINGS,
    ),
)


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
    profiles = [
        _local_judge_profile(profile_id, codex_profile, model, model_role, settings)
        for profile_id, codex_profile, model, model_role, settings in _LOCAL_JUDGE_PROFILE_SPECS
    ]
    profiles.extend([
        {
            "id": "oss-cloud",
            "codex_profile": "oss-cloud",
            "provider": "codex",
            "mode": "cloud",
            "host": "codex-cli-profile",
            "model": "deepseek-v4-flash:cloud",
            "model_role": "cloud_confirmation",
            "model_settings": None,
            "runtime_metadata": None,
            "smoke_guard": None,
            "network_required": True,
            "secret_env_names": ["OLLAMA_API_KEY"],
            "auth_boundary": "codex_cli_auth",
            "receives_sanitized_outputs_only": True,
        },
        {
            "id": "codex-fast",
            "codex_profile": "fast",
            "provider": "codex",
            "mode": "codex-fast",
            "host": "codex-cli-authenticated-session",
            "model": "gpt-5.3-codex-spark",
            "model_role": "codex_fast_smoke",
            "model_settings": None,
            "runtime_metadata": None,
            "smoke_guard": None,
            "network_required": True,
            "secret_env_names": [],
            "auth_boundary": "codex_cli_auth",
            "receives_sanitized_outputs_only": True,
        },
    ])
    return profiles


def _local_judge_profile(
    profile_id: str,
    codex_profile: str,
    model: str,
    model_role: str,
    settings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": profile_id,
        "codex_profile": codex_profile,
        "provider": "codex",
        "mode": "local",
        "host": "codex-cli-profile",
        "model": model,
        "model_role": model_role,
        "model_settings": dict(settings),
        "runtime_metadata": _runtime_metadata_for_model(model),
        "smoke_guard": _smoke_guard_for_model(model),
        "network_required": True,
        "secret_env_names": [],
        "auth_boundary": "none",
        "receives_sanitized_outputs_only": True,
    }


def _runtime_metadata_for_model(model: str) -> dict[str, Any] | None:
    if model == "qwen3.5:9b-mlx":
        return dict(LOCAL_QWEN35_MLX_RUNTIME_METADATA)
    return None


def _smoke_guard_for_model(model: str) -> dict[str, Any] | None:
    if model == "qwen3.5:9b-mlx":
        return dict(LOCAL_QWEN35_SMOKE_GUARD)
    return None


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


def judge_profile_ids() -> tuple[str, ...]:
    return tuple(str(profile["id"]) for profile in _judge_profiles())


def codex_score_judge_profile_ids() -> tuple[str, ...]:
    supported_codex_profiles = {"oss-local", "oss-local-code", "oss-local-fallback", "oss-security", "oss-cloud"}
    return tuple(
        str(profile["id"])
        for profile in _judge_profiles()
        if profile["provider"] == "codex" and profile.get("codex_profile", profile["id"]) in supported_codex_profiles
    )


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
