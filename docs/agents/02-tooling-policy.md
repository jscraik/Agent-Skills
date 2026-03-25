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
- Default to `zsh -lc` for shell tooling; switch to `bash` only when a script relies on bash internals.

## Command preflight
- Run `bash scripts/codex-preflight.sh --stack auto --mode required` before multi-step, destructive, or path-sensitive work.
- The verified optional overrides are `--repo-fragment`, `--bins`, and `--paths`.
- Confirm `pwd` is `/Users/jamiecraik/dev/Agent-Skills` before edits.
- Verify required binaries with `which` before running installs.
- Confirm target paths with `fd` before destructive operations.
- Do not source `scripts/codex-preflight.sh` or call `preflight_repo`; the current script is a bash CLI, not a shell function library.

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
- `bash scripts/codex-preflight.sh --stack auto --mode required`
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/scripts/verify-work.sh`
