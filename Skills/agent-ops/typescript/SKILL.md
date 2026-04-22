---
name: typescript
description: Use when authoring or reviewing TypeScript code that requires strict type safety, explicit module contracts, and predictable runtime boundaries.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Type Safety](#type-safety)
- [Module Boundaries](#module-boundaries)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for TypeScript code authoring or review.
- Use when strict typing and API contracts need hardening.

## Required inputs

- Target files or module scope.
- Runtime constraints (Node/browser/edge).
- Existing type errors or contract requirements.

## Deliverables

- Type-safe implementation changes.
- Explicitly typed exported surfaces.
- Notes for any unavoidable tradeoffs.

## Type Safety

- Avoid `any`; model unknown values with guards and narrow types.
- Prefer explicit return types on exported functions.
- Use discriminated unions for stateful workflows.


- Redact secrets, tokens, credentials, and sensitive data by default.
## Module Boundaries

- Prefer named exports over default exports in shared modules.
- Keep runtime validation close to IO boundaries.
- Avoid barrel files when they obscure ownership.

## Examples

```typescript
export function parsePort(value: string): number {
  const parsed = Number.parseInt(value, 10)
  if (Number.isNaN(parsed)) throw new Error(`Invalid port: ${value}`)
  return parsed
}
```

## Failure mode

- If domain types are unclear, pause and request schema clarification.

## Gotchas

- Casting with `as unknown as` hides real typing defects.

## See Also

| Skill | When to use |
|---|---|
| [[javascript-pro]] | Base JavaScript patterns when runtime compatibility and async flow need attention |
| [[biome-linting]] | Enforce TypeScript lint and format rules with Biome |

**Topic map:** [[agent-ops]]


## Philosophy

- Optimize for clear, verifiable outcomes with the minimum necessary changes.
- Keep guidance deterministic so repeated runs produce consistent decisions.

## Procedure

1. Confirm scope, constraints, and required inputs before edits.
2. Apply focused changes tied directly to the requested outcome.
3. Re-run the highest-signal validations and capture concrete evidence.

## Validation

- Run the relevant local checks for touched files and workflow contracts.
- Fail fast: stop at the first blocking validation failure and report exact evidence.
- Re-run checks after fixes and record residual risk if any remains.

## Anti-patterns

- Skipping validation after making changes.
- Applying broad refactors to solve narrow issues.
- Assuming behavior without evidence from current checks.

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
