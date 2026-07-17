#!/usr/bin/env python3
"""Validate that a pull request body preserves the repository template shape."""

from __future__ import annotations

import argparse
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SECTION_RE = re.compile(r"^## (?P<title>.+?)\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^- \[[ xX]\] (?P<label>.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- (?P<label>[^:\n]+):", re.MULTILINE)
FIELD_LINE_RE = re.compile(r"^- (?P<label>[^:\n]+):(?P<value>.*)$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")
CHECKLIST_STATUS_RE = re.compile(r"^\*\*\((?:pending|n/a|not applicable)\)\*\*\s*", re.IGNORECASE)
ANGLE_BRACKET_URL_RE = re.compile(r"^<https?://[^>\s]+>$")
DEPENDABOT_GROUPED_HEADER_RE = re.compile(
    r"^Bumps the .+ group with \d+ update(?:s)? in the .+ directory: "
    r"\[[^\]]+\]\(https://github\.com/[^)\s]+\)"
    r"(?:\s*(?:,|and)\s*\[[^\]]+\]\(https://github\.com/[^)\s]+\))*\.$",
    re.IGNORECASE,
)
DEPENDABOT_SINGLE_HEADER_RE = re.compile(
    r"^Bumps \S+ from \S+ to \S+$",
    re.IGNORECASE,
)
DEPENDABOT_UPDATE_RE = re.compile(r"^Updates `[^`]+` from \S+ to \S+$", re.IGNORECASE)
SAFE_HTML_TAG_RE = re.compile(
    r"</?(?:a|abbr|b|blockquote|br|code|dd|del|details|div|dl|dt|em|h[1-6]|hr|i|img|ins|kbd|li|mark|ol|p|pre|s|samp|small|source|span|strong|sub|summary|sup|table|tbody|td|th|thead|time|tr|u|ul|var)"
    r"(?:\s+[^>\n]*)?\s*/?>",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class TemplateContract:
    sections: list[str]
    checklist_items: list[str]
    fields_by_section: dict[str, list[str]]


def _section_blocks(markdown: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(markdown))
    blocks: dict[str, str] = {}
    for index, match in enumerate(matches):
        title = match.group("title").strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        blocks[title] = markdown[start:end]
    return blocks


def _template_contract(template: str) -> TemplateContract:
    sections = [match.group("title").strip() for match in SECTION_RE.finditer(template)]
    blocks = _section_blocks(template)
    checklist_items = [
        _normalize_checklist_label(match.group("label"))
        for match in CHECKBOX_RE.finditer(blocks.get("Checklist", ""))
    ]
    fields_by_section: dict[str, list[str]] = {}
    for section, body in blocks.items():
        if section in {"Checklist", "Notes"}:
            continue
        fields = [match.group("label").strip() for match in FIELD_RE.finditer(body)]
        if fields:
            fields_by_section[section] = fields
    return TemplateContract(
        sections=sections,
        checklist_items=checklist_items,
        fields_by_section=fields_by_section,
    )


def _body_from_args(args: argparse.Namespace) -> str:
    if args.body_file is not None:
        return args.body_file.read_text(encoding="utf-8")
    if args.body_env is not None:
        return os.environ.get(args.body_env, "")
    return sys.stdin.read()


def _section_errors(contract: TemplateContract, body: str) -> list[str]:
    errors: list[str] = []
    body_sections = [match.group("title").strip() for match in SECTION_RE.finditer(body)]
    if body_sections != contract.sections:
        errors.append(
            "PR body sections must match .github/PULL_REQUEST_TEMPLATE.md exactly. "
            f"expected={contract.sections!r} actual={body_sections!r}"
        )

    body_blocks = _section_blocks(body)
    missing_sections = [section for section in contract.sections if section not in body_blocks]
    for section in missing_sections:
        errors.append(f"Missing required section: ## {section}")
    return errors


def _field_errors(contract: TemplateContract, body_blocks: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for section, expected_fields in contract.fields_by_section.items():
        block = body_blocks.get(section, "")
        field_values, field_counts = _field_values(block)
        expected_counts = Counter(expected_fields)
        actual_fields = list(field_values)
        missing_fields = [field for field, count in expected_counts.items() if field_counts.get(field, 0) < count]
        extra_fields = [field for field in actual_fields if field not in expected_fields]
        for field, count in field_counts.items():
            if field in expected_counts and count > expected_counts[field]:
                errors.append(f"Duplicate field in ## {section}: {field}:")
        for field in missing_fields:
            errors.append(f"Missing required field in ## {section}: {field}:")
        for field in extra_fields:
            errors.append(f"Unexpected field in ## {section}: {field}:")
        for field in expected_fields:
            if field in field_values and field_values[field] == "":
                errors.append(f"Required field in ## {section} is empty: {field}:")
    return errors


def _field_values(block: str) -> tuple[dict[str, str], Counter[str]]:
    matches = list(FIELD_LINE_RE.finditer(block))
    values: dict[str, str] = {}
    counts: Counter[str] = Counter()
    for index, match in enumerate(matches):
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(block)
        continuation = block[match.end():next_start].strip()
        label = match.group("label").strip()
        counts[label] += 1
        values[label] = f"{match.group('value').strip()}\n{continuation}".strip()
    return values, counts


def _normalize_checklist_label(label: str) -> str:
    return CHECKLIST_STATUS_RE.sub("", label.strip()).strip()


def _checklist_labels(checklist_block: str) -> list[str]:
    return [_normalize_checklist_label(match.group("label")) for match in CHECKBOX_RE.finditer(checklist_block)]


def _checklist_errors(contract: TemplateContract, body_blocks: dict[str, str]) -> list[str]:
    errors: list[str] = []
    checklist_block = body_blocks.get("Checklist", "")
    actual_checklist_items = _checklist_labels(checklist_block)
    if actual_checklist_items != contract.checklist_items:
        errors.append(
            "Checklist item text/order must match .github/PULL_REQUEST_TEMPLATE.md exactly. "
            f"expected={contract.checklist_items!r} actual={actual_checklist_items!r}"
        )
    errors.extend(_unchecked_checklist_errors(checklist_block))
    return errors


def _unchecked_checklist_errors(checklist_block: str) -> list[str]:
    unchecked = [
        match.group(0).strip()
        for match in CHECKBOX_RE.finditer(checklist_block)
        if match.group(0).startswith("- [ ]")
    ]
    unresolved_unchecked = [
        item
        for item in unchecked
        if not re.search(r"\*\*\((pending|n/a|not applicable)\)\*\*", item, re.IGNORECASE)
    ]
    return [
        "Checklist has unchecked item without explicit status marker ((Pending) or (N/A)): "
        f"{item}"
        for item in unresolved_unchecked
    ]


def _placeholder_errors(template: str, body: str) -> list[str]:
    template_tokens = set(PLACEHOLDER_RE.findall(template))
    placeholders = [
        "pass/fail",
        "Add one-paragraph merge rationale here.",
        "describe the observable behavior, issue, or n.a. reason",
        "list exact commands run here",
        "record pass/fail/blocked for each command here",
    ]
    errors: list[str] = []
    for placeholder in placeholders:
        if placeholder in body:
            errors.append(f"Replace template placeholder: {placeholder}")
    for token in PLACEHOLDER_RE.findall(body):
        if (
            token.startswith("<!--")
            or ANGLE_BRACKET_URL_RE.match(token)
            or (SAFE_HTML_TAG_RE.fullmatch(token) and "<" not in token[1:])
        ):
            continue
        if token in template_tokens or " " in token or "/" in token:
            errors.append(f"Replace unresolved placeholder token: {token}")
    return errors


def _dependabot_body_errors(body: str) -> list[str]:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    errors: list[str] = []
    if not lines or not _is_dependabot_header(lines[0]):
        errors.append("Dependabot body must start with its generated update summary.")
    if lines and DEPENDABOT_GROUPED_HEADER_RE.fullmatch(lines[0]) and (
        len(lines) < 2 or not DEPENDABOT_UPDATE_RE.fullmatch(lines[1])
    ):
        errors.append("Dependabot body must include its generated version update line.")
    if "Dependabot will resolve any conflicts with this PR" not in body:
        errors.append("Dependabot body is missing its generated conflict-resolution notice.")
    return errors


def _is_dependabot_header(line: str) -> bool:
    return bool(
        DEPENDABOT_GROUPED_HEADER_RE.fullmatch(line)
        or DEPENDABOT_SINGLE_HEADER_RE.fullmatch(line)
    )


def _is_dependabot_body(body: str) -> bool:
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    return bool(
        lines
        and _is_dependabot_header(lines[0])
        and "Dependabot will resolve any conflicts with this PR" in body
    )


def validate_pr_body(template: str, body: str, *, author: str | None = None) -> list[str]:
    contract = _template_contract(template)
    if body.strip() == "":
        return ["PR body is empty. Fill out the full PR template."]
    if _is_dependabot_body(body):
        if author not in {"dependabot[bot]", "dependabot"}:
            return ["Dependabot body exception requires the trusted Dependabot PR author."]
        return _dependabot_body_errors(body)

    body_blocks = _section_blocks(body)
    errors = _section_errors(contract, body)
    errors.extend(_field_errors(contract, body_blocks))
    errors.extend(_checklist_errors(contract, body_blocks))
    errors.extend(_placeholder_errors(template, body))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--template",
        type=Path,
        default=Path(".github/PULL_REQUEST_TEMPLATE.md"),
        help="Path to the canonical pull request template.",
    )
    body_group = parser.add_mutually_exclusive_group()
    body_group.add_argument("--body-file", type=Path, help="Path containing the PR body.")
    body_group.add_argument("--body-env", help="Environment variable containing the PR body.")
    parser.add_argument(
        "--author",
        default=None,
        help="Trusted pull-request author login; Dependabot exceptions require dependabot[bot].",
    )
    args = parser.parse_args()

    template = args.template.read_text(encoding="utf-8")
    body = _body_from_args(args)
    errors = validate_pr_body(template, body, author=args.author or os.environ.get("PR_AUTHOR"))
    if errors:
        print("PR template validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PR template validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
