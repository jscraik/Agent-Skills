---
title: Code Scanning Remediation
type: playbook
status: active
last_reviewed: 2026-04-09
sources:
  - /Users/jamiecraik/.codex/memories/MEMORY.md
  - https://github.com/jscraik/Agent-Skills/security/code-scanning
---

# Code Scanning Remediation

## Purpose

Close open code quality/security findings quickly while preserving branch hygiene and test confidence.

## Steps

1. Query live open alerts from GitHub API before editing.
2. Group by rule and file, then patch with smallest behavior-preserving edits.
3. Run targeted local tests/compile checks.
4. Commit and push.
5. Wait for CodeQL workflow completion, then re-query live counts.

## Commands

```bash
gh api 'repos/jscraik/Agent-Skills/code-scanning/alerts?state=open&per_page=100'
gh api 'repos/jscraik/Agent-Skills/dependabot/alerts?state=open&per_page=100'
gh run list --workflow "CodeQL" --branch main --limit 5
gh run watch <run-id> --exit-status
```

## Failure Handling

- If command execution is blocked by runtime policy, apply [AskForApproval Policy Block](../failures/askforapproval-policy-bug.md) mitigation.
- If commit signing fails, apply [1Password Git Signing Buffer Error](../failures/onepassword-git-signing-buffer.md) mitigation.
