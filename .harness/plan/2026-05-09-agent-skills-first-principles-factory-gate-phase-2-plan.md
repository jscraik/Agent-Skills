---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-2-plan
artifact_type: he-plan
canonical_slug: agent-skills-first-principles-factory-gate-phase-2
title: First-Principles Factory Gate Phase 2 Plan
harness_stage: he-plan
status: deepened
date: 2026-05-09
deepened: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-spec.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: deepened-standard
ui: false
---

# First-Principles Factory Gate Phase 2 Plan

## Executive Plan Summary

This plan implements Phase 2 of the first-principles factory gate migration:
add one shared procedural reference for the full gate schema and wire compact
`Read when` / procedure guidance into the factory lanes that actually create,
harden, refactor, skillify, route, or package skills/plugins.

The plan deliberately stops before validator enforcement, factory eval
fixtures, MCP tools, apps, Linear mutation, generated projections, and any
claim that the full factory-gate program is complete.

## Deepening Enhancement Summary

This deepening pass strengthens the plan without changing its Phase 2 intent:

- adds a concrete evidence check for relative reference depth across every
  selected lane;
- narrows the optional `workflow.md` source to evidence-only unless
  implementation finds a contradiction;
- defines the static test contract in stable terms so Phase 2 drift protection
  does not become Phase 3 enforcement;
- aligns the static test schema keys to the Phase 2 spec's minimum
  `first_principles_gate` schema;
- adds a dirty-worktree and scope guard for `he-work`;
- records the exact readiness boundary that must remain open for Phase 3
  validator warning/failure policy and Phase 4 behavior proof.

## Source Evidence

| Source | Evidence Used | Planning Impact |
| --- | --- | --- |
| `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-spec.md` | Defines Phase 2 boundary, schema fields, decisions, candidate lane files, and SA2 acceptance IDs. | Primary execution contract. |
| `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md` | Phase 1 is complete with follow-up; full readiness still needs schema/procedure, validation, and behavior eval proof. | Confirms Phase 2 is next and prevents closure overclaiming. |
| `.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md` | Phase 2 objective is reference schema and factory procedure wiring. | Confirms migration order and rollback posture. |
| `Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md` | Creates or reshapes skills and already collects outcomes, examples, resources, and OpenAI-style design contract fields. | Phase 2 wiring target. |
| `Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md` | Hardens existing skills/plugins and already applies design-contract checks before readiness claims. | Phase 2 wiring target. |
| `Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/SKILL.md` | Recommends keep/improve/merge/retire from evidence. | Phase 2 wiring target for non-build decisions. |
| `Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md` | Converts workflows into durable skills and already warns against one-off transcript capture. | Phase 2 wiring target for repeatability versus `DO_NOT_BUILD`. |
| `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md` | Creates plugin packages and optional surfaces. | Phase 2 wiring target. |
| `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md` | Hardens plugin packages, release claims, and bundled hook validation. | Phase 2 wiring target. |
| `Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md` | Routes broad/mixed plugin requests after the root router. | Phase 2 wiring target for mixed artifact decisions. |
| `Plugins/plugin-factory/skills/plugin-factory-router/references/workflow.md` | Contains compact plugin lane map. | Evidence-only source in Phase 2; edit only if implementation finds the lane map contradicts new `plugin-router` wiring. |

## Synthesis Checkpoint

Known:

- Phase 2 must create the full gate reference and make factory lanes point to
  it.
- The full schema belongs in a reference, not in always-loaded `SKILL.md`
  bodies.
- The highest-value first wiring set is `skill-creator`, `skill-builder`,
  `plugin-creator`, and `plugin-builder`.
- `skill-refactor`, `skillify`, and `plugin-router` are also small enough to
  wire without bloating if each receives one compact bullet or `Read when`
  signpost.

Inferred:

- `Infrastructure/references/first-principles-factory-gate.md` is the best
  shared location because both factory plugins already link to
  `Infrastructure/references/*` contracts and the gate is cross-factory.
