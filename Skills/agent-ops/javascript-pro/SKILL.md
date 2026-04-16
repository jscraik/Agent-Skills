---
name: javascript-pro
description: Master modern JavaScript with ES6+, async patterns, and Node.js APIs. Handles promises, event loops, and browser/Node compatibility.
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

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
