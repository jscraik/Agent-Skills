---
name: he-spec
description: "Use when HE work needs Linear-backed scope, requirements, acceptance, and validation."
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
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not invent requirements. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Doctrine: `Plugins/harness-engineering/references/he-spec-doctrine.md`
- Artifact: `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
