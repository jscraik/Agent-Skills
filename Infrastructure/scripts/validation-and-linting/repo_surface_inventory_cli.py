"""CLI parsing and error rendering for repository surface inventory."""

from __future__ import annotations

import argparse
from typing import Any


SERVICE_ID = "agent-skills"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Classify tracked repository paths by repo surface ownership policy.")
    parser.add_argument("--json", action="store_true", help="Emit JSON-only stdout.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when blocking findings exist.")
    parser.add_argument("--repo-root", default=None, help="Repository root to inventory. Defaults to this checkout.")
    parser.add_argument("--changed-files", nargs="*", default=[], help="Changed repo-relative paths to assess.")
    parser.add_argument("--changed-files-from", default=None, help="Read changed paths from a newline-delimited file.")
    return parser.parse_args()


def _inventory_error_finding(exc: Exception) -> dict[str, Any]:
    recommendation = "Fix the inventory command inputs or canonical ownership rule."
    return {
        "path": "",
        "classification": "unknown",
        "status": "violation",
        "code": "inventory_error",
        "severity": "error",
        "blocking": True,
        "allowlist_entry": None,
        "reason": str(exc),
        "recommendation": recommendation,
        "metadata": {
            "service": SERVICE_ID,
            "next_steps": [
                {
                    "type": "fix",
                    "command": "./bin/ask repo surface --help",
                    "rationale": recommendation,
                }
            ],
        },
    }


def error_report(args: argparse.Namespace, exc: Exception) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "status": "error",
        "summary": {
            "total_paths": 0,
            "blocking_findings": 1,
            "counts_by_classification": {},
            "counts_by_status": {"violation": 1},
            "counts_by_code": {"inventory_error": 1},
        },
        "findings": [_inventory_error_finding(exc)],
        "metadata": {
            "service": SERVICE_ID,
            "inventory_scope": "tracked_existing_files",
            "strict": args.strict,
            "changed_files_policy": "not_applied",
            "changed_file_count": 0,
        },
    }
