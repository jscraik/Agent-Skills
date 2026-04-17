#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir/../.." rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd -P "$script_dir/../.." && pwd -P)"
fi
cd "$repo_root"

scope="${PROJECTION_INTEGRITY_SCOPE:-all}"
manifest_out="${PROJECTION_INTEGRITY_MANIFEST:-Infrastructure/artifacts/validation/projection-integrity/latest.json}"
output_format="${PROJECTION_INTEGRITY_FORMAT:-text}"

set +e
python3 Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py verify \
  --scope "$scope" \
  --manifest-out "$manifest_out" \
  --format "$output_format"
verify_status=$?
set -e

if [[ "$verify_status" -eq 0 ]]; then
  if [[ "$output_format" != "json" ]]; then
    echo "[projection-integrity] pass: scope=${scope}"
  fi
elif [[ "$verify_status" -eq 1 ]] && [[ -e "$manifest_out" ]] && python3 - "$manifest_out" <<'PY'
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
  echo "[projection-integrity]        run: bash Infrastructure/scripts/lifecycle-and-sync/sync_projection_trees.sh ${scope}" >&2
  exit "$verify_status"
else
  echo "[projection-integrity] ERROR: verification failed for scope=${scope} (exit=${verify_status})" >&2
  exit "$verify_status"
fi
