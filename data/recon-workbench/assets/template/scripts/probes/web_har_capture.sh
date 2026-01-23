#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/probes/web_har_capture.sh --har <path> --out <dir>

Notes:
- This probe imports an existing HAR file (captured manually).
- It validates JSON and copies it to the output directory.
USAGE
}

HAR=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --har) HAR="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
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

python3 - <<'PY'
import json, sys
path = sys.argv[1]
with open(path, 'r', encoding='utf-8') as f:
    json.load(f)
PY
"$HAR"

cp "$HAR" "$OUT/har.json"

echo "OK" > "$OUT/status.txt"
