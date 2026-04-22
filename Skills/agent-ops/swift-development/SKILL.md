---
name: swift-development
description: Create and review Swift code with modern concurrency, performance tuning, and idiomatic language patterns. Use when building or debugging Swift application logic.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Language Patterns](#language-patterns)
- [Concurrency](#concurrency)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for Swift language and architecture changes.
- Use when concurrency and state isolation require review.

## Required inputs

- Target module or feature.
- Concurrency model requirements.
- Platform/runtime constraints.

## Deliverables

- Idiomatic Swift changes.
- Concurrency-safe patterns.
- Notes on actor or threading assumptions.

## Language Patterns

- Favor value types for local state and predictable mutation.
- Use protocol-based composition for dependency boundaries.
- Keep API names aligned with Swift naming guidelines.

## Concurrency

- Prefer structured concurrency over detached tasks.
- Mark UI-facing work with `@MainActor`.
- Avoid shared mutable state across task boundaries.

## Examples

```swift
func parsePort(_ value: String) throws -> Int {
    guard let port = Int(value) else {
        throw NSError(domain: "Port", code: 1)
    }
    return port
}
```

## Failure mode

- If actor boundaries are ambiguous, reduce scope and preserve current behavior.

## Gotchas

- Detached tasks can bypass expected cancellation behavior.

## See Also

| Skill | When to use |
|---|---|
| [[rust-pro]] | Systems-level safety patterns that share Swift's value-type and concurrency thinking |
| [[he-fix-bugs]] | Triage Swift concurrency and actor isolation issues with evidence-first diagnosis |

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

## Constraints

- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not expand scope beyond the request unless explicitly asked.
- Prefer safe, reversible edits over broad refactors.

## Anti-patterns

- Skipping validation after making changes.
- Applying broad refactors to solve narrow issues.
- Assuming behavior without evidence from current checks.

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
