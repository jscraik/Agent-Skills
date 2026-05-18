---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-phase-4-spec
artifact_type: he-spec
canonical_slug: agent-skills-first-principles-factory-gate-phase-4
title: First-Principles Factory Gate Phase 4 Spec
harness_stage: he-spec
status: drafted
date: 2026-05-13
traceability_required: false
origin: .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
risk: medium
depth: standard
ui: false
linear_mutation_status: not_needed
---

# First-Principles Factory Gate Phase 4 Spec

## Command Summary

BLUF: This spec covers the final proof phase for Jamie, future agents, and developers working on the first-principles factory gate in skill-factory and plugin-factory. Phase 1 made the gate visible, Phase 2 wired the shared procedure, and Phase 3 made missing evidence detectable, but none of that proves the factories make better artifact-selection decisions. Phase 4 must add behavior-focused eval proof showing that the gate changes outcomes in both directions: it builds the right small capability when evidence supports it and refuses, defers, or improves existing work when a copied template would add noise. The main risk is mistaking phrase matching or structured YAML presence for decision quality, so the next step is a plan that adds minimal eval cases and closure evidence without widening runtime hooks, validators, generators, Linear state, or generated projections.

Decision Needed: approve a Phase 4 plan that adds behavior-proof eval cases and a closure artifact, then stop the broader factory-gate initiative only if the eval evidence shows real decision movement.

Top Risks: eval cases may only prove the phrase first_principles_gate appears; behavior proof may accidentally become a generator rewrite; and the closure artifact may overclaim full factory readiness while warning-first validation remains advisory.

Next Action: hand this spec to he-plan for a small implementation plan scoped to eval fixtures, validation, and closure proof.

## Purpose

Phase 4 proves whether the first-principles factory gate changes factory
decisions. The target behavior is not more YAML, more docs, or more factory
surfaces. The target behavior is better artifact selection by the factory
plugins before build or hardening work claims readiness.

This spec turns the remaining refactor-program objective into a bounded
behavior contract. It defines the eval cases, expected evidence, acceptance
criteria, and closure boundary needed before the broader first-principles
factory-gate program can be called complete.

## Problem Statement

The factory gate is now present in routers, hook context, shared procedure,
factory lane guidance, and a warning-first validator. That is necessary but not
sufficient. A factory can still produce ceremonial compliance by adding a
parseable first_principles_gate record while keeping the same copied artifact
choice it would have made before the gate existed.

The remaining problem is proof quality: the repository needs deterministic,
reviewable evidence that the gate affects decisions across positive,
negative, plugin-runtime, and drift scenarios.

## User / Operator Scenarios

Scenario 1: Build the right skill.

An operator asks the factory to turn a repeated, evidence-backed workflow into
a durable skill. The factory should select BUILD_SKILL, identify the smallest
reusable cognitive move, reject broader copied package shapes, and name a
validation proof.

Scenario 2: Do not build the wrong skill.

An operator asks for a broad or copied skill because a similar package exists.
The factory should select DO_NOT_BUILD, DOCS_ONLY, or IMPROVE_EXISTING when the
request lacks a recurring cognitive move, evidence, or validation proof.

Scenario 3: Choose plugin runtime behavior only when it must travel.

An operator asks for a plugin capability involving hooks, MCP, apps, or bundled
metadata. The plugin factory should choose BUILD_PLUGIN, ADD_HOOK, or another
plugin surface only when runtime behavior should travel with the capability and
the trust boundary is explicit.

Scenario 4: Reject hook availability as a reason to add hooks.

An operator asks to add hooks because bundled plugin hooks now exist. The
factory should reject the assumption that availability implies usefulness and
should choose DO_NOT_BUILD, DOCS_ONLY, or IMPROVE_EXISTING unless there is
runtime behavior, evidence, and validation proof.

## Goals

- Prove the first-principles gate changes factory artifact-selection behavior.
- Add eval cases that require build, non-build, plugin-runtime, and drift decisions.
- Keep the eval proof tied to first_principles_gate fields and decision values from the Phase 2 reference.
- Preserve Phase 3 warning-first validator policy unless a later plan explicitly approves stricter enforcement.
- Produce closure evidence that separates Phase 4 success from unrelated plugin, hook, or Linear work.

## Non-Goals