- A targeted text assertion is useful because Phase 2 otherwise relies on
  manual diff inspection. It can live in
  `Infrastructure/tests/test_plugin_bundled_hooks_contract.py` only if the
  implementation keeps the test name honest or adds a small new test class for
  factory-gate wiring.
- Phase 2 should not modify package-generation scripts because the spec
  deliberately defers enforcement and output generation semantics to later
  phases.

Must not happen:

- Do not edit `.agents/**`, `.skillsets/**`, runtime mirrors, or user-level
  plugin copies.
- Do not add strict validator failures or factory eval cases.
- Do not make `plugin_hooks` required.
- Do not add optional plugin surfaces because the schema mentions hooks, MCP,
  apps, or evals.
- Do not treat the optional `workflow.md` source as an automatic edit target.
  It remains evidence-only unless the implementation discovers a concrete
  contradiction with the selected lane wiring.

## Deepening Confidence Gaps Resolved

### Relative Link Depth

All seven selected lane entrypoints sit five directories below the repository
root. The planned reference link can therefore use the same relative target in
each lane:

```text
../../../../../Infrastructure/references/first-principles-factory-gate.md
```

Implementation should still verify this with the focused static test, because a
future lane move would break the assumption.

### Static Test Boundary

The focused test is allowed to protect Phase 2 wiring, but it must not judge
whether factory outputs are high quality. It should assert only stable
structure:

- the shared reference file exists;
- all decision values exist exactly as named;
- the schema keys needed by downstream validators exist;
- each selected lane links to `first-principles-factory-gate.md`;
- no generated projection path is part of the asserted file set.

The test should not assert exact paragraphs, examples, heading order, or any
runtime behavior.

Schema-key assertions must use the Phase 2 spec's canonical minimum
`first_principles_gate` shape. Do not mix in exploratory plugin-specific fields
unless a later spec revises the schema.

### Dirty Worktree Guard

The current branch already contains unrelated dirty files outside this Phase 2
plan. `he-work` must inspect `git diff --name-only` before editing and limit
source changes to the Phase 2 file contract unless a directly blocking
contradiction is found. Unrelated dirty files must be left intact.

### Readiness Boundary

Phase 2 can claim procedure availability only. It cannot claim:

- gate enforcement;
- validator coverage;
- generated package behavior;
- behavior-changing eval proof;
- bundled hook runtime enforcement.

Those claims remain blocked until Phase 3 and Phase 4.

## Planning Decisions

### Decision 1: Shared Infrastructure Reference

Create `Infrastructure/references/first-principles-factory-gate.md`.

Reason: the gate applies to both factory plugins and should not belong to only
one plugin's reference tree.

### Decision 2: Wire Seven Lane Entrypoints, Not Scripts

Wire these `SKILL.md` entrypoints:

- `skill-creator`
- `skill-builder`
- `skill-refactor`
- `skillify`
- `plugin-creator`
- `plugin-builder`
- `plugin-router`

Reason: those are the lanes that make or route artifact decisions. Script and
template changes would imply Phase 3 enforcement or scaffold behavior changes.

### Decision 3: Keep Root Routers Stable

Do not change the two root routers unless implementation finds a broken link or
contradiction. Phase 1 already added compact root-router gates.

### Decision 4: Use One Focused Wiring Test

Add a small static test that checks the shared reference contains the required
schema/decision terms and the selected lane files reference it. This is not
validator enforcement; it is drift protection for Phase 2 wiring.

## Scope

In scope:

- shared reference document;
- seven compact factory lane entrypoint edits;
- one focused static wiring test;
- artifact lints, diff check, focused pytest, and changed-file
  authoring-family validation.

Out of scope:

- validators;
- eval fixtures;
- generator scripts;
- plugin creator/builder Python behavior;
- hook config changes;
- MCP/app surfaces;
- generated projections;
- Linear mutation.

