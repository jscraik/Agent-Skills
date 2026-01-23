#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Scaffold a recon-workbench repo from the template.

Usage:
  scripts/scaffold_repo.sh --repo <path> [--force] [--dry-run]

Options:
  --repo <path>   Target repo root.
  --force         Overwrite existing files.
  --dry-run       Print actions without writing.
USAGE
}

REPO=""
FORCE="0"
DRY_RUN="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --force) FORCE="1"; shift 1 ;;
    --dry-run) DRY_RUN="1"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" ]]; then
  echo "ERROR: --repo is required"; usage; exit 2
fi

if [[ ! -d "$REPO" ]]; then
  echo "ERROR: repo path is not a directory: $REPO"; exit 2
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$(dirname -- "$SCRIPT_DIR")" && pwd)"
TEMPLATE_DIR="${ROOT_DIR}/assets/template"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "ERROR: template not found at: $TEMPLATE_DIR"; exit 2
fi

copy_any() {
  local src="$1"
  local dest="$2"
  local dest_dir
  dest_dir="$(dirname "$dest")"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY-RUN: mkdir -p $dest_dir"
  else
    mkdir -p "$dest_dir"
  fi

  if [[ -e "$dest" && "$FORCE" != "1" ]]; then
    echo "SKIP: $dest exists (use --force)"
    return
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY-RUN: cp $src $dest"
  else
    cp "$src" "$dest"
  fi
}

export -f copy_any

cd "$TEMPLATE_DIR"
find . -type f | while read -r f; do
  copy_any "$TEMPLATE_DIR/$f" "$REPO/$f"
done

if [[ "$DRY_RUN" != "1" ]]; then
  if [[ -d "$REPO/scripts" ]]; then
    find "$REPO/scripts" -type f -name '*.sh' -exec chmod +x {} \;
  fi
fi

echo "Done."
