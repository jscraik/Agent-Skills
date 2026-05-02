---
name: he-brainstorm
description: "Use when fuzzy intent needs grounded HE options before spec, plan, or work."
metadata:
  skill-type: team_automation
---
# Harness Engineering Brainstorm
## When to Use
Use before spec writing when intent is fuzzy; preserve Context preservation and assign `scope_tier`.
## Inputs
User goal, repo evidence, Linear/project hints.
## Outputs
Return schema_version when structured. Stated / Inferred / Out of scope, options, risks, warrant notes, and next stage.
## Procedure
Explore first; separate evidence from guesses; route to he-spec, he-plan, or he-work only when ready.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check scope, traceability, and handoff clarity.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; do not turn brainstorming into execution. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
