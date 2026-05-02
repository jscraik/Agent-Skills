---
name: he-brainstorm
description: "Generate grounded Harness Engineering options from fuzzy product or engineering intent. Use when requirements are unclear and no spec should be written yet."
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
## Constraints
Redact secrets; do not turn brainstorming into execution. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No fake certainty, hidden assumptions, or context trimming.
## Philosophy
Harness Engineering brainstorming makes ambiguity useful without losing evidence.
## Examples
- User says: "Can you inspect this vague Linear idea and turn it into grounded options?"
- User says: "Help me validate whether this should become a spec or plan."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
