#!/usr/bin/env python3
"""Shared template render/drift helpers for skill-factory skills."""

from __future__ import annotations

import difflib
import json
import re
from pathlib import Path
from typing import Pattern

PLACEHOLDER_PATTERN: Pattern[str] = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")
CONTEXT_KEY_PATTERN: Pattern[str] = re.compile(r"^[A-Z0-9_]+$")


class TemplateRenderError(RuntimeError):
    """Raised when template rendering fails."""


def parse_key_value(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise TemplateRenderError("Invalid --var value. Expected KEY=VALUE.")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise TemplateRenderError("Invalid --var value. KEY cannot be empty.")
    if not CONTEXT_KEY_PATTERN.match(key):
        raise TemplateRenderError(
            "Invalid --var key. Expected uppercase KEY with only A-Z, 0-9, and underscore."
        )
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
    context = {str(key): str(value) for key, value in payload.items()}
    _validate_context_keys(context.keys(), source=f"JSON context {path}")
    return context


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
    _validate_context_keys(context.keys(), source="template context")
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
    if max_diff_lines < 0:
        raise TemplateRenderError("max_diff_lines must be non-negative.")
    for line in diff_lines[:max_diff_lines]:
        print(line)
    if len(diff_lines) > max_diff_lines:
        print(f"... truncated {len(diff_lines) - max_diff_lines} diff lines ...")


def _validate_context_keys(keys: list[str] | tuple[str, ...] | set[str], *, source: str) -> None:
    invalid = sorted({key for key in keys if not CONTEXT_KEY_PATTERN.match(str(key))})
    if invalid:
        raise TemplateRenderError(
            f"{source} contains invalid keys {invalid}; expected uppercase KEY names with A-Z, 0-9, and underscore."
        )