## File-Level Change Contract

### Shared Reference

Create:

- `Infrastructure/references/first-principles-factory-gate.md`

The reference must include:

- purpose and trigger;
- all decision values;
- full YAML schema;
- concise field meanings;
- required output/handoff snippet;
- examples for `BUILD_SKILL`, `BUILD_PLUGIN`, `ADD_HOOK`, `ADD_EVAL`,
  `IMPROVE_EXISTING`, `DOCS_ONLY`, and `DO_NOT_BUILD`;
- warnings that the gate exists to reduce surface area, not justify new
  surfaces;
- Phase boundary note: Phase 2 defines procedure, Phase 3 enforces, Phase 4
  proves behavior.

Keep it procedural. Avoid article-like philosophy.

### Lane Wiring

Each selected lane should add no more than one compact paragraph or two bullets.

Required phrase:

```text
Read when: choosing whether the requested factory work should build a new
artifact, improve an existing one, stay docs-only, or stop: [First-principles
factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).
```

Adjust relative depth per file location.

Required behavior statement:

```text
For non-trivial factory work, include `first_principles_gate` or an explicit
`first_principles_gate_status: not_applicable` with the reason in the output or
handoff before claiming readiness.
```

Use shorter wording where the lane body is already dense.

### Focused Static Test

Preferred location:

- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Add a test named for factory gate wiring, not hook runtime, if using that file.
The test should assert:

- shared reference exists;
- reference contains all nine decision values;
- reference contains schema field names;
- each selected lane `SKILL.md` references
  `first-principles-factory-gate.md`;
- no generated projection path is required.

Do not assert exact prose beyond stable filenames, decision values, and schema
keys.

Recommended stable assertion lists:

```python
FACTORY_GATE_DECISIONS = {
    "BUILD_SKILL",
    "BUILD_PLUGIN",
    "ADD_HOOK",
    "ADD_MCP_TOOL",
    "ADD_APP",
    "ADD_EVAL",
    "IMPROVE_EXISTING",
    "DOCS_ONLY",
    "DO_NOT_BUILD",
}

FACTORY_GATE_SCHEMA_KEYS = {
    "desired_outcome",
    "user_specific_constraints",
    "copied_assumption_rejected",
    "fundamental_constraints",
    "smallest_effective_mechanism",
    "artifact_decision",
    "rejected_alternatives",
    "evidence_required",
    "validation_proof",
    "stop_or_pivot_condition",
}
```

This is intentionally broader than a hook-only test and should use a test name
that says `factory_gate` so future maintainers do not mistake it for hook
runtime coverage.

## Implementation Units

### PU2-001: Add Shared Factory Gate Reference

Objective: define the full reusable gate procedure in one shared reference.

Edit:

- `Infrastructure/references/first-principles-factory-gate.md`

Acceptance IDs:

- `SA2-001`
- `SA2-002`
- `SA2-003`
- `SA2-007`
- `SA2-009`

Validation:

- diff inspection;
- focused static test after `PU2-003`.

Rollback:

- delete the new reference and remove lane links.

### PU2-002: Wire Factory Lane Entrypoints

Objective: make selected factory lanes load the shared gate when non-trivial
artifact decisions are in scope.

Edit:

- `Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md`
- `Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md`
- `Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/SKILL.md`
- `Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md`
- `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md`
- `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md`
- `Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md`

Acceptance IDs:

- `SA2-004`
- `SA2-005`
- `SA2-006`
- `SA2-007`
- `SA2-008`

Validation:

- diff inspection for compactness;
- authoring-family changed-file validation after all edits.
- focused link check confirms each lane points to the shared reference.

Review emphasis:

- The full YAML schema must not be copied into any lane `SKILL.md`.
- Each lane should keep its existing job description, trigger language, and
  validation expectations.
- The wiring should add decision pressure, not a new standalone procedure that
  competes with the lane's current workflow.

