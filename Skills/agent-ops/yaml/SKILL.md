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
- [YAML Guidelines](#yaml-guidelines)
- [Editing Rules](#editing-rules)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for YAML authoring and review.
- Use when indentation/schema correctness is critical.

## Required inputs

- Target YAML file(s) and consumer tool.
- Schema expectations and required keys.
- Formatting constraints from existing conventions.

## Deliverables

- Valid YAML updates.
- Stable indentation and key ordering.
- Notes on ambiguous scalar handling.

## YAML Guidelines

- Use spaces only; never use tabs for indentation.
- Keep indentation width consistent within a file.
- Quote values that could be misread as booleans, numbers, dates, or null.
- Prefer block style for complex mappings and sequences.

## Editing Rules

- Minimize whitespace-only churn unless formatting is the task.
- Preserve key order when downstream tooling expects logical ordering.
- Avoid mixing flow style with block style in the same section.

## Examples

```yaml
version: "1"
services:
  api:
    image: ghcr.io/example/api:latest
    environment:
      LOG_LEVEL: "info"
      FEATURE_FLAG: "false"
    ports:
      - "3000:3000"
```

## Failure mode

- If schema compatibility is uncertain, stop and confirm constraints.

## Gotchas

- Unquoted values like `on`, `off`, or `no` may coerce unexpectedly.

## See Also

| Skill | When to use |
|---|---|
| [[toml]] | Schema-aware config review for TOML-based tooling configs |
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
