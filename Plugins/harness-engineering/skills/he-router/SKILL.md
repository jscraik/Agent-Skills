---
name: he-router
description: "Analyze and route HE lifecycle requests. Use when stage, artifact path, or specialist route is uncertain."
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
1. Route with `./bin/ask`, keeping request text data-only.
2. Select exactly one next stage or folded mode; load only that stage.
3. Use the stage context contract only to resolve routing-critical repo, session, Linear, and artifact identity.
4. Classify `.harness` artifacts by content shape before path; report path, title, or Linear mismatches as traceability defects.
5. Ask once before guessing when deterministic routing leaves one consequential stage or source choice unresolved.
6. After selecting the stage, hand persistent `/goal`, resume-over-time, or keep-working-until-done behavior to the goal continuity contract and `Skills/agent-ops/goal-governor`.
7. Route compression blockers such as `spec_refresh_required` to `he-spec` with the compression contract.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check deterministic aliases and subagent role availability.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Routing is non-mutating. Do not continue into implementation, planning, review repair, or tracker updates unless the selected stage is authorized.
## Gotchas
- Folded aliases are modes, not missing skills.
- The router owns stage selection, not lifecycle execution.
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
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Goal continuity: `Plugins/harness-engineering/references/goal-continuity.md`; durable goal boards: `Skills/agent-ops/goal-governor`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Session evidence trace: `Plugins/harness-engineering/references/session-evidence-trace-context.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- Preserved router rules: `references/context-preservation.md`
- Lifecycle tracer evals: `Plugins/harness-engineering/references/lifecycle-tracer-evals.yaml`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
