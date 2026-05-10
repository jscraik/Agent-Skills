---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-3-plan
artifact_type: he-plan
canonical_slug: agent-skills-first-principles-factory-gate-phase-3
title: First-Principles Factory Gate Phase 3 Plan
harness_stage: he-plan
status: proposed
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: standard
ui: false
---

# First-Principles Factory Gate Phase 3 Plan

## Executive Plan Summary

This plan implements Phase 3 of the first-principles factory gate migration:
add deterministic warning-first validation for missing or malformed
`first_principles_gate` evidence in factory-created, factory-hardened, or
factory-readiness work.

The plan deliberately stops before Phase 4 behavior-changing eval proof. Phase
3 can prove structural enforcement, scoped warnings, strict-mode unit behavior,
and authoring-family integration. It cannot claim that the gate improves factory
artifact-selection decisions.

## Source Evidence

| Source | Evidence Used | Planning Impact |
| --- | --- | --- |
| `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec.md` | Defines warning-first rollout, accepted evidence locations, scope detection, acceptance IDs SA1-SA11, and Phase 4 boundary. | Primary execution contract. |
| `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-spec-technical-review.md` | Approves spec for planning and calls out helper placement, strict-mode exposure, and behavior-proof boundary as residual risks. | Resolves plan focus. |
| `.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md` | Phase 3 objective is validator/test enforcement; Phase 4 owns eval proof. | Prevents scope expansion. |
| `Infrastructure/references/first-principles-factory-gate.md` | Defines required field names and allowed decisions from Phase 2. | Validator vocabulary source. |
| `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh` | Existing authoring-family validation front door with changed-file scoping and pytest selection. | Integration point. |
| `Infrastructure/tests/test_plugin_bundled_hooks_contract.py` | Current focused test proving bundled hooks and Phase 2 gate reference wiring. | Regression validation target, not the best new parser-test home. |

## Stage Context

```yaml
schema_version: 1
stage_context:
  selected_stage: he-plan
  selected_slice: first-principles-factory-gate-phase-3-validator-and-test-enforcement
  slice_status: resolved
  tracker_status: user_opted_out
  artifact_identity_status: pass
  artifact_route_status: pass
  evidence_freshness: fresh
  session_trace_status: resolved
  linear_delta_status: not_applicable
  domain_skill_status: not_applicable
  steering_status: assumed_headless
  coding_harness_status: not_applicable
  project_brain_status: not_checked
  validation_status: not_run_with_reason
  blocker: null
```

Validation status is `not_run_with_reason` because this plan is a durable
planning artifact. Artifact lints are run after writing; implementation
validation belongs to `he-work`.

## Planning Decisions

### Decision 1: Add A Dedicated Python Helper

Add a focused helper at:

`Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py`

Reason: parsing markdown frontmatter, fenced YAML, and labeled sections is
structured data work. Embedding that logic in
`validate_skill_authoring_family.sh` would increase shell complexity and make
unit tests weaker.

### Decision 2: Keep Authoring-Family Integration Warning-First

`validate_skill_authoring_family.sh` should invoke the helper for matching
changed-file scopes, but the default behavior must not hard-block active
historical files. Missing or malformed gate evidence should produce warning
classification by default.

Reason: the branch has unrelated dirty files and existing fixtures. A strict
default would risk noisy false positives before Phase 4 proves behavioral value.

### Decision 3: Expose Strict Mode On The Helper, Not Broadly In The Family Gate

The helper may support `--strict` for direct tests. The authoring-family shell
gate should not enable strict mode by default in Phase 3.

Reason: this proves hard-failure behavior without making broad CI/repo
validation brittle.

### Decision 4: Put Parser Tests Beside Validation Scripts

Add tests at:

`Infrastructure/scripts/testing/test_validate_first_principles_gate.py`

Reason: the parser/helper is an infrastructure validator, not a bundled-hook
contract. Keeping tests beside existing validation script tests makes
ownership clearer and avoids overloading
`Infrastructure/tests/test_plugin_bundled_hooks_contract.py`.

## Scope

In scope:

- new first-principles gate validator helper;
- focused parser/helper tests;
- minimal `validate_skill_authoring_family.sh` integration;
- changed-file trigger and skip/warn/fail/pass classification output;
- validation evidence for the new helper and existing Phase 1/2 hook/gate
  surfaces.

