#!/usr/bin/env bash

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'USAGE'
Usage: verify-work [options]
  --project-governance
    Select project-local scope (default).
  --workspace-governance
    Select workspace-wide governance checks.
    Backward-compatible alias for --workspace-governance.
  --persistent-artifacts
    Keep validation artifacts in place.
Validation artifacts are ephemeral.
Validation artifacts are persistent.
USAGE
  exit 0
fi

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
exec bash "$SCRIPT_DIR/verify-work_impl.sh" "$@"
