---
name: he-work
description: "Implement approved Harness Engineering plan slices with strict scope control. Use when code or artifact changes are authorized by a bounded plan, validation commands are known, and the work can preserve traceability, rollback, and handoff evidence."
metadata:
  skill-type: team_automation
---
# Harness Engineering Work
## Philosophy
Ship the smallest honest slice. Work should leave clear proof of what changed, why it matched the plan, and which validation or blocked gate supports the handoff.
## When to Use
Use when execution is approved or tiny and low risk.
Treat tiny low-risk execution as no more than two files, no auth/security/permissions/data/CI/dependency/public-API/tool/skill/plugin changes, no external side effects, and a known validation command. Otherwise route to `he-spec`, `he-plan`, or the relevant risk stage first.
## Inputs
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees, optional active thread goal.
## Outputs
Return schema_version when structured. schema_version: 1, changed files, validation, blockers, rollback, next handoff, slack_policy, blackboard_delta, git_staging_status, and staged_paths.

Always make steering and proof searchable in the output: include `interactive_status`, `selection_evidence`, `route`, `stage`, `scope`, `traceability`, `validation`, `safe_to_continue`, and `blocked_reason`. When branch, goal, plan, Linear issue, selected slice, or multiple next stages conflict, ask once with `request_user_input` when available or return `interactive_status: blocked`; in unattended mode record `interactive_status: autonomous_assumption` only for non-mutating assumptions and keep mutation blocked without authority.
## Procedure
1. Mark live state before editing: branch, dirty worktree, active `/goal`, plan, Linear issue, PR, and selected slice.
2. Resolve the stage context contract; stop on conflicts between branch, goal, plan, Linear issue, or selected slice.
3. Load specialist, UI-plan, coding-harness, and Linear Delta references only when the approved slice proves the trigger.
4. Keep `update_plan` as a live checklist; execute only the approved implementation unit.
5. Before delegation or parallel work, run the work contract overlap check and use external delegation only for bounded non-overlapping slices or isolated worktrees.
6. Run or explicitly block the smallest relevant validation gates, preserving exact command/path, actor, timestamp, recovery step, and rollback posture when blocked.
7. Apply the git staging contract for files changed in this turn only; report any unrelated dirty paths without staging them.
7. Apply the visual reference contract when user-visible behavior, screenshot
   evidence, rollback state, validation evidence, or before/after state cannot
   be reviewed clearly from text alone.
8. Handoff to `he-code-review` mode `autofix` when review or validation evidence requires repair.
For blocked coding-harness gates, preserve exact failing command/path, actor, timestamp, recovery step, and rollback posture in the handoff.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Run exact gates for changed paths and report outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Mutate only files in the approved implementation slice. Do not stage, commit, push, resolve review threads, or close trackers unless separately authorized.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- Dirty worktree ownership and active `/goal` conflicts are blockers, not context to overwrite.
- Validation must run against the touched production path or be recorded as blocked with the smallest recovery step.
## Constraints
Redact secrets; preserve user edits. Do not remove important context for budget trimming; apply the context-disposition policy by moving important still-valid context to references and intentionally discarding stale, duplicated, unsafe, superseded, or low-signal text.
## Anti-Patterns
- Editing before checking the active branch, dirty state, and source artifact.
- Editing when an active thread goal conflicts with the branch, issue, plan, or PR.
- Expanding product scope because implementation uncovered a tempting adjacent fix.
- Pulling unapproved work from secondary review, strategy, triage, or feature docs instead of the selected execution slice.
- Claiming done without exact validation or blocked-gate evidence.
## Examples
- "Inspect JSC-246 and implement only the units in `.harness/plan/JSC-246-account-settings.md`, preserve my dirty edits, then run `bash scripts/run-harness-setup-checks.sh`."
- "Inspect `Infrastructure/templates/linear-handoff.md`; it has the wrong Linear field name, so make that tiny fix, run its focused test, and hand off for review."
- "Use delegate mode only for bounded verified slices."
## Assets
Reference `assets/` only for skill packaging and browseability; execution evidence belongs in validation output, PRs, and handoff notes.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Domain context: `Plugins/harness-engineering/references/domain-context-contract.md`
- Domain model production: `Plugins/harness-engineering/references/domain-model-production-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
- Execution slice contract: `Plugins/harness-engineering/references/execution-slice-contract.md`
- Linear delta capture gate: `Plugins/harness-engineering/references/linear-delta-capture-gate.md`
- Approval flow: `repo:Plugins/harness-engineering/skills/shared/references/approval-flow.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Work contract: `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- Modes: `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`
- UI plan routing: `Plugins/harness-engineering/references/ui-plan-routing-contract.md`
- Visual reference contract: `Plugins/harness-engineering/references/visual-reference-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
