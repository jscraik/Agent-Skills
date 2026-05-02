---
name: he-router
description: "Analyze and route ambiguous Harness Engineering requests to the right lifecycle stage. Use when routing is unclear, mixed, or a folded HE alias is invoked."
metadata:
  skill-type: team_automation
---
# Harness Engineering Router
## When to Use
Use when stage choice is unclear, mixed, or a folded alias appears.
## Inputs
Request text, repo root, optional Linear/session evidence.
## Outputs
Return schema_version when structured. schema_version, selected stage, source_path, folded mode, blocker, lifecycle exit status.
## Procedure
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check deterministic aliases and subagent role availability.
## Constraints
Redact secrets; never enumerate every child skill to the model. Do not remove important context for budget trimming; move it to the deferred context index.
## Anti-patterns
No shell interpolation, broad loading, or archive symlink routing.
## Philosophy
Harness Engineering routing protects context budget and stage accuracy.
## Examples
- User says: "Can you inspect this mixed request and choose the right HE stage?"
- User says: "Use he-deepen-plan on this approved spec."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Preserved router rules: `references/context-preservation.md`
