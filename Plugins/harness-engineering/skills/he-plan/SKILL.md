---
name: he-plan
description: "WHAT: Generate HE plans from approved specs, Linear issues, or source artifacts. Use when sequencing, tests, rollback, or traceability need planning."
metadata:
  skill-type: team_automation
---
# Harness Engineering Plan
## Philosophy
Plans are execution contracts, not chat checklists. They should let another agent implement the work from source evidence while preserving Linear/spec/plan/PR traceability.
## When to Use
Use after approved spec/issue; do non-mutating inspection before planning.
## Inputs
Spec, Linear issue, repo state, constraints, product blockers.
## Outputs
Return schema_version when structured. `.harness/plan/**.md` durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, post_plan_handoff, slack_policy, and blackboard_delta.
## Procedure
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract and apply its Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; for dedicated UI plans use `.harness/plan/**-ui-plan.md` and the UI plan routing contract, treating `docs/ui-plan/**` and `docs/ui-plans/**` as legacy source evidence and reporting Project Brain sync/defer/block status when `.harness/knowledge/**` is in use; when planning coding-harness-managed work load the execution slice contract, run the Linear Delta Capture Gate for existing tracked plans, and keep the plan inside the selected milestone, parent issue, refactor phase, or execution slice; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. Treat `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` as context unless the approved Linear/refactor slice admits them. End with the post-plan handoff state, and route to the next authorized HE stage in the same run when the user has already asked to continue. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check dependencies, tests, rollback, and handoff readiness.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not mutate files in planning. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Using `update_plan` as the durable plan artifact.
- Planning implementation units without acceptance IDs, validation, or rollback.
- Skipping the Linear or coding-harness gate because the implementation feels obvious.
- Deferring the real compression moves while counting metadata, classification, or docs routing as success.
- Leaving help/catalog budgets as principles instead of naming the concrete public rails, hidden commands, and blocked future additions.
- Expanding a plan from secondary review, strategy, triage, or feature docs after the selected execution slice is already approved.
## Examples
- "Inspect `.harness/specs/account-settings.md` and JSC-246, then write the implementation plan under `.harness/plan/` with plan IDs, validation commands, rollback, and a Linear/spec/plan traceability table."
- "Inspect the latest preflight output, then deepen `.harness/plan/JSC-246-account-settings.md` and return a complete replacement plan."
- Run `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <plan-path>` for tracked plan artifacts before handoff.
## Assets
Reference `assets/` only for skill packaging and browseability; durable plans and diagrams belong in repo artifacts or references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Linear delta capture gate: `Plugins/harness-engineering/references/linear-delta-capture-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Execution slice contract: `Plugins/harness-engineering/references/execution-slice-contract.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- UI plan routing: `Plugins/harness-engineering/references/ui-plan-routing-contract.md`
- Post-plan handoff: `Plugins/harness-engineering/skills/he-plan/references/post-plan-handoff.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
