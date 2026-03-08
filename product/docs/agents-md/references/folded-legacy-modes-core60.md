# Folded Legacy Modes (Core60)

Destination skill: `product/docs/agents-md`

This file captures legacy capabilities migrated from retired skills.

## `claude-target`
- Source skill: `product/docs/claude-md`
- Legacy description: Refactor or create CLAUDE.md using progressive disclosure: keep always-on guidance concise, include only non-obvious commands/style/workflow rules, use @imports for deeper docs, and flag contradictions/bloat. Use when the user asks to create, update, or audit CLAUDE.md files.
- Fold rationale: Both are agent-instruction doc refactors with target-specific output flavor.
- Legacy section map:
  - Remember
  - Compliance
  - Philosophy
  - Scope and triggers
  - Response format (required)
  - Cognitive Support / Plain-Language

## `gemini-target`
- Source skill: `product/docs/gemini-md`
- Legacy description: Use when a user asks to create, update, or review Gemini CLI context (`GEMINI.md`) and memory workflows; emit merge-safe edits that preserve existing guidance while adding what is missing for in-scope tasks.
- Fold rationale: Same core operation as agents-md with different platform framing.
- Legacy section map:
  - Table of Contents
  - Remember
  - Compliance
  - Philosophy
  - Scope and triggers
  - Response format (required)
