#!/usr/bin/env bash
set -euo pipefail

timeout_seconds="${SYNC_SKILLS_TIMEOUT_SECONDS:-300}"
lock_stale_after_seconds="${SYNC_SKILLS_LOCK_STALE_AFTER_SECONDS:-900}"
sync_scope="${SYNC_SKILLS_SCOPE:-workspace}"
projection_mode_cli=""
plugin_cache_refresh="${SYNC_SKILLS_PLUGIN_CACHE_REFRESH:-auto}"
dry_run=0
lock_dir="${TMPDIR:-/tmp}/agent-skills-sync.lock"
lock_pid_file="$lock_dir/pid"
lock_owned=0
watchdog_pid=""
timeout_marker="${TMPDIR:-/tmp}/agent-skills-sync-timeout.$$"

usage() {
  cat <<'USAGE'
Usage:
  Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh [--timeout-seconds <int>] [--workspace|--user|--project-local] [--projection <mode>] [--plugin-cache-refresh <auto|skip|only>] [--dry-run]

Regenerates skill/plugin symlinks and SKILL.md index for this repository.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --timeout-seconds)
      if [[ -z "${2:-}" ]] || [[ "${2:-}" == --* ]]; then
        echo "Missing value for --timeout-seconds" >&2
        usage
        exit 2
      fi
      timeout_seconds="${2:-}"
      shift 2
      ;;
    --project-local)
      sync_scope="workspace"
      shift
      ;;
    --workspace)
      sync_scope="workspace"
      shift
      ;;
    --user)
      sync_scope="user"
      shift
      ;;
    --projection)
      if [[ -z "${2:-}" ]] || [[ "${2:-}" == --* ]]; then
        echo "Missing value for --projection" >&2
        usage
        exit 2
      fi
      projection_mode_cli="${2:-}"
      shift 2
      ;;
    --plugin-cache-refresh)
      if [[ -z "${2:-}" ]] || [[ "${2:-}" == --* ]]; then
        echo "Missing value for --plugin-cache-refresh" >&2
        usage
        exit 2
      fi
      plugin_cache_refresh="${2:-}"
      shift 2
      ;;
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

if ! [[ "$timeout_seconds" =~ ^[0-9]+$ ]] || [[ "$timeout_seconds" -lt 30 ]]; then
  echo "Invalid --timeout-seconds value: $timeout_seconds (expected integer >= 30)" >&2
  exit 2
fi
if ! [[ "$lock_stale_after_seconds" =~ ^[0-9]+$ ]] || [[ "$lock_stale_after_seconds" -lt 30 ]]; then
  echo "Invalid SYNC_SKILLS_LOCK_STALE_AFTER_SECONDS: $lock_stale_after_seconds (expected integer >= 30)" >&2
  exit 2
fi

# Normalize legacy alias before validation so env vars like SYNC_SKILLS_SCOPE=project-local work.
if [[ "$sync_scope" == "project-local" ]]; then
  sync_scope="workspace"
fi

case "$sync_scope" in
  workspace|user)
    ;;
  *)
    echo "Invalid sync scope: $sync_scope (expected workspace or user; project-local is a legacy alias for workspace)" >&2
    exit 2
    ;;
esac

case "$plugin_cache_refresh" in
  auto|skip|only)
    ;;
  *)
    echo "Invalid --plugin-cache-refresh value: $plugin_cache_refresh (expected auto, skip, or only)" >&2
    exit 2
    ;;
esac

script_dir="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
if repo_root="$(git -C "$script_dir/../.." rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  repo_root="$(cd -P "$script_dir/../.." && pwd -P)"
fi
cd "$repo_root"

# acquire_sync_lock acquires an exclusive filesystem lock at $lock_dir to ensure only one sync run runs at a time, waits briefly for in-progress initialisation, and reclaims stale locks (with PID or based on directory mtime) before failing.
acquire_sync_lock() {
  local existing_pid=""
  local lock_mtime=""
  local lock_age_seconds="unknown"

  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\n' "$$" > "$lock_pid_file"
    lock_owned=1
    return 0
  fi

  if [[ -f "$lock_pid_file" ]]; then
    existing_pid="$(cat "$lock_pid_file" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "sync_skills already running (pid=$existing_pid); exiting without duplicate work."
      exit 0
    fi
    echo "Reclaiming stale sync lock from pid=${existing_pid:-unknown}."
    rm -rf -- "$lock_dir"
    if mkdir "$lock_dir" 2>/dev/null; then
      printf '%s\n' "$$" > "$lock_pid_file"
      lock_owned=1
      return 0
    fi
    echo "Unable to acquire sync lock at $lock_dir" >&2
    exit 1
  fi

  # A lock directory without a pid file can occur briefly while another
  # process initializes ownership. Treat fresh locks as in-progress and avoid
  # forcing concurrent sync runs.
  sleep 1
  if [[ -f "$lock_pid_file" ]]; then
    existing_pid="$(cat "$lock_pid_file" 2>/dev/null || true)"
    if [[ -n "$existing_pid" ]] && kill -0 "$existing_pid" 2>/dev/null; then
      echo "sync_skills already running (pid=$existing_pid); exiting without duplicate work."
      exit 0
    fi
  fi
  lock_mtime="$(
    stat -f '%m' "$lock_dir" 2>/dev/null || stat -c '%Y' "$lock_dir" 2>/dev/null || true
  )"
  if [[ -n "$lock_mtime" ]]; then
    lock_age_seconds="$(( $(date +%s) - lock_mtime ))"
    if (( lock_age_seconds < lock_stale_after_seconds )); then
      echo "sync_skills lock is still initializing (age=${lock_age_seconds}s); exiting without duplicate work."
      exit 0
    fi
  fi

  echo "Reclaiming stale sync lock without pid file (age=${lock_age_seconds}s)."
  rm -rf -- "$lock_dir"
  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\n' "$$" > "$lock_pid_file"
    lock_owned=1
    return 0
  fi

  echo "Unable to acquire sync lock at $lock_dir" >&2
  exit 1
}

release_sync_lock() {
  if [[ "$lock_owned" -eq 1 ]]; then
    rm -rf -- "$lock_dir"
    lock_owned=0
  fi
}

start_watchdog() {
  python3 - "$timeout_seconds" "$$" "$timeout_marker" <<'PY' &
import os
import signal
import sys
import time

timeout_seconds = int(sys.argv[1])
parent_pid = int(sys.argv[2])
timeout_marker = sys.argv[3]
time.sleep(timeout_seconds)
with open(timeout_marker, "w", encoding="utf-8") as marker:
    marker.write("timeout\n")
print(f"[ERROR] sync_skills timed out after {timeout_seconds}s", file=sys.stderr, flush=True)
try:
    os.kill(parent_pid, signal.SIGTERM)
except ProcessLookupError:
    pass
PY
  watchdog_pid="$!"
}

stop_watchdog() {
  if [[ -n "$watchdog_pid" ]]; then
    kill "$watchdog_pid" 2>/dev/null || true
    wait "$watchdog_pid" 2>/dev/null || true
    watchdog_pid=""
  fi
  rm -f -- "$timeout_marker"
}

handle_timeout_signal() {
  if [[ -f "$timeout_marker" ]]; then
    rm -f -- "$timeout_marker"
    exit 124
  fi
  exit 143
}

trap handle_timeout_signal TERM

projection_args=(--format shell)
if [ -n "$projection_mode_cli" ]; then
  projection_args+=(--mode "$projection_mode_cli")
fi
projection_policy_shell="$(
  python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_engine.py" "${projection_args[@]}" 2>&1
)" || true
if python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_engine.py" "${projection_args[@]}" >/dev/null 2>&1; then
  # Only eval on success; validate output is non-empty and contains safe patterns.
  projection_policy_shell="$(python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_engine.py" "${projection_args[@]}")"
  if [ -z "$projection_policy_shell" ]; then
    echo "Projection engine returned empty output." >&2
    exit 2
  fi
  # Basic validation: ensure output contains only expected variable assignments.
  if ! echo "$projection_policy_shell" | grep -qE '^[A-Z_]+=' || echo "$projection_policy_shell" | grep -qEv '^[A-Z_]+='; then
    echo "Projection engine output does not match expected format." >&2
    exit 2
  fi
  eval "$projection_policy_shell"
else
  # Extract SYNC_SKILLS_PROJECTION_ERROR_MESSAGE from projection engine output
  error_message="$(
    printf '%s\n' "$projection_policy_shell" | python3 -c '
import shlex
import sys

for line in sys.stdin:
    if not line.startswith("SYNC_SKILLS_PROJECTION_ERROR_MESSAGE="):
        continue
    rhs = line.split("=", 1)[1].strip()
    try:
        tokens = shlex.split(rhs, posix=True)
        print(tokens[0] if tokens else "")
    except ValueError:
        print(rhs.strip("\"'\''"))
    break
'
  )"
  if [ -n "$error_message" ]; then
    echo "$error_message" >&2
  else
    echo "Invalid projection mode." >&2
  fi
  exit 2
fi
# Keep the shell entrypoint as a compatibility wrapper while the projection-aware
# ask implementation owns dry-run previews and rooted runtime mutation. Flat
# workspace/user non-dry-run sync remains on the legacy shell path below.
if [[ "$dry_run" == "1" || "${SYNC_SKILLS_RESOLVED_PROJECTION_MODE:-flat}" != "flat" || "$plugin_cache_refresh" != "auto" ]]; then
  ask_sync_args=(skills sync --scope "$sync_scope" --projection "${SYNC_SKILLS_RESOLVED_PROJECTION_MODE:-flat}")
  if [[ "$dry_run" == "1" ]]; then
    ask_sync_args+=(--dry-run)
  fi
  ask_sync_args+=(--plugin-cache-refresh "$plugin_cache_refresh")
  cleanup_delegated_sync() {
    stop_watchdog
    release_sync_lock
  }
  if [[ "$dry_run" != "1" ]]; then
    acquire_sync_lock
  fi
  trap cleanup_delegated_sync EXIT
  start_watchdog
  python3 "$repo_root/bin/ask" "${ask_sync_args[@]}"
  exit $?
fi

selection_policy_shell="$(
  python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/selection_policy.py" --format shell
)"
if [ -z "$selection_policy_shell" ]; then
  echo "Failed to load selection policy shell exports." >&2
  exit 1
fi
eval "$selection_policy_shell"

acquire_sync_lock
start_watchdog

skills_dir="$repo_root/.agents/skills"
plugins_dir="$repo_root/plugins"
runtime_cache_root="$repo_root/.agents/plugins-runtime/cache"
system_skills_dir="$repo_root/skills-system"

mkdir -p "$skills_dir"
mkdir -p "$plugins_dir"

repo_root_real="$(cd "$repo_root" && pwd -P)"

# Return success when sync phases can create and remove a file in the target
# directory. Plain `-w` checks can be misleading in sandboxed runs, so use the
# can_mutate_sync_dir verifies the given directory can be created and written to by creating the directory, writing a probe file inside it, and removing that probe file.
can_mutate_sync_dir() {
  local dir="$1"
  local probe=""

  if ! mkdir -p "$dir" 2>/dev/null; then
    return 1
  fi

  probe="$dir/.sync-skills-write-test.$$"
  if ! ( : > "$probe" ) 2>/dev/null; then
    return 1
  fi

  if ! rm -f -- "$probe" 2>/dev/null; then
    return 1
  fi
  return 0
}

# skip_unwritable_sync_phase logs a warning that the given directory is not writable and that the named sync phase will be skipped to avoid sandbox rsync/cache cleanup noise.
skip_unwritable_sync_phase() {
  local label="$1"
  local dir="$2"
  echo "[WARN] $dir is not writable; skipping $label to avoid sandbox rsync/cache cleanup noise."
}

# Flag semantics:
# - flat_projection_rebuilt is pessimistic: downstream skill publication waits
#   until the flat projection is confirmed rebuilt.
# - runtime_cache_fresh is pessimistic: downstream cache publication waits
#   until every runtime cache rebuild/projection step confirms it can run.
skills_dir_writable=0
flat_projection_rebuilt=0
runtime_cache_fresh=0
runtime_cache_rebuild_blocked=0
mark_runtime_cache_stale() {
  runtime_cache_fresh=0
  runtime_cache_rebuild_blocked=1
}
if can_mutate_sync_dir "$skills_dir"; then
  skills_dir_writable=1
else
  skip_unwritable_sync_phase "flat runtime skill projection" "$skills_dir"
fi

# Remove legacy aggregation directories that could cause duplicate skills in IDE panels.
# sync-symlink/ was created by an older version of this script under a different name.
if [ -d "$repo_root/sync-symlink" ]; then
  echo "Removing legacy skill aggregation dir: $repo_root/sync-symlink"
  rm -rf -- "$repo_root/sync-symlink"
