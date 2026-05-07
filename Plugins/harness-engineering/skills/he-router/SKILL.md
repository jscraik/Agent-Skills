---
name: he-router
description: "WHAT: Route ambiguous HE requests to the right lifecycle stage. Use when intent mixes brainstorm, spec, plan, work, review, or aliases."
metadata:
  skill-type: team_automation
---
# Harness Engineering Router
## Philosophy
Keep routing small and evidence-led. The router decides the next Harness Engineering stage, preserves traceability, and avoids loading inactive or unrelated skill context until a concrete stage is selected.

## When to Use
Use when stage choice is unclear, mixed, or a folded alias appears.
## Inputs
Request text, repo root, optional Linear/session evidence.
## Outputs
Return `schema_version` when structured, plus `selected_stage`, `source_path`, `folded_mode`, `blocker`, `blackboard_delta`, and `lifecycle_exit_status`.
## Procedure
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement. When the request explicitly asks for persistent continuation, `/goal`, resume-over-time, or keep-working-until-done behavior, apply the goal continuity contract after selecting the HE stage.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check deterministic aliases and subagent role availability.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; never enumerate every child skill to the model. Do not remove important context for budget trimming; move it to the deferred context index.
## Anti-patterns
- Do not treat folded aliases as missing skills when they can map to a supported stage.
- Do not continue into implementation, review, or planning when required Linear, spec, plan, PR, validation, or session evidence is missing.
- Do not load every Harness Engineering reference file to choose a route; inspect the router rules and then load only the selected stage.
## Examples
- "Inspect this HE request; it mentions a bug, plan drift, and CodeRabbit comments, so pick the right stage and tell me what evidence is missing."
- "Inspect and route this old `$he-refine` request through the current Harness Engineering surface."
- "Inspect the mixed brainstorm plus implementation request, decide the first lifecycle stage, and preserve Linear traceability."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`
- Preserved router rules: `references/context-preservation.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
