#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPEC_LINT="${SCRIPT_DIR}/spec-lint.py"
VALIDATE_MERMAID="${SCRIPT_DIR}/validate-mermaid.sh"

if [[ ! -f "$SPEC_LINT" ]]; then
  echo "error: missing $SPEC_LINT" >&2
  exit 1
fi

if [[ ! -x "$VALIDATE_MERMAID" ]]; then
  echo "error: missing or not executable: $VALIDATE_MERMAID" >&2
  echo "fix: chmod +x scripts/validate-mermaid.sh" >&2
  exit 1
fi

STRICT="${STRICT:-0}"

# Gather files
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

echo "=== Quality Gates start ==="
echo "Files: ${FILES[*]}"
echo "STRICT=$STRICT"

# 1) Spec lint
echo ""
echo "==> Spec lint"
for f in "${FILES[@]}"; do
  if [[ "$STRICT" == "1" ]]; then
    python3 "$SPEC_LINT" --strict "$f"
  else
    python3 "$SPEC_LINT" "$f"
  fi
done

# 2) Mermaid compile/render validation
echo ""
echo "==> Mermaid validation"
"$VALIDATE_MERMAID" "${FILES[@]}"

# 3) Optional: Vale prose lint
echo ""
echo "==> Prose lint (Vale) [optional]"
if command -v vale >/dev/null 2>&1; then
  if [[ -f ".vale.ini" ]]; then
    vale "${FILES[@]}"
    echo "Vale: OK"
  else
    echo "Vale installed but .vale.ini not found; skipping."
  fi
else
  echo "Vale not installed; skipping."
fi

echo ""
echo "=== Quality Gates PASS ==="
