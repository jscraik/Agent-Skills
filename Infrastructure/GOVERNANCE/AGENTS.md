---
schema_version: 1
---

# GOVERNANCE Agent Guide

## Scope

- Applies to `GOVERNANCE/**`.
- Inherits the repository root [AGENTS.md](../../AGENTS.md).

## Edit Policy

- Treat this subtree as policy, risk, context-budget, and runtime-separation
  governance. Changes should name the mechanism they alter, not just the prose
  being edited.
- Keep governance claims evidence-backed. Do not relax risk, exception,
  runtime-separation, or lockfile constraints without a matching validator,
  schema, or documented decision.
- Preserve machine-readable files as machine-readable contracts. Use structured
  editors or schema-aware checks for JSON and YAML.

## Context Pointers

- Runtime separation manifests: `GOVERNANCE/runtime-separation/**`.
- Repo surface policy: [../../Docs/agents/15-repo-surface-ownership.md](../../Docs/agents/15-repo-surface-ownership.md).
- Validation policy: [../../Docs/agents/04-validation.md](../../Docs/agents/04-validation.md).

## Validation

- For runtime-separation changes, run the relevant runtime-separation validator
  or report the exact blocker.
- For policy-only edits, validate links and state whether executable behavior
  changed.
