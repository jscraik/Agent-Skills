#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RULESET_PATH="$REPO_ROOT/scripts/semgrep-pre-push.yml"

# Source shared Semgrep bootstrap functions
# shellcheck source=scripts/semgrep-bootstrap.sh
source "$REPO_ROOT/scripts/semgrep-bootstrap.sh"

cd "$REPO_ROOT"

if [[ ! -f "$RULESET_PATH" ]]; then
	echo "Error: missing Semgrep ruleset at $RULESET_PATH"
	exit 1
fi

ensure_semgrep_version

run_semgrep scan \
	--config "$RULESET_PATH" \
	--disable-version-check \
	--error \
	--jobs 1 \
	.