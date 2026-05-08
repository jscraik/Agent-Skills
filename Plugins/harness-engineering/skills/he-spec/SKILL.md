---
name: he-spec
description: "Create evidence-backed HE specs. Use when approved intent needs acceptance criteria before implementation."
metadata:
  skill-type: product_verification
---
# Harness Engineering Spec
## Philosophy
Make intent testable. A good HE spec preserves source truth, states boundaries, and gives planning enough acceptance detail without doing the plan's job.
## When to Use
Use when requirements are needed before plan/work; Explore first and ask second.
## Inputs
Problem, approved execution slice as one milestone, one parent issue, one refactor phase, or one execution slice, Linear issue, QA report, source evidence, current-vs-latest spec status.
## Outputs
Return schema_version when structured. schema_version: 1, bounded implementation spec for one milestone, parent issue, refactor phase, or execution slice; complete replacement spec section or `.harness/specs/**.md` artifact; Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
## Procedure
1. Resolve the stage context contract first; stop if no milestone, parent issue, refactor phase, or execution slice is selected.
2. Load primary source artifacts for the selected slice: Linear plan, selected refactor when applicable, decisions, core invariants, and brainstorm artifacts. Treat strategy, triage, review, and feature docs as evidence only unless the slice admits them.
3. Apply document-review tiers, specialist skill steering, and interactive steering only when their trigger conditions are proven by source inspection.
4. Resolve or block the Linear tracker; run the Linear Delta Capture Gate for existing tracked plans before admitting changed Linear work into scope.
5. Route durable output to `.harness/specs/**.md`, classify existing artifacts by content shape before path, and apply Artifact Identity frontmatter.
6. Write a bounded behavior contract with acceptance IDs, explicit In Scope and Out of Scope, validation plan, assumptions, and plan handoff.
7. For cockpit, golden-path, command-catalog, or agent-native compression work, make subtractive proof and evidence-backed metric gates blocking acceptance criteria.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check traceability, tests, observability, rollback, and owner evidence.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Non-mutating until the user authorizes artifact writes. Do not create, close, or mutate Linear objects unless the current task explicitly grants that authority.
## Gotchas
- Stage context is required before writing specs; local docs do not replace Linear/source traceability.
- Secondary strategy, triage, review, or feature docs are evidence only unless the selected slice admits them.
## Constraints
Redact secrets; do not invent requirements. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Inventing acceptance criteria that are not grounded in source evidence.
- Writing task sequences instead of behavior contracts.
- Weakening Linear traceability because a local spec already exists.
- Treating classification, metadata, docs routing, or command existence as compression proof.
- Letting secondary review, strategy, triage, or feature material drive implementation beyond the selected Linear/refactor slice.
- Writing a giant programme spec instead of a bounded spec for one approved milestone, parent issue, refactor phase, or execution slice.
## Examples
- For `JSC-246`, convert a QA report about the account settings flow into a complete replacement spec section with Linear Acceptance Traceability, acceptance IDs, assumptions, validation, and rollback notes.
- When a current spec exists but the latest session evidence changes scope, compare current-vs-latest spec status before adding requirements.
- Write new or replacement durable spec docs under `.harness/specs/**.md`; treat legacy `Specs/` paths as source evidence.
- Run `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py <spec-path>` for tracked spec artifacts before handoff.
## Assets
Reference `assets/` only for skill packaging and browseability; spec source material belongs in references, not generated images.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Document review tiers: `Plugins/harness-engineering/references/document-review-finding-tiers.md`
- Session evidence trace: `Plugins/harness-engineering/references/session-evidence-trace-context.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Linear delta capture gate: `Plugins/harness-engineering/references/linear-delta-capture-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Execution slice contract: `Plugins/harness-engineering/references/execution-slice-contract.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- Doctrine: `Plugins/harness-engineering/references/he-spec-doctrine.md`
- Artifact: `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
