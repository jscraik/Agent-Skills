---
name: he-compound
description: "Analyze session, repo, Linear, and harness evidence to refresh HE lifecycle state. Use when multi-stage HE work needs source-prompt coverage, resume routing, or earliest-stage recovery."
metadata:
  skill-type: team_automation
---
# Harness Engineering Compound
## Philosophy
Coordinate state, not ceremony. Compound should identify the earliest incomplete stage and preserve the evidence chain that lets the next agent act immediately.
## When to Use
Use when work spans brainstorm/spec/plan/work/review or needs refresh/resume control.
## Inputs
Goal, Linear/project-brain state, specs, plans, PRs, session evidence, solved-problem evidence.
## Outputs
Return schema_version when structured. Stage map, active owner, blockers, next action, blackboard_delta, retained references, `.harness/solutions/**` capture status, and Project Brain status.
## Procedure
1. Reconstruct lifecycle state from live repo evidence, Linear, specs, plans, PRs, validation, session evidence, and Project Brain.
2. Resolve the stage context contract enough to identify the earliest incomplete, stale, or conflicted stage.
3. When an original prompt, external workflow, old manual method, or plugin comparison is the baseline, apply source-prompt coverage before routing downstream; preserve source prompt status, evidence depth, coverage gaps, not-inspected evidence classes, repo-specific drift signals, original prompt coverage, downstream confidence, and next route.
4. Keep scope tight: start with 2-3 focused surfaces that prove lifecycle state
   before loading broader repo or session evidence.
5. Ask before choosing when earliest incomplete stage, resume target, refresh route, or source-prompt coverage conflicts across evidence.
6. Preserve Harness lifecycle state in coding-harness-managed repos and refresh or explicitly block Project Brain only when repository context changed.
7. Use solution capture only for solved-problem evidence; write new captures under `.harness/solutions/**`, not legacy `docs/solutions/**`.
8. Use UI plan routing only when UI-plan artifacts are present, then hand off to `he-plan`, `he-work`, or `he-code-review`.
9. Route product-compression blockers such as `active_stage: spec_refresh_required` to `he-spec` instead of approving another additive implementation pass.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check routing, stage artifacts, and handoff evidence.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Compound reconstructs lifecycle state and routes the next stage. Do not collapse multi-stage work into execution or refresh Project Brain unless source evidence proves a context change.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- Compound owns state reconstruction, not implementation.
- Legacy docs may be source evidence, but new solved-problem captures belong under `.harness/solutions/**`.
## Constraints
Redact secrets; never collapse multi-stage work into one vague task. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Turning a multi-stage workflow into one vague implementation task.
- Refreshing Project Brain without checking whether repo context changed.
- Writing new HE solution captures to legacy `docs/solutions/**` instead of `.harness/solutions/**`.
- Treating `docs/ui-plan/**` or `docs/ui-plans/**` as new canonical output instead of legacy UI-plan source evidence.
- Treating a chat summary as a replacement for Linear, spec, plan, PR, or validation links.
- Advancing to work when prior acceptance proved implementation presence but not first-contact compression.
## Examples
- "Inspect and resume the coding-harness run for JSC-246; map Linear, spec, plan, PR, Project Brain, north-star evidence, and tell me the exact next HE stage."
- "Inspect the HE compound state after PR 154 merged, update Project Brain if `.harness` changed, and capture any solved-problem doc that is now warranted."
## Assets
Reference `assets/` only for skill packaging and browseability; lifecycle state belongs in structured handoff evidence.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Solution capture: `Plugins/harness-engineering/references/solution-capture-contract.md`
- Source prompt coverage: `Plugins/harness-engineering/references/source-prompt-coverage-contract.md`
- UI plan routing: `Plugins/harness-engineering/references/ui-plan-routing-contract.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
