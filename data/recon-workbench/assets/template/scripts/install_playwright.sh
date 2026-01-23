#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Install Playwright and required browsers.

Usage:
  scripts/install_playwright.sh [--package-manager npm|pnpm|yarn] [--no-browsers]
USAGE
}

PM="npm"
NO_BROWSERS="0"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --package-manager) PM="$2"; shift 2 ;;
    --no-browsers) NO_BROWSERS="1"; shift 1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
done

case "$PM" in
  npm) npm install -D playwright ;;
  pnpm) pnpm add -D playwright ;;
  yarn) yarn add -D playwright ;;
  *) echo "Unsupported package manager: $PM"; exit 2 ;;
 esac

if [[ "$NO_BROWSERS" != "1" ]]; then
  npx playwright install
fi

echo "Playwright install complete."
