---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-4-plan
artifact_type: he-plan
canonical_slug: agent-skills-first-principles-factory-gate-phase-4
title: First-Principles Factory Gate Phase 4 Plan
harness_stage: he-plan
status: drafted
date: 2026-05-13
traceability_required: false
origin: .harness/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: standard
ui: false
linear_mutation_status: not_applicable
---

# First-Principles Factory Gate Phase 4 Plan

## Command Summary

BLUF: This plan tells Jamie, future agents, and developers how to finish the first-principles factory-gate program by proving behavior, not just structure. It will add a small set of factory eval cases to the existing skill-factory and plugin-factory eval YAML surfaces so the factories must choose BUILD_SKILL, IMPROVE_EXISTING or DO_NOT_BUILD, BUILD_PLUGIN or ADD_HOOK, and a hook-availability rejection case from first-principles evidence. The main risk is that evals can pass on wording alone, so every unit requires a decision label plus at least one gate evidence signal and a closure artifact that refuses to claim universal factory correctness. The next action is he-work implementation of the scoped eval changes, validation, review gates, and closure evidence only.

Decision Needed: authorize he-work to implement this Phase 4 plan with changes limited to the allowed paths and validation gates below.

Top Risks: eval cases may become phrase checks; existing eval schema may reject unsupported proof metadata; live model evals may be too slow or unavailable; unrelated dirty Harness Engineering work may contaminate validation.

Next Action: implement PU-001 through PU-005 in order, then stop for review or commit authorization.

## Objective

Prove that the first-principles factory gate changes factory artifact-selection
behavior. Phase 4 should make the factories demonstrate build, non-build,
plugin-runtime, and drift-rejection decisions through deterministic eval
coverage and closure evidence.

## Source Contract

Primary source:

- .harness/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md

Source requirements:

| Requirement | Planned coverage |
| --- | --- |
| FR-001, SA-002 | PU-001 adds a positive BUILD_SKILL proof case. |
| FR-002, SA-003 | PU-002 adds an IMPROVE_EXISTING or DO_NOT_BUILD proof case. |
| FR-003, SA-004 | PU-003 adds a plugin-runtime surface decision proof case. |
| FR-004, SA-005 | PU-003 adds a drift rejection case for hook availability. |
| FR-005, FR-006, SA-006, SA-007 | PU-001 through PU-003 require decision labels plus gate evidence signals. |
| FR-007, SA-009 | PU-004 writes Phase 4 closure evidence. |
| FR-008, FR-009, FR-010, SA-010 | PU-005 validation and scope checks preserve boundaries. |

## Scope and Boundaries

Allowed paths:

- Plugins/skill-factory/skills/scaffolding_templates/skillify/references/evals.yaml
- Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/references/evals.yaml
- Plugins/plugin-factory/skills/plugin-factory-router/references/evals.yaml
- .harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md
- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md only if the closure proof needs aggregate status text after the Phase 4 eval exists.

Forbidden paths and side effects:

