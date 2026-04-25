#!/usr/bin/env bash
set -euo pipefail

TARGET_PATH="${1:-docs/}"
CONFIG_FILE="${2:-.vale.ini}"

if ! command -v vale >/dev/null 2>&1; then
  echo "ERROR: 'vale' is not installed or not on PATH." >&2
  echo "Install example (macOS): brew install vale" >&2
  exit 1
fi

echo "==> Vale version"
vale --version

if [ ! -e "${CONFIG_FILE}" ]; then
  echo "ERROR: Vale config not found at ${CONFIG_FILE}" >&2
  exit 1
fi

echo "==> Active Vale config"
vale --config="${CONFIG_FILE}" ls-config

if grep -Eq '^[[:space:]]*Packages[[:space:]]*=' "${CONFIG_FILE}"; then
  echo "==> Packages detected in ${CONFIG_FILE}; running vale sync"
  vale --config="${CONFIG_FILE}" sync
else
  echo "==> No Packages key detected; skipping vale sync"
fi

echo "==> Lint check (line output, error threshold)"
vale --config="${CONFIG_FILE}" --output=line --minAlertLevel=error "${TARGET_PATH}"

echo "==> Lint check (JSON output)"
vale --config="${CONFIG_FILE}" --output=JSON "${TARGET_PATH}" >/dev/null

echo "Vale verification completed successfully."
