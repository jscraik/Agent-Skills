#!/usr/bin/env python3
"""Verify active repository paths obey the provider offboarding policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY = REPO_ROOT / "Infrastructure" / "config" / "provider-policy.json"
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}


def _load_policy(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"provider policy not found: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit("provider policy must be a JSON object")
    return payload


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _matches_allowed(rel_path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        normalized = pattern.strip()
        if normalized.startswith("./"):
            normalized = normalized[2:]
        if not normalized:
            continue
        if normalized.endswith("/"):
            if rel_path.startswith(normalized) or fnmatch.fnmatch(rel_path, normalized + "*"):
                return True
        elif fnmatch.fnmatch(rel_path, normalized):
            return True
    return False


def _iter_repo_paths() -> list[str]:
    paths: list[str] = []
    for path in REPO_ROOT.rglob("*"):
        parts = set(path.relative_to(REPO_ROOT).parts)
        if parts & DEFAULT_EXCLUDED_DIRS:
            continue
        paths.append(_rel(path))
    return sorted(paths)


def build_report(policy_path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    policy = _load_policy(policy_path)
    blocked_terms = [str(term).lower() for term in policy.get("blocked_active_path_terms", [])]
    allowed_prefixes = [str(pattern) for pattern in policy.get("allowed_path_prefixes", [])]

    violations: list[dict[str, str]] = []
    for rel_path in _iter_repo_paths():
        lowered = rel_path.lower()
        matched_term = next((term for term in blocked_terms if term in lowered), None)
        if not matched_term:
            continue
        if _matches_allowed(rel_path, allowed_prefixes):
            continue
        violations.append({"path": rel_path, "term": matched_term})

    return {
        "default_provider": policy.get("default_provider"),
        "allowed_runtime_providers": policy.get("allowed_runtime_providers", []),
        "blocked_active_path_terms": blocked_terms,
        "allowed_path_prefixes": allowed_prefixes,
        "violation_count": len(violations),
        "violations": violations,
        "status": "pass" if not violations else "fail",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="Provider policy JSON path")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    report = build_report(Path(args.policy))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Provider policy: {report['status']} ({report['violation_count']} violation(s))")
        for item in report["violations"]:
            print(f"- {item['path']} contains blocked provider term {item['term']}")

    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