Out of scope:

- Phase 4 eval fixtures;
- live model eval execution;
- plugin hook runtime requirements;
- broad plugin/skill generator rewrites;
- changes to `.agents/**`, `.skillsets/**`, generated projections, runtime
  mirrors, or user-level plugin copies;
- Linear mutation;
- strict authoring-family default enforcement.

## Implementation Units

### PU-001: Add Validator Helper

Files:

- `Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py`

Acceptance:

- SA1, SA2, SA3, SA4, SA6, SA9, SA10

Work:

- Define required fields from the Phase 2 reference:
  `desired_outcome`, `user_specific_constraints`,
  `copied_assumption_rejected`, `fundamental_constraints`,
  `smallest_effective_mechanism`, `artifact_decision`,
  `rejected_alternatives`, `evidence_required`, `validation_proof`, and
  `stop_or_pivot_condition`.
- Define allowed decisions:
  `BUILD_SKILL`, `BUILD_PLUGIN`, `ADD_HOOK`, `ADD_MCP_TOOL`, `ADD_APP`,
  `ADD_EVAL`, `IMPROVE_EXISTING`, `DOCS_ONLY`, and `DO_NOT_BUILD`.
- Parse gate evidence from:
  - YAML frontmatter;
  - fenced YAML containing top-level `first_principles_gate`;
  - labeled markdown section with parseable `key: value` lines.
- Reject prose-only mentions of first-principles thinking.
- Classify each inspected path as `pass`, `warn`, `fail`, or `skipped`.
- Support `--strict` for direct helper tests.
- Emit stable text output and JSON output if practical. If both are too much,
  prefer stable text plus focused unit tests.

Rollback:

- Remove the helper and keep Phase 2 reference/procedure wiring advisory.

### PU-002: Add Focused Validator Tests

Files:

- `Infrastructure/scripts/testing/test_validate_first_principles_gate.py`

Acceptance:

- SA2, SA3, SA4, SA5, SA6, SA9, SA10

Work:

- Add fixtures in test temp directories rather than committed generated
  package fixtures unless a committed fixture is proven necessary.
- Cover:
  - complete frontmatter gate record;
  - complete fenced-YAML gate record;
  - complete labeled-section gate record;
  - missing required key;
  - invalid `artifact_decision`;
  - blank / `TODO` / `TBD` placeholder values;
  - valid `not_applicable` with reason;
  - invalid `not_applicable` for readiness-claiming output;
  - prose-only first-principles mention;
  - archive/generated/unrelated path skip behavior;
  - strict-mode failure versus warning-default behavior.

Rollback:

- Remove tests with helper if helper is reverted.

### PU-003: Wire Authoring-Family Changed-File Scope

Files:

- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`

Acceptance:

- SA1, SA5, SA7, SA10, SA11

Work:

- Add a small changed-file trigger block for first-principles validation.
- Trigger when changed files include:
  - `Plugins/skill-factory/skills/**`;
  - `Plugins/plugin-factory/skills/**`;
  - `Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py`;
  - `Infrastructure/scripts/testing/test_validate_first_principles_gate.py`;
  - explicitly selected active factory-output fixtures, if added later.
- Skip or warning-only for:
  - `.agents/**`;
  - `.skillsets/**`;
  - `Plugins/**/fixtures/budget-archive/**`;
  - generated/runtime projection paths;
  - unrelated docs/packages.
- Invoke the helper in default warning mode.
- Print an explicit skip message when no changed path needs first-principles
  validation.

Rollback:

- Remove the shell integration; helper can remain direct-test-only if useful.

### PU-004: Preserve Existing Factory Hook And Gate Tests

Files:

- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Acceptance:

- SA7, SA11

Work:

- Do not move the Phase 2 wiring tests unless needed.
- Run existing focused tests to prove Phase 3 did not regress bundled hook or
  Phase 2 gate-reference wiring.
- Only edit this file if implementation discovers a direct test integration
  need; otherwise leave it unchanged.

Rollback:

- Revert any accidental broadening of bundled-hook tests.

### PU-005: Validate And Record Phase 3 Boundary

Files:

- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md`
- future `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`

Acceptance:

- SA7, SA8, SA11

Work:

- Run focused helper tests.
- Run authoring-family validation with exact Phase 3 changed files.
- Run `git diff --check`.
- Run artifact lints for the plan/eval artifacts.
- In the Phase 3 eval, explicitly state that Phase 4 behavior-changing eval
  proof remains open.

Rollback:

- If validation creates noisy false positives, downgrade to helper-only tests
  and remove shell integration until scope detection is corrected.

## Acceptance Traceability

| Acceptance ID | Planned Unit(s) | Proof |
| --- | --- | --- |
| SA1 | PU-001, PU-003 | Helper exists and authoring-family gate invokes it for matching changed files. |
| SA2 | PU-001, PU-002 | Tests cover required keys and allowed decisions. |
| SA3 | PU-001, PU-002 | Tests cover blank/TODO/TBD placeholder rejection. |
| SA4 | PU-001, PU-002 | Tests cover valid and invalid `not_applicable` cases. |
| SA5 | PU-002, PU-003 | Tests/command output prove archive/unrelated paths are skipped or warning-only. |
| SA6 | PU-001, PU-002 | Tests assert stable path/remediation output. |
| SA7 | PU-002, PU-003, PU-004, PU-005 | Focused pytest, family validation, and diff check pass. |
| SA8 | PU-005 | Phase 3 eval keeps Phase 4 open. |
| SA9 | PU-001, PU-002 | Tests cover frontmatter, fenced YAML, labeled section, and prose-only rejection. |
| SA10 | PU-001, PU-003 | Helper/family output classifies pass/warn/fail/skipped. |
| SA11 | PU-004, PU-005 | Diff inspection and validation show no live eval, hook runtime, projection, or generator rewrite. |

## Validation Plan

Minimum Phase 3 implementation commands:

```bash
python3 -m py_compile Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Infrastructure/scripts/testing/test_validate_first_principles_gate.py
python3 -m pytest Infrastructure/scripts/testing/test_validate_first_principles_gate.py -q
python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q
git diff --check
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py Infrastructure/scripts/testing/test_validate_first_principles_gate.py Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md
```

If implementation touches additional files, append those exact paths to the
`--changed-files` validation command.

Do not run live model evals for Phase 3.

## Dirty Worktree Guard

Before `he-work` edits files, inspect:

```bash
git status --short --branch
git diff --name-only
```

The current branch already contains unrelated dirty files. `he-work` must leave
unrelated user/generated edits untouched and limit Phase 3 source edits to the
planned file contract unless a direct validator dependency requires otherwise.

## Risks And Mitigations

| Risk | Mitigation |
| --- | --- |
| Warning mode becomes toothless ceremony. | Require negative tests and strict-mode helper behavior even though family-gate default is warning-first. |
| Strict mode blocks existing historical fixtures. | Keep strict mode off by default and test archive/generated path skipping. |
| Parser accepts vague prose as proof. | Add prose-only negative test. |
| Shell script grows complex. | Put parsing in Python helper and keep shell integration small. |
| Phase 3 overclaims behavior improvement. | Require Phase 3 eval to state Phase 4 remains open. |
| Validator requires plugin hooks at runtime. | Keep validator about factory evidence only; do not read `plugin_hooks` feature state. |

## Rollback Plan

1. Remove `validate_skill_authoring_family.sh` integration if family validation
   becomes noisy.
2. Keep the helper direct-test-only while scope detection is repaired, or
   remove the helper if the parser design is wrong.
3. Preserve Phase 1 router/hook context and Phase 2 reference/procedure wiring.
4. Mark the Phase 3 eval as blocked or inconclusive.
5. Do not claim factory-gate readiness until Phase 4 behavior proof exists.

## Out Of Scope Reminder

Do not add:

- Phase 4 eval fixtures;
- live model evals;
- new plugin hooks;
- MCP tools or apps;
- broad generator rewrites;
- generated projections;
- Linear mutations.

## Post-Plan Handoff

```yaml
post_plan_handoff:
  state: explicit_stop
  selected_next_stage: he-work
  evidence: ".harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md"
  next_action: "Run he-work only after user authorizes implementation of this Phase 3 plan."
```
