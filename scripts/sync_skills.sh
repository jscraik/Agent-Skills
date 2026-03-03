#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/sync_skills.sh

Regenerates skill symlinks and SKILL.md index for this repository.
USAGE
}

if [[ $# -gt 0 ]]; then
  case "${1:-}" in
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
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skills_dir="$repo_root/skills"
system_skills_dir="$repo_root/skills-system"
antigravity_skills_dir="$repo_root/skills-antigravity"

mkdir -p "$skills_dir"
mkdir -p "$antigravity_skills_dir"

cleanup_paths=()
cleanup_on_exit() {
  local path=""
  for path in "${cleanup_paths[@]:-}"; do
    if [ -n "$path" ] && [ -d "$path" ]; then
      rm -rf -- "$path"
    fi
  done
}
trap cleanup_on_exit EXIT

# Ensure system skills are not in the flat symlink view (prevents duplicates).
if [ -d "$skills_dir/.system" ]; then
  mkdir -p "$system_skills_dir"
  # Safety: if repo already has a skills-system marker, do NOT overwrite it from
  # whatever happens to be in skills/.system (which can be partial/ephemeral).
  # Just remove skills/.system so system skills don't appear in the flat view.
  if [ -f "$system_skills_dir/.codex-system-skills.marker" ]; then
    rm -rf "$skills_dir/.system"
  else
  # Use rsync to handle existing directories, then remove source
  if command -v rsync >/dev/null 2>&1; then
    rsync -a "$skills_dir/.system/" "$system_skills_dir/"
    rm -rf "$skills_dir/.system"
  else
    # Fallback: remove target first, then move
    find "$system_skills_dir" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
    mv "$skills_dir"/.[!.]* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/..?* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/* "$system_skills_dir"/ 2>/dev/null || true
    rmdir "$skills_dir/.system" 2>/dev/null || true
  fi
  fi
fi

# Remove stale symlinks only (keep any real files that might be intentional).
find "$skills_dir" -maxdepth 1 -type l -exec rm -f {} +

# Recreate symlinks for all discovered SKILL.md directories (with exclusions).
skill_files_cmd() {
  find . \
    -path "*/_archive" -prune -o \
    -path "./skills" -prune -o \
    -path "./skills-system" -prune -o \
    -path "./.git" -prune -o \
    -path "./.agent" -prune -o \
    -path "./.agents" -prune -o \
    -path "./.claude" -prune -o \
    -path "./.cursor" -prune -o \
    -path "./.kiro" -prune -o \
    -path "./.narrative" -prune -o \
    -path "./.skillsctl" -prune -o \
    -path "./.tmp" -prune -o \
    -path "./.system" -prune -o \
    -path "./node_modules" -prune -o \
    -path "./artifacts" -prune -o \
    -path "./data/recon-workbench/assets/template" -prune -o \
    -path "*/assets/*" -prune -o \
    -path "*/rules/*" -prune -o \
    -path "*/scripts/*" -prune -o \
    -name "SKILL.md" -print
}

# Include supplemental skills that intentionally live outside canonical
# category folders.
extra_skill_files_cmd() {
  if [ -d "./.agents/skills" ]; then
    while IFS= read -r extra_skill; do
      if git ls-files --error-unmatch "$extra_skill" >/dev/null 2>&1; then
        echo "$extra_skill"
      fi
    done < <(find "./.agents/skills" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print)
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
    done < <(find "./skills" -mindepth 2 -maxdepth 3 -name "SKILL.md" -print)
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
while IFS= read -r skill_path; do
  # Skip the root index.
  if [ "$skill_path" = "./SKILL.md" ]; then
    continue
  fi
  skill_dir="$(dirname "$skill_path")"
  skill_name="$(basename "$skill_dir")"
  skill_dir_abs="$repo_root/$skill_dir"
  if [ -e "$skills_dir/$skill_name" ]; then
    existing_dir="$(cd "$skills_dir/$skill_name" 2>/dev/null && pwd || true)"
    discovered_dir="$(cd "$skill_dir_abs" 2>/dev/null && pwd || true)"
    # If the discovered skill already lives directly in the flat skills view
    # (for example ./skills/sentry), skip without duplicate noise.
    if [ -n "$existing_dir" ] && [ "$existing_dir" = "$discovered_dir" ]; then
      continue
    fi
    echo "Duplicate skill name: $skill_name (skip $skill_dir_abs)"
    continue
  fi
  ln -s "$skill_dir_abs" "$skills_dir/$skill_name"
done < <(all_skill_files_cmd)

# Build a strict Antigravity-compatible projection:
# - flat first-level skill folders only
# - each folder must contain SKILL.md
# This avoids loader confusion from metadata folders like .system/ or helper repos.
find "$antigravity_skills_dir" -mindepth 1 -maxdepth 1 -type l -exec rm -f {} +
find "$antigravity_skills_dir" -mindepth 1 -maxdepth 1 -type f -exec rm -f {} +

for skill_link in "$skills_dir"/*; do
  if [ ! -L "$skill_link" ]; then
    continue
  fi
  if [ ! -f "$skill_link/SKILL.md" ]; then
    continue
  fi

  skill_name="$(basename "$skill_link")"
  target_dir="$(cd "$skill_link" && pwd)"
  ln -s "$target_dir" "$antigravity_skills_dir/$skill_name"
done

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

Canonical skills live in categorized folders below. Each tool loads skills via the flat symlink directory at `~/dev/agent-skills/skills`.

HEADER

  # Collect skills into temp files by category
  while IFS= read -r skill_path; do
    # Skip the root index
    if [ "$skill_path" = "./SKILL.md" ]; then
      continue
    fi

    skill_dir="$(dirname "$skill_path")"
    skill_name="$(basename "$skill_dir")"
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
    category="$(echo "$cat_file" | tr '_' '/' | sed 's|/| — |g; s|-| |g; s|_| |g')"
    # Capitalize each word
    category_display=""
    for word in $category; do
      first="$(echo "$word" | cut -c1 | tr '[:lower:]' '[:upper:]')"
      rest="$(echo "$word" | cut -c2-)"
      category_display="$category_display$first$rest "
    done

    echo "## $(echo "$category_display" | sed 's/ *$//')" >> "$index_file"
    echo "" >> "$index_file"
    sort "$temp_dir/$cat_file" >> "$index_file"
    echo "" >> "$index_file"
  done < <(cd "$temp_dir" && find . -mindepth 1 -maxdepth 1 -type f -print | sed 's|^\./||' | sort)
}

generate_skill_index "$repo_root/SKILL.md"

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

# Sync to user-level tool directories (Claude Code + OpenAI Codex/Agents)
sync_user_skills() {
  local source_dir="$1"
  local target_dir="$2"
  mkdir -p "$(dirname "$target_dir")"
  if [ -L "$target_dir" ]; then
    # Update existing symlink
    ln -sfn "$source_dir" "$target_dir"
    echo "[OK] Updated symlink: $target_dir -> $source_dir"
  elif [ -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
    # Exists but is not a symlink - warn and skip
    echo "[WARN] $target_dir exists but is not a symlink (skipping)"
    echo "       Remove it manually to enable automatic sync: rm -rf $target_dir"
  else
    # Create new symlink
    ln -s "$source_dir" "$target_dir"
    echo "[OK] Created symlink: $target_dir -> $source_dir"
  fi
}

# Sync to Claude Code, OpenAI Codex/Agents, and Gemini loaders.
sync_user_skills "$skills_dir" "$HOME/.claude/skills"
sync_user_skills "$skills_dir" "$HOME/.agents/skills"
sync_user_skills "$skills_dir" "$HOME/.codex/skills"
sync_user_skills "$antigravity_skills_dir" "$HOME/.gemini/antigravity/skills"
sync_user_skills "$antigravity_skills_dir" "$HOME/.gemini/skills"
sync_user_skills "$antigravity_skills_dir" "$HOME/.antigravity/skills"

chmod +x "$repo_root/scripts/sync_skills.sh"

echo "Synced symlinks and regenerated SKILL.md."
