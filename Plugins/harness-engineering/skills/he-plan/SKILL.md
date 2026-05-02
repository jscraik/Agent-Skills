---
name: he-plan
description: "Use when approved specs or Linear issues need execution-ready HE plans before work."
metadata:
  skill-type: team_automation
---
# Harness Engineering Plan
## When to Use
Use after approved spec/issue; do non-mutating inspection before planning.
## Inputs
Spec, Linear issue, repo state, constraints, product blockers.
## Outputs
Return schema_version when structured. durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix.
## Procedure
Explore first, ask second; use update_plan only for live progress; turn scope into ordered implementation units.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check dependencies, tests, rollback, and handoff readiness.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not mutate files in planning. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
