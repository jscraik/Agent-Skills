---
title: Learning-Preserving Skill Design Pilot
type: feat
status: draft
date: 2026-03-10
origin: docs/brainstorms/2026-03-10-learning-preserving-skills-brainstorm.md
risk: medium
spec_depth: lite
---

# Learning-Preserving Skill Design Pilot Spec

## Table of Contents
- [Enhancement Summary](#enhancement-summary)
- [Problem Statement](#problem-statement)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [System Boundary](#system-boundary)
- [Core Domain Model](#core-domain-model)
- [Main Flow / Lifecycle](#main-flow--lifecycle)
- [Interfaces and Dependencies](#interfaces-and-dependencies)
- [Invariants / Safety Requirements](#invariants--safety-requirements)
- [Failure Model and Recovery](#failure-model-and-recovery)
- [Observability](#observability)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)

## Enhancement Summary

**Deepened on:** 2026-03-10
**Key areas improved:** boundary clarity, posture-selection rules, runtime lifecycle, degraded-state handling, observability, and validation realism

- Added explicit compatibility rules between `LearningPosture` and `DelegationMode`, including invalid and degraded combinations.
- Expanded the lifecycle from repo-definition only into run-time posture selection, application, evaluation, observation, and review.
- Strengthened failure, recovery, and conformance rules for missing posture metadata, weak telemetry, and pilot drift.

## Problem Statement

`agent-skills` already has strong contracts for routing, delegation mode, question timing, promotion gates, and human oversight. However, it does not yet have an explicit contract for when a skill should optimize for preserving human understanding instead of only maximizing speed or task completion.

That gap creates two risks:
- high-quality execution skills can still encourage over-delegation in unfamiliar domains
- evaluation and telemetry can report strong artifact quality while missing whether the human can still supervise, debug, or explain the result

The pilot must define a repo-native way to represent learning-preserving behavior without breaking the current canonical delegation vocabulary of `autopilot | co-pilot | manual`.

## Goals

- Define a pilot contract for learning-preserving behavior that is orthogonal to existing delegation/runtime mode.
- Preserve existing skill-graph, question-lifecycle, and promotion-gate contracts.
- Standardize a small set of interaction patterns that improve human oversight in unfamiliar or debugging-heavy work.
- Extend pilot evaluation and telemetry so the repo can compare learning-preserving behavior with throughput-oriented behavior.
- Produce a contract that `/prompts:workflow-plan` can use without inventing pilot scope, ownership, or validation rules.

## Non-Goals

- Do not replace canonical delegation mode values in task profiles or runtime artifacts.
- Do not require every skill in the repo to become teaching-oriented.
- Do not redesign the recursive skill loop, promotion system, or question-lifecycle runtime.
- Do not introduce a repo-wide migration in this phase.
- Do not define implementation tasks, file diffs, or rollout sequencing in this spec.

## System Boundary

Owned by this pilot:
- The repo-level definition of a `learning posture` concept for pilot skills.
- The canonical vocabulary, meaning, and defaults for pilot learning-posture values.
- The pilot skill set and the contract each pilot skill must express.
- The evaluation dimensions and telemetry expectations required to assess the pilot.
- The observability and validation signals used to judge whether the pilot is safe and useful.

Not owned by this pilot:
- Runtime execution orchestration beyond existing delegation modes.
- Question timing policy, which remains governed by the question lifecycle contract.
- Promotion decision mechanics, which remain governed by existing human-gated promotion workflows.
- Full-repo adoption of the learning-posture contract.
- Changes to external tooling or external model behavior.

## Core Domain Model

### Primary entities

- `DelegationMode`
  - Existing canonical runtime mode from task profiles and skill-graph artifacts.
  - Allowed values remain `autopilot | co-pilot | manual`.

- `LearningPosture`
  - New pilot-only contract that describes how a skill should balance explanation, prediction, generation, and review when the skill is in use.
  - Canonical values for the pilot:
    - `learn`
    - `guided`
    - `execute`

- `LearningPosturePolicy`
  - Repo-level definition of what each `LearningPosture` value requires and forbids.
  - Lives as canonical prose in repo docs, not as ad hoc per-skill phrasing.

- `PilotSkill`
  - A selected skill participating in the pilot and expected to declare learning-preserving behavior.
  - Initial pilot set:
    - `Skills/skill-builder`
    - `frontend/tools/agentation`
    - `Skills/systematic-debugging`
    - `interview/interview-me`

- `LearningEvidence`
  - Evaluation or telemetry signal showing whether a skill preserved human oversight and understanding.
  - Includes eval results, declared posture, and tagged interaction patterns.

### Semantics

- `learn`
  - Use when the primary goal is conceptual understanding, diagnosis skill, or safe onboarding in an unfamiliar domain.
  - Requires prediction, explanation, and explain-back style behavior before or immediately after generation.

- `guided`
  - Use when the task should still move forward efficiently, but the human must remain able to inspect, supervise, and intervene confidently.
  - Allows generation, but requires compact rationale, assumptions, and review framing.

- `execute`
  - Use when throughput is the priority and the user or operator already has enough context to supervise the result.
  - Explanation is still honest and sufficient, but the contract does not force learning-oriented checkpoints by default.

### Normalization rules

- `LearningPosture` is a second dimension, not a replacement for `DelegationMode`.
- Pilot artifacts must never serialize `LearningPosture` into the `delegation.mode` field.
- If a pilot skill omits `LearningPosture`, the pilot treats it as `unspecified` and the skill fails pilot conformance checks.
- Existing `autopilot` skills may still exist in the pilot, but they must explicitly warn when the mode optimizes for throughput rather than learning.

### Compatibility matrix

Expected pairings in the pilot:

| Delegation mode | Allowed learning posture | Notes |
| --- | --- | --- |
| `manual` | `learn`, `guided`, `execute` | Preferred for onboarding and debugging-heavy learning cases |
| `co-pilot` | `learn`, `guided`, `execute` | Default pilot pairing for mixed progress plus oversight |
| `autopilot` | `execute` | Canonical execution-first pairing in the pilot |

Disallowed or degraded pairings:
- `autopilot + learn` is invalid in v1.
- `autopilot + guided` is degraded unless the skill explicitly limits scope to critique/review-style behavior and emits a throughput-priority warning.
- `manual + execute` is valid, but the skill must not silently omit review context when the surrounding task is unfamiliar or debugging-heavy.

### Selection rules

- Repo docs define the vocabulary and required semantics.
- Each pilot skill owns its declared default posture for supported task shapes.
- The runtime is not required to auto-classify posture in v1.
- If task context and declared defaults conflict, the pilot must choose the safer interpretation:
  - prefer `learn` over `guided`
  - prefer `guided` over `execute`
- If no safe posture can be determined, the run is treated as `guided` for pilot-evaluation purposes and must surface a conformance warning.

## Main Flow / Lifecycle

### Lifecycle states

- `S0_DEFINED_REPO_LEVEL`
  - The repo-level contract and vocabulary are defined.

- `S1_DECLARED_IN_PILOT_SKILL`
  - A pilot skill declares a learning posture and the required behavior patterns for that posture.

- `S2_SELECTED_FOR_RUN`
  - A pilot skill invocation has an explicit or inferred posture selection for the current task.

- `S3_APPLIED_DURING_RUN`
  - The skill actually applies the required posture behaviors during the run.

- `S4_EVALUATED`
  - The pilot skill has eval coverage for learning-preserving behavior, not only output correctness.

- `S5_OBSERVED`
  - Telemetry or structured run signals capture how the pilot skill behaved in practice.

- `S6_REVIEWED`
  - Pilot results are reviewed against existing human-gated standards and judged suitable for broader reuse.

- `S7_PROMOTION_READY`
  - The concept is stable enough to inform wider standardization or broader rollout planning.

### Allowed transitions

- `S0 -> S1`
- `S1 -> S2`
- `S2 -> S3`
- `S3 -> S4`
- `S4 -> S5`
- `S5 -> S6`
- `S6 -> S7`
- `S6 -> S1` when contract changes are required after review findings

Disallowed transitions:
- `S1 -> S4` without run-time posture application evidence.
- `S2 -> S5` without evaluation coverage.
- `S3 -> S7` without human review.

### Step contract

1. Repo-level definition
- Define the canonical `LearningPosture` vocabulary and behavior expectations once.
- Publish the contract in the repo-level skill-graph docs.

2. Pilot skill declaration
- Each pilot skill declares which posture(s) it supports and how behavior changes by posture.
- Pilot skills must preserve current delegation/runtime semantics.

3. Run-time posture selection
- For each pilot invocation, posture must be explicit or safely inferred from declared skill guidance.
- The run must know whether it is operating in `learn`, `guided`, or `execute`.
- Unsupported posture combinations must fail closed into warning or invalid states rather than being silently normalized.

4. Run-time posture application
- `learn` requires prediction, explanation, and review-oriented behavior before or immediately after generation.
- `guided` requires rationale, assumptions, and intervention-friendly framing around generated outputs.
- `execute` may optimize for speed, but must still remain auditable and honest about assumptions.

5. Evaluation
- Pilot evals must check both task quality and oversight-preserving behaviors.
- Eval failures in learning-preserving criteria do not silently downgrade to output-only success.

6. Observation
- Pilot runs record enough structured signal to distinguish:
  - conceptual inquiry
  - hybrid explanation plus generation
  - full delegation
  - AI-led debugging loops

7. Review
- Human review determines whether the pilot contract is reusable, safe, and worth broader propagation.
- Broader adoption remains gated on review evidence, not optimistic prose.

## Interfaces and Dependencies

### Primary repo interfaces

- `docs/skill-graphs/index.md`
  - Canonical repo-level home for the learning-posture contract.

- `README.md`
  - Contributor-facing summary of the concept and its intended use.

- `Infrastructure/templates/SKILL.md.template`
  - Propagation point for future skill authoring once the pilot contract is stable.

- `Infrastructure/references/task-profile.json`
  - Candidate home for machine-readable learning-posture metadata used by evaluation or telemetry tooling.

### Existing contracts this spec must preserve

- `docs/skill-graphs/schemas/task-profile.schema.md`
  - Delegation mode remains canonical and unchanged.

- `docs/skill-graphs/question-lifecycle.md`
  - Question timing remains a runtime-owned concern.

- `docs/skill-graphs/workflows/promotion-gate.md`
  - Promotion remains human-gated.

- `docs/skill-graphs/workflows/reviewer-rubric.md`
  - Reviewer criteria remain explicit and evidence-based.

- `Infrastructure/scripts/validation-and-linting/verify_skill_catalog_freshness.py`
  - Existing metadata quality gates remain in effect.

- `Infrastructure/scripts/validate_all.sh`
  - Broader repo validation remains the final guard before completion.

### Dependency assumptions

- Pilot skills already have `Infrastructure/references/task-profile.json` and existing evaluation structures.
- Existing skill telemetry and promotion workflows are the baseline operating environment.
- The pilot may add new metadata or checks, but must remain compatible with current repo validation flows.

### Trust boundary assumptions

- User prompts, annotation text, failure logs, and generated code remain untrusted inputs.
- The pilot may classify interaction patterns, but must not treat self-reported explanation quality as sufficient evidence on its own.
- Repo-level docs remain the source of truth for pilot semantics; per-skill prose may specialize behavior but must not contradict canonical meanings.

## Invariants / Safety Requirements

- `DelegationMode` and `LearningPosture` must remain separate concepts.
- No pilot artifact may overload or redefine `delegation.mode`.
- A pilot skill must not claim to preserve learning while omitting explanation or review obligations for `learn` and `guided` posture.
- Autonomy-first skills must clearly signal when they optimize for throughput rather than understanding.
- The pilot must remain human-gated for repo-wide adoption decisions.
- The pilot must not require invasive runtime changes to question ownership, promotion authority, or control precedence.
- Evaluation must not treat artifact correctness as sufficient proof of preserved human oversight.
- Invalid posture/mode combinations must fail closed into explicit warnings or blocked pilot conformance, not silent coercion.
- Missing posture declaration for a pilot skill is a pilot-conformance failure, not a harmless omission.

## Failure Model and Recovery

### Failure classes

- `contract_drift`
  - Repo-level docs, skill template, and pilot skills define inconsistent posture semantics.

- `mode_collision`
  - A draft implementation mixes `LearningPosture` into `delegation.mode` or otherwise conflicts with canonical runtime mode.

- `selection_ambiguity`
  - The pilot cannot tell which posture should apply to a run, or the declared/default posture conflicts with the task shape.

- `eval_coverage_gap`
  - Pilot skills declare posture support but lack matching eval coverage.

- `telemetry_ambiguity`
  - Run signals cannot distinguish explanation-oriented behavior from pure delegation.

- `scope_bloat`
  - Pilot changes drift toward repo-wide migration or runtime redesign.

### Recovery rules

- On `contract_drift`
  - Treat the repo-level contract as authoritative and realign pilot skill wording before expansion.

- On `mode_collision`
  - Fail the pilot change and revert to canonical delegation semantics.
  - No compatibility shim may silently reinterpret runtime mode values.

- On `selection_ambiguity`
  - Fall back to `guided` for pilot-evaluation purposes.
  - Emit a conformance warning and require explicit clarification in the affected pilot skill contract.

- On `eval_coverage_gap`
  - Block pilot completion until the affected skill has explicit learning-preserving evals.

- On `telemetry_ambiguity`
  - Mark the pilot result as partial rather than successful.
  - Prefer fewer, clearer interaction tags over noisy or weak signals.

- On `scope_bloat`
  - Return to pilot-only scope and defer broader migration decisions to a later spec.

## Observability

Minimum observability required for the pilot:

- `declared_learning_posture`
  - Whether each pilot skill declares a posture contract and where it is defined.

- `selected_learning_posture`
  - Which posture a pilot run actually used.

- `posture_eval_result`
  - Whether the pilot skill passes the required learning-preserving eval checks.

- `interaction_pattern_tags`
  - Whether observed behavior looked like:
    - `conceptual_inquiry`
    - `explain_then_generate`
    - `generate_then_explain`
    - `full_delegation`
    - `ai_led_debugging`

- `posture_warning_presence`
  - Whether execution-first or autonomy-first skills clearly warn when throughput is prioritized over learning.

- `pilot_conformance_summary`
  - One artifact or summary view showing posture declaration, eval coverage, telemetry coverage, and conformance state for each pilot skill.

- `invalid_pairing_count`
  - Count of pilot runs or declarations that attempted a disallowed mode/posture combination.

- `telemetry_coverage_ratio`
  - Share of pilot runs that emitted enough signal to classify interaction patterns confidently.

Observability rules:
- Pilot observability should reuse existing repo artifact patterns where possible.
- New telemetry must stay structured and machine-diffable.
- Missing observability for a pilot skill is a degraded state, not silent success.
- Conformance summaries must distinguish `pass`, `partial`, and `blocked` rather than collapsing all non-pass outcomes into one bucket.

## Acceptance and Test Matrix

| Area | Requirement | Validation expectation |
| --- | --- | --- |
| Vocabulary | `LearningPosture` values are explicit and distinct from delegation mode | Spec and pilot docs use `learn | guided | execute` consistently |
| Boundary | Delegation/runtime mode remains canonical | No pilot contract rewrites `autopilot | co-pilot | manual` semantics |
| Compatibility | Invalid or degraded combinations are explicit | `autopilot + learn` is blocked; degraded pairings emit warnings |
| Repo ownership | Repo-level canonical home is explicit | Spec points to `docs/skill-graphs/index.md` as primary home |
| Pilot scope | Initial pilot skill set is concrete | Spec names four pilot skills |
| Selection | Run-time posture can be determined safely | Spec defines defaults, safer fallback order, and ambiguity handling |
| Skill contract | Pilot skills must declare posture support and behavior expectations | Planning can map this into specific file changes without inventing new rules |
| Evaluation | Learning-preserving eval dimensions are required | Spec names explanation, code reading, debugging independence, and delegation risk |
| Observability | Pilot behavior is observable beyond output success | Spec requires structured interaction pattern tags, selected posture, and conformance summary |
| Safety | Human-gated review remains intact | Spec preserves promotion and question-lifecycle ownership boundaries |
| Recovery | Failure classes have explicit responses | Spec defines block/partial/re-align behavior for each failure class |

## Open Questions

- Should pilot machine-readable posture metadata live only in `Infrastructure/references/task-profile.json`, or should there also be a derived artifact for telemetry tooling?
- What is the smallest useful implementation of `pilot_conformance_summary` that fits existing state-map and telemetry workflows?
- Should `generate_then_explain` and `explain_then_generate` remain separate telemetry tags, or collapse into one hybrid-explanation family if signal quality is weak?

These questions do not block planning. They affect implementation shape, not the core contract.

## Definition of Done

This spec is done when:
- the pilot concept is defined clearly enough that planning does not need to guess about vocabulary, ownership, or scope
- the relationship between `LearningPosture` and `DelegationMode` is explicit and stable
- pilot skills are named
- required evaluation and observability expectations are explicit
- major failure modes and recovery rules are defined
- the next step can safely be `/prompts:workflow-plan` without reopening brainstorm-level ambiguity
