---
name: he-router
description: "Use when ambiguous, mixed, or folded-alias HE requests need the correct stage."
metadata:
  skill-type: team_automation
---
# Harness Engineering Router
## When to Use
Use when stage choice is unclear, mixed, or a folded alias appears.
## Inputs
Request text, repo root, optional Linear/session evidence.
## Outputs
Return `schema_version` when structured, plus `selected_stage`, `source_path`, `folded_mode`, `blocker`, and `lifecycle_exit_status`.
## Procedure
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check deterministic aliases and subagent role availability.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; never enumerate every child skill to the model. Do not remove important context for budget trimming; move it to the deferred context index.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Preserved router rules: `references/context-preservation.md`
