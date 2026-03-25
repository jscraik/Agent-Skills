#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/normalize_skill_headings.sh [--dry-run]

Normalizes SKILL.md section headings to progressive-disclosure canonical names
and inserts missing required headings with safe placeholders.
USAGE
}

dry_run=0
while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --dry-run)
      dry_run=1
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

roots=(auth backend frontend github interview product utilities)
modified=0
checked=0

find_cmd=""
if command -v fd >/dev/null 2>&1; then
  find_cmd="fd"
elif command -v fdfind >/dev/null 2>&1; then
  find_cmd="fdfind"
else
  find_cmd="find"
fi

append_section_if_missing() {
  local file="$1"
  local heading="$2"
  local body="$3"
  if ! rg -qi "^##[[:space:]]+${heading}([[:space:]]*\\(.+\\))?[[:space:]]*$" "$file"; then
    {
      echo
      echo "## ${heading}"
      echo "$body"
    } >> "$file"
  fi
}

list_skill_files() {
  if [[ "$find_cmd" == "find" ]]; then
    find "${roots[@]}" -type f -name SKILL.md | sort
  else
    "$find_cmd" -t f SKILL.md "${roots[@]}" | sort
  fi
}

while IFS= read -r file; do
  [[ -n "$file" ]] || continue
  checked=$((checked + 1))

  tmp_file="$(mktemp)"
  awk '
    BEGIN {
      IGNORECASE = 1
    }
    {
      line = $0
      if (line ~ /^##[ \t]+Use when([ \t]*\(.+\))?[ \t]*$/) {
        print "## When to use"
      } else if (line ~ /^##[ \t]+Scope and triggers([ \t]*\(.+\))?[ \t]*$/) {
        print "## When to use"
      } else if (line ~ /^##[ \t]+Do not use when([ \t]*\(.+\))?[ \t]*$/) {
        print "## When not to use"
      } else if (line ~ /^##[ \t]+Inputs([ \t]*\(.+\))?[ \t]*$/) {
        print "## Required inputs"
      } else if (line ~ /^##[ \t]+Outputs([ \t]*\(.+\))?[ \t]*$/) {
        print "## Deliverables"
      } else {
        print $0
      }
    }
  ' "$file" > "$tmp_file"

  if ! cmp -s "$file" "$tmp_file"; then
    if [[ "$dry_run" -eq 0 ]]; then
      mv "$tmp_file" "$file"
    else
      rm -f "$tmp_file"
    fi
    modified=$((modified + 1))
  else
    rm -f "$tmp_file"
  fi

  if [[ "$dry_run" -eq 0 ]]; then
    append_section_if_missing "$file" "When to use" "- TODO: define trigger conditions and boundaries."
    append_section_if_missing "$file" "Required inputs" "- TODO: define minimum inputs required to run this skill safely."
    append_section_if_missing "$file" "Deliverables" "- TODO: define concrete outputs this skill must produce."
    append_section_if_missing "$file" "Failure mode" "- TODO: define fail-fast behavior and nearest safe fallback."
    append_section_if_missing "$file" "Gotchas" "- Symptom: TODO. Cause: TODO. Do instead: TODO. Check: TODO."
  fi
done < <(list_skill_files)

echo "Checked files: $checked"
echo "Modified files: $modified"
echo "Dry run: $dry_run"
