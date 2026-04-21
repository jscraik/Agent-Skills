---
name: rust-pro
description: Master Rust 1.75+ with modern async patterns, advanced type system features, and production-ready systems programming.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Ownership Rules](#ownership-rules)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for Rust implementation or review work.
- Use when correctness, safety, and performance all matter.

## Required inputs

- Target crate/module.
- Borrowing/ownership constraints.
- Error semantics and runtime expectations.

## Deliverables

- Safe and idiomatic Rust updates.
- Explicit error propagation.
- Notes on any performance-sensitive decisions.

## Ownership Rules

- Prefer borrowing over cloning in hot paths.
- Use iterators before indexing loops when possible.
- Keep lifetimes implicit unless explicit annotations improve clarity.

## Error Handling

- Prefer `Result<T, E>` for recoverable paths.
- Use domain-specific error enums over stringly-typed errors.
- Attach context when propagating errors.

## Examples

```rust
pub fn parse_port(value: &str) -> Result<u16, String> {
    value.parse::<u16>().map_err(|_| format!("invalid port: {value}"))
}
```

## Failure mode

- If ownership requirements conflict, favor correctness and simplify data flow.

## Gotchas

- Overusing `clone()` can hide unnecessary allocations.

## See Also

| Skill | When to use |
|---|---|
| [[go]] | Systems programming with similar error-handling and concurrency patterns |
| [[he-fix-bugs]] | Triage Rust ownership and borrow-checker errors with evidence-first diagnosis |

**Topic map:** [[agent-ops]]

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