- Do not rewrite factory generators.
- Do not make plugin_hooks required.
- Do not add new MCP tools, apps, plugin hook configs, or runtime surfaces.
- Do not mutate .agents/**, .skillsets/**, plugin caches, runtime mirrors, or user-level plugin copies.
- Do not create or update Linear issues unless the user explicitly asks.
- Do not run broad live model evals when focused fixture or benchmark evidence is sufficient.
- Do not claim the factories are universally correct after a small proof set.

## Current State / Evidence

| Source | Evidence | Impact |
| --- | --- | --- |
| .harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md | Defines Phase 4 as eval proof and closure artifact. | Primary program boundary. |
| .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md | Reports Phase 3 validator implementation complete with follow-up. | Confirms behavior proof remains open. |
| .harness/solutions/2026-05-09-agent-skills-first-principles-factory-gate-validator-solution.md | Documents warning-first validator pattern and states Phase 4 remains required. | Prevents strict-enforcement drift. |
| Infrastructure/references/first-principles-factory-gate.md | Defines required gate fields and allowed decisions. | Source of truth for eval expectations. |
| Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py | Validates parseable gate evidence and warning/strict behavior. | Structural proof exists but not behavior proof. |
| Factory eval YAML files under Plugins/skill-factory/**/references/evals.yaml and Plugins/plugin-factory/**/references/evals.yaml | Existing eval shape supports realistic prompts, categories, trigger expectations, deterministic checks, and regex or skill-selection acceptance. | Likely implementation target for Phase 4 proof cases. |

Compatibility note: he-reframe is the canonical reframe skill. The legacy
he-refactor handle remains supported as a deterministic alias to he-reframe, and
the HE router now verifies that alias against the live manifest.

## Proposed Behavior

Phase 4 should add a small proof set that demonstrates decision movement. Each
proof case must require a concrete artifact decision and must fail if the
factory only mentions first-principles language without choosing and justifying
the right action.

The proof set should cover at least:

- one BUILD_SKILL case;
- one DO_NOT_BUILD, DOCS_ONLY, or IMPROVE_EXISTING case;
- one plugin-runtime case where BUILD_PLUGIN or ADD_HOOK is justified;
- one drift case where hook or plugin surface availability is rejected as an insufficient reason.

The implementation may add these as eval cases in existing factory
references/evals.yaml files, as a focused Phase 4 eval harness, or as both, but
the plan must choose the smallest maintainable surface after inspecting the
existing evaluator commands.

## Requirements

### Functional Requirements

FR-001: Phase 4 MUST add behavior-proof eval coverage for a positive skill build decision.

FR-002: Phase 4 MUST add behavior-proof eval coverage for a non-build or improve-existing decision.

FR-003: Phase 4 MUST add behavior-proof eval coverage for a plugin runtime surface decision, such as BUILD_PLUGIN or ADD_HOOK, only when runtime behavior must travel with the plugin.

FR-004: Phase 4 MUST add behavior-proof eval coverage for a drift case that rejects hook or plugin surface availability as sufficient justification.

FR-005: Each new proof case MUST assert at least one allowed artifact_decision value from the Phase 2 reference.

FR-006: Each new proof case MUST assert at least one evidence or reasoning signal from the gate, such as desired_outcome, copied_assumption_rejected, smallest_effective_mechanism, or validation_proof.

FR-007: Phase 4 MUST update or create a closure eval artifact under .harness/evals/** that states whether the broader first-principles factory gate initiative is complete, complete with follow-up, or blocked.

FR-008: Phase 4 MUST preserve Phase 3 warning-first validator behavior unless a separate approved plan explicitly changes enforcement mode.

FR-009: Phase 4 MUST NOT edit generated projections, runtime mirrors, plugin caches, or user-level plugin copies.

FR-010: Phase 4 MUST NOT add new hooks, MCP servers, apps, or generator rewrites unless a later approved spec supersedes this one.

### Non-Functional Requirements

NFR-001: Eval cases SHOULD be realistic operator prompts, not benchmark-only phrasing.

NFR-002: Eval assertions SHOULD be deterministic enough for review without requiring subjective interpretation of long model output.

NFR-003: The proof set SHOULD stay small enough to preserve quick focused validation.

NFR-004: Closure language MUST avoid claiming universal factory correctness.

NFR-005: Any live eval or model-backed run MUST record exact command, duration-relevant output, and pass/fail result.

## Interfaces

Primary candidate surfaces:

- Plugins/skill-factory/**/references/evals.yaml
- Plugins/plugin-factory/**/references/evals.yaml
- Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh
- Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py
- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
- a new Phase 4 eval artifact if the plan chooses not to mutate the aggregate closure eval directly.

