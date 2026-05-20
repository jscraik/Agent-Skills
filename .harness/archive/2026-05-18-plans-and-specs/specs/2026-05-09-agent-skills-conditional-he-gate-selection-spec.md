---
schema_version: 1
artifact_id: agent-skills-conditional-he-gate-selection-spec
artifact_type: he-spec
canonical_slug: agent-skills-conditional-he-gate-selection
title: Conditional HE Gate Selection Spec
harness_stage: he-spec
status: draft
date: 2026-05-09
traceability_required: false
origin: chat
linear_issue: not_tracked
linear_milestone: not_tracked
---

# Conditional HE Gate Selection Spec

## Mode Decision

This is an untracked Harness Engineering plugin-hardening spec produced from the
`he-brainstorm` survivor selection and deepened by `he-spec`.

The selected execution slice is:

`Conditional HE Gate Selection and Negative Evals`

No Linear destination has been provided. Traceability is intentionally marked
`false` for this draft, and tracked closure must not be claimed until a Linear
project, milestone, or parent issue is assigned.

Implementation authority is also not assumed. This spec is ready for planning
and implementation only after the user confirms either:

- keep this as an untracked plugin-hardening slice; or
- attach it to a Linear project, milestone, or parent issue.

## Problem

Recent Harness Engineering hardening added useful contracts from Pragmatic
Programmer, XP, Philosophy of Software Design, and Domain-Driven Design lenses.
Those contracts strengthen production readiness, but they also create an
over-application risk: agents may invoke domain, strategy, refactor, Linear, or
eval gates for low-risk work where those gates add ceremony instead of proof.

Harness Engineering needs a small gate-selection layer that decides which
contracts apply for the current slice, what minimum proof is required, and which
heavy gates are explicitly skipped.

## Goals

- Preserve rigorous proof for risky Harness Engineering work.
- Keep trivial and low-risk work lightweight.
- Make `minimum_proof_required` explicit before handoff or closure.
- Prevent DDD/domain gates from becoming always-on.
- Prevent strategy, refactor, Linear, and eval-report gates from creating
  unnecessary artifacts.
- Add negative evals proving HE does not over-route simple work.
- Keep the first implementation slice bounded to high-traffic lifecycle stages.

## Non-Goals

- Do not rewrite the full Harness Engineering router.
- Do not add a new visible skill.
- Do not add a broad philosophy document.
- Do not fix the lifecycle eval timeout problem in this slice.
- Do not create Linear issues, milestones, labels, or tracker updates.
- Do not make every HE contract mandatory.
- Do not treat production-grade output as maximum governance.

## Boundary

### In Scope

- Add a compact gate-selection contract.
- Wire gate selection into `he-router`, `he-spec`, `he-code-review`, and
  `he-eval-report`.
- Add negative evals for over-routing prevention.
- Add a small wiring validator if needed.
- Update deferred context routing so the new contract is discoverable.

### Out of Scope

- Runtime projection sync under `.agents/**`.
- Plugin marketplace metadata.
- Full lifecycle eval timeout repair.
- Whole-plugin token budget reduction.
- Linear object creation.
- Broad rollout to every lifecycle skill in the first patch.

## Domain Model

```yaml
domain_model:
  status: applicable
  bounded_context: Harness Engineering lifecycle routing and artifact production
  core_domain_relevance: core
  entities:
    - name: HE stage
      identity_rule: stage handle and lifecycle role
      lifecycle_states: routed, active, blocked, complete
  value_objects:
    - name: gate profile
      equality_rule: risk class plus required and skipped contracts
      immutability_expectation: generated per selected slice
    - name: minimum proof
      equality_rule: proof required for continue, close, or block decision
      immutability_expectation: stable within one stage handoff
  aggregates:
    - name: selected execution slice
      root: selected_slice
      invariants:
        - exactly one active slice drives spec, plan, or work
        - secondary artifacts may inform but must not expand scope
        - skipped gates must carry reasons
  domain_services:
    - name: gate selector
      reason: selects applicable contracts from slice risk and evidence, not keyword matching alone
  integration_contexts:
    - context: skill evals
      translation_rule: gate-selection behavior must be represented by positive and negative eval fixtures
    - context: Linear
      translation_rule: tracked closure gates apply only when Linear destination is resolved or explicitly blocked
  unresolved_model_questions:
    - whether gate selection should stay standalone or fold into lifecycle-exit-contract after validation
  closure_impact: blocks_plan
```

## Proposed Contract Shape

Create:

`Plugins/harness-engineering/references/gate-selection-contract.md`

The contract should define:

```yaml
gate_profile:
  risk_class: trivial|standard|domain_sensitive|architecture_sensitive|closure_sensitive|security_sensitive|mixed
  required_contracts: []
  skipped_contracts:
    - contract: ""
      reason: ""
  minimum_proof_required:
    continue_to_next_stage: ""
    safe_to_close: ""
    block_next_stage: ""
  evidence_basis: direct|repo|linear|harness|external|reasoned
  downstream_route: he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-eval-report|blocked
```

## Risk Classes

### Trivial

Use for typo, copy edit, local formatting, or metadata-only cleanup with no
behavioral, routing, Linear, validation, or artifact-chain impact.

Required behavior:

