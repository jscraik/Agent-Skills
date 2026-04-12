#!/usr/bin/env bash
set -euo pipefail

timeout_seconds="${SYNC_SKILLS_TIMEOUT_SECONDS:-300}"
sync_scope="${SYNC_SKILLS_SCOPE:-workspace}"
lock_dir="${TMPDIR:-/tmp}/agent-skills-sync.lock"
lock_pid_file="$lock_dir/pid"
lock_owned=0
watchdog_pid=""

usage() {
  cat <<'USAGE'
Usage:
  scripts/sync_skills.sh [--timeout-seconds <int>] [--project-local|--workspace]

Regenerates skill/plugin symlinks and SKILL.md index for this repository.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --timeout-seconds)
      timeout_seconds="${2:-}"
      shift 2
      ;;
    --project-local)
      sync_scope="project-local"
      shift
      ;;
    --workspace)
      sync_scope="workspace"
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

if [[ "$sync_scope" != "project-local" && "$sync_scope" != "workspace" ]]; then
  echo "Invalid sync scope: $sync_scope (expected project-local or workspace)" >&2
  exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

selection_policy_shell="$(
  python3 "$repo_root/scripts/selection_policy.py" --format shell
)"
if [ -z "$selection_policy_shell" ]; then
  echo "Failed to load selection policy shell exports." >&2
  exit 1
fi
eval "$selection_policy_shell"

acquire_sync_lock() {
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
  fi

  rm -rf -- "$lock_dir"
  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\n' "$$" > "$lock_pid_file"
    lock_owned=1
    return 0
  fi

  echo "Unable to acquire sync lock at $lock_dir" >&2
  exit 1
}

start_watchdog() {
  (
    sleep "$timeout_seconds"
    echo "[ERROR] sync_skills timed out after ${timeout_seconds}s" >&2
    kill -TERM "$$" 2>/dev/null || true
  ) &
  watchdog_pid="$!"
}

stop_watchdog() {
  if [[ -n "$watchdog_pid" ]]; then
    kill "$watchdog_pid" 2>/dev/null || true
    wait "$watchdog_pid" 2>/dev/null || true
    watchdog_pid=""
  fi
}

release_sync_lock() {
  if [[ "$lock_owned" -eq 1 ]]; then
    rm -rf -- "$lock_dir"
    lock_owned=0
  fi
}

acquire_sync_lock
start_watchdog

skills_dir="$repo_root/.agents/skills"
plugins_dir="$repo_root/plugins"
runtime_cache_root="$repo_root/.agents/plugins-runtime/cache"
system_skills_dir="$repo_root/skills-system"
antigravity_skills_dir="$repo_root/skills-antigravity"
antigravity_skills_txt="$HOME/.gemini/antigravity/skills.txt"

mkdir -p "$skills_dir"
mkdir -p "$plugins_dir"

# Security guard: never operate on a symlinked antigravity catalog path.
if [ -L "$antigravity_skills_dir" ]; then
  echo "Refusing to use symlinked path: $antigravity_skills_dir" >&2
  exit 1
fi
if [ -e "$antigravity_skills_dir" ] && [ ! -d "$antigravity_skills_dir" ]; then
  echo "Refusing to use non-directory path: $antigravity_skills_dir" >&2
  exit 1
fi
mkdir -p "$antigravity_skills_dir"
if [ -L "$antigravity_skills_dir" ]; then
  echo "Refusing to use symlinked path: $antigravity_skills_dir" >&2
  exit 1
fi

repo_root_real="$(cd "$repo_root" && pwd -P)"
antigravity_skills_dir_real="$(cd "$antigravity_skills_dir" && pwd -P)"
if [ "$antigravity_skills_dir_real" != "$repo_root_real/skills-antigravity" ]; then
  echo "Refusing to use unexpected antigravity path: $antigravity_skills_dir_real" >&2
  exit 1
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
      cp -R "$skills_dir/.system"/. "$system_skills_dir"/ 2>/dev/null || true
    fi
    if ! rm -rf "$skills_dir/.system"; then
      echo "[WARN] Unable to remove $skills_dir/.system after preservation (continuing anyway)."
    fi
  fi
fi

# Remove stale symlinks only (keep any real files that might be intentional).
if [ -w "$skills_dir" ]; then
  find "$skills_dir" -maxdepth 1 -type l -exec rm -f {} +
else
  echo "[WARN] $skills_dir is not writable; skipping stale symlink cleanup."
fi

