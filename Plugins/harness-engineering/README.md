# Harness Engineering Plugin

`harness-engineering` is the lifecycle plugin for shaping, specifying, planning, implementing, reviewing, improving, and monitoring work. It is not the `@brainwav/coding-harness` infrastructure toolchain.

## Active Skills

- `he-router`
- `he-brainstorm`
- `he-spec`
- `he-plan`
- `he-work`
- `he-code-review`
- `he-eval-report`
- `he-strategy`
- `he-refactor`
- `he-linear-plan`
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

For existing tracked plans, run `references/linear-delta-capture-gate.md`
before `he-spec`, `he-plan`, or `he-work` consumes
`.harness/linear/<repo-name>-linear-plan.md`. New or changed Linear issues are
captured into the plan as classified deltas first, then at most one admitted
item becomes the current or next execution slice.

Solved-problem capture belongs to `he-compound` and writes new HE solution
artifacts under `.harness/solutions/**` using
`references/solution-capture-contract.md`. Legacy `docs/solutions/**` entries
are source evidence and overlap/freshness inputs. When the repo uses Project
Brain, solution capture also syncs or explicitly blocks the matching
`.harness/knowledge/**` update.

Post-implementation closure proof belongs to `he-eval-report` and writes
`.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<linear-parent-issue-or-milestone>-eval.md`
when Linear context is known, or the dated repo fallback when it is not.
Do not recommend Linear parent issue, milestone, project, or execution-slice
closure from implementation status alone; use the eval artifact to record
validation evidence, drift posture, proof artifacts, and completion safety.

Strategy, architectural review, triage, ADR compression, and core invariant
compression belong to `he-strategy`. These artifacts are cognition context, not
implementation authority, until admitted by a refactor, Linear, spec, or plan
artifact. New lifecycle artifacts prefer dated Linear filenames such as
`YYYY-MM-DD-JSC-###-<slug>-strategy.md`; stable names are reserved for living
`.harness/core/**` files and numbered ADRs.

High-leverage architectural migration programs belong to `he-refactor` and
write `.harness/refactors/YYYY-MM-DD-JSC-###-<refactor-slug>.md` when tracked.
They define staged evolution, rollback, eval proof, and Linear mapping without
editing implementation code or creating Linear objects.

Linear execution mapping belongs to `he-linear-plan` and writes
`.harness/linear/YYYY-MM-DD-JSC-###-<repo-name>-<slice-slug>-linear-plan.md`
when tracked.
It maps `.harness` cognition into small Now/Next/Later/Do Not Create execution
sets, milestones, parent issues, dependencies, eval gates, and human/agent
routing, but never mutates Linear without explicit confirmation.

Dedicated UI plans are `he-plan` artifacts. New UI plans use
`.harness/plan/**-ui-plan.md`; legacy `docs/ui-plan/**` and
`docs/ui-plans/**` paths are compatibility source evidence unless the user asks
to preserve that convention. When Project Brain is active, UI plans feed it as
plan/decision context first; only implementation-proven reusable UI learnings
become `.harness/solutions/**` captures.

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
