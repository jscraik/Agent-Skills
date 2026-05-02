---
name: he-spec
description: "Generate traceable Harness Engineering specs with Linear-backed acceptance criteria. Use when a problem needs requirements, scope, and validation before planning."
metadata:
  skill-type: team_automation
---
# Harness Engineering Spec
## When to Use
Use when requirements are needed before plan/work; Explore first and ask second.
## Inputs
Problem, Linear issue, QA report, source evidence, current-vs-latest spec status.
## Outputs
Return schema_version when structured. schema_version: 1, complete replacement spec section, Linear Acceptance Traceability, acceptance IDs, validation plan.
## Procedure
Inspect session-collector evidence and repo truth; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check traceability, tests, observability, rollback, and owner evidence.
## Constraints
Redact secrets; do not invent requirements. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No optional Linear for tracked work, no trimmed context, no plan disguised as spec.
## Philosophy
Harness Engineering specs make intent testable.
## Examples
- User says: "Can you inspect JSC-246 QA report and write the account settings flow spec?"
- User says: "Please compare the active spec with the latest spec first."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
- Doctrine: `Plugins/harness-engineering/references/he-spec-doctrine.md`
- Artifact: `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