Interface contract for new eval cases:

- id: stable, unique, kebab-case.
- category: one of the repo existing eval categories such as happy, edge, negative, or pressure.
- realistic: true for behavior-proof prompts.
- eval_modes: include smoke when cheap and release when the case must be part of closure confidence.
- should_trigger: reflects whether the target factory skill should activate.
- prompt: realistic operator request that forces artifact selection.
- acceptance: includes deterministic checks for the expected decision and gate evidence.
- deterministic_checks: includes forbidden commands when the prompt contains pressure or untrusted text.

Unknown fields should follow the existing eval loader behavior. Phase 4 must
not rely on undocumented fields unless validation proves they are accepted.

## Data / Domain Contract

Allowed artifact decisions:

~~~text
BUILD_SKILL
BUILD_PLUGIN
ADD_HOOK
ADD_MCP_TOOL
ADD_APP
ADD_EVAL
IMPROVE_EXISTING
DOCS_ONLY
DO_NOT_BUILD
~~~

Required proof signals:

~~~yaml
first_principles_behavior_proof:
  prompt_id: ""
  expected_decision: ""
  rejected_assumption: ""
  smallest_effective_mechanism: ""
  validation_signal: ""
  pass_condition: ""
~~~

Compatibility:

- Existing first_principles_gate schema remains authoritative for factory outputs.
- Phase 4 proof metadata may appear only in .harness eval/plan artifacts if adding it to eval YAML would create unsupported fields.
- Any closure artifact MUST map Phase 4 proof cases back to `FR-*` and `SA-*` IDs.

## Security, Privacy, and Safety

Phase 4 should not increase external side effects. Prompts that include
untrusted text, install scripts, hooks, GitHub operations, or command pressure
must include deterministic forbidden-command checks when supported by the eval
format.

No secrets, tokens, private local paths beyond repository evidence, or raw
session transcripts should be embedded into eval prompts.

## Accessibility and Operator Ergonomics

The Phase 4 artifacts are operator-facing markdown and YAML. They must use
plain labels, exact paths, stable IDs, and non-color-only pass/fail language.

The closure artifact should make the program state understandable without
requiring the reader to open every earlier phase artifact.

## Failure and Recovery

| Failure | Recovery |
| --- | --- |
| Eval accepts phrase matching only | Tighten acceptance to require decision and evidence signals. |
| Eval runner rejects new fields | Move proof metadata into .harness artifact text and keep eval YAML compatible. |
| Live eval is too slow or unavailable | Use focused static or fixture proof and record live eval as blocked, not passed. |
| Proof cases encourage building extra surfaces | Rewrite prompts to force smallest mechanism and non-build alternatives. |
| Validation fails from unrelated dirty generated files | Preserve unrelated work and rerun with changed-file scope. |

## Validation Plan

Minimum planning validation:

~~~bash
vale sync && vale .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md --json
python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md --kind spec --json
git diff --check -- .harness/archive/2026-05-18-plans-and-specs/specs/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-spec.md
~~~

Minimum implementation validation for the future Phase 4 plan:

~~~bash
python3 -m pytest Infrastructure/scripts/testing/test_validate_first_principles_gate.py -q
python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files <exact Phase 4 changed files>
git diff --check -- <exact Phase 4 changed files>
~~~

If the plan adds or changes eval YAML, it must also run the smallest available
eval-schema or benchmark listing command that validates those files.

## Acceptance Criteria

SA-001: A Phase 4 plan can identify exactly where behavior-proof eval cases will live.

SA-002: The proof set includes one positive BUILD_SKILL case.

SA-003: The proof set includes one non-build, docs-only, or improve-existing case.

SA-004: The proof set includes one plugin-runtime decision case.

SA-005: The proof set includes one drift case rejecting hook or plugin surface availability as justification.

SA-006: Each proof case asserts an allowed artifact_decision.

SA-007: Each proof case asserts at least one gate evidence signal beyond the decision label.

