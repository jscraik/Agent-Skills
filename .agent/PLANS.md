# Plans


<!-- AGENT-FIRST-PLANS:START -->
## Plan Contract (Agent-first)

All significant implementation plans MUST use task graphs with explicit dependencies.

Validation command:

```bash
python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md
```

Current implementation plan:

```yaml
tasks:
  - id: T1
    title: Define canonical eval schema v2 and migration rules
    depends_on: []
  - id: T2
    title: Extend eval templates and docs for schema v2
    depends_on: [T1]
  - id: T3
    title: Add Codex JSONL deterministic grader and assertion support
    depends_on: [T1]
  - id: T4
    title: Extend run_skill_evals.py for dual-run and merged scorecards
    depends_on: [T3]
  - id: T5
    title: Add rubric/budget score merging patterns
    depends_on: [T4]
  - id: T6
    title: Bulk-migrate missing/weak skill eval+contract references
    depends_on: [T2]
  - id: T7
    title: Add CI tiered gate interface and artifact publishing flow
    depends_on: [T4, T5, T6]
  - id: T8
    title: Add baseline and regression dashboard generation
    depends_on: [T7]
  - id: T9
    title: Document week-3 hardening policy for tier2 promotion
    depends_on: [T8]
  - id: T10
    title: Run verification gates and summarize readiness
    depends_on: [T5, T6, T7, T8, T9]
```

Optional cross-plan reference:

```yaml
external_dep: "/absolute/repo/path#T12"
```
<!-- AGENT-FIRST-PLANS:END -->
