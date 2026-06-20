---
schema_version: 1
---

# Docs Agent Guide

## Scope

- Applies to uppercase `Docs/**`, the canonical repository guidance and
  reference-documentation tree.
- Inherits the repository root [AGENTS.md](/AGENTS.md). Do not use this file
  as guidance for a lowercase compatibility `docs/**` tree unless content is
  explicitly moved there with a documented ownership change.

## Edit Policy

- Before changing workflow, validation, path ownership, skill management, or
  agent-facing guidance here, prefer the canonical owner under `Docs/agents/**`
  unless a narrower `Docs/**` reference surface is explicitly intended.
- Keep any future lowercase docs as compatibility, generated, or intentionally
  retained documentation only when a reader or migration reason is clear.
- Do not create a competing instruction hierarchy here. If a rule must bind
  agents, place it in the nearest applicable `AGENTS.md` or canonical
  `Docs/agents/**` file.

## Context Pointers

- Canonical instruction map: [Docs/agents/README.md](/Docs/agents/README.md).
- Lowercase surface policy: [Docs/agents/15-repo-surface-ownership.md](/Docs/agents/15-repo-surface-ownership.md).
- Path authority model: [Docs/agents/14-path-ownership-boundaries.md](/Docs/agents/14-path-ownership-boundaries.md).

## Validation

- Validate links after documentation edits.
- If moving content between `docs/**` and `Docs/**`, state the source,
  destination, owner, and reason; do not silently duplicate guidance.
