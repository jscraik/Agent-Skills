#!/usr/bin/env python3
"""Classify captured oss-cloud output without emitting its contents."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


EXIT_CLEAR = 0
EXIT_SECRET_OBSERVED = 1
EXIT_UNAVAILABLE = 2

# Match shell, plain-text, and JSON-style diagnostics without capturing or
# emitting a value. The caller receives only this process's exit status.
SECRET_OUTPUT_RE = re.compile(
    r'(?im)(?:\bauthorization\b["\']?\s*[:=]\s*["\']?(?:basic|bearer)\s+\S+|["\']?(?:[A-Z][A-Z0-9]*(?:_(?:API_KEY|ACCESS_KEY|KEY|TOKEN|PASSWORD|PASSWD|SECRET(?:_ACCESS_KEY|_KEY)?))|(?:api|access)[_-]?key|token|password|passwd|secret(?:[_-]?(?:access_)?key)?)'
    r'\b["\']?\s*[:=]\s*["\']?\S+)'
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Classify captured oss-cloud output without writing it to stdout or stderr.",
    )
    parser.add_argument("paths", nargs="+", help="Captured output files to scan.")
    return parser


def _contains_secret_output(path: Path) -> bool | None:
    try:
        return bool(SECRET_OUTPUT_RE.search(path.read_text(encoding="utf-8", errors="replace")))
    except OSError:
        return None


def secret_output_scan_exit_code(paths: list[Path]) -> int:
    """Return a fixed exit code; never return or print captured file contents."""
    observed = [_contains_secret_output(path) for path in paths]
    if any(result is None for result in observed):
        return EXIT_UNAVAILABLE
    return EXIT_SECRET_OBSERVED if any(observed) else EXIT_CLEAR


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    return secret_output_scan_exit_code([Path(raw_path) for raw_path in args.paths])


if __name__ == "__main__":
    raise SystemExit(main())
