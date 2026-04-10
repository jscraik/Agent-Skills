#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

scope="${PROJECTION_INTEGRITY_SCOPE:-all}"
manifest_out="${PROJECTION_INTEGRITY_MANIFEST:-artifacts/validation/projection-integrity/latest.json}"
output_format="${PROJECTION_INTEGRITY_FORMAT:-text}"

set +e
python3 scripts/projection_integrity.py verify \
  --scope "$scope" \
  --manifest-out "$manifest_out" \
  --format "$output_format"
verify_status=$?
set -e

if [[ "$verify_status" -eq 0 ]]; then
  echo "[projection-integrity] pass: scope=${scope}"
elif [[ "$verify_status" -eq 1 ]] && [[ -f "$manifest_out" ]] && python3 - "$manifest_out" <<'PY'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
payload = json.loads(manifest.read_text(encoding="utf-8"))
results = payload.get("results") or []
statuses = {str(entry.get("status", "")).lower() for entry in results}
is_drift = payload.get("status") == "fail" and "drift" in statuses and "error" not in statuses
raise SystemExit(0 if is_drift else 1)
PY
then
  echo "[projection-integrity] ERROR: drift detected for scope=${scope}" >&2
  echo "[projection-integrity]        run: bash scripts/sync_projection_trees.sh ${scope}" >&2
  exit "$verify_status"
else
  echo "[projection-integrity] ERROR: verification failed for scope=${scope} (exit=${verify_status})" >&2
  exit "$verify_status"
fi
