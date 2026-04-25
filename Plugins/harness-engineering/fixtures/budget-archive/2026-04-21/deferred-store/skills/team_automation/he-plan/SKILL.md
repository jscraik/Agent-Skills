---
name: he-plan
description: Plan execution work from specs, brainstorm outputs, bugs, or feature requests into an implementation-ready sequence. Use when the user needs the Harness Engineering planning stage before execution.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for the Harness Engineering planning stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Plans should be executable, testable, and constraint-aware.
- Resolve risk and sequencing ambiguity before coding.
- Stay in planning mode when directly invoked; ask focused clarifying questions or bootstrap context rather than abandoning the planning workflow.

## When to use

- Use when requirements exist and implementation sequencing must be defined.
- Use before `he-work` when execution tasks and verification strategy are not yet explicit.
- Use when a spec, brainstorm, bug report, or raw feature description must be turned into a durable implementation plan.

## Inputs

- Source spec, brainstorm output, or defect scope.
- Constraints, dependencies, and risk/compliance requirements.
- Optional existing plan path to update or deepen.
- Optional requirements document or recent planning artifact that should be treated as the primary source.

## Outputs

- Ordered implementation plan with validation intent per task.
- Explicit blockers, assumptions, and next-stage recommendation.
- Domain-readiness decision that confirms canonical terms are stable or routes back upstream.
- Explicit plan route: `fresh`, `resume`, or `deepen`.
- Plan depth sized to the work: `lightweight`, `standard`, or `deep`.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Resolve the best planning source first: existing plan, requirements doc, spec, brainstorm output, or direct request.
2. If a matching recent plan already exists, decide whether to resume, deepen, or start a fresh plan instead of duplicating it.
3. Treat the most authoritative source artifact as primary input and carry forward its problem frame, scope, requirements, and open questions.
4. Check interface readiness before task decomposition. If the work depends on a new module, API, CLI, plugin, tool, service, data-access, or shared-helper boundary, confirm the source defines the caller-facing contract.
5. If the interface contract is missing or only implied, route back to `he-deepen-spec` instead of burying interface design inside implementation tasks.
6. Check domain readiness: if core terms, relationships, or `CONTEXT.md` updates are missing, route back to `he-brainstorm` or `he-deepen-spec`.
7. If source material is unclear or incomplete, run a lightweight planning bootstrap to establish enough context without leaving planning mode.
8. Research local patterns and prior learnings before finalizing structure when they materially affect sequencing or risk.
9. Size the plan depth to the work, then decompose into ordered, verifiable tasks with explicit dependencies, tests, and next-stage handoff.

## Validation

- Ensure tasks are actionable and independently verifiable.
- Ensure dependencies, rollback, and risk controls are explicit.
- Ensure the plan uses the most authoritative available source and does not silently drop upstream requirements.
- Ensure any new caller-facing interface needed by the plan is already specified; otherwise stop and route to `he-deepen-spec`.
- Ensure tasks use canonical domain terms from `CONTEXT.md` when one exists, and link Linear decision notes when durable tradeoffs shaped the plan.
- Ensure the chosen route (`fresh`, `resume`, or `deepen`) matches the artifact state.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not produce plan steps that depend on unstated assumptions.
- Do not turn planning into implementation, test execution, or speculative debugging.
- Do not silently convert true product blockers into technical assumptions.
- Do not create ADRs; use Linear issues or comments for durable decision capture.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Producing abstract plans without executable task boundaries.
- Omitting verification intent for critical tasks.
- Planning implementation tasks around an interface that has not been designed.
- Decomposing tasks around ambiguous project terms that should have been resolved upstream.
- Replanning from scratch when a relevant current plan or requirements doc should be updated in place.
- Routing directly to execution when the request is still asking for planning.

## Examples

- "When the user asks, `Turn this approved spec into an execution-ready implementation plan with phases, tests, and rollout guidance.`"
- "Please plan this production bug fix from the report and validate the safest execution order."
- "Help me inspect the recent plan and decide whether to resume it, deepen it, or replace it."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
Read when: project terminology, `CONTEXT.md`, or Linear issue wording affects planning readiness.
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.
