# Harness Engineering Plugin

`harness-engineering` is the lifecycle plugin for shaping, specifying, planning, implementing, reviewing, improving, and monitoring work. It is not the `@brainwav/coding-harness` infrastructure toolchain.

## Active Skills

- `he-router`
- `he-brainstorm`
- `he-spec`
- `he-plan`
- `he-work`
- `he-code-review`
- `he-fix-bugs`
- `he-improve`
- `he-compound`
- `he-heartbeat`

## Routing

Start with `he-router` when the stage is unclear. Direct stage calls are fine when the user names an active skill. Folded legacy names are aliases or modes, not packaged skills:

- `he-ideate` -> `he-brainstorm`
- `he-deepen-spec` -> `he-spec`
- `he-deepen-plan` -> `he-plan`
- `he-tdd` -> `he-work`
- `he-technical-review` / `he-reliability-review` -> `he-code-review`
- `he-refine` -> `he-improve`
- `he-compound-refresh` -> `he-compound`
- `he-prune-branches` -> `he-router` branch-hygiene handoff

Source of truth:

- `Plugins/harness-engineering/references/routing-map.json`
- `Plugins/harness-engineering/references/deterministic-stage-routing.md`
- `Plugins/harness-engineering/references/subagent-routing.md`

## Traceability

Tracked work should carry the same Linear/spec/plan/PR chain through brainstorm, spec, plan, work, and review. Non-trivial tracked work must resolve or create the Linear issue through `references/linear-tracker-gate.md`; blocked tracker writes must return a ready-to-create payload instead of silently continuing.

## Agent-Native Compression

When HE work touches a cockpit, command catalog, README front door, default help,
or golden-path command, use `references/agent-native-compression-contract.md`.
Compression is a blocking product gate: visible surfaces must be selected by the
golden path, emitted in readiness/learning packets, hidden as plumbing, merged,
deprecated, or explicitly justified. Metadata and classification alone do not
count as compression.

## Goal Continuity

Use Codex `/goal` for explicit long-running continuation only. A goal preserves the thread objective across resumes; it does not replace Linear, specs, plans, PRs, validation, or the HE lifecycle exit contract. See `references/goal-continuity.md`; hand off repo-visible goal boards, native-goal reconciliation, receipts, and worker scope checks to the independent `Skills/agent-ops/goal-governor` skill.

## Validation

Validate plugin contract and marketplace registration:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate Plugins/harness-engineering --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
```

Audit marketplace alignment:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/Plugins/marketplace.json --plugins-path Plugins
```
