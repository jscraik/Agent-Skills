#!/usr/bin/env bash
set -euo pipefail

codex_home="${CODEX_HOME:-$HOME/.codex}"
cache_rel="plugins/cache"
strict=0
show_overlap=0
all_marketplaces=0
remediate_cache_skills=0
marketplaces=()
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

usage() {
  cat <<'USAGE'
Usage:
  scripts/check_codex_home_skill_overlap.sh [options]

Compares flat surfaced skills in <codex-home>/skills against plugin-cache
skills in <codex-home>/<cache-rel>/<marketplace>/... and reports overlap.
Overlaps allowlisted by selection policy are excluded from strict failures.

Options:
  --codex-home <path>     Codex home to inspect (default: $CODEX_HOME or ~/.codex)
  --cache-rel <path>      Cache root relative to codex home (default: plugins/cache)
  --marketplace <name>    Marketplace to inspect (repeatable, default: agent-skills-local)
  --all-marketplaces      Inspect every marketplace under cache root
  --show-overlap          Print overlapping skill names when overlap_count > 0
  --strict                Exit non-zero when overlap_count > 0
  --remediate-cache-skills
                          Repair plugin cache root layout under selected marketplaces
                          before overlap computation (flattens nested local/version dirs)
  -h, --help              Show this help
USAGE
}

expand_home_path() {
  local raw_path="$1"
  case "$raw_path" in
    "~")
      printf '%s\n' "$HOME"
      ;;
    ~/*)
      printf '%s/%s\n' "$HOME" "${raw_path#~/}"
      ;;
    *)
      printf '%s\n' "$raw_path"
      ;;
  esac
}

collect_manifest_skill_names() {
  local market_dir="$1"

  python3 - "$market_dir" <<'PY'
import json
import sys
from pathlib import Path

market_dir = Path(sys.argv[1])
for manifest_path in sorted(market_dir.rglob(".codex-plugin/plugin.json")):
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        continue

    skills_value = payload.get("skills")
    declared_relative = "skills"
    if isinstance(skills_value, str) and skills_value.startswith("./") and len(skills_value) > 2:
        declared_relative = skills_value[2:].rstrip("/")
    if not declared_relative:
        continue

    skills_root = manifest_path.parent.parent / declared_relative
    if not skills_root.is_dir():
        continue

    for skill_md in sorted(skills_root.glob("*/SKILL.md")):
        if skill_md.is_file():
            print(skill_md.parent.name)
PY
}

