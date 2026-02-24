#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/ci_check.sh

Runs recon template CI checks across existing run artifacts.
USAGE
}

if [[ $# -gt 0 ]]; then
  case "${1:-}" in
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
fi

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

find_files() {
  local name="$1"
  if command -v fd >/dev/null 2>&1; then
    fd -t f "$name" "$ROOT/runs"
  else
    find "$ROOT/runs" -type f -name "$name"
  fi
}

# Validate any existing findings.json files
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  validate "$ROOT/schemas/findings.schema.json" "$f"
done < <(find_files 'findings.json')

# Validate any existing manifest.json files
while IFS= read -r f; do
  [[ -n "$f" ]] || continue
  validate "$ROOT/schemas/manifest.schema.json" "$f"
done < <(find_files 'manifest.json')

echo "CI checks complete."
