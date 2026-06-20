#!/usr/bin/env python3
"""Validate that a pull request body preserves the repository template shape."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SECTION_RE = re.compile(r"^## (?P<title>.+?)\s*$", re.MULTILINE)
CHECKBOX_RE = re.compile(r"^- \[[ xX]\] (?P<label>.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^- (?P<label>[^:\n]+):", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"<[^>\n]+>")


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
        match.group("label").strip()
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
        actual_fields = [match.group("label").strip() for match in FIELD_RE.finditer(block)]
        missing_fields = [field for field in expected_fields if field not in actual_fields]
        extra_fields = [field for field in actual_fields if field not in expected_fields]
        for field in missing_fields:
            errors.append(f"Missing required field in ## {section}: {field}:")
        for field in extra_fields:
            errors.append(f"Unexpected field in ## {section}: {field}:")
    return errors


def _checklist_labels(checklist_block: str) -> list[str]:
    return [match.group("label").strip() for match in CHECKBOX_RE.finditer(checklist_block)]


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
        if token in template_tokens:
            errors.append(f"Replace unresolved placeholder token: {token}")
    return errors


def validate_pr_body(template: str, body: str) -> list[str]:
    contract = _template_contract(template)
    if body.strip() == "":
        return ["PR body is empty. Fill out the full PR template."]

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
    args = parser.parse_args()

    template = args.template.read_text(encoding="utf-8")
    body = _body_from_args(args)
    errors = validate_pr_body(template, body)
    if errors:
        print("PR template validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PR template validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
