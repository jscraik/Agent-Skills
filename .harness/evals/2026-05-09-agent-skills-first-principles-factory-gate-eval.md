---
schema_version: 1
artifact_id: agent-skills-first-principles-factory-gate-eval
artifact_type: he-eval-report
canonical_slug: agent-skills-first-principles-factory-gate
title: First-Principles Factory Gate Eval
harness_stage: he-eval-report
status: complete_with_followup
date: 2026-05-13
traceability_required: false
origin: .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md
linear_issue: not_created
linear_milestone: First-Principles Factory Gate (proposed)
---

# First-Principles Factory Gate Eval

## Executive Eval Summary

Status: Complete with follow-up for the four-phase first-principles factory
gate program.

Linear Completion Recommendation: no Linear mutation is required because no
Linear issue exists. If the proposed parent or phase sub-issues are created
later, mark the completed slices Complete with follow-up after user acceptance
of this aggregate eval.

Primary Blockers: no phase-owned validation blocker remains. The only follow-up
is optional live model eval or smoke benchmarking if Jamie wants trajectory
proof beyond static eval fixtures and deterministic validation.

Confidence: high for router/hook context, reference schema/procedure wiring,
warning-first validator coverage, and static behavior-proof eval fixtures;
medium for live runtime behavior until optional model eval smoke proof is run.

## Evaluated Slice

Linear Project: `agent-skills` proposed only.

Linear Milestone: `First-Principles Factory Gate` proposed only.

Linear Parent Issue: not created.

Linear Sub-Issues: not created; proposed slice is `[agent-skills] Add factory
first-principles checkpoint to routers and hooks`.

Refactor Program:
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`.

Plugin Harness Engineering Spec:
`.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md`.

Affected Files/Modules:

- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
- `Plugins/skill-factory/hooks/session_start_routing.py`
- `Plugins/plugin-factory/hooks/session_start_contract.py`
- `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`
- `Plugins/harness-engineering/references/folded-skill-context.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`

Affected Workflows: factory routing, plugin-bundled SessionStart hook context,
focused bundled-hook contract tests, and HE preserved-context validation.

Related ADRs: none.

Related Core Invariants: canonical plugin source paths, advisory hook context
before enforcement, no generated projection edits, and proof-before-closure.

## Linear Definition of Done Status

Artifact Path:
`.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md`.

Definition of Done Status: satisfied with follow-up for the four-phase
first-principles factory-gate program.

Closure Safety: safe to close the local four-phase implementation as complete
with follow-up. Unsafe to claim universal factory correctness without live
trajectory evidence.

## Linear Backlink Map

Linear Project: `agent-skills` proposed.

Linear Milestone: `First-Principles Factory Gate` proposed.

Linear Parent Issue: not created.

Linear Sub-Issues: not created.

Linear Status Recommendation: leave uncreated unless the user wants external
tracking; if created, recommend Complete with follow-up for the completed local
implementation and keep optional live trajectory proof as follow-up.

Proof Artifact Links:

- `.harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md`
- `.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`
- `.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan-technical-review.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-eval.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`
- `.harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md`
- `.harness/review/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-technical-review.md`
- this eval artifact

Missing Identifiers: Linear parent issue ID and Linear sub-issue ID were not
created by design.

Traceability Repair: create Linear issues only if the user explicitly wants
tracker mutation; otherwise keep traceability in `.harness`.

## Source Artifact Trace

Linear Plan:
`.harness/linear/2026-05-09-agent-skills-first-principles-factory-gate-linear-plan.md`.

Refactor Program:
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`.

Plugin HE Spec:
`.harness/specs/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-spec.md`.

ADRs: none.

Core Invariants: Phase 1 encodes the decision boundary in routers and advisory
hook context; Phase 2 moves full schema and examples into references and lane
procedures; Phase 3 adds warning-first validator coverage; Phase 4 adds static
behavior-proof eval fixtures. No phase changed generated projections, runtime
mirrors, plugin caches, MCP servers, apps, or Linear state.

Other Source Artifacts:

- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`
- `.harness/review/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan-technical-review.md`
- live Codex hook schema evidence recorded in the plan
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-plan.md`
- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-plan.md`
- `.harness/plan/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-plan.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-eval.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`
- `.harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md`

## Planned Proof Check

Promised Proof From Source Artifacts: routers gain compact gate wording, hook
scripts emit Codex-compatible `SessionStart` context with the gate, focused
tests assert old and new fragments, and changed-file validation passes.

Proof Planned Before Implementation: yes.

Proof Produced: Phase 1 source edits were made, focused Python compile and
pytest passed, `git diff --check` passed, authoring-family changed-file
validation passed after preserving unrelated HE plan context, and plan artifact
lints passed after implementation evidence was recorded.

Proof Missing: live model trajectory, pass@k reporting, and saturation
measurement remain optional follow-up. Phase 4 added static eval fixtures that
require artifact-selection decisions, but those fixtures were not run as live
model trials.

Interpretation: the four-phase program met its planned local proof for
factory-gate availability, procedure wiring, warning-first validation, and
static behavior-proof eval coverage. It should not be used to claim universal
factory correctness.

Blocks Closure: no for local four-phase closure; yes for stronger live-runtime
readiness claims.

## Functional Validation Results

Command or Method:
`python3 -m py_compile Plugins/plugin-factory/hooks/session_start_contract.py Plugins/skill-factory/hooks/session_start_routing.py Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Result: pass.

Evidence: command exited `0`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q`

Result: pass.

Evidence: `11 passed, 8 subtests passed in 0.13s` on the final rerun.

Confidence: high.

Blocks Closure: no.

Command or Method:
`git diff --check`

Result: pass.

Evidence: command exited `0`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh --changed-files Plugins/skill-factory/skills/skill-factory-router/SKILL.md Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md Plugins/skill-factory/hooks/session_start_routing.py Plugins/plugin-factory/hooks/session_start_contract.py Infrastructure/tests/test_plugin_bundled_hooks_contract.py`

Result: pass.

