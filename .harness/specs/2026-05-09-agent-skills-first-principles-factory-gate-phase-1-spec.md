---
schema_version: 1
artifact_id: 2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec
artifact_type: he-spec
canonical_slug: agent-skills-first-principles-factory-gate-phase-1
title: First-Principles Factory Gate Phase 1 Spec
status: proposed
date: 2026-05-09
origin: he-spec
harness_stage: he-spec
risk: medium
depth: bounded
ui: false
linear_project: agent-skills
linear_milestone: First-Principles Factory Gate
linear_slice: "[agent-skills] Add factory first-principles checkpoint to routers and hooks"
linear_status: proposed
traceability_required: false
---

# First-Principles Factory Gate Phase 1 Spec

## Mode Decision

Selected stage: `he-spec`

Selected slice: Phase 1 from
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`:
`Router And Hook Checkpoint`.

Slice status: resolved.

Tracker status: ready-to-create Linear plan exists; no Linear mutation has been
performed.

Artifact route status: pass; durable spec belongs under `.harness/specs/`.

Linear delta status: not applicable; no live Linear objects were inspected or
mutated in this stage.

## Problem

`skill-factory` and `plugin-factory` can currently route and validate package
shape, but Phase 1 must make the first-principles decision visible at the
factory boundary before any broader factory behavior changes are attempted.

Without this slice, later validation and eval work would lack a stable wording
surface to test against. The risk is building the enforcement layer before the
factory entrypoints and hooks agree on what the gate means.

## Goals

- Add compact first-principles checkpoint language to both factory routers.
- Extend both existing factory `SessionStart` hook scripts with the same
  compact checkpoint.
- Keep Phase 1 limited to routing/context injection and focused test updates.
- Preserve valid bundled hook JSON output.
- Prove the hook context includes gate decision terms without claiming full
  factory readiness.

## Non-Goals

- Do not add MCP tools, apps, or new plugin surfaces.
- Do not add the full schema/procedure wiring from Phase 2.
- Do not enforce factory output validation from Phase 3.
- Do not write the closure eval artifact from Phase 4.
- Do not mutate Linear.
- Do not create a standalone first-principles skill.

## Linear Contract

Source Linear plan:
`.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md`

Selected parent issue payload:
`[agent-skills] Add first-principles gate to Skill and Plugin Factory`

Selected sub-issue payload:
`[agent-skills] Add factory first-principles checkpoint to routers and hooks`

Priority: `2`

Labels: `Architecture`, `Agent-Native`, `Eval`, `Factory`, `Governance`

Payload status: ready-to-create only. No Linear objects have been created.

## Boundary

In scope:

- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
- `Plugins/skill-factory/hooks/session_start_routing.py`
- `Plugins/plugin-factory/hooks/session_start_contract.py`
- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Out of scope:

- factory creator/builder implementation changes;
- reference-schema additions;
- validator enforcement;
- eval fixture changes;
- generated runtime projections;
- `.agents/**` command-handle edits;
- Linear mutation.

## Baseline

Current baseline evidence:

- `skill-factory-router` routes to one skill-factory lane and applies the local
  design contract, but it does not yet require an explicit artifact-selection
  gate.
- `plugin-factory-router` names package boundary, bundled hook surface,
  side-effect classes, install determinism, and eval coverage, but it does not
  yet require the gate decision output.
- `session_start_routing.py` injects skill-factory lane context.
- `session_start_contract.py` injects plugin hook contract context.
- `test_plugin_bundled_hooks_contract.py` already checks factory hook manifests,
  scoped commands, and hook script JSON output.

## Domain Model

`first_principles_gate`:

- A compact decision checkpoint that asks whether the requested artifact should
  exist and what smallest mechanism should carry the behavior.

Gate decision:

- One of `BUILD_SKILL`, `BUILD_PLUGIN`, `ADD_HOOK`, `ADD_MCP_TOOL`, `ADD_APP`,
  `ADD_EVAL`, `IMPROVE_EXISTING`, `DOCS_ONLY`, or `DO_NOT_BUILD`.

Phase 1 checkpoint:

- Short router and hook wording that introduces the gate without requiring the
  full schema.

Compact gate wording:

```text
Before build work, identify the user outcome, copied assumption, smallest
effective mechanism, artifact decision, and proof needed. Prefer
IMPROVE_EXISTING, DOCS_ONLY, or DO_NOT_BUILD when a new skill/plugin would only
copy a template or increase context load.
```

This wording is intentionally smaller than the full gate schema. Phase 1 only
creates a shared decision phrase that later phases can formalize.

## Lifecycle

1. A user invokes `skill-factory` or `plugin-factory`.
2. The router sees create, harden, refactor, or package-design work.
3. Before selecting build work, the router requires the compact gate question:
   what is the user outcome, copied assumption, smallest effective mechanism,
   artifact decision, and proof needed?
4. When the factory plugin is active and plugin hooks are enabled, the
   `SessionStart` hook injects the same compact checkpoint as bounded context.
5. Focused tests verify the hook context remains valid JSON and includes the
   checkpoint terms.

## Interfaces

Router interface:

- Adds a short "First-Principles Gate" or equivalent section to each router.
- Requires exactly one artifact decision before create/harden/refactor/package
  work.
- Keeps full schema detail out of the entrypoint.
- Places the gate near existing decision procedure or validation text, not in
  examples only.
- Uses explicit non-build decisions so agents do not interpret the gate as
  "build, but think first."
- Does not change lane ownership or permit the router to perform lane-specific
  implementation.

Router placement guidance:

- In `skill-factory-router`, add the checkpoint after the existing
  OpenAI-style design-contract procedure step or immediately before validation.
- In `plugin-factory-router`, add the checkpoint in the deliverables/design
  checkpoint area or immediately before the workflow handoff.
- Do not add a long YAML schema to either router in Phase 1.

Hook interface:

- Existing command hook configuration remains unchanged.
- Hook scripts continue to print JSON with:

```json
{
  "continue": true,
  "suppressOutput": true,
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "..."
  }
}
```

- Additional context should include the compact gate wording once per hook
  output.
- `hookSpecificOutput.hookEventName` must be `SessionStart`, matching the live
  Codex `SessionStart` command output schema.
- Hook text must stay advisory. It must not imply that hooks enforce readiness
  or that `plugin_hooks` is enabled in every runtime.
- Hook text must keep the existing domain-specific context: `skill-factory`
  still needs lane routing, and `plugin-factory` still needs the bundled hook
  contract.

Test interface:

- Extend existing factory hook tests to assert that hook context includes gate
  terms such as `first-principles`, `artifact decision`, and at least one
  non-build decision term such as `DO_NOT_BUILD` or `IMPROVE_EXISTING`.
- Assert both hook scripts emit `hookSpecificOutput.hookEventName` as
  `SessionStart`, not only generic JSON with `additionalContext`.
- Keep tests close to current hook-script output tests so Phase 1 proves the
  runtime context path without inventing a new validator.
- Suggested minimum assertions:

```text
first-principles
artifact decision
smallest effective mechanism
IMPROVE_EXISTING
DO_NOT_BUILD
```

- Do not assert the full Phase 2 schema in Phase 1.

## Technical Constraints

- Hook scripts remain dependency-free Python scripts using only the standard
  library.
- Hook scripts must remain executable through the existing manifest-declared
  command paths and continue to use `${PLUGIN_ROOT}` in hook config.
- Hook output must match the live Codex `SessionStart` output shape by
  including `hookSpecificOutput.hookEventName: "SessionStart"`.
- Router edits must preserve read-only router execution boundaries.
- Test updates must not require `plugin_hooks` to be enabled at runtime; tests
  execute the scripts directly and validate JSON output.
- Phase 1 must not edit generated `.agents/**` surfaces.
- Phase 1 must not change `plugin_builder.pyw`, `create_basic_plugin.pyw`, or
  factory scaffolding templates unless a direct test failure proves those files
  are needed for the checkpoint.

## Invariants

- Hooks inject context only; they do not enforce readiness.
- The checkpoint must remain compact enough to preserve progressive disclosure.
- Phase 1 must not claim full factory readiness.
- The bundled hook contract must remain valid: `hooks/hooks.json`, top-level
  `hooks`, command handler, `timeout`, and `${PLUGIN_ROOT}` command paths.
- Factory source edits must remain under canonical plugin source paths, not
  runtime projections.

## Failure And Recovery

Failure: router text becomes too long or philosophical.

Recovery: move detail back out of the router and keep only the compact
checkpoint.

Failure: hook output stops parsing as JSON.

Recovery: fix the hook script and rerun focused py_compile and pytest before
any broader validation.

Failure: tests only assert vague wording.

Recovery: assert concrete gate terms and at least one non-build decision term.

Failure: Phase 1 expands into validation/eval enforcement.

Recovery: stop and route the added work to Phase 2, 3, or 4.

## Observability

Minimum observable signals:

- Hook scripts compile.
- Hook scripts emit valid JSON.
- Hook scripts emit Codex-compatible `SessionStart` hook output, including
  `hookSpecificOutput.hookEventName: "SessionStart"`.
- Hook context includes compact first-principles gate terms.
- Existing factory hook contract tests continue to pass.
- Authoring-family changed-file validation either passes or records an exact
  blocker.

Expected focused commands:

```bash
python3 -m py_compile \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py

python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q

git diff --check
```

Expected broader command, when practical after focused tests pass:

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files \
  Plugins/skill-factory/skills/skill-factory-router/SKILL.md \
  Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md \
  Plugins/skill-factory/hooks/session_start_routing.py \
  Plugins/plugin-factory/hooks/session_start_contract.py \
  Infrastructure/tests/test_plugin_bundled_hooks_contract.py
```

## Acceptance Matrix

| ID | Acceptance criterion | Evidence required |
| --- | --- | --- |
| SA-001 | `skill-factory-router` requires a compact first-principles gate before create, harden, refactor, or skillify decisions. | Diff in `Plugins/skill-factory/skills/skill-factory-router/SKILL.md` plus review against this spec. |
| SA-002 | `plugin-factory-router` requires the same compact gate before create, harden, refactor, or package-design decisions. | Diff in `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md` plus review against this spec. |
| SA-003 | `skill-factory` SessionStart context includes the compact gate and remains Codex-compatible hook JSON output. | `python3 -m py_compile ...` and focused pytest pass, including `hookEventName` assertion. |
| SA-004 | `plugin-factory` SessionStart context includes the compact gate and remains Codex-compatible hook JSON output. | `python3 -m py_compile ...` and focused pytest pass, including `hookEventName` assertion. |
| SA-005 | Tests assert concrete gate terms, at least one non-build decision, and `hookSpecificOutput.hookEventName`. | Diff in `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`; focused pytest pass. |
| SA-006 | Phase 1 does not add schema/procedure wiring, validator enforcement, eval fixtures, MCP tools, apps, or Linear mutation. | Git diff inspection confirms only Phase 1 files changed. |
| SA-007 | Broader readiness remains blocked until the eval artifact exists. | `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md` remains required for closure. |
| SA-008 | Router and hook wording preserve the advisory/enforcement split: hooks inject context, validators/evals enforce readiness. | Diff inspection confirms no hook text claims enforcement and no validator/eval files are changed in Phase 1. |
| SA-009 | The compact gate preserves existing factory-specific context instead of replacing it. | Hook output tests still assert existing plugin hook contract terms and skill routing terms alongside new gate terms. |

## Acceptance Traceability

| Linear payload | Spec IDs |
| --- | --- |
| `[agent-skills] Add factory first-principles checkpoint to routers and hooks` | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006 |
| Parent issue validation gates | SA-003, SA-004, SA-005, SA-007, SA-008, SA-009 |
| Refactor Phase 1 rollback rules | SA-006, SA-007 |

## First Slice

Implement only Phase 1:

1. Add compact gate text to the two factory routers.
2. Add compact gate text to the two factory hook script contexts.
3. Extend existing hook tests.
4. Run focused validation.

Stop after Phase 1 validation and hand off to `he-plan` before any broader
procedure, validator, or eval work.

Implementation order:

1. Update router text first so the human-visible decision boundary is clear.
2. Update hook script context second so runtime context matches the routers.
3. Update tests last so they assert both old and new context.
4. Run focused commands before the broader authoring-family gate.

## Questions

- Should Phase 2 use one shared factory reference schema or separate
  skill-factory and plugin-factory schemas?
- Should Phase 3 begin as warning-only for existing packages and strict for new
  factory output?

These questions do not block Phase 1.

## Done

Phase 1 is done when SA-001 through SA-006 pass and SA-007 is recorded as a
known future closure gate. SA-008 and SA-009 must also pass before Phase 1 is
ready for implementation handoff.

Factory-gate readiness is not done until Phase 4 writes and validates the eval
artifact.

## he-plan Handoff

Recommended next stage: `he-plan`

Selected implementation slice:
`Phase 1: Router And Hook Checkpoint`

Use this spec as the bounded implementation authority. Treat the strategy,
refactor program, and Linear plan as context only unless this spec references
them directly.
