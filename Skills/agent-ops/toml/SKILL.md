---
name: toml
description: Create and review TOML configuration with strict typing and predictable structure. Use when editing tool configuration files that require schema-safe TOML.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [TOML Guidelines](#toml-guidelines)
- [Editing Rules](#editing-rules)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for TOML config creation and review.
- Use when config correctness and low-churn edits are required.

## Required inputs

- Target file(s) and owning tool.
- Schema or expected key paths.
- Constraints on backward compatibility.

## Deliverables

- Valid TOML updates.
- Minimal-scope key-path changes.
- Notes for any schema-impacting edits.

## TOML Guidelines

- Preserve key order where tool owners expect readability.
- Prefer explicit scalars and arrays over ambiguous shapes.
- Keep one responsibility per table and use dotted keys consistently.
- Do not mix inline tables and expanded tables for the same object path.

## Editing Rules

- Change only the smallest required key path.
- Retain existing comments unless provably outdated.
- Keep trailing commas out of arrays and inline tables.

## Examples

```toml
[tool.ruff]
line-length = 100
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
```

## Failure mode

- If schema ownership is unclear, pause and confirm before adding keys.

## Gotchas

- Quoting numeric values can silently change type semantics.

## See Also

| Skill | When to use |
|---|---|
| [[yaml]] | Schema-aware config review for YAML-based tooling configs |
| [[he-fix-bugs]] | Triage config parsing failures with evidence-first diagnosis |

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
