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
