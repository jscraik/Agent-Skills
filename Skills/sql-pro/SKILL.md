---
name: sql-pro
description: Master modern SQL with cloud-native databases, OLTP/OLAP optimization, and advanced query techniques.
metadata:
  skill-type: code_quality_review
---

## Table of Contents

- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Query Design](#query-design)
- [Safety](#safety)
- [Examples](#examples)
- [Failure mode](#failure-mode)
- [Gotchas](#gotchas)

## When to use

- Use for SQL query, migration, or schema review work.
- Use when correctness and performance both matter.

## Required inputs

- Database engine and version.
- Tables/indexes in scope.
- Query goals and latency expectations.

## Deliverables

- Correct, parameterized SQL.
- Performance-aware query structure.
- Notes on indexing or migration implications.

## Query Design

- Select only needed columns; avoid `SELECT *` in production queries.
- Keep predicates sargable so indexes remain usable.
- Prefer explicit joins with clear alias naming.

## Safety

- Always parameterize user input.
- Separate read and write transactions when possible.
- Verify migration rollback behavior before release.

## Examples

```sql
SELECT id, email
FROM users
WHERE created_at >= $1
ORDER BY created_at DESC
LIMIT 100;
```

## Failure mode

- If schema assumptions are uncertain, stop and confirm before mutating data.

## Gotchas

- Non-sargable filters can negate otherwise correct indexes.

## References and assets

- Open deep guidance: `Infrastructure/references/deep-guidance.md`
- Read when: the task needs advanced edge cases, migration-safe patterns, or runtime-specific nuance beyond the core checklist.
