---
name: go
description: Best practices for working with Go codebases. Use when writing, debugging, or exploring Go code, including reading dependency sources and documentation.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Style](#style)
- [Error Flow](#error-flow)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for Go code authoring and review tasks.
- Use when package boundaries and error handling need tightening.

## Required inputs

- Package and file scope.
- Expected API behavior.
- Runtime/performance constraints.

## Deliverables

- Idiomatic Go changes.
- Wrapped, actionable errors.
- Minimal API churn outside requested scope.

## Style

- Keep functions small and package-focused.
- Return concrete structs from constructors when interfaces are unnecessary.
- Prefer composition over deep embedding chains.

## Error Flow

- Return wrapped errors with `%w` for traceability.
- Avoid panic in library code.
- Check and handle every returned error.

## Examples

```go
func ParsePort(value string) (int, error) {
	port, err := strconv.Atoi(value)
	if err != nil {
		return 0, fmt.Errorf("parse port %q: %w", value, err)
	}
	return port, nil
}
```

## Failure mode

- If API compatibility risk is high, keep signatures stable and narrow the patch.

## Gotchas

- Silent ignored errors usually become runtime bugs.

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
