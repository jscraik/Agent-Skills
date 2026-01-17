#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Create a run manifest with tool versions and artifact hashes.

Usage:
  scripts/manifest.sh --run-dir <path> --target-id <id> --target-locator <locator> [--out <manifest.json>]
USAGE
}

RUN_DIR=""
TARGET_ID=""
TARGET_LOCATOR=""
OUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="$2"; shift 2 ;;
    --target-id) TARGET_ID="$2"; shift 2 ;;
    --target-locator) TARGET_LOCATOR="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$RUN_DIR" || -z "$TARGET_ID" || -z "$TARGET_LOCATOR" ]]; then
  echo "Missing required args"; usage; exit 2
fi

if [[ ! -d "$RUN_DIR" ]]; then
  echo "ERROR: run dir not found: $RUN_DIR"; exit 2
fi

if [[ -z "$OUT" ]]; then
  OUT="$RUN_DIR/manifest.json"
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DOCTOR_JSON=$("$SCRIPT_DIR/doctor.sh" --json)

RUN_DIR="$RUN_DIR" TARGET_ID="$TARGET_ID" TARGET_LOCATOR="$TARGET_LOCATOR" DOCTOR_JSON="$DOCTOR_JSON" OUT="$OUT" \
python3 - <<'PY'
import json, hashlib, os, sys
from datetime import datetime, timezone

run_dir = os.environ.get("RUN_DIR")
target_id = os.environ.get("TARGET_ID")
target_locator = os.environ.get("TARGET_LOCATOR")
Doctor = json.loads(os.environ.get("DOCTOR_JSON", "{}"))

artifact_hashes = {}
for root, _, files in os.walk(run_dir):
    for name in files:
        path = os.path.join(root, name)
        rel = os.path.relpath(path, run_dir)
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                h.update(chunk)
        artifact_hashes[rel] = h.hexdigest()

tool_versions = {}
for item in Doctor.get("tools", []):
    if item.get("status") == "ok":
        tool_versions[item.get("name")] = item.get("version", "unknown")

manifest = {
    "run_id": os.path.basename(run_dir),
    "target_id": target_id,
    "target_locator": target_locator,
    "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "tool_versions": tool_versions,
    "artifact_hashes": artifact_hashes,
}

out = os.environ.get("OUT")
with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, sort_keys=True)
PY
