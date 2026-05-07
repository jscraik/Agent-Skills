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
Problem, Linear issue, QA report, source evidence, current-vs-latest spec status.
## Outputs
Return schema_version when structured. schema_version: 1, complete replacement spec section or `.harness/specs/**.md` artifact, Linear Acceptance Traceability, acceptance IDs, validation plan, and blackboard_delta.
## Procedure
Inspect session-collector evidence and repo truth; resolve/create the Linear tracker for non-trivial work; before writing durable docs choose `.harness/specs/**.md` from the artifact routing contract; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan with coding-harness state when applicable. When feedback says a prior cockpit, golden-path, or agent-native plan was too additive, load the compression contract and make first-contact budget, standalone command admission, docs deletion budget, fresh-agent eval, ablation proof, and evidence-backed metric gates blocking acceptance criteria.
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
## Examples
- For `JSC-246`, convert a QA report about the account settings flow into a complete replacement spec section with Linear Acceptance Traceability, acceptance IDs, assumptions, validation, and rollback notes.
- When a current spec exists but the latest session evidence changes scope, compare current-vs-latest spec status before adding requirements.
- Write new or replacement durable spec docs under `.harness/specs/**.md`; treat legacy `Specs/` paths as source evidence.
## Assets
Reference `assets/` only for skill packaging and browseability; spec source material belongs in references, not generated images.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Doctrine: `Plugins/harness-engineering/references/he-spec-doctrine.md`
- Artifact: `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
