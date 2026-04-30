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
- Use when multiple related Linear QA issues need dependency ordering, blocker handling, or parallelization decisions.

## Inputs

- Source spec, brainstorm output, or defect scope.
- Optional related Linear QA issues and their blocker relationships.
- Constraints, dependencies, and risk/compliance requirements.
- Optional existing plan path to update or deepen.
- Optional requirements document or recent planning artifact that should be treated as the primary source.

## Outputs

- Ordered implementation plan with validation intent per task.
- Ordered Linear QA issue execution sequence, with blocker-first work and independent issues marked parallelizable.
- Explicit blockers, assumptions, and next-stage recommendation.
- Domain-readiness decision that confirms canonical terms are stable or routes back upstream.
- Explicit plan route: `fresh`, `resume`, or `deepen`.
- Plan depth sized to the work: `lightweight`, `standard`, or `deep`.
- Required artifact frontmatter, including `schema_version`, governing source path, plan route, and plan depth when writing a plan file.
- Traceability from source requirements, spec `SA` IDs, invariants, or UI `VAC` criteria to plan acceptance items.
- Stable implementation phase IDs (`P` or `UP`) and acceptance IDs (`AC` or `UAC`) that `he-work` can execute without reinterpreting scope.
- Execution checkpoints, rollback/recovery notes, and a validation ladder for non-trivial plans.
- Execution Ledger guidance with exactly one actionable first step ready for handoff.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Resolve the best planning source first: existing plan, requirements doc, spec, brainstorm output, or direct request.
2. If a matching recent plan already exists, decide whether to resume, deepen, or start a fresh plan instead of duplicating it.
3. Treat the most authoritative source artifact as primary input and carry forward its problem frame, scope, requirements, and open questions.
4. Check interface readiness before task decomposition. If the work depends on a new module, API, CLI, plugin, tool, service, data-access, or shared-helper boundary, confirm the source defines the caller-facing contract.
5. If the interface contract is missing or only implied, route back to `he-deepen-spec` instead of burying interface design inside implementation tasks.
6. Check domain readiness: if core terms, relationships, or `CONTEXT.md` updates are missing, route back to `he-brainstorm` or `he-deepen-spec`.
7. If the source is a set of Linear QA issues, put blockers first, preserve issue links, and mark independent defects as parallel work instead of merging them into one broad task.
8. If source material is unclear or incomplete, run a lightweight planning bootstrap to establish enough context without leaving planning mode.
9. Research local patterns and prior learnings before finalizing structure when they materially affect sequencing or risk.
10. Size the plan depth to the work, then decompose into ordered, verifiable tasks with explicit dependencies, tests, and next-stage handoff.
11. For source specs with stable `SA` or `VAC` IDs, build a traceability matrix that maps each source acceptance item to one or more plan acceptance items.
12. For high-risk, multi-phase, CLI/API/plugin/service, persistence, or governance work, add execution checkpoints with stop conditions before downstream units depend on unproven seams.
13. For each feature-bearing implementation unit, name expected production files, test files, requirements, dependencies, validation intent, completion criteria, and rollback guidance.
14. Add a validation ladder that starts with focused checks and widens only after the narrow behavior path is proven; include blocked-step reporting when a command cannot run.
15. Before handoff, verify the plan artifact against the selected mode, initialize the Execution Ledger, and keep exactly one actionable next step ready for `he-work`.

## Validation

- Ensure tasks are actionable and independently verifiable.
- Ensure dependencies, rollback, and risk controls are explicit.
- Ensure the plan uses the most authoritative available source and does not silently drop upstream requirements.
- Ensure any new caller-facing interface needed by the plan is already specified; otherwise stop and route to `he-deepen-spec`.
- Ensure tasks use canonical domain terms from `CONTEXT.md` when one exists, and link Linear decision notes when durable tradeoffs shaped the plan.
- Ensure the chosen route (`fresh`, `resume`, or `deepen`) matches the artifact state.
- Ensure written plan frontmatter includes `schema_version`, route, depth, and governing source links when applicable.
- Ensure stable `P` / `AC` or `UP` / `UAC` identifiers are present and traceable to source requirements.
- Ensure implementation units include concrete files, test files, dependencies, exit criteria, rollback guidance, and validation intent when the unit is feature-bearing.
- Ensure high-risk plans include checkpoints, stop conditions, rollout or recovery notes, and an explicit validation ladder.
- Ensure the Execution Ledger exists for written plans and has no more than one `in_progress` item.
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
- Producing a task list that lacks source traceability, checkpoint gates, rollback notes, or focused-to-broad validation.

## Examples

- "When the user asks, `Turn this approved spec into an execution-ready implementation plan with phases, tests, and rollout guidance.`"
- "Please plan this production bug fix from the report and validate the safest execution order."
- "Help me inspect the recent plan and decide whether to resume it, deepen it, or replace it."
- "Can you sequence these related Linear QA issues so blockers are fixed first and independent defects can move in parallel?"

## Full Context

- Full plan guide: [repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/SKILL.full.md](repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/SKILL.full.md)
- Plan artifact contract: [repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/plan-artifacts.md](repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/plan-artifacts.md)
- Verification-first planning: [repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/verification-first.md](repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/verification-first.md)
- Production and rollout controls: [repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/production-considerations.md](repo:Plugins/harness-engineering/fixtures/preserved-context/skills/team_automation/he-plan/references/production-considerations.md)
- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
- QA intake routing: [../../../references/qa-intake-routing.md](../../../references/qa-intake-routing.md)
Read when: project terminology, `CONTEXT.md`, or Linear issue wording affects planning readiness.
Read when: planning from multiple Linear QA issues, especially when blocker order or parallel fix lanes matter.
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, route to [codex-agent-creator](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) and provide the exact role names to create or install.