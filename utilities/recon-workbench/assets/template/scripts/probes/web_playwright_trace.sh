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

while [[ $# -gt 0 ]]; do
  case "$1" in
    --url) URL="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --wait-ms) WAIT_MS="$2"; shift 2 ;;
    --timeout-ms) TIMEOUT_MS="$2"; shift 2 ;;
    --headless) HEADLESS="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$URL" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
node "$SCRIPT_DIR/web_playwright_trace.mjs" \
  --url "$URL" --out "$OUT" --wait-ms "$WAIT_MS" --timeout-ms "$TIMEOUT_MS" --headless "$HEADLESS"
