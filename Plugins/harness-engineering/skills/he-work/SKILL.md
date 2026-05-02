---
name: he-work
description: "Use when approved HE plans or tiny low-risk tasks need traceable execution."
metadata:
  skill-type: team_automation
---
# Harness Engineering Work
## When to Use
Use when execution is approved or tiny and low risk.
## Inputs
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees.
## Outputs
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff.
## Procedure
Mark current active state; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; handoff to he-code-review mode:autofix when needed.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Run exact gates for changed paths and report outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Examples
- For `JSC-246`, implement the approved account settings flow plan in delegate mode, keep `update_plan` as the live checklist, and return changed files plus verified slices.
- For a tiny low-risk fix, capture the current active state, make the smallest traceable edit, run the exact gate, and hand off to `he-code-review mode:autofix` if review findings remain.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Work contract: `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- Modes: `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`
