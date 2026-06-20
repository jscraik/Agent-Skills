---
schema_version: 1
---

# docs Agent Guide

## Scope

- Applies to lowercase `docs/**`.
- Inherits the repository root [AGENTS.md](/AGENTS.md). Do not confuse this
  subtree with uppercase `Docs/**`, which contains the canonical repo guidance
  referenced by the root instructions.

## Edit Policy

- Before changing workflow, validation, path ownership, skill management, or
  agent-facing guidance here, check whether the canonical owner is under
  `Docs/agents/**` instead.
- Keep lowercase docs as compatibility, generated, or intentionally retained
  documentation only when a reader or migration reason is clear.
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
