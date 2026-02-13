# Plan: run-tests-and-write-artifacts

## Summary
Create a utility skill that runs tests reproducibly and writes required artifacts to `/mnt/data`, scoped to Jamie core tooling defaults:
1) `just test` (if available)
2) `uv run pytest -q`
3) `pnpm test` / `pnpm -r test`

## Task graph
```yaml
tasks:
  - id: T1
    title: Bootstrap + scaffold skill skeleton
    depends_on: []
  - id: T2
    title: Author SKILL.md with scoped routing, negative examples, edge-case routing
    depends_on: [T1]
  - id: T3
    title: Author references/contract.yaml (artifact + JSON schema contract)
    depends_on: [T2]
  - id: T4
    title: Author references/evals.yaml (happy/edge/negative cases)
    depends_on: [T2, T3]
  - id: T5
    title: Run skill validators and fix failures
    depends_on: [T2, T3, T4]
  - id: T6
    title: Sync skill index/symlinks and run repo verification
    depends_on: [T5]
```

## Assumptions and defaults
- `/mnt/data` is writable in execution environment.
- Skill remains instruction-only in v0.1.0.
- Artifact overwrite is allowed.
- Network remains denied unless explicitly allowlisted.
