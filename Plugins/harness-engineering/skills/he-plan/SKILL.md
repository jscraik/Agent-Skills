---
name: he-plan
description: "Create execution-ready Harness Engineering plans from approved specs or issues. Use when sequencing, risk, validation, and handoff are needed before work."
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
## Constraints
Redact secrets; do not mutate files in planning. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No vague phases, missing validation, or orphan Linear/spec links.
## Philosophy
Harness Engineering plans are execution contracts.
## Examples
- User says: "Can you inspect this approved spec and make the implementation plan?"
- User says: "Please revise the plan as a complete replacement plan."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
