#!/usr/bin/env python3
"""Verify active repository paths obey the provider offboarding policy."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
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


def _require_non_empty_string(policy: dict[str, Any], key: str) -> str:
    value = policy.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SystemExit(f"provider policy field '{key}' must be a non-empty string")
    return value.strip()


def _require_string_list(policy: dict[str, Any], key: str) -> list[str]:
    value = policy.get(key)
    if not isinstance(value, list) or not value:
        raise SystemExit(f"provider policy field '{key}' must be a non-empty list of strings")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise SystemExit(f"provider policy field '{key}' must be a non-empty list of strings")
        normalized.append(item.strip())
    return normalized


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
    for root, dirnames, filenames in os.walk(REPO_ROOT, topdown=True):
        dirnames[:] = [name for name in dirnames if name not in DEFAULT_EXCLUDED_DIRS]
        root_path = Path(root)
        for dirname in dirnames:
            paths.append(_rel(root_path / dirname))
        for filename in filenames:
            paths.append(_rel(root_path / filename))
    return sorted(paths)


def build_report(policy_path: Path = DEFAULT_POLICY) -> dict[str, Any]:
    policy = _load_policy(policy_path)
    default_provider = _require_non_empty_string(policy, "default_provider")
    allowed_runtime_providers = _require_string_list(policy, "allowed_runtime_providers")
    if default_provider not in allowed_runtime_providers:
        raise SystemExit("provider policy field 'default_provider' must be present in 'allowed_runtime_providers'")
    blocked_terms = [term.lower() for term in _require_string_list(policy, "blocked_active_path_terms")]
    allowed_prefixes = _require_string_list(policy, "allowed_path_prefixes")

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
        "default_provider": default_provider,
        "allowed_runtime_providers": allowed_runtime_providers,
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
