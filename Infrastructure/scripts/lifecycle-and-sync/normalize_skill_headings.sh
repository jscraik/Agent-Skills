#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/lifecycle-and-sync/normalize_skill_headings.sh [--dry-run]

Normalizes SKILL.md section headings to progressive-disclosure canonical names
and inserts missing required headings with actionable starter guidance.
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

roots=("Skills" "skills-antigravity" "skills-system" "plugins/harness-engineering" "plugins/plugin-factory" "plugins/skill-factory")
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
    append_section_if_missing "$file" "When to use" "- Use when the request clearly matches this skill's owned workflow and expected outputs."
    append_section_if_missing "$file" "Required inputs" "- Confirm goal, constraints, and required paths or URLs before execution."
    append_section_if_missing "$file" "Deliverables" "- Produce concrete outputs with exact paths, commands run, and verification evidence."
    append_section_if_missing "$file" "Failure mode" "- Stop at the first blocker, report root cause, and provide the safest next command."
    append_section_if_missing "$file" "Gotchas" "- Symptom: ambiguous scope. Cause: missing constraints. Do instead: ask one routing question. Check: plan and output contract are explicit."
  fi
done < <(list_skill_files)

echo "Checked files: $checked"
echo "Modified files: $modified"
echo "Dry run: $dry_run"
