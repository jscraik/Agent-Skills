---
name: he-work
description: "Build approved Harness Engineering plans or scoped todos with traceable validation. Use when execution is approved or the task is tiny and low risk."
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
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No untracked work, speculative fixes, or skipped validation.
## Philosophy
Harness Engineering work ships traceable verified slices.
## Examples
- User says: "Can you build JSC-246 with delegate mode and verified slices?"
- User says: "Implement the plan while preserving user edits in dirty worktrees."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
- Work contract: `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- Modes: `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`
