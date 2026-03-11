# Agent Testing Gates

## Table of Contents
- [Validation order](#validation-order)
- [Failure policy](#failure-policy)

## Validation order
1. `bash scripts/sync_skills.sh`
2. `python3 scripts/docs_lint.py --mode warn --config docs-policy.json`
3. `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md` (if plans touched)
4. `bash ~/.codex/scripts/verify-work.sh`
5. `codex review --uncommitted` before merge

## Failure policy
- Fail fast.
- Fix first failure, then rerun the same check.
- Keep diffs limited to the failure domain.
