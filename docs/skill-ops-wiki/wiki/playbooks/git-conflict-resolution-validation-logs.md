---
title: Git Conflict Resolution for Validation Logs
type: playbook
status: active
last_reviewed: 2026-04-09
sources:
  - /Users/jamiecraik/dev/Agent-Skills/artifacts/validation/latest
---

# Git Conflict Resolution for Validation Logs

## Purpose

Safely resolve stash/pop conflicts in frequently changing validation logs.

## Steps

1. Run `git status --short --branch` to confirm conflicted files.
2. Inspect conflict markers in each file.
3. Prefer the newer upstream validation snapshot unless local run output is intentionally retained.
4. Stage resolved files, including force-add for ignored tracked paths when needed.
5. Confirm clean state and drop stale stash entries.

## Commands

```bash
git status --short --branch
git checkout --ours artifacts/validation/latest/<file>
git add -f artifacts/validation/latest/<file>
git stash drop stash@{0}
```

## Related

- [AskForApproval Policy Block](/docs/skill-ops-wiki/wiki/failures/askforapproval-policy-bug.md)
- [Validation Artifact Consistency](/docs/skill-ops-wiki/wiki/playbooks/validation-artifact-consistency.md)
