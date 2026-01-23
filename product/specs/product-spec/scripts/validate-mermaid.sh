#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDER="${SCRIPT_DIR}/render-diagrams.sh"

if [[ ! -x "$RENDER" ]]; then
  echo "error: render script not found or not executable: $RENDER" >&2
  echo "fix: chmod +x scripts/render-diagrams.sh" >&2
  exit 1
fi

TMP_OUT="$(mktemp -d)"
cleanup() { rm -rf "$TMP_OUT"; }
trap cleanup EXIT

# Default files if none provided
FILES=()
if [[ $# -gt 0 ]]; then
  FILES=("$@")
else
  [[ -f "spec-output.md" ]] && FILES+=("spec-output.md")
  [[ -f "tech-spec-output.md" ]] && FILES+=("tech-spec-output.md")
fi

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "error: no markdown files provided and no spec-output.md / tech-spec-output.md found" >&2
  exit 1
fi

echo "Validating Mermaid blocks by rendering to: $TMP_OUT"
OUT_DIR="$TMP_OUT" KEEP_TMP=0 "$RENDER" "${FILES[@]}"

echo "Mermaid validation: OK"
