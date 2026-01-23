# Dependencies (Baseline -> Advanced -> Worst-case)

This is the dependency inventory required to cover the "worst-case" tier across:
browser apps (React/etc) and OSS.

## Baseline (recommended for all workflows)
- Codex CLI (planning + summarization; schema outputs)
- Git
- Python 3
- Node.js + npm (for Playwright/web probes)
## Web/React + browser apps
Baseline:
- Chrome DevTools HAR export

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
