#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Open a Playwright trace file in the trace viewer.

Usage:
  scripts/view_trace.sh --trace <path>
USAGE
}

TRACE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --trace) TRACE="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$TRACE" ]]; then
  echo "Missing --trace"; usage; exit 2
fi

if [[ ! -f "$TRACE" ]]; then
  echo "ERROR: trace not found: $TRACE"; exit 2
fi

npx playwright show-trace "$TRACE"
