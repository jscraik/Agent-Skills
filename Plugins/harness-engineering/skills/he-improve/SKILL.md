---
name: he-improve
description: "Analyze and improve existing code, skills, or workflows through measured Harness Engineering loops. Use when the goal is hardening, optimization, polish, or capability lift."
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
## Constraints
Redact secrets; preserve important context in references. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No novelty for novelty, no context deletion, no unmeasured polish.
## Philosophy
Harness Engineering improvement raises reliability without hiding tradeoffs.
## Examples
- User says: "Can you inspect session evidence and harden this HE skill?"
- User says: "Improve this workflow while keeping references callable."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
- Session evidence: `Plugins/harness-engineering/references/session-evidence-skillify-triage.md`
