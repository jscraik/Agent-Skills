#!/usr/bin/env bash
set -euo pipefail

repo_root=""

usage() {
  cat <<'USAGE'
Usage: Infrastructure/scripts/validation-and-linting/check_plugin_skill_shadowing.sh [--repo-root <path>]

Fails when a flat surfaced skill in .agents/skills shares a name with any
plugin-exported skill under Plugins/*/skills/*. Hidden `.system` bridge aliases
are the only allowlisted overlap.
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
  script_dir_default="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
  if repo_root="$(git -C "$script_dir_default/../.." rev-parse --show-toplevel 2>/dev/null)"; then
    :
  else
    repo_root="$(cd -P "$script_dir_default/../.." && pwd -P)"
  fi
fi
cd "$repo_root"
script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
selection_policy_path="$repo_root/Infrastructure/scripts/lifecycle-and-sync/selection_policy.py"
if [ ! -f "$selection_policy_path" ]; then
  selection_policy_path="$script_dir/../lifecycle-and-sync/selection_policy.py"
fi

plugin_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-skill-names.XXXXXX")"
flat_names_file="$(mktemp "${TMPDIR:-/tmp}/flat-skill-names.XXXXXX")"
overlap_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-flat-overlap.XXXXXX")"
shadowed_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-shadowed-overlap.XXXXXX")"
system_bridge_names_file="$(mktemp "${TMPDIR:-/tmp}/system-bridge-skill-names.XXXXXX")"
root_skill_names_file="$(mktemp "${TMPDIR:-/tmp}/root-skill-set-names.XXXXXX")"
command_handle_names_file="$(mktemp "${TMPDIR:-/tmp}/command-handle-skill-names.XXXXXX")"
trap 'rm -f "$plugin_names_file" "$flat_names_file" "$overlap_names_file" "$shadowed_names_file" "$system_bridge_names_file" "$root_skill_names_file" "$command_handle_names_file"' EXIT

selection_policy_shell="$(
  python3 "$selection_policy_path" --format shell
)"
if [ -z "$selection_policy_shell" ]; then
  echo "Failed to load selection policy shell exports." >&2
  exit 1
fi
eval "$selection_policy_shell"
# Safely handle empty arrays under bash 3.x where ${arr[@]} with set -u
# fails when the array is empty.  Re-parse the variable line from the eval output.
is_allowlisted_overlap_skill_name() {
  local skill_name="$1"
  local _rv_list=""
  _rv_list="${system_bridge_skill_names[*]:-}"
  if [[ -n "$_rv_list" ]] && [[ " $_rv_list " == *" $skill_name "* ]]; then
    return 0
  fi
  return 1
}

is_rooted_projection_active() {
  [ -s "$root_skill_names_file" ] || return 1
  while IFS= read -r root_skill_name; do
    [ -n "$root_skill_name" ] || continue
    if [ -f ".agents/skills/$root_skill_name/SKILL.md" ]; then
      return 0
    fi
  done < "$root_skill_names_file"
  return 1
}

is_root_skill_set_name() {
  local skill_name="$1"
  [ -s "$root_skill_names_file" ] || return 1
  grep -Fxq "$skill_name" "$root_skill_names_file"
}

is_command_handle_skill_name() {
  local skill_name="$1"
  [ -s "$command_handle_names_file" ] || return 1
  grep -Fxq "$skill_name" "$command_handle_names_file"
}

# Only treat bridge names as intentional when the top-level skill path is a
# real symlink into `.system/<name>`; a plain directory with the same name
# should still count as shadowing.
if [ -d .agents/skills/.system ]; then
  while IFS= read -r bridge_path; do
    [ -n "$bridge_path" ] || continue
    if [ -L "$bridge_path" ]; then
      bridge_name="$(basename "$bridge_path")"
      bridge_target="$(readlink "$bridge_path" 2>/dev/null || true)"
      if [ "$bridge_target" = ".system/$bridge_name" ]; then
        printf '%s\n' "$bridge_name" >> "$system_bridge_names_file"
      fi
    fi
  done < <(find .agents/skills -mindepth 1 -maxdepth 1 -type l 2>/dev/null | sort)
fi

system_bridge_skill_names=()
if [ -s "$system_bridge_names_file" ]; then
  while IFS= read -r line; do
    system_bridge_skill_names+=("$line")
  done < "$system_bridge_names_file"
fi

for root_skill_name in "${SELECTION_POLICY_ROOT_SKILL_SETS[@]:-}"; do
  printf '%s\n' "$root_skill_name" >> "$root_skill_names_file"
done

if [ -f ".skillsets/command-surface.json" ]; then
  python3 - <<'PY' > "$command_handle_names_file"
import json
from pathlib import Path

path = Path(".skillsets/command-surface.json")
payload = json.loads(path.read_text(encoding="utf-8"))
for handle in payload.get("handles", []):
    if not isinstance(handle, dict):
        continue
    if handle.get("kind") == "skill" and handle.get("command_handle_path") and handle.get("handle"):
        print(handle["handle"])
PY
fi

: > "$plugin_names_file"
for plugins_root in Plugins plugins; do
  [ -d "$plugins_root" ] || continue
  while IFS= read -r plugin_skills_root; do
    [ -d "$plugin_skills_root" ] || continue
    find -L "$plugin_skills_root" -mindepth 2 -maxdepth 3 -type f -name 'SKILL.md' 2>/dev/null \
      | awk -F/ '{print $(NF-1)}' >> "$plugin_names_file"
  done < <(find -L "$plugins_root" -mindepth 2 -maxdepth 2 -type d -name skills 2>/dev/null | sort)
done
sort -u "$plugin_names_file" -o "$plugin_names_file"

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
    if [ -z "$overlap_name" ] || is_allowlisted_overlap_skill_name "$overlap_name"; then
      continue
    fi
    if is_rooted_projection_active && is_root_skill_set_name "$overlap_name"; then
      continue
    fi
    if is_rooted_projection_active && is_command_handle_skill_name "$overlap_name"; then
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
  echo "Run: bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh" >&2
  exit 1
fi

echo "Plugin-shadowing check passed: no non-allowlisted flat skills shadow plugin-exported names."
