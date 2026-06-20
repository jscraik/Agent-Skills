---
schema_version: 1
---

# Skills Agent Guide

## Scope

- Applies to `Skills/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat this subtree as canonical first-party skill source. Runtime projections
  under `.agents/**`, `.skillsets/**`, or user home links are generated views,
  not the source to edit.
- Before changing skills, sync policy, runtime projections, or agent-facing
  docs, read [UBIQUITOUS_LANGUAGE.md](../UBIQUITOUS_LANGUAGE.md).
- Keep each `SKILL.md` focused. Move bulky detail to nearby `references/**`,
  `scripts/**`, `assets/**`, or templates, then leave a clear route from the
  skill entrypoint.
- Do not claim a skill is runtime-usable from source existence alone. Prove the
  runtime projection or state the boundary as source inspection only.

## Context Pointers

- Skill lifecycle rules: [../Docs/agents/17-skill-management.md](../Docs/agents/17-skill-management.md).
- Path ownership: [../Docs/agents/14-path-ownership-boundaries.md](../Docs/agents/14-path-ownership-boundaries.md).
- Skill templates: `Infrastructure/templates/**`.

## Validation

- For skill content changes, run the strictest practical skill audit or the
  relevant `./bin/ask skills ... --json --robot` command.
- For projection changes, regenerate through the repo wrapper and validate
  freshness; never hand-edit generated projection files.
