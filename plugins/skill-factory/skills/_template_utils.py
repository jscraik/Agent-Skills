#!/usr/bin/env python3
"""Shared template render/drift helpers for skill-factory skills."""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Pattern

PLACEHOLDER_PATTERN: Pattern[str] = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")


class TemplateRenderError(RuntimeError):
    """Raised when template rendering fails."""


def parse_key_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise TemplateRenderError(f"Invalid --var value {raw}. Expected KEY=VALUE.")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise TemplateRenderError(f"Invalid --var value {raw}. KEY cannot be empty.")
    return key, value


def load_json_context(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TemplateRenderError(f"Failed to read context JSON {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TemplateRenderError(f"Failed to parse JSON context {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise TemplateRenderError(f"JSON context {path} must decode to an object.")
    return {str(key): str(value) for key, value in payload.items()}


def build_context(
    *,
    default_context: dict[str, str],
    use_defaults: bool,
    json_context: dict[str, str],
    cli_context: dict[str, str],
) -> dict[str, str]:
    context: dict[str, str] = {}
    if use_defaults:
        context.update(default_context)
    context.update(json_context)
    context.update(cli_context)
    return context


def render_template(
    template_text: str,
    context: dict[str, str],
    *,
    placeholder_pattern: Pattern[str] = PLACEHOLDER_PATTERN,
) -> str:
    missing: list[str] = []

    def replacement(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            missing.append(key)
            return match.group(0)
        return context[key]

    rendered = placeholder_pattern.sub(replacement, template_text)
    if missing:
        missing_keys = ", ".join(sorted(set(missing)))
        raise TemplateRenderError(f"Missing template variables: {missing_keys}")
    return rendered


def render_from_path(
    *,
    template_path: Path,
    context: dict[str, str],
    placeholder_pattern: Pattern[str] = PLACEHOLDER_PATTERN,
) -> str:
    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TemplateRenderError(f"Failed to read template {template_path}: {exc}") from exc
    return render_template(template_text, context, placeholder_pattern=placeholder_pattern)


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def unified_diff_lines(
    *,
    actual_text: str,
    expected_text: str,
    output_path: Path,
    template_path: Path,
) -> list[str]:
    return list(
        difflib.unified_diff(
            actual_text.splitlines(),
            expected_text.splitlines(),
            fromfile=str(output_path),
            tofile=f"rendered({template_path})",
            lineterm="",
        )
    )


def print_diff_lines(diff_lines: list[str], *, max_diff_lines: int) -> None:
    for line in diff_lines[:max_diff_lines]:
        print(line)
    if len(diff_lines) > max_diff_lines:
        print(f"... truncated {len(diff_lines) - max_diff_lines} diff lines ...")
