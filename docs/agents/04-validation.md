# Validation and Checks

## Table of Contents
- [Repository checks](#repository-checks)
- [AI workflow checks](#ai-workflow-checks)
- [Failure handling](#failure-handling)

## Repository checks
- `bash scripts/sync_skills.sh`
- `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
- `python3 /Users/jamiecraik/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `/Users/jamiecraik/.codex/scripts/verify-work.sh`

## AI workflow checks
- Ensure `README.md`, `AGENTS.md`, and linked docs agree on commands and scope.
- Prefer repository-root commands over guessed defaults.

## Failure handling
- Stop at the first failed gate, fix, then rerun the minimal required check.