- skip domain model;
- skip strategy;
- skip refactor program;
- skip Linear planning unless already tracked;
- require only local evidence and diff or identity sanity.

### Standard

Use for ordinary bounded skill, reference, or documentation changes with no
major architecture or domain impact.

Required behavior:

- load only the active stage contract and directly relevant shared contract;
- require focused validation;
- record skipped heavy gates with reasons.

### Domain Sensitive

Use when behavior depends on product semantics, workflow state, permissions,
account or billing behavior, persisted lifecycle state, or cross-system
translation.

Required behavior:

- load `domain-model-production-contract.md`;
- require bounded context, invariant, identity/equality, lifecycle, or
  translation evidence;
- block closure if model, code, and test language diverge.

### Architecture Sensitive

Use for routing, orchestration, context loading, plugin boundary, lifecycle
stage, abstraction, or eval-lane changes.

Required behavior:

- require drift and rollback evidence;
- require local reasoning impact;
- prevent speculative broad refactors.

### Closure Sensitive

Use for Linear closure, milestone completion, eval report completion, or safe to
mark done recommendations.

Required behavior:

- require proof artifacts;
- require eval or drift validation where relevant;
- recommend `Blocked`, `Needs rework`, or `Unsafe to close` when proof is
  missing.

### Security Sensitive

Use for secrets, auth, permission checks, destructive operations, external
writes, privacy, or exposure risk.

Required behavior:

- route security specialist only when justified;
- require explicit security proof or blocker;
- do not bury security as a generic validation note.

### Mixed

Use only when multiple risk types are materially proven.

Required behavior:

- list each proven risk;
- choose the smallest sufficient contract set;
- reject keyword-only expansion.
- state why each included contract is necessary;
- state why each adjacent but skipped contract is unnecessary.

## Acceptance Matrix

| ID | Acceptance Criterion | Validation |
| --- | --- | --- |
| SA-001 | Gate selector contract exists and defines `gate_profile`. | Contract wiring check passes. |
| SA-002 | Trivial work skips domain, strategy, refactor, Linear, and eval-report gates. | Negative eval expects skipped gates with reasons. |
| SA-003 | Standard work requires focused proof without heavy gate expansion. | Negative eval for bounded skill wording change. |
| SA-004 | Domain-sensitive work loads the domain model production contract. | Positive eval for persisted workflow or permission semantics. |
| SA-005 | Architecture-sensitive work requires drift and rollback evidence. | Positive eval for routing or context-loading change. |
| SA-006 | Closure-sensitive work cannot close from implementation status alone. | Eval-report fixture expects blocked closure when proof is missing. |
| SA-007 | Security-sensitive work routes to security proof or blocker. | Fixture verifies security is not treated as generic validation. |
| SA-008 | Mixed work lists proven risks and smallest sufficient contract set. | Fixture rejects load-everything behavior. |
| SA-009 | `minimum_proof_required` is present for non-trivial risk classes. | Wiring check fails when omitted. |
| SA-010 | Specialist skills remain conditional and evidence-backed. | Negative eval rejects keyword-only specialist selection. |
| SA-011 | Gate selection cannot claim release confidence while lifecycle evals timeout. | Eval timeout is recorded as blocked evidence or routed to a separate refactor. |
| SA-012 | Security-sensitive gate selection records specialist proof, blocker, or explicit non-applicability. | Fixture verifies security-sensitive work cannot pass as generic validation only. |

## Expected File Changes

- `Plugins/harness-engineering/references/gate-selection-contract.md`
- `Plugins/harness-engineering/references/deferred-context-index.md`
- `Plugins/harness-engineering/references/lifecycle-exit-contract.md`
- `Plugins/harness-engineering/skills/he-router/SKILL.md`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`
- `Plugins/harness-engineering/skills/he-router/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-spec/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`
- optional `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py`

## Validation Plan

Required:

```text
python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py --json
python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py --json
python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json
./bin/ask skills audit Plugins/harness-engineering/skills/he-router --level strict --json
./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json
./bin/ask skills audit Plugins/harness-engineering/skills/he-code-review --level strict --json
./bin/ask skills audit Plugins/harness-engineering/skills/he-eval-report --level strict --json
git diff --check -- Plugins/harness-engineering
```

After `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py` is
created, it becomes required:

```text
python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json
```

Optional:

```text
python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --skill he-spec --skill he-code-review --skill he-eval-report --json
```

If lifecycle evals still timeout, record the result as blocked validation
evidence, not as passing behavior proof.

Do not claim full Harness Engineering release confidence from this slice while
the lifecycle eval lane is timing out. The acceptable confidence claim is
limited to static contract wiring, skill audit, and fixture coverage for the
touched surfaces.

## Failure and Recovery

- If the gate selector becomes verbose, fold examples into references and keep
  lifecycle skill entrypoints small.
- If `mixed` loads too many contracts, require proof per included risk class and
  reject keyword-only matches.
- If negative evals are brittle, simplify them to check selected/skipped gate
  fields rather than exact prose.
- If runtime evals timeout, keep timeout recovery as a separate refactor slice.

## Handoff

Recommended next stage: `he-plan`.

The plan should implement the first slice only: gate contract, high-traffic
lifecycle wiring, negative evals, and a wiring validator. Broader lifecycle
rollout and eval-timeout recovery should remain separate slices.
