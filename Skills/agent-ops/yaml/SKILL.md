---
name: yaml
description: Write and review YAML files with safe indentation, schema-aware structure, and low-surprise serialization.
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
| [[systematic-debugging]] | Triage config parsing failures with evidence-first diagnosis |

**Topic map:** [[agent-ops]]

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
