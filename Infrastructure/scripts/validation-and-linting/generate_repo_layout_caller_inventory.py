#!/usr/bin/env python3
"""Generate the Phase 1 caller inventory for root-layout migration."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

ROOT_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "Skills/": [re.compile(r"(?<![A-Za-z0-9_.-])Skills/")],
    "Plugins/": [re.compile(r"(?<![A-Za-z0-9_.-])Plugins/")],
    "plugins/": [re.compile(r"(?<![A-Za-z0-9_.-])plugins/")],
    "skills-system/": [re.compile(r"(?<![A-Za-z0-9_.-])skills-system/")],
    "Infrastructure/": [re.compile(r"(?<![A-Za-z0-9_.-])Infrastructure/")],
    "Docs/": [re.compile(r"(?<![A-Za-z0-9_.-])Docs/")],
    "artifacts/": [re.compile(r"(?<![A-Za-z0-9_.-])artifacts/")],
    "brand/": [re.compile(r"(?<![A-Za-z0-9_.-])brand/")],
    "scripts": [
        re.compile(r"(?<![A-Za-z0-9_.-])(?:\./)?scripts/"),
        re.compile(r"(?<![A-Za-z0-9_.-])['\"]scripts['\"]"),
    ],
    "GOVERNANCE": [re.compile(r"(?<![A-Za-z0-9_.-])GOVERNANCE(?![A-Za-z0-9_.-])")],
    "docs-policy.json": [re.compile(r"(?<![A-Za-z0-9_.-])docs-policy\.json(?![A-Za-z0-9_-])")],
}

TEXT_SUFFIXES = {
    ".bash",
    ".cfg",
    ".command",
    ".css",
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".mdx",
    ".mjs",
    ".py",
    ".rb",
    ".sh",
    ".swift",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}


@dataclass(frozen=True)
class Occurrence:
    legacy_root: str
    path: str
    line: int
    categories: tuple[str, ...]
    snippet: str

    def to_json(self) -> dict[str, Any]:
        return {
            "legacy_root": self.legacy_root,
            "path": self.path,
            "line": self.line,
            "categories": list(self.categories),
            "snippet": self.snippet,
        }


def _tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return sorted(line for line in result.stdout.splitlines() if line)


def _is_text_candidate(path: str) -> bool:
    path_obj = Path(path)
    if path_obj.name in {"Makefile", "justfile", "Dockerfile"}:
        return True
    if path_obj.suffix in TEXT_SUFFIXES:
        return True
    if "/" not in path and "." not in path:
        return True
    return False


def _read_text(path: Path) -> str | None:
    try:
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _classify_path(path: str) -> set[str]:
    suffix = Path(path).suffix
    name = Path(path).name
    rules = (
        ("ci_workflow", path.startswith(".github/workflows/") or path.startswith(".circleci/")),
        ("precommit_or_hook", "/hooks/" in path or path.startswith(".git-hooks/") or "pre-commit" in path),
        ("ask_cli_route", path.startswith("Infrastructure/scripts/lib/ask/") or path == "bin/ask"),
        ("test_fixture", path.startswith("Infrastructure/tests/") or "/tests/" in path or name.startswith("test_")),
        ("runtime_projection_input", path.startswith(".agents/") or path.startswith(".skillsets/")),
        ("generated_artifact_input", path.startswith(".harness/evidence/") or path.startswith("artifacts/")),
        ("docs_reference_link", suffix in {".md", ".mdx", ".html"} or path.startswith("Docs/") or path == "README.md"),
        ("internal_python_import", suffix == ".py"),
        ("shell_command", suffix in {".sh", ".command"} or name in {"Makefile", "justfile"}),
        ("external_operator_entrypoint", path in {"AGENTS.md", "README.md", "CONTRIBUTING.md", "WORKFLOW.md"}),
    )
    return {category for category, matched in rules if matched}


def _classify_line(line: str) -> set[str]:
    lowered = line.lower()
    rules = (
        ("tessl_staging_input", "tessl" in lowered),
        ("ask_cli_route", "./bin/ask" in line or " bin/ask" in line or "ask " in line),
        ("runtime_projection_input", "projection" in lowered or ".agents/" in line or ".skillsets/" in line),
        ("generated_artifact_input", "generate" in lowered or "generated" in lowered or "artifact" in lowered),
        ("ci_workflow", "github/workflows" in lowered or "circleci" in lowered),
    )
    return {category for category, matched in rules if matched}


def _matching_roots(line: str) -> list[str]:
    roots: list[str] = []
    for legacy_root, patterns in ROOT_PATTERNS.items():
        if any(pattern.search(line) for pattern in patterns):
            roots.append(legacy_root)
    return roots


def _scan_file(root: Path, rel_path: str) -> tuple[bool, list[Occurrence]]:
    if not _is_text_candidate(rel_path):
        return False, []
    text = _read_text(root / rel_path)
    if text is None:
        return False, []
    return True, _line_occurrences(rel_path, text)


def _line_occurrences(rel_path: str, text: str) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    path_categories = _classify_path(rel_path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        occurrences.extend(_line_root_occurrences(rel_path, line_number, line, path_categories))
    return occurrences


def _line_root_occurrences(
    rel_path: str,
    line_number: int,
    line: str,
    path_categories: set[str],
) -> list[Occurrence]:
    categories = tuple(sorted(path_categories | _classify_line(line) or {"unclassified"}))
    snippet = " ".join(line.strip().split())[:240]
    return [
        Occurrence(
            legacy_root=legacy_root,
            path=rel_path,
            line=line_number,
            categories=categories,
            snippet=snippet,
        )
        for legacy_root in _matching_roots(line)
    ]


def generate_inventory(root: Path) -> dict[str, Any]:
    occurrences: list[Occurrence] = []
    scanned_files = 0
    skipped_files = 0

    for rel_path in _tracked_files(root):
        scanned, file_occurrences = _scan_file(root, rel_path)
        scanned_files += int(scanned)
        skipped_files += int(not scanned)
        occurrences.extend(file_occurrences)

    root_counts = Counter(item.legacy_root for item in occurrences)
    category_counts = Counter(category for item in occurrences for category in item.categories)
    file_counts = Counter(item.path for item in occurrences)
    return {
        "schema_version": "repo-layout-caller-inventory.v1",
        "repo_root": root.as_posix(),
        "legacy_roots": list(ROOT_PATTERNS),
        "summary": {
            "scanned_files": scanned_files,
            "skipped_files": skipped_files,
            "occurrence_count": len(occurrences),
            "file_count": len(file_counts),
            "root_counts": dict(sorted(root_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
        },
        "top_files": [
            {"path": path, "occurrence_count": count}
            for path, count in file_counts.most_common(50)
        ],
        "occurrences": [item.to_json() for item in occurrences],
    }


def _is_actionable_occurrence(item: dict[str, Any]) -> bool:
    path = str(item["path"])
    categories = set(item.get("categories", []))
    if "generated_artifact_input" in categories:
        return False
    return not (
        path.startswith(".harness/")
        or path.startswith("Infrastructure/artifacts/")
        or path.startswith("artifacts/")
    )


def filter_actionable(report: dict[str, Any]) -> dict[str, Any]:
    filtered = {
        **report,
        "mode": "actionable_only",
        "occurrences": [
            item for item in report["occurrences"] if _is_actionable_occurrence(item)
        ],
    }
    root_counts = Counter(item["legacy_root"] for item in filtered["occurrences"])
    category_counts = Counter(
        category for item in filtered["occurrences"] for category in item["categories"]
    )
    file_counts = Counter(item["path"] for item in filtered["occurrences"])
    filtered["summary"] = {
        **report["summary"],
        "occurrence_count": len(filtered["occurrences"]),
        "file_count": len(file_counts),
        "root_counts": dict(sorted(root_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "excluded_generated_or_evidence_occurrences": (
            report["summary"]["occurrence_count"] - len(filtered["occurrences"])
        ),
    }
    filtered["top_files"] = [
        {"path": path, "occurrence_count": count}
        for path, count in file_counts.most_common(50)
    ]
    return filtered


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = _markdown_summary_lines(report["summary"])
    lines.extend(_markdown_count_tables(report))
    lines.extend(_markdown_migration_notes())
    path.write_text("\n".join(lines), encoding="utf-8")


def _markdown_summary_lines(summary: dict[str, Any]) -> list[str]:
    lines = [
        "# Repo Layout Caller Inventory",
        "",
        "Generated from tracked repository files for the foundry/ and skills-sdk/",
        "migration Phase 1 caller inventory.",
        "",
        "## Summary",
        "",
        f"- Scanned files: {summary['scanned_files']}",
        f"- Skipped non-text files: {summary['skipped_files']}",
        f"- Files with legacy-root references: {summary['file_count']}",
        f"- Total legacy-root references: {summary['occurrence_count']}",
    ]
    if "excluded_generated_or_evidence_occurrences" in summary:
        lines.append(
            "- Excluded generated/evidence references: "
            f"{summary['excluded_generated_or_evidence_occurrences']}"
        )
    return lines


def _markdown_count_tables(report: dict[str, Any]) -> list[str]:
    summary = report["summary"]
    lines = [
        "",
        "## Counts By Legacy Root",
        "",
        "| Legacy root | References |",
        "| --- | ---: |",
    ]
    for legacy_root, count in summary["root_counts"].items():
        lines.append(f"| {legacy_root} | {count} |")
    lines.extend(["", "## Counts By Caller Category", "", "| Category | References |", "| --- | ---: |"])
    for category, count in summary["category_counts"].items():
        lines.append(f"| {category} | {count} |")
    lines.extend(["", "## Top Files", "", "| File | References |", "| --- | ---: |"])
    for item in report["top_files"][:30]:
        lines.append(f"| {item['path']} | {item['occurrence_count']} |")
    return lines


def _markdown_migration_notes() -> list[str]:
    return [
        "",
        "## Migration Use",
        "",
        "- Use the JSON artifact for exact file:line occurrences.",
        "- Classify wrappers before moving a root.",
        "- Regenerate this inventory after each migration bucket.",
        "- Do not treat this inventory as behavior proof or hosted PR proof.",
        "",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--output-md", type=Path)
    parser.add_argument(
        "--actionable-only",
        action="store_true",
        help="Exclude generated artifacts and historical evidence from occurrences.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    report = generate_inventory(root)
    if args.actionable_only:
        report = filter_actionable(report)
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(report, args.output_md)
    if args.json or not (args.output_json or args.output_md):
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
