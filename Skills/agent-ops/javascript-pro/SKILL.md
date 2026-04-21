---
name: javascript-pro
description: Create and debug modern JavaScript code with ES6+, async patterns, and Node.js APIs. Use when working on runtime behavior, promises, or browser and Node compatibility.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Core Practices](#core-practices)
- [Async Safety](#async-safety)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for JavaScript implementation and review tasks.
- Use when async behavior or runtime compatibility is critical.

## Required inputs

- Target runtime and module format.
- Files or functions to update.
- Error or performance constraints.

## Deliverables

- Behavior-correct JavaScript changes.
- Clear async flow and explicit error handling.
- Compatibility notes when needed.

## Core Practices

- Prefer small pure functions for transformation logic.
- Use `const` by default, `let` only when reassignment is required.
- Keep API surfaces explicit and documented through JSDoc when needed.

## Async Safety

- Await every promise that affects correctness.
- Use `Promise.all` only for truly independent operations.
- Surface actionable errors with context.


- Redact secrets, tokens, credentials, and sensitive data by default.
## Examples

```javascript
export async function loadJson(url) {
  const response = await fetch(url)
  if (!response.ok) throw new Error(`Fetch failed: ${response.status}`)
  return response.json()
}
```

## Failure mode

- If side effects cannot be isolated, keep behavior unchanged and document risk.

## Gotchas

- Unawaited promises can mask production failures.

## See Also

| Skill | When to use |
|---|---|
| [[typescript]] | Typed JavaScript superset when strict contracts and module boundaries are needed |
| [[biome-linting]] | Enforce JavaScript/TypeScript lint and format rules with Biome |

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