while (($# > 0)); do
  case "${1:-}" in
    --codex-home)
      codex_home="${2:-}"
      shift 2
      ;;
    --cache-rel)
      cache_rel="${2:-}"
      shift 2
      ;;
    --marketplace)
      marketplaces+=("${2:-}")
      shift 2
      ;;
    --all-marketplaces)
      all_marketplaces=1
      shift
      ;;
    --show-overlap)
      show_overlap=1
      shift
      ;;
    --remediate-cache-skills)
      remediate_cache_skills=1
      shift
      ;;
    --strict)
      strict=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$all_marketplaces" -eq 1 && "${#marketplaces[@]}" -gt 0 ]]; then
  echo "Cannot combine --all-marketplaces with --marketplace." >&2
  exit 2
fi

if [[ -z "$cache_rel" ]]; then
  echo "--cache-rel must not be empty." >&2
  exit 2
fi

codex_home="$(expand_home_path "$codex_home")"
flat_root="$codex_home/skills"
cache_root="$codex_home/$cache_rel"

is_safe_codex_path() {
  local path_value="$1"
  [[ -n "$path_value" ]] || return 1
  [[ "$path_value" = /* ]] || return 1
  [[ "$path_value" != "/" ]] || return 1
  case "$path_value" in
    "$HOME"/.codex*|*/.codex/*|*/.codex)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

flat_names_file="$(mktemp "${TMPDIR:-/tmp}/codex-flat-skills.XXXXXX")"
plugin_names_file="$(mktemp "${TMPDIR:-/tmp}/codex-plugin-skills.XXXXXX")"
overlap_names_file="$(mktemp "${TMPDIR:-/tmp}/codex-overlap-skills.XXXXXX")"
selected_markets_file="$(mktemp "${TMPDIR:-/tmp}/codex-selected-markets.XXXXXX")"
allowlisted_overlap_file="$(mktemp "${TMPDIR:-/tmp}/codex-allowlisted-overlap.XXXXXX")"
filtered_overlap_file="$(mktemp "${TMPDIR:-/tmp}/codex-filtered-overlap.XXXXXX")"
trap 'rm -f "$flat_names_file" "$plugin_names_file" "$overlap_names_file" "$selected_markets_file" "$allowlisted_overlap_file" "$filtered_overlap_file"' EXIT

if [[ -d "$flat_root" ]]; then
  find -L "$flat_root" -mindepth 2 -maxdepth 2 -type f -name 'SKILL.md' \
    | awk -F/ '{print $(NF-1)}' \
    | sort -u > "$flat_names_file"
else
  : > "$flat_names_file"
fi

: > "$selected_markets_file"
if [[ "$all_marketplaces" -eq 1 ]]; then
  if [[ -d "$cache_root" ]]; then
    find "$cache_root" -mindepth 1 -maxdepth 1 -type d \
      | awk -F/ '{print $NF}' \
      | sort -u > "$selected_markets_file"
  fi
elif [[ "${#marketplaces[@]}" -gt 0 ]]; then
  printf '%s\n' "${marketplaces[@]}" | sed '/^$/d' | sort -u > "$selected_markets_file"
else
  printf '%s\n' "agent-skills-local" > "$selected_markets_file"
fi

: > "$plugin_names_file"
if [[ "$remediate_cache_skills" -eq 1 ]]; then
  if ! is_safe_codex_path "$codex_home"; then
    echo "Refusing remediation for unexpected --codex-home: $codex_home" >&2
    exit 2
  fi
  if ! is_safe_codex_path "$cache_root"; then
    echo "Refusing remediation for unexpected cache root: $cache_root" >&2
    exit 2
  fi

  while IFS= read -r marketplace_name; do
    [[ -n "$marketplace_name" ]] || continue
    market_dir="$cache_root/$marketplace_name"
    [[ -d "$market_dir" ]] || continue
    while IFS= read -r plugin_dir; do
      [[ -n "$plugin_dir" ]] || continue
      [[ -d "$plugin_dir" ]] || continue
      if [[ "$plugin_dir" != "$cache_root/"* ]]; then
        echo "Refusing remediation for plugin dir outside cache root: $plugin_dir" >&2
        exit 2
      fi
      if [[ -f "$plugin_dir/.codex-plugin/plugin.json" ]]; then
        continue
      fi

      candidate_dir=""
      if [[ -f "$plugin_dir/local/.codex-plugin/plugin.json" ]]; then
        candidate_dir="$plugin_dir/local"
      else
        while IFS= read -r child_dir; do
          [[ -n "$child_dir" ]] || continue
          if [[ -f "$child_dir/.codex-plugin/plugin.json" ]]; then
            candidate_dir="$child_dir"
            break
          fi
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d | sort)
      fi

      [[ -n "$candidate_dir" ]] || continue
      if [[ "$candidate_dir" != "$plugin_dir/"* ]]; then
        echo "Refusing remediation for candidate dir outside plugin dir: $candidate_dir" >&2
        exit 2
      fi
      if [[ "$candidate_dir" == "$plugin_dir/"* ]]; then
        tmp_copy_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-cache-fix.XXXXXX")"
        cp -R "$candidate_dir"/. "$tmp_copy_dir"/
        while IFS= read -r child_dir; do
          [[ -n "$child_dir" ]] || continue
          rm -rf -- "$child_dir"
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -print)
        cp -R "$tmp_copy_dir"/. "$plugin_dir"/
        rm -rf -- "$tmp_copy_dir"
      elif command -v rsync >/dev/null 2>&1; then
        rsync -a --delete --force "$candidate_dir/" "$plugin_dir/"
      else
        tmp_copy_dir="$(mktemp -d "${TMPDIR:-/tmp}/codex-cache-fix.XXXXXX")"
        cp -R "$candidate_dir"/. "$tmp_copy_dir"/
        while IFS= read -r child_dir; do
          [[ -n "$child_dir" ]] || continue
          rm -rf -- "$child_dir"
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -print)
        cp -R "$tmp_copy_dir"/. "$plugin_dir"/
        rm -rf -- "$tmp_copy_dir"
      fi

      while IFS= read -r child_dir; do
        [[ -n "$child_dir" ]] || continue
        if [[ "$child_dir" == "$plugin_dir/.codex-plugin" ]]; then
          continue
        fi
        if [[ -f "$child_dir/.codex-plugin/plugin.json" ]]; then
          rm -rf -- "$child_dir"
        fi
      done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d -print)
    done < <(find "$market_dir" -mindepth 1 -maxdepth 1 -type d -print)
  done < "$selected_markets_file"
