#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -P "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

# Use a temporary file for changed paths to avoid bash 3.2 associative-array limitation.
_changed_paths_file="$(mktemp "${TMPDIR:-/tmp}/path-ownership-paths.XXXXXX")"
trap 'rm -f "$_changed_paths_file"' EXIT
: > "$_changed_paths_file"
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
      git diff --name-only "${base_ref}...HEAD" >> "$_changed_paths_file"
      return 0
    fi
  fi

  if [[ "$selected_scope" == "staged" ]]; then
    git diff --name-only --cached >> "$_changed_paths_file"
    return 0
  fi

  {
    git diff --name-only
    git diff --name-only --cached
    git ls-files --others --exclude-standard
  } >> "$_changed_paths_file"

  if [[ -n "${PATH_OWNERSHIP_GUARD_BASE_REF:-}" ]] && git rev-parse --verify "$PATH_OWNERSHIP_GUARD_BASE_REF" >/dev/null 2>&1; then
    git diff --name-only "$PATH_OWNERSHIP_GUARD_BASE_REF...HEAD" >> "$_changed_paths_file"
    return 0
  fi

  if [[ -n "${GITHUB_BASE_REF:-}" ]] && git rev-parse --verify "origin/${GITHUB_BASE_REF}" >/dev/null 2>&1; then
    git diff --name-only "origin/${GITHUB_BASE_REF}...HEAD" >> "$_changed_paths_file"
  fi
}

collect_changed_paths

# Deduplicate and count paths.
_dedup_file="$(mktemp "${TMPDIR:-/tmp}/path-ownership-dedup.XXXXXX")"
trap 'rm -f "$_changed_paths_file" "$_dedup_file"' EXIT
sort -u "$_changed_paths_file" > "$_dedup_file"
sed -i '' '/^$/d' "$_dedup_file" 2>/dev/null || sed -i '/^$/d' "$_dedup_file"

changed_count="$(wc -l < "$_dedup_file" | tr -d '[:space:]')"

if [[ "$changed_count" -eq 0 ]]; then
  echo "[path-ownership] no changed paths detected"
  exit 0
fi

# Helper: check if a path exists in the changed set.
has_path() {
  grep -qxF "$1" "$_dedup_file"
}

mechanics_changed=0
for mechanics_path in \
  "scripts/lifecycle-and-sync/projection_integrity.py" \
  "scripts/lifecycle-and-sync/sync_skills.sh" \
  "scripts/lifecycle-and-sync/sync_projection_trees.sh" \
  "scripts/lifecycle-and-sync/sync_plugin_factory_family.sh" \
  "scripts/lifecycle-and-sync/validate_projection_integrity.sh"; do
  if has_path "$mechanics_path"; then
    mechanics_changed=1
    break
  fi
done

runtime_violations_file="$(mktemp "${TMPDIR:-/tmp}/path-ownership-runtime.XXXXXX")"
cache_violations_file="$(mktemp "${TMPDIR:-/tmp}/path-ownership-cache.XXXXXX")"
trap 'rm -f "$_changed_paths_file" "$_dedup_file" "$runtime_violations_file" "$cache_violations_file"' EXIT
: > "$runtime_violations_file"
: > "$cache_violations_file"

while IFS= read -r path; do
  [[ -z "$path" ]] && continue
  case "$path" in
    .agents/*|.agent/skills/*|skills-antigravity/*|runtime/*)
      printf '%s\n' "$path" >> "$runtime_violations_file"
      ;;
    Plugins/cache/*)
      if [[ "$allow_cache_projection_writes" != "1" ]]; then
        printf '%s -> set PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 for explicit projection-refresh lanes\n' "$path" >> "$cache_violations_file"
        continue
      fi

      if [[ "$path" =~ ^Plugins/cache/[^/]+/([^/]+)/local/(.+)$ ]]; then
        plugin_name="${BASH_REMATCH[1]}"
        rel_path="${BASH_REMATCH[2]}"
        source_path="plugins/${plugin_name}/${rel_path}"
        if has_path "$source_path" || [[ "$mechanics_changed" -eq 1 ]]; then
          :
        else
          printf '%s -> expected source change: %s (or projection mechanics update)\n' "$path" "$source_path" >> "$cache_violations_file"
        fi
      elif [[ "$path" =~ ^Plugins/cache/[^/]+/([^/]+)/(.+)$ ]]; then
        plugin_name="${BASH_REMATCH[1]}"
        rel_path="${BASH_REMATCH[2]}"
        source_path="plugins/${plugin_name}/${rel_path}"
        if has_path "$source_path" || [[ "$mechanics_changed" -eq 1 ]]; then
          :
        else
          printf '%s -> expected source change: %s (or projection mechanics update)\n' "$path" "$source_path" >> "$cache_violations_file"
        fi
      else
        printf '%s -> unmapped cache path\n' "$path" >> "$cache_violations_file"
      fi
      ;;
  esac
done < "$_dedup_file"

runtime_count="$(wc -l < "$runtime_violations_file" | tr -d '[:space:]')"
cache_count="$(wc -l < "$cache_violations_file" | tr -d '[:space:]')"

if [[ "$runtime_count" -eq 0 && "$cache_count" -eq 0 ]]; then
  echo "[path-ownership] pass"
  exit 0
fi

echo "[path-ownership] ERROR: direct edits crossed runtime/projection ownership boundaries." >&2
echo "[path-ownership] Canonical guidance: docs/agents/14-path-ownership-boundaries.md" >&2

if [[ "$runtime_count" -gt 0 ]]; then
  echo "[path-ownership] runtime surfaces must not be edited directly:" >&2
  sed 's/^/  - /' "$runtime_violations_file" >&2
fi

if [[ "$cache_count" -gt 0 ]]; then
  echo "[path-ownership] Plugins/cache edits are blocked by default and require explicit projection-write intent." >&2
  echo "[path-ownership] set PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 only for projection-refresh lanes." >&2
  sed 's/^/  - /' "$cache_violations_file" >&2
fi

echo "[path-ownership] Fix: edit canonical source paths, then regenerate via ask/scripts sync wrappers." >&2
exit 1
