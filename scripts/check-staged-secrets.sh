#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if ! command -v gitleaks >/dev/null 2>&1; then
	echo "Error: required binary 'gitleaks' is not installed or not on PATH"
	exit 1
fi

if git diff --cached --quiet --exit-code; then
	echo "No staged changes detected for gitleaks."
	exit 0
fi

config_args=()
if [[ -f "$REPO_ROOT/.gitleaks.toml" ]]; then
	config_args+=(--config "$REPO_ROOT/.gitleaks.toml")
fi

gitleaks git \
	--staged \
	--redact \
	--no-banner \
	"${config_args[@]}"
