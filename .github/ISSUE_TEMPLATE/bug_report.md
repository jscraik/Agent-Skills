---
name: Bug report
about: Report a defect in a skill, script, or docs workflow
title: "[bug] "
labels: bug
assignees: ""
---

## Summary

Describe the bug in 1-2 sentences.

## Reproduction steps

1.
2.
3.

## Expected behavior

What should have happened?

## Actual behavior

What happened instead?

## Environment

- OS:
- Shell:
- Branch/commit:

## Evidence

Paste logs, command output, or screenshots that help reproduce the issue.

## Checks run

- [ ] `bash Infrastructure/scripts/sync_skills.sh` (if relevant)
- [ ] `python3 Infrastructure/scripts/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` (if relevant)
