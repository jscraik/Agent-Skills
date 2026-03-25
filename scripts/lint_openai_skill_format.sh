#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/lint_openai_skill_format.sh [--mode strict|warn]

Checks SKILL.md files for OpenAI skill frontmatter compatibility.
- Requires top-level frontmatter keys: name, description
- Allows optional top-level keys: license, allowed-tools, metadata
- Flags unknown top-level keys in frontmatter
USAGE
}

mode="strict"
if [[ $# -gt 0 ]]; then
  case "${1:-}" in
    --mode)
      mode="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
fi

if [[ "$mode" != "strict" && "$mode" != "warn" ]]; then
  echo "Invalid mode: $mode (expected strict|warn)" >&2
  exit 2
fi

find_cmd=""
if command -v fd >/dev/null 2>&1; then
  find_cmd="fd"
elif command -v fdfind >/dev/null 2>&1; then
  find_cmd="fdfind"
else
  echo "fd or fdfind is required to lint OpenAI skill format" >&2
  exit 2
fi

roots=(auth backend frontend github interview product utilities)
errors=0
warnings=0
checked=0

while IFS= read -r file; do
  [[ -n "$file" ]] || continue
  checked=$((checked + 1))

  output="$(
    awk '
      BEGIN {
        bad_start = 0
        in_fm = 0
        fm_started = 0
        fm_ended = 0
        has_name = 0
        has_description = 0
      }
      NR == 1 {
        if ($0 !~ /^---[ \t]*$/) {
          print "ERR:1:missing opening frontmatter delimiter (first line must be ---)"
          bad_start = 1
          next
        }
        in_fm = 1
        fm_started = 1
        next
      }
      bad_start == 1 {
        next
      }
      in_fm == 1 && /^---[ \t]*$/ {
        in_fm = 0
        fm_ended = 1
        next
      }
      in_fm == 0 {
        next
      }
      in_fm == 1 && /^[A-Za-z0-9_-]+:[ \t]*/ {
        key = $0
        sub(/:.*/, "", key)
        if (key == "name") {
          has_name = 1
        } else if (key == "description") {
          has_description = 1
        } else if (key != "license" && key != "allowed-tools" && key != "metadata") {
          print "ERR:" NR ":unknown top-level frontmatter key `" key "`"
        }
      }
      END {
        if (bad_start == 1) {
          exit
        }
        if (fm_started == 0) {
          print "ERR:1:missing frontmatter"
        }
        if (fm_started == 1 && fm_ended == 0) {
          print "ERR:1:missing closing frontmatter delimiter"
        }
        if (has_name == 0) {
          print "ERR:1:missing required frontmatter key `name`"
        }
        if (has_description == 0) {
          print "ERR:1:missing required frontmatter key `description`"
        }
      }
    ' "$file"
  )"

  if [[ -n "$output" ]]; then
    while IFS= read -r line; do
      [[ -n "$line" ]] || continue
      if [[ "$mode" == "strict" ]]; then
        echo "ERROR $file: $line"
        errors=$((errors + 1))
      else
        echo "WARN  $file: $line"
        warnings=$((warnings + 1))
      fi
    done <<< "$output"
  fi
done < <("$find_cmd" -t f SKILL.md "${roots[@]}" | sort)

echo "Checked files: $checked"
echo "Errors: $errors"
echo "Warnings: $warnings"
echo "Mode: $mode"

if [[ "$mode" == "strict" && "$errors" -gt 0 ]]; then
  exit 1
fi

echo "OpenAI skill format lint passed"
