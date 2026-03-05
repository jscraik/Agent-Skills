#!/usr/bin/env python3
"""Validate router JSON payloads for schema and telemetry safety."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_LIB = REPO_ROOT / 'utilities' / 'skill-creator' / 'scripts'
if str(SCHEMA_LIB) not in sys.path:
    sys.path.insert(0, str(SCHEMA_LIB))

from skill_router_schema import validate_router_result  # noqa: E402


def load_payload(path: Path | None) -> Dict[str, Any]:
    if path is None:
        data = sys.stdin.read().strip()
    else:
        data = path.read_text(encoding='utf-8')

    if not data:
        return {}

    obj = json.loads(data)
    if not isinstance(obj, dict):
        raise ValueError('Expected JSON object payload')
    return obj


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Verify router schema payload')
    parser.add_argument('--input', type=Path, help='Path to router JSON payload (defaults to stdin)')
    parser.add_argument(
        '--fail-on-sensitive-fields',
        action='store_true',
        help='Fail if sensitive patterns are present in payload values',
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)

    if not payload:
        print('No payload provided; schema verification skipped.')
        return 0

    issues: List[str] = validate_router_result(
        payload,
        fail_on_sensitive_fields=args.fail_on_sensitive_fields,
    )
    if issues:
        print('Router schema validation failed:')
        for issue in issues:
            print(f'- {issue}')
        return 1

    print('Router schema validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
