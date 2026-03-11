# Validation and Checks

## Table of Contents
- [Repository checks](#repository-checks)
- [Config-sensitive checks](#config-sensitive-checks)
- [AI workflow checks](#ai-workflow-checks)
- [Failure handling](#failure-handling)

## Repository checks
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `just validate` (or `bash scripts/validate_all.sh`)
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/scripts/verify-work.sh`

## Config-sensitive checks
- For edits to `package.json`, CI workflows, `settings.json`, or similar config files:
  - Run applicable lint/test/typecheck gates before commit.
  - Confirm pass status explicitly in handoff notes.
- For implementation work, run separate implementation and verification workflows.
- Require `codex review --uncommitted` before merge.

## AI workflow checks
- Ensure `README.md`, `AGENTS.md`, and linked docs agree on commands and scope.
- Prefer repository-root commands over guessed defaults.

## Failure handling
- Stop at the first failed gate, fix, then rerun the minimal required check.
