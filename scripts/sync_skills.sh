#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

skills_dir="$repo_root/skills"
system_skills_dir="$repo_root/skills-system"

mkdir -p "$skills_dir"

# Ensure system skills are not in the flat symlink view (prevents duplicates).
if [ -d "$skills_dir/.system" ]; then
  mkdir -p "$system_skills_dir"
  # Use rsync to handle existing directories, then remove source
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$skills_dir/.system/" "$system_skills_dir/"
    rm -rf "$skills_dir/.system"
  elif command -v zsh >/dev/null 2>&1; then
    zsh -c "setopt globdots; rm -rf \"$system_skills_dir\"/*; mv \"$skills_dir/.system\"/* \"$system_skills_dir\"/; rmdir \"$skills_dir/.system\""
  else
    # Fallback: remove target first, then move
    rm -rf "$system_skills_dir"/*
    mv "$skills_dir"/.[!.]* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/..?* "$system_skills_dir"/ 2>/dev/null || true
    mv "$skills_dir"/* "$system_skills_dir"/ 2>/dev/null || true
    rmdir "$skills_dir/.system" 2>/dev/null || true
  fi
fi

# Remove stale symlinks only (keep any real files that might be intentional).
find "$skills_dir" -maxdepth 1 -type l -exec rm -f {} +

# Recreate symlinks for all discovered SKILL.md directories (with exclusions).
skill_files_cmd() {
  find . \
    -path "./skills" -prune -o \
    -path "./skills-system" -prune -o \
    -path "./.git" -prune -o \
    -path "./.tmp" -prune -o \
    -path "./.system" -prune -o \
    -path "./node_modules" -prune -o \
    -path "./data/recon-workbench/assets/template" -prune -o \
    -path "*/assets/*" -prune -o \
    -path "*/rules/*" -prune -o \
    -path "*/scripts/*" -prune -o \
    -name "SKILL.md" -print
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
    echo "Duplicate skill name: $skill_name (skip $skill_dir_abs)"
    continue
  fi
  ln -s "$skill_dir_abs" "$skills_dir/$skill_name"
done < <(skill_files_cmd | sort)

# Regenerate root SKILL.md index dynamically from skill frontmatter.
generate_skill_index() {
  local index_file="$1"
  local temp_dir="$(mktemp -d)"
  trap "rm -rf $temp_dir" EXIT

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
    category="$(dirname "$skill_dir" | sed 's|^\./||')"
    safe_category="$(echo "$category" | tr '/' '_')"

    # Extract description from YAML frontmatter
    description=""
    if [ -f "$skill_path" ]; then
      description=$(head -20 "$skill_path" | awk '/^description:/{found=1; sub(/^description: *"?/, ""); sub(/"?$/, ""); print; exit}')
    fi

    # Store description (or placeholder)
    if [ -z "$description" ]; then
      description="Skill description pending."
    fi

    # Append to category file
    echo "- \`$skill_name\` — $description" >> "$temp_dir/$safe_category"
  done < <(skill_files_cmd | sort)

  # Output categories and skills in deterministic order
  for cat_file in $(ls "$temp_dir" | sort); do
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
  done
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

# Remove old symlinks from unsupported tools
remove_legacy_symlink "$HOME/.copilot/skills"
remove_legacy_symlink "$HOME/.config/agents/skills"
remove_legacy_symlink "$HOME/.cursor/skills"

# Sync to user-level tool directories (Claude Code + OpenAI Codex/Agents)
sync_user_skills() {
  local target_dir="$1"
  mkdir -p "$(dirname "$target_dir")"
  if [ -L "$target_dir" ]; then
    # Update existing symlink
    ln -sfn "$skills_dir" "$target_dir"
    echo "[OK] Updated symlink: $target_dir -> $skills_dir"
  elif [ -e "$target_dir" ] && [ ! -L "$target_dir" ]; then
    # Exists but is not a symlink - warn and skip
    echo "[WARN] $target_dir exists but is not a symlink (skipping)"
    echo "       Remove it manually to enable automatic sync: rm -rf $target_dir"
  else
    # Create new symlink
    ln -s "$skills_dir" "$target_dir"
    echo "[OK] Created symlink: $target_dir -> $skills_dir"
  fi
}

# Sync to Claude Code and OpenAI Agents/Codex
sync_user_skills "$HOME/.claude/skills"
sync_user_skills "$HOME/.agents/skills"

chmod +x "$repo_root/scripts/sync_skills.sh"

echo "Synced symlinks and regenerated SKILL.md."
