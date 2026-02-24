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

emit_json="0"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --json)
      emit_json="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 2
      ;;
  esac
done

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

json_escape() {
  local s="$1"
  s="${s//\\/\\\\}"
  s="${s//\"/\\\"}"
  s="${s//$'\n'/\\n}"
  s="${s//$'\r'/\\r}"
  s="${s//$'\t'/\\t}"
  printf '%s' "$s"
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
    printf '{ "name": "%s", "status": "%s", "version": "%s" }' \
      "$(json_escape "$t")" \
      "$(json_escape "$status")" \
      "$(json_escape "$version")"
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
