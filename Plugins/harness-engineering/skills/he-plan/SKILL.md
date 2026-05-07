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
Return schema_version when structured. `.harness/plan/**.md` durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, slack_policy, and blackboard_delta.
## Procedure
Explore first, ask second; use update_plan only for live progress; before writing durable docs choose `.harness/plan/**.md` from the artifact routing contract; turn scope into ordered implementation units; run or explicitly block coding-harness plan gates when the repo exposes them. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility: name the exact first-contact budget, shrink default help, demote plumbing commands, require full catalogs to use an advanced/all flag, rewrite the README front door around the golden path, add admission tests, add fresh-agent eval, and require ablation decisions for every still-visible command family.
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
## Examples
- "Inspect `.harness/specs/account-settings.md` and JSC-246, then write the implementation plan under `.harness/plan/` with plan IDs, validation commands, rollback, and a Linear/spec/plan traceability table."
- "Inspect the latest preflight output, then deepen `.harness/plan/JSC-246-account-settings.md` and return a complete replacement plan."
## Assets
Reference `assets/` only for skill packaging and browseability; durable plans and diagrams belong in repo artifacts or references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
