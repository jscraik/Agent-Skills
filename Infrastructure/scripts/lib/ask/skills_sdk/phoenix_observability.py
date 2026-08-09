"""Public Phoenix receipt facade.

Schema constants and redaction helpers live in ``phoenix_observability_support``;
receipt builders live in ``phoenix_observability_receipts``.  Keep this module
small so callers retain one stable import surface without hiding shape debt.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ask.skills_sdk.phoenix_observability_receipts import (
    build_phoenix_eval_trace_receipt,
    build_phoenix_mirror_receipt,
    build_phoenix_smoke_receipt,
    build_phoenix_status_receipt,
)
from ask.skills_sdk.phoenix_observability_support import (
    PHOENIX_ACCEPTANCE_TRACE,
    PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT,
    PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT,
    PHOENIX_EVAL_TRACE_SCHEMA_URI,
    PHOENIX_EVAL_TRACE_SCHEMA_VERSION,
    PHOENIX_MIRROR_SCHEMA_URI,
    PHOENIX_MIRROR_SCHEMA_VERSION,
    PHOENIX_SMOKE_SCHEMA_URI,
    PHOENIX_SMOKE_SCHEMA_VERSION,
    PHOENIX_STATUS_SCHEMA_URI,
    PHOENIX_STATUS_SCHEMA_VERSION,
    OSS_CODEX_PROFILES,
    SUPPORTED_SOURCE_KINDS,
    PhoenixObservabilityError,
)


def emit_ask_result_to_phoenix(
    repo_root: Path,
    *,
    command_name: str,
    command_status: str,
    latency_ms: int | None,
    base_url: str,
    profile: str,
    otel_python_path: str | None = None,
    model_name: str | None = None,
    provider: str | None = None,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    timeout_seconds: float = 2.0,
) -> dict[str, Any]:
    """Emit the stable command-level observability receipt."""
    return build_phoenix_smoke_receipt(
        repo_root,
        base_url=base_url,
        profile=profile,
        timeout_seconds=timeout_seconds,
        otel_python_path=otel_python_path,
        model_name=model_name,
        provider=provider,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        command_name=command_name,
        command_status=command_status,
        latency_ms=latency_ms,
    )


__all__ = [
    "OSS_CODEX_PROFILES",
    "PHOENIX_ACCEPTANCE_TRACE",
    "PHOENIX_EVAL_TRACE_DEFAULT_CASE_SPAN_LIMIT",
    "PHOENIX_EVAL_TRACE_MAX_CASE_SPAN_LIMIT",
    "PHOENIX_EVAL_TRACE_SCHEMA_URI",
    "PHOENIX_EVAL_TRACE_SCHEMA_VERSION",
    "PHOENIX_MIRROR_SCHEMA_URI",
    "PHOENIX_MIRROR_SCHEMA_VERSION",
    "PHOENIX_SMOKE_SCHEMA_URI",
    "PHOENIX_SMOKE_SCHEMA_VERSION",
    "PHOENIX_STATUS_SCHEMA_URI",
    "PHOENIX_STATUS_SCHEMA_VERSION",
    "SUPPORTED_SOURCE_KINDS",
    "PhoenixObservabilityError",
    "build_phoenix_eval_trace_receipt",
    "build_phoenix_mirror_receipt",
    "build_phoenix_smoke_receipt",
    "build_phoenix_status_receipt",
    "emit_ask_result_to_phoenix",
]
