from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ask.skills_sdk.eval_profiles import LOCAL_QWEN35_MLX_RUNTIME_METADATA


_LOCAL_CODEX_MODEL_CATALOG_BY_MODEL: dict[str, dict[str, Any]] = {
    "qwen3.5:9b-mlx": {
        "slug": "qwen3.5:9b-mlx",
        "display_name": "Qwen 3.5 9B MLX",
        "description": "Local Ollama qwen3.5:9b-mlx evaluator profile.",
        "default_reasoning_level": "none",
        "supported_reasoning_levels": [],
        "shell_type": "shell_command",
        "visibility": "list",
        "supported_in_api": False,
        "priority": 1,
        "additional_speed_tiers": [],
        "service_tiers": [],
        "availability_nux": None,
        "upgrade": None,
        "base_instructions": "",
        "model_messages": {},
        "supports_reasoning_summaries": False,
        "default_reasoning_summary": "none",
        "support_verbosity": False,
        "default_verbosity": "low",
        "apply_patch_tool_type": "freeform",
        "web_search_tool_type": "text",
        "truncation_policy": {"mode": "tokens", "limit": 10000},
        "supports_parallel_tool_calls": False,
        "supports_image_detail_original": False,
        "context_window": LOCAL_QWEN35_MLX_RUNTIME_METADATA["context_length"],
        "max_context_window": LOCAL_QWEN35_MLX_RUNTIME_METADATA["context_length"],
        "comp_hash": "local-qwen35-mlx",
        "effective_context_window_percent": 95,
        "experimental_supported_tools": [],
        "input_modalities": ["text"],
        "supports_search_tool": False,
        "use_responses_lite": False,
    }
}


def local_codex_catalog_entry(model: str | None) -> dict[str, Any] | None:
    if model is None:
        return None
    entry = _LOCAL_CODEX_MODEL_CATALOG_BY_MODEL.get(model)
    return None if entry is None else dict(entry)


def augment_local_codex_profile_config(profile_path: Path, model: str | None) -> Path | None:
    entry = local_codex_catalog_entry(model)
    if entry is None:
        return None
    catalog_path = profile_path.parent / "local-model-catalog.json"
    catalog_path.write_text(json.dumps({"models": [entry]}, sort_keys=True, indent=2), encoding="utf-8")
    _append_missing_profile_keys(
        profile_path,
        {
            "model_catalog_json": str(catalog_path),
            "model_context_window": entry["context_window"],
            "model_reasoning_summary": "none",
            "hide_agent_reasoning": True,
            "show_raw_agent_reasoning": False,
        },
    )
    return catalog_path


def _append_missing_profile_keys(profile_path: Path, keys: dict[str, object]) -> None:
    profile_text = profile_path.read_text(encoding="utf-8", errors="replace")
    existing_keys = {
        line.split("=", 1)[0].strip()
        for line in profile_text.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }
    additions: list[str] = []
    for key, value in keys.items():
        if key in existing_keys:
            continue
        additions.append(f"{key} = {_toml_value(value)}")
    if not additions:
        return
    separator = "" if profile_text.endswith("\n") or not profile_text else "\n"
    profile_path.write_text(profile_text + separator + "\n".join(additions) + "\n", encoding="utf-8")


def _toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    raise TypeError(f"Unsupported TOML value for local Codex catalog config: {value!r}")
