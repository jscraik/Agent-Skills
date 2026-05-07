---
name: he-work
description: "WHAT: Build approved HE changes in verified slices with traceability. Use when execution is approved or bounded delegation is needed."
metadata:
  skill-type: team_automation
---
# Harness Engineering Work
## Philosophy
Ship the smallest honest slice. Work should leave clear proof of what changed, why it matched the plan, and which validation or blocked gate supports the handoff.
## When to Use
Use when execution is approved or tiny and low risk.
## Inputs
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees, optional active thread goal.
## Outputs
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff, slack_policy, and blackboard_delta.
## Procedure
Mark current active state; if `/goal` is active, confirm it matches the branch, issue, plan, or PR before editing and treat mismatches as blockers rather than overwriting project truth. Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
For blocked coding-harness gates, preserve exact failing command/path, actor, timestamp, recovery step, and rollback posture in the handoff.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Run exact gates for changed paths and report outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Editing before checking the active branch, dirty state, and source artifact.
- Editing when an active thread goal conflicts with the branch, issue, plan, or PR.
- Expanding product scope because implementation uncovered a tempting adjacent fix.
- Claiming done without exact validation or blocked-gate evidence.
## Examples
- "Inspect JSC-246 and implement only the units in `Plans/JSC-246-account-settings.md`, preserve my dirty edits, then run `bash scripts/run-harness-setup-checks.sh`."
- "Inspect `Infrastructure/templates/linear-handoff.md`; it has the wrong Linear field name, so make that tiny fix, run its focused test, and hand off for review."
## Assets
Reference `assets/` only for skill packaging and browseability; execution evidence belongs in validation output, PRs, and handoff notes.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Work contract: `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- Modes: `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
