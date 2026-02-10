#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./run.sh [codex_home] [out_dir]
#
# Defaults:
#   codex_home: $CODEX_HOME or ~/.codex
#   out_dir:    <codex_home>/reports/codex-home-audit

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

CODEX_HOME_DIR="${1:-${CODEX_HOME:-$HOME/.codex}}"
OUT_DIR="${2:-${CODEX_HOME_DIR}/reports/codex-home-audit}"

exec zsh -lc "python3 \"${SCRIPT_DIR}/audit_codex_home.py\" --codex-home \"${CODEX_HOME_DIR}\" --out-dir \"${OUT_DIR}\""

