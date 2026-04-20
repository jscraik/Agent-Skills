# Lifecycle Modes

Read when: the selected `he-compound` mode is `full-lifecycle` or `resume-from-stage`.

## Canonical purpose

Use `he-compound` as the orchestration layer for:

1. `he-brainstorm`
2. `he-spec`
3. `he-deepen-spec`
4. `he-technical-review` against the spec
5. `he-plan`
6. `he-deepen-plan`
7. `he-technical-review` against the plan
8. `he-work`
9. `he-review`
10. `he-compound` learning capture

This is the durable stage sequence to preserve from `workflow-compound.md`.

## Mode selection

### Full lifecycle

Use when:
- the request starts from a feature idea, problem statement, or rough delivery ask
- no trustworthy downstream CE artifact exists yet

Behavior:
- initialize a stage ledger
- set the current stage to the earliest required stage
- advance only when the active stage exit criteria are met

### Resume from stage

Use when:
- CE artifacts already exist
- the user wants the next correct stage instead of a fresh full run

Behavior:
- inspect the available artifacts and their quality
- mark already validated stages as complete
- continue from the earliest incomplete or untrusted stage
- if a later artifact exists but an upstream stage is weak, route backward to the smallest failing stage rather than pretending downstream work is still trustworthy

## Stage exit criteria

### 1. Brainstorm

Exit criteria:
- clear user or job context
- recommended approach selected
- explicit `spec_required`, risk, and complexity

### 2. Spec

Exit criteria:
- scope boundaries and invariants are explicit
- failure modes, operational behavior, and acceptance criteria are testable
- assumptions and non-goals are explicit

### 3. Deepen-spec

Exit criteria:
- missing edge cases resolved
- interfaces and contracts are concrete
- rollout, migration, and observability requirements are explicit

### 4. Technical review (spec)

Exit criteria:
- blocking gaps resolved
- risks categorized and mitigated
- readiness recommendation is explicit: proceed, revise, or stop

### 5. Plan

Exit criteria:
- implementation strategy decomposed into ordered, verifiable tasks
- each task has validation intent
- dependencies and rollback path are explicit

### 6. Deepen-plan

Exit criteria:
- execution details are practical and constraint-aware
- sequencing, ownership, and checkpoints are unambiguous
- test strategy covers critical paths and regressions

### 7. Technical review (plan)

Exit criteria:
- plan is operationally realistic
- hidden coupling and rollout risks are addressed
- implementation readiness is confirmed

### 8. Work

Exit criteria:
- code matches the approved plan or spec
- validations pass
- deviations are reflected upstream

### 9. Review

Exit criteria:
- findings synthesized and prioritized
- merge or readiness recommendation recorded
- follow-up actions are explicit

### 10. Compound (knowledge capture)

Exit criteria:
- one solution artifact created or updated
- reusable lessons linked to the relevant spec, plan, work, or review outcomes
- future-prevention recommendations documented

## Cross-stage quality gates

At every stage boundary verify:
- correctness: the artifact is internally consistent and testable
- design, if UI: accessibility, interaction states, and content strategy are explicit
- operational safety: observability, rollback, recovery, and failure handling are covered
- security: trust boundaries, auth assumptions, and data handling are explicit
- decision log: major tradeoffs are captured with rationale

Do not advance if a blocking gate fails. Fix the smallest blocking gap first.

## Planning-ledger rules

When using a planning ledger:
1. initialize one ledger step per lifecycle stage
2. keep exactly one stage `in_progress`
3. mark completed stages only when evidence exists
4. if a gate fails, keep the stage in progress and attach a concise remediation note
5. if scope changes, revise the ledger before continuing

Recommended ledger:

```text
1. Brainstorm
2. Spec
3. Deepen-spec
4. Technical review (spec)
5. Plan
6. Deepen-plan
7. Technical review (plan)
8. Work
9. Review
10. Compound
```

## UI branching protocol

For UI-impacting work, insert:
1. `workflow-spec-ui` after initial spec drafting
2. `workflow-plan-ui` before implementation starts

Use these to enforce:
- design-system consistency
- accessibility conformance, minimum WCAG 2.2 AA
- responsive behavior and loading, empty, and error states
- instrumentation for UX outcomes

## Output contract

Return:
- current stage
- completed stages with artifact paths
- open blockers and risks
- recommended next command
- if the lifecycle is effectively complete, a readiness summary plus optional learning-capture recommendation

If routing is ambiguous:
- ask one minimal clarifying question

If a stage check fails:
- report the exact failure
- recommend the smallest safe remediation