- Do not edit .agents/**, .skillsets/**, Plugins/cache/**, runtime mirrors, or user-level plugin copies.
- Do not change factory generators, plugin hooks, MCP servers, apps, hook configs, or plugin_hooks feature state.
- Do not mutate Linear.
- Do not broaden the he-refactor to he-reframe compatibility repair beyond route evidence and this plan/spec metadata.
- Do not run broad live model evals unless a validation gate explicitly requires them and the user authorizes the runtime cost.

## Current State / Evidence

Verified in this turn:

- Phase 4 spec exists and passes artifact identity, traceability, BLUF, generated-spec shape, and diff checks.
- Phase 3 implementation files exist: validate_first_principles_gate.py, test_validate_first_principles_gate.py, and validate_skill_authoring_family.sh.
- No Phase 4 spec or plan existed before this continuation.
- The HE router verifies the current compatibility path: legacy he-refactor prompts deterministically select canonical he-reframe.
- Broad unrelated working-tree changes exist in Harness Engineering files; this plan must preserve them.

Existing eval surfaces:

- skillify/references/evals.yaml already owns workflow-to-skill cases and is the natural home for BUILD_SKILL proof.
- skill-refactor/references/evals.yaml already owns keep, improve, merge, retire decisions and is the natural home for IMPROVE_EXISTING or DO_NOT_BUILD proof.
- plugin-factory-router/references/evals.yaml already owns plugin lane and surface routing and is the natural home for plugin-runtime and hook-drift proof.

## Implementation Strategy

Use existing eval YAML rather than introducing a new eval runner in Phase 4.
Add the smallest realistic cases that force artifact-selection behavior and can
be validated by existing YAML parsing plus repo tests.

Do not add unsupported schema fields to eval YAML until a validator proves they
are accepted. Encode proof expectations through existing acceptance checks such
as regex checks for decision labels and gate evidence terms.

Pre-verify any new eval YAML acceptance-check shape against the eval runner
schema before adding it to the Phase 4 artifact.

Create a Phase 4 eval artifact that records what changed, what validation ran,
and whether the broader program can be closed. Update the aggregate eval only
if the Phase 4 eval is present and validation passes.

## Work Units

### PU-001: Add BUILD_SKILL Behavior Proof

Objective: prove the factory can build the right small skill from a repeated,
evidence-backed workflow.

Source trace: FR-001, FR-005, FR-006, SA-002, SA-006, SA-007.

Allowed path:

- Plugins/skill-factory/skills/scaffolding_templates/skillify/references/evals.yaml

Forbidden paths:

- Skill source bodies, generator scripts, .agents/**, .skillsets/**, runtime mirrors.

Steps:

1. Add one realistic release-mode or smoke-and-release eval case.
2. Prompt should describe a repeated workflow with evidence and ask for the smallest durable capability.
3. Acceptance should require BUILD_SKILL and at least one evidence signal such as smallest reusable move, copied assumption, or validation proof.
4. Include deterministic forbidden commands only if the prompt introduces unsafe command pressure.

Validation:

- YAML parse through the focused tests chosen in PU-005.
- Authoring-family changed-file validation with this file included.

Stop condition:

- Stop if the eval format cannot express decision plus evidence checks without unsupported fields.

Rollback:

- Remove only the new eval case.

Handoff:

- Complete when the case is parseable and validation can inspect it.

### PU-002: Add Non-Build Or Improve-Existing Behavior Proof

Objective: prove the factory can reject a copied template or choose to improve
existing work instead of building another package.

Source trace: FR-002, FR-005, FR-006, SA-003, SA-006, SA-007.

Allowed path:

- Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/references/evals.yaml

Forbidden paths:

- Skill source bodies, generator scripts, .agents/**, .skillsets/**, runtime mirrors.

Steps:

1. Add one realistic eval case where the user asks for a broad or copied skill because another package exists.
2. Acceptance should require IMPROVE_EXISTING, DO_NOT_BUILD, or DOCS_ONLY.
3. Acceptance should require rejected assumption or evidence-required language.
4. Preserve existing category style and realistic prompt wording.

Validation:

- YAML parse through the focused tests chosen in PU-005.
- Authoring-family changed-file validation with this file included.

Stop condition:

- Stop if the existing skill-refactor route cannot naturally own the case; move the case to the router only after evidence shows ownership mismatch.

Rollback:

- Remove only the new eval case.

Handoff:

- Complete when the case proves a non-build decision rather than a generic review.

### PU-003: Add Plugin Runtime And Hook Drift Proof

Objective: prove the plugin factory chooses runtime behavior only when it must
travel with the plugin, and rejects hook availability as justification.

Source trace: FR-003, FR-004, FR-005, FR-006, SA-004, SA-005, SA-006, SA-007.

Allowed path:

- Plugins/plugin-factory/skills/plugin-factory-router/references/evals.yaml

Forbidden paths:

- Plugin generator scripts, hook config files, MCP server files, app surfaces, .agents/**, .skillsets/**, runtime mirrors.

Steps:

1. Add one plugin-runtime case that expects BUILD_PLUGIN or ADD_HOOK only when runtime behavior and trust boundary are explicit.
2. Add one hook-drift case that expects DO_NOT_BUILD, DOCS_ONLY, or IMPROVE_EXISTING when the only reason is that bundled hooks are available.
3. Acceptance should require decision labels plus runtime behavior, trust boundary, or rejected assumption evidence.
4. Include forbidden-command deterministic checks if prompts mention external scripts or untrusted plugin instructions.

Validation:

- YAML parse through the focused tests chosen in PU-005.
- Authoring-family changed-file validation with this file included.

Stop condition:

- Stop if the eval cases start implying plugin_hooks must be globally enabled.

Rollback:

- Remove only the new eval cases.

Handoff:

- Complete when both cases distinguish useful runtime behavior from surface bloat.

### PU-004: Write Phase 4 Closure Evidence

Objective: record whether Phase 4 proves enough behavior movement to close the
broader initiative.

Source trace: FR-007, NFR-004, SA-009.

Allowed paths:

- .harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md
- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md only after the Phase 4 eval exists and validation passes.

Forbidden paths:

- Linear, generated projections, runtime mirrors, plugin caches.

Steps:

1. Create a Phase 4 eval artifact mapping PU-001 through PU-003 to FR and SA IDs.
2. Record exact validation outcomes.
3. State whether the broader initiative is complete, complete with follow-up, or blocked.
4. If aggregate status is updated, make the change minimal and cite the Phase 4 eval path.

Validation:

- he eval report validator if available for the new eval artifact.
- artifact identity lint and traceability lint for any .harness eval artifact changed.

Stop condition:

- Stop if behavior proof is inconclusive; record complete_with_followup or blocked instead of forcing closure.

Rollback:

- Revert the closure artifact or aggregate status edit only.

Handoff:

- Complete when closure status is evidence-backed and not overclaimed.

### PU-005: Validate Scope And Preserve Boundaries

Objective: prove the Phase 4 changes are parseable, scoped, and do not regress
Phase 2 or Phase 3 surfaces.

Source trace: FR-008, FR-009, FR-010, NFR-001 through NFR-005, SA-008, SA-010.

Allowed paths:

- Validation commands only; no additional source files unless a direct validation blocker identifies a Phase 4-owned defect.

Forbidden paths:

- Any path outside PU-001 through PU-004 without fresh review.

Steps:

1. Run YAML/eval schema validation for the edited eval files.
2. Run Phase 3 helper tests.
3. Run bundled hook and Phase 2 wiring tests.
4. Run authoring-family validation with exact changed files.
5. Run git diff checks scoped to Phase 4 files.
6. Record unrelated dirty files without staging or editing them.

Validation:

- python3 -m pytest Infrastructure/tests/test_context_budgeted_skillsets.py -q
- python3 -m pytest Infrastructure/scripts/testing/test_validate_first_principles_gate.py -q
- python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q
- bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files $(git diff --name-only origin/main...HEAD -- Skills/ Plugins/ Infrastructure/ .harness/)
- git diff --check -- $(git diff --name-only origin/main...HEAD -- Skills/ Plugins/ Infrastructure/ .harness/)
- eval artifact lint commands for any .harness eval artifact changed.

Stop condition:

- Stop at the first Phase 4-owned validation failure and fix in scope.
- If validation failure is unrelated dirty-worktree contamination, record blocker and do not broaden scope.

Rollback:

- Revert PU-001 through PU-004 changes in reverse order.

Handoff:

- Complete when all validation passes or blockers are classified.

## Dependencies and Sequencing

| Order | Unit | Depends on | Reason |
| --- | --- | --- | --- |
| 1 | PU-001 | Phase 4 spec | Establish positive skill-build proof. |
| 2 | PU-002 | Phase 4 spec | Establish non-build or improve-existing proof. |
| 3 | PU-003 | Phase 4 spec | Establish plugin runtime and hook-drift proof. |
| 4 | PU-004 | PU-001, PU-002, PU-003 | Closure evidence depends on proof cases. |
| 5 | PU-005 | All prior units | Validation must inspect exact final changed files. |

PU-001 through PU-003 can be edited in one implementation pass, but validation
must treat them as distinct proof claims.

## Validation Gates

Required before implementation closeout:

- python3 -m pytest Infrastructure/tests/test_context_budgeted_skillsets.py -q
- python3 -m pytest Infrastructure/scripts/testing/test_validate_first_principles_gate.py -q
- python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q
- bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files <exact Phase 4 changed files>
- git diff --check -- <exact Phase 4 changed files>

Conditional:

- python3 Plugins/harness-engineering/skills/he-eval-report/scripts/validate_eval_report.py <Phase 4 eval path>, required if the script exists and a Phase 4 eval artifact is created.
- ./bin/ask evals run <target-skill-path> --mode smoke --json, optional and user-cost-gated if static validation cannot prove behavior coverage.

Not applicable:

- Browser/UI validation: no UI.
- Plugin hook runtime tests beyond existing bundled hook contract: Phase 4 does not change runtime hooks.
- Linear mutation validation: no Linear mutation.

## Review Plan

After implementation and validation:

- Run simplify review focused on whether the proof cases are the smallest useful set.
- Run he-code-review focused on eval validity, overclaiming, and scope drift.
- Run he-fix-bugs only if validation or review finds a Phase 4-owned failure.

Do not request a broad review swarm unless the diff expands beyond the allowed
paths.

## Rollback Plan

Rollback is text-local:

1. Remove closure or aggregate eval changes from PU-004.
2. Remove plugin-router eval cases from PU-003.
3. Remove skill-refactor eval case from PU-002.
4. Remove skillify eval case from PU-001.
5. Rerun the focused validation gates that apply to the remaining diff.

No data, Linear, hook, MCP, app, runtime, cache, or projection rollback is
expected.

## Risk Register

| Risk | Mitigation |
| --- | --- |
| Eval passes on phrase matching | Require decision label plus gate evidence signal. |
| Eval schema rejects new proof metadata | Use existing acceptance regex checks, not new schema fields. |
| Existing route ownership is wrong | Stop and move the case only after repo evidence proves ownership mismatch. |
| Closure overclaims | Closure artifact must distinguish complete, complete_with_followup, and blocked. |
| Dirty worktree contaminates validation | Use exact changed-file commands and preserve unrelated changes. |

## Observability and Evidence

Evidence to record in Phase 4 eval:

- changed file list;
- exact new eval case IDs;
- validation command outputs;
- closure status and confidence;
- explicit statement that no runtime hooks, validators, generators, projections, or Linear state changed.

## Visual References / Diagrams

| Unit | Proof role | Closure impact |
| --- | --- | --- |
| PU-001 | BUILD_SKILL behavior proof | Shows the gate can build when evidence supports it. |
| PU-002 | Non-build or improve-existing proof | Shows the gate can resist copied template pressure. |
| PU-003 | Plugin runtime plus drift proof | Shows plugin surfaces are chosen from runtime need, not availability. |
| PU-004 | Closure evidence | Converts proof results into bounded initiative status. |
| PU-005 | Validation | Prevents scope and readiness overclaims. |

## Accessibility and Operator Ergonomics

Use stable case IDs, plain acceptance labels, and exact commands. The closure
artifact should be readable without opening the full prior phase chain.

## Open Questions

- Whether static eval YAML checks are sufficient, or whether Jamie wants a live ./bin/ask evals smoke run for the new cases.
- Whether the aggregate factory-gate eval should be updated in the same phase or left for he-compound closeout.

These do not block implementation if PU-004 records the chosen closure posture
and does not overclaim.

## Final Decision

Proceed to he-work only after Jamie authorizes implementation of this plan. The
plan is scoped and ready for review, but it does not itself grant permission to
edit eval files or closure artifacts.

## Appendix A. Harness Metadata / Traceability

stage_context:

- selected_stage: he-plan
- selected_slice: first-principles-factory-gate-phase-4-eval-proof-and-closure
- source_spec: .harness/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
- linear_mutation_status: not_applicable
- generated_projection_status: not_touched
- router_status: verified_he_refactor_aliases_he_reframe

post_plan_handoff:

- state: explicit_stop
- selected_next_stage: he-work
- evidence: .harness/plan/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-plan.md
- next_action: Run he-work only after user authorizes implementation of this Phase 4 plan.

## Appendix B. Linear / Tracker Handoff

No Linear mutation was performed. Suggested Linear topology remains in
.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md
if Jamie wants tracker-backed execution later.

## Appendix C. Review Outcomes

Technical review has not yet been run for this Phase 4 plan.

## No-Fog Gate

- This plan changes eval evidence, not runtime factory behavior.
- The proof target is decision movement, not first-principles wording.
- The allowed implementation files are narrow and listed above.
- Do not claim broad factory correctness from this small proof set.
