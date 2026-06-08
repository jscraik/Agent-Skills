# SynAIpse Harness Plugin

`synaipse-harness` is the compact SynAIpse lifecycle plugin. It chooses one next stage, records authority limits, and hands off through the core `sy-*` command-surface handles.

Plugin metadata points local plugin information links at this README so the
picker has a durable operator-facing reference.

It is not the `@brainwav/coding-harness` infrastructure toolchain.

## Reader Map

- [Command-Facing Skills](#command-facing-skills)
- [Lifecycle Flow](#lifecycle-flow)
- [Routing](#routing)
- [Traceability](#traceability)
- [Artifact Review Surface](#artifact-review-surface)
- [Agent-Native Compression](#agent-native-compression)
- [Goal Continuity](#goal-continuity)
- [Validation](#validation)

## Command-Facing Skills

Use `sy-strategy` when the stage is unclear. Direct stage work lives behind the core `sy-*` command-surface handles so the package stays cheap, visible, and grep-friendly.

Lifecycle stages are plain English. Skill IDs use `sy-` so the package stays grep-friendly and avoids collisions with generic skills.

| Skill | Reader job |
| --- | --- |
| `sy-strategy` | Decide the route, boundary, architecture, or strategy posture. |
| `sy-reframe` | Turn a failed or stale migration plan into concrete options. |
| `sy-brainstorm` | Explore options before a trace, tracker, spec, or plan is ready. |
| `sy-trace-plan` | Decompose strategy, brainstorm, or reframe output into traceable work. |
| `sy-tracker-plan` | Map trace work into tracker-ready Now/Next/Later slices. |
| `sy-spec` | Write scoped technical specs from approved trace or tracker inputs. |
| `sy-execution-plan` | Sequence implementation, validation, rollback, and evidence work. |
| `sy-work` | Implement an approved spec or execution plan. |
| `sy-review` | Produce severity-ranked review findings and next-stage guidance. |
| `sy-eval-report` | Record closure proof after work, review, and validation. |
| `sy-reconcile` | Recover stale, conflicting, or partially complete lifecycle state. |
| `sy-reinforce` | Capture solved problems and update durable learning surfaces. |

## Lifecycle Flow

Most tracked work follows this shape. The lifecycle separates **trace decomposition** from **per-slice specification** and **execution sequencing**. Skip stages only when the source artifact already proves the missing decision.

```mermaid
flowchart LR
  A["Rough idea or stale state"] --> B["sy-strategy"]
  B --> C["sy-reframe"]
  C --> D["sy-brainstorm"]
  D --> E["sy-trace-plan"]
  E --> F["sy-tracker-plan"]
  F --> G["sy-spec"]
  G --> H["sy-execution-plan"]
  H --> I["sy-work"]
  I --> J["sy-review"]
  J --> K["sy-eval-report"]
  K --> L["sy-reconcile"]
  L --> M["sy-reinforce"]
```

The diagram is a routing aid, not a mandate. Tracker, PR, validation, and artifact evidence decide whether a stage is required or already satisfied.

## Routing

Start with `sy-strategy` when the stage is unclear. Direct stage calls are fine when the user names one of the core handles.

Source of truth:

- `Plugins/synaipse-harness/references/routing-map.json`
- `Plugins/synaipse-harness/references/deterministic-stage-routing.md`
- `Plugins/synaipse-harness/references/stage-arc-boundary-contract.md`

## Traceability

Tracked work should carry the same trace/spec/plan/PR chain through brainstorm, trace planning, tracker planning, slice spec, execution plan, work, and review. Non-trivial tracked work must resolve or create the Linear issue through `references/linear-tracker-gate.md`; blocked tracker writes must return a ready-to-create payload instead of silently continuing.

For existing tracked trace plans or tracker plans, run `references/linear-delta-capture-gate.md`
before `sy-spec`, execution `sy-execution-plan`, or `sy-work` consumes
`.harness/linear/<repo-name>-linear-plan.md`. New or changed Linear issues are
captured into the plan as classified deltas first, then at most one admitted
item becomes the current or next execution slice.

Lifecycle state reconciliation belongs to `sy-reconcile`: use it when SynAIpse work
needs earliest-stage recovery, source-prompt coverage, tracker/artifact conflict
resolution, or session-evidence resume routing.

Solved-problem capture and stale learning refresh belong to `sy-reinforce` and write new SynAIpse solution
artifacts under `.harness/solutions/**` using
`references/solution-capture-contract.md`. Legacy `docs/solutions/**` entries
are source evidence and overlap/freshness inputs. When the repo uses Project
Brain, solution capture also syncs or explicitly blocks the matching
`.harness/knowledge/**` update.

Post-implementation closure proof belongs to `sy-eval-report` and writes
`.harness/evals/YYYY-MM-DD-JSC-###-<repo-name>-<linear-parent-issue-or-milestone>-eval.md`
when Linear context is known, or the dated repo fallback when it is not.
Do not recommend Linear parent issue, milestone, project, or execution-slice
closure from implementation status alone; use the eval artifact to record
validation evidence, drift posture, proof artifacts, and completion safety.

Strategy, architectural review, triage, ADR compression, and core invariant
compression belong to `sy-strategy`. These artifacts are cognition context, not
implementation authority, until admitted by a reframe, Linear, spec, or plan
artifact. New lifecycle artifacts prefer dated Linear filenames such as
`YYYY-MM-DD-JSC-###-<slug>-strategy.md`; stable names are reserved for living
`.harness/core/**` files and numbered ADRs.

Artifact classification uses
`references/artifact-classification-and-traceability.md`: content shape beats
path. Frontmatter, H1, required sections, source links, and Linear identifiers
classify existing `.harness` files before directory names. Path/title/date
mismatches are traceability defects, not silent routing assumptions.

High-leverage architectural migration programs belong to `sy-reframe` and
write `.harness/reframes/YYYY-MM-DD-JSC-###-<reframe-slug>.md` when tracked.
They define staged evolution, rollback, eval proof, and Linear mapping without
editing implementation code or creating Linear objects.

Tracker execution mapping belongs to `sy-tracker-plan` and writes
`.harness/linear/YYYY-MM-DD-JSC-###-<repo-name>-<slice-slug>-linear-plan.md`
when tracked.
It maps `.harness` trace bullets into small Now/Next/Later/Do Not Create execution
sets, milestones, parent issues, dependencies, eval gates, and human/agent
routing, but never mutates Linear without explicit confirmation.
Repo identity is carried by labels, preferably `Repo › ...`, while projects are
reserved for bounded deliverables with a clear completion state. Use labels and
views for repo queues, maintenance, triage, and backlog organization; use cycles
only for active execution commitment.

Dedicated UI plans are `sy-execution-plan` artifacts. New UI plans use
`.harness/plan/**-ui-plan.md`; legacy `docs/ui-plan/**` and
`docs/ui-plans/**` paths are compatibility source evidence unless the user asks
to preserve that convention. When Project Brain is active, UI plans feed it as
plan/decision context first; only implementation-proven reusable UI learnings
become `.harness/solutions/**` captures.

## Artifact Review Surface

Durable SynAIpse artifacts should be understandable without reading the originating
chat. Non-trivial specs, plans, reframes, Linear plans, strategies, reconcile
notes, reinforce captures, and eval reports use:

- one opening `BLUF:` paragraph in the command summary, not repeated
  section-level BLUF labels;
- reader-first body sections with explicit requirements, gates, risks,
  decisions, and next action;
- a visual-reference decision when flow, state, dependency, boundary, rollback,
  UI, media, or source-of-truth complexity would be clearer as a Mermaid
  diagram, table, screenshot, or persisted image reference;
- `Not needed` with a reason when no visual lowers review cost.

Mermaid and tables are the default visual references because humans can scan
them and agents can parse them. Generated images are exceptional and require
the repository media path plus proof that the file exists. Review-only media
belongs under repository `.harness/media/**`, not inside this plugin package.

## Agent-Native Compression

When SynAIpse work touches a cockpit, command catalog, README front door, default help,
or golden-path command, use `references/agent-native-compression-contract.md`.
Compression is a blocking product gate: visible surfaces must be selected by the
golden path, emitted in readiness/learning packets, hidden as plumbing, merged,
deprecated, or explicitly justified. Metadata and classification alone do not
count as compression.

When SynAIpse work touches skills, plugins, CLIs, agent docs, evals, routing,
projections, automation, or workflow surfaces, use
`references/agent-native-audit-scorecard.md`. Agent-native readiness must prove
action parity, capability discovery, context ownership, shared truth surfaces,
entity completion, integration feedback, prompt-native composability, and
deterministic completion.

When SynAIpse consumes prior sessions or collector evidence, use
`references/session-evidence-trace-context.md` to resolve repo, branch, PR,
Linear, artifact chain, source bundle, and currentness before drawing scope or
closure conclusions.

When review feedback changes a spec, plan, strategy artifact, Linear plan,
reframe program, or eval, use
`references/document-review-finding-tiers.md` to separate `safe_auto`,
`gated_auto`, `manual`, and `fyi` findings before editing or asking.

## Goal Continuity

Use Codex `/goal` for explicit long-running continuation only. A goal preserves the thread objective across resumes; it does not replace Linear, specs, plans, PRs, validation, or the SynAIpse lifecycle exit contract. See `references/goal-continuity.md`; hand off repo-visible goal boards, native-goal reconciliation, receipts, and worker scope checks to the independent `Skills/agent-ops/goal-governor` skill.

## Validation

Validate plugin contract and marketplace registration:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py validate Plugins/synaipse-harness --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
```

Audit marketplace alignment:

```sh
python3 Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.py audit-marketplace --marketplace-path .agents/Plugins/marketplace.json --plugins-path Plugins
```