Rollback:

- remove only the compact reference wiring lines.

### PU2-003: Add Focused Wiring Test

Objective: guard the new reference and selected lane links without adding
validation enforcement.

Edit:

- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Acceptance IDs:

- `SA2-001`
- `SA2-002`
- `SA2-003`
- `SA2-004`
- `SA2-005`
- `SA2-008`

Validation:

- `python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q`

Rollback:

- remove the focused static test.

### PU2-004: Validate And Record Scope

Objective: prove Phase 2 and record any blocked gates.

Commands:

```bash
python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check

bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Infrastructure/references/first-principles-factory-gate.md \
  Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md \
  Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md \
  Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/SKILL.md \
  Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md \
  Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md \
  Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md \
  Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

Acceptance IDs:

- `SA2-008`
- `SA2-010`

Rollback:

- if focused tests fail, fix the smallest test/reference mismatch;
- if authoring-family validation fails on unrelated dirty HE files, record the
  exact blocker and do not broaden Phase 2 scope without a separate decision.

## Dependency Order

| Order | Unit | Depends on | Can run in parallel |
| --- | --- | --- | --- |
| 1 | `PU2-001` | Phase 2 spec | no |
| 2 | `PU2-002` | `PU2-001` reference path | partly |
| 3 | `PU2-003` | `PU2-001`, `PU2-002` | no |
| 4 | `PU2-004` | all edits | no |

## Verification Scenarios

Scenario 1: shared reference is complete.

- Inspect `Infrastructure/references/first-principles-factory-gate.md`.
- Confirm all schema fields and all nine decision values exist.
- Confirm examples include build and non-build outcomes.

Scenario 2: factory lanes can find the reference.

- Run the focused wiring test.
- Confirm all seven selected lane entrypoints reference
  `first-principles-factory-gate.md`.

Scenario 3: Phase 2 does not become enforcement.

- Inspect `git diff --name-only`.
- Confirm no validator scripts, eval fixtures, package-generation scripts,
  generated projections, MCP/app files, or hook configs changed.

Scenario 4: progressive disclosure holds.

- Inspect lane diffs.
- Confirm the full YAML schema appears only in the shared reference, not in
  lane `SKILL.md` bodies.

## Plan Acceptance Traceability

| Spec ID | Plan units | Evidence |
| --- | --- | --- |
| `SA2-001` | `PU2-001`, `PU2-003` | reference diff and focused test |
| `SA2-002` | `PU2-001`, `PU2-003` | decision value assertions |
| `SA2-003` | `PU2-001`, `PU2-003` | schema field assertions |
| `SA2-004` | `PU2-002`, `PU2-003` | skill-factory lane link assertions |
| `SA2-005` | `PU2-002`, `PU2-003` | plugin-factory lane link assertions |
| `SA2-006` | `PU2-002`, `PU2-004` | lane diff inspection |
| `SA2-007` | `PU2-001`, `PU2-002` | non-build decision text |
| `SA2-008` | `PU2-004` | diff scope inspection |
| `SA2-009` | `PU2-001`, `PU2-004` | advisory hook compatibility text |
| `SA2-010` | `PU2-004` | spec and plan artifact validation |

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Lane bodies grow too much | Keep only one signpost and one output rule per lane. |
| Shared reference becomes philosophical | Keep sections procedural: purpose, schema, decisions, examples, output. |
| Phase 2 accidentally changes factory output behavior | Do not edit generation scripts or validators. |
| Static test becomes brittle | Assert stable filenames, decision values, and schema keys only. |
| Static test schema drifts from the spec | Assert the exact Phase 2 minimum schema keys: `desired_outcome`, `user_specific_constraints`, `copied_assumption_rejected`, `fundamental_constraints`, `smallest_effective_mechanism`, `artifact_decision`, `rejected_alternatives`, `evidence_required`, `validation_proof`, and `stop_or_pivot_condition`. |
| Authoring-family validation trips on unrelated dirty work | Record exact blocker and do not repair unrelated files unless required for the changed-file gate. |
| Hooks are treated as live enforcement | Reference states hooks remain advisory until later validation/eval proof. |
| Relative links are copied incorrectly | Use the five-level relative link for the selected lanes and prove it in the focused static test. |
| Review scope drifts into unrelated dirty files | Inspect changed files before editing; preserve unrelated work and mention any blocker explicitly. |

## Review Checklist For `he-work` Closeout

- Confirm exactly one shared reference was added.
- Confirm full schema appears in the shared reference, not lane entrypoints.
- Confirm selected lane entrypoints link to the shared reference.
- Confirm no generated projection directories changed.
- Confirm no validator, eval fixture, MCP/app, or hook config changed.
- Confirm focused wiring test passes.
- Confirm authoring-family changed-file validation passes or records an exact
  unrelated blocker.
- Confirm closeout states Phase 3 and Phase 4 are still required for
  enforcement and behavior proof.
- Confirm the technical review artifact for this plan has no blocking findings
  or that any blocking finding was fixed before implementation.

## Open Questions Handling

Resolved in this plan:

- Shared reference location: `Infrastructure/references/`.
- Initial lane set: seven selected lanes, because each edit is a compact
  signpost and covers the Phase 2 acceptance matrix.
- Output requirement: non-trivial factory outputs should include the full
  `first_principles_gate`; audit-only paths may explicitly report
  `first_principles_gate_status: not_applicable`.

Deferred:

- Whether Phase 3 starts warning-only or strict.
- Whether Phase 4 uses plugin-eval, authoring-family benchmark cases, or both.
- Whether future MCP/app surfaces are useful after behavior proof exists.
- Whether the static wiring test should move into a dedicated factory-gate test
  file if more gate tests are added after Phase 2.

Non-question:

- `workflow.md` is not a default Phase 2 edit target. Treat it as source
  evidence unless implementation exposes a contradiction.

## Rollback Strategy

Rollback is text-local:

1. Remove the focused wiring test.
2. Remove lane reference wiring lines.
3. Delete `Infrastructure/references/first-principles-factory-gate.md`.
4. Rerun focused pytest, `git diff --check`, and changed-file
   authoring-family validation.

No data migration, Linear rollback, projection rollback, hook rollback, or
external rollback is expected.

## Validation Plan

Primary validation:

```bash
python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check
```

Secondary validation:

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Infrastructure/references/first-principles-factory-gate.md \
  Plugins/skill-factory/skills/scaffolding_templates/skill-creator/SKILL.md \
  Plugins/skill-factory/skills/code_quality_review/skill-builder/SKILL.md \
  Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/SKILL.md \
  Plugins/skill-factory/skills/scaffolding_templates/skillify/SKILL.md \
  Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md \
  Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md \
  Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

Plan artifact validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py \
  .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-plan.md

python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py \
  .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-plan.md
```

## Completion Definition

Phase 2 implementation is complete only when:

- `PU2-001` through `PU2-004` are complete;
- focused wiring test passes;
- changed-file authoring-family validation passes or records an exact unrelated
  blocker;
- `SA2-001` through `SA2-010` are explicitly accounted for;
- no Phase 3 validator or Phase 4 eval files were edited;
- closeout states that full factory-gate readiness remains blocked until
  enforcement and behavior-changing eval proof exist.

## Post-Plan Handoff

```yaml
post_plan_handoff:
  state: ready_for_technical_review
  selected_next_stage: he-work
  evidence: ".harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-plan.md"
  required_before_he_work:
    - ".harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-plan-technical-review.md"
  next_action: "After technical review, implement Phase 2 only: shared reference, compact lane wiring, focused wiring test, and validation."
```

The next stage mutates source files, so execution should proceed only when the
technical review is complete and the user authorizes `he-work` or plainly asks
to implement this plan.