# Remove meta/internal skills from the flat runtime surface so they do not
# appear as user-selectable skills in Codex. Lifecycle family skills such as
# `skill-creator` and `skill-installer` are intentionally visible again.
hidden_flat_skills=("${SELECTION_POLICY_HIDDEN_FLAT_SKILLS[@]}")
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
for hidden_skill in "${hidden_flat_skills[@]}"; do
  if [ -e "$skills_dir/$hidden_skill" ]; then
    if rm -rf -- "${skills_dir:?}/${hidden_skill:?}"; then
      echo "Removed hidden flat skill: $hidden_skill"
    else
      echo "[WARN] Could not remove hidden skill $hidden_skill at $skills_dir (continuing anyway)."
    fi
  fi
done

# Recreate symlinks for all discovered SKILL.md directories (with exclusions).
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
  for plugin_skills_root in ${SELECTION_POLICY_PLUGIN_SKILL_ROOT_GLOB}; do
    [ -d "$plugin_skills_root" ] || continue
    find_skill_files_with_policy "$plugin_skills_root"
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
# under plugins/<plugin>/skills/<skill>. These should not appear as standalone
# entries in the flat runtime skill list.
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
    "$repo_root_real"/plugins/*/skills/*) return 0 ;;
    *) return 1 ;;
  esac
}

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
    if ! is_plugin_visible_router_skill_name "$skill_name"; then
      echo "Skipping plugin-owned skill from flat projection: $skill_name"
      continue
    fi
    if is_plugin_hidden_lane_skill_name "$skill_name"; then
      echo "Skipping hidden plugin lane skill: $skill_name"
      continue
    fi
    if ! is_plugin_visible_router_skill_name "$skill_name"; then
      echo "Skipping non-router plugin skill in flat runtime list: $skill_name"
      continue
    fi
    if ! register_plugin_router_skill_source "$skill_name" "$discovered_dir"; then
      router_collision_count=$((router_collision_count + 1))
      continue
    fi
    echo "Including plugin-owned skill in flat runtime list: $skill_name"
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

# Keep only the approved bridge skills routed through the hidden `.system`
# lane so these four remain available while avoiding direct top-level plugin
# path coupling in profile homes.
for bridge_skill in "${system_bridge_skills[@]}"; do
  bridge_source=".system/$bridge_skill"
  if [ ! -e "$skills_dir/$bridge_source" ]; then
    echo "[WARN] Missing system bridge source: $skills_dir/$bridge_source"
    continue
  fi

  if [ -L "$skills_dir/$bridge_skill" ]; then
    rm -f "$skills_dir/$bridge_skill"
  elif [ -e "$skills_dir/$bridge_skill" ]; then
    rm -rf -- "${skills_dir:?}/${bridge_skill:?}"
  fi

  ln -s "$bridge_source" "$skills_dir/$bridge_skill"
  echo "Routed bridge skill through .system: $bridge_skill -> $bridge_source"
done

# Build a strict Antigravity-compatible projection:
# - flat first-level skill folders only
# - each folder must contain SKILL.md
# - each entry must be a first-level directory with SKILL.md (symlink or real dir)
# This avoids loader confusion from metadata folders like .system/ or helper repos.
#
# Keep the projection incremental instead of deleting everything first:
# unchanged skills stay in place, changed skills are refreshed, and stale skills
# are pruned at the end. This preserves output behavior while reducing I/O.
antigravity_state_dir="$(mktemp -d)"
cleanup_paths+=("$antigravity_state_dir")
antigravity_keep_file="$antigravity_state_dir/skills.keep"
: > "$antigravity_keep_file"

for skill_entry in "$skills_dir"/*; do
  # Keep hidden entries excluded (glob does not match dotfiles like .system),
  # but allow both symlinked and real first-level directories with SKILL.md.
  if [ ! -d "$skill_entry" ]; then
    continue
  fi
  if [ ! -f "$skill_entry/SKILL.md" ]; then
    continue
  fi

  skill_name="$(basename "$skill_entry")"
  target_dir="$antigravity_skills_dir/$skill_name"
  printf '%s\n' "$skill_name" >> "$antigravity_keep_file"
  mkdir -p "$target_dir"

  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --delete \
      --exclude '.git' \
      --exclude 'node_modules' \
      --exclude '__pycache__' \
      "$skill_entry/" "$target_dir/"
  else
    rm -rf -- "$target_dir"
    mkdir -p "$target_dir"
    cp -R "$skill_entry"/. "$target_dir"/
    rm -rf -- "$target_dir/.git" "$target_dir/node_modules" "$target_dir/__pycache__"
  fi
done

# Remove non-directory entries that could confuse flat directory loaders.
find "$antigravity_skills_dir" -mindepth 1 -maxdepth 1 ! -type d -exec rm -rf -- {} +

# Prune stale directories that were not refreshed in this run.
while IFS= read -r existing_dir; do
  existing_name="$(basename "$existing_dir")"
  if ! grep -Fqx "$existing_name" "$antigravity_keep_file"; then
    rm -rf -- "$existing_dir"
  fi
done < <(find "$antigravity_skills_dir" -mindepth 1 -maxdepth 1 -type d -print)

# generate_skill_index regenerates the repository root SKILL.md index from skills' YAML frontmatter, grouping skills by category and extracting short descriptions where available.
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

    # Store description (or placeholder)
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
# generate_skill_type_index takes a single argument: the path to the output index file.
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

python3 "$repo_root/scripts/skill_catalog.py" --source repo --write-index "$repo_root/SKILL.md"
generate_skill_type_index "$repo_root/docs/skills-by-type.md"

# Remove legacy tool symlinks (no longer supported)
remove_legacy_symlink() {
  local target_dir="$1"
  if [ -L "$target_dir" ]; then
    rm -f "$target_dir"
    echo "[OK] Removed legacy symlink: $target_dir"
  fi
}

# Remove old/legacy symlinks from unsupported locations.
# Keep this workspace-only so project-local sync stays side-effect free outside
# the repository checkout.
remove_legacy_home_skill_symlinks() {
  remove_legacy_symlink "$HOME/.copilot/skills"
  remove_legacy_symlink "$HOME/.config/agents/skills"
  remove_legacy_symlink "$HOME/.cursor/skills"
  remove_legacy_symlink "$HOME/.gemini/skills"
}

# Sync to user-level tool directories (Claude Code + OpenAI Codex/Agents)
sync_user_skills() {
  local source_dir="$1"
  local target_dir="$2"
  local force="${3:-0}"
  local mode="${4:-symlink}"

  sync_dir_copy() {
    local source_dir="$1"
    local target_dir="$2"

    mkdir -p "$target_dir"

    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete --force "$source_dir/" "$target_dir/"
      return 0
    fi

    # Fallback for environments without rsync.
    find "$target_dir" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    cp -a "$source_dir/." "$target_dir/"
  }

  if [ "$mode" = "copy" ]; then
    mkdir -p "$(dirname "$target_dir")"
    if [ -L "$target_dir" ] || [ ! -d "$target_dir" ]; then
      rm -rf "$target_dir" || echo "[WARN] Could not replace non-directory target at $target_dir (continuing with copy)."
    fi
    sync_dir_copy "$source_dir" "$target_dir"
    echo "[OK] Synced directory: $target_dir"
    return 0
  fi

  mkdir -p "$(dirname "$target_dir")"
  if [ -L "$target_dir" ]; then
    # Update existing symlink
    if ln -sfn "$source_dir" "$target_dir"; then
      echo "[OK] Updated symlink: $target_dir -> $source_dir"
    else
      echo "[WARN] Unable to update symlink $target_dir -> $source_dir (continuing)."
    fi
  elif [ -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
    if [ "$force" = "1" ]; then
      if rm -rf "$target_dir"; then
        if ln -s "$source_dir" "$target_dir"; then
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
    ln -s "$source_dir" "$target_dir"
    echo "[OK] Created symlink: $target_dir -> $source_dir"
  fi
}

sync_skill_path_file() {
  local source_dir="$1"
  local target_file="$2"
  local rendered_dir="${source_dir%/}/"
  mkdir -p "$(dirname "$target_file")"
  printf '%s\n' "$rendered_dir" > "$target_file"
  echo "[OK] Wrote skill path file: $target_file -> $rendered_dir"
}

# Keep home-level plugin source paths aligned with the canonical repo plugins.
# Some plugin installers resolve marketplace relative paths (./plugins/<name>)
# against $HOME, so this mirror prevents "path is not a directory" failures.
sync_home_plugin_mirrors() {
  local marketplace_file="$1"
  local canonical_plugins_dir="$2"
  local home_plugins_dir="$3"
  local plugin_name=""
  local source_dir=""
  local target_dir=""

  if [ ! -f "$marketplace_file" ]; then
    echo "[WARN] Marketplace file missing: $marketplace_file (skipping home plugin mirrors)."
    return 0
  fi

  mkdir -p "$home_plugins_dir"

  while IFS= read -r plugin_name; do
    [ -n "$plugin_name" ] || continue
    source_dir="$canonical_plugins_dir/$plugin_name"
    target_dir="$home_plugins_dir/$plugin_name"

    if [ ! -d "$source_dir" ]; then
      echo "[WARN] Plugin listed in marketplace but missing in canonical dir: $source_dir"
      continue
    fi

    if [ -L "$target_dir" ]; then
      if ln -sfn "$source_dir" "$target_dir"; then
        echo "[OK] Updated home plugin symlink: $target_dir -> $source_dir"
      else
        echo "[WARN] Unable to update home plugin symlink $target_dir -> $source_dir"
      fi
    elif [ -e "$target_dir" ]; then
      echo "[WARN] $target_dir exists as a non-symlink; leaving it untouched."
      echo "       Move/remove it to allow canonical mirror linking."
    else
      if ln -s "$source_dir" "$target_dir"; then
        echo "[OK] Created home plugin symlink: $target_dir -> $source_dir"
      else
        echo "[WARN] Unable to create home plugin symlink $target_dir -> $source_dir"
      fi
    fi
  done < <(
    python3 - "$marketplace_file" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

for plugin in data.get("plugins", []):
    name = plugin.get("name")
    if isinstance(name, str) and name.strip():
        print(name.strip())
PY
  )
}

# Keep repo-local plugin caches aligned with the marketplace so Codex surfaces
# freshly updated plugin skills immediately in runtime discovery.
# Runtime cache layout: <cache-root>/<marketplace-name>/<plugin-name>/...
sync_local_marketplace_cache() {
  local marketplace_file="$1"
  local cache_root="$2"
  local cache_state_dir=""
  local keep_file=""
  local marketplace_keep_file=""
  local marketplace_name=""
  local plugin_name=""
  local source_path=""
  local source_dir=""
  local marketplace_dir=""
  local target_plugin_dir=""
  local child_dir=""
  local tracked_marketplace_dir=""

  if [ ! -f "$marketplace_file" ]; then
    echo "[WARN] Marketplace file missing: $marketplace_file (skipping local marketplace cache sync)."
    return 0
  fi

  mkdir -p "$cache_root"
  cache_state_dir="$(mktemp -d)"
  cleanup_paths+=("$cache_state_dir")
  keep_file="$cache_state_dir/cache.keep"
  marketplace_keep_file="$cache_state_dir/marketplace.keep"
  : > "$keep_file"
  : > "$marketplace_keep_file"

  while IFS=$'\t' read -r marketplace_name plugin_name source_path; do
    [ -n "$marketplace_name" ] || continue
    [ -n "$plugin_name" ] || continue
    [ -n "$source_path" ] || continue

    case "$source_path" in
      ./*) source_dir="$repo_root/${source_path#./}" ;;
      *)
        echo "[WARN] Unsupported marketplace source.path for $plugin_name: $source_path (expected ./... path)"
        continue
        ;;
    esac

    if [ ! -d "$source_dir" ]; then
      echo "[WARN] Cache source plugin directory missing for $plugin_name: $source_dir"
      continue
    fi

    target_plugin_dir="$cache_root/$marketplace_name/$plugin_name"
    marketplace_dir="$cache_root/$marketplace_name"
    printf '%s\n' "$marketplace_dir" >> "$marketplace_keep_file"
    if [ -L "$target_plugin_dir" ]; then
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
  done < <(
    python3 - "$marketplace_file" <<'PY'
import json
import sys

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as fh:
    data = json.load(fh)

marketplace_name = data.get("name")
if not isinstance(marketplace_name, str) or not marketplace_name.strip():
    marketplace_name = "local-marketplace"
marketplace_name = marketplace_name.strip()

for plugin in data.get("plugins", []):
    if not isinstance(plugin, dict):
        continue
    name = plugin.get("name")
    if not isinstance(name, str) or not name.strip():
        continue
    source = plugin.get("source")
    if not isinstance(source, dict):
        continue
    source_type = source.get("source")
    source_path = source.get("path")
    if source_type != "local":
        continue
    if not isinstance(source_path, str) or not source_path.strip():
        continue
    print(f"{marketplace_name}\t{name.strip()}\t{source_path.strip()}")
PY
  )

  # Prune stale local-cache plugin dirs only inside marketplaces represented in
  # this marketplace file. Do not touch other cache families (for example
  # openai-curated snapshots).
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
  done < <(sort -u "$marketplace_keep_file")
}

sync_repo_cache_snapshots_to_runtime_cache() {
  local source_cache_root="$1"
  local target_cache_root="$2"

  if [ ! -d "$source_cache_root" ]; then
    return 0
  fi

  mkdir -p "$target_cache_root"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete --force "$source_cache_root/" "$target_cache_root/"
  else
    rm -rf -- "$target_cache_root"
    mkdir -p "$target_cache_root"
    cp -R "$source_cache_root"/. "$target_cache_root"/
  fi
}

materialize_plugin_cache_roots() {
  local cache_root="$1"
  local marketplace_dir=""
  local plugin_dir=""
  local candidate_dir=""
  local child_dir=""

  [ -d "$cache_root" ] || return 0

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

sync_codex_profile_homes() {
  local cache_source="$1"
  local marketplace_file="$2"
  local profile_home=""
  local profile_plugins=""

  while IFS= read -r profile_home; do
    [ -n "$profile_home" ] || continue
    [ -d "$profile_home" ] || continue

    sync_user_skills "$skills_dir" "$profile_home/skills"

    profile_plugins="$profile_home/plugins"
    mkdir -p "$profile_plugins"
    if [ -L "$profile_plugins" ]; then
      echo "[WARN] Skipping profile plugin-cache projection for symlinked path: $profile_plugins"
      continue
    fi

    sync_user_skills "$cache_source" "$profile_plugins/cache" 0 copy
    materialize_plugin_cache_roots "$profile_plugins/cache"
    if [ -f "$marketplace_file" ]; then
      cp "$marketplace_file" "$profile_plugins/marketplace.json"
      echo "[OK] Synced profile marketplace manifest: $profile_plugins/marketplace.json"
      # Keep profile-local marketplace source paths resolvable at
      # <profile-home>/plugins/<plugin-name> for local plugin installs.
      sync_home_plugin_mirrors "$marketplace_file" "$plugins_dir" "$profile_plugins"
    fi
  done < <({
    [ -d "$HOME/.codex" ] && printf '%s\n' "$HOME/.codex"
    find "$HOME" -maxdepth 1 -mindepth 1 -type d -name '.codex-*'
  } | sort -u)
}

cleanup_legacy_local_marketplace_cache() {
  local legacy_cache_root="$1"
  if [ -d "$legacy_cache_root" ] || [ -L "$legacy_cache_root" ]; then
    rm -rf -- "$legacy_cache_root"
    echo "[OK] Removed legacy visible local marketplace cache: $legacy_cache_root"
  fi
}

sync_plugin_cache_projections() {
  local projection_script="$repo_root/scripts/projection_integrity.py"

  if [ ! -f "$projection_script" ]; then
    echo "[WARN] Projection integrity script missing; skipping plugin-cache header sync."
    return 0
  fi

  python3 "$projection_script" sync --scope plugin-caches --format text
}

# Sync to Claude Code, OpenAI Codex/Agents, and Gemini loaders.
sync_repo_cache_snapshots_to_runtime_cache "$plugins_dir/cache" "$runtime_cache_root"
sync_local_marketplace_cache "$plugins_dir/marketplace.json" "$runtime_cache_root"
materialize_plugin_cache_roots "$runtime_cache_root"
cleanup_legacy_local_marketplace_cache "$plugins_dir/cache/agent-skills-local"
sync_plugin_cache_projections
sync_user_skills "$skills_dir" "$repo_root/skills" 1
sync_user_skills "$plugins_dir" "$repo_root/.agents/plugins" 1
if [[ "$sync_scope" == "workspace" ]]; then
  remove_legacy_home_skill_symlinks
  sync_user_skills "$skills_dir" "$HOME/.claude/skills"
  sync_user_skills "$skills_dir" "$HOME/.agents/skills"
  sync_user_skills "$repo_root" "$HOME/.agents/agent-skills"
  sync_user_skills "$plugins_dir" "$HOME/.agents/plugins"
  sync_codex_profile_homes "$runtime_cache_root" "$plugins_dir/marketplace.json"
  # Antigravity app requires a flat copy (no symlinks) in its own config dir
  sync_user_skills "$antigravity_skills_dir" "$HOME/.gemini/antigravity/skills" 1 copy
  sync_user_skills "$antigravity_skills_dir" "$HOME/.antigravity/skills"
  sync_skill_path_file "$antigravity_skills_dir" "$antigravity_skills_txt"
  sync_home_plugin_mirrors "$plugins_dir/marketplace.json" "$plugins_dir" "$HOME/plugins"
else
  echo "Project-local scope: skipped home runtime projections."
fi

chmod +x "$repo_root/scripts/sync_skills.sh"

echo "Selection policy identity: $SELECTION_POLICY_IDENTITY"
echo "Synced symlinks and regenerated SKILL.md."
