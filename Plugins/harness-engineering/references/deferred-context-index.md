# Harness Engineering Deferred Context Index

This runtime index keeps the active Harness Engineering plugin package compact while preserving traceability to deferred context.

Active Harness Engineering entrypoints and references must be real plugin-owned files. `fixtures/budget-archive/**` is historical input only; active plugin paths must not symlink into it.

Use this index when a compact stage skill says context was moved for budget reasons.

## Progressive Disclosure Move Evidence

Use this skill as normal for the Harness Engineering brainstorm stage.
- Use this skill as normal for the Harness Engineering brainstorm stage.
Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.
Use when requirements, defects, specs, brainstorms, or Linear QA issues need an implementation-ready plan before `he-work`.
description: Write Harness Engineering specs before planning. Use when a feature, QA report, Linear issue, or UI source needs a clear WHAT contract.
- Ship small verified slices.

- `he-brainstorm`: Use this skill as normal for the Harness Engineering brainstorm stage.
- `he-plan`: Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.
- `he-spec`: Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.
- `he-work`: Context preservation: Do not remove important context for budget trimming; move it to references and index it in `Plugins/harness-engineering/references/deferred-context-index.md`.

## Runtime References

- Deterministic stage routing: `references/deterministic-stage-routing.md`
- Domain-model routing: `references/domain-model-routing.md`
- QA intake routing: `references/qa-intake-routing.md`
- Session evidence contract: `references/session-evidence-contract.md`
- Subagent routing policy: `references/subagent-routing.md`
- Machine-readable routing map: `references/routing-map.json`
- Stage-local contracts, evals, and task profiles: each stage `references/` directory

## Router Folded Context

The router procedure now resolves folded stage names before applying the older direct routing steps. These preserved procedure lines remain here as move evidence:

```text
2. Apply the deterministic decision order in [deterministic stage routing](../../references/deterministic-stage-routing.md).
3. Pick exactly one stage from [routing map](../../references/routing-map.json).
If required evidence is missing, return the missing input and the most likely stage with low confidence.
```

## Code Review Preserved Context

The active `he-code-review` entrypoint now keeps the readiness path compact. These preserved lines remain here as move evidence:

```text
- Linked Linear issue, spec, plan, PR body, or branch identifier when the target is tracked delivery work
- Missing traceability is at least `go-with-conditions`; missing issue, missing validation, or mismatched scope is `no-go`.
```

## Plan Preserved Context

The active `he-plan` entrypoint now keeps Codex plan-mode lessons, synthesis rules, deepening, testing, handoff, and visual planning doctrine in:

- `Plugins/harness-engineering/references/he-plan-doctrine.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/codex-plan-mode.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/plan-artifact-contract.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/planning-depth.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/deepening-review.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/test-strategy.md`
- `Plugins/harness-engineering/skills/team_automation/he-plan/references/visual-communication.md`

## Spec Preserved Context

The active `he-spec` entrypoint now keeps Codex collaboration lessons, session evidence intake, source-parity rules, artifact templates, and autoresearch decisions in:

- `Plugins/harness-engineering/references/he-spec-doctrine.md`
- `Plugins/harness-engineering/skills/team_automation/he-spec/references/autoresearch-2026-05-02.md`
- `Plugins/harness-engineering/skills/team_automation/he-spec/references/codex-and-session-evidence.md`
- `Plugins/harness-engineering/skills/team_automation/he-spec/references/spec-artifact-contract.md`
- `Plugins/harness-engineering/skills/team_automation/he-spec/references/spec-mode-rules.md`

## Work Preserved Context

The active `he-work` entrypoint now keeps Codex execution lessons, Harness Engineering work-execution patterns, execution mode rules, and handoff requirements in:

- `Plugins/harness-engineering/skills/team_automation/he-work/references/work-execution-contract.md`
- `Plugins/harness-engineering/skills/team_automation/he-work/references/codex-execution-lessons.md`
- `Plugins/harness-engineering/skills/team_automation/he-work/references/handoff-and-shipping.md`
- `Plugins/harness-engineering/skills/team_automation/he-work/references/execution-modes.md`

## CI Move Evidence

The authoring-family gate compares shortened HE skill bodies against added reference/index content. These exact removed lines are preserved here so compact runtime entries remain traceable to deferred context:

```text
# Progressive Disclosure Entry
This entrypoint stays concise and keeps full operational context in archived references.
- If the request is already concrete enough for planning or direct execution, keep the interaction brief and recommend the next stage instead of forcing a brainstorm.
automation_status: "<created | needs-user-action | blocked>"
description: "Execute a plan, todo list, or tightly scoped spec with traceable progress, validation, contract-drift control, UI execution gates, and optional external delegation. Use when the user wants Harness Engineering work implemented, not just planned."
- `references/review-modes.md`, `references/findings-and-todos.md`, `references/contract.yaml`
| [[gh-workflow]] | GitHub merge readiness |
- start `he-work` (with `[[he-tdd]]` posture if TDD) or hand to `[[gh-workflow]]` for issue creation
- proceed to `he-plan` when the contract is ready for execution sequencing
- issue creation/update via `[[gh-workflow]]` or repo tracker
description: Route ambiguous Harness Engineering requests to one lifecycle stage when users ask where to start, resume, plan, implement, review, debug, schedule a heartbeat, or resolve domain terminology.
5. Emit separate Codex-compatible code review and Harness readiness results.
```

## Remote Merge Move Evidence

The PR merge on 2026-05-02 normalized active router numbering and preserved a historical he-work fixture wording choice. These exact lines are preserved here so the branch-level progressive-disclosure gate can distinguish mechanical merge cleanup from context loss:

```text
Use `he-work` when the user wants implementation of approved Harness Engineering work with traceable progress and validation evidence.
5. Route domain-language conflicts through [domain model routing](../../references/domain-model-routing.md).
6. Route QA or feedback sessions through [QA intake routing](../../references/qa-intake-routing.md).
7. Route prior-session or repeated-failure requests through [session evidence contract](../../references/session-evidence-contract.md).
8. Route coverage-gap and skillify-candidate evidence to `he-improve` for triage before any new skill package is proposed.
```

## Preserved Context

Full historical move evidence and exact removed-line preservation live outside the plugin package budget at:

- `Infrastructure/references/harness-engineering/deferred-context-index.full.md`

Full stage guides and preserved legacy references remain in:

- `fixtures/preserved-context/**`

`fixtures/skill-archive` remains a compatibility alias for older links only.

## Preservation Contract

- Active `SKILL.md` files should remain concise and routing-safe.
- Context trimmed for token budget must be linked here, in stage-local `references/*`, or in `Infrastructure/references/harness-engineering/deferred-context-index.full.md`.
- Do not delete preserved context; move and link it.
