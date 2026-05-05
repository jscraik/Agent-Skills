#!/usr/bin/env python3
"""Bounded read-only Codex local-state reporter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from keep_codex_fast_classify import likely_subsystem  # noqa: E402,F401
from keep_codex_fast_report import build_report  # noqa: E402


def report(args: argparse.Namespace) -> int:
    payload = build_report(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"status: {payload['status']}")
    print(f"codex_home: {payload['codex_home']}")
    print(f"elapsed_ms: {payload['elapsed_ms']}")
    for target in payload["storage_targets"]:
        print(f"- {target['path']} {target['size']} files={target['file_count']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    report_parser = subparsers.add_parser("report", help="run read-only dry-run report")
    report_parser.add_argument("--codex-home", default=None)
    report_parser.add_argument("--json", action="store_true")
    report_parser.add_argument("--large-threshold-mb", type=int, default=50)
    report_parser.add_argument("--top-n", type=int, default=10)
    report_parser.add_argument("--max-files-per-target", type=int, default=100_000)
    report_parser.add_argument("--max-seconds-per-target", type=float, default=4.0)
    report_parser.set_defaults(func=report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
