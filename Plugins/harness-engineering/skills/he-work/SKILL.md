---
name: he-work
description: "Execute approved Harness Engineering plans, ordered todos, or tiny low-risk direct tasks when code or docs must land with traceable validation, tracker state, and handoff evidence."
metadata:
  skill-type: team_automation
---
# Harness Engineering Work
## Philosophy
Ship the smallest verified slice that preserves the active plan, tracker, user edits, and evidence chain.

## When to Use
Use when execution is approved or tiny and low risk.
## Inputs
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees, optional active thread goal.
## Outputs
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff.
## Procedure
Mark current active state; if a thread goal exists, verify it matches the active Linear/spec/plan/branch/PR chain before editing; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; handoff to he-code-review mode:autofix when needed.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Run exact gates for changed paths and report outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
- Do not use a thread goal as the source of truth for scope, acceptance, validation, or tracker state.
- Do not continue when the active goal, plan, Linear issue, branch, or PR disagree.
- Do not hand off meaningful changes without validation evidence or a concrete blocker.
## Examples
- For `JSC-246`, implement the approved account settings flow plan in delegate mode, keep `update_plan` as the live checklist, and return changed files plus verified slices.
- For a tiny low-risk fix, capture the current active state, make the smallest traceable edit, run the exact gate, and hand off to `he-code-review mode:autofix` if review findings remain.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Work contract: `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- Modes: `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`
