#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

mkdir -p "$ROOT/runs/_ci"
"$SCRIPT_DIR/doctor.sh" --json > "$ROOT/runs/_ci/doctor.json"

validate() {
  local schema="$1"
  local data="$2"
  if [[ -f "$schema" && -f "$data" ]]; then
    "$SCRIPT_DIR/validate_schema.py" --schema "$schema" --data "$data"
  fi
}

# Validate any existing findings.json files
if command -v fd >/dev/null 2>&1; then
  mapfile -t findings < <(fd -t f 'findings.json' "$ROOT/runs")
else
  mapfile -t findings < <(find "$ROOT/runs" -type f -name 'findings.json')
fi

for f in "${findings[@]:-}"; do
  validate "$ROOT/schemas/findings.schema.json" "$f"
done

# Validate any existing manifest.json files
if command -v fd >/dev/null 2>&1; then
  mapfile -t manifests < <(fd -t f 'manifest.json' "$ROOT/runs")
else
  mapfile -t manifests < <(find "$ROOT/runs" -type f -name 'manifest.json')
fi

for f in "${manifests[@]:-}"; do
  validate "$ROOT/schemas/manifest.schema.json" "$f"
done

echo "CI checks complete."
