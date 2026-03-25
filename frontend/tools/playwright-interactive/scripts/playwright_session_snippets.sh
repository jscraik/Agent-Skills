#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/playwright_session_snippets.sh bootstrap
  scripts/playwright_session_snippets.sh web-start --url <url>
  scripts/playwright_session_snippets.sh electron-start --entry <path>
  scripts/playwright_session_snippets.sh reload-plan --surface web|electron --change renderer|process
USAGE
}

cmd="${1:-}"
if [[ -z "$cmd" ]]; then
  usage
  exit 2
fi
shift || true

case "$cmd" in
  bootstrap)
    cat <<'JS'
var chromium;
var electronLauncher;
var browser;
var context;
var page;
var mobileContext;
var mobilePage;
var electronApp;
var appWindow;

({ chromium, _electron: electronLauncher } = await import("playwright"));
console.log("Playwright loaded");
JS
    ;;

  web-start)
    url=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --url) url="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$url" ]]; then
      echo "missing --url" >&2
      exit 2
    fi
    cat <<JS
var TARGET_URL = "${url}";

browser ??= await chromium.launch({ headless: false });
context ??= await browser.newContext({ viewport: { width: 1600, height: 900 } });
page ??= await context.newPage();
await page.goto(TARGET_URL, { waitUntil: "domcontentloaded" });
JS
    ;;

  electron-start)
    entry=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --entry) entry="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$entry" ]]; then
      echo "missing --entry" >&2
      exit 2
    fi
    cat <<JS
var ELECTRON_ENTRY = "${entry}";

electronApp ??= await electronLauncher.launch({ args: [ELECTRON_ENTRY] });
appWindow ??= await electronApp.firstWindow();
console.log(await appWindow.title());
JS
    ;;

  reload-plan)
    surface=""
    change=""
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --surface) surface="${2:-}"; shift 2 ;;
        --change) change="${2:-}"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; usage; exit 2 ;;
      esac
    done
    if [[ -z "$surface" || -z "$change" ]]; then
      echo "missing --surface or --change" >&2
      exit 2
    fi
    if [[ "$surface" == "web" && "$change" == "renderer" ]]; then
      echo "reload current page/context"
      exit 0
    fi
    if [[ "$surface" == "electron" && "$change" == "renderer" ]]; then
      echo "reload appWindow"
      exit 0
    fi
    if [[ "$surface" == "electron" && "$change" == "process" ]]; then
      echo "close and relaunch electronApp"
      exit 0
    fi
    echo "unknown combination: surface=$surface change=$change" >&2
    exit 2
    ;;

  *)
    echo "unknown command: $cmd" >&2
    usage
    exit 2
    ;;
esac
