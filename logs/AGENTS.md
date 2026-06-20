---
schema_version: 1
---

# logs Agent Guide

## Scope

- Applies to `logs/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat this subtree as local run output unless a tracked file has an explicit
  fixture, archive, or reader contract.
- Do not commit raw logs, secrets, tokens, private telemetry, or bulky local
  traces. Promote only distilled summaries, fixtures, or policy evidence with a
  retention reason.
- Redact sensitive content before using logs in docs, PR bodies, or review
  artifacts.

## Context Pointers

- Repo surface ownership: [../Docs/agents/15-repo-surface-ownership.md](../Docs/agents/15-repo-surface-ownership.md).
- Security and governance: [../Docs/agents/06-security-and-governance.md](../Docs/agents/06-security-and-governance.md).

## Validation

- Before staging anything under `logs/**`, identify its owner, reader, retention
  reason, and whether it should be a fixture or ignored runtime state.
- If no durable role exists, leave the log untracked and summarize the evidence
  elsewhere.
