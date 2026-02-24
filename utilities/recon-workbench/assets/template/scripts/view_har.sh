#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Open or reveal a HAR file for manual import into DevTools.

Usage:
  scripts/view_har.sh --har <path> [--reveal]
USAGE
}

HAR=""
REVEAL="0"

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --har)
      require_option_value "$1" "$@"
      HAR="$2"
      shift 2
      ;;
    --reveal) REVEAL="1"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$HAR" ]]; then
  echo "Missing --har"; usage; exit 2
fi

if [[ ! -f "$HAR" ]]; then
  echo "ERROR: HAR not found: $HAR"; exit 2
fi

if [[ "$REVEAL" == "1" ]]; then
  open -R "$HAR"
  exit 0
fi

echo "HAR ready: $HAR"
echo "Import into DevTools Network panel (Export/Import HAR)."
