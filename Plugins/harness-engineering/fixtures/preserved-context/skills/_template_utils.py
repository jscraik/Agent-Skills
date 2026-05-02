#!/usr/bin/env python3
"""Shared template render/drift helpers for harness-engineering skills."""

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
    """
    Parse a KEY=VALUE string into its key and value components.

    Parameters:
        raw (str): Input string expected in the form "KEY=VALUE".

    Returns:
        tuple[str, str]: A (key, value) pair where `key` is trimmed of surrounding whitespace.

    Raises:
        TemplateRenderError: If the input does not contain "=", or if the key (left side) is empty.
    """
    if "=" not in raw:
        raise TemplateRenderError(f"Invalid --var value {raw}. Expected KEY=VALUE.")
    key, value = raw.split("=", 1)
    key = key.strip()
    if not key:
        raise TemplateRenderError(f"Invalid --var value {raw}. KEY cannot be empty.")
    return key, value


def load_json_context(path: Path) -> dict[str, str]:
    """
    Load a JSON file and return its contents as a flat dict of strings.

    Reads the file at `path`, parses it as JSON, and coerces all top-level keys and values to strings.
    Raises TemplateRenderError if the file cannot be read, if the JSON is invalid, or if the decoded
    JSON is not an object (mapping).

    Parameters:
        path (Path): Filesystem path to a JSON file containing an object of key/value pairs.

    Returns:
        dict[str, str]: A dictionary mapping each top-level key to its stringified value.
    """
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
    """
    Builds a merged rendering context from default, JSON, and CLI sources.

    default_context (dict[str, str]): Default key/value pairs to include when `use_defaults` is True.
    use_defaults (bool): If True, start with `default_context`; otherwise ignore it.
    json_context (dict[str, str]): Key/value pairs loaded from a JSON context file; these override defaults.
    cli_context (dict[str, str]): Key/value pairs provided via the CLI; these override both JSON and defaults.

    Returns:
        dict[str, str]: The merged context where later sources take precedence (CLI > JSON > defaults when defaults are used).
    """
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
    """
    Render a template by replacing {{ KEY }} placeholders with values from the provided context.

    Parameters:
        template_text (str): Template content containing placeholders of the form `{{ KEY }}`.
        context (dict[str, str]): Mapping of placeholder keys to replacement strings.
        placeholder_pattern (Pattern[str], optional): Regular expression used to locate placeholders (defaults to `PLACEHOLDER_PATTERN`).

    Returns:
        str: The rendered template with placeholders substituted by their corresponding context values.

    Raises:
        TemplateRenderError: If one or more placeholders in the template have no corresponding key in `context`; the error message lists the missing keys.
    """
    missing: list[str] = []

    def replacement(match: re.Match[str]) -> str:
        """
        Produce the replacement text for a regex placeholder match using the surrounding `context`.

        Parameters:
            match (re.Match[str]): A regex match whose group(1) is the placeholder key.

        Returns:
            str: The context value for the matched key if present; otherwise the original matched text.

        Notes:
            If the key is not found in `context`, the key is appended to the outer-scope `missing` list as a side effect.
        """
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
    """
    Render a template file using the provided context and return the resulting text.

    Parameters:
        template_path (Path): Path to the template file to read using UTF-8 encoding.
        context (dict[str, str]): Mapping of placeholder keys to replacement strings.
        placeholder_pattern (Pattern[str]): Regex pattern used to identify placeholders in the template.

    Returns:
        str: The rendered template text with placeholders replaced by their context values.

    Raises:
        TemplateRenderError: If the template file cannot be read or if rendering fails (for example, due to missing placeholders).
    """
    try:
        template_text = template_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TemplateRenderError(f"Failed to read template {template_path}: {exc}") from exc
    return render_template(template_text, context, placeholder_pattern=placeholder_pattern)


def ensure_trailing_newline(text: str) -> str:
    """
    Ensure the given text ends with a newline character.

    Parameters:
        text (str): Input text to normalize.

    Returns:
        str: The input text, with a trailing `\n` appended if it did not already end with one.
    """
    return text if text.endswith("\n") else text + "\n"


def unified_diff_lines(
    *,
    actual_text: str,
    expected_text: str,
    output_path: Path,
    template_path: Path,
) -> list[str]:
    """
    Generate unified diff lines comparing the actual text to the expected text.

    Each returned string is a single line from a unified diff (no trailing newline characters).
    The diff headers use `fromfile` set to the string form of `output_path` and `tofile` set to `rendered(<template_path>)`.

    Parameters:
        actual_text (str): The existing or "from" content.
        expected_text (str): The desired or "to" content.
        output_path (Path): Path displayed as the `fromfile` header in the diff.
        template_path (Path): Path displayed (wrapped as `rendered(...)`) as the `tofile` header in the diff.

    Returns:
        list[str]: Unified diff lines between `actual_text` and `expected_text`, with lines returned without trailing line terminators.
    """
    return list(
        difflib.unified_diff(
            actual_text.splitlines(keepends=True),
            expected_text.splitlines(keepends=True),
            fromfile=str(output_path),
            tofile=f"rendered({template_path})",
            lineterm="",
        )
    )


def print_diff_lines(diff_lines: list[str], *, max_diff_lines: int) -> None:
    """
    Print a unified diff to stdout limited to a maximum number of lines.

    Prints each line from `diff_lines` up to `max_diff_lines`. If `diff_lines` contains more lines than `max_diff_lines`, prints a final truncation message indicating how many lines were omitted.

    Parameters:
        diff_lines (list[str]): The diff lines to print.
        max_diff_lines (int): Maximum number of diff lines to print before truncating.
    """
    for line in diff_lines[:max_diff_lines]:
        print(line)
    if len(diff_lines) > max_diff_lines:
        print(f"... truncated {len(diff_lines) - max_diff_lines} diff lines ...")
