---
name: he-plan
description: "Create bounded Harness Engineering execution plans from approved specs or issue slices. Use when work needs ordered implementation units, explicit scope boundaries, rollback posture, traceability, and validation gates before code changes."
metadata:
  skill-type: team_automation
---
# Harness Engineering Plan
## Philosophy
Plans are execution contracts, not chat checklists. They should let another agent implement the work from source evidence while preserving Linear/spec/plan/PR traceability.
## When to Use
Use after an approved spec/issue; do non-mutating inspection before planning. Keep scope tight: start with the approved artifact plus the nearest repo evidence, and only load additional surfaces when they change sequencing, validation, or rollback.
## Inputs
Spec, Linear issue, repo state, constraints, product blockers.
## Outputs
Return schema_version when structured. `.harness/plan/**.md` durable plan, complete replacement plan when revising, repo-relative file paths, risks, validation, Linear/spec/plan/PR traceability matrix, post_plan_handoff, slack_policy, and blackboard_delta.

Always make steering and proof searchable in the output: include `interactive_status`, `selection_evidence`, `route`, `stage`, `scope`, `traceability`, `validation`, `safe_to_continue`, and `blocked_reason`. For post-plan handoff, set `interactive_status: asked` when multiple valid next stages require a blocking choice, `interactive_status: autonomous_assumption` when headless mode records the conservative route, or `interactive_status: blocked` when execution would otherwise proceed without authority.
## Procedure
1. Explore first and resolve the stage context contract; use `update_plan` only for live progress.
2. Confirm the plan stays inside one selected milestone, parent issue, refactor phase, or execution slice; run the Linear Delta Capture Gate when consuming existing tracked plans.
3. Route durable output to `.harness/plan/**.md`, or `.harness/plan/**-ui-plan.md` for dedicated UI plans, and apply Artifact Identity frontmatter.
4. Load UI, coding-harness, document-review, and specialist-skill references only when the selected slice proves the trigger.
5. Apply the first-principles contract to choose the smallest proof-producing slice first and classify Type 1 versus Type 2 decisions before broad sequencing.
6. Apply the plugin hook capability contract when implementation may add, alter, or depend on bundled plugin hooks. Treat `plugin_hooks` as optional feature-gated runtime behavior, and plan fallback skill, validator, or eval proof rather than assuming hooks are live.
7. Convert scope into ordered implementation units with acceptance traceability, dependencies, validation gates, rollback, risks, and out-of-scope boundaries.
8. Treat strategy, triage, review, and feature docs as context unless the approved Linear/refactor slice admits them.
9. End with `post_plan_handoff`; ask before continuing when multiple valid next stages remain, and continue only when the user already authorized it.
10. For cockpit, golden-path, command-catalog, or agent-native compression work, plan subtractive proof before additive compatibility.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check dependencies, tests, rollback, and handoff readiness.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Planning is non-mutating except for approved durable plan artifacts. Do not implement, commit, create Linear objects, or advance stages unless the user already authorized continuation.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- A chat `update_plan` is not the durable HE plan artifact.
- Multiple valid next stages require interactive steering before execution.
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
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Domain context: `Plugins/harness-engineering/references/domain-context-contract.md`
- Domain model routing: `Plugins/harness-engineering/references/domain-model-routing.md`
- Domain model production: `Plugins/harness-engineering/references/domain-model-production-contract.md`
- First principles: `Plugins/harness-engineering/references/first-principles-contract.md`
- Plugin hook capability: `Plugins/harness-engineering/references/plugin-hook-capability-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Document review tiers: `Plugins/harness-engineering/references/document-review-finding-tiers.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Linear delta capture gate: `Plugins/harness-engineering/references/linear-delta-capture-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Execution slice contract: `Plugins/harness-engineering/references/execution-slice-contract.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- UI plan routing: `Plugins/harness-engineering/references/ui-plan-routing-contract.md`
- Post-plan handoff: `Plugins/harness-engineering/skills/he-plan/references/post-plan-handoff.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
