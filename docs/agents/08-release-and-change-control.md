# Release and Change-Control Checks

## Table of Contents
- [Release prerequisites](#release-prerequisites)
- [Governance gates](#governance-gates)

## Release prerequisites
- Confirm changed files are intentional and minimal.
- Keep `.agent/PLANS.md` idempotent when plan work touches it.

## Governance gates
- `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
- `bash ~/.codex/scripts/verify-work.sh`

- If either command fails, fix first failure, then rerun until green.
