---
schema_version: 1
---

# scripts Agent Guide

## Scope

- Applies to root-level `scripts/**`.
- Inherits the repository root [AGENTS.md](../../AGENTS.md).

## Edit Policy

- Treat root-level scripts as stable operator entrypoints or compatibility
  wrappers. Prefer implementation logic in `Infrastructure/scripts/**` or
  `Infrastructure/scripts/lib/**` when a change needs tests or shared code.
- Keep wrappers explicit, shell-safe, and runnable through `bash` or the
  documented interpreter. Avoid hidden dependency on the caller's interactive
  shell state.
- Preserve root command contracts from `./bin/ask`; do not add parallel
  command surfaces when an existing wrapper can be extended.
- For technical work, read the root [CODESTYLE.md](../../CODESTYLE.md) before
  editing.

## Context Pointers

- Tooling policy: [../../Docs/agents/02-tooling-policy.md](../../Docs/agents/02-tooling-policy.md).
- Validation guidance: [../../Docs/agents/04-validation.md](../../Docs/agents/04-validation.md).
- Infrastructure scripts: [README.md](README.md).

## Validation

- Run the exact script path touched with the narrowest safe arguments.
- If a wrapper delegates to `Infrastructure/**`, also run the delegated path or
  an owning test that proves the handoff.
