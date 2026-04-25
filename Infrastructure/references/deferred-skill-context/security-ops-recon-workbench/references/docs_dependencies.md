# Dependencies (Baseline -> Advanced -> Worst-case)

Summary from `docs/reference/DEPENDENCIES.md`.

## Baseline (recommended)
- Codex CLI, Git, Python 3, Node.js + npm
- Xcode Command Line Tools
- Xcode + iOS Simulator

## macOS apps
- Baseline: codesign, otool, nm, strings
- Optional: Ghidra, class-dump, swift-demangle, Hopper/IDA
- Worst-case: Instruments + unified logging (no circumvention)

## iOS Simulator
- Baseline: xcrun simctl, Safari Web Inspector
- Optional: class-dump, swift-demangle, LLDB (debug builds only)
- Worst-case: Instruments + HTTPS proxy tooling (mitmproxy/Burp/Charles)

## Web/React apps
- Baseline: Chrome DevTools HAR export, Safari Web Inspector
- Worst-case: Playwright + trace viewer, HTTPS proxy tooling

## OSS repos
- Baseline: language toolchains + package managers
- Worst-case: Semgrep, CodeQL CLI

## Verification
- Run doctor before probes to record tool versions.
- Schema validation requires `jsonschema`.
