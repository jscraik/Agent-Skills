---
schema_version: 1
---

# Infrastructure Agent Guide

## Scope

- Applies to `Infrastructure/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat this subtree as the factory plane for `ask`, validation, schemas,
  fixtures, tests, sync, projection, packaging, and governance mechanics.
- Keep public repo operations routed through root `./bin/ask`; edit
  `Infrastructure/bin/ask` and implementation modules only when changing the
  command machinery itself.
- When changing CLI behavior, schemas, generated receipts, or SDK contracts,
  update implementation, tests, fixtures, and docs together.
- For technical work, read the root [CODESTYLE.md](../CODESTYLE.md) before
  editing. If a narrower module document exists, follow it as well.
- Keep canonical source and runtime projection lanes separate. Do not use
  generated projections as implementation source.

## Context Pointers

- Infrastructure scripts map: [scripts/README.md](scripts/README.md).
- Path ownership: [../Docs/agents/14-path-ownership-boundaries.md](../Docs/agents/14-path-ownership-boundaries.md).
- Validation contract: [../Docs/agents/04-validation.md](../Docs/agents/04-validation.md).
- Skill lifecycle rules: [../Docs/agents/17-skill-management.md](../Docs/agents/17-skill-management.md).

## Validation

- Prefer repo wrappers and targeted tests over ad hoc commands.
- For Python changes, run the nearest targeted `pytest` path under
  `Infrastructure/tests/**` before widening.
- For schema or fixture changes, run the owning validator and include exact
  `pass`, `fail`, or `blocked` outcomes.
