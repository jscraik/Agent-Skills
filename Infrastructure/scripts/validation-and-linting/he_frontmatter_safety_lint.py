#!/usr/bin/env python3
"""Check parser-safe YAML frontmatter for Harness Engineering markdown artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)
DATE_PREFIX_RE = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})[-_]")
H1_RE = re.compile(r"^# (?P<title>.+)$", re.MULTILINE)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TRACEABLE_ROOTS = {
    "brainstorm",
    "specs",
    "plan",
    "evals",
    "review",
    "solutions",
    "ideate",
    "linear",
}


@dataclass(frozen=True)
class LintResult:
    path: Path
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors


def _candidate_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*.md") if p.is_file()))
        elif path.is_file():
            files.append(path)
        else:
            files.extend(sorted(Path().glob(path.as_posix())))
    return files


def _harness_root(path: Path) -> str | None:
    parts = path.as_posix().split("/")
    try:
        index = parts.index(".harness")
    except ValueError:
        return None
    if index + 1 >= len(parts):
        return None
    return parts[index + 1]


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _parse_frontmatter(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in body.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#") or line.startswith("  - "):
            continue
        if line.startswith((" ", "-")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = _strip_quotes(value.strip())
    return fields


def _unsafe_unquoted_scalar(value: str) -> bool:
    stripped = value.strip()
    if not stripped or stripped.startswith(("'", '"', "[", "{", "|", ">")):
        return False
    return any(token in stripped for token in (" #", ": ", "[", "]", "{", "}", ", "))


def lint_markdown(path: Path, markdown: str) -> LintResult:
    errors: list[str] = []
    match = FRONTMATTER_RE.match(markdown)
    if match is None:
        return LintResult(path, ("missing or malformed opening YAML frontmatter block",))

    body = match.group("body")
    fields = _parse_frontmatter(body)
    harness_root = _harness_root(path)
    traceable = harness_root in TRACEABLE_ROOTS

    if markdown.count("\n---\n") < 1:
        errors.append("frontmatter closing delimiter is missing")

    for line_number, raw_line in enumerate(body.splitlines(), start=2):
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#") or line.startswith((" ", "-")):
            continue
        if ":" not in line:
            errors.append(f"frontmatter line {line_number} is not key: value")
            continue
        key, value = line.split(":", 1)
        if not key.strip():
            errors.append(f"frontmatter line {line_number} has an empty key")
        if _unsafe_unquoted_scalar(value):
            errors.append(
                f"frontmatter line {line_number} value should be quoted for parser safety"
            )

    if traceable:
        for field in ("canonical_slug", "title", "date"):
            if not fields.get(field):
                errors.append(f"traceable .harness artifact needs frontmatter {field}")

    canonical_slug = fields.get("canonical_slug", "")
    if canonical_slug and not SLUG_RE.fullmatch(canonical_slug):
        errors.append("canonical_slug must be lowercase kebab-case")

    date_match = DATE_PREFIX_RE.match(path.name)
    if date_match and fields.get("date") != date_match.group("date"):
        errors.append("date-prefixed filename must match frontmatter date")

    title = fields.get("title")
    h1_match = H1_RE.search(FRONTMATTER_RE.sub("", markdown, count=1))
    if title:
        if h1_match is None:
            errors.append("frontmatter title requires a matching first H1")
        elif title != h1_match.group("title").strip():
            errors.append("frontmatter title must match the first H1 exactly")

    return LintResult(path, tuple(errors))


def lint_path(path: Path) -> LintResult:
    return lint_markdown(path, path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="he-frontmatter-safety-lint",
        description="Validate parser-safe frontmatter on Harness Engineering markdown artifacts.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    args = parser.parse_args(argv)

    files = _candidate_files(args.paths)
    if not files:
        print("FAIL no markdown files matched")
        return 1

    failed = False
    for path in files:
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
