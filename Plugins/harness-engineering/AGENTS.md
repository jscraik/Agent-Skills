---
schema_version: 1
---

# Harness Engineering Plugin Agent Guide

These instructions apply to the canonical Harness Engineering plugin source
under `Plugins/harness-engineering/**`.

## Scope

`Plugins/harness-engineering` owns the shipped HE plugin: stage skills,
references, validation scripts, plugin metadata, and product documentation. HE
is a harness layer for routing, state recovery, validation evidence, closure
proof, and learned-problem capture. Keep it narrow; do not turn it into a
general productivity toolkit.

## Runtime Contract

Authoring guidance is not runtime behavior. If an installed agent must follow a
rule, put that rule in a shipped `SKILL.md`, reference file, script, generated
contract, or plugin manifest. Do not rely on this `AGENTS.md` alone for runtime
behavior.

When runtime behavior differs from source, check these surfaces before changing
skill logic:

1. canonical source: `Plugins/harness-engineering/**`
2. command-surface handles: `.skillsets/command-surface.json` entries for `he-*`
3. plugin runtime/cache mirrors: `Plugins/cache/**` and local plugin runtime
   copies
4. generated route, deferred-context, and authority artifacts

## Path Ownership

- Edit canonical plugin source under `Plugins/harness-engineering/**`.
- Do not hand-edit `.agents/**`, `.skillsets/**`, `Plugins/cache/**`, or other
  runtime projections.
- Do not create review-only media inside this plugin. Put review media under
  repository `.harness/media/**`.
- Keep `.harness/**` cognition and evidence artifacts outside the plugin unless
  the artifact is an intentional reusable plugin fixture.

## Skill Design

- Use hard rules for deterministic safety: canonical source ownership,
  external writes, destructive actions, closure proof, tracker mutation, secret
  handling, and generated projection boundaries.
- Use compact guidance for judgment calls. Avoid turning stage skills into
  long controller prompts.
- Keep always-loaded `SKILL.md` files trigger-focused and move bulky examples,
  matrices, rubrics, and extended rationale into references.
- Do not preserve stale, duplicated, unsafe, inappropriate, or superseded text
  merely because a `SKILL.md` became shorter. Removed context should be
  classified as moved, superseded, intentionally discarded, or not-context.
- Preserve validator-required headings and compatibility aliases when local
  validators still require them.
- Split independent decisions into sequential questions. Do not ask one broad
  confirmation question when the blocker is stage, authority, tracker freshness,
  validation freshness, or closure eligibility.

## Artifact Discipline

Durable HE artifacts should contain decisions, evidence, command outcomes,
blockers, route previews, validation status, rollback notes, and handoffs.
Avoid process exhaust: chatty narration, duplicated lifecycle boilerplate,
irrelevant logs, unsupported confidence, and speculation that is not needed for
replay or audit.

Linear is execution state; `.harness` is cognition and proof. A local artifact
does not mean a live Linear issue, tracker mutation, or closure action occurred.
Always report live mutation status explicitly.

## Product Surface

Keep user-facing HE language plain:

- "Where is this work?"
- "I have a rough idea."
- "Make this buildable."
- "Is this safe to close?"
- "Capture what we learned."

Stage names are allowed as the routed result, not as a prerequisite for human
use. Product copy must keep HE's core value visible: preventing local-only
progress from masquerading as done.

## Validation

Prefer the smallest matching gate and record exact `pass`, `fail`, or
`blocked` outcomes.

Core checks:

```bash
python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py Plugins/harness-engineering --json
python3 Plugins/harness-engineering/scripts/validate_routing_map.py Plugins/harness-engineering --json
python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py Plugins/harness-engineering/references/deferred-context-index.md --json
```

Plugin checks:

```bash
python3 Plugins/plugin-factory/scripts/plugin-builder/plugin_builder.py validate Plugins/harness-engineering --require-marketplace --marketplace-path .agents/Plugins/marketplace.json
python3 Plugins/plugin-factory/scripts/plugin-builder/plugin_builder.py audit-marketplace --marketplace-path .agents/Plugins/marketplace.json --plugins-path Plugins
```

Skill checks:

```bash
./bin/ask skills audit Plugins/harness-engineering/skills/<skill> --level strict --json
```

Run broader lifecycle release evals only when the local runner prerequisites are
healthy. Mark tool, auth, runtime, or quota blockers explicitly instead of
converting them into skill failures.

## Handoff Rules

- Use `he-reconcile` for stage selection and authority limits.
- Use `he-reframe` for staged migration programs.
- Use `he-linear-plan` for Linear-ready tracking plans and mutation status.
- Use `he-eval-report` for closure proof.
- Use Skill Factory or Plugin Factory when the work is about generic skill or
  plugin authoring mechanics rather than HE's lifecycle contract.
- Stop for human confirmation before broad rewrites, destructive actions,
  production/external writes, credential access, tracker mutation, or ambiguous
  source/runtime ownership.

## Linear issue template policy for `he-linear-plan`

- Treat repo identity as a label, not a project. Prefer `Repo › ...` labels and
  allow legacy plain repo labels only until migrated.
- Use projects only for bounded deliverables with a clear completion state; do
  not create repo-container projects.
- Use cycles only for work actively being committed to now.
- Prefer labels and views for repo queues, maintenance, triage, backlog, and
  operational filtering.
- Apply the following non-triage template mapping when creating or editing issues:
  - Bug -> Type > Bug
  - Feature -> Type > Feature + Roadmap > Roadmap: Next
  - Research -> Type > Research + Roadmap > Roadmap: Next
  - Release -> Release + Reliability + Type > Docs + Roadmap > Roadmap: Now
  - Governance / Policy -> Policy + Governance + Type > Docs + Roadmap > Roadmap: Next
- Use exactly one Type label and exactly one Roadmap label on every non-triage issue.
- Domain labels must not replace Type labels.
- Release is not a Type label.
- If this is unclear, leave it in Triage and ask.
- Always prefer updating an existing issue over creating a duplicate.
- Keep GitHub as the implementation and review surface, but keep Linear as the
  source of truth for issue structure, grouping, active commitment, and workflow
  state.
- Do not treat merged PRs as shipped evidence; use Linear Releases when
  available, otherwise use tag, deployment, changelog, package, or manual
  release evidence.
