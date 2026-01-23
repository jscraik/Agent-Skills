#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install codex-ui-kit files into a repo.

Usage:
  scripts/install_kit.sh [--repo <path>] [--install-prompts] [--prompts-dir <path>] [--force] [--dry-run] [--verify]

Options:
  --repo <path>         Target repo root. Defaults to current working directory.
  --install-prompts     Also install prompts to the prompts directory.
  --prompts-dir <path>  Prompts directory. Default: ~/.codex/prompts
  --force               Overwrite existing files.
  --dry-run             Print actions without modifying files.
  --verify              Validate expected files without modifying the repo.
  -h, --help            Show help.
EOF
}

say() { printf '%s\n' "$*"; }

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="${SCRIPT_DIR}/../assets/codex-ui-kit"

REPO=""
INSTALL_PROMPTS="0"
PROMPTS_DIR="${HOME}/.codex/prompts"
FORCE="0"
DRY_RUN="0"
VERIFY="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="${2:-}"; shift 2 ;;
    --install-prompts) INSTALL_PROMPTS="1"; shift 1 ;;
    --prompts-dir) PROMPTS_DIR="${2:-}"; shift 2 ;;
    --force) FORCE="1"; shift 1 ;;
    --dry-run) DRY_RUN="1"; shift 1 ;;
    --verify) VERIFY="1"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) say "Unknown option: $1"; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" ]]; then
  REPO="$(pwd)"
fi

if [[ ! -d "$REPO" ]]; then
  say "ERROR: repo path is not a directory: $REPO"
  exit 2
fi

if [[ ! -d "$ASSETS_DIR" ]]; then
  say "ERROR: assets not found at: $ASSETS_DIR"
  exit 2
fi

if [[ "$INSTALL_PROMPTS" != "1" && "$PROMPTS_DIR" != "${HOME}/.codex/prompts" ]]; then
  say "NOTE: --prompts-dir is ignored unless --install-prompts is set."
fi

verify_file() {
  local label="$1"
  local path="$2"
  if [[ -e "$path" ]]; then
    say "OK: $label -> $path"
  else
    say "MISSING: $label -> $path"
  fi
}

copy_file() {
  local src="$1"
  local dest="$2"
  local dest_dir
  dest_dir="$(dirname "$dest")"

  if [[ "$DRY_RUN" == "1" ]]; then
    say "DRY-RUN: mkdir -p $dest_dir"
  else
    mkdir -p "$dest_dir"
  fi

  if [[ -e "$dest" && "$FORCE" != "1" ]]; then
    say "SKIP: $dest already exists (use --force to overwrite)"
    return
  fi

  if [[ "$DRY_RUN" == "1" ]]; then
    say "DRY-RUN: cp $src $dest"
  else
    cp "$src" "$dest"
  fi
}

say "Installing codex-ui-kit into: $REPO"

if [[ "$VERIFY" == "1" ]]; then
  say "Verify only (no changes)."
  verify_file "AGENTS.md" "$REPO/AGENTS.md"
  verify_file "schema" "$REPO/codex/ui_report.schema.json"
  verify_file "ui-codex" "$REPO/bin/ui-codex"
  verify_file "ios-web" "$REPO/bin/ios-web"
  if [[ "$INSTALL_PROMPTS" == "1" ]]; then
    verify_file "ios_ui_fix" "$PROMPTS_DIR/ios_ui_fix.md"
    verify_file "ui_regression_check" "$PROMPTS_DIR/ui_regression_check.md"
    verify_file "draftpr" "$PROMPTS_DIR/draftpr.md"
  else
    say "Prompts not checked (pass --install-prompts to verify prompts)."
  fi
  exit 0
fi

copy_file "$ASSETS_DIR/AGENTS.md" "$REPO/AGENTS.md"
copy_file "$ASSETS_DIR/codex/ui_report.schema.json" "$REPO/codex/ui_report.schema.json"
copy_file "$ASSETS_DIR/bin/ui-codex" "$REPO/bin/ui-codex"
copy_file "$ASSETS_DIR/bin/ios-web" "$REPO/bin/ios-web"
copy_file "$ASSETS_DIR/bin/ios-web-storybook" "$REPO/bin/ios-web-storybook"
copy_file "$ASSETS_DIR/bin/ios-web-openai" "$REPO/bin/ios-web-openai"

if [[ "$DRY_RUN" == "1" ]]; then
  say "DRY-RUN: chmod +x $REPO/bin/ui-codex"
  say "DRY-RUN: chmod +x $REPO/bin/ios-web"
  say "DRY-RUN: chmod +x $REPO/bin/ios-web-storybook"
  say "DRY-RUN: chmod +x $REPO/bin/ios-web-openai"
else
  chmod +x "$REPO/bin/ui-codex"
  chmod +x "$REPO/bin/ios-web"
  chmod +x "$REPO/bin/ios-web-storybook"
  chmod +x "$REPO/bin/ios-web-openai"
fi

if [[ "$INSTALL_PROMPTS" == "1" ]]; then
  say "Installing prompts into: $PROMPTS_DIR"
  copy_file "$ASSETS_DIR/prompts/ios_ui_fix.md" "$PROMPTS_DIR/ios_ui_fix.md"
  copy_file "$ASSETS_DIR/prompts/ui_regression_check.md" "$PROMPTS_DIR/ui_regression_check.md"
  copy_file "$ASSETS_DIR/prompts/draftpr.md" "$PROMPTS_DIR/draftpr.md"
else
  say "Prompts not installed (pass --install-prompts to copy to $PROMPTS_DIR)"
fi

say "Done."
