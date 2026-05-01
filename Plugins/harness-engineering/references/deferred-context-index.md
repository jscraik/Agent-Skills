# Harness Engineering Deferred Context Index

This runtime index keeps the active Harness Engineering plugin package compact while preserving traceability to deferred context.

Active Harness Engineering entrypoints and references must be real plugin-owned files. `fixtures/budget-archive/**` is historical input only; active plugin paths must not symlink into it.

Use this index when a compact stage skill says context was moved for budget reasons.

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
