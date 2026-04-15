#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

declare -A changed_map=()
allow_cache_projection_writes="${PATH_OWNERSHIP_ALLOW_CACHE_WRITES:-0}"
if [[ "$allow_cache_projection_writes" != "0" && "$allow_cache_projection_writes" != "1" ]]; then
  echo "[path-ownership] invalid PATH_OWNERSHIP_ALLOW_CACHE_WRITES=${allow_cache_projection_writes} (expected 0 or 1)" >&2
  exit 2
fi
guard_scope="${PATH_OWNERSHIP_GUARD_SCOPE:-auto}"
if [[ "$guard_scope" != "auto" && "$guard_scope" != "staged" && "$guard_scope" != "working" && "$guard_scope" != "base-ref" ]]; then
  echo "[path-ownership] invalid PATH_OWNERSHIP_GUARD_SCOPE=${guard_scope} (expected auto|staged|working|base-ref)" >&2
  exit 2
fi

add_path() {
  local path="$1"
  [[ -z "$path" ]] && return 0
  changed_map["$path"]=1
}

collect_changed_paths() {
  local path=""
  local selected_scope="$guard_scope"
  local base_ref=""

  if [[ "$selected_scope" == "auto" ]]; then
    if [[ -n "${PATH_OWNERSHIP_GUARD_BASE_REF:-}" ]]; then
      selected_scope="base-ref"
    elif [[ "${GITHUB_ACTIONS:-}" == "true" && -n "${GITHUB_BASE_REF:-}" ]]; then
      selected_scope="base-ref"
    else
      selected_scope="staged"
    fi
  fi

  if [[ "$selected_scope" == "base-ref" ]]; then
    if [[ -n "${PATH_OWNERSHIP_GUARD_BASE_REF:-}" ]]; then
      base_ref="$PATH_OWNERSHIP_GUARD_BASE_REF"
    elif [[ -n "${GITHUB_BASE_REF:-}" ]]; then
      base_ref="origin/${GITHUB_BASE_REF}"
    fi

    if [[ -z "$base_ref" ]] || ! git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
      echo "[path-ownership] base-ref scope requested but base ref is unavailable; falling back to staged scope" >&2
      selected_scope="staged"
    else
      while IFS= read -r path; do
        add_path "$path"
      done < <(git diff --name-only "${base_ref}...HEAD")
      return 0
    fi
  fi

  if [[ "$selected_scope" == "staged" ]]; then
    while IFS= read -r path; do
      add_path "$path"
    done < <(git diff --name-only --cached)
    return 0
  fi

  while IFS= read -r path; do
    add_path "$path"
  done < <(git diff --name-only)

  while IFS= read -r path; do
    add_path "$path"
  done < <(git diff --name-only --cached)

  while IFS= read -r path; do
    add_path "$path"
  done < <(git ls-files --others --exclude-standard)

  if [[ -n "${PATH_OWNERSHIP_GUARD_BASE_REF:-}" ]] && git rev-parse --verify "$PATH_OWNERSHIP_GUARD_BASE_REF" >/dev/null 2>&1; then
    while IFS= read -r path; do
      add_path "$path"
    done < <(git diff --name-only "$PATH_OWNERSHIP_GUARD_BASE_REF...HEAD")
    return 0
  fi

  if [[ -n "${GITHUB_BASE_REF:-}" ]] && git rev-parse --verify "origin/${GITHUB_BASE_REF}" >/dev/null 2>&1; then
    while IFS= read -r path; do
      add_path "$path"
    done < <(git diff --name-only "origin/${GITHUB_BASE_REF}...HEAD")
  fi
}

collect_changed_paths

if [[ "${#changed_map[@]}" -eq 0 ]]; then
  echo "[path-ownership] no changed paths detected"
  exit 0
fi

mechanics_changed=0
for mechanics_path in \
  "Infrastructure/scripts/projection_integrity.py" \
  "Infrastructure/scripts/sync_skills.sh" \
  "Infrastructure/scripts/sync_projection_trees.sh" \
  "Infrastructure/scripts/sync_plugin_factory_family.sh" \
  "Infrastructure/scripts/validate_projection_integrity.sh"; do
  if [[ -n "${changed_map[$mechanics_path]:-}" ]]; then
    mechanics_changed=1
    break
  fi
done

declare -a runtime_violations=()
declare -a cache_violations=()

for path in "${!changed_map[@]}"; do
  case "$path" in
    .agents/*|.agent/skills/*|skills-antigravity/*|runtime/*)
      runtime_violations+=("$path")
      ;;
    Plugins/cache/*)
      if [[ "$allow_cache_projection_writes" != "1" ]]; then
        cache_violations+=("$path -> set PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 for explicit projection-refresh lanes")
        continue
      fi

      if [[ "$path" =~ ^Plugins/cache/[^/]+/([^/]+)/local/(.+)$ ]]; then
        plugin_name="${BASH_REMATCH[1]}"
        rel_path="${BASH_REMATCH[2]}"
        source_path="Plugins/${plugin_name}/${rel_path}"
        if [[ -n "${changed_map[$source_path]:-}" || "$mechanics_changed" -eq 1 ]]; then
          :
        else
          cache_violations+=("$path -> expected source change: $source_path (or projection mechanics update)")
        fi
      elif [[ "$path" =~ ^Plugins/cache/[^/]+/([^/]+)/(.+)$ ]]; then
        plugin_name="${BASH_REMATCH[1]}"
        rel_path="${BASH_REMATCH[2]}"
        source_path="Plugins/${plugin_name}/${rel_path}"
        if [[ -n "${changed_map[$source_path]:-}" || "$mechanics_changed" -eq 1 ]]; then
          :
        else
          cache_violations+=("$path -> expected source change: $source_path (or projection mechanics update)")
        fi
      else
        cache_violations+=("$path -> unmapped cache path")
      fi
      ;;
  esac
done

if [[ "${#runtime_violations[@]}" -eq 0 && "${#cache_violations[@]}" -eq 0 ]]; then
  echo "[path-ownership] pass"
  exit 0
fi

echo "[path-ownership] ERROR: direct edits crossed runtime/projection ownership boundaries." >&2
echo "[path-ownership] Canonical guidance: Docs/agents/14-path-ownership-boundaries.md" >&2

if [[ "${#runtime_violations[@]}" -gt 0 ]]; then
  echo "[path-ownership] runtime surfaces must not be edited directly:" >&2
  printf '  - %s\n' "${runtime_violations[@]}" >&2
fi

if [[ "${#cache_violations[@]}" -gt 0 ]]; then
  echo "[path-ownership] Plugins/cache edits are blocked by default and require explicit projection-write intent." >&2
  echo "[path-ownership] set PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 only for projection-refresh lanes." >&2
  printf '  - %s\n' "${cache_violations[@]}" >&2
fi

echo "[path-ownership] Fix: edit canonical source paths, then regenerate via ask/scripts sync wrappers." >&2
exit 1
