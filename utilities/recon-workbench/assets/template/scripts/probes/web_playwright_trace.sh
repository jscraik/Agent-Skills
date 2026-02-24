#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/probes/web_playwright_trace.sh --url <url> --out <dir> [--wait-ms <n>] [--timeout-ms <n>] [--headless true|false]
USAGE
}

URL=""
OUT=""
WAIT_MS="3000"
TIMEOUT_MS="30000"
HEADLESS="true"

require_option_value() {
  local opt="$1"
  if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
    echo "Missing value for ${opt}" >&2
    usage
    exit 2
  fi
}

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 127
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url)
      require_option_value "$1" "${2:-}"
      URL="$2"
      shift 2
      ;;
    --out)
      require_option_value "$1" "${2:-}"
      OUT="$2"
      shift 2
      ;;
    --wait-ms)
      require_option_value "$1" "${2:-}"
      WAIT_MS="$2"
      shift 2
      ;;
    --timeout-ms)
      require_option_value "$1" "${2:-}"
      TIMEOUT_MS="$2"
      shift 2
      ;;
    --headless)
      require_option_value "$1" "${2:-}"
      HEADLESS="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$URL" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
require_cmd node
node "$SCRIPT_DIR/web_playwright_trace.mjs" \
  --url "$URL" --out "$OUT" --wait-ms "$WAIT_MS" --timeout-ms "$TIMEOUT_MS" --headless "$HEADLESS"
