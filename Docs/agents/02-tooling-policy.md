# Tooling and Command Policy

## Table of Contents
- [Tools](#tools)
- [Command preflight](#command-preflight)
- [Verified command style](#verified-command-style)
- [Package command map](#package-command-map)
- [Useful checks](#useful-checks)
- [Skill line-budget policy](#skill-line-budget-policy)

## Tools
- Use `rg`, `fd`, `jq` from repo workflow.
- Read `~/.codex/instructions/tooling.md` for the current authoritative tool stack.
- Default to `bash -lc` for shell tooling in this repository. Use `zsh -lc` only when you must validate zsh-specific behavior.

## Command preflight
- Run `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required` before multi-step, destructive, or path-sensitive work.
- The verified optional overrides are `--repo-fragment`, `--bins`, and `--paths`.
- Confirm `pwd` is `/Users/jamiecraik/dev/Agent-Skills` before edits.
- Verify required binaries with `which` before running installs.
- Confirm target paths with `fd` before destructive operations.
- Do not source `Infrastructure/scripts/codex-preflight/codex-preflight.sh` or call `preflight_repo`; the current script is a bash CLI, not a shell function library.

## Verified command style
- Keep command snippets backed by repo files before documenting them.
- Prefer one-shot, reproducible commands.

## Package command map
- Repository root is configuration-oriented and has no package manager install step.
- Verified npm package roots from lockfiles:
  - `Skills/content-publishing/video-transcript-downloader/`
  - `Skills/frontend-ui/ui-ux-creative-coding/`
- Use per-package npm commands at those roots:
  - `npm --prefix <path> install`
  - `npm --prefix <path> run <script>`
  - `npm --prefix <path> exec <bin>`

## Useful checks
- `bash Infrastructure/scripts/codex-preflight/codex-preflight.sh --stack auto --mode required`
- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agents/PLANS.md` (external dependency)
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh` (repo-local wrapper preferred over `~/.codex` version)

## Skill line-budget policy

When a `SKILL.md` exceeds the 360-line split budget (`PD_SKILLMD_TOO_LONG`), **never delete content** to bring it under the limit. Move the bulk section(s) to `Infrastructure/references/<topic>.md` under the skill directory and replace with a one-line link. Removing blank lines or navigation-only TOC entries (no prose content) is acceptable as a last resort. Owner rule: context is never lost, only relocated.
