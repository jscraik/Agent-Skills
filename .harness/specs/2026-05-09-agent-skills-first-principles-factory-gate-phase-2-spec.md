---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-2-spec
artifact_type: he-spec
canonical_slug: agent-skills-first-principles-factory-gate-phase-2
title: First-Principles Factory Gate Phase 2 Spec
status: proposed
date: 2026-05-09
origin: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
harness_stage: he-spec
risk: medium
depth: bounded
ui: false
linear_project: agent-skills
linear_milestone: First-Principles Factory Gate
linear_slice: "[agent-skills] Add factory gate schema and procedure wiring"
linear_status: proposed
traceability_required: false
---

# First-Principles Factory Gate Phase 2 Spec

## Mode Decision

Selected stage: `he-spec`

Selected slice: Phase 2 from
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`:
`Reference Schema And Factory Procedure`.

Slice status: ready for specification after Phase 1 implementation and eval
proof.

Tracker status: ready-to-create Linear plan exists; no Linear mutation has
been performed.

Artifact route status: pass; durable spec belongs under `.harness/specs/`.

Linear delta status: not applicable; no live Linear objects were inspected or
mutated in this stage.

## Problem

Phase 1 made the first-principles factory gate visible in the two factory
routers and bundled `SessionStart` hook context. That makes the idea available
to agents, but it does not yet define the reusable schema or procedure contract
that factory lanes should use when they create, harden, refactor, or package
skills and plugins.

Without Phase 2, later validation has nothing precise to check. The factories
could mention "first principles" while still producing vague, copied, or
overbuilt artifacts because the full decision record is not defined anywhere
durable.

## Goals

- Add one shared first-principles factory-gate reference that contains the full
  schema, decision values, examples, and completion rules.
- Wire the reference into the factory lanes that perform create, harden,
  refactor, or package-design work.
- Keep always-loaded `SKILL.md` changes compact and procedural.
- Preserve Phase 1's advisory/enforcement split: Phase 2 defines and wires the
  procedure, but does not add validator failures or eval fixtures.
- Make later Phase 3 validation possible by giving generated or hardened
  factory outputs a stable gate evidence shape.

## Non-Goals

- Do not add deterministic validator enforcement.
- Do not add factory eval fixtures.
- Do not change `plugin_builder.pyw`, `create_basic_plugin.pyw`, or factory
  scaffold templates unless a Phase 2 plan later proves a narrow reference path
  update is required.
- Do not add MCP tools, apps, or new plugin surfaces.
- Do not mutate Linear.
- Do not edit generated `.agents/**`, `.skillsets/**`, or runtime projection
  paths.
- Do not make hooks enforce readiness.

## Linear Contract

Source Linear plan:
`.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md`

Selected parent issue payload:
`[agent-skills] Add first-principles gate to Skill and Plugin Factory`

Selected sub-issue payload:
`[agent-skills] Add factory gate schema and procedure wiring`

Priority: `2`

Labels: `Architecture`, `Agent-Native`, `Eval`, `Factory`, `Governance`

Payload status: ready-to-create only. No Linear objects have been created.

## Boundary

In scope:

- one shared reference for the full first-principles gate contract;
- compact reference links or procedure bullets in factory lanes that perform
  create, harden, refactor, or package-design work;
- targeted tests or text assertions that prove the reference exists and the
  selected lane entrypoints point to it;
- artifact lint and changed-file authoring-family validation.

Candidate source paths for Phase 2 planning:

- `Infrastructure/references/first-principles-factory-gate.md`
- `Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md`
- `Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md`
- `Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/SKILL.md`
- `Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md`
- `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md`
- `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md`
- `Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/references/workflow.md`

Out of scope:

- factory runtime projections;
- plugin install/discovery behavior;
- marketplace mutation;
- strict validation;
- eval fixture implementation;
- Phase 3 or Phase 4 closure claims.

## Baseline

Phase 1 baseline:

- `skill-factory-router` and `plugin-factory-router` now include compact
  `First-Principles Gate` sections.
- `session_start_routing.py` and `session_start_contract.py` inject advisory
  gate context and emit `hookSpecificOutput.hookEventName: "SessionStart"`.
- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py` asserts old
  routing/hook fragments plus the compact gate fragments.
- The Phase 1 eval says Phase 1 is complete with follow-up, but full program
  readiness is blocked until later behavior proof exists.

Current lane baseline:

- `skill-creator` already collects user outcome, examples, resource
  boundaries, and OpenAI-style design-contract information before editing.
- `skill-builder` already hardens existing skills with evidence, side-effect
  class, output shape, and validation checks.
- `skill-refactor` already decides keep, improve, merge, or retire from
  evidence but does not use the factory-gate decision vocabulary.
- `skillify` is a likely route for reusable workflow capture and should avoid
  turning every repeated event into a new skill without the gate.
- `plugin-creator` already starts minimal and adds optional surfaces only when
  requested.
- `plugin-builder` already hardens plugin packages and treats bundled hooks as
  executable runtime behavior.
- `plugin-router` already routes mixed plugin intent but does not require the
  full artifact-decision record.

## Domain Model

`first_principles_factory_gate`:

- A durable decision record used before non-trivial factory create, harden,
  refactor, skillify, plugin conversion, or package-design work.

Gate decision:

- One of `BUILD_SKILL`, `BUILD_PLUGIN`, `ADD_HOOK`, `ADD_MCP_TOOL`, `ADD_APP`,
  `ADD_EVAL`, `IMPROVE_EXISTING`, `DOCS_ONLY`, or `DO_NOT_BUILD`.

Minimum schema:

```yaml
first_principles_gate:
  desired_outcome: ""
  user_specific_constraints: []
  copied_assumption_rejected: ""
  fundamental_constraints: []
  smallest_effective_mechanism: ""
  artifact_decision: ""
  rejected_alternatives: []
  evidence_required: []
  validation_proof: []
  stop_or_pivot_condition: ""
```

Field meanings:

- `desired_outcome`: the user-visible result the factory output must improve.
- `user_specific_constraints`: constraints from this repo, user, workflow,
  safety posture, runtime, or audience.
- `copied_assumption_rejected`: the template, habit, or inherited shape the
  factory refuses to copy without proof.
- `fundamental_constraints`: irreducible facts such as side effects, context
  budget, trigger shape, runtime availability, validation surface, and trust
  boundary.
- `smallest_effective_mechanism`: the smallest artifact or change that can
  produce the desired outcome.
- `artifact_decision`: the selected gate decision.
- `rejected_alternatives`: plausible options rejected with reasons.
- `evidence_required`: evidence needed before build or hardening continues.
- `validation_proof`: command, artifact, review, or eval proof required before
  handoff.
- `stop_or_pivot_condition`: condition that should stop, route, or shrink the
  factory work.

## Lifecycle

1. A user asks either factory to create, harden, refactor, route, skillify, or
   package a capability.
2. The root router applies the compact Phase 1 gate and chooses a lane.
3. The selected lane loads the shared first-principles gate reference when work
   is non-trivial, copied from an existing template, crosses plugin/package
   boundaries, adds runtime behavior, or could increase always-loaded context.
4. The lane records the gate decision in its output or handoff before editing
   source files or claiming readiness.
5. `IMPROVE_EXISTING`, `DOCS_ONLY`, and `DO_NOT_BUILD` are valid successful
   outcomes, not failures.
6. Later Phase 3 validators may check for this shape, but Phase 2 only defines
   and wires the procedure.

## Interfaces

Shared reference interface:

- Path should be stable and reachable from both factory plugins. Preferred
  location: `Infrastructure/references/first-principles-factory-gate.md`.
- The reference must include:
  - gate purpose;
  - decision values;
  - YAML schema;
  - field meanings;
  - examples for skill, plugin, hook, eval, improve-existing, docs-only, and
    do-not-build decisions;
  - "do not use this gate to justify more surface area" warning;
  - handoff/output snippet suitable for factory lane responses.
- The reference must stay procedural, not philosophical.

Factory lane interface:

- Lane entrypoints should add a short `Read when` signpost or procedure bullet
  to the shared reference.
- The entrypoint should not paste the full YAML schema.
- The entrypoint should say when the gate is required and where to put the
  decision in output/handoff.
- The entrypoint should preserve existing OpenAI-style design contract and
  agent-native contract language instead of duplicating it.

Recommended lane requirements:

- `skill-creator`: require the gate before creating or reshaping a non-trivial
  skill, adding scripts/assets/agents, or converting workflow notes into a
  reusable skill.
- `skill-builder`: require the gate before release-readiness claims, large
  context moves, or hardening work that might split, merge, or expand a skill.
- `skill-refactor`: use the gate vocabulary for keep/improve/merge/retire
  recommendations and to route `IMPROVE_EXISTING` versus new skill creation.
- `skillify`: require the gate before turning session evidence into a new
  skill; repeated behavior alone is not enough.
- `plugin-creator`: require the gate before adding optional surfaces such as
  child skills, hooks, MCP servers, apps, assets, or evals.
- `plugin-builder`: require the gate before release claims, hook packaging,
  plugin conversion, or child-skill restructuring.
- `plugin-router`: use the gate when mixed plugin intent could route to build,
  hook, MCP/app, eval, install, improve-existing, docs-only, or do-not-build.

Output interface:

- Non-trivial factory outputs should include a `first_principles_gate` block or
  handoff field.
- Audit-only outputs may include `first_principles_gate_status:
  not_applicable` only when the reason is explicit.
- The gate may be abbreviated in chat responses, but durable artifacts and
  handoffs should preserve enough fields for later validation.

## Technical Constraints

- Use markdown/reference files and compact `SKILL.md` wiring only.
- Do not require `plugin_hooks = true` for Phase 2.
- Do not introduce Python validators, schema parsers, or strict failure checks.
- Do not edit generated projections.
- Do not expand factory root routers with the full schema.
- Do not add new dependencies.
- Keep relative links valid from each edited `SKILL.md`.
- Use the existing authoring-family validation wrapper for changed factory
  skill files.

## Invariants

- The gate prevents unnecessary artifact creation; it must not become another
  checklist that justifies all builds.
- The smallest effective mechanism can be an edit to an existing reference,
  validator, eval, hook, or skill; it does not have to be a new skill/plugin.
- Hooks remain advisory context unless a later phase validates runtime behavior
  and fallback proof.
- Phase 2 makes gate evidence recordable; Phase 3 decides enforcement.
- Phase 2 must preserve progressive disclosure by putting long schema/examples
  in references.

## Failure And Recovery

Failure: the shared reference becomes a long essay.

Recovery: reduce it to purpose, schema, decision values, examples, and output
snippet.

Failure: lane entrypoints paste the full schema.

Recovery: move the schema back to the shared reference and leave only a compact
`Read when` signpost.

Failure: the gate duplicates the OpenAI-style design contract without changing
artifact decisions.

Recovery: rewrite around `artifact_decision`, rejected alternatives, and
non-build outcomes.

Failure: implementation drifts into strict validation.

Recovery: stop and route that work to Phase 3.

Failure: optional plugin surfaces are added because the schema mentions them.

Recovery: remove the surface addition; Phase 2 only defines decision evidence.

## Observability

Minimum observable signals:

- Shared reference exists at the agreed path.
- Shared reference includes the schema fields and all decision values.
- Factory lane entrypoints link to the shared reference without pasting the
  full schema.
- At least one skill-factory lane and one plugin-factory lane require the gate
  before non-trivial create/harden/package work.
- No validators, eval fixtures, MCP tools, apps, generated projections, or
  Linear objects are changed.
- Artifact identity and traceability lints pass for this spec.

Expected Phase 2 validation commands:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py \
  .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-spec.md

python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py \
  .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-spec.md

git diff --check
```

Expected implementation validation, to be confirmed in `he-plan`:

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  <changed-factory-skill-files-and-reference>
```

## Acceptance Matrix

| ID | Acceptance criterion | Evidence required |
| --- | --- | --- |
| SA2-001 | A shared first-principles factory-gate reference exists and contains the full schema. | Diff for `Infrastructure/references/first-principles-factory-gate.md`. |
| SA2-002 | The reference defines all gate decisions: `BUILD_SKILL`, `BUILD_PLUGIN`, `ADD_HOOK`, `ADD_MCP_TOOL`, `ADD_APP`, `ADD_EVAL`, `IMPROVE_EXISTING`, `DOCS_ONLY`, `DO_NOT_BUILD`. | Reference diff inspection or targeted text assertion. |
| SA2-003 | The reference explains field meanings, rejected alternatives, validation proof, and stop/pivot conditions. | Reference diff inspection. |
| SA2-004 | Skill Factory create/harden/refactor/skillify lanes can find the reference through compact entrypoint wiring. | Diffs in selected skill-factory lane `SKILL.md` files. |
| SA2-005 | Plugin Factory create/build/route lanes can find the reference through compact entrypoint wiring. | Diffs in selected plugin-factory lane `SKILL.md` files. |
| SA2-006 | Lane entrypoints do not paste the full YAML schema or duplicate long examples. | Diff inspection against progressive-disclosure rule. |
| SA2-007 | Non-build outcomes are treated as valid successful factory outcomes. | Reference text and lane wiring mention `IMPROVE_EXISTING`, `DOCS_ONLY`, or `DO_NOT_BUILD`. |
| SA2-008 | Phase 2 does not add validators, eval fixtures, MCP tools, apps, generated projections, or Linear mutation. | `git diff --name-only` inspection. |
| SA2-009 | Phase 2 remains compatible with Phase 1 hook context and does not require `plugin_hooks` runtime enablement. | No hook config changes required; reference explains hooks remain advisory until later proof. |
| SA2-010 | The spec validates and hands off cleanly to `he-plan`. | Artifact identity and traceability lints pass. |

## Acceptance Traceability

| Linear payload | Spec IDs |
| --- | --- |
| `[agent-skills] Add factory gate schema and procedure wiring` | SA2-001 through SA2-010 |
| Parent issue validation gates | SA2-008, SA2-009, SA2-010 |
| Refactor Phase 2 rollback rules | SA2-006, SA2-008 |

## First Slice

Implement only Phase 2:

1. Add the shared reference.
2. Add compact `Read when` or procedure wiring to the selected factory lane
   entrypoints.
3. Add a targeted text assertion only if the plan identifies an existing
   appropriate test location; otherwise rely on authoring-family validation and
   diff inspection.
4. Validate the spec and changed files.

Stop after Phase 2 validation. Do not implement Phase 3 validator enforcement
or Phase 4 eval fixtures.

## Questions

- Should the shared reference live in `Infrastructure/references/` or under a
  factory-specific shared reference path?
- Should Phase 2 wire all candidate lanes immediately, or start with the
  minimum useful set: `skill-creator`, `skill-builder`, `plugin-creator`, and
  `plugin-builder`?
- Should durable factory outputs require the full schema immediately, or allow
  an abbreviated chat form with full schema required only in artifacts?

These questions should be resolved in `he-plan` before implementation.

## Done

Phase 2 is done when SA2-001 through SA2-010 pass and the implementation
records that full program readiness still depends on Phase 3 validation and
Phase 4 behavior-changing eval proof.

Factory-gate readiness is not done when the schema exists. Readiness is only
safe after validators or evals prove the gate changes factory behavior.

## he-plan Handoff

Recommended next stage: `he-plan`

Selected implementation slice:
`Phase 2: Reference Schema And Factory Procedure`

Use this spec as the bounded implementation authority. Treat Phase 1 eval,
strategy, refactor program, and Linear plan as source evidence only. Do not
admit Phase 3 validation or Phase 4 eval proof into the Phase 2 plan.