fi

cleanup_paths=()
cleanup_on_exit() {
  local path=""
  stop_watchdog
  for path in "${cleanup_paths[@]:-}"; do
    if [ -n "$path" ] && [ -d "$path" ]; then
      rm -rf -- "$path"
    fi
  done
  release_sync_lock
}
trap cleanup_on_exit EXIT

# Preserve upstream-managed system skills in a repo-level store, then expose
# them through a hidden `.system` entry so only the hidden system copy remains.
mkdir -p "$system_skills_dir"
touch "$system_skills_dir/.codex-system-skills.marker"
if [ -d "$skills_dir/.system" ] && [ ! -L "$skills_dir/.system" ]; then
  if [ ! -w "$skills_dir/.system" ]; then
    echo "[WARN] $skills_dir/.system is not writable; skipping preservation to avoid blocking sync."
  else
    if command -v rsync >/dev/null 2>&1; then
      if ! rsync -a "$skills_dir/.system/" "$system_skills_dir/"; then
        echo "[WARN] Failed to preserve system skills into $system_skills_dir (continuing anyway)."
      fi
    else
      mkdir -p "$system_skills_dir"
      cp -a "$skills_dir/.system"/. "$system_skills_dir"/ 2>/dev/null || true
    fi
    if ! rm -rf "$skills_dir/.system"; then
      echo "[WARN] Unable to remove $skills_dir/.system after preservation (continuing anyway)."
    fi
  fi
fi

# Reassert projection-managed bridge aliases after preserving `.system` into
# `skills-system/`. Without this, preserved runtime copies can replace the
# canonical plugin/skill-factory aliases with real directories and leave
# projection integrity in drift until a manual repair pass.
if [ "$skills_dir_writable" = "1" ]; then
  python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py" sync --scope skill-factory >/dev/null
  python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py" sync --scope plugin-factory >/dev/null
else
  echo "[INFO] Skipped bridge alias projection repair because $skills_dir is not writable."
fi

# Remove stale symlinks only (keep any real files that might be intentional).
if [ "$skills_dir_writable" = "1" ]; then
  find "$skills_dir" -maxdepth 1 -type l -exec rm -f {} +
else
  echo "[WARN] $skills_dir is not writable; skipping stale symlink cleanup."
fi

# Remove hidden/internal skills and skills outside the default policy from the
# flat runtime surface so they do not appear as user-selectable skills in Codex.
# Lifecycle bridge skills stay available through the hidden `.system` lane.
hidden_flat_skills=("${SELECTION_POLICY_HIDDEN_FLAT_SKILLS[@]}")
default_visible_flat_skills=("${SELECTION_POLICY_DEFAULT_VISIBLE_FLAT_SKILLS[@]}")
plugin_visible_router_skills=("${SELECTION_POLICY_PLUGIN_VISIBLE_ROUTER_SKILLS[@]}")
plugin_hidden_lane_skills=("${SELECTION_POLICY_PLUGIN_HIDDEN_LANE_SKILLS[@]}")
if declare -p SELECTION_POLICY_SYSTEM_BRIDGE_SKILLS >/dev/null 2>&1; then
  system_bridge_skills=("${SELECTION_POLICY_SYSTEM_BRIDGE_SKILLS[@]}")
else
  system_bridge_skills=("plugin-creator" "plugin-installer" "skill-creator" "skill-installer")
