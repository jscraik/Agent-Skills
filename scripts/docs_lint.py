#!/usr/bin/env python3
"""Lint repository docs conventions for Codex-friendly docs governance."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Iterable

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
FILE_PATH_RE = re.compile(r"[A-Za-z0-9_./-]+[.][A-Za-z0-9]+")
VAGUE_REF_RE = re.compile(r"\b(server file|config file|this file|that file|the file)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


@dataclass
class Issue:
    code: str
    severity: str
    file: str
    line: int
    message: str
    suggestion: str | None = None


def load_config(config_path: Path) -> dict:
    with config_path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    defaults = {
        "enforcement_mode": "warn",
        "docs_root": "/docs",
        "required_index_dirs": ["/docs"],
        "allow_relative_links": False,
        "allow_trailing_slash_links": False,
        "exclude_paths": [],
        "required_sections": {},
    }
    defaults.update(cfg)
    return defaults


def resolve_mode(config: dict, requested_mode: str | None) -> str:
    if requested_mode:
        return requested_mode
    mode = str(config.get("enforcement_mode", "warn"))
    block_after = str(config.get("block_after", "")).strip()
    if block_after and date.today().isoformat() >= block_after:
        return "block"
    return mode


def run_git(repo_root: Path, args: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def changed_paths(repo_root: Path) -> set[Path]:
    base_sha = os.getenv("GITHUB_BASE_SHA", "").strip()
    head_sha = os.getenv("GITHUB_SHA", "").strip()
    paths: set[str] = set()
    if base_sha and head_sha:
        paths.update(run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR", f"{base_sha}..{head_sha}"]))
    else:
        paths.update(run_git(repo_root, ["diff", "--name-only", "--diff-filter=ACMR", "HEAD"]))
    paths.update(run_git(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return {(repo_root / p).resolve() for p in paths}


def should_scan(path: Path, repo_root: Path, config: dict) -> bool:
    if path.suffix.lower() != ".md":
        return False
    if not path.exists():
        return False
    rel = "/" + path.relative_to(repo_root).as_posix()
    if rel == "/CONTRIBUTING.md":
        return True
    docs_root = str(config["docs_root"]).rstrip("/")
    if not rel.startswith(f"{docs_root}/") and rel != f"{docs_root}/index.md":
        return False
    for excluded in config.get("exclude_paths", []):
        excluded_norm = str(excluded).rstrip("/")
        if rel == excluded_norm or rel.startswith(f"{excluded_norm}/"):
            return False
    return True


def discover_markdown_files(repo_root: Path, config: dict, changed_only: bool) -> list[Path]:
    files: set[Path] = set()
    docs_dir = (repo_root / config["docs_root"].lstrip("/")).resolve()
    if docs_dir.exists():
        for md in docs_dir.rglob("*.md"):
            files.add(md.resolve())
    contributing = (repo_root / "CONTRIBUTING.md").resolve()
    if contributing.exists():
        files.add(contributing)
    if changed_only:
        changed = changed_paths(repo_root)
        files = {p for p in files if p in changed}
    return sorted(p for p in files if should_scan(p, repo_root, config))


def normalize_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target:
        target = target.split(" ", 1)[0]
    return target


def is_external_link(target: str) -> bool:
    return target.startswith(("http://", "https://", "mailto:", "tel:", "data:"))


def is_internal_relative(target: str) -> bool:
    if target.startswith(("#", "/", "@")):
        return False
    if is_external_link(target):
        return False
    return True


def line_has_explicit_path(line: str) -> bool:
    return bool(FILE_PATH_RE.search(line))


def should_skip_vague_reference_warning(line: str) -> bool:
    lower = line.lower()
    skip_markers = (
        "avoid vague references",
        "common anti-patterns",
        "vague references like",
        "vague references (",
    )
    return any(marker in lower for marker in skip_markers)


def lint_file(path: Path, repo_root: Path, config: dict) -> list[Issue]:
    issues: list[Issue] = []
    rel = path.relative_to(repo_root).as_posix()
    allow_relative = bool(config.get("allow_relative_links", False))
    allow_trailing = bool(config.get("allow_trailing_slash_links", False))
    with path.open("r", encoding="utf-8") as f:
        in_fence = False
        for idx, line in enumerate(f, start=1):
            if line.strip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for match in LINK_RE.finditer(line):
                target = normalize_link_target(match.group(1))
                if not target:
                    continue
                if is_external_link(target) or target.startswith("#"):
                    continue
                if is_internal_relative(target) and not allow_relative:
                    issues.append(
                        Issue(
                            code="relative-link",
                            severity="error",
                            file=rel,
                            line=idx,
                            message=f"Relative internal link is not allowed: {target}",
                            suggestion="Use a full root path (for example, /docs/reference).",
                        )
                    )
                if target.startswith("/") and target != "/" and target.rstrip("#").endswith("/") and not allow_trailing:
                    issues.append(
                        Issue(
                            code="trailing-slash-link",
                            severity="error",
                            file=rel,
                            line=idx,
                            message=f"Internal link uses a trailing slash: {target}",
                            suggestion="Use a non-trailing-slash internal path.",
                        )
                    )
            if VAGUE_REF_RE.search(line) and not line_has_explicit_path(line) and not should_skip_vague_reference_warning(line):
                issues.append(
                    Issue(
                        code="vague-file-reference",
                        severity="warning",
                        file=rel,
                        line=idx,
                        message="Potential vague file reference; use an explicit path.",
                        suggestion="Reference a concrete path like `scripts/docs_lint.py`.",
                    )
                )
    return issues


def index_file_issues(repo_root: Path, config: dict) -> list[Issue]:
    issues: list[Issue] = []
    for dir_path in config.get("required_index_dirs", []):
        target_dir = (repo_root / str(dir_path).lstrip("/")).resolve()
        target_index = target_dir / "index.md"
        if not target_index.exists():
            rel_dir = "/" + target_dir.relative_to(repo_root).as_posix()
            issues.append(
                Issue(
                    code="missing-index",
                    severity="error",
                    file=rel_dir,
                    line=1,
                    message=f"Required index.md missing under {rel_dir}",
                    suggestion="Add index.md to satisfy docs hierarchy contract.",
                )
            )
    return issues


def required_section_issues(repo_root: Path, config: dict) -> list[Issue]:
    issues: list[Issue] = []
    required_sections = config.get("required_sections", {})
    if not isinstance(required_sections, dict):
        return issues

    for raw_path, raw_sections in required_sections.items():
        rel_path = str(raw_path).strip()
        if not rel_path:
            continue
        target = (repo_root / rel_path.lstrip("/")).resolve()
        if not target.exists():
            issues.append(
                Issue(
                    code="missing-required-doc",
                    severity="error",
                    file="/" + rel_path.lstrip("/"),
                    line=1,
                    message="Required documentation file is missing.",
                    suggestion="Create the required doc path and include the mandated section headings.",
                )
            )
            continue

        expected_sections = [str(section).strip() for section in (raw_sections or []) if str(section).strip()]
        headings: set[str] = set()
        with target.open("r", encoding="utf-8") as f:
            in_fence = False
            for line in f:
                stripped = line.strip()
                if stripped.startswith("```"):
                    in_fence = not in_fence
                    continue
                if in_fence:
                    continue
                match = HEADING_RE.match(stripped)
                if not match:
                    continue
                heading_text = match.group(2).strip().rstrip("#").strip()
                headings.add(heading_text)

        for section in expected_sections:
            if section not in headings:
                issues.append(
                    Issue(
                        code="missing-required-section",
                        severity="error",
                        file="/" + target.relative_to(repo_root).as_posix(),
                        line=1,
                        message=f"Required section heading missing: {section}",
                        suggestion=f"Add a markdown heading exactly named '{section}'.",
                    )
                )

    return issues


def emit_text_summary(issues: Iterable[Issue], effective_mode: str, scanned_files: int) -> None:
    issues = list(issues)
    errors = [i for i in issues if i.severity == "error"]
    warnings = [i for i in issues if i.severity == "warning"]
    print(f"docs-lint mode={effective_mode} scanned_files={scanned_files} errors={len(errors)} warnings={len(warnings)}")
    for issue in issues:
        print(f"{issue.severity.upper():7} {issue.file}:{issue.line} {issue.code} - {issue.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint docs governance rules.")
    parser.add_argument("--mode", choices=["warn", "block"], default=None)
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--report-json", default="")
    parser.add_argument("--config", default="docs-policy.json")
    args = parser.parse_args()

    repo_root = Path.cwd().resolve()
    config_path = (repo_root / args.config).resolve()
    if not config_path.exists():
        print(f"ERROR: config file not found: {config_path}", file=sys.stderr)
        return 2

    config = load_config(config_path)
    effective_mode = resolve_mode(config, args.mode)
    files = discover_markdown_files(repo_root, config, args.changed_only)

    issues: list[Issue] = []
    for md in files:
        issues.extend(lint_file(md, repo_root, config))
    issues.extend(index_file_issues(repo_root, config))
    issues.extend(required_section_issues(repo_root, config))

    emit_text_summary(issues, effective_mode, len(files))

    report = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": effective_mode,
        "scanned_files": len(files),
        "errors": sum(1 for i in issues if i.severity == "error"),
        "warnings": sum(1 for i in issues if i.severity == "warning"),
        "issues": [asdict(i) for i in issues],
    }
    if args.report_json:
        out = Path(args.report_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if effective_mode == "block" and report["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
