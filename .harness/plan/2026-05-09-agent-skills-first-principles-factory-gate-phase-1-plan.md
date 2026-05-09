---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-1-plan
artifact_type: he-plan
canonical_slug: agent-skills-first-principles-factory-gate-phase-1
title: First-Principles Factory Gate Phase 1 Plan
harness_stage: he-plan
status: proposed
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: standard
ui: false
---

# First-Principles Factory Gate Phase 1 Plan

## Executive Plan Summary

This plan implements Phase 1 of the first-principles factory gate migration:
make the gate visible in the two factory routers, inject the same compact gate
through the existing factory `SessionStart` hooks, and extend focused hook tests
so the new context is guarded.

The plan deliberately stops before schema/procedure wiring, validation
enforcement, eval fixtures, MCP tools, apps, Linear mutation, or generated
runtime projections.

## Source Evidence

| Source | Evidence Used | Planning Impact |
| --- | --- | --- |
| `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md` | Defines selected slice, scope, compact gate wording, `SA-001` through `SA-009`, expected commands, and out-of-scope boundaries. | Primary execution contract. |
| `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-technical-review.md` | Confirms no P0/P1/P2 blockers; records P3 risks for context budget and lack of router behavior tests. | Adds implementation review checks. |
| `.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md` | Selects Phase 1 as the Now slice and defers MCP/app/eval work. | Confirms active set and priority. |
| `.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md` | Defines migration phases and rollback conditions. | Keeps plan scoped to Phase 1. |
| `Plugins/skill-factory/skills/skill-factory-router/SKILL.md` | Current router procedure has lane selection and design-contract handoff but no artifact-selection gate. | Target for `PU-001`. |
| `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md` | Current router deliverables include plugin design checkpoint but no explicit first-principles gate. | Target for `PU-002`. |
| `Plugins/skill-factory/hooks/session_start_routing.py` | Current hook context carries skill lane routing. | Target for `PU-003`; preserve existing context. |
| `Plugins/plugin-factory/hooks/session_start_contract.py` | Current hook context carries bundled hook contract. | Target for `PU-004`; preserve existing context. |
| `Infrastructure/tests/test_plugin_bundled_hooks_contract.py` | Existing tests execute scripts directly and assert hook context fragments. | Target for `PU-005`. |

## Planning Decisions

### Decision 1: Router Text Before Hook Text

Update the routers first so the human-visible decision boundary is the source
of the wording. Hook context should mirror the routers, not invent a separate
gate.

### Decision 2: One Compact Phrase, No Full Schema

Use the spec's compact wording:

```text
Before build work, identify the user outcome, copied assumption, smallest
effective mechanism, artifact decision, and proof needed. Prefer
IMPROVE_EXISTING, DOCS_ONLY, or DO_NOT_BUILD when a new skill/plugin would only
copy a template or increase context load.
```

Do not include the Phase 2 YAML schema in routers or hooks.

### Decision 3: Hooks Stay Advisory

The hook scripts may inject the gate as additional context, but they must not
claim readiness enforcement or imply `plugin_hooks` is enabled everywhere.
Validators and evals own enforcement in later phases.

### Decision 4: Focused Tests Before Broad Gate

Run focused py_compile and pytest first. Run the changed-file authoring-family
gate only after focused tests pass, because broad gates are slower and may
surface unrelated repository warnings.

## Scope

In scope:

- two factory router `SKILL.md` files;
- two factory hook scripts;
- one focused hook contract test file;
- focused validation commands and changed-file authoring-family validation.

Out of scope:

- `plugin_builder.pyw`;
- `create_basic_plugin.pyw`;
- factory scaffolding templates;
- factory reference-schema docs;
- eval fixture files;
- `.agents/**`;
- `.skillsets/**`;
- Linear mutation;
- MCP/app implementation.

## Implementation Units

### PU-001: Add Gate To Skill Factory Router

Objective: make `skill-factory-router` require the compact gate before create,
harden, refactor, or skillify handoff.

Edit:

- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`

Steps:

1. Add a compact `First-Principles Gate` section near the existing procedure or
   validation section.
2. State that create/harden/refactor/skillify decisions must identify user
   outcome, copied assumption, smallest effective mechanism, artifact decision,
   and proof needed.
3. Include explicit non-build decisions: `IMPROVE_EXISTING`, `DOCS_ONLY`,
   `DO_NOT_BUILD`.
4. Preserve read-only router boundaries and existing deterministic decision
   order.

Acceptance IDs:

- `SA-001`
- `SA-006`
- `SA-008`

Validation:

- manual diff inspection against the compact wording;
- no test command specific to router behavior in Phase 1.

Rollback:

- remove only the new compact gate section from this router.

### PU-002: Add Gate To Plugin Factory Router

Objective: make `plugin-factory-router` require the compact gate before plugin
creation, hardening, refactor, or package-design handoff.

Edit:

- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`

Steps:

1. Add compact gate wording near the existing deliverables/design-checkpoint or
   workflow handoff area.
2. State that package work must choose an artifact decision before build work.
3. Preserve plugin-specific design checkpoint language for package boundary,
   hook surface, side effects, install determinism, and eval coverage.
4. Keep the router read-only.

Acceptance IDs:

- `SA-002`
- `SA-006`
- `SA-008`

Validation:

- manual diff inspection against the compact wording;
- no test command specific to router behavior in Phase 1.

Rollback:

- remove only the new compact gate section from this router.

### PU-003: Extend Skill Factory SessionStart Context

Objective: inject the compact gate into `skill-factory` hook context while
preserving lane routing.

Edit:

- `Plugins/skill-factory/hooks/session_start_routing.py`

Steps:

1. Add a short first-principles gate paragraph or bullets to `CONTEXT`.
2. Include the concrete fragments expected by tests:
   `first-principles`, `artifact decision`, `smallest effective mechanism`,
   `IMPROVE_EXISTING`, and `DO_NOT_BUILD`.
3. Preserve existing lane-routing bullets for `skill-creator`,
   `skill-builder`, `skill-installer`, `skill-refactor`, and `skillify`.
4. Do not change JSON output shape.

Acceptance IDs:

- `SA-003`
- `SA-005`
- `SA-008`
- `SA-009`

Validation:

- `python3 -m py_compile Plugins/skill-factory/hooks/session_start_routing.py`
- focused pytest after `PU-005`

Rollback:

- remove the added gate context from `CONTEXT`.

### PU-004: Extend Plugin Factory SessionStart Context

Objective: inject the compact gate into `plugin-factory` hook context while
preserving bundled hook contract context.

Edit:

- `Plugins/plugin-factory/hooks/session_start_contract.py`

Steps:

1. Add a short first-principles gate paragraph or bullets to `CONTEXT`.
2. Include the concrete fragments expected by tests:
   `first-principles`, `artifact decision`, `smallest effective mechanism`,
   `IMPROVE_EXISTING`, and `DO_NOT_BUILD`.
3. Preserve existing hook contract bullets for `hooks/hooks.json`, `timeout`,
   `plugin_hooks`, and `${PLUGIN_ROOT}` / `${PLUGIN_DATA}`.
4. Do not change JSON output shape.

Acceptance IDs:

- `SA-004`
- `SA-005`
- `SA-008`
- `SA-009`

Validation:

- `python3 -m py_compile Plugins/plugin-factory/hooks/session_start_contract.py`
- focused pytest after `PU-005`

Rollback:

- remove the added gate context from `CONTEXT`.

### PU-005: Extend Focused Hook Tests

Objective: assert the new gate context without inventing Phase 2 validation.

Edit:

- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Steps:

1. Extend `test_factory_session_start_scripts_emit_context`.
2. Keep existing fragment checks for plugin hook contract terms and skill
   routing terms.
3. Add expected gate fragments for both scripts:
   - `first-principles`
   - `artifact decision`
   - `smallest effective mechanism`
   - `IMPROVE_EXISTING`
   - `DO_NOT_BUILD`
4. Do not assert the full gate schema.
5. Do not require `plugin_hooks` runtime enablement.

Acceptance IDs:

- `SA-003`
- `SA-004`
- `SA-005`
- `SA-009`

Validation:

- `python3 -m py_compile Infrastructure/tests/test_plugin_bundled_hooks_contract.py`
- `python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q`

Rollback:

- remove the new gate fragments from the test expectations.

### PU-006: Run Focused And Changed-File Validation

Objective: prove Phase 1 without claiming broader readiness.

Commands:

