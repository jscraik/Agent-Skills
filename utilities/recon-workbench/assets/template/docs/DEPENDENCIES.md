# Dependencies (Baseline -> Advanced -> Worst-case)

This is the dependency inventory required to cover the "worst-case" tier across:
macOS apps, iOS Simulator, browser apps (React/etc), and OSS.

## Baseline (recommended for all workflows)
- Codex CLI (planning + summarization; schema outputs)
- Git
- Python 3
- Node.js + npm (for Playwright/web probes)
- Xcode Command Line Tools (codesign, otool, etc.)
- Xcode + iOS Simulator

## macOS apps
Baseline:
- codesign, otool, nm, strings (Apple tooling)
- Optional: Ghidra (static disassembly/decomp)

Worst-case (observation-first; no circumvention):
- Instruments (Network/File Activity templates)
- Unified logging capture (log stream / Console)

## iOS Simulator
Baseline:
- xcrun simctl (screenshot, recordVideo)
- Safari Web Inspector / Develop menu

Worst-case:
- Instruments Network template (HTTP analysis)
- HTTPS proxy tooling (mitmproxy / Burp / Charles) + certificate install

## Web/React + browser apps
Baseline:
- Chrome DevTools HAR export
- Safari Web Inspector (especially for WKWebView and Simulator inspection)

Worst-case:
- Playwright + trace viewer
- Playwright requires `npm install -D playwright` and `npx playwright install` to fetch browsers.
- Optional helper: `scripts/install_playwright.sh` in the template.
- HTTPS proxy tooling (mitmproxy / Burp) when appropriate

## OSS repos
Baseline:
- language toolchains + package managers
- optional: ripgrep, graphviz

Worst-case:
- Semgrep (SAST)
- CodeQL CLI (deep static analysis)

## Verification
- Use a "doctor" check to confirm presence and record versions before running probes.
- For schema validation, install the Python package `jsonschema`.
