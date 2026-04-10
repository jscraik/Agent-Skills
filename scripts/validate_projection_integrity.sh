#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

scope="${PROJECTION_INTEGRITY_SCOPE:-all}"
manifest_out="${PROJECTION_INTEGRITY_MANIFEST:-artifacts/validation/projection-integrity/latest.json}"
output_format="${PROJECTION_INTEGRITY_FORMAT:-text}"

if python3 scripts/projection_integrity.py verify \
  --scope "$scope" \
  --manifest-out "$manifest_out" \
  --format "$output_format"; then
  echo "[projection-integrity] pass: scope=${scope}"
else
  echo "[projection-integrity] ERROR: drift detected for scope=${scope}" >&2
  echo "[projection-integrity]        run: bash scripts/sync_projection_trees.sh ${scope}" >&2
  exit 2
fi
