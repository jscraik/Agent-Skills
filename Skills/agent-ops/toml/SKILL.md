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
- [Philosophy](#philosophy)
- [Procedure](#procedure)
- [TOML Guidelines](#toml-guidelines)
- [Editing Rules](#editing-rules)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [References](#references)

## When to use

- Use for TOML config creation, review, or schema-safe fixes.
- Inputs: target files, owning tool, expected key paths, and compatibility constraints.
- Deliver valid TOML with minimal key-path churn and notes for schema-impacting edits.

## Required inputs

- Target TOML file path and owning tool or schema.
- Intended key paths, value types, and compatibility constraints.
- Validation command or parser expected to consume the file.

## Deliverables

- Minimal TOML edit preserving existing comments and order where possible.
- Validation evidence from parser, schema, or owning tool.
- Notes for any type, key-path, or compatibility risk.

## Philosophy

- Prefer schema truth and low-churn edits over clever rewrites.

## Procedure

1. Confirm the consumer schema and current key paths.
2. Make the smallest compatible edit.
3. Validate before closeout.

## TOML Guidelines

- Preserve key order where tool owners expect readability.
- Prefer explicit scalars and arrays over ambiguous shapes.
- Keep one responsibility per table and use dotted keys consistently.
- Do not mix inline tables and expanded tables for the same object path.

## Editing Rules

- Change only the smallest required key path.
- Retain existing comments unless provably outdated.
- Keep trailing commas out of arrays and inline tables.

## Validation

- Run the relevant parser/schema/tool checks for touched files.
- Fail fast: stop at the first failed gate and report exact blocker evidence.

## Constraints

- If schema ownership is unclear, pause before adding keys.
- Redact secrets and do not run destructive or network commands unless explicitly approved.

## Anti-patterns

- Redefining key paths, mixing table styles for one object, or skipping validation.

## Failure mode

If the owning schema, value type, or validation command cannot be identified, stop and report the missing contract before editing.

## Gotchas

- Quoting numeric values can silently change type semantics.

## See Also

| Skill | When to use |
|---|---|
| [[yaml]] | Schema-aware config review for YAML-based tooling configs |
| [[he-fix-bugs]] | Triage config parsing failures with evidence-first diagnosis |

**Topic map:** [[agent-ops]]

## References

- Deep guidance: `references/deep-guidance.md`
