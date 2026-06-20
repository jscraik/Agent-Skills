---
schema_version: 1
---

# Wiki Agent Guide

## Scope

- Applies to `Wiki/**`.
- Inherits the repository root [AGENTS.md](../AGENTS.md).

## Edit Policy

- Treat this subtree as reference, knowledge, and wiki material unless a file is
  explicitly admitted by a plan, policy, or workflow as binding source.
- Preserve provenance, dates, source links, and migration notes when editing
  knowledge pages.
- Do not let wiki prose override `AGENTS.md`, `Docs/agents/**`, schemas,
  validators, or executable contracts. Promote durable rules into the owning
  instruction or policy surface instead.

## Context Pointers

- Wiki entrypoint: [README.md](README.md).
- Published/wiki pages: `Wiki/wiki/**`.
- Workflow and safety guidance: [../Docs/agents/13-workflow-and-safety-guidance.md](../Docs/agents/13-workflow-and-safety-guidance.md).

## Validation

- Validate internal links and any generated index that consumes the wiki.
- If a wiki page is used as evidence for a code or governance change, cite the
  owning source of truth as well as the wiki summary.