Evidence: final run ended with `pass: all authoring-family skills met
structural contract/security checks`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`

Result: pass.

Evidence: `PASS .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`.

Confidence: high.

Blocks Closure: no.

Command or Method:
`python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`

Result: pass.

Evidence: `PASS .harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`.

Confidence: high.

Blocks Closure: no.

## Eval Gate Matrix

Gate: Phase 1 scope boundary

Expected: implementation edits only the two routers, two hook scripts, focused
hook test, and necessary HE proof artifacts.

Actual: source implementation stayed in the approved Phase 1 source files; the
additional `folded-skill-context.md` change preserved prior `he-plan` context
required by validation.

Status: pass

Evidence: `git diff --name-only` shows Phase 1 files plus harness proof
artifacts; no `.agents/**`, `.skillsets/**`, factory templates, validators,
MCP tools, apps, or eval fixtures were edited for implementation.

Confidence: high.

Blocks Closure: no

Required Action: none; later phases are now covered by their own proof
artifacts.

Gate: Hook runtime output shape

Expected: both hook scripts emit `hookSpecificOutput.hookEventName:
"SessionStart"` and preserve existing `additionalContext`.

Actual: focused tests assert `hookEventName == "SessionStart"` for both
factory hook scripts.

Status: pass

Evidence: `python3 -m pytest Infrastructure/tests/test_plugin_bundled_hooks_contract.py -q` passed.

Confidence: high.

Blocks Closure: no

Required Action: none for Phase 1.

Gate: Advisory versus enforcement split

Expected: routers and hooks introduce the first-principles gate without strict
validator or eval enforcement.

Actual: router and hook wording is advisory; no validator enforcement or
factory eval fixture was added.

Status: pass

Evidence: implementation diff contains router context, hook context, and
focused tests only.

Confidence: high.

Blocks Closure: no

Required Action: implement enforcement only under a later approved phase.

Gate: Behavior-changing eval proof

Expected: full program readiness requires eval coverage proving the gate can
change at least one build, improve-existing, hook, or do-not-build decision.

Actual: Phase 4 added four static behavior-proof fixtures across skillify,
skill-refactor, and plugin-factory-router.

Status: pass with follow-up

Evidence: .harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md and .harness/review/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-technical-review.md.

Confidence: high for static fixture coverage; medium for live runtime behavior.

Blocks Closure: no for local four-phase closure; yes for universal runtime
readiness claims.

Required Action: optional live model eval smoke proof if Jamie wants trajectory
evidence.

## Agentic Eval Validity

Evaluated Capability / Task: factory boundary guidance and bundled
`SessionStart` hook context for first-principles artifact selection.

Task Validity: valid for Phase 1 because the source spec asked for router,
hook, and focused-test updates only.

Outcome Validity: high for Phase 1 because the expected fragments and runtime
hook event field are asserted by tests.

Trajectory / Transcript Evidence: phases 1 through 4 are recorded in local
plan/eval/review artifacts. Live model trajectories were not collected.

Grader Coverage: deterministic tests cover hook JSON output and context
fragments; router text was checked by diff inspection rather than model-graded
evals.

Trial Policy: single deterministic local run is acceptable for this static
context-and-test slice.

Pass@k / Pass^k Reporting: not applicable because no stochastic model eval was
run.

Authorization Validator: user explicitly invoked `$he-work` for implementation
and `$he-eval-report` for proof artifact creation.

Saturation / Maintenance Signal: partially saturated for static coverage; live
model saturation remains optional follow-up.

Blocks Completion: no

Required Action: run live behavior eval before claiming universal factory-gate
readiness.

## Side-Effect Authorization

Protected Action: repo artifact writes only; no external Linear mutation,
stage, commit, push, deletion, or approval action.

User Authorization Evidence: user invoked `$he-work` for implementation and
`$he-eval-report` for eval proof.

Agent Justification: proof artifact records whether Phase 1 is safe to review
and prevents over-claiming broader factory readiness.

External Party Influence: no

Validator Decision: approved

Validator Confidence: high

Suggested Next Step: ask accept, challenge, or rework before any closure claim
is copied to Linear or used for commit/PR messaging.

Blocks Completion: no

## Domain Model Integrity Check

Domain Model Status: complete with follow-up for the four-phase local program.

Bounded Context: `skill-factory` and `plugin-factory` authoring boundaries.

Aggregate / Invariant Proof: the first-principles gate is represented as a
compact decision checkpoint, not as enforcement or a new package model.

Model-Code-Test Language Match: router/hook/test text consistently uses
`first-principles factory gate`, `artifact decision`, `smallest effective
mechanism`, `IMPROVE_EXISTING`, and `DO_NOT_BUILD`.

Translation Boundary: live trajectory proof and strict validator enforcement
remain outside this local closure.

Closure Impact: no local four-phase closure block; broader runtime readiness
requires optional live eval evidence.

Evidence: source diffs and focused hook tests.

Blocks Completion: no

## Drift Validation

Architecture Drift: Improved

Routing Drift: Improved

Context Drift: Neutral

Governance Drift: Neutral

Agent-Native Drift: Improved

Moat Drift: Improved

## Architecture Integrity Check

Conclusion: improved because the gate is placed at factory decision boundaries,
wired into factory procedures, covered by warning-first validation, and backed
by static behavior-proof eval fixtures.

Evidence: router additions and hook context additions only.

Affected Files/Modules: factory routers and factory hook scripts.

Confidence: high.

Blocks Completion: no.

## Routing Determinism Check

Conclusion: improved because routers now name the artifact decision before
handoff while preserving one-lane routing, and Phase 4 route checks verified
the new eval prompts select the intended factory surfaces.

Evidence: both router diffs keep read-only boundaries and add one compact gate
section.

Affected Files/Modules: `skill-factory-router` and `plugin-factory-router`.

Confidence: medium; no executable router behavior test exists in Phase 1.

Blocks Completion: no.

## Context Load Check

Conclusion: neutral because always-visible router additions are short and hook
context additions are compact, but the gate is still extra text.

Evidence: each router received one compact section; each hook received two
short bullets.

Affected Files/Modules: factory routers and hook context strings.

Confidence: medium.

Blocks Completion: no.

## Agent-Native Check

Conclusion: improved because the factories now tell agents to consider
`IMPROVE_EXISTING`, `DOCS_ONLY`, and `DO_NOT_BUILD` rather than defaulting to
more package output.

Evidence: router and hook wording plus focused tests for the non-build terms.

Affected Files/Modules: factory routers, factory hook scripts, and bundled
hook contract tests.

Confidence: high.

Blocks Completion: no.

## Governance Simplicity Check

Conclusion: neutral to improved because Phase 1 adds decision context without
adding a new standalone skill, MCP tool, app, validator, or Linear object.

Evidence: no generated projections, external trackers, or enforcement scripts
were edited.

Affected Files/Modules: source-only Phase 1 files and harness proof artifacts.

Confidence: high.

Blocks Completion: no.

## Moat Protection Check

Conclusion: improved because the factories now encode the repository's stated
preference for small proof-backed capability over package volume.

Evidence: the first-principles gate asks for user outcome, copied assumption,
smallest effective mechanism, artifact decision, and proof before build work.

Affected Files/Modules: factory routers and hook context.

Confidence: high for static factory behavior coverage; medium for full moat
impact until live behavior evals exist.

Blocks Completion: no for local four-phase closure.

## Proof Artifacts

Produced:

- `.harness/plan/2026-05-09-agent-skills-first-principles-factory-gate-phase-1-plan.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-2-eval.md`
- `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-phase-3-eval.md`
- `.harness/evals/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-eval.md`
- `.harness/review/2026-05-13-agent-skills-first-principles-factory-gate-phase-4-technical-review.md`
- focused hook contract test results
- authoring-family changed-file validation result

Required:

- user review or accept/challenge/rework decision for this aggregate eval;
- optional live model eval smoke proof before stronger runtime-readiness claims.

Missing: live model trajectory proof, pass@k reporting, and saturation
measurement.

Planned Before Implementation: yes for phase-local proof; Phase 4 explicitly
made live model trajectory proof optional follow-up.

Blocks Completion: no for local four-phase closure; yes for universal runtime
readiness claims.

Attach or Link Back to Linear: not applicable until Linear objects are created.

## Failures / Regressions

Failure or Regression: initial authoring-family validation failed on an
already-dirty `he-plan` progressive-disclosure issue.

Evidence: first broad gate run reported `he-progressive` failure for
`Plugins/harness-engineering/skills/he-plan/SKILL.md`.

Required Corrective Action: moved the retired `he-plan` context into
`Plugins/harness-engineering/references/folded-skill-context.md` and reran the
authoring-family gate successfully.

Follow-Up Justified: no separate follow-up needed for Phase 1; the repair is
included in this diff because it was required to satisfy canonical validation.

Blocks Closure: no.

## Linear Completion Recommendation

Classification: Complete with follow-up

Recommended Linear Status: no Linear update; if created later for Phase 1,
`Done` or equivalent is reasonable after user acceptance.

Required Linear Comment/Update: none unless the user asks to create or update
Linear.

Issues to Close: none.

Issues to Reopen: none.

Issues to Leave Open: any future Phase 2, Phase 3, or Phase 4 tracking issues.

New Follow-Up Issues: do not create automatically.

Labels to Add/Remove: none.

Milestone Completion: do not complete the proposed `First-Principles Factory
Gate` milestone from Phase 1 alone.

Project Status Change: none.

Status Update Needed: not unless the user wants external tracker state.

Proof Artifacts to Attach or Link: this eval plus the implemented Phase 1 plan.

## Follow-Up Work

Classification: Do Not Create

Target Linear Project: `agent-skills` proposed only.

Parent Issue or Milestone: `First-Principles Factory Gate` proposed only.

Reason: follow-up work is already represented by the staged refactor program;
creating tracker objects now would be external mutation beyond this eval.

Priority: later, gated by user authorization.

Labels: `Architecture`, `Agent-Native`, `Eval`, `Factory`, `Governance` if
Linear tracking is later authorized.

Agent-Safe or Human Review Required: Phase 2 can be agent-assisted; Phase 3
and Phase 4 should require human review because they affect enforcement and
readiness claims.

## Core / ADR Update Recommendation

Core Update: not required for Phase 1.

ADR Update: not required for Phase 1.

Reason: the decision is captured in harness strategy/refactor/spec/plan/eval
artifacts and in factory source guidance; no architectural decision record is
needed until enforcement or runtime behavior changes.

## Evidence & Traceability Matrix

Conclusion: Phase 1 is implemented and safe to review; full factory-gate
completion is not safe to claim.

Fact: both factory routers now include compact first-principles gate sections.

Interpretation: agents invoking the factories have earlier pressure to choose
the smallest artifact, including non-build outcomes.

Assumption: advisory context will improve agent behavior before strict
validation exists.

Evidence: router diffs and hook context tests.

Affected Files/Modules: factory routers, factory hook scripts, focused bundled
hook tests, and harness proof artifacts.

Command or Inspection Method: diff inspection, focused pytest, py_compile,
`git diff --check`, changed-file authoring-family validation, plan artifact
lints.

Confidence: high for Phase 1, medium for broader behavior impact.

Operational Impact: improves factory guidance without requiring `plugin_hooks`
to be enabled or changing package generation.

Blocks Completion: no for Phase 1; yes for full factory-gate program closure
until later behavior eval proof exists.
