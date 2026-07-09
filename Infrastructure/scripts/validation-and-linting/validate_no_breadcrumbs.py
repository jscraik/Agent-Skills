#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[3]

BREADCRUMB_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("todo-marker", re.compile(r"\b(?:TODO|FIXME|HACK|XXX|TBD)\b")),
    ("todo-token", re.compile(r"\[(?:TODO|FIXME|HACK|TBD)[:\]]", re.IGNORECASE)),
    ("not-implemented", re.compile(r"\bnot\s+implemented\b", re.IGNORECASE)),
    ("wire-later", re.compile(r"\b(?:wire|wired|wiring)\s+(?:it\s+)?later\b", re.IGNORECASE)),
    ("coming-soon", re.compile(r"\bcoming\s+soon\b", re.IGNORECASE)),
    ("temporary-placeholder", re.compile(r"\b(?:temporary|temp|stub|dummy)\s+placeholder\b", re.IGNORECASE)),
    ("placeholder-text", re.compile(r"\bplaceholder\s+(?:text|content|copy|value|stub)\b", re.IGNORECASE)),
)

DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt"}
CODE_SUFFIXES = {
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".css",
    ".scss",
    ".html",
    ".jsonc",
    ".yaml",
    ".yml",
    ".toml",
}

SKIP_PREFIXES = (
    ".git/",
    ".agents/",
    ".codex/",
    ".harness/implementation-notes/",
    ".harness/memory/",
    ".harness/media/",
    ".harness/plan/",
    ".harness/quality/",
    ".harness/reports/",
    ".harness/review-artifacts/",
    "artifacts/",
    "Docs/brainstorms/",
    "Docs/plans/",
    "Docs/specs/",
    "Docs/reference/",
    "Infrastructure/tests/fixtures/",
)

ALLOW_MARKERS = (
    "no-breadcrumbs: allow",
    "breadcrumb: allow",
    "breadcrumbs: allow",
    "intentional breadcrumb example",
)


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    code: str
    text: str


def _run_git(args: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def changed_paths() -> list[str]:
    paths = set(_run_git(["diff", "--name-only", "--diff-filter=ACMR", "HEAD"]))
    paths.update(_run_git(["ls-files", "--others", "--exclude-standard"]))
    return sorted(paths)


def normalize_path(path: str) -> str:
    return path.strip().removeprefix("./")


def should_scan_path(path: str) -> bool:
    rel = normalize_path(path)
    if not rel:
        return False
    if any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in SKIP_PREFIXES):
        return False
    candidate = REPO_ROOT / rel
    if not candidate.is_file():
        return False
    suffix = candidate.suffix.lower()
    return suffix in DOC_SUFFIXES or suffix in CODE_SUFFIXES or candidate.name in {"AGENTS.md", "CODESTYLE.md", "README.md"}


def _is_comment_line(line: str, in_block_comment: bool) -> tuple[bool, bool]:
    stripped = line.lstrip()
    if in_block_comment:
        return True, "*/" not in stripped
    if stripped.startswith("<!--"):
        return True, "-->" not in stripped
    if stripped.startswith(("#", "//", "*")):
        return True, False
    if stripped.startswith(("/*", "/**")):
        return True, "*/" not in stripped
    return False, False


def _is_doc_line_scannable(line: str, *, in_fence: bool) -> bool:
    if in_fence:
        return False
    stripped = line.lstrip()
    if not stripped:
        return False
    if stripped.startswith(">"):
        return False
    if stripped.startswith("|"):
        return False
    if stripped.startswith(("-", "*", "+")) and "`" in stripped:
        return False
    return True


def _has_allow_marker(line: str) -> bool:
    lower = line.lower()
    return any(marker in lower for marker in ALLOW_MARKERS)


def _scan_text(rel_path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    suffix = Path(rel_path).suffix.lower()
    is_doc = suffix in DOC_SUFFIXES or rel_path in {"AGENTS.md", "CODESTYLE.md", "README.md"}
    in_fence = False
    in_block_comment = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if is_doc and stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if _has_allow_marker(line):
            continue
        if is_doc:
            should_scan = _is_doc_line_scannable(line, in_fence=in_fence)
        else:
            should_scan, in_block_comment = _is_comment_line(line, in_block_comment)
        if not should_scan:
            continue
        for code, pattern in BREADCRUMB_PATTERNS:
            if pattern.search(line):
                findings.append(Finding(file=rel_path, line=line_no, code=code, text=line.strip()))
                break
    return findings


def scan_paths(paths: Iterable[str]) -> list[Finding]:
    findings: list[Finding] = []
    for raw_path in paths:
        rel_path = normalize_path(raw_path)
        if not should_scan_path(rel_path):
            continue
        try:
            text = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        findings.extend(_scan_text(rel_path, text))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fail on obvious unresolved breadcrumbs in changed docs and code comments.")
    parser.add_argument("--changed-files", nargs="*", help="Repo-relative files to scan. Defaults to current changed files.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    paths = [normalize_path(path) for path in args.changed_files] if args.changed_files is not None else changed_paths()
    findings = scan_paths(paths)
    result = {
        "schema_version": "no-breadcrumbs-validation/v1",
        "status": "pass" if not findings else "fail",
        "scanned_files": [path for path in paths if should_scan_path(path)],
        "findings": [asdict(finding) for finding in findings],
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
        for finding in findings:
            print(f"{finding.file}:{finding.line}: {finding.code}: {finding.text}")
    return 0 if not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
