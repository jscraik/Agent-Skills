#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install Playwright and required browsers.

Usage:
  Infrastructure/scripts/install_playwright.sh [--package-manager npm|pnpm|yarn] [--no-browsers]
USAGE
}

PM="npm"
NO_BROWSERS="0"

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 127
  fi
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --package-manager)
      if [[ $# -lt 2 || -z "${2:-}" || "${2:-}" == --* ]]; then
        echo "Missing value for --package-manager" >&2
        usage
        exit 2
      fi
      PM="$2"
      shift 2
      ;;
    --no-browsers) NO_BROWSERS="1"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

case "$PM" in
  npm)
    require_cmd npm
    npm install -D playwright
    ;;
  pnpm)
    require_cmd pnpm
    pnpm add -D playwright
    ;;
  yarn)
    require_cmd yarn
    yarn add -D playwright
    ;;
  *) echo "Unsupported package manager: $PM"; exit 2 ;;
 esac

if [[ "$NO_BROWSERS" != "1" ]]; then
  case "$PM" in
    npm)
      require_cmd npx
      npx playwright install
      ;;
    pnpm)
      pnpm exec playwright install
      ;;
    yarn)
      yarn playwright install
      ;;
  esac
fi

echo "Playwright install complete."
