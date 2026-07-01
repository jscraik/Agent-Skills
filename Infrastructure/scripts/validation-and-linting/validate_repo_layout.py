#!/usr/bin/env python3
"""Validate repository layout and symlink ownership policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = Path("Infrastructure/config/repo-layout.v1.json")
SKIP_DIRS = {
    ".cache",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
}


@dataclass(frozen=True)
class Finding:
    code: str
    status: str
    severity: str
    path: str
    message: str
    classification: str | None = None
    owner: str | None = None
    metadata: dict[str, Any] | None = None

    @property
    def blocking(self) -> bool:
        return self.severity == "error"

    def to_json(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "status": self.status,
            "severity": self.severity,
            "blocking": self.blocking,
            "path": self.path,
            "message": self.message,
            "classification": self.classification,
            "owner": self.owner,
            "metadata": self.metadata or {},
        }


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_layout_entries(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    for section_id, section in config.get("target_layout", {}).items():
        paths: list[str] = []
        for key in ("paths", "future_paths", "legacy_paths"):
            raw_paths = section.get(key, [])
            if isinstance(raw_paths, list):
                paths.extend(str(item).rstrip("/") for item in raw_paths)
        for path in paths:
            status = (
                "future"
                if path in section.get("future_paths", [])
                else "legacy"
                if path in section.get("legacy_paths", [])
                else "current"
            )
            entry = {
                "section": section_id,
                "purpose": section.get("purpose", ""),
                "status": status,
            }
            entries[path] = entry
            top_level = path.split("/", 1)[0]
            entries.setdefault(top_level, entry)
    return entries


def _top_level_paths(root: Path) -> list[Path]:
    return sorted(root.iterdir(), key=lambda item: item.name)


def _tracked_top_level_names(root: Path) -> set[str] | None:
    if not (root / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    names = {
        line.split("/", 1)[0]
        for line in result.stdout.splitlines()
        if line and not line.startswith(".git/")
    }
    return names


def _legacy_layout_finding(name: str, entry: dict[str, Any]) -> Finding:
    return Finding(
        code="legacy_layout_path",
        status="ok",
        severity="info",
        path=name,
        message=(
            "Legacy path is allowed until the foundry/skills-sdk migration "
            "moves it."
        ),
        classification=entry["section"],
        owner="repo-layout.v1",
        metadata={"purpose": entry["purpose"]},
    )


def _unknown_top_level_finding(name: str) -> Finding:
    return Finding(
        code="top_level_unclassified",
        status="violation",
        severity="error",
        path=name,
        message=(
            "Top-level path is not classified by "
            "Infrastructure/config/repo-layout.v1.json."
        ),
        classification="unknown",
        owner="repo-layout.v1",
    )


def _validate_top_level(root: Path, config: dict[str, Any]) -> list[Finding]:
    entries = _iter_layout_entries(config)
    tracked_names = _tracked_top_level_names(root)
    findings: list[Finding] = []
    for child in _top_level_paths(root):
        name = child.name
        if name == ".git":
            continue
        if tracked_names is not None and name not in tracked_names:
            continue
        if name in entries:
            entry = entries[name]
            if entry["status"] == "legacy":
                findings.append(_legacy_layout_finding(name, entry))
            continue
        findings.append(_unknown_top_level_finding(name))
    return findings


def _walk_symlinks(root: Path) -> list[Path]:
    symlinks: list[Path] = []
    for current_root, dirnames, filenames in os.walk(root):
        rel_root = _rel(Path(current_root), root)
        parts = set(Path(rel_root).parts)
        if parts & SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [dirname for dirname in dirnames if dirname not in SKIP_DIRS]
        current = Path(current_root)
        for name in sorted([*dirnames, *filenames]):
            path = current / name
            if path.is_symlink():
                symlinks.append(path)
    return sorted(symlinks, key=lambda item: _rel(item, root))


def _matches_any(value: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(value, pattern) for pattern in patterns)


def _classify_symlink(
    rel_path: str, target: str, config: dict[str, Any]
) -> dict[str, Any] | None:
    for entry in config.get("symlink_policy", {}).get("classes", []):
        path_patterns = [str(pattern) for pattern in entry.get("path_patterns", [])]
        target_patterns = [str(pattern) for pattern in entry.get("target_patterns", [])]
        if not _matches_any(rel_path, path_patterns):
            continue
        if target_patterns and not _matches_any(target, target_patterns):
            continue
        return entry
    return None


def _validate_symlinks(root: Path, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for path in _walk_symlinks(root):
        rel_path = _rel(path, root)
        target = os.readlink(path)
        entry = _classify_symlink(rel_path, target, config)
        if entry is None:
            findings.append(
                Finding(
                    code="unknown_symlink",
                    status="violation",
                    severity="error",
                    path=rel_path,
                    message="Symlink is not classified by repo-layout symlink_policy.",
                    classification="unknown",
                    owner="repo-layout.v1",
                    metadata={"target": target},
                )
            )
            continue

        entry_status = str(entry.get("status", "allowed"))
        severity = "warning" if entry_status == "deprecated" else "info"
        findings.append(
            Finding(
                code=f"symlink_{entry_status}",
                status="warning" if entry_status == "deprecated" else "ok",
                severity=severity,
                path=rel_path,
                message=str(entry.get("reason", "Classified symlink.")),
                classification=str(entry.get("classification", "unknown")),
                owner=str(entry.get("owner", "unknown")),
                metadata={"target": target, "policy_id": entry.get("id")},
            )
        )
    return findings


def validate_repo_layout(root: Path, config_path: Path) -> dict[str, Any]:
    config = _load_json(config_path)
    if config.get("schema_version") != "repo-layout.v1":
        raise ValueError(f"{config_path}: schema_version must be repo-layout.v1")

    findings = [
        *_validate_top_level(root, config),
        *_validate_symlinks(root, config),
    ]
    blocking_findings = [finding for finding in findings if finding.blocking]
    warning_findings = [finding for finding in findings if finding.severity == "warning"]
    symlink_findings = [
        finding
        for finding in findings
        if finding.code.startswith("symlink_") or finding.code == "unknown_symlink"
    ]
    status = "fail" if blocking_findings else "pass"
    return {
        "schema_version": "repo-layout-validation.v1",
        "status": status,
        "root": root.as_posix(),
        "config_path": _rel(config_path, root),
        "summary": {
            "finding_count": len(findings),
            "blocking_count": len(blocking_findings),
            "warning_count": len(warning_findings),
            "symlink_count": len(symlink_findings),
        },
        "findings": [finding.to_json() for finding in findings],
    }


def _error_report(root: Path, config_path: Path, exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": "repo-layout-validation.v1",
        "status": "fail",
        "root": root.as_posix(),
        "config_path": config_path.as_posix(),
        "summary": {
            "finding_count": 1,
            "blocking_count": 1,
            "warning_count": 0,
            "symlink_count": 0,
        },
        "findings": [
            {
                "code": "validator_error",
                "status": "violation",
                "severity": "error",
                "blocking": True,
                "path": config_path.as_posix(),
                "message": str(exc),
                "classification": "validator",
                "owner": "validate_repo_layout.py",
                "metadata": {},
            }
        ],
    }


def _print_plain_report(report: dict[str, Any]) -> None:
    print(
        f"status={report['status']} "
        f"blockers={report['summary']['blocking_count']}"
    )
    for finding in report["findings"]:
        if finding["severity"] in {"error", "warning"}:
            print(f"{finding['severity']}: {finding['path']}: {finding['message']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=REPO_ROOT.as_posix())
    parser.add_argument("--config", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    config_path = Path(args.config) if args.config else root / DEFAULT_CONFIG
    if not config_path.is_absolute():
        config_path = root / config_path

    try:
        report = validate_repo_layout(root, config_path)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        error_report = _error_report(root, config_path, exc)
        if args.json:
            print(json.dumps(error_report, indent=2, sort_keys=True))
        else:
            print(f"fail: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_plain_report(report)
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
