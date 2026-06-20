---
schema_version: 1
---

# Infrastructure Scripts Agent Guide

## Scope

- Applies to `Infrastructure/scripts/**`.
- Inherits the repository root [AGENTS.md](../../AGENTS.md).

## Edit Policy

- Treat `Infrastructure/scripts/**` as canonical implementation, validation,
  and test-support code for the root wrapper surfaces.
- Keep CLI and validation behavior testable through focused Python tests or the
  owning root `./bin/ask` command path.
- Preserve root command contracts from `./bin/ask`; update delegated
  implementation here when the behavior belongs behind an existing wrapper.
- For technical work, read the root [CODESTYLE.md](../../CODESTYLE.md) before
  editing.

## Context Pointers

- Tooling policy: [../../Docs/agents/02-tooling-policy.md](../../Docs/agents/02-tooling-policy.md).
- Validation guidance: [../../Docs/agents/04-validation.md](../../Docs/agents/04-validation.md).
- Root wrappers: [../../scripts/AGENTS.md](../../scripts/AGENTS.md).

## Validation

- Run the narrowest owning test or validator for the implementation path
  touched.
- If a root wrapper delegates to this subtree, also run the wrapper path when
  the change affects its observable behavior.
