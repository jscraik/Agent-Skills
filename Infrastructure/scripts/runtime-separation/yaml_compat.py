"""Small YAML compatibility loader for runtime-separation governance files."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _strip_comment(line: str) -> str:
    in_quote: str | None = None
    for index, char in enumerate(line):
        if char in {"'", '"'}:
            in_quote = None if in_quote == char else char
        if char == "#" and in_quote is None:
            return line[:index]
    return line


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) >= 2:
        return value[1:-1]
    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return int(value)
    return value


def _tokenize(text: str) -> list[tuple[int, str]]:
    tokens: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        without_comment = _strip_comment(raw_line).rstrip()
        if not without_comment.strip():
            continue
        indent = len(without_comment) - len(without_comment.lstrip(" "))
        tokens.append((indent, without_comment.strip()))
    return tokens


def _parse_key_value(content: str) -> tuple[str, Any] | tuple[str, None]:
    if ":" not in content:
        raise ValueError(f"unsupported YAML mapping line: {content!r}")
    key, raw_value = content.split(":", 1)
    key = key.strip()
    value = raw_value.strip()
    if not key:
        raise ValueError(f"empty YAML mapping key: {content!r}")
    return (key, _parse_scalar(value)) if value else (key, None)


def _parse_block(tokens: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(tokens):
        return {}, index
    current_indent, content = tokens[index]
    if current_indent < indent:
        return {}, index
    if content.startswith("-"):
        return _parse_list(tokens, index, current_indent)
    return _parse_mapping(tokens, index, current_indent)


def _parse_list(tokens: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    while index < len(tokens):
        current_indent, content = tokens[index]
        if current_indent != indent or not content.startswith("-"):
            break
        rest = content[1:].strip()
        index += 1
        if not rest:
            if index < len(tokens) and tokens[index][0] > current_indent:
                value, index = _parse_block(tokens, index, tokens[index][0])
            else:
                value = {}
            items.append(value)
            continue
        if ":" in rest:
            key, value = _parse_key_value(rest)
            item: dict[str, Any] = {}
            if value is None:
                if index < len(tokens) and tokens[index][0] > current_indent:
                    value, index = _parse_block(tokens, index, tokens[index][0])
                else:
                    value = {}
            item[key] = value
            if index < len(tokens) and tokens[index][0] > current_indent:
                extra, index = _parse_mapping(tokens, index, tokens[index][0], item)
                item = extra
            items.append(item)
            continue
        items.append(_parse_scalar(rest))
    return items, index


def _parse_mapping(
    tokens: list[tuple[int, str]],
    index: int,
    indent: int,
    initial: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], int]:
    mapping = dict(initial or {})
    while index < len(tokens):
        current_indent, content = tokens[index]
        if current_indent < indent or content.startswith("-"):
            break
        if current_indent > indent:
            raise ValueError(f"unexpected indentation before line: {content!r}")
        key, value = _parse_key_value(content)
        index += 1
        if value is None:
            if index < len(tokens) and tokens[index][0] > current_indent:
                value, index = _parse_block(tokens, index, tokens[index][0])
            else:
                value = {}
        mapping[key] = value
    return mapping, index


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load repo-owned YAML mappings when PyYAML is unavailable."""
    tokens = _tokenize(path.read_text(encoding="utf-8"))
    payload, index = _parse_block(tokens, 0, tokens[0][0] if tokens else 0)
    if index != len(tokens):
        raise ValueError(f"unsupported trailing YAML content in {path}")
    if not isinstance(payload, dict):
        raise ValueError(f"YAML root must be mapping: {path}")
    return payload
