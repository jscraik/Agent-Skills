# Release and Change-Control Checks

## Table of Contents
- [Git risk escalation](#git-risk-escalation)
- [Release prerequisites](#release-prerequisites)
- [Governance gates](#governance-gates)

## Git risk escalation
- For rebase of 5+ commits, merge-conflict resolution, or force-pushes, pause and present:
  1. Current branch state.
  2. Proposed strategy and risks.
  3. Alternatives.
  4. User confirmation before proceeding.
- Verify conflicts explicitly before claiming a clean merge path.

## Release prerequisites
- Confirm changed files are intentional and minimal.
- Keep `.agent/PLANS.md` idempotent when plan work touches it.

## Governance gates
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agent/PLANS.md` (external dependency)
- `bash Infrastructure/scripts/verify-work.sh` (repo-local wrapper)

- If either command fails, fix first failure, then rerun until green.
