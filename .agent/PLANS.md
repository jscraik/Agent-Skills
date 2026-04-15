# Plans


<!-- AGENT-FIRST-PLANS:START -->
## Plan Contract (Agent-first)

All significant implementation plans MUST use task graphs with explicit dependencies.

Validation command:

```bash
python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agent/PLANS.md
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

Skill-graph onboarding migration plan (2026-02-26):

```yaml
tasks:
  - id: M1
    title: Freeze active skill inventory and baseline onboarding snapshot
    depends_on: []
  - id: M2
    title: Enforce task-profile schema requirements (delegation + no-improvement escalation)
    depends_on: [M1]
  - id: M3
    title: Implement profile generator and SKILL frontmatter binding updater
    depends_on: [M2]
  - id: M4
    title: Implement profile validator and wave-readiness artifact generation
    depends_on: [M3]
  - id: M5
    title: Generate all per-skill task profiles and onboarding checklist
    depends_on: [M3]
  - id: M6
    title: Validate all skills and publish profile-index + wave-readiness artifacts
    depends_on: [M4, M5]
  - id: M7
    title: Update promotion workflow and kill-switch runbook for wave gate preconditions
    depends_on: [M2]
  - id: M8
    title: Update governance approver policy to require >=2 approvers
    depends_on: [M2]
  - id: M9
    title: Add smoke runner for observe-only recursive loop probes
    depends_on: [M4]
  - id: M10
    title: Run onboarding smoke checks and capture report artifact
    depends_on: [M6, M9]
  - id: M11
    title: Document all-skills migration plan in docs/plans with wave acceptance gates
    depends_on: [M6, M7, M8]
  - id: M12
    title: Final verification and go/no-go readiness summary
    depends_on: [M10, M11]
```

Outstanding onboarding/readiness closeout plan (2026-03-29):

```yaml
tasks:
  - id: P0
    title: Baseline freeze and closeout contract
    depends_on: []
  - id: P1
    title: Event-envelope gate remediation
    depends_on: [P0]
  - id: P2
    title: Checklist ownership and status operationalization
    depends_on: [P0]
  - id: P3
    title: Plan-state and completion-tracking reconciliation
    depends_on: [P0, P1, P2]
  - id: P4
    title: Worktree closeout and change-slice hygiene
    depends_on: [P1, P2, P3]
  - id: P5
    title: Final validation and readiness handoff
    depends_on: [P4]
```

Closeout status update (2026-03-30):
- Closeout execution completed; evidence recorded in `Docs/plans/2026-03-29-fix-outstanding-onboarding-readiness-closeout-plan.md` execution ledger and acceptance checklist.
<!-- AGENT-FIRST-PLANS:END -->
