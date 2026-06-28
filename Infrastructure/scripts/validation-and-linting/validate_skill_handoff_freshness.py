#!/usr/bin/env python3
"""Validate Skills SDK handoff/status artifacts were generated for current HEAD."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STATUS_JSON = ROOT / ".harness/evidence/handoff/technical-writer/status.json"
DEFAULT_TRACKER_JSON = ROOT / ".harness/reports/skills-sdk-tracker-state-current.json"
DEFAULT_ATLAS_HTML = ROOT / "Docs/reference/skills-sdk-platform-atlas.html"


@dataclass
class FreshnessFinding:
    code: str
    message: str
    path: str
    expected: str
    actual: str | None


def _repo_relative(path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def current_git_head(repo_root: Path = ROOT) -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return loaded if isinstance(loaded, dict) else None


def _nested_repo_head(payload: dict[str, Any] | None) -> str | None:
    if payload is None:
        return None
    repo = payload.get("repo")
    if isinstance(repo, dict) and isinstance(repo.get("head"), str):
        return repo["head"]
    return None


def _atlas_generated_head(path: Path) -> str | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r"\bdata-generated-head=[\"']([^\"']+)[\"']", text)
    return match.group(1) if match else None


def _finding(code: str, path: Path, expected: str, actual: str | None) -> FreshnessFinding:
    return FreshnessFinding(
        code=code,
        message=f"{_repo_relative(path)} repo head is stale or missing.",
        path=_repo_relative(path),
        expected=expected,
        actual=actual,
    )


def validate_freshness(
    current_head: str,
    *,
    status_json: Path = DEFAULT_STATUS_JSON,
    tracker_json: Path = DEFAULT_TRACKER_JSON,
    atlas_html: Path = DEFAULT_ATLAS_HTML,
) -> list[FreshnessFinding]:
    checks = [
        ("status_json_head_stale", status_json, _nested_repo_head(_load_json(status_json))),
        ("tracker_json_head_stale", tracker_json, _nested_repo_head(_load_json(tracker_json))),
        ("atlas_generated_head_stale", atlas_html, _atlas_generated_head(atlas_html)),
    ]
    return [_finding(code, path, current_head, actual) for code, path, actual in checks if actual != current_head]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", type=Path, default=DEFAULT_STATUS_JSON)
    parser.add_argument("--tracker-json", type=Path, default=DEFAULT_TRACKER_JSON)
    parser.add_argument("--atlas-html", type=Path, default=DEFAULT_ATLAS_HTML)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main() -> int:
    args = _parser().parse_args()
    head = current_git_head()
    findings = validate_freshness(
        head,
        status_json=args.status_json,
        tracker_json=args.tracker_json,
        atlas_html=args.atlas_html,
    )
    payload = {
        "schema_version": "skill-handoff-freshness.v1",
        "status": "fail" if findings else "pass",
        "current_head": head,
        "checked_paths": [
            _repo_relative(args.status_json),
            _repo_relative(args.tracker_json),
            _repo_relative(args.atlas_html),
        ],
        "findings": [asdict(finding) for finding in findings],
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(payload["status"])
        for finding in findings:
            print(f"{finding.path}: expected {finding.expected}, actual {finding.actual or 'missing'}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
