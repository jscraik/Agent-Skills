---
name: he-spec
description: "WHAT: Generate Linear-backed HE specs with acceptance IDs and validation. Use when requirements or traceability are needed before planning."
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
Inspect session-collector evidence and repo truth; for coding-harness-managed work load the execution slice contract before writing requirements; consume the approved `.harness/linear/<repo-name>-linear-plan.md`, selected `.harness/refactors/<selected-refactor>.md` when applicable, `.harness/decisions/*.md`, `.harness/core/*.md`, and `.harness/brainstorm/*.md` as primary inputs; use `.harness/strategy/*.md`, `.harness/triage/*.md`, `.harness/review/*.md`, and `.harness/features/*.md` only for evidence or context; apply the specialist skill steering contract when a proven domain need can sharpen acceptance criteria, validation, non-goals, or risk; apply the interactive steering contract when behavior, scope boundary, acceptance authority, or selected slice remains unresolved after source inspection; stop if no selected milestone, parent issue, refactor phase, or execution slice is identified. Resolve/create the Linear tracker for non-trivial work; for existing tracked plans run the Linear Delta Capture Gate before consuming the approved slice, reconcile required labels, classify new or changed Linear issues, and promote at most one admitted item into the spec scope; require Linear project, milestone, parent issue, sub-issues when present, labels, priority, dependencies, and agent/human route for tracked specs; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract and apply its Artifact Identity frontmatter so `artifact_id`, `canonical_slug`, `title`, H1, origin, and Linear identifiers trace to the same slice; define scope, assumptions, assets/icon-small.png if packaging matters, explicit In Scope and Out of Scope boundaries, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check traceability, tests, observability, rollback, and owner evidence.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
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
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Linear delta capture gate: `Plugins/harness-engineering/references/linear-delta-capture-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Execution slice contract: `Plugins/harness-engineering/references/execution-slice-contract.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Doctrine: `Plugins/harness-engineering/references/he-spec-doctrine.md`
- Artifact: `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
