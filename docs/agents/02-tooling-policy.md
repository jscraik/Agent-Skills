# Tooling and Command Policy

## Table of Contents
- [Tools](#tools)
- [Verified command style](#verified-command-style)
- [Useful checks](#useful-checks)

## Tools
- Use `rg`, `fd`, `jq` from repo workflow.
- Read `/Users/jamiecraik/.codex/instructions/tooling.md` for the current authoritative tool stack.
- Use `zsh -lc` in shell tooling.

## Verified command style
- Keep command snippets backed by repo files before documenting them.
- Prefer one-shot, reproducible commands.

## Useful checks
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `/Users/jamiecraik/.codex/scripts/verify-work.sh`
