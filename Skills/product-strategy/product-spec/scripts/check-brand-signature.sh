#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'TXT'
Usage:
  check-brand-signature.sh [--help]

Environment:
  README_PATH  Path to README to validate (default: README.md)
  STRICT       Set to 1 to fail when brand assets are missing
TXT
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -gt 0 ]]; then
  echo "ERROR: unknown option: $1"
  usage
  exit 2
fi

README="${README_PATH:-README.md}"
STRICT="${STRICT:-0}"

if [[ ! -f "$README" ]]; then
  echo "WARN: $README not found. Skipping signature check."
  exit 0
fi

has_md_signature=0
rg -q '\*\*brAInwav\*\*' "$README" && rg -q '_from demo to duty_' "$README" && has_md_signature=1

has_ascii_signature=0
rg -qi '^\s*brAInwav\s*$' "$README" && rg -qi '^\s*from demo to duty\s*$' "$README" && has_ascii_signature=1

if [[ "$has_md_signature" -eq 0 && "$has_ascii_signature" -eq 0 ]]; then
  echo "ERROR: README is missing BrAInwav documentation signature."
  echo "Expected either:"
  echo "  **brAInwav** + _from demo to duty_"
  echo "or ASCII fallback lines:"
  echo "  brAInwav"
  echo "  from demo to duty"
  exit 1
fi

missing_assets=0
for f in "brand/brand-mark.webp" "brand/brand-mark@2x.webp"; do
  if [[ ! -f "$f" ]]; then
    echo "WARN: missing brand asset: $f"
    missing_assets=1
  fi
done

if [[ "$missing_assets" -eq 1 && "$STRICT" == "1" ]]; then
  echo "ERROR: missing brand assets and STRICT=1"
  exit 1
fi

echo "Brand signature check: OK"
