from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from ask.envelope import CallResult


def _env_int(name: str, default: int = 0) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _phoenix_config(repo_root: Path) -> dict[str, Any]:
    config_path = repo_root / "Infrastructure" / "config" / "observability" / "phoenix.json"
    if not config_path.is_file():
        return {}
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _config_bool(config: dict[str, Any], key: str, default: bool = False) -> bool:
    value = config.get(key, default)
    return value is True or (isinstance(value, str) and value.lower() in {"1", "true", "yes", "on"})


def _config_str(config: dict[str, Any], key: str, default: str | None = None) -> str | None:
    value = config.get(key, default)
    return value if isinstance(value, str) and value else default


def _config_int(config: dict[str, Any], key: str, default: int = 0) -> int:
    value = config.get(key, default)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    return default


def _config_float(config: dict[str, Any], key: str, default: float) -> float:
    value = config.get(key, default)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return default
    return default


def _phoenix_trace_enabled(config: dict[str, Any]) -> bool:
    env_enabled = os.environ.get("ASK_PHOENIX_AUTO_TRACE")
    if env_enabled is not None:
        return env_enabled == "1"
    return _config_bool(config, "enabled", False)


def _is_phoenix_self_command(args: argparse.Namespace) -> bool:
    if getattr(args, "topic", None) != "sdk" or getattr(args, "action", None) != "observability":
        return False
    return str(getattr(args, "observability_action", "")).startswith("phoenix-")


def maybe_emit_phoenix_trace(repo_root: Path, args: argparse.Namespace, result: CallResult) -> None:
    config = _phoenix_config(repo_root)
    if not _phoenix_trace_enabled(config) or _is_phoenix_self_command(args):
        return
    try:
        _emit_phoenix_trace(repo_root, config, result)
    except (ImportError, KeyError, OSError, TypeError, ValueError) as exc:
        result.telemetry["phoenix_trace_status"] = "blocked"
        result.telemetry["phoenix_trace_error_class"] = type(exc).__name__


def _emit_phoenix_trace(repo_root: Path, config: dict[str, Any], result: CallResult) -> None:
    from ask.skills_sdk.phoenix_observability import emit_ask_result_to_phoenix

    receipt = emit_ask_result_to_phoenix(
        repo_root,
        command_name=str(result.metadata.get("command") or "unknown"),
        command_status=result.status,
        latency_ms=int(result.telemetry.get("latency_ms", 0)) if result.telemetry.get("latency_ms") is not None else None,
        base_url=os.environ.get("ASK_PHOENIX_BASE_URL") or _config_str(config, "base_url", "http://localhost:6006") or "http://localhost:6006",
        profile=os.environ.get("ASK_PHOENIX_PROFILE") or _config_str(config, "profile", "oss-local") or "oss-local",
        otel_python_path=os.environ.get("ASK_PHOENIX_OTEL_PYTHON") or _config_str(config, "otel_python") or None,
        model_name=os.environ.get("ASK_PHOENIX_MODEL") or _config_str(config, "model") or None,
        provider=os.environ.get("ASK_PHOENIX_PROVIDER") or _config_str(config, "provider") or None,
        prompt_tokens=_env_int("ASK_PHOENIX_PROMPT_TOKENS", _config_int(config, "prompt_tokens", 0)),
        completion_tokens=_env_int("ASK_PHOENIX_COMPLETION_TOKENS", _config_int(config, "completion_tokens", 0)),
        timeout_seconds=_env_float("ASK_PHOENIX_TIMEOUT_SECONDS", _config_float(config, "timeout_seconds", 2.0)),
    )
    result.telemetry["phoenix_trace_status"] = receipt["status"]
    result.telemetry["phoenix_trace_id"] = receipt["trace_id"]
    result.telemetry["phoenix_span_name"] = receipt["span_name"]
