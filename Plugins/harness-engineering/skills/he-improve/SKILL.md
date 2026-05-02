---
name: he-improve
description: "Use when HE hardening, optimization, polish, or capability improvement needs measurement."
metadata:
  skill-type: team_automation
---
# Harness Engineering Improve
## When to Use
Use when hardening, optimising, polishing, or capability-lifting existing code/skills/workflows.
## Inputs
Current artifact, evidence, session-collector evidence, metrics, constraints.
## Outputs
Return schema_version when structured. Gap list, prioritized improvements, validation, retained references.
## Procedure
Before any new skill package is proposed, inspect existing surfaces; label path fragments and bundle names as evidence labels; close coverage-gap items.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Compare before/after behavior and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve important context in references. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Session evidence: `Plugins/harness-engineering/references/session-evidence-skillify-triage.md`
