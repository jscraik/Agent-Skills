#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/probes/macos_bundle_tree.sh --app <path> --out <dir>
USAGE
}

APP=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --app) APP="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$APP" || -z "$OUT" ]]; then
  echo "Missing required args"; usage; exit 2
fi

if [[ ! -d "$APP" ]]; then
  echo "ERROR: app path not found: $APP"; exit 2
fi

mkdir -p "$OUT"

if command -v fd >/dev/null 2>&1; then
  fd --hidden --type f . "$APP" > "$OUT/bundle_tree.txt"
else
  find "$APP" -type f > "$OUT/bundle_tree.txt"
fi

if [[ -f "$APP/Contents/Info.plist" ]]; then
  echo "$APP/Contents/Info.plist" > "$OUT/info_plist_path.txt"
fi

echo "OK" > "$OUT/status.txt"
