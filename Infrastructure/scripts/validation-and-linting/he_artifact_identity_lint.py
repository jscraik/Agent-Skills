#!/usr/bin/env python3
"""Validate Harness Engineering markdown artifact identity fields."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
ISSUE_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]+-\d+\b")
DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})[-_]")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STAGE_BY_ROOT = {
    "brainstorm": "he-brainstorm",
    "specs": "he-spec",
    "plan": "he-plan",
    "evals": "he-eval-report",
    "review": "he-code-review",
    "solutions": "he-compound",
}
REQUIRED_FIELDS = (
    "schema_version",
    "artifact_id",
    "artifact_type",
    "canonical_slug",
    "title",
    "harness_stage",
    "status",
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


def _first_h1(markdown: str) -> str:
    body = FRONTMATTER_RE.sub("", markdown, count=1)
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _harness_root(path: Path) -> str | None:
    parts = path.as_posix().split("/")
    try:
        index = parts.index(".harness")
    except ValueError:
        return None
    if index + 1 >= len(parts):
        return None
    return parts[index + 1]


def lint_markdown(path: Path, markdown: str) -> LintResult:
    frontmatter = _extract_frontmatter(markdown)
    errors: list[str] = []

    if not frontmatter:
        return LintResult(path, ("missing YAML frontmatter",))

    for field in REQUIRED_FIELDS:
        if not frontmatter.get(field):
            errors.append(f"frontmatter {field} is required")

    artifact_id = frontmatter.get("artifact_id", "")
    canonical_slug = frontmatter.get("canonical_slug", "")
    title = frontmatter.get("title", "")
    date = frontmatter.get("date", "")
    h1 = _first_h1(markdown)
    harness_stage = frontmatter.get("harness_stage", "")
    artifact_type = frontmatter.get("artifact_type", "")
    traceability_required = frontmatter.get("traceability_required", "").lower() == "true"
    linear_issue = frontmatter.get("linear_issue", "")

    for field_name, value in (("artifact_id", artifact_id), ("canonical_slug", canonical_slug)):
        if value and not SLUG_RE.fullmatch(value):
            errors.append(f"frontmatter {field_name} must be a lowercase kebab-case slug")

    if artifact_id and canonical_slug and canonical_slug not in artifact_id:
        errors.append("frontmatter artifact_id must contain canonical_slug")

    if title and h1 and title != h1:
        errors.append("frontmatter title must match the first H1 heading")
    elif title and not h1:
        errors.append("artifact must include a first H1 heading matching frontmatter title")

    expected_stage = STAGE_BY_ROOT.get(_harness_root(path) or "")
    if expected_stage and harness_stage and harness_stage != expected_stage:
        errors.append(f"frontmatter harness_stage must be {expected_stage} for this .harness root")

    if expected_stage and artifact_type and expected_stage not in artifact_type:
        errors.append("frontmatter artifact_type must include the owning harness_stage")

    path_stem = path.stem.lower()
    if canonical_slug and canonical_slug not in path_stem:
        errors.append("filename stem must contain canonical_slug")

    date_match = DATE_PREFIX_RE.match(path.name)
    if date_match and date != date_match.group("date"):
        errors.append("date-prefixed filenames must have matching frontmatter date")

    issue_match = ISSUE_KEY_RE.search(linear_issue)
    if issue_match and canonical_slug:
        issue_slug = issue_match.group(0).lower()
        title_uses_issue = title.lower().startswith(issue_slug)
        if (issue_slug in path_stem or issue_slug in artifact_id or title_uses_issue) and issue_slug not in canonical_slug:
            errors.append("frontmatter canonical_slug must include lower-case linear_issue")

    if traceability_required:
        linear_milestone = frontmatter.get("linear_milestone", "")
        if not issue_match and not linear_milestone:
            errors.append("traceability_required artifacts need linear_issue or linear_milestone")
        if not (frontmatter.get("origin") or frontmatter.get("source_artifacts")):
            errors.append("traceability_required artifacts need origin or source_artifacts")

    return LintResult(path=path, errors=tuple(errors))


def lint_path(path: Path) -> LintResult:
    return lint_markdown(path, path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="he-artifact-identity-lint",
        description="Validate stable identity metadata for Harness Engineering markdown artifacts.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Harness markdown artifact paths")
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
    raise SystemExit(main(sys.argv[1:]))