fi

while IFS= read -r marketplace_name; do
  [[ -n "$marketplace_name" ]] || continue
  market_dir="$cache_root/$marketplace_name"
  [[ -d "$market_dir" ]] || continue
  collect_manifest_skill_names "$market_dir" >> "$plugin_names_file"
done < "$selected_markets_file"
sort -u "$plugin_names_file" -o "$plugin_names_file"

if [[ -s "$flat_names_file" && -s "$plugin_names_file" ]]; then
  comm -12 "$flat_names_file" "$plugin_names_file" > "$overlap_names_file"
else
  : > "$overlap_names_file"
fi

: > "$allowlisted_overlap_file"
if [[ -f "$repo_root/scripts/selection_policy.py" ]]; then
  python3 - "$repo_root/scripts/selection_policy.py" <<'PY' > "$allowlisted_overlap_file" || true
import json
import subprocess
import sys

policy_script = sys.argv[1]
try:
    raw = subprocess.check_output(
        ["python3", policy_script, "--format", "json"],
        text=True,
    )
    data = json.loads(raw)
except Exception:
    raise SystemExit(0)

seen = set()
for key in ("plugin_visible_router_skill_names", "system_bridge_skill_names"):
    for name in data.get(key, []):
        if isinstance(name, str):
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                print(name)
PY
fi

if [[ -s "$overlap_names_file" && -s "$allowlisted_overlap_file" ]]; then
  grep -Fvx -f "$allowlisted_overlap_file" "$overlap_names_file" > "$filtered_overlap_file" || true
  mv "$filtered_overlap_file" "$overlap_names_file"
fi

flat_count="$(wc -l < "$flat_names_file" | tr -d '[:space:]')"
plugin_count="$(wc -l < "$plugin_names_file" | tr -d '[:space:]')"
overlap_count="$(wc -l < "$overlap_names_file" | tr -d '[:space:]')"
markets_csv="$(paste -sd, "$selected_markets_file" 2>/dev/null || true)"
[[ -n "$markets_csv" ]] || markets_csv="none"

echo "codex_home=$codex_home"
echo "flat_skills_dir=$flat_root"
echo "plugin_cache_root=$cache_root"
echo "marketplaces=$markets_csv"
echo "flat_count=$flat_count"
echo "plugin_cache_count=$plugin_count"
echo "overlap_count=$overlap_count"

if [[ "$overlap_count" -gt 0 && "$show_overlap" -eq 1 ]]; then
  echo "overlap_names:"
  sed 's/^/- /' "$overlap_names_file"
fi

if [[ "$strict" -eq 1 && "$overlap_count" -gt 0 ]]; then
  echo "Skill overlap check failed: flat/runtime skills overlap plugin-cache skills." >&2
  exit 1
fi

echo "Skill overlap check completed."
