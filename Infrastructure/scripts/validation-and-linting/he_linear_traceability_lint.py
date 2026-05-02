#!/usr/bin/env python3
"""Lint Harness Engineering Linear traceability blocks in markdown artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ISSUE_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
REQUIRED_PLAN_COLUMNS = (
    "Linear issue",
    "Source acceptance IDs",
    "Plan units",
    "Acceptance IDs",
    "PR evidence",
)
REQUIRED_SPEC_COLUMNS = (
    "Linear issue",
    "Acceptance IDs",
)
REQUIRED_PR_COLUMNS = (
    "Linear issue",
    "Acceptance IDs",
    "Validation",
)


@dataclass(frozen=True)
class LintResult:
    path: Path
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


def _extract_frontmatter(markdown: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(markdown)
    if match is None:
        return {}

    fields: dict[str, str] = {}
    for line in match.group("body").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def _has_heading(markdown: str, heading: str) -> bool:
    escaped = re.escape(heading)
    return re.search(rf"^#+\s+(?:\d+(?:\.\d+)*\s+)?{escaped}\s*$", markdown, re.MULTILINE) is not None


def _has_any_heading(markdown: str, headings: tuple[str, ...]) -> bool:
    return any(_has_heading(markdown, heading) for heading in headings)


def _heading_level(line: str) -> int | None:
    match = re.match(r"^(#+)\s+", line)
    return len(match.group(1)) if match else None


def _section_lines(markdown: str, heading: str) -> list[str]:
    escaped = re.escape(heading)
    heading_re = re.compile(rf"^(?P<marks>#+)\s+(?:\d+(?:\.\d+)*\s+)?{escaped}\s*$")
    lines = markdown.splitlines()
    section_start: int | None = None
    section_level: int | None = None
    for index, line in enumerate(lines):
        match = heading_re.match(line)
        if match:
            section_start = index + 1
            section_level = len(match.group("marks"))
            break

    if section_start is None or section_level is None:
        return []

    section: list[str] = []
    for line in lines[section_start:]:
        next_level = _heading_level(line)
        if next_level is not None and next_level <= section_level:
            break
        section.append(line)
    return section


def _split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    return all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def _first_table(section_lines: list[str]) -> tuple[list[str], list[list[str]]] | None:
    table_lines: list[str] = []
    for line in section_lines:
        if line.lstrip().startswith("|"):
            table_lines.append(line)
            continue
        if table_lines:
            break

    if len(table_lines) < 2:
        return None

    header = _split_table_row(table_lines[0])
    rows = [_split_table_row(line) for line in table_lines[1:]]
    rows = [row for row in rows if len(row) == len(header) and not _is_separator_row(row)]
    return header, rows


def _validate_traceability_table(
    markdown: str,
    heading: str,
    required_columns: tuple[str, ...],
    expected_issue: str,
) -> list[str]:
    errors: list[str] = []
    table = _first_table(_section_lines(markdown, heading))
    if table is None:
        return [f"{heading} section must include a markdown table"]

    header, rows = table
    missing_columns = [column for column in required_columns if column not in header]
    if missing_columns:
        missing = ", ".join(missing_columns)
        errors.append(f"{heading} table must include columns: {missing}")
        return errors

    if not rows:
        errors.append(f"{heading} table must include at least one data row")
        return errors

    issue_column = header.index("Linear issue")
    matching_issue_rows = []
    for row in rows:
        if issue_column >= len(row):
            continue
        issue_keys = set(ISSUE_KEY_RE.findall(row[issue_column]))
        if expected_issue in issue_keys:
            matching_issue_rows.append(row)
    if not matching_issue_rows:
        errors.append(f"{heading} table must include a row for frontmatter linear_issue {expected_issue}")

    return errors


def _traceability_required(frontmatter: dict[str, str], markdown: str) -> bool:
    if frontmatter.get("traceability_required", "").lower() == "true":
        return True
    return _has_any_heading(
        markdown,
        (
            "Linear Work Item Contract",
            "Linear / Spec / Plan / PR Traceability",
            "Linear Acceptance Traceability",
            "PR Traceability",
        ),
    )


def lint_markdown(path: Path, markdown: str) -> LintResult:
    frontmatter = _extract_frontmatter(markdown)
    errors: list[str] = []

    if not _traceability_required(frontmatter, markdown):
        return LintResult(path=path, errors=())

    linear_issue = frontmatter.get("linear_issue", "")
    linear_issue_match = ISSUE_KEY_RE.search(linear_issue)
    if not linear_issue_match:
        errors.append("frontmatter linear_issue must contain a Linear issue key like JSC-224")
    expected_issue = linear_issue_match.group(0) if linear_issue_match else ""

    if not frontmatter.get("linear_status"):
        errors.append("frontmatter linear_status is required")

    if not _has_heading(markdown, "Linear Work Item Contract"):
        errors.append("missing 'Linear Work Item Contract' section")

    has_plan_trace = _has_heading(markdown, "Linear / Spec / Plan / PR Traceability")
    has_spec_trace = _has_heading(markdown, "Linear Acceptance Traceability")
    has_pr_trace = _has_heading(markdown, "PR Traceability")
    if not (has_plan_trace or has_spec_trace or has_pr_trace):
        errors.append("missing Linear traceability section")

    if has_plan_trace and expected_issue:
        errors.extend(
            _validate_traceability_table(
                markdown,
                "Linear / Spec / Plan / PR Traceability",
                REQUIRED_PLAN_COLUMNS,
                expected_issue,
            )
        )

    if has_spec_trace and expected_issue:
        errors.extend(
            _validate_traceability_table(
                markdown,
                "Linear Acceptance Traceability",
                REQUIRED_SPEC_COLUMNS,
                expected_issue,
            )
        )

    if has_pr_trace and expected_issue:
        errors.extend(
            _validate_traceability_table(
                markdown,
                "PR Traceability",
                REQUIRED_PR_COLUMNS,
                expected_issue,
            )
        )

    body = FRONTMATTER_RE.sub("", markdown, count=1)
    if expected_issue and expected_issue not in body:
        errors.append(f"artifact body must include frontmatter linear_issue {expected_issue}")

    return LintResult(path=path, errors=tuple(errors))


def lint_path(path: Path) -> LintResult:
    return lint_markdown(path, path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="he-linear-traceability-lint",
        description="Validate Linear/spec/plan/PR traceability in Harness Engineering markdown artifacts.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown plan, spec, or PR body paths")
    args = parser.parse_args(argv)

    failed = False
    for path in args.paths:
        result = lint_path(path)
        if result.passed:
            print(f"PASS {path}")
            continue

        failed = True
        print(f"FAIL {path}")
        for error in result.errors:
            print(f"  - {error}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
