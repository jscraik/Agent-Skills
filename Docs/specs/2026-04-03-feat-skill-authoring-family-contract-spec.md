---
title: Skill Authoring Family Contract and Iteration Spec
type: feat
status: draft
date: 2026-04-04
origin: docs/brainstorms/2026-04-03-skill-authoring-family-contract-requirements.md
risk: medium
spec_depth: full
ui_required: false
deepened: 2026-04-04
---

# Skill Authoring Family Contract and Iteration Spec

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

**Deepened on:** 2026-04-04  
**Mode:** targeted-confidence  
**Key areas improved:** comparison-state semantics, baseline and input parity rules, blocked-state handling, observability signals, and acceptance precision

- Preserved the current family routing split instead of reopening the consolidation debate.
- Added an explicit `HandoffPackage` contract so `skill-creator` does not end at `quick_validate.py` with only implied escalation.
- Defined `skill-builder` as the canonical owner of the non-trivial iterative improvement loop, including paired baseline comparisons, timing and token evidence when available, qualitative plus quantitative review, description tuning, and wider reruns.
- Kept install and plugin packaging as downstream lifecycle states, not alternate authoring owners for unfinished or unvalidated skills.
- Tightened the adoption posture so the repo can import high-value Anthropic workflow ideas without cloning Anthropic's role model, file layout, or helper surface wholesale.
- Added explicit comparison-parity, round-state, and blocked-readiness rules so planning can distinguish a valid draft, a meaningful comparison, and a downstream-ready skill.

## Problem Statement

The skill-authoring family is now clearer at the routing level than it was before:

