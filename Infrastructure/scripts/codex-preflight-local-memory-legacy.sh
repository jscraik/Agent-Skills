#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/codex-preflight-local-memory-legacy_impl.sh"

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  preflight_local_memory_shell_fallback "$@"
fi
