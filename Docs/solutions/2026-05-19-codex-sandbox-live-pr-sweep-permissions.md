---
title: Codex sandbox live PR sweep permissions
asset_family: agent operations automation
owner: Agent Skills Team
source_artifact: Skills/agent-ops/pr-green-sweep/SKILL.md
freshness_reviewed_on: 2026-05-19
review_after_days: 90
---

# Codex Sandbox Live PR Sweep Permissions

## Problem

The PR green sweep retried live GitHub state commands and classified repeated
`api.github.com` failures as network or credential trouble without first
proving that the Codex sandbox had explicit network permission. The same lane
also mixed in `mise` cache warnings, which obscured the actual live-state
blocker.

This caused repeated user steering instead of a durable operating fix.

## Resolution

For PR sweep work, treat GitHub, CodeRabbit, CircleCI, Snyk, package-registry,
and branch-protection checks as networked live-state commands. Run them with
explicit Codex sandbox network permission before diagnosing outage, credential,
or platform failures.

When a command may invoke `gh`, `mise`, or `uv`, set `XDG_CACHE_HOME`,
`XDG_STATE_HOME`, `MISE_CACHE_DIR`, and `UV_CACHE_DIR` to writable
sandbox-approved directories before treating cache or state warnings as the
blocker.

After two equivalent live-state, approval, or user-correction failures, stop the
PR rotation and refine the nearest durable contract before retrying:

- `AGENTS.md` for repo-wide operating defaults.
- `Docs/agents/13-workflow-and-safety-guidance.md` for workflow policy.
- `Skills/agent-ops/pr-green-sweep/SKILL.md` for the PR sweep execution lane.
- `.harness/memory/LEARNINGS.md` for learned failure prevention.

## Evidence

The corrected environment contract was proven by running a live GitHub PR query
with explicit network permission and a writable `mise` cache:

```bash
XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache XDG_STATE_HOME=/private/tmp/agent-skills-xdg-state \
UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache MISE_CACHE_DIR=/private/tmp/agent-skills-mise-cache \
gh pr list --state open --limit 3 --json number,title,headRefName,headRefOid,mergeable
```

The command returned current open pull requests instead of the previous
`api.github.com` connection failure.

The validation path also proved why `XDG_CACHE_HOME`, `UV_CACHE_DIR`, and
`XDG_STATE_HOME` must be part of the standard contract: strict skill audit
reached diagnostics and security checks only after temp state/cache paths were
configured, and the family benchmark passed when run with the repo's
PyYAML-capable Python.

## Follow-Up

Keep this solution linked from any future PR sweep, CI sweep, or review-thread
automation that runs inside Codex sandboxing. If similar failures recur, update
the wrapper or validation script so the corrected permission/cache setup is
applied mechanically.