- `skill-creator` owns starter authoring and scaffold-bound edits in [Skills/skill-creator/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-creator/SKILL.md#L1)
- `skill-builder` owns lifecycle hardening, validators, evals, and standalone packaging in [Skills/skill-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/SKILL.md#L1)
- `skill-installer` owns already-valid install and import execution in [Skills/skill-installer/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-installer/SKILL.md#L1)
- `plugin-builder` owns plugin packaging once the deliverable boundary is a plugin in [Skills/plugin-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/plugin-builder/SKILL.md#L1)

That routing work solved the major family-overlap problem. The remaining weakness is loop maturity rather than role ambiguity.

Current repo evidence shows:

- `skill-creator` still ends primarily with starter drafting plus `quick_validate.py` in [Skills/skill-creator/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-creator/SKILL.md#L373)
- `skill-builder` already has validators, smoke and release eval modes, and description optimization hooks in [Skills/skill-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/SKILL.md#L247), but does not yet expose one explicit iterative loop that compares candidate behavior against a baseline and bundles the resulting evidence coherently
- the seam between creation and hardening is described, but not yet captured as a durable artifact that a maintainer or planner can rely on

The result is a contract gap:

- first-draft creation can succeed without preserving the exact context the next stage needs
- hardening can happen without a clearly specified paired-comparison loop
- planners would still have to invent handoff format, evidence expectations, and baseline rules ad hoc

This spec closes that gap without undoing the family split that now works.

## Goals

- Preserve the current family split and existing routing contract as the baseline.
- Define the canonical creator-to-builder handoff artifact for non-trivial skills.
- Define the canonical `skill-builder` iterative improvement loop for non-trivial skill hardening.
- Specify how baseline comparison works for new skills versus existing skills.
- Specify the minimum evidence bundle required to judge whether a skill revision is actually better.
- Keep installation and plugin packaging as downstream lifecycle states gated by validity evidence.
- Keep the upgraded loop understandable to less technical users, not only maintainers steeped in eval jargon.
- Reuse repo-native validation, eval, and reporting surfaces where practical so the contract fits this repo's existing architecture.

## Non-Goals

- Do not collapse `skill-creator` and `skill-builder` into one end-to-end surface in this phase.
- Do not redesign the whole repo into a generic skill-evals platform.
- Do not change the canonical owner of pure installation or pure plugin packaging work.
- Do not specify file-by-file implementation sequencing; that belongs to planning.
- Do not require a dedicated UI spec; this is a workflow and system contract with `ui_required: false`.
- Do not clone Anthropic's directory layout, script names, or single-surface operating model literally.

## System Boundary

Owned by this spec:

- the preserved routing and ownership relationship across `skill-creator`, `skill-builder`, `skill-installer`, and `plugin-creator` (active gate family); `plugin-builder` remains an adjacent handoff surface for full plugin packaging and is not a gate-family member
- the creator-to-builder handoff contract for non-trivial skills
- the `skill-builder` iteration loop for baseline comparison, evidence capture, review, tuning, and reruns
- the rules for when a skill is ready to hand off into install/import or plugin packaging
- the minimum observability and acceptance requirements that make the upgraded loop planning-ready

Not owned by this spec:

- specific code patches to `SKILL.md`, `Infrastructure/references/evals.yaml`, or helper scripts
- a repo-wide redesign of every skill eval artifact
- unrelated routing behavior outside the skill-authoring family
- UI component or design-system contracts
- future family consolidation or deprecation strategy

## Core Domain Model

### Primary entities

- `SkillSurface`
  - One discoverable authoring-family skill surface.
  - Phase-one members (active gate family):
    - `skill-creator`
    - `skill-builder`
    - `skill-installer`
    - `plugin-creator`
  - Adjacent handoff surface (not a gate-family member):
    - `plugin-builder` — full plugin packaging; valid handoff target from `skill-builder` once lifecycle validity is established

- `PrimaryJob`
  - The strongest lifecycle responsibility of a `SkillSurface`.
  - Required phase-one values:
    - `starter_authoring`
    - `expert_lifecycle_maintenance`
    - `skill_installation`
    - `plugin_scaffolding`
    - `plugin_packaging`
  - `authoring-family-gate` CI contract must validate schema parity for active gate members (`skill-creator`, `skill-builder`, `skill-installer`, `plugin-creator`) so `PrimaryJob` and routing fields stay harmonized across all four.

- `RoutingIntent`
  - The normalized dominant user intent already governed by the current family contract.
  - Required phase-one values:
    - `create_skill`
    - `improve_skill`
    - `audit_or_validate_skill`
    - `install_skill`
    - `package_standalone_skill`
    - `package_as_plugin`
    - `mixed_authoring_and_install`

- `HandoffPackage`
  - The explicit creator-to-builder artifact produced when non-trivial skill work moves beyond starter authoring.
  - Phase-one canonical representation:
    - a dedicated repo-visible artifact file referenced by the creator-stage output
  - Required minimum fields:
    - `skill_goal`
    - `boundary_summary`
    - `trigger_contexts`
    - `resource_inventory`
    - `starter_prompts`
    - `known_risks_or_unknowns`
    - `validation_state`
    - `authoring_state`
  - This is a lifecycle artifact, not merely a chat summary.

- `StarterPromptSet`
  - The initial 2-3 realistic user prompts or prompt candidates that represent how the skill should be exercised once it reaches `skill-builder`.
  - Must reflect plausible user wording rather than synthetic lint-check phrasing.

- `BaselineType`
  - The comparison target used by `skill-builder` in a given evaluation round.
  - Required phase-one values:
    - `no_skill`
    - `prior_skill_snapshot`
    - `neutral_repo_baseline`
  - `neutral_repo_baseline` is only valid when a comparable no-skill path does not exist and a human-approved planning decision records:
    - why `no_skill` and `prior_skill_snapshot` are not legitimate comparisons
    - what neutral target is being used
    - why the chosen target preserves comparison parity well enough for the round

- `IterationRound`
  - One bounded `skill-builder` improvement cycle over a candidate skill version.
  - Required fields:
    - `candidate_version`
    - `baseline_type`
    - `eval_prompt_set`
    - `comparison_inputs`
    - `quantitative_results`
    - `qualitative_review`
    - `tuning_changes`
    - `round_decision`

- `ComparisonInputs`
  - The normalized set of prompts, files, fixtures, and relevant environment assumptions that both candidate and baseline runs must share for a valid comparison.
  - Allowed phase-one differences:
    - skill under test
    - baseline target
  - Disallowed phase-one differences:
    - materially different prompts
    - materially different input artifacts
    - hidden context only one side receives

- `IterationRoundState`
  - The lifecycle state of one comparison round.
  - Required phase-one values:
    - `prepared`
    - `running`
    - `evidence_captured`
    - `reviewed`
    - `decision_recorded`
    - `blocked`

- `EvalEvidenceBundle`
  - The combined evidence package used to judge whether the candidate is better than the baseline.
  - Required phase-one contents:
    - prompt set
    - comparison inputs
    - candidate outputs
    - baseline outputs
    - assertion or grading outcomes when applicable
    - timing and token usage when the runner exposes them
    - explicit unavailable marker when the runner cannot expose those metrics
    - reviewer-visible qualitative comparison surface
    - round decision with rationale

- `RoundDecision`
  - The next step chosen after an `IterationRound`.
  - Required phase-one values:
    - `iterate_again`
    - `widen_eval_set`
    - `ready_for_install_handoff`
    - `ready_for_plugin_handoff`
    - `stop_blocked`

- `ContractValidityEvidence`
  - The validator-visible proof that a skill is valid enough to proceed to downstream lifecycle work.
  - Required phase-one minimum evidence:
    - starter validation outcome for creator-stage work
    - `skill-builder` smoke or release eval evidence for the relevant risk level
    - current routing and boundary contract compliance
    - provenance details when imported or external material is involved

### Canonical routing roles for phase one

| Skill surface                    | Primary job                    | Strongest triggers                                                                                                                                   | Non-triggers                                                                                |
| -------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `skill-creator`                  | `starter_authoring`            | create a first draft, finish a just-created scaffold, turn an already-understood workflow into a starter skill shape                                 | benchmark-heavy hardening, install execution, plugin packaging, broad lifecycle audit       |
| `skill-builder`                  | `expert_lifecycle_maintenance` | improve routing, harden workflow, compare candidate vs baseline behavior, evaluate, package a validated standalone skill, prepare downstream handoff | pure install/import, plugin conversion without lifecycle judgment, unrelated feature work   |
| `skill-installer`                | `skill_installation`           | install, import, list, project, or repair visibility for an already-valid skill package                                                              | first-draft creation, lifecycle benchmarking, plugin packaging                              |
| `plugin-creator` _(gate member)_ | `plugin_scaffolding`           | scaffold a new plugin skeleton, generate a valid `plugin.json`, add or update local marketplace entries                                              | skill lifecycle hardening, install execution, full plugin packaging and governance programs |
| `plugin-builder` _(adjacent)_    | `plugin_packaging`             | convert or package a contract-valid standalone skill as a full plugin with governance checks                                                         | first-draft creation, lifecycle benchmarking, install-only work; not a gate-family member   |

## Main Flow / Lifecycle

### 1. Preserve the current routing contract

The existing family routing contract remains the baseline:

- `create_skill` routes to `skill-creator`
- `improve_skill` and `audit_or_validate_skill` route to `skill-builder`
- `install_skill` routes to `skill-installer`
- `package_standalone_skill` routes to `skill-builder`
- `package_as_plugin` routes to `plugin-builder`

Mixed-intent rules remain in force:

- lifecycle-shaping work wins over install execution
- plugin packaging does not preempt unresolved lifecycle judgment
- low-confidence or deliverable-ambiguous requests still fail to route clarification rather than guessed ownership

### 2. Creator stage: capture and scaffold

`skill-creator` owns the first-draft stage.

Required creator-stage behavior:

- extract intent from the current conversation before re-asking obvious questions
- establish the starter skill boundary, likely trigger contexts, and reusable resource inventory
- scaffold or finish the starter skill shape
- run creator-stage validation such as `quick_validate.py`
- decide whether the work can safely stop at starter authoring or whether lifecycle hardening is now the dominant concern

Stop rule:

- if the work remains truly scaffold-bound and no lifecycle hardening, routing, packaging, or benchmark concern is requested, `skill-creator` may finish without a downstream handoff
- otherwise, `skill-creator` must produce a `HandoffPackage` and route the next lifecycle stage to `skill-builder`

### 3. Creator-to-builder handoff

The handoff from `skill-creator` to `skill-builder` is a normal lifecycle transition for non-trivial skills, not an exceptional recovery path.

Required handoff fields:

- `skill_goal`
  - what the skill is intended to enable
- `boundary_summary`
  - what is in scope, out of scope, and any explicit deliverable constraints
- `trigger_contexts`
  - the user phrases or contexts that should and should not trigger the skill
- `resource_inventory`
  - draft or existing `Infrastructure/scripts/`, `Infrastructure/references/`, `assets/`, and helper metadata that matter to the next stage
- `starter_prompts`
  - 2-3 realistic prompts or prompt candidates that represent real user behavior
- `known_risks_or_unknowns`
  - routing ambiguity, likely failure areas, subjective judgment points, or open questions
- `validation_state`
  - what starter validation ran and whether it passed
- `authoring_state`
  - whether the candidate is brand-new, scaffold-complete, or partially hardened already

Handoff integrity rules:

- the handoff package must be durable and inspectable by planning or later maintainers
- the smallest durable representation for phase one is a dedicated repo-visible artifact file rather than an inline-only chat summary or ad hoc markdown fragment
- the handoff must minimize rediscovery but must not smuggle in a predetermined success judgment
- the handoff package is complete only when it contains enough context for `skill-builder` to begin comparative iteration without re-interviewing the whole skill from scratch

### 4. Builder stage: run the iterative improvement loop

`skill-builder` is the canonical owner of the non-trivial iterative loop.

Each `IterationRound` must follow this contract:

1. **Prepare the prompt set**
   - refine or confirm realistic prompts from the `HandoffPackage`
   - expand only if the initial prompts are too weak to expose meaningful differences
   - keep the first non-trivial round aligned with current Codex guidance to start from 2 to 3 concrete use cases before broader expansion

2. **Freeze the comparison inputs**
   - record the prompt set, relevant input artifacts, and any material environment assumptions as `ComparisonInputs`
   - the canonical comparison path must keep these inputs fixed across candidate and baseline runs inside the round
   - if a prompt, fixture, or environment assumption changes materially, treat that as a new round rather than silently mixing evidence

3. **Select the baseline**
   - new skill: compare against `no_skill` unless planning defines a stronger neutral baseline
   - existing skill: compare against `prior_skill_snapshot`
   - if neither comparison is valid, planning must define the allowed `neutral_repo_baseline`; the round must not fabricate one informally

4. **Run candidate and baseline in the same round**
   - candidate and baseline runs must be comparable within one evaluation window
   - the loop must avoid sequential "candidate first, baseline later if time" behavior for the canonical comparison path
   - the round enters `running` only once both sides of the comparison have started or the workflow has explicitly entered `blocked`

5. **Capture evidence**
   - assertion or grading results when appropriate
   - timing and token usage when the runner exposes them
   - explicit unavailable marker when those metrics are not exposed by the runner or environment
   - qualitative output comparison suitable for human review
   - the round enters `evidence_captured` only when both candidate and baseline evidence are present or the bundle explicitly records why one side could not complete

6. **Review and tune the skill**
   - review the evidence bundle before changing the skill again
   - route and description tuning are part of the canonical loop, not a side quest
   - each non-trivial round must explicitly assess whether route or description tuning is needed
   - actual route or description edits are mandatory only when the evidence shows trigger weakness, route ambiguity, or materially misleading descriptions
   - tuning may also include prompt shaping, eval refinement, or bundled-resource adjustments when the evidence justifies it
   - if the eval set is non-discriminating or too narrow, repair the eval set before claiming the candidate is better
   - the round enters `reviewed` only after the candidate-versus-baseline difference has been examined qualitatively and quantitatively where possible

7. **Make a round decision**
   - `iterate_again` when the evidence is still mixed or the candidate clearly needs another pass
   - `widen_eval_set` when small-sample evidence is promising and the next best move is broader coverage
   - `ready_for_install_handoff` only when the skill is contract-valid and the remaining work is install/import/visibility
   - `ready_for_plugin_handoff` only when the skill is contract-valid and the remaining work is plugin packaging
   - `stop_blocked` when tooling, runner behavior, or unresolved contract questions prevent trustworthy progress
   - the round enters `decision_recorded` only when the decision and rationale are preserved in the evidence bundle or a repo-visible summary artifact

### 5. Wider reruns happen after directional confidence

The loop must not jump straight from starter prompts to wide release-style coverage without first establishing directional confidence.

Required widening rule:

- a wider rerun is appropriate only after a smaller comparison round provides enough evidence that the candidate is plausibly better or at least meaningfully different from the baseline
- if the small round is inconclusive because prompts, assertions, or grading are weak, repair the comparison first rather than scaling noise
- when the skill risk justifies it, the wider rerun should expand beyond happy-path prompts to include representative edge cases and adversarial or failure-oriented cases rather than only more of the same prompt shape

### 6. Downstream lifecycle handoffs stay gated

Downstream handoff rules:

- `skill-builder` may hand off to `skill-installer` only when `ContractValidityEvidence` exists and the remaining work is install/import/projection/visibility
- `skill-builder` may hand off to `plugin-builder` only when `ContractValidityEvidence` exists and the remaining work is plugin packaging
- downstream surfaces must not self-attest lifecycle validity when the comparative loop is incomplete or inconclusive
- a `quick_validate.py` pass or equivalent creator-stage success alone is never sufficient downstream validity evidence for install or plugin handoff

## Interfaces and Dependencies

### Repo interfaces

- [Skills/skill-creator/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-creator/SKILL.md)
  - creator-stage contract and current `quick_validate.py` endpoint
- [Skills/skill-creator/Infrastructure/scripts/quick_validate.py](/Users/jamiecraik/dev/agent-skills/Skills/skill-creator/Infrastructure/scripts/quick_validate.py)
  - creator-stage validation helper
- [Skills/skill-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/SKILL.md)
  - lifecycle hardening, eval, and standalone packaging surface
- [Skills/skill-builder/Infrastructure/references/evals.yaml](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/references/evals.yaml)
  - current eval-manifest surface that can absorb the upgraded iterative loop
- [Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py](/Users/jamiecraik/dev/agent-skills/Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py)
  - current runner surface for smoke and release evals
- [Skills/skill-installer/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/skill-installer/SKILL.md)
  - downstream install/import surface
- [Skills/plugin-builder/SKILL.md](/Users/jamiecraik/dev/agent-skills/Skills/plugin-builder/SKILL.md)
  - downstream plugin packaging surface

### Source contract boundary

- This spec is the authoritative contract for the family's creator-to-builder iteration upgrade.
- The earlier routing and ownership decisions remain authoritative here unless explicitly replaced by a newer spec.
- Mirrored docs, `SKILL.md` descriptions, `agents/openai.yaml` metadata, eval manifests, and helper outputs are subordinate views that must not silently contradict this spec.

### External guidance dependencies

This spec uses the Anthropic pinned `skill-creator` reference as a workflow-quality source, not as a packaging or ownership template:

- [Anthropic `skill-creator` at pinned commit `98669c11ca63e9c81c11501e1437e5c47b556621`](https://github.com/anthropics/skills/tree/98669c11ca63e9c81c11501e1437e5c47b556621/skills/skill-creator)

This spec also depends on current official OpenAI and Codex guidance as of **2026-04-04**:

- [Codex best practices: Turn repeatable work into skills](https://developers.openai.com/codex/learn/best-practices/#turn-repeatable-work-into-skills)
- [Codex customization: Skills](https://developers.openai.com/codex/concepts/customization/#skills)
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices/#example-qa-over-docs)

Imported ideas allowed by this spec:

- explicit intent capture from conversation context
- paired candidate-versus-baseline comparison
- timing and token evidence when available
- qualitative plus quantitative review
- description optimization as a named loop stage

Imported guidance from current official docs:

- keep each skill scoped to one job
- start from 2 to 3 concrete use cases and trigger phrases a user would actually say
- keep descriptions focused on what the skill does and when to use it
- grow eval sets over time with representative typical, edge, and adversarial cases when risk justifies it

Explicitly rejected imports:

- collapsing `skill-creator` and `skill-builder` into one owner
- adopting Anthropic's file layout, workspace layout, or viewer contract literally where repo-native surfaces already exist

## Invariants / Safety Requirements

- The family split remains intact: `skill-creator` creates, `skill-builder` hardens, `skill-installer` installs, `plugin-creator` scaffolds plugins. `plugin-builder` is an adjacent handoff surface for full plugin packaging and is not a gate-family member.
- `skill-creator` validation is an early correctness gate, not proof that a skill is lifecycle-ready.
- A non-trivial creator-to-builder transition must leave behind a durable `HandoffPackage`.
- `skill-builder` must compare candidate behavior against an explicit baseline in the canonical non-trivial loop.
- Timing and token evidence must be captured when the runner exposes them, and explicitly marked unavailable when it does not.
- Qualitative review and quantitative grading must both be represented in the evidence bundle for non-trivial hardening.
- Description and routing tuning must be assessed in every non-trivial round, even when no edits are ultimately required.
- No downstream install or plugin handoff may bypass `ContractValidityEvidence`.
- Repo-native helper surfaces remain preferred over imported parallel infrastructure when they can satisfy the contract.
- The workflow must remain understandable to less technical users; jargon is not allowed to become an unstated gate to participation.

## Failure Model and Recovery

### Failure classes

- `handoff_missing`
  - `skill-creator` finishes starter work but does not preserve the next-stage context in a durable form.

- `baseline_invalid`
  - `skill-builder` claims a comparison loop but uses no meaningful baseline, an inconsistent baseline, or an improvised baseline that planning never sanctioned.

- `evidence_gap`
  - outputs exist, but the round does not preserve enough quantitative or qualitative evidence to support a trustworthy decision.

- `metric_unavailability_confusion`
  - timing or token data is absent, but the workflow treats that absence as zero, pass, or unimportant instead of marking it unavailable.

- `comparison_contamination`
  - candidate and baseline are run with materially different prompts, fixtures, or context, so the result looks comparative but is not trustworthy.

- `non_discriminating_eval_set`
  - the prompt set or assertions are too weak to show whether the candidate is actually better than the baseline.

- `premature_scale_up`
  - the workflow jumps to wide eval coverage before small-sample evidence shows the direction is promising.

- `downstream_bypass`
  - install/import or plugin packaging proceeds without the comparative loop establishing contract validity.

- `ambiguous_readiness_state`
  - the workflow reports success without distinguishing "starter-valid", "comparatively improved", and "downstream-ready".

- `jargon_overload`
  - the workflow assumes users understand eval vocabulary without explanation, causing avoidable confusion about what is happening or why.

### Recovery requirements

- `handoff_missing`
  - recover by reconstructing the minimum `HandoffPackage` before continuing to lifecycle hardening
- `baseline_invalid`
  - recover by stopping the round, defining the valid baseline explicitly, and rerunning the comparison
- `evidence_gap`
  - recover by adding the missing review or grading surface before making a readiness claim
- `metric_unavailability_confusion`
  - recover by marking the metrics unavailable explicitly and keeping decisions scoped to the evidence that does exist
- `comparison_contamination`
  - recover by freezing `ComparisonInputs`, invalidating the contaminated round as a planning-grade comparison, and rerunning the round cleanly
- `non_discriminating_eval_set`
  - recover by replacing or extending the prompt set, assertions, or review criteria before claiming improvement
- `premature_scale_up`
  - recover by returning to the smallest realistic prompt set that can expose candidate-versus-baseline differences
- `downstream_bypass`
  - recover by blocking install/plugin handoff until `ContractValidityEvidence` is complete
- `ambiguous_readiness_state`
  - recover by labeling the current state explicitly as starter-valid, comparison-incomplete, blocked, or downstream-ready and refusing to collapse those states into one success label
- `jargon_overload`
  - recover by rephrasing the stage in plain language and explaining what the review bundle is intended to show

## Observability

The upgraded loop must be visible through repo artifacts rather than chat memory alone.

Required signals:

- a durable creator-to-builder handoff artifact file exists for non-trivial creator output
- iteration rounds record an explicit `IterationRoundState`
- iteration rounds record the chosen baseline type and round decision
- any `neutral_repo_baseline` records the human approval and justification that made it valid
- iteration rounds record frozen `ComparisonInputs` or an explicit reason why comparison parity could not be achieved
- candidate and baseline outputs are both represented in the evidence bundle
- timing and token metrics are preserved when available, and explicitly marked unavailable when not available
- qualitative plus quantitative review surfaces are both present for non-trivial hardening
- the route and description tuning assessment is visible in changed artifacts or round notes, even when it concludes no edits were needed
- downstream handoff readiness is distinguishable from starter validation success and from comparison-complete readiness
- blocked rounds are distinguishable from passed rounds in repo-visible artifacts

Suggested verification surfaces:

- `quick_validate.py` or equivalent creator-stage validation evidence
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode smoke`
- `python3 Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py Skills/skill-builder --eval-mode release`
- repo-visible scorecards, manifests, or summary artifacts produced by the canonical eval flow

Minimum readiness checks for planning:

- the spec identifies a smallest durable representation for `HandoffPackage`
- the spec defines canonical baseline rules for new and existing skills
- the spec defines the minimum evidence set for a non-trivial `IterationRound`
- the spec defines comparison-parity rules through `ComparisonInputs`
- the spec defines when the loop may widen and when it must stop blocked
- the spec defines how downstream install and plugin handoffs depend on `ContractValidityEvidence`

## Acceptance and Test Matrix

- SA1. The family split remains preserved: `skill-creator` owns starter authoring, `skill-builder` owns lifecycle hardening, `skill-installer` owns install/import of already-valid skills, and `plugin-creator` owns plugin scaffolding. `plugin-builder` is an adjacent handoff surface for full plugin packaging and is not a gate-family member.
- SA2. Non-trivial creator-stage work ends with a durable `HandoffPackage` rather than a purely implicit referral.
- SA2a. The phase-one `HandoffPackage` is represented as a dedicated repo-visible artifact file.
- SA3. The `HandoffPackage` includes at least: skill goal, boundary summary, trigger contexts, resource inventory, 2-3 realistic starter prompts, known risks or unknowns, validation state, and authoring state.
- SA4. The canonical non-trivial `skill-builder` loop includes prompt preparation, explicit baseline selection, same-round candidate-versus-baseline comparison, evidence capture, tuning, and a round decision.
- SA5. New skills compare against `no_skill` by default unless a human-approved planning decision explicitly defines a stronger neutral baseline; existing skills compare against a prior valid snapshot.
- SA6. Non-trivial iteration evidence includes both qualitative and quantitative review surfaces; if timing or token metrics are unavailable, the evidence bundle records them as unavailable rather than silently omitting or fabricating them.
- SA7. Description and routing assessment is part of every non-trivial round, and edits cannot be skipped when the evidence shows trigger-quality weakness, ambiguity, or misleading descriptions.
- SA8. Wider reruns happen only after smaller-sample evidence establishes directional confidence or exposes the need for stronger prompts or grading first.
- SA9. `skill-builder` may hand off to `skill-installer` only when `ContractValidityEvidence` exists and the remaining work is pure install/import/visibility execution.
- SA10. `skill-builder` may hand off to `plugin-builder` only when `ContractValidityEvidence` exists and the remaining work is pure plugin packaging.
- SA11. The upgraded loop reuses repo-native eval and reporting surfaces where practical rather than requiring a literal Anthropic-style workspace and viewer contract.
- SA12. The workflow explains evaluation and review stages clearly enough that a less technical user can understand why the candidate is being compared against a baseline and what the results mean.
- SA13. Planning can consume this spec without inventing the handoff artifact shape, baseline rules, iteration stages, evidence requirements, or downstream handoff gates.
- SA14. Each non-trivial `IterationRound` records a round state from `prepared`, `running`, `evidence_captured`, `reviewed`, `decision_recorded`, or `blocked`.
- SA15. Candidate and baseline runs in a planning-grade comparison round share the same `ComparisonInputs`; if they do not, the round is not treated as valid comparative evidence.
- SA16. Wider reruns for non-trivial skills expand beyond happy-path prompts to include representative edge or adversarial cases when the skill risk justifies them.
- SA17. Repo-visible artifacts distinguish at least these readiness states: starter-valid, comparison-incomplete or blocked, and downstream-ready.
- SA18. A creator-stage validation pass by itself is insufficient evidence for install or plugin handoff.

## Open Questions

- Which existing repo-native review artifacts are sufficient for qualitative plus quantitative comparison, and where is a minimal helper addition justified?

## Definition of Done

- The spec preserves the current family routing split without reopening consolidation.
- The creator-to-builder handoff is defined strongly enough that planning does not need to invent what context must survive beyond starter authoring.
- The `skill-builder` loop is defined strongly enough that planning does not need to invent baseline rules, evidence requirements, or round decisions.
- The spec fixes the phase-one `HandoffPackage` representation and `neutral_repo_baseline` approval rule strongly enough that planning does not have to invent them.
- The spec makes it impossible to confuse starter validation with contract-valid lifecycle readiness.
- The spec defines when downstream installation or plugin packaging may proceed and when they must remain blocked behind lifecycle evidence.
- The spec is verified for required sections, frontmatter, and stable `SA` IDs.
