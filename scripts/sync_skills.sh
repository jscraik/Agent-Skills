#!/usr/bin/env bash
set -euo pipefail

timeout_seconds="${SYNC_SKILLS_TIMEOUT_SECONDS:-300}"
lock_dir="${TMPDIR:-/tmp}/agent-skills-sync.lock"
lock_pid_file="$lock_dir/pid"
lock_owned=0
watchdog_pid=""

usage() {
  cat <<'USAGE'
Usage:
  scripts/sync_skills.sh [--timeout-seconds <int>]

Regenerates skill/plugin symlinks and SKILL.md index for this repository.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "${1:-}" in
    --timeout-seconds)
      timeout_seconds="${2:-}"
      shift 2
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

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

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
hidden_flat_skills=(
  "coderabbit"
  "linear"
  "plugin-builder"
  "plugin-creator"
  "plugin-installer"
  "skillgrade-graders"
  "skillgrade-setup"
)
is_hidden_flat_skill_name() {
  local skill_name="$1"
  case " ${hidden_flat_skills[*]} " in
    *" $skill_name "*) return 0 ;;
    *) return 1 ;;
  esac
}
for hidden_skill in "${hidden_flat_skills[@]}"; do
  if [ -e "$skills_dir/$hidden_skill" ]; then
    if rm -rf -- "$skills_dir/$hidden_skill"; then
      echo "Removed hidden flat skill: $hidden_skill"
    else
      echo "[WARN] Could not remove hidden skill $hidden_skill at $skills_dir (continuing anyway)."
    fi
  fi
done

# Recreate symlinks for all discovered SKILL.md directories (with exclusions).
skill_files_cmd() {
  # Allowlist of trusted category directories — only these are scanned.
  # This prevents untrusted paths (artifacts/, logs/, reports/, templates/, etc.)
  # from ever contributing a SKILL.md into the canonical skills/ view.
  local skill_roots=(
    "./auth"
    "./backend"
    "./design"
    "./frontend"
    "./github"
    "./interview"
    "./ops"
    "./personas"
    "./product"
    "./skills-system"
    "./utilities"
  )

  local root=""
  for root in "${skill_roots[@]}"; do
    [ -d "$root" ] || continue
    find -L "$root" \
      -path "*/_archive/*" -prune -o \
      -path "*/assets/*" -prune -o \
      -path "*/fixtures/*" -prune -o \
      -path "*/examples/*" -prune -o \
      -path "*/templates/*" -prune -o \
      -path "*/references/*" -prune -o \
      -path "*/agents/*" -prune -o \
      -path "*/rules/*" -prune -o \
      -path "*/scripts/*" -prune -o \
      -name "SKILL.md" -print
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
  if is_plugin_owned_skill_path "$skill_path"; then
    echo "Skipping plugin-owned skill from flat runtime list: $skill_name"
    continue
  fi
  skill_dir_abs="$repo_root/$skill_dir"
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
      if ! rm -rf -- "$skills_dir/$skill_name"; then
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

# Re-expose preserved system skills through the hidden `.system` path without
# bringing them back into the flat runtime skill list.
if [ -e "$skills_dir/.system" ] && [ ! -L "$skills_dir/.system" ]; then
  echo "[WARN] $skills_dir/.system exists as a non-symlink; leaving it in place."
elif [ ! -e "$skills_dir/.system" ]; then
  ln -s "../../skills-system" "$skills_dir/.system"
fi

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

# Regenerate root SKILL.md index dynamically from skill frontmatter.
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
      continue
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
      continue
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
  echo "- \`invalid\`: $invalid_count" >> "$index_file"
  echo "- \`total_tagged\`: $tagged_count" >> "$index_file"
  echo "" >> "$index_file"

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

# Remove old/legacy symlinks from unsupported locations
remove_legacy_symlink "$HOME/.copilot/skills"
remove_legacy_symlink "$HOME/.config/agents/skills"
remove_legacy_symlink "$HOME/.cursor/skills"
remove_legacy_symlink "$HOME/.gemini/skills"

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
      rsync -a "$source_dir/" "$target_dir/" --delete
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

# Sync to Claude Code, OpenAI Codex/Agents, and Gemini loaders.
sync_user_skills "$skills_dir" "$repo_root/skills" 1
sync_user_skills "$plugins_dir" "$repo_root/.agents/plugins" 1
sync_user_skills "$skills_dir" "$HOME/.claude/skills"
sync_user_skills "$skills_dir" "$HOME/.agents/skills"
sync_user_skills "$repo_root" "$HOME/.agents/agent-skills"
sync_user_skills "$plugins_dir" "$HOME/.agents/plugins"
sync_user_skills "$skills_dir" "$HOME/.codex/skills"
sync_user_skills "$plugins_dir" "$HOME/.codex/plugins" 1
# Antigravity app requires a flat copy (no symlinks) in its own config dir
sync_user_skills "$antigravity_skills_dir" "$HOME/.gemini/antigravity/skills" 1 copy
sync_user_skills "$antigravity_skills_dir" "$HOME/.antigravity/skills"
sync_skill_path_file "$antigravity_skills_dir" "$antigravity_skills_txt"
sync_home_plugin_mirrors "$plugins_dir/marketplace.json" "$plugins_dir" "$HOME/plugins"

chmod +x "$repo_root/scripts/sync_skills.sh"

echo "Synced symlinks and regenerated SKILL.md."
