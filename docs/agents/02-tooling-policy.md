# Tooling and Command Policy

## Table of Contents
- [Tools](#tools)
- [Command preflight](#command-preflight)
- [Verified command style](#verified-command-style)
- [Package command map](#package-command-map)
- [Useful checks](#useful-checks)

## Tools
- Use `rg`, `fd`, `jq` from repo workflow.
- Read `~/.codex/instructions/tooling.md` for the current authoritative tool stack.
- Use `zsh -lc` in shell tooling.

## Command preflight
- Confirm `pwd` is `/Users/jamiecraik/dev/agent-skills` before edits.
- Verify required binaries with `which` before running installs.
- Confirm target paths with `fd` before destructive operations.
- Use `bash -lc` only when bash-specific internals are required.

## Verified command style
- Keep command snippets backed by repo files before documenting them.
- Prefer one-shot, reproducible commands.

## Package command map
- Repository root is configuration-oriented and has no package manager install step.
- Verified npm package roots from lockfiles:
  - `frontend/stitch-react-components/`
  - `product/content/video-transcript-downloader/`
- Use per-package npm commands at those roots:
  - `npm --prefix <path> install`
  - `npm --prefix <path> run <script>`
  - `npm --prefix <path> exec <bin>`

## Useful checks
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/scripts/verify-work.sh`
