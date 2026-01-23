#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Check availability of common inspection tools.

Usage:
  scripts/doctor.sh [--json]

Options:
  --json   Emit JSON summary.
  -h       Show help.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

emit_json="0"
if [[ "${1:-}" == "--json" ]]; then
  emit_json="1"
fi

tools=(
  "rg"
  "fd"
  "jq"
  "git"
  "python3"
  "node"
  "xcrun"
  "otool"
  "nm"
  "codesign"
  "strings"
  "lldb"
)

tool_version() {
  local t="$1"
  local out=""
  if ! command -v "$t" >/dev/null 2>&1; then
    echo ""
    return
  fi
  for flag in "--version" "-v" "-V"; do
    if out="$("$t" "$flag" 2>/dev/null | head -n 1)"; then
      if [[ -n "$out" ]]; then
        echo "$out"
        return
      fi
    fi
  done
  echo ""
}

if [[ "$emit_json" == "1" ]]; then
  printf '{ "tools": ['
  first=1
  for t in "${tools[@]}"; do
    if command -v "$t" >/dev/null 2>&1; then
      status="ok"
      version="$(tool_version "$t")"
      if [[ -z "$version" ]]; then
        version="unknown"
      fi
    else
      status="missing"
      version="unknown"
    fi
    if [[ "$first" == "0" ]]; then
      printf ', '
    fi
    first=0
    printf '{ "name": "%s", "status": "%s", "version": "%s" }' "$t" "$status" "$version"
  done
  printf ' ] }\n'
  exit 0
fi

for t in "${tools[@]}"; do
  if command -v "$t" >/dev/null 2>&1; then
    ver="$(tool_version "$t")"
    if [[ -z "$ver" ]]; then
      ver="unknown"
    fi
    printf 'OK: %s (%s)\n' "$t" "$ver"
  else
    printf 'MISSING: %s\n' "$t"
  fi
done