fi
plugin_router_skill_names=()
plugin_router_skill_dirs=()
router_collision_count=0
# is_hidden_flat_skill_name returns success (exit code 0) if the supplied skill name is listed in the hidden_flat_skills array, failure (exit code 1) otherwise.
is_hidden_flat_skill_name() {
  local skill_name="$1"
  case " ${hidden_flat_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}
# is_default_visible_flat_skill_name returns success (exit code 0) when the
# supplied skill name belongs to the default flat-runtime surface.
is_default_visible_flat_skill_name() {
  local skill_name="$1"
  case " ${default_visible_flat_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}
# is_plugin_visible_router_skill_name checks whether the given skill name is present in the plugin_visible_router_skills array and returns success (0) if it is.
is_plugin_visible_router_skill_name() {
  local skill_name="$1"
  case " ${plugin_visible_router_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}
# is_plugin_hidden_lane_skill_name checks whether the given skill name is present in the plugin_hidden_lane_skills array and returns success (`0`) if present and failure (`1`) otherwise.
is_plugin_hidden_lane_skill_name() {
  local skill_name="$1"
  case " ${plugin_hidden_lane_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}
# register_plugin_router_skill_source registers a mapping from a router-visible plugin skill name to its discovered directory and detects name collisions.
# register_plugin_router_skill_source registers a plugin-visible router skill name with its discovered directory and detects collisions.
# If the same skill name is already registered with a different directory, prints collision details to stderr and returns 1; returns 0 on success.
register_plugin_router_skill_source() {
  local skill_name="$1"
  local discovered_dir="$2"
  local idx=""
  for idx in "${!plugin_router_skill_names[@]}"; do
    if [ "${plugin_router_skill_names[$idx]}" != "$skill_name" ]; then
      continue
    fi
    if [ "${plugin_router_skill_dirs[$idx]}" = "$discovered_dir" ]; then
      return 0
    fi
    echo "[ERROR] Plugin-visible router skill collision: $skill_name" >&2
    echo "        first:  ${plugin_router_skill_dirs[$idx]}" >&2
    echo "        second: $discovered_dir" >&2
    return 1
  done
  plugin_router_skill_names+=("$skill_name")
  plugin_router_skill_dirs+=("$discovered_dir")
  return 0
}
if [ "$skills_dir_writable" = "1" ]; then
  for hidden_skill in "${hidden_flat_skills[@]}"; do
    if [ -e "$skills_dir/$hidden_skill" ]; then
      if rm -rf -- "${skills_dir:?}/${hidden_skill:?}"; then
        echo "Removed hidden flat skill: $hidden_skill"
      else
        echo "[WARN] Could not remove hidden skill $hidden_skill at $skills_dir (continuing anyway)."
      fi
    fi
  done
fi

# find_skill_files_with_policy lists SKILL.md files under the given root while excluding any paths that match SELECTION_POLICY_EXCLUDED_SEGMENTS and prints matching paths to stdout.
find_skill_files_with_policy() {
  local root="$1"
  local segment=""
  local -a find_args=()

  for segment in "${SELECTION_POLICY_EXCLUDED_SEGMENTS[@]}"; do
    find_args+=(-path "*/$segment/*" -prune -o)
  done

  find -L "$root" "${find_args[@]}" -name "SKILL.md" -print
}

skill_files_cmd() {
  local root=""
  for root in "${SELECTION_POLICY_REPO_SCAN_ROOTS[@]}"; do
    [ -d "$root" ] || continue
    find_skill_files_with_policy "$root"
  done

  local plugin_skills_root=""
  local plugin_glob=""
  local nested_glob=""
  for plugin_glob in ${SELECTION_POLICY_PLUGIN_SKILL_ROOT_GLOB}; do
    for plugin_skills_root in ${plugin_glob}; do
      [ -d "$plugin_skills_root" ] || continue
      find_skill_files_with_policy "$plugin_skills_root"
    done

    if [[ "$plugin_glob" == */\*/skills ]]; then
      nested_glob="${plugin_glob%/*/skills}/*/*/skills"
      for plugin_skills_root in ${nested_glob}; do
        [ -d "$plugin_skills_root" ] || continue
        find_skill_files_with_policy "$plugin_skills_root"
      done
    fi
  done
}

# Include supplemental skills that intentionally live outside canonical
# category folders.
extra_skill_files_cmd() {
  if [ -d "./.agents/skills" ]; then
    while IFS= read -r extra_skill; do
      if git ls-files --error-unmatch "$extra_skill" >/dev/null 2>&1; then
        echo "$extra_skill"
      fi
    done < <(find -L "./.agents/skills" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print)
  fi
  if [ -d "./skills" ]; then
    while IFS= read -r extra_skill; do
      # `./skills` may include vendored git submodules. Files inside those
      # submodules are intentionally not visible to `git ls-files` in the
      # parent repo, so do not require a tracked-file check here.
      case "$extra_skill" in
        ./skills/.system/*) continue ;;
      esac
      echo "$extra_skill"
    done < <(find -L "./skills" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print)
  fi
}

# Emit skill files in deterministic precedence order:
# 1) canonical category folders
# 2) supplemental locations
# Deduplicate by skill name (folder basename), keeping the first match.
all_skill_files_cmd() {
  {
    skill_files_cmd | sort
    extra_skill_files_cmd | sort
  } | awk '
    {
      skill = $0
      sub(/\/SKILL\.md$/, "", skill)
      sub(/^.*\//, "", skill)
      if (!seen[skill]++) {
        print $0
      }
    }
  '
}

# Extract `metadata.skill-type` (or `metadata.skill_type`) from frontmatter.
# Returns empty when the field is not present.
extract_skill_type() {
  local skill_path="$1"
  awk '
    function ltrim(s) { sub(/^[ \t]+/, "", s); return s }
    function rtrim(s) { sub(/[ \t]+$/, "", s); return s }
    function trim(s) { return rtrim(ltrim(s)) }
    BEGIN { in_fm = 0; in_meta = 0 }
    /^---[ \t]*$/ {
      if (in_fm == 0) { in_fm = 1; next }
      exit
    }
    in_fm == 0 { next }
    /^[A-Za-z0-9_-]+:[ \t]*/ {
      key = $0
      sub(/:.*/, "", key)
      if (key == "metadata") { in_meta = 1; next }
      if (in_meta == 1) { in_meta = 0 }
    }
    in_meta == 1 && /^[ \t]+(skill-type|skill_type):[ \t]*/ {
      rest = $0
      sub(/^[ \t]+(skill-type|skill_type):[ \t]*/, "", rest)
      rest = trim(rest)
      if (rest ~ /^["\047].*["\047]$/) {
        q1 = substr(rest, 1, 1)
        q2 = substr(rest, length(rest), 1)
        if (q1 == q2) {
          rest = substr(rest, 2, length(rest) - 2)
        }
      }
      print rest
      exit
    }
  ' "$skill_path"
}

# Return success when a discovered skill path resolves to a plugin-owned bundle
# under Plugins/<plugin>/skills/<skill>. These should not appear as standalone
# is_plugin_owned_skill_path determines whether a SKILL.md path belongs to a plugin's skills directory under the repository's Plugins/<plugin>/skills tree and returns 0 if it does, 1 otherwise.
is_plugin_owned_skill_path() {
  local skill_path="$1"
  local skill_dir_rel=""
  local skill_dir_abs=""
  local skill_dir_real=""

  skill_dir_rel="$(dirname "$skill_path")"
  skill_dir_abs="$repo_root/${skill_dir_rel#./}"
  if [ ! -d "$skill_dir_abs" ]; then
    return 1
  fi
  skill_dir_real="$(cd "$skill_dir_abs" 2>/dev/null && pwd -P || true)"
  case "$skill_dir_real" in
    "$repo_root_real"/Plugins/*/skills/*) return 0 ;;
    *) return 1 ;;
  esac
}

generated_command_handle_names_cmd() {
  local command_surface_file="$repo_root/.skillsets/command-surface.json"
  if [ ! -f "$command_surface_file" ]; then
    return 0
  fi

  jq -r '
    .handles[]?
    | select(type == "object")
    | select((.command_handle_path // "") | startswith(".agents/skills/"))
    | .handle // empty
  ' "$command_surface_file" 2>/dev/null || true
}

is_generated_command_handle_name() {
  local skill_name="$1"
  if [ -z "${generated_command_handle_names_file:-}" ] || [ ! -f "$generated_command_handle_names_file" ]; then
    return 1
  fi

  jq -e --arg skill_name "$skill_name" 'index($skill_name) != null' \
    "$generated_command_handle_names_file" >/dev/null
}

is_generated_command_handle_dir() {
  local skill_name="$1"
  local generated_skill_md="$skills_dir/$skill_name/SKILL.md"

  if [ ! -f "$generated_skill_md" ] || [ -L "$generated_skill_md" ]; then
    return 1
  fi

  python3 - "$generated_skill_md" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
if "Internal activation entrypoint for a child skill under" not in text:
    raise SystemExit(1)
if "Source: " not in text:
    raise SystemExit(1)
PY
}

if [ "$skills_dir_writable" = "1" ]; then
  generated_command_handle_names_file="$(mktemp)"
  generated_command_handle_names_cmd | jq -Rsc 'split("\n") | map(select(length > 0)) | unique' \
    > "$generated_command_handle_names_file"
  while IFS= read -r skill_path; do
    # Skip the root index.
    if [ "$skill_path" = "./SKILL.md" ]; then
      continue
    fi
    skill_dir="$(dirname "$skill_path")"
    skill_name="$(basename "$skill_dir")"
    if is_hidden_flat_skill_name "$skill_name"; then
      echo "Skipping hidden flat skill: $skill_name"
      continue
    fi
    skill_dir_abs="$repo_root/$skill_dir"
    discovered_dir="$(cd "$skill_dir_abs" 2>/dev/null && pwd || true)"
    if is_plugin_owned_skill_path "$skill_path"; then
      if is_generated_command_handle_name "$skill_name"; then
        if is_generated_command_handle_dir "$skill_name"; then
          echo "Preserving plugin-owned generated command handle: $skill_name"
          continue
        fi
        if [ -e "$skills_dir/$skill_name" ] || [ -L "$skills_dir/$skill_name" ]; then
          if rm -rf -- "${skills_dir:?}/${skill_name:?}"; then
            echo "Removed stale plugin-owned runtime entry before regenerating command handle: $skill_name"
          else
            echo "[WARN] Could not remove stale plugin-owned runtime entry $skill_name at $skills_dir (continuing anyway)."
            continue
          fi
        fi
      fi
      if [ -e "$skills_dir/$skill_name" ] || [ -L "$skills_dir/$skill_name" ]; then
        if rm -rf -- "${skills_dir:?}/${skill_name:?}"; then
          echo "Removed stale plugin-owned flat skill: $skill_name"
        else
          echo "[WARN] Could not remove stale plugin-owned skill $skill_name at $skills_dir (continuing anyway)."
          continue
        fi
      fi
      if ! is_plugin_visible_router_skill_name "$skill_name"; then
        echo "Skipping plugin-owned skill from flat projection: $skill_name"
        continue
      fi
      if is_plugin_hidden_lane_skill_name "$skill_name"; then
        echo "Skipping hidden plugin lane skill: $skill_name"
        continue
      fi
      if ! register_plugin_router_skill_source "$skill_name" "$discovered_dir"; then
        router_collision_count=$((router_collision_count + 1))
        continue
      fi
      echo "Including plugin-owned skill in flat runtime list: $skill_name"
    elif ! is_default_visible_flat_skill_name "$skill_name"; then
      echo "Skipping non-default flat skill: $skill_name"
      continue
    fi
    # Relative path from $skills_dir (.agents/skills/) back to the skill source.
    # Strip the leading './' from skill_dir to get e.g. 'auth/create-auth',
    # then prepend '../..' to escape .agents/skills/ back to repo root.
    skill_dir_rel="../../${skill_dir#./}"
    if [ -e "$skills_dir/$skill_name" ]; then
      existing_dir="$(cd "$skills_dir/$skill_name" 2>/dev/null && pwd || true)"
      discovered_dir="$(cd "$skill_dir_abs" 2>/dev/null && pwd || true)"
      # If the discovered skill already lives directly in the flat skills view
      # (for example ./skills/sentry), skip without duplicate noise.
      if [ -n "$existing_dir" ] && [ "$existing_dir" = "$discovered_dir" ]; then
        continue
      fi
      # Canonical category-folder skills win precedence over stale/generated flat
      # copies so the loader view stays aligned with the source-of-truth skill.
      if [ -d "$skills_dir/$skill_name" ] && [ "${skill_dir#./.agents/skills/}" = "$skill_dir" ]; then
        echo "Replacing conflicting flat skill dir: $skill_name -> $skill_dir_rel"
        if ! rm -rf -- "${skills_dir:?}/${skill_name:?}"; then
          echo "[WARN] Could not replace existing $skill_name in $skills_dir; skipping $skill_dir_rel."
          continue
        fi
      else
        echo "Duplicate skill name: $skill_name (skip $skill_dir_rel)"
        continue
      fi
    fi
    ln -s "$skill_dir_rel" "$skills_dir/$skill_name"
  done < <(all_skill_files_cmd)
  rm -f -- "$generated_command_handle_names_file"

  if [ "$router_collision_count" -gt 0 ]; then
    echo "[ERROR] Aborting sync due to plugin-visible router skill collisions." >&2
    exit 1
  fi

  # Re-expose preserved system skills through the hidden `.system` path without
  # bringing them back into the flat runtime skill list.
  if [ -e "$skills_dir/.system" ] && [ ! -L "$skills_dir/.system" ]; then
    echo "[WARN] $skills_dir/.system exists as a non-symlink; leaving it in place."
  elif [ ! -e "$skills_dir/.system" ]; then
    ln -s "../../skills-system" "$skills_dir/.system"
  fi

  # Keep approved bridge skills available only through the hidden `.system`
  # lane. First-level aliases make lifecycle helper skills appear as duplicate
  # user-facing skills in Codex, so remove stale aliases instead of creating them.
  for bridge_skill in "${system_bridge_skills[@]}"; do
    bridge_source=".system/$bridge_skill"
    if [ ! -e "$skills_dir/$bridge_source" ]; then
      echo "[WARN] Missing system bridge source: $skills_dir/$bridge_source"
      if [ -e "$skills_dir/$bridge_skill" ] || [ -L "$skills_dir/$bridge_skill" ]; then
        rm -rf -- "${skills_dir:?}/${bridge_skill:?}"
        echo "Removed stale first-level bridge skill alias: $bridge_skill"
      fi
      continue
    fi

    if [ -e "$skills_dir/$bridge_skill" ] || [ -L "$skills_dir/$bridge_skill" ]; then
      rm -rf -- "${skills_dir:?}/${bridge_skill:?}"
      echo "Removed first-level bridge skill alias: $bridge_skill"
    fi

    echo "Bridge skill kept under .system: $bridge_skill -> $bridge_source"
  done
  flat_projection_rebuilt=1
else
  echo "[INFO] Skipped flat runtime skill projection because $skills_dir is not writable."
fi

# generate_skill_index regenerates the repository SKILL.md index from discovered SKILL.md frontmatter, grouping skills by category and using `metadata.short-description` (falling back to `description`) for each entry.
# index_file is the path to write the generated index (overwrites or creates the file).
generate_skill_index() {
  local index_file="$1"
  local temp_dir=""
  temp_dir="$(mktemp -d)"
  cleanup_paths+=("$temp_dir")

  # Extract a YAML frontmatter `description:` value, including common multiline forms.
  #
  # Supported patterns seen in this repo:
  # - Single-line: description: Foo bar.
  # - Multiline indented scalar:
  #     description: Foo bar. Use
  #       when ...
  # - Quoted multiline scalar (single or double quotes)
  # - Block scalars (| or >), best-effort
  extract_description() {
    local skill_path="$1"
    awk '
      function ltrim(s) { sub(/^[ \t]+/, "", s); return s }
      function rtrim(s) { sub(/[ \t]+$/, "", s); return s }
      function trim(s) { return rtrim(ltrim(s)) }
      BEGIN {
        in_fm = 0
        in_desc = 0
        quote = ""
        block = ""
        desc = ""
      }
      /^---[ \t]*$/ {
        if (in_fm == 0) { in_fm = 1; next }
        # End of frontmatter
        if (in_desc) { print trim(desc) }
        exit
      }
      in_fm == 0 { next }

      # While collecting the description, stop at the next top-level key.
      in_desc == 1 {
        if ($0 ~ /^[A-Za-z0-9_-]+:[ \t]*/) {
          print trim(desc)
          exit
        }

        line = $0
        line = ltrim(line)

        if (quote != "") {
          # Quoted scalar: keep consuming until a closing quote at line end.
          if (line ~ quote "[ \t]*$") {
            sub(quote "[ \t]*$", "", line)
            desc = (desc == "" ? line : desc " " line)
            print trim(desc)
            exit
          }
          desc = (desc == "" ? line : desc " " line)
          next
        }

        if (block != "") {
          # Block scalar: keep newlines (best-effort; good enough for index output).
          desc = (desc == "" ? line : desc "\n" line)
          next
        }

        # Plain multiline scalar: only treat indented lines as continuation.
        if ($0 ~ /^[ \t]+/) {
          desc = (desc == "" ? line : desc " " line)
          next
        }

        print trim(desc)
        exit
      }

      /^description:[ \t]*/ {
        rest = $0
        sub(/^description:[ \t]*/, "", rest)
        rest = trim(rest)

        if (rest == "|" || rest == ">") {
          block = rest
          in_desc = 1
          next
        }

        if (rest ~ /^["\047]/) {
          quote = substr(rest, 1, 1)
          rest = substr(rest, 2)
          if (rest ~ quote "[ \t]*$") {
            sub(quote "[ \t]*$", "", rest)
            print trim(rest)
            exit
          }
          desc = rest
          in_desc = 1
          next
        }

        desc = rest
        in_desc = 1
        next
      }
    ' "$skill_path"
  }

  # Extract `metadata.short-description:` (preferred for the generated index).
  # Supports:
  # - `metadata:\n  short-description: ...`
  # - single-line and common multiline continuation styles
  extract_short_description() {
    local skill_path="$1"
    awk '
      function ltrim(s) { sub(/^[ \t]+/, "", s); return s }
      function rtrim(s) { sub(/[ \t]+$/, "", s); return s }
      function trim(s) { return rtrim(ltrim(s)) }
      BEGIN {
        in_fm = 0
        in_meta = 0
        in_sd = 0
        quote = ""
        block = ""
        sd = ""
      }
      /^---[ \t]*$/ {
        if (in_fm == 0) { in_fm = 1; next }
        if (in_sd) { print trim(sd) }
        exit
      }
      in_fm == 0 { next }

      # Enter/leave metadata block (top-level key)
      /^[A-Za-z0-9_-]+:[ \t]*/ {
        key = $0
        sub(/:.*/, "", key)
        if (key == "metadata") { in_meta = 1; next }
        if (in_meta == 1) { in_meta = 0 }
      }

      in_sd == 1 {
        # Continuations are usually indented (>=4 spaces). Stop when we hit
        # a new key at indent 0 or 2 (common frontmatter patterns).
        match($0, /^[ ]*/)
        ind = RLENGTH
        if (ind < 4 && $0 ~ /^[ ]*[A-Za-z0-9_-]+:[ \t]*/) {
          print trim(sd)
          exit
        }

        line = substr($0, ind + 1)
        line = trim(line)

        if (quote != "") {
          if (substr(line, length(line), 1) == quote) {
            line = substr(line, 1, length(line) - 1)
            sd = (sd == "" ? line : sd " " line)
            print trim(sd)
            exit
          }
          sd = (sd == "" ? line : sd " " line)
          next
        }

        if (block != "") {
          sd = (sd == "" ? line : sd "\n" line)
          next
        }

        # Plain multiline scalar: keep indented lines.
        sd = (sd == "" ? line : sd " " line)
        next
      }

      in_meta == 1 && /^[ \t]+short-description:[ \t]*/ {
        rest = $0
        sub(/^[ \t]+short-description:[ \t]*/, "", rest)
        rest = trim(rest)

        if (rest == "|" || rest == ">") {
          block = rest
          in_sd = 1
          next
        }

        if (rest ~ /^["\047]/) {
          quote = substr(rest, 1, 1)
          rest = substr(rest, 2)
          if (substr(rest, length(rest), 1) == quote) {
            rest = substr(rest, 1, length(rest) - 1)
            print trim(rest)
            exit
          }
          sd = rest
          in_sd = 1
          next
        }

        sd = rest
        in_sd = 1
        next
      }
    ' "$skill_path"
  }

  # Start with header
  cat > "$index_file" << 'HEADER'
# Agent Skills Index

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/.agents/skills`.

HEADER

  # Collect skills into temp files by category
  while IFS= read -r skill_path; do
    # Skip the root index
    if [ "$skill_path" = "./SKILL.md" ]; then
      continue
    fi
    skill_dir="$(dirname "$skill_path")"
    skill_name="$(basename "$skill_dir")"
    if is_hidden_flat_skill_name "$skill_name"; then
      continue
    fi
    if is_plugin_owned_skill_path "$skill_path"; then
      if is_plugin_hidden_lane_skill_name "$skill_name"; then
        continue
      fi
    fi
    category="$(dirname "$skill_dir" | sed 's|^\./||; s|^\.||')"
    safe_category="$(echo "$category" | tr '/' '_')"

    # Extract description from YAML frontmatter
    description=""
    if [ -f "$skill_path" ]; then
      short_description="$(extract_short_description "$skill_path" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/[[:space:]]+$//')"
      if [ -n "$short_description" ]; then
        description="$short_description"
      else
        description="$(extract_description "$skill_path" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/[[:space:]]+$//')"
      fi
    fi

    # Store description (or fallback text)
    if [ -z "$description" ]; then
      description="Skill description pending."
    fi

    # Append to category file
    echo "- \`$skill_name\` — $description" >> "$temp_dir/$safe_category"
  done < <(all_skill_files_cmd)

  # Output categories and skills in deterministic order
  while IFS= read -r cat_file; do
    category="${cat_file//_/\/}"
    category="${category//\// — }"
    category="${category//-/ }"
    category="${category//_/ }"
    category="${category% }"
    # Capitalize each word
    capitalized_category=""
    for word in $category; do
      first="$(echo "$word" | cut -c1 | tr '[:lower:]' '[:upper:]')"
      rest="$(echo "$word" | cut -c2-)"
      capitalized_category="$capitalized_category$first$rest "
    done

    capitalized_category="${capitalized_category% }"
    {
      echo "## $capitalized_category"
      echo ""
      sort "$temp_dir/$cat_file"
      echo ""
    } >> "$index_file"
  done < <(cd "$temp_dir" && find . -mindepth 1 -maxdepth 1 -type f -print | sed 's|^\./||' | sort)
}

# generate_skill_type_index generates a skills-by-type markdown index from `metadata.skill-type` tags, grouping discovered skills into canonical semantic types, emitting counts, per-type lists and validation notes.
# generate_skill_type_index generates a skills-by-type index at the specified output path by scanning SKILL.md files and grouping entries by the canonical `metadata.skill-type` values, emitting counts, per-type lists, and validation notes for unrecognized tags.
generate_skill_type_index() {
  local index_file="$1"
  local temp_dir=""
  local type_file=""
  temp_dir="$(mktemp -d)"
  cleanup_paths+=("$temp_dir")

  mkdir -p "$(dirname "$index_file")"

  local ordered_types=(
    "library_api_reference"
    "product_verification"
    "data_fetch_analysis"
    "team_automation"
    "scaffolding_templates"
    "code_quality_review"
    "ci_cd_deployment"
    "runbook"
    "infrastructure_ops"
  )

  # Bucket tagged skills by semantic type.
  while IFS= read -r skill_path; do
    if [ "$skill_path" = "./SKILL.md" ]; then
      continue
    fi
    skill_dir="$(dirname "$skill_path")"
    skill_name="$(basename "$skill_dir")"
    if is_hidden_flat_skill_name "$skill_name"; then
      continue
    fi
    if is_plugin_owned_skill_path "$skill_path"; then
      if is_plugin_hidden_lane_skill_name "$skill_name"; then
        continue
      fi
    fi
    skill_type_raw="$(extract_skill_type "$skill_path" | tr '\n' ' ' | sed -E 's/[[:space:]]+/ /g; s/^[[:space:]]+//; s/[[:space:]]+$//')"
    if [ -z "$skill_type_raw" ]; then
      continue
    fi

    skill_type="$(echo "$skill_type_raw" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]-]+/_/g')"
    category="$(dirname "$skill_dir" | sed 's|^\./||; s|^\.||')"

    case "$skill_type" in
      library_api_reference|product_verification|data_fetch_analysis|team_automation|scaffolding_templates|code_quality_review|ci_cd_deployment|runbook|infrastructure_ops)
        echo "- \`$skill_name\` — \`$category\`" >> "$temp_dir/$skill_type"
        ;;
      *)
        echo "[WARN] Unrecognized metadata.skill-type in $skill_path: $skill_type_raw" >&2
        echo "- \`$skill_name\` — \`$category\` (\`$skill_type_raw\`)" >> "$temp_dir/__invalid__"
        ;;
    esac
  done < <(all_skill_files_cmd)

  cat > "$index_file" << 'HEADER'
# Skill Type Index

Generated from `metadata.skill-type` tags in skill frontmatter. This index complements the directory-based catalog in `SKILL.md`.
Entries are grouped by declared semantic type; each path names the owning skill package root, including plugin-owned surfaces.

## Table of Contents
- [Summary](#summary)
- [Semantic Types](#semantic-types)
- [Validation Notes](#validation-notes)

HEADER

  {
    echo "## Summary"
    echo ""
  } >> "$index_file"

  tagged_count=0
  for type_name in "${ordered_types[@]}"; do
    type_file="$temp_dir/$type_name"
    count=0
    if [ -f "$type_file" ]; then
      count="$(wc -l < "$type_file" | tr -d '[:space:]')"
    fi
    tagged_count=$((tagged_count + count))
    echo "- \`$type_name\`: $count" >> "$index_file"
  done

  invalid_count=0
  if [ -f "$temp_dir/__invalid__" ]; then
    invalid_count="$(wc -l < "$temp_dir/__invalid__" | tr -d '[:space:]')"
  fi
  {
    echo "- \`invalid\`: $invalid_count"
    echo "- \`total_tagged\`: $tagged_count"
    echo ""
  } >> "$index_file"

  {
    echo "## Semantic Types"
    echo ""
  } >> "$index_file"

  for type_name in "${ordered_types[@]}"; do
    header="$(echo "$type_name" | tr '_' ' ')"
    title=""
    for word in $header; do
      first="$(echo "$word" | cut -c1 | tr '[:lower:]' '[:upper:]')"
      rest="$(echo "$word" | cut -c2-)"
      title="$title$first$rest "
    done
    title="${title% }"

    {
      echo "### $title"
      echo ""
      if [ -f "$temp_dir/$type_name" ]; then
        sort "$temp_dir/$type_name"
      else
        echo "- _No tagged skills yet._"
      fi
      echo ""
    } >> "$index_file"
  done

  {
    echo "## Validation Notes"
    echo ""
    if [ "$invalid_count" -gt 0 ]; then
      echo "- Unrecognized tags were found. Check script warnings and normalize to the canonical values."
      echo ""
      sort "$temp_dir/__invalid__"
    else
      echo "- No invalid semantic type tags detected."
    fi
    echo ""
  } >> "$index_file"
}

python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py" --source catalog --write-index "$repo_root/SKILL.md"
catalog_count="$(
  python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py" --source catalog --count
)"
python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/update_readme_catalog_text.py" \
  "$repo_root/README.md" \
  "$catalog_count"
generate_skill_type_index "$repo_root/docs/skills-by-type.md"

# remove_legacy_symlink removes the symlink at the given path if it exists and echoes a confirmation.
remove_legacy_symlink() {
  local target_dir="$1"
  if [ -L "$target_dir" ]; then
    rm -f "$target_dir"
    echo "[OK] Removed legacy symlink: $target_dir"
  fi
}

# Remove old/legacy symlinks from unsupported locations.
# Keep this user-only so workspace/project-local sync stays side-effect free outside.
# remove_legacy_home_skill_symlinks removes legacy per-user skill symlinks from common home locations if they exist.
remove_legacy_home_skill_symlinks() {
  remove_legacy_symlink "$HOME/.copilot/skills"
  remove_legacy_symlink "$HOME/.Infrastructure/config/agents/skills"
  remove_legacy_symlink "$HOME/.cursor/skills"
}

# sync_user_skills synchronizes a source skills directory into a user's target directory by creating or updating a symlink (default) or by copying contents when mode="copy"; when `force` is `1` an existing non-symlink target will be replaced.
sync_user_skills() {
  local source_dir="$1"
  local target_dir="$2"
  local force="${3:-0}"
  local mode="${4:-symlink}"

  # sync_dir_copy copies the contents of source_dir into target_dir, preserving file metadata and mirroring the source (removing extraneous files); it prefers `rsync -a --delete --force` when available and falls back to removing first-level entries and using portable `cp -R` otherwise.
  sync_dir_copy() {
    local source_dir="$1"
    local target_dir="$2"

    if [ -L "$target_dir" ]; then
      rm -f -- "$target_dir"
    elif [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
      rm -f -- "$target_dir"
    fi
    mkdir -p "$target_dir"

    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete --force "$source_dir/" "$target_dir/"
      return 0
    fi

    # Fallback for environments without rsync.
    find "$target_dir" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    cp -R "$source_dir/." "$target_dir/"
  }

  if [ "$mode" = "copy" ]; then
    mkdir -p "$(dirname "$target_dir")"
    if [ -L "$target_dir" ]; then
      rm -f -- "$target_dir" || echo "[WARN] Could not replace symlink target at $target_dir (continuing with copy)."
    elif [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
      rm -f -- "$target_dir" || echo "[WARN] Could not replace non-directory target at $target_dir (continuing with copy)."
    fi
    sync_dir_copy "$source_dir" "$target_dir"
    echo "[OK] Synced directory: $target_dir"
    return 0
  fi

  mkdir -p "$(dirname "$target_dir")"
  if [ -L "$target_dir" ]; then
    local current_target
    current_target="$(readlink "$target_dir" 2>/dev/null || true)"
    if [ "$current_target" = "$source_dir" ]; then
      echo "[OK] Symlink already current: $target_dir -> $source_dir"
      return 0
    fi
    # Update existing symlink
    if ln -sfn "$source_dir" "$target_dir" 2>/dev/null; then
      echo "[OK] Updated symlink: $target_dir -> $source_dir"
    else
      echo "[WARN] Unable to update symlink $target_dir -> $source_dir (continuing)."
    fi
  elif [ -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
    if [ "$force" = "1" ]; then
      if rm -rf "$target_dir"; then
        if ln -s "$source_dir" "$target_dir" 2>/dev/null; then
          echo "[OK] Replaced existing path with symlink: $target_dir -> $source_dir"
        else
          echo "[WARN] Unable to create symlink $target_dir -> $source_dir (continuing)."
        fi
      else
        echo "[WARN] Could not remove existing path at $target_dir; skipping symlink update."
      fi
    else
      # Exists but is not a symlink - warn and skip
      echo "[WARN] $target_dir exists but is not a symlink (skipping)"
      echo "       Remove it manually to enable automatic sync: rm -rf $target_dir"
    fi
  else
    # Create new symlink
    if ln -s "$source_dir" "$target_dir" 2>/dev/null; then
      echo "[OK] Created symlink: $target_dir -> $source_dir"
    else
      echo "[ERROR] Unable to create symlink $target_dir -> $source_dir."
      return 1
    fi
  fi
}

# ensure_real_home_plugin_root replaces a repo-backed plugin-root symlink with a
# real directory so home/plugin surfaces stop aliasing the repository vendored
# ensure_real_home_plugin_root ensures the given target_dir exists as a real directory, replacing a symlink that points into canonical_plugins_dir with a real directory and creating the directory (and its parent) if it does not exist; prints status messages.
ensure_real_home_plugin_root() {
  local target_dir="$1"
  local canonical_plugins_dir="$2"
  local label="${3:-home plugin root}"
  local target_link=""
  local link_target_real=""
  local canonical_plugins_real=""
  local backup_path=""

  mkdir -p "$(dirname "$target_dir")"
  canonical_plugins_real="$(cd "$canonical_plugins_dir" 2>/dev/null && pwd -P || true)"
  if [ -z "$canonical_plugins_real" ]; then
    echo "[WARN] Could not resolve canonical plugins dir for $label: $canonical_plugins_dir"
    return 0
  fi

  if [ -L "$target_dir" ]; then
    case "$label" in
      profile*|home\ plugin\ root)
        if ! rm -f -- "$target_dir" 2>/dev/null; then
          echo "[WARN] Could not replace symlinked $label at $target_dir; skipping protected plugin root."
          return 1
        fi
        if ! mkdir -p "$target_dir" 2>/dev/null; then
          echo "[WARN] Could not create $label directory at $target_dir; skipping protected plugin root."
          return 1
        fi
        echo "[OK] Replaced symlinked $label with directory: $target_dir"
        return 0
        ;;
    esac
    target_link="$(readlink "$target_dir" || true)"
    if [ -n "$target_link" ]; then
      link_target_real="$(cd "$(dirname "$target_dir")" 2>/dev/null && cd "$target_link" 2>/dev/null && pwd -P || true)"
    fi
    if [ -n "$link_target_real" ] && python3 "$repo_root/Infrastructure/scripts/lifecycle-and-sync/path_identity.py" is-same-or-child "$canonical_plugins_real" "$link_target_real"
    then
      if ! rm -f -- "$target_dir" 2>/dev/null; then
        echo "[WARN] Could not replace repo-backed symlinked $label at $target_dir; skipping protected plugin root."
        return 1
      fi
      if ! mkdir -p "$target_dir" 2>/dev/null; then
        echo "[WARN] Could not create $label directory at $target_dir; skipping protected plugin root."
        return 1
      fi
      echo "[OK] Replaced repo-backed symlinked $label with directory: $target_dir"
      return 0
    fi
  fi

  if [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
    backup_path="${target_dir}.bak.$(date +%Y%m%d%H%M%S)"
    if mv -- "$target_dir" "$backup_path"; then
      echo "[WARN] Moved non-directory $label path aside: $target_dir -> $backup_path"
    else
      echo "[WARN] Could not move non-directory $label path aside; removing: $target_dir"
      if ! rm -f -- "$target_dir" 2>/dev/null; then
        echo "[WARN] Could not remove non-directory $label path at $target_dir; skipping protected plugin root."
        return 1
      fi
    fi
  fi

  if [ ! -e "$target_dir" ]; then
    if ! mkdir -p "$target_dir" 2>/dev/null; then
      echo "[WARN] Could not create $label directory at $target_dir; skipping protected plugin root."
      return 1
    fi
    echo "[OK] Created $label directory: $target_dir"
  fi
  return 0
}

# sync_skill_path_file writes a small file at the specified target containing the canonicalised source directory path with a trailing slash to support loaders that expect a directory-path file.
sync_skill_path_file() {
  local source_dir="$1"
  local target_file="$2"
  local rendered_dir="${source_dir%/}/"
  mkdir -p "$(dirname "$target_file")"
  printf '%s\n' "$rendered_dir" > "$target_file"
  echo "[OK] Wrote skill path file: $target_file -> $rendered_dir"
}

# is_safe_path_component validates marketplace/plugin path components before they
# is_safe_path_component returns success if the given value is a single safe path component containing only ASCII letters, digits, dot, underscore or hyphen.
is_safe_path_component() {
  local value="$1"
  [[ "$value" =~ ^[A-Za-z0-9._-]+$ ]]
}

# resolve_marketplace_source_dir returns a canonical source directory for a
# resolve_marketplace_source_dir resolves a relative './Plugins/...' marketplace `source.path` to its canonical absolute directory under the repository `plugins` tree and prints that path.
# It rejects paths that are not relative, contain `..`, do not start with `./Plugins/`, cannot be resolved to an existing directory, or resolve outside `$repo_root_real/Plugins/`, returning non‑zero in those cases.
resolve_marketplace_source_dir() {
  local source_path="$1"
  local candidate=""
  local resolved=""

  case "$source_path" in
    ./*) ;;
    *) return 1 ;;
  esac
  if [[ "$source_path" == *".."* ]]; then
    return 1
  fi
  case "$source_path" in
    ./Plugins/*) ;;
    *) return 1 ;;
  esac

  candidate="$repo_root/${source_path#./}"
  resolved="$(cd "$candidate" 2>/dev/null && pwd -P || true)"
  if [ -z "$resolved" ]; then
    return 1
  fi

  case "$resolved" in
    "$repo_root_real"/Plugins/*)
      printf '%s\n' "$resolved"
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

# normalize_plugin_copy materializes top-level skill alias symlink directories
# and symlinked skill files inside copied plugin skills/ trees, then removes
# fixtures and duplicate category lanes.
# normalize_plugin_copy materializes symlinked skills and nested symlinks inside a plugin copy, removes fixtures and duplicate category lanes, and prunes command-handle duplicate entries so the plugin copy becomes a self-contained, real directory tree.
#
# It replaces first-level skill symlinks under <plugin_dir>/skills with copied directories when the symlink target resolves inside the plugin copy, recursively materializes nested directory and file symlinks within those copies, materializes stray symlinks elsewhere in the plugin before pruning fixtures, removes configured duplicate category lanes, and removes duplicate command-handle skill entries according to the repository command-surface index.
#
# plugin_dir - path to the plugin copy root to normalize.
# label - optional short context string used in log messages (default: "runtime").
normalize_plugin_copy() {
  local plugin_dir="$1"
  local label="${2:-runtime}"
  local skills_dir="$plugin_dir/skills"
  local plugin_dir_real=""
  local skill_entry=""
  local resolved=""
  local skill_link=""
  local tmp_file=""
  local duplicate_category=""
  local handle_name=""
  local skill_entry=""
  local nested_link=""
  local nested_link_abs=""
  local nested_resolved=""
  local command_surface_file="$repo_root/.skillsets/command-surface.json"

  plugin_dir_real="$(cd "$plugin_dir" 2>/dev/null && pwd -P || true)"
  if [ -z "$plugin_dir_real" ]; then
    echo "[WARN] Could not resolve ${label} plugin copy root: $plugin_dir"
    return 0
  fi

  if [ -d "$skills_dir" ]; then
    while IFS= read -r skill_entry; do
      [ -n "$skill_entry" ] || continue
      case "$(basename "$skill_entry")" in
        _*|agents|assets|examples|fixtures|infrastructure_ops|references|rules|scripts|scaffolding_templates|shared|team_automation|templates|code_quality_review|data_fetch_analysis)
          continue
          ;;
      esac
      [ -L "$skill_entry" ] || continue
      resolved="$(cd "$(dirname "$skill_entry")" 2>/dev/null && cd "$(readlink "$skill_entry")" 2>/dev/null && pwd -P || true)"
      [ -n "$resolved" ] || continue
      [ -d "$resolved" ] || continue
      case "$resolved" in
        "$plugin_dir_real"|"$plugin_dir_real"/*) ;;
        *)
          echo "[WARN] Refusing to materialize ${label} skill alias outside plugin copy: skills_dir=$skills_dir skill_entry=$skill_entry resolved=$resolved"
          continue
          ;;
      esac
      rm -f -- "$skill_entry"
      cp -R "$resolved" "$skill_entry"
      echo "[OK] Materialized ${label} skill alias: $skill_entry"

      # Recursively materialize any nested symlinks (both files and directories) within the copied tree
      # Repeat until no more directory symlinks are materialized (to catch second-order directory symlinks)
      local dir_symlinks_materialized=1
      while [ "$dir_symlinks_materialized" -gt 0 ]; do
        dir_symlinks_materialized=0
        while IFS= read -r -d '' nested_link; do
          [ -n "$nested_link" ] || continue
          [ -L "$nested_link" ] || continue
          local nested_resolved
          nested_resolved="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$nested_link" 2>/dev/null || true)"
          if [ -z "$nested_resolved" ]; then
            echo "[WARN] Could not resolve ${label} nested symlink: $nested_link"
            continue
          fi
          case "$nested_resolved" in
            "$plugin_dir_real"|"$plugin_dir_real"/*) ;;
            *)
              echo "[WARN] Refusing to materialize ${label} nested symlink outside plugin copy: nested_link=$nested_link nested_resolved=$nested_resolved"
              continue
              ;;
          esac
          if [ -d "$nested_link" ]; then
            # Directory symlink - copy recursively then remove link
            local tmp_dir
            tmp_dir="$(mktemp -d)"
            if cp -R "$nested_link/." "$tmp_dir/"; then
              rm -f -- "$nested_link"
              mv "$tmp_dir" "$nested_link"
              echo "[OK] Materialized ${label} nested directory symlink: $nested_link"
              dir_symlinks_materialized=$((dir_symlinks_materialized + 1))
            else
              rm -rf -- "$tmp_dir"
              echo "[WARN] Failed to materialize ${label} nested directory symlink: $nested_link"
            fi
          elif [ -f "$nested_link" ]; then
            # File symlink - copy to temp then replace
            local tmp_file
            tmp_file="$(mktemp)"
            if cp -- "$nested_link" "$tmp_file"; then
              rm -f -- "$nested_link"
              mv "$tmp_file" "$nested_link"
              echo "[OK] Materialized ${label} nested file symlink: $nested_link"
            else
              rm -f -- "$tmp_file"
              echo "[WARN] Failed to materialize ${label} nested file symlink: $nested_link"
            fi
          fi
        done < <(find "$skill_entry" -type l -print0)
      done
    done < <(find "$skills_dir" -mindepth 1 -maxdepth 1 -type l -print)

    while IFS= read -r -d '' skill_link; do
      [ -n "$skill_link" ] || continue
      [ -L "$skill_link" ] || continue
      [ -f "$skill_link" ] || continue
      if ! [ -r "$skill_link" ]; then
        echo "[WARN] Could not read ${label} skill symlink target: $skill_link"
        continue
      fi
      resolved="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$skill_link" 2>/dev/null || true)"
      if [ -z "$resolved" ]; then
        echo "[WARN] Could not resolve ${label} skill symlink target: skills_dir=$skills_dir skill_link=$skill_link"
        continue
      fi
      case "$resolved" in
        "$plugin_dir_real"|"$plugin_dir_real"/*) ;;
        *)
          echo "[WARN] Refusing to materialize ${label} skill file outside plugin copy: skills_dir=$skills_dir skill_link=$skill_link resolved=$resolved"
          continue
          ;;
      esac
      tmp_file="$(mktemp)"
      if cp -- "$skill_link" "$tmp_file"; then
        rm -f -- "$skill_link"
        mv "$tmp_file" "$skill_link"
        echo "[OK] Materialized ${label} skill file: $skill_link"
      else
        rm -f -- "$tmp_file"
        echo "[WARN] Failed to materialize ${label} skill file: $skill_link"
      fi
    done < <(find "$skills_dir" -type l -print0)
  fi

  local whole_plugin_dir_symlinks_materialized=1
  while [ "$whole_plugin_dir_symlinks_materialized" -gt 0 ]; do
    whole_plugin_dir_symlinks_materialized=0
    while IFS= read -r -d '' nested_link; do
      [ -n "$nested_link" ] || continue
      [ -L "$nested_link" ] || continue
      nested_resolved="$(python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' "$nested_link" 2>/dev/null || true)"
      if [ -z "$nested_resolved" ] || [ ! -e "$nested_resolved" ]; then
        echo "[WARN] Could not resolve ${label} symlink before fixture pruning: $nested_link"
        continue
      fi
      nested_link_abs="$(
        nested_link_dir="$(dirname "$nested_link")"
        nested_link_base="$(basename "$nested_link")"
        if cd "$nested_link_dir" 2>/dev/null; then
          printf '%s/%s\n' "$(pwd -P)" "$nested_link_base"
        fi
      )"
      case "$nested_link_abs" in
        "$nested_resolved"|"$nested_resolved"/*)
          echo "[WARN] Refusing to materialize ${label} symlink whose destination is inside its source tree: nested_link=$nested_link nested_resolved=$nested_resolved"
          continue
          ;;
      esac
      case "$nested_resolved" in
        "$plugin_dir_real"|"$plugin_dir_real"/*) ;;
        *)
          echo "[WARN] Refusing to materialize ${label} symlink outside plugin copy: nested_link=$nested_link nested_resolved=$nested_resolved"
          continue
          ;;
      esac
      if [ -d "$nested_resolved" ]; then
        local tmp_dir
        tmp_dir="$(mktemp -d)"
        if cp -R "$nested_resolved/." "$tmp_dir/"; then
          rm -f -- "$nested_link"
          mv "$tmp_dir" "$nested_link"
          echo "[OK] Materialized ${label} directory symlink before fixture pruning: $nested_link"
          whole_plugin_dir_symlinks_materialized=$((whole_plugin_dir_symlinks_materialized + 1))
        else
          rm -rf -- "$tmp_dir"
          echo "[WARN] Failed to materialize ${label} directory symlink before fixture pruning: $nested_link"
        fi
      elif [ -f "$nested_resolved" ]; then
        tmp_file="$(mktemp)"
        if cp -- "$nested_resolved" "$tmp_file"; then
          rm -f -- "$nested_link"
          mv "$tmp_file" "$nested_link"
          echo "[OK] Materialized ${label} file symlink before fixture pruning: $nested_link"
        else
          rm -f -- "$tmp_file"
          echo "[WARN] Failed to materialize ${label} file symlink before fixture pruning: $nested_link"
        fi
      fi
    done < <(find "$plugin_dir" -type l -print0)
  done

  if [ -d "${plugin_dir:?}/fixtures" ]; then
    rm -rf -- "${plugin_dir:?}/fixtures"
    echo "[OK] Removed ${label} plugin fixtures: ${plugin_dir:?}/fixtures"
  fi

  for duplicate_category in \
    team_automation \
    code_quality_review \
    scaffolding_templates \
    infrastructure_ops \
    data_fetch_analysis; do
    if [ -d "${skills_dir:?}/${duplicate_category:?}" ]; then
      rm -rf -- "${skills_dir:?}/${duplicate_category:?}"
      echo "[OK] Removed ${label} duplicate category lane: ${skills_dir:?}/${duplicate_category:?}"
    fi
  done

  # Local plugin caches are still scanned by some Codex picker paths. When a
  # plugin skill already has a generated `.agents/skills/<handle>` command
  # handle, keeping the full plugin entry visible creates duplicate picker rows.
  # The plugin copy remains the canonical source; only the runtime cache entry
  # is pruned so the command handle owns mentionability.
  if [ -f "$command_surface_file" ] && [ -d "$skills_dir" ]; then
    local plugin_owner=""
    plugin_owner="$(
      jq -r '.name // empty | tostring | gsub("^\\s+|\\s+$"; "")' \
        "${plugin_dir:?}/.codex-plugin/plugin.json" 2>/dev/null || true
    )"
    if ! is_safe_path_component "$plugin_owner"; then
      plugin_owner="$(basename "$(dirname "${plugin_dir:?}")")"
    fi
    if ! is_safe_path_component "$plugin_owner"; then
      echo "[WARN] Ignoring unsafe plugin owner for command-surface pruning: $plugin_owner"
      return
    fi

    while IFS= read -r handle_name; do
      [ -n "$handle_name" ] || continue
      if ! is_safe_path_component "$handle_name"; then
        echo "[WARN] Ignoring unsafe command handle in command surface: $handle_name"
        continue
      fi
      if [ -e "${skills_dir:?}/${handle_name:?}" ] || [ -L "${skills_dir:?}/${handle_name:?}" ]; then
        rm -rf -- "${skills_dir:?}/${handle_name:?}"
        echo "[OK] Removed ${label} command-handle duplicate skill entry: ${skills_dir:?}/${handle_name:?}"
      fi
      while IFS= read -r skill_entry; do
        [ -n "$skill_entry" ] || continue
        rm -rf -- "${skill_entry:?}"
        echo "[OK] Removed ${label} command-handle duplicate skill entry: $skill_entry"
      done < <(
        find "$skills_dir" -type f -name SKILL.md -path "*/$handle_name/SKILL.md" -print 2>/dev/null \
          | while IFS= read -r skill_file; do dirname "$skill_file"; done
      )
    done < <(
      jq -r --arg owner "$plugin_owner" '
        ((.handles // []) + (.hidden_handles // []))[]
        | select(type == "object")
        | select((.owner // "") == $owner)
        | select(((.command_handle_path // "") | startswith(".agents/skills/")) or ((.command_visibility // "") == "none"))
        | .handle // empty
      ' "$command_surface_file" 2>/dev/null || true
    )
  fi
}

# Keep home-level plugin source paths aligned with the canonical repo plugins.
# Some plugin installers resolve marketplace relative paths (./Plugins/<name>)
# sync_home_plugin_mirrors copies local plugins from the canonical repo plugins
# tree into a home plugins directory, pruning stale copied plugin entries while
# sync_home_plugin_mirrors mirrors local plugins declared in a marketplace JSON into a home plugins directory as real copies, writes a source marker, materializes runtime skill symlink aliases, preserves reserved entries (`marketplace.json` and `cache`), and removes stale home plugin entries not listed in the marketplace.
sync_home_plugin_mirrors() {
  local marketplace_file="$1"
  local canonical_plugins_dir="$2"
  local home_plugins_dir="$3"
  local repo_plugin_marker=".codex-repo-plugin-source"
  local state_dir=""
  local keep_file=""
  local plugin_name=""
  local source_dir=""
  local target_dir=""
  local existing_dir=""
  local source_real=""
  local target_real=""
  local link_target=""
  local link_target_real=""
  local canonical_plugins_real=""
  local marker_file=""
  local marker_source=""
  local source_manifest=""
  local existing_manifest=""

  if [ ! -f "$marketplace_file" ]; then
    echo "[WARN] Marketplace file missing: $marketplace_file (skipping home plugin mirrors)."
    return 0
  fi

  mkdir -p "$home_plugins_dir"
  state_dir="$(mktemp -d)"
  cleanup_paths+=("$state_dir")
  keep_file="$state_dir/home-plugins.keep"
  : > "$keep_file"
  canonical_plugins_real="$(cd "$canonical_plugins_dir" 2>/dev/null && pwd -P || true)"

  # is_repo_managed_home_plugin_copy determines whether the given directory is a repository-managed copy of a plugin from the canonical plugins directory.
  # It returns exit status 0 if a marker file points into the canonical plugins real path or the `.codex-plugin/plugin.json` in the directory matches the canonical source; returns 1 otherwise.
  is_repo_managed_home_plugin_copy() {
    local existing_dir="$1"
    local legacy_source_dir="$canonical_plugins_dir/$(basename "$existing_dir")"

    marker_file="$existing_dir/$repo_plugin_marker"
    if [ -f "$marker_file" ]; then
      marker_source="$(head -n 1 "$marker_file" 2>/dev/null || true)"
      case "$marker_source" in
        "$canonical_plugins_real"/*)
          return 0
          ;;
      esac
    fi

    source_manifest="$legacy_source_dir/.codex-plugin/plugin.json"
    existing_manifest="$existing_dir/.codex-plugin/plugin.json"
    if [ ! -f "$source_manifest" ] || [ ! -f "$existing_manifest" ]; then
      return 1
    fi
    cmp -s -- "$source_manifest" "$existing_manifest"
  }

  # normalize_runtime_plugin_copy materializes symlinked skill files inside
  # copied plugin skills/ trees, then removes fixtures/ from runtime copies so
  # archive assets do not inflate active skill discovery surfaces while helper
  # modules stay reachable after pruning fixtures.
  normalize_runtime_plugin_copy() {
    normalize_plugin_copy "$1" "runtime"
  }

  while IFS= read -r plugin_name; do
    [ -n "$plugin_name" ] || continue
    if ! is_safe_path_component "$plugin_name"; then
      echo "[WARN] Invalid plugin name in marketplace: $plugin_name"
      continue
    fi
    source_dir="$canonical_plugins_dir/$plugin_name"
    target_dir="$home_plugins_dir/$plugin_name"
    printf '%s\n' "$target_dir" >> "$keep_file"

    if [ ! -d "$source_dir" ]; then
      echo "[WARN] Plugin listed in marketplace but missing in canonical dir: $source_dir"
      continue
    fi

    source_real="$(cd "$source_dir" 2>/dev/null && pwd -P || true)"
    target_real="$(cd "$target_dir" 2>/dev/null && pwd -P || true)"
    if [ -n "$source_real" ] && [ -n "$target_real" ] && [ "$source_real" = "$target_real" ]; then
      echo "[INFO] Skipping mirror because source and target resolve to same path: $target_dir"
      continue
    fi

    sync_user_skills "$source_dir" "$target_dir" 0 copy
    normalize_runtime_plugin_copy "$target_dir"
    marker_file="$target_dir/$repo_plugin_marker"
    printf '%s\n' "$source_real" > "$marker_file"
    echo "[OK] Installed home plugin copy: $target_dir"
  done < <(
    jq -r '
      def trim: gsub("^[[:space:]]+|[[:space:]]+$"; "");
      def is_safe_identifier: test("^[A-Za-z0-9._-]+$") and (test("/") | not) and (test("\\.\\.") | not) and (test("\\u0000") | not);
      .plugins[]?
      | select(type == "object")
      | select(.source.source == "local")
      | .name?
      | select(type == "string")
      | trim
      | select(length > 0)
      | select(is_safe_identifier)
    ' "$marketplace_file"
  )

  while IFS= read -r existing_dir; do
    [ -n "$existing_dir" ] || continue
    if grep -Fqx "$existing_dir" "$keep_file"; then
      continue
    fi
    case "$(basename "$existing_dir")" in
      marketplace.json|cache)
        continue
        ;;
    esac
    if [ ! -e "$existing_dir" ] && [ ! -L "$existing_dir" ]; then
      continue
    fi

    if [ -L "$existing_dir" ]; then
      link_target="$(readlink "$existing_dir" || true)"
      [ -n "$link_target" ] || continue
      link_target_real="$(cd "$(dirname "$existing_dir")" 2>/dev/null && cd "$link_target" 2>/dev/null && pwd -P || true)"
      [ -n "$link_target_real" ] || continue
      case "$link_target_real" in
        "$canonical_plugins_real"/*)
          rm -f -- "$existing_dir"
          echo "[OK] Removed stale home plugin entry: $existing_dir"
          ;;
      esac
      continue
    fi

    if ! is_repo_managed_home_plugin_copy "$existing_dir"; then
      continue
    fi
    rm -rf -- "$existing_dir"
    echo "[OK] Removed stale home plugin entry: $existing_dir"
  done < <(find "$home_plugins_dir" -mindepth 1 -maxdepth 1 -print)
}

prune_profile_command_handle_plugin_skills() {
  local marketplace_file="$1"
  local profile_plugins_dir="$2"
  local command_surface_file="$repo_root/.skillsets/command-surface.json"
  local plugin_name=""
  local handle=""
  local target_dir=""

  [ -f "$marketplace_file" ] || return 0
  [ -f "$command_surface_file" ] || return 0
  [ -d "$profile_plugins_dir" ] || return 0

  while IFS= read -r plugin_name; do
    [ -n "$plugin_name" ] || continue
    is_safe_path_component "$plugin_name" || continue
    while IFS= read -r handle; do
      [ -n "$handle" ] || continue
      is_safe_path_component "$handle" || continue
      target_dir="$profile_plugins_dir/$plugin_name/skills/$handle"
      if [ ! -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
        continue
      fi
      if rm -rf -- "$target_dir" 2>/dev/null; then
        echo "[OK] Removed command-handle duplicate plugin skill entry: $target_dir"
      else
        echo "[WARN] Skipped protected command-handle duplicate plugin skill entry: $target_dir"
      fi
    done < <(
      jq -r --arg plugin_name "$plugin_name" '
        ((.handles // []) + (.hidden_handles // []))[]
        | select((.owner // "") == $plugin_name)
        | select(((.command_handle_path // "") | startswith(".agents/skills/")) or ((.command_visibility // "") == "none"))
        | .handle // empty
      ' "$command_surface_file"
    )
  done < <(
    jq -r '
      def trim: gsub("^[[:space:]]+|[[:space:]]+$"; "");
      .plugins[]?
      | select(type == "object")
      | select(.source.source == "local")
      | .name?
      | select(type == "string")
      | trim
      | select(length > 0)
    ' "$marketplace_file"
  )
}

# Keep repo-local plugin caches aligned with the marketplace so Codex surfaces
# freshly updated plugin skills immediately in runtime discovery.
# sync_local_marketplace_cache synchronises local marketplace plugins listed in a marketplace JSON into the runtime cache at <cache-root>/<marketplace-name>/<plugin-name>, copying validated local plugin sources, flattening nested variants, and pruning stale entries.
sync_local_marketplace_cache() {
  local marketplace_file="$1"
  local cache_root="$2"
  local cache_state_dir=""
  local keep_file=""
  local marketplace_keep_file=""
  local plugin_rows_file=""
  local tracked_marketplaces_file=""
  local marketplace_name=""
  local plugin_name=""
  local source_path=""
  local source_dir=""
  local marketplace_dir=""
  local target_plugin_dir=""
  local child_dir=""
  local tracked_marketplace_dir=""

  # normalize_cached_plugin_runtime_copy materializes symlinked skill files and
  # removes fixtures from runtime cache plugin copies so archived skill fixtures
  # do not inflate active runtime skill counts while helper modules remain
  # importable.
  normalize_cached_plugin_runtime_copy() {
    normalize_plugin_copy "$1" "cached"
  }

  if [ ! -f "$marketplace_file" ]; then
    echo "[WARN] Marketplace file missing: $marketplace_file (skipping local marketplace cache sync)."
    mark_runtime_cache_stale
    return 0
  fi

  if ! can_mutate_sync_dir "$cache_root"; then
    skip_unwritable_sync_phase "local marketplace cache sync" "$cache_root"
    mark_runtime_cache_stale
    return 0
  fi

  cache_state_dir="$(mktemp -d)"
  cleanup_paths+=("$cache_state_dir")
  keep_file="$cache_state_dir/cache.keep"
  marketplace_keep_file="$cache_state_dir/marketplace.keep"
  plugin_rows_file="$cache_state_dir/plugin_rows.tsv"
  tracked_marketplaces_file="$cache_state_dir/tracked_marketplaces.txt"
  : > "$keep_file"
  : > "$marketplace_keep_file"
  : > "$plugin_rows_file"
  : > "$tracked_marketplaces_file"

  jq -r '
    def trim: gsub("^[[:space:]]+|[[:space:]]+$"; "");
    def is_safe_identifier: test("^[A-Za-z0-9._-]+$") and (test("/") | not) and (test("\\.\\.") | not) and (test("\\u0000") | not);
    (.name // "agent-skills-local" | tostring | trim) as $default_market
    | .plugins[]?
    | select(type == "object")
    | .name as $name
    | .source as $source
    | (.marketplace // $source.marketplace // $default_market | tostring | trim) as $market
    | select(($name | type) == "string")
    | select(($source | type) == "object")
    | select($source.source == "local")
    | select(($source.path | type) == "string")
    | ($name | trim) as $clean_name
    | ($source.path | trim) as $clean_path
    | select($market | is_safe_identifier)
    | select($clean_name | is_safe_identifier)
    | "\($market)\t\($clean_name)\t\($clean_path)"
  ' "$marketplace_file" > "$plugin_rows_file"

  while IFS=$'\t' read -r marketplace_name plugin_name source_path; do
    [ -n "$marketplace_name" ] || continue
    [ -n "$plugin_name" ] || continue
    [ -n "$source_path" ] || continue
    if ! is_safe_path_component "$marketplace_name"; then
      echo "[WARN] Invalid marketplace name in marketplace.json: $marketplace_name"
      continue
    fi
    if ! is_safe_path_component "$plugin_name"; then
      echo "[WARN] Invalid plugin name in marketplace.json: $plugin_name"
      continue
    fi
    source_dir="$(resolve_marketplace_source_dir "$source_path" || true)"
    if [ -z "$source_dir" ]; then
      echo "[WARN] Unsupported marketplace source.path for $plugin_name: $source_path"
      continue
    fi

    if [ ! -d "$source_dir" ]; then
      echo "[WARN] Cache source plugin directory missing for $plugin_name: $source_dir"
      continue
    fi

    target_plugin_dir="$cache_root/$marketplace_name/$plugin_name"
    marketplace_dir="$cache_root/$marketplace_name"
    printf '%s\n' "$marketplace_dir" >> "$marketplace_keep_file"

    # Remove any existing non-directory entries before mkdir
    if [ -e "$marketplace_dir" ] && [ ! -d "$marketplace_dir" ]; then
      rm -f "$marketplace_dir"
    fi

    if [ -L "$target_plugin_dir" ]; then
      rm -f "$target_plugin_dir"
    elif [ -e "$target_plugin_dir" ] && [ ! -d "$target_plugin_dir" ]; then
      rm -f "$target_plugin_dir"
    fi

    mkdir -p "$target_plugin_dir"
    printf '%s\n' "$target_plugin_dir" >> "$keep_file"

    if command -v rsync >/dev/null 2>&1; then
      rsync -a \
        --delete \
        --force \
        --exclude '.git' \
        --exclude 'node_modules' \
        --exclude '__pycache__' \
        --exclude '.DS_Store' \
        "$source_dir/" "$target_plugin_dir/"
    else
      rm -rf -- "$target_plugin_dir"
      mkdir -p "$target_plugin_dir"
      cp -R "$source_dir"/. "$target_plugin_dir"/
      rm -rf -- "$target_plugin_dir/.git" "$target_plugin_dir/node_modules" "$target_plugin_dir/__pycache__"
      find "$target_plugin_dir" -name '.DS_Store' -type f -delete
    fi

    normalize_cached_plugin_runtime_copy "$target_plugin_dir"

    # Remove stale nested cache variants (for example `local` or `0.1.0`) so
    # plugin roots resolve directly at <cache>/<marketplace>/<plugin>.
    while IFS= read -r child_dir; do
      [ -n "$child_dir" ] || continue
      if [ "$child_dir" = "$target_plugin_dir/.codex-plugin" ]; then
        continue
      fi
      if [ -f "$child_dir/.codex-plugin/plugin.json" ]; then
        rm -rf -- "$child_dir"
        echo "[OK] Removed nested cache variant: $child_dir"
      fi
    done < <(find "$target_plugin_dir" -mindepth 1 -maxdepth 1 -type d -print)
  done < "$plugin_rows_file"

  # Prune stale local-cache plugin dirs only inside marketplaces represented in
  # this marketplace file. Do not touch other cache families (for example
  # openai-curated snapshots).
  sort -u "$marketplace_keep_file" > "$tracked_marketplaces_file"
  while IFS= read -r tracked_marketplace_dir; do
    [ -n "$tracked_marketplace_dir" ] || continue
    [ -d "$tracked_marketplace_dir" ] || continue
    while IFS= read -r existing_plugin_dir; do
      [ -n "$existing_plugin_dir" ] || continue
      if ! grep -Fqx "$existing_plugin_dir" "$keep_file"; then
        rm -rf -- "$existing_plugin_dir"
        echo "[OK] Removed stale local cache plugin dir: $existing_plugin_dir"
      fi
    done < <(find "$tracked_marketplace_dir" -mindepth 1 -maxdepth 1 -type d -print)

    if [ -d "$tracked_marketplace_dir" ] && [ -z "$(find "$tracked_marketplace_dir" -mindepth 1 -maxdepth 1 -type d -print -quit)" ]; then
      rm -rf -- "$tracked_marketplace_dir"
      echo "[OK] Removed empty marketplace cache dir: $tracked_marketplace_dir"
    fi
  done < "$tracked_marketplaces_file"
}

# sync_versioned_local_marketplace_cache keeps the legacy repository-local
# cache shape aligned for Codex builds that still inspect
# sync_versioned_local_marketplace_cache synchronizes local marketplace plugins listed in a marketplace JSON into a versioned cache at the given cache root, installing each plugin under <cache_root>/<marketplace>/<plugin>/<version>, normalizing copied plugin content, and pruning stale versions and plugin directories.
sync_versioned_local_marketplace_cache() {
  local marketplace_file="$1"
  local cache_root="$2"
  local state_dir=""
  local plugin_rows_file=""
  local keep_file=""
  local market_keep_file=""
  local tracked_markets_file=""
  local marketplace_name=""
  local plugin_name=""
  local source_path=""
  local source_dir=""
  local plugin_version=""
  local market_dir=""
  local plugin_dir=""
  local target_dir=""
  local existing_dir=""
  local tracked_market_dir=""

  if [ ! -f "$marketplace_file" ]; then
    echo "[WARN] Marketplace file missing: $marketplace_file (skipping versioned local marketplace cache sync)."
    return 0
  fi

  if ! can_mutate_sync_dir "$cache_root"; then
    skip_unwritable_sync_phase "versioned local marketplace cache sync" "$cache_root"
    mark_runtime_cache_stale
    return 0
  fi

  state_dir="$(mktemp -d)"
  cleanup_paths+=("$state_dir")
  plugin_rows_file="$state_dir/versioned_plugin_rows.tsv"
  keep_file="$state_dir/versioned_cache.keep"
  market_keep_file="$state_dir/versioned_markets.keep"
  tracked_markets_file="$state_dir/versioned_markets.txt"
  : > "$keep_file"
  : > "$market_keep_file"

  jq -r '
    def trim: gsub("^[[:space:]]+|[[:space:]]+$"; "");
    def is_safe_identifier: test("^[A-Za-z0-9._-]+$") and (test("/") | not) and (test("\\.\\.") | not) and (test("\\u0000") | not);
    (.name // "agent-skills-local" | tostring | trim) as $default_market
    | .plugins[]?
    | select(type == "object")
    | .name as $name
    | .source as $source
    | (.marketplace // $source.marketplace // $default_market | tostring | trim) as $market
    | select(($name | type) == "string")
    | select(($source | type) == "object")
    | select($source.source == "local")
    | select(($source.path | type) == "string")
    | ($name | trim) as $clean_name
    | ($source.path | trim) as $clean_path
    | select($market | is_safe_identifier)
    | select($clean_name | is_safe_identifier)
    | "\($market)\t\($clean_name)\t\($clean_path)"
  ' "$marketplace_file" > "$plugin_rows_file"

  while IFS=$'\t' read -r marketplace_name plugin_name source_path; do
    [ -n "$marketplace_name" ] || continue
    [ -n "$plugin_name" ] || continue
    [ -n "$source_path" ] || continue
    if ! is_safe_path_component "$marketplace_name" || ! is_safe_path_component "$plugin_name"; then
      echo "[WARN] Invalid versioned cache marketplace/plugin identity: $marketplace_name/$plugin_name"
      continue
    fi

    source_dir="$(resolve_marketplace_source_dir "$source_path" || true)"
    if [ -z "$source_dir" ] || [ ! -d "$source_dir" ]; then
      echo "[WARN] Versioned cache source plugin directory missing for $plugin_name: $source_path"
      continue
    fi

    plugin_version="$(jq -r '.version // "0.1.0" | tostring | gsub("^\\s+|\\s+$"; "")' "$source_dir/.codex-plugin/plugin.json" 2>/dev/null || printf '0.1.0')"
    [ -n "$plugin_version" ] || plugin_version="0.1.0"
    if ! is_safe_path_component "$plugin_version"; then
      echo "[WARN] Invalid plugin version in plugin.json for $plugin_name: $plugin_version"
      continue
    fi

    market_dir="$cache_root/$marketplace_name"
    plugin_dir="$market_dir/$plugin_name"
    target_dir="$plugin_dir/$plugin_version"
    printf '%s\n' "$market_dir" >> "$market_keep_file"
    printf '%s\n' "$plugin_dir" >> "$keep_file"

    if [ -L "$plugin_dir" ] || [ -f "$plugin_dir/.codex-plugin/plugin.json" ]; then
      rm -rf -- "$plugin_dir"
    elif [ -e "$plugin_dir" ] && [ ! -d "$plugin_dir" ]; then
      rm -f -- "$plugin_dir"
    fi

    if [ -e "$target_dir" ] || [ -L "$target_dir" ]; then
      rm -rf -- "$target_dir"
    fi
    mkdir -p "$target_dir"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete --force \
        --exclude '.git' \
        --exclude 'node_modules' \
        --exclude '__pycache__' \
        --exclude '.DS_Store' \
        "$source_dir/" "$target_dir/"
    else
      rm -rf -- "$target_dir"
      mkdir -p "$target_dir"
      cp -R "$source_dir"/. "$target_dir"/
      rm -rf -- "$target_dir/.git" "$target_dir/node_modules" "$target_dir/__pycache__"
      find "$target_dir" -name '.DS_Store' -type f -delete
    fi

    normalize_plugin_copy "$target_dir" "versioned-cache"
    while IFS= read -r existing_dir; do
      [ -n "$existing_dir" ] || continue
      [ "$existing_dir" = "$target_dir" ] && continue
      rm -rf -- "$existing_dir"
      echo "[OK] Removed stale versioned local cache variant: $existing_dir"
    done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d -print)
  done < "$plugin_rows_file"

  sort -u "$market_keep_file" > "$tracked_markets_file"
  while IFS= read -r tracked_market_dir; do
    [ -n "$tracked_market_dir" ] || continue
    [ -d "$tracked_market_dir" ] || continue
    while IFS= read -r existing_dir; do
      [ -n "$existing_dir" ] || continue
      if ! grep -Fqx "$existing_dir" "$keep_file"; then
        rm -rf -- "$existing_dir"
        echo "[OK] Removed stale versioned local cache plugin dir: $existing_dir"
      fi
    done < <(find "$tracked_market_dir" -mindepth 1 -maxdepth 1 -type d -print)
  done < "$tracked_markets_file"
}

# sync_repo_cache_snapshots_to_runtime_cache syncs repository plugin cache snapshots from the source directory into the runtime cache directory, ensuring the target exists and replacing its contents.
sync_repo_cache_snapshots_to_runtime_cache() {
  local source_cache_root="$1"
  local target_cache_root="$2"

  if [ ! -d "$source_cache_root" ]; then
    return 0
  fi

  if ! can_mutate_sync_dir "$target_cache_root"; then
    skip_unwritable_sync_phase "repository plugin cache snapshot sync" "$target_cache_root"
    mark_runtime_cache_stale
    return 0
  fi

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --force "$source_cache_root/" "$target_cache_root/"
  else
    rm -rf -- "$target_cache_root"
    mkdir -p "$target_cache_root"
    cp -R "$source_cache_root"/. "$target_cache_root"/
  fi
}

# materialize_plugin_cache_roots ensures each plugin directory under `cache_root` contains a top-level `.codex-plugin` root by locating a nested candidate (preferentially `local/`) and promoting it into the plugin directory, removing other nested `.codex-plugin` roots.
#
# Arguments:
#   cache_root - path to the runtime cache root containing marketplace/plugin subdirectories.
materialize_plugin_cache_roots() {
  local cache_root="$1"
  local marketplace_dir=""
  local plugin_dir=""
  local candidate_dir=""
  local child_dir=""

  [ -d "$cache_root" ] || return 0
  if ! can_mutate_sync_dir "$cache_root"; then
    skip_unwritable_sync_phase "plugin cache root materialization" "$cache_root"
    mark_runtime_cache_stale
    return 0
  fi

  while IFS= read -r marketplace_dir; do
    [ -n "$marketplace_dir" ] || continue
    while IFS= read -r plugin_dir; do
      [ -n "$plugin_dir" ] || continue
      if [ -f "$plugin_dir/.codex-plugin/plugin.json" ]; then
        continue
      fi

      candidate_dir=""
      if [ -f "$plugin_dir/local/.codex-plugin/plugin.json" ]; then
        candidate_dir="$plugin_dir/local"
      else
        while IFS= read -r child_dir; do
          [ -n "$child_dir" ] || continue
          if [ -f "$child_dir/.codex-plugin/plugin.json" ]; then
            candidate_dir="$child_dir"
            break
          fi
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d | sort)
      fi

      if [ -z "$candidate_dir" ]; then
        continue
      fi

      if [[ "$candidate_dir" == "$plugin_dir/"* ]]; then
        local tmp_copy_dir=""
        tmp_copy_dir="$(mktemp -d)"
        cleanup_paths+=("$tmp_copy_dir")
        cp -R "$candidate_dir"/. "$tmp_copy_dir"/
        while IFS= read -r child_dir; do
          [ -n "$child_dir" ] || continue
          rm -rf -- "$child_dir"
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -print)
        cp -R "$tmp_copy_dir"/. "$plugin_dir"/
      elif command -v rsync >/dev/null 2>&1; then
        rsync -a --delete --force "$candidate_dir/" "$plugin_dir/"
      else
        local tmp_copy_dir=""
        tmp_copy_dir="$(mktemp -d)"
        cleanup_paths+=("$tmp_copy_dir")
        cp -R "$candidate_dir"/. "$tmp_copy_dir"/
        while IFS= read -r child_dir; do
          [ -n "$child_dir" ] || continue
          rm -rf -- "$child_dir"
        done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -print)
        cp -R "$tmp_copy_dir"/. "$plugin_dir"/
      fi

      while IFS= read -r child_dir; do
        [ -n "$child_dir" ] || continue
        if [ "$child_dir" = "$plugin_dir/.codex-plugin" ]; then
          continue
        fi
        if [ -f "$child_dir/.codex-plugin/plugin.json" ]; then
          rm -rf -- "$child_dir"
          echo "[OK] Flattened plugin cache root: $plugin_dir (removed $child_dir)"
        fi
      done < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d -print)
    done < <(find "$marketplace_dir" -mindepth 1 -maxdepth 1 -type d -print)
  done < <(find "$cache_root" -mindepth 1 -maxdepth 1 -type d -print)
}

# sync_codex_profile_homes synchronises skills, plugin runtime cache and marketplace metadata into each Codex profile home found under $HOME.
# sync_codex_profile_homes projects skills, plugin cache snapshots, and marketplace manifests into each Codex profile home and ensures profile-local plugin mirrors so local plugin installs resolve under each profile's Plugins directory.
# sync_codex_profile_homes syncs the repository runtime cache and marketplace manifest into each detected Codex profile home, ensures profile plugin-root directories are real, mirrors marketplace-listed local plugins into each profile, and materializes plugin cache roots.
# Arguments: cache_source — path to the repository runtime cache to copy into each profile; marketplace_file — path to a marketplace JSON file to install into each profile's Plugins/marketplace.json.
sync_codex_profile_homes() {
  local cache_source="$1"
  local marketplace_file="$2"
  local profile_home=""
  local profile_plugins=""
  local profile_plugins_root=""
  local profile_agents_plugins=""
  local profile_cache_target=""
  local cache_source_real=""
  local profile_cache_target_real=""
  local marketplace_target=""
  local profile_plugins_ready=0
  local profile_plugins_root_ready=0
  local profile_agents_plugins_ready=0

  while IFS= read -r profile_home; do
    [ -n "$profile_home" ] || continue
    [ -d "$profile_home" ] || continue

    if [ "$flat_projection_rebuilt" = "1" ]; then
      sync_user_skills "$skills_dir" "$profile_home/skills"
    else
      echo "[INFO] Skipping profile skills sync because flat runtime skill projection was not rebuilt."
    fi

    profile_plugins="$profile_home/plugins"
    profile_plugins_root="$profile_home/Plugins"
    profile_agents_plugins="$profile_home/.agents/plugins"
    profile_plugins_ready=0
    profile_plugins_root_ready=0
    profile_agents_plugins_ready=0
    if ensure_real_home_plugin_root "$profile_plugins" "$plugins_dir" "profile plugin root"; then
      profile_plugins_ready=1
    fi
    if ensure_real_home_plugin_root "$profile_plugins_root" "$plugins_dir" "profile Plugins root"; then
      profile_plugins_root_ready=1
    fi
    if ensure_real_home_plugin_root "$profile_agents_plugins" "$plugins_dir" "profile .agents plugin root"; then
      profile_agents_plugins_ready=1
    fi

    profile_cache_target="$profile_plugins_root/cache"
    cache_source_real="$(cd "$cache_source" 2>/dev/null && pwd -P || true)"
    profile_cache_target_real="$(cd "$profile_cache_target" 2>/dev/null && pwd -P || true)"
    if [ "$profile_plugins_root_ready" != "1" ]; then
      skip_unwritable_sync_phase "profile cache publication" "$profile_plugins_root"
    elif [ "$runtime_cache_fresh" != "1" ]; then
      echo "[INFO] Skipping profile cache publication because runtime cache rebuild was not fresh."
    elif [ -n "$cache_source_real" ] && [ -n "$profile_cache_target_real" ] && [ "$cache_source_real" = "$profile_cache_target_real" ]; then
      echo "[INFO] Skipping profile cache copy for identical source/target: $profile_cache_target"
    else
      sync_user_skills "$cache_source" "$profile_cache_target" 0 copy
      materialize_plugin_cache_roots "$profile_cache_target"
    fi
    if [ "$runtime_cache_fresh" != "1" ]; then
      echo "[INFO] Skipping profile marketplace publication because runtime cache rebuild was not fresh."
      if [ -f "$marketplace_file" ]; then
        # Profile plugin mirrors are live picker inputs. Keep them aligned even
        # when cache publication is skipped, otherwise stale plugin copies can
        # duplicate generated command handles such as sy-spec and sy-work.
        if [ "$profile_plugins_root_ready" = "1" ] && can_mutate_sync_dir "$profile_plugins_root"; then
          sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins_root"
          prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins_root"
        else
          skip_unwritable_sync_phase "profile Plugins mirror publication" "$profile_plugins_root"
        fi
        if [ "$profile_plugins_ready" = "1" ] && can_mutate_sync_dir "$profile_plugins"; then
          sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"
          prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins"
        else
          skip_unwritable_sync_phase "profile plugin mirror publication" "$profile_plugins"
        fi
        if [ "$profile_agents_plugins_ready" = "1" ] && can_mutate_sync_dir "$profile_agents_plugins"; then
          sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"
          prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_agents_plugins"
        else
          skip_unwritable_sync_phase "profile .agents plugin mirror publication" "$profile_agents_plugins"
        fi
      fi
    elif [ "$profile_plugins_root_ready" != "1" ]; then
      skip_unwritable_sync_phase "profile marketplace publication" "$profile_plugins_root"
    elif [ -f "$marketplace_file" ]; then
      marketplace_target="$profile_plugins_root/marketplace.json"
      if [ -e "$marketplace_target" ] && cmp -s "$marketplace_file" "$marketplace_target"; then
        echo "[INFO] Profile marketplace manifest already points at canonical source: $marketplace_target"
      else
        cp "$marketplace_file" "$marketplace_target"
        echo "[OK] Synced profile marketplace manifest: $marketplace_target"
      fi
      # Keep profile-local marketplace source paths resolvable at
      # <profile-home>/Plugins/<plugin-name> for local plugin installs.
      if can_mutate_sync_dir "$profile_plugins_root"; then
        sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins_root"
        prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins_root"
      else
        skip_unwritable_sync_phase "profile Plugins mirror publication" "$profile_plugins_root"
      fi
      if [ "$profile_plugins_ready" = "1" ] && can_mutate_sync_dir "$profile_plugins"; then
        sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"
        prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_plugins"
      else
        skip_unwritable_sync_phase "profile plugin mirror publication" "$profile_plugins"
      fi
      if [ "$profile_agents_plugins_ready" = "1" ] && can_mutate_sync_dir "$profile_agents_plugins"; then
        sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_agents_plugins"
        prune_profile_command_handle_plugin_skills "$marketplace_file" "$profile_agents_plugins"
      else
        skip_unwritable_sync_phase "profile .agents plugin mirror publication" "$profile_agents_plugins"
      fi
    fi
  done < <({
    [ -d "$HOME/.codex" ] && printf '%s\n' "$HOME/.codex"
    find "$HOME" -maxdepth 1 -mindepth 1 -type d -name '.codex-*'
  } | sort -u)
}

# cleanup_legacy_local_marketplace_cache removes a legacy visible local marketplace
# cleanup_legacy_local_marketplace_cache removes a legacy local marketplace cache directory or symlink if it exists, skipping the operation when the parent directory cannot be safely mutated.
cleanup_legacy_local_marketplace_cache() {
  local legacy_cache_root="$1"
  if [ -d "$legacy_cache_root" ] || [ -L "$legacy_cache_root" ]; then
    if ! can_mutate_sync_dir "$(dirname "$legacy_cache_root")"; then
      skip_unwritable_sync_phase "legacy local marketplace cache cleanup" "$(dirname "$legacy_cache_root")"
      return 0
    fi
    rm -rf -- "$legacy_cache_root"
    echo "[OK] Removed legacy visible local marketplace cache: $legacy_cache_root"
  fi
}

# sync_plugin_cache_projections synchronizes plugin-cache projections by invoking Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py; if that script is missing or the runtime cache root cannot be mutated, it logs a warning and skips the sync.
sync_plugin_cache_projections() {
  local projection_script="$repo_root/Infrastructure/scripts/lifecycle-and-sync/projection_integrity.py"

  if [ ! -f "$projection_script" ]; then
    echo "[WARN] Projection integrity script missing; skipping plugin-cache header sync."
    mark_runtime_cache_stale
    return 0
  fi
  if ! can_mutate_sync_dir "$runtime_cache_root"; then
    skip_unwritable_sync_phase "plugin-cache projection sync" "$runtime_cache_root"
    mark_runtime_cache_stale
    return 0
  fi

  python3 "$projection_script" sync --scope plugin-caches --format text
}

# Sync to Claude Code, OpenAI Codex/Agents, and Gemini loaders.
sync_repo_cache_snapshots_to_runtime_cache "$plugins_dir/cache" "$runtime_cache_root"
sync_local_marketplace_cache "$plugins_dir/marketplace.json" "$runtime_cache_root"
materialize_plugin_cache_roots "$runtime_cache_root"
cleanup_legacy_local_marketplace_cache "$plugins_dir/cache/local"
cleanup_legacy_local_marketplace_cache "$runtime_cache_root/local"
sync_plugin_cache_projections
if [ "$runtime_cache_rebuild_blocked" = "0" ]; then
  runtime_cache_fresh=1
fi
sync_versioned_local_marketplace_cache "$plugins_dir/marketplace.json" "$plugins_dir/cache"
# On case-insensitive filesystems (e.g. default macOS), "skills" aliases
# "Skills"; forcing a lowercase symlink would replace the canonical tracked
# Skills/ tree and can introduce symlink loops.
if [ -d "$repo_root/Skills" ] && [ ! -L "$repo_root/Skills" ]; then
  echo "[INFO] Skipping repo-local skills symlink projection because canonical Skills/ exists."
elif [ "$flat_projection_rebuilt" = "1" ]; then
  sync_user_skills "$skills_dir" "$repo_root/skills" 1
else
  echo "[INFO] Skipping repo-local skills symlink projection because flat runtime skill projection was not rebuilt."
fi
sync_user_skills "$plugins_dir" "$repo_root/.agents/plugins" 1
if [[ "$sync_scope" == "user" ]]; then
  remove_legacy_home_skill_symlinks
  if [ "$flat_projection_rebuilt" = "1" ]; then
    sync_user_skills "$skills_dir" "$HOME/.agents/skills"
  else
    echo "[INFO] Skipping home skills sync because flat runtime skill projection was not rebuilt."
  fi
  sync_user_skills "$repo_root" "$HOME/.agents/agent-skills"
  sync_user_skills "$plugins_dir" "$HOME/.agents/plugins"
  home_plugins_ready=0
  if ensure_real_home_plugin_root "$HOME/plugins" "$plugins_dir" "home plugin root"; then
    home_plugins_ready=1
  fi
  sync_codex_profile_homes "$runtime_cache_root" "$plugins_dir/marketplace.json"
  if [ "$home_plugins_ready" = "1" ] && can_mutate_sync_dir "$HOME/plugins"; then
    sync_home_plugin_mirrors "$plugins_dir/marketplace.json" "$plugins_dir" "$HOME/plugins"
  else
    skip_unwritable_sync_phase "home plugin mirror publication" "$HOME/plugins"
  fi
else
  echo "Workspace scope: skipped home runtime projections."
fi

chmod +x "$repo_root/Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh"

echo "Selection policy identity: $SELECTION_POLICY_IDENTITY"
echo "Synced symlinks and regenerated SKILL.md."
