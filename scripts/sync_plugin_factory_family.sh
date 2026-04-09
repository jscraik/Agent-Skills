#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

sync_tree() {
  local src="$1"
  local dest="$2"

  if [[ ! -d "$src" ]]; then
    echo "ERROR: source path is not a directory: $src" >&2
    return 1
  fi

  if command -v rsync >/dev/null 2>&1; then
    mkdir -p "$dest"
    rsync -a --delete --exclude "__pycache__/" --exclude ".DS_Store" "$src"/ "$dest"/
  else
    rm -rf "$dest"
    mkdir -p "$dest"
    cp -a "$src"/. "$dest"/
    find "$dest" -type d -name "__pycache__" -prune -exec rm -rf {} +
    find "$dest" -type f -name ".DS_Store" -delete
  fi

  echo "synced $src -> $dest"
}

sync_tree "utilities/plugin-builder" "plugins/plugin-factory/skills/plugin-builder"
sync_tree "skills-system/plugin-creator" "plugins/plugin-factory/skills/plugin-creator"
sync_tree "skills-system/plugin-installer" "plugins/plugin-factory/skills/plugin-installer"

echo "plugin-factory family sync complete"
