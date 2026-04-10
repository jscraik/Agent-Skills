#!/usr/bin/env bash
set -euo pipefail

repo_root=""

usage() {
  cat <<'USAGE'
Usage: scripts/check_plugin_skill_shadowing.sh [--repo-root <path>]

Fails when a flat surfaced skill in .agents/skills shares a name with any
plugin-exported skill under plugins/*/skills/*, excluding policy-allowlisted
plugin router skills intentionally surfaced in flat runtime.
USAGE
}

while (($# > 0)); do
  case "${1:-}" in
    --repo-root)
      repo_root="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ -z "$repo_root" ]; then
  repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
fi
cd "$repo_root"
script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
selection_policy_path="$repo_root/scripts/selection_policy.py"
if [ ! -f "$selection_policy_path" ]; then
  selection_policy_path="$script_dir/selection_policy.py"
fi

plugin_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-skill-names.XXXXXX")"
flat_names_file="$(mktemp "${TMPDIR:-/tmp}/flat-skill-names.XXXXXX")"
overlap_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-flat-overlap.XXXXXX")"
shadowed_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-shadowed-overlap.XXXXXX")"
trap 'rm -f "$plugin_names_file" "$flat_names_file" "$overlap_names_file" "$shadowed_names_file"' EXIT

selection_policy_shell="$(
  python3 "$selection_policy_path" --format shell
)"
if [ -z "$selection_policy_shell" ]; then
  echo "Failed to load selection policy shell exports." >&2
  exit 1
fi
eval "$selection_policy_shell"
plugin_visible_router_skills=("${SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS[@]}")

is_allowlisted_router_skill_name() {
  local skill_name="$1"
  case " ${plugin_visible_router_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}

find -L plugins -type f -path '*/skills/*/SKILL.md' 2>/dev/null \
  | awk -F/ '{print $(NF-1)}' \
  | sort -u > "$plugin_names_file"

if [ -d .agents/skills ]; then
  find -L .agents/skills -mindepth 2 -maxdepth 2 -type f -name 'SKILL.md' 2>/dev/null \
    | awk -F/ '{print $(NF-1)}' \
    | sort -u > "$flat_names_file"
else
  : > "$flat_names_file"
fi

shadowed_count=0
if [ -s "$plugin_names_file" ] && [ -s "$flat_names_file" ]; then
  comm -12 "$plugin_names_file" "$flat_names_file" | sed '/^$/d' > "$overlap_names_file"
  while IFS= read -r overlap_name; do
    if [ -z "$overlap_name" ] || is_allowlisted_router_skill_name "$overlap_name"; then
      continue
    fi
    printf '%s\n' "$overlap_name" >> "$shadowed_names_file"
  done < "$overlap_names_file"
  shadowed_count="$(wc -l < "$shadowed_names_file" | tr -d '[:space:]')"
fi

if [ "$shadowed_count" -gt 0 ]; then
  echo "Plugin-shadowing check failed: standalone flat skills overlap plugin-exported skills." >&2
  echo "Overlapping skill names:" >&2
  sed 's/^/- /' "$shadowed_names_file" >&2
  echo "" >&2
  echo "Run: bash scripts/sync_skills.sh" >&2
  exit 1
fi

echo "Plugin-shadowing check passed: no non-allowlisted flat skills shadow plugin-exported names."
