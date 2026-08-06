"""Markdown-only helpers for deterministic authoring-contract checks."""

from __future__ import annotations

import re


def normalized_text(value: str) -> str:
    return " ".join(value.casefold().split())


def without_fenced_content(text: str) -> str:
    lines: list[str] = []
    fence: str | None = None
    for raw_line in text.splitlines():
        marker = raw_line.lstrip()[:3]
        if marker in {"```", "~~~"}:
            fence = _next_fence(fence, marker)
        elif fence is None:
            lines.append(raw_line)
    return "\n".join(lines)


def level_two_heading_sections(text: str) -> tuple[dict[str, str], set[str]]:
    sections: dict[str, list[str]] = {}
    duplicates: set[str] = set()
    current: str | None = None
    for raw_line in without_fenced_content(text).splitlines():
        current = _collect_heading_line(raw_line, current, sections, duplicates)
    return {anchor: "\n".join(lines) for anchor, lines in sections.items()}, duplicates


def duplicate_nonempty_paragraphs(text: str) -> list[str]:
    paragraphs = _paragraphs_without_fences(text)
    seen: set[str] = set()
    duplicates: set[str] = set()
    for paragraph in paragraphs:
        if len(paragraph) < 12:
            continue
        if paragraph in seen:
            duplicates.add(paragraph)
        else:
            seen.add(paragraph)
    return sorted(duplicates)


def markdown_heading_position(text: str, heading: object) -> int | None:
    if not isinstance(heading, str) or not heading.strip():
        return None
    expected = normalized_text(heading)
    for index, actual in markdown_headings(text):
        if actual == expected:
            return index
    return None


def explicit_phase_headings(text: str) -> list[tuple[int, str]]:
    return [
        (index, title)
        for index, title in markdown_headings(text)
        if re.match(r"^(?:phase|stage)\s+\d+\b", title)
    ]


def markdown_headings(text: str) -> list[tuple[int, str]]:
    headings: list[tuple[int, str]] = []
    for index, line in enumerate(without_fenced_content(text).splitlines()):
        match = re.fullmatch(r"#{2,3}\s+(.+)", line.strip())
        if match:
            headings.append((index, normalized_text(match.group(1))))
    return headings


def _next_fence(current: str | None, marker: str) -> str | None:
    if current == marker:
        return None
    return marker if current is None else current


def _collect_heading_line(
    raw_line: str,
    current: str | None,
    sections: dict[str, list[str]],
    duplicates: set[str],
) -> str | None:
    line = raw_line.strip()
    match = re.fullmatch(r"##\s+(.+)", line)
    if match is not None:
        return _start_section(match.group(1), sections, duplicates)
    if line.startswith("#"):
        return None
    if current is not None:
        sections[current].append(raw_line)
    return current


def _start_section(
    title: str,
    sections: dict[str, list[str]],
    duplicates: set[str],
) -> str | None:
    anchor = re.sub(r"[^a-z0-9]+", "-", title.strip().casefold()).strip("-")
    if not anchor or anchor in sections:
        if anchor:
            duplicates.add(anchor)
        return None
    sections[anchor] = []
    return anchor


def _paragraphs_without_fences(text: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    fence: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith(("```", "~~~")):
            fence = _next_fence(fence, line[:3])
            current = []
            continue
        if fence is not None:
            continue
        if not line or line.startswith("#"):
            _append_paragraph(paragraphs, current)
            current = []
        else:
            current.append(line)
    _append_paragraph(paragraphs, current)
    return paragraphs


def _append_paragraph(paragraphs: list[str], lines: list[str]) -> None:
    if lines:
        paragraphs.append(normalized_text(" ".join(lines)))
