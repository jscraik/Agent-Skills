#!/usr/bin/env bash
set -euo pipefail

repo_root=""

usage() {
  cat <<'USAGE'
Usage: scripts/check_plugin_skill_shadowing.sh [--repo-root <path>]

Fails when a flat surfaced skill in .agents/skills shares a name with any
plugin-exported skill under plugins/*/skills/*.
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

plugin_names_file="$(mktemp "${TMPDIR:-/tmp}/plugin-skill-names.XXXXXX")"
flat_names_file="$(mktemp "${TMPDIR:-/tmp}/flat-skill-names.XXXXXX")"
trap 'rm -f "$plugin_names_file" "$flat_names_file"' EXIT

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
  shadowed_count="$(comm -12 "$plugin_names_file" "$flat_names_file" | sed '/^$/d' | wc -l | tr -d '[:space:]')"
fi

if [ "$shadowed_count" -gt 0 ]; then
  echo "Plugin-shadowing check failed: standalone flat skills overlap plugin-exported skills." >&2
  echo "Overlapping skill names:" >&2
  comm -12 "$plugin_names_file" "$flat_names_file" | sed '/^$/d' | sed 's/^/- /' >&2
  echo "" >&2
  echo "Run: bash scripts/sync_skills.sh" >&2
  exit 1
fi

echo "Plugin-shadowing check passed: no standalone flat skills shadow plugin-exported names."