SA-008: Focused validation passes for modified eval/validator/factory files.

SA-009: Closure evidence states whether the broader initiative is complete or still blocked.

SA-010: No generated projections, plugin caches, runtime mirrors, Linear objects, hook configs, MCP servers, apps, or generator rewrites are mutated.

## Visual References / Diagrams

~~~mermaid
flowchart LR
    P1[Phase 1: visible gate] --> P2[Phase 2: shared procedure]
    P2 --> P3[Phase 3: warning-first validator]
    P3 --> P4[Phase 4: behavior proof]
    P4 --> C{Closure claim?}
    C -->|Build and non-build decisions proven| Done[Complete with bounded confidence]
    C -->|Only words or YAML proven| Follow[Complete with follow-up or blocked]
~~~

The diagram is normative only for phase order and closure decision. The
requirements and acceptance criteria are authoritative when text and diagram
differ.

## Implementation Notes

- Prefer adding the smallest number of eval cases across the factory lanes that naturally own each behavior.
- Start by inspecting existing eval schema and validation commands before editing YAML.
- Keep closure evidence in .harness/evals/**; do not treat chat commentary as closure proof.
- Preserve the Phase 2 reference and Phase 3 validator constants as the source of gate vocabulary.
- If the implementation discovers Phase 3 validation evidence is stale, refresh it before adding Phase 4 proof.

## Open Questions

- Which existing eval runner is the canonical smallest command for validating factory eval YAML in this repo?
- Should Phase 4 update the aggregate factory-gate eval artifact directly or create a dated Phase 4 eval and leave aggregate closure for he-compound?
- Should proof cases live in skillify, skill-refactor, plugin-router, plugin-builder, or a focused shared benchmark file?

These questions should be resolved by he-plan from repo evidence, not by
guessing during implementation.

## Decision

Proceed to he-plan for Phase 4. Implementation is not yet authorized by this
spec alone because the exact eval target files and validation commands still
need to be selected.

## Evidence and References

- .harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md
- .harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md
- .harness/solutions/2026-05-09-agent-skills-first-principles-factory-gate-validator-solution.md
- Infrastructure/references/first-principles-factory-gate.md
- Infrastructure/scripts/validation-and-linting/validate_first_principles_gate.py
- Plugins/skill-factory/skills/data_fetch_analysis/skill-refactor/references/evals.yaml
- Plugins/skill-factory/skills/scaffolding_templates/skillify/references/evals.yaml
- Plugins/plugin-factory/skills/plugin-factory-router/references/evals.yaml

## Appendix A. Harness Metadata / Traceability

~~~yaml
schema_version: 1
stage_context:
  selected_stage: he-spec
  selected_slice: first-principles-factory-gate-phase-4-eval-proof-and-closure
  source_program: .harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md
  prior_phase_status:
    phase_1: complete_with_followup
    phase_2: implemented
    phase_3: complete_with_followup
  linear_mutation_status: not_needed
  generated_projection_status: not_touched
  router_status: verified_he_refactor_aliases_he_reframe
~~~

Linear action required: none. Suggested Linear parent/sub-issue payloads remain
in .harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md
if Jamie later wants tracker mutation.

## Appendix B. Review Outcomes

Technical review has not yet been run for this Phase 4 spec. A future deepen or
review pass should challenge whether the proposed proof cases measure decision
movement rather than language presence.

## Appendix C. he-plan Handoff

~~~yaml
post_spec_handoff:
  state: ready_for_he_plan
  selected_next_stage: he-plan
  plan_target: .harness/plan/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-plan.md
  implementation_authority: not_granted_by_spec
  required_plan_decisions:
    - exact eval target files
    - smallest eval validation command
    - aggregate versus phase-specific closure artifact
    - review gate sequence before commit
  next_action: "Create a Phase 4 plan that adds behavior-proof eval cases and closure evidence without changing runtime hooks, validators, generators, projections, or Linear state."
~~~

## No-Fog Gate

- This spec is about behavior proof, not new factory surfaces.
- The pass condition is changed artifact-selection behavior, not the presence of first-principles language.
- The next artifact must be a plan, because the exact eval target files and validation command still need repo-backed selection.
- Full factory-gate readiness remains unclaimed until Phase 4 validation and closure evidence pass.
