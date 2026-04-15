#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/probes/web_har_capture.sh --har <path> --out <dir>

Notes:
- This probe imports an existing HAR file (captured manually).
- It validates JSON and copies it to the output directory.
USAGE
}

HAR=""
OUT=""

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
    --har)
      require_option_value "$1" "${2:-}"
      HAR="$2"
      shift 2
      ;;
    --out)
      require_option_value "$1" "${2:-}"
      OUT="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$HAR" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
fi

if [[ ! -f "$HAR" ]]; then
  echo "ERROR: HAR not found: $HAR"; exit 2
fi

mkdir -p "$OUT"

require_cmd python3
python3 - "$HAR" <<'PY'
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    json.load(f)
PY

cp "$HAR" "$OUT/har.json"

echo "OK" > "$OUT/status.txt"