```bash
python3 -m py_compile \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py

python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check

bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Plugins/skill-factory/skills/skill-factory-router/SKILL.md \
  Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

Acceptance IDs:

- `SA-003`
- `SA-004`
- `SA-005`
- `SA-006`
- `SA-007`
- `SA-008`
- `SA-009`

Rollback:

- if focused tests fail, revert the smallest failing unit and rerun the focused
  command;
- if broad authoring-family validation fails for unrelated reasons, record the
  blocker and do not broaden Phase 1 scope.

## Dependency Order

| Order | Unit | Depends on | Can run in parallel |
| --- | --- | --- | --- |
| 1 | `PU-001` | spec approval | no |
| 2 | `PU-002` | spec approval | yes, after `PU-001` wording is settled |
| 3 | `PU-003` | `PU-001` wording | no |
| 4 | `PU-004` | `PU-002` wording | yes, after compact wording is settled |
| 5 | `PU-005` | `PU-003`, `PU-004` | no |
| 6 | `PU-006` | all edit units | no |

## Plan Acceptance Traceability

| Spec ID | Plan units | Evidence |
| --- | --- | --- |
| `SA-001` | `PU-001` | router diff inspection |
| `SA-002` | `PU-002` | router diff inspection |
| `SA-003` | `PU-003`, `PU-005`, `PU-006` | py_compile and focused pytest |
| `SA-004` | `PU-004`, `PU-005`, `PU-006` | py_compile and focused pytest |
| `SA-005` | `PU-005`, `PU-006` | focused pytest asserts gate fragments |
| `SA-006` | `PU-001` through `PU-006` | git diff inspection confirms Phase 1 scope |
| `SA-007` | `PU-006` | closeout records eval artifact remains future closure gate |
| `SA-008` | `PU-001` through `PU-006` | diff inspection confirms advisory/enforcement split |
| `SA-009` | `PU-003`, `PU-004`, `PU-005` | tests assert old context plus new gate context |

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Router text becomes philosophical or too long | Use only the compact gate wording; reject full schema or long examples. |
| Hook context replaces existing domain context | Tests must assert old plugin hook and skill routing fragments remain. |
| Tests overfit to Phase 2 schema | Assert only Phase 1 fragments. |
| Phase 1 drifts into validation/eval enforcement | Keep `plugin_builder.pyw`, eval fixtures, validators, and references out of scope. |
| Broad validation reports unrelated warning | Record exact blocker; do not widen scope to unrelated fixes. |

## Rollback Strategy

Rollback is file-local:

1. Remove new gate section from `skill-factory-router`.
2. Remove new gate section from `plugin-factory-router`.
3. Remove gate bullets from both hook script `CONTEXT` strings.
4. Remove added gate fragment expectations from the focused test.
5. Rerun focused py_compile and pytest to restore baseline.

No data migration, Linear rollback, projection rollback, or external rollback
is expected because Phase 1 does not touch those systems.

## Out-Of-Scope Guardrails

Do not edit:

- `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/scripts/plugin_builder.pyw`
- `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/scripts/create_basic_plugin.pyw`
- factory templates;
- factory eval fixtures;
- `.harness/evals/**`;
- `.agents/**`;
- `.skillsets/**`.

If a test failure appears to require one of these, stop and reclassify the work
as Phase 2, Phase 3, or Phase 4 before editing.

## Validation Plan

Primary validation:

```bash
python3 -m py_compile \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py

python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check
```

Secondary validation:

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Plugins/skill-factory/skills/skill-factory-router/SKILL.md \
  Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

Plan artifact validation:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md
```

## Completion Definition

Phase 1 implementation is complete only when:

- `PU-001` through `PU-006` are complete;
- focused tests pass;
- changed-file authoring-family validation passes or records an exact unrelated
  blocker;
- `SA-001` through `SA-009` are explicitly accounted for;
- no Phase 2, 3, or 4 files were edited;
- closeout states that broader factory-gate readiness remains blocked until
  `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md`
  exists and passes its later eval criteria.

## Post-Plan Handoff

```yaml
post_plan_handoff:
  state: awaiting_user_choice
  selected_next_stage: he-work
  evidence: ".harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md"
  next_action: "Implement Phase 1 only: router checkpoint, hook context, focused tests, and validation."
```

The next stage mutates source files, so execution should proceed only when the
user authorizes `he-work` or plainly asks to implement this plan.
