---
name: yaml
description: Create and review YAML files with safe indentation, schema-aware structure, and low-surprise serialization. Use when editing YAML config or workflow files.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Philosophy](#philosophy)
- [Procedure](#procedure)
- [YAML Guidelines](#yaml-guidelines)
- [Editing Rules](#editing-rules)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)
- [References](#references)

## When to use

- Use for YAML authoring, review, or schema-safe fixes.
- Inputs: target files, consumer tool, required keys, and formatting conventions.
- Deliver valid YAML with stable indentation, key ordering, and scalar notes.

## Required inputs

- Target YAML file path and consuming tool or schema.
- Required keys, scalar expectations, and formatting conventions.
- Validation command or parser expected to consume the file.

## Deliverables

- Minimal YAML edit preserving meaningful ordering and comments.
- Validation evidence from parser, schema, or consuming tool.
- Notes for indentation, scalar coercion, or compatibility risk.

## Philosophy

- Prefer schema truth and low-churn edits over clever rewrites.

## Procedure

1. Confirm the consumer schema and current key paths.
2. Make the smallest compatible edit.
3. Validate before closeout.

## YAML Guidelines

- Use spaces only; never use tabs for indentation.
- Keep indentation width consistent within a file.
- Quote values that could be misread as booleans, numbers, dates, or null.
- Prefer block style for complex mappings and sequences.

## Editing Rules

- Minimize whitespace-only churn unless formatting is the task.
- Preserve key order when downstream tooling expects logical ordering.
- Avoid mixing flow style with block style in the same section.

## Validation

- Run the relevant parser/schema/tool checks for touched files.
- Fail fast: stop at the first failed gate and report exact blocker evidence.

## Constraints

- If schema compatibility is uncertain, stop and confirm constraints.
- Redact secrets and do not run destructive or network commands unless explicitly approved.

## Anti-patterns

- Reindenting unrelated sections, changing scalar meaning, or skipping validation.

## Failure mode

If the consuming schema, scalar expectations, or validation command cannot be identified, stop and report the missing contract before editing.

## Gotchas

- Unquoted values like `on`, `off`, or `no` may coerce unexpectedly.

## See Also

| Skill | When to use |
|---|---|
| [[toml]] | Schema-aware config review for TOML-based tooling configs |
| [[he-fix-bugs]] | Triage config parsing failures with evidence-first diagnosis |

**Topic map:** [[agent-ops]]

## References

- Deep guidance: `references/deep-guidance.md`
