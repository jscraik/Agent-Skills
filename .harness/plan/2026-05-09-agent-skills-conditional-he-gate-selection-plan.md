---
schema_version: 1
artifact_id: agent-skills-conditional-he-gate-selection-plan
artifact_type: he-plan
canonical_slug: agent-skills-conditional-he-gate-selection
title: Conditional HE Gate Selection Plan
harness_stage: he-plan
status: draft
date: 2026-05-09
traceability_required: false
origin: .harness/specs/2026-05-09-agent-skills-conditional-he-gate-selection-spec.md
linear_issue: not_tracked
linear_milestone: not_tracked
---

# Conditional HE Gate Selection Plan

## Mode Decision

This plan implements the first bounded slice from
`.harness/specs/2026-05-09-agent-skills-conditional-he-gate-selection-spec.md`.

No Linear destination has been provided. Treat this as an untracked
plugin-hardening draft until a Linear project, milestone, or parent issue is
assigned.

Implementation is blocked until the user confirms either:

- proceed as an untracked plugin-hardening slice; or
- attach the slice to a Linear project, milestone, or parent issue.

## Execution Boundary

Implement only the smallest useful slice:

1. Add the shared gate-selection contract.
2. Make it discoverable through deferred context.
3. Wire high-traffic lifecycle skills only.
4. Add positive and negative eval cases.
5. Add a focused wiring validator.
6. Validate with existing HE checks and strict skill audits.

Do not repair lifecycle eval timeouts, reduce whole-plugin token budget, sync
runtime projections, or mutate Linear in this plan.

## Implementation Units

### P1 - Add Gate Selection Contract

Files:

- `Plugins/harness-engineering/references/gate-selection-contract.md`

Work:

- Define `gate_profile`.
- Define risk classes.
- Define `minimum_proof_required`.
- Define skipped-gate recording.
- Include production-grade versus enterprise-grade guidance.
- Include examples for trivial, standard, domain-sensitive,
  architecture-sensitive, closure-sensitive, security-sensitive, and mixed work.

Acceptance:

- Satisfies `SA-001`, `SA-007`, `SA-009`.

Validation:

Validation:

- P1 acceptance: manual inspection of contract file structure and content
- P5 retroactive proof: `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json`

Rollback:

- Remove the new contract and references if it causes over-routing or audit
  failure.

### P2 - Add Deferred Context Routing

Files:

- `Plugins/harness-engineering/references/deferred-context-index.md`
- `Plugins/harness-engineering/references/lifecycle-exit-contract.md`

Work:

- Add the gate-selection contract to deferred context.
- Add a lifecycle exit field for `gate_profile` or equivalent structured
  output.
- Require non-trivial work to state minimum proof before downstream handoff.
- Require lifecycle confidence claims to distinguish static wiring confidence
  from release confidence when lifecycle evals timeout.

Acceptance:

- Satisfies `SA-001`, `SA-009`.

Validation:

- `python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py --json`
- `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json`

Rollback:

- Revert lifecycle-exit additions while keeping the standalone contract if it is
  still useful.

### P3 - Wire High-Traffic Lifecycle Skills

Files:

- `Plugins/harness-engineering/skills/he-router/SKILL.md`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/skills/he-code-review/SKILL.md`
- `Plugins/harness-engineering/skills/he-eval-report/SKILL.md`

Work:

- `he-router`: classify the request risk before selecting heavy downstream
  gates.
- `he-spec`: make selected risk class part of acceptance criteria.
- `he-code-review`: treat wrong or missing gate profile as a readiness finding.
- `he-eval-report`: block closure when closure-sensitive proof is missing.

Acceptance:

- Satisfies `SA-002` through `SA-010`.

Validation:

- `./bin/ask skills audit Plugins/harness-engineering/skills/he-router --level strict --json`
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json`
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-code-review --level strict --json`
- `./bin/ask skills audit Plugins/harness-engineering/skills/he-eval-report --level strict --json`

Rollback:

- Revert skill entrypoint changes if audits fail or line budgets regress.

### P4 - Add Positive and Negative Evals

Files:

- `Plugins/harness-engineering/skills/he-router/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-spec/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`
- `Plugins/harness-engineering/skills/he-eval-report/references/evals.yaml`

Work:

- Add positive evals proving domain, architecture, closure, and security risks
  select the right gates.
- Add negative evals proving trivial and standard work avoid heavy gates.
- Add specialist-selection negative eval for keyword-only matches.
- Add a mixed-risk negative eval proving the selector does not load every
  adjacent contract.
- Add an eval-timeout confidence case proving release confidence is blocked or
  scoped down when lifecycle evals do not complete.

Acceptance:

- Satisfies `SA-002` through `SA-010`.

Validation:

- YAML parse for edited eval files.
- Strict skill audits.
- Optional lifecycle smoke evals, recorded as blocked if timeout persists.
- Static fixture assertions in `check_gate_selection_wiring.py` after P5 exists.

Rollback:

- Remove brittle eval cases and replace with simpler selected/skipped gate
  assertions.

### P5 - Add Wiring Validator

Files:

- `Plugins/harness-engineering/scripts/check_gate_selection_wiring.py`

Work:

- Assert the contract exists.
- Assert deferred context references it.
- Assert lifecycle exit output can carry gate profile data.
- Assert high-traffic lifecycle skills reference the contract.
- Assert required positive and negative eval case names exist.
- Assert the plan includes the known lifecycle-eval timeout confidence boundary.

Acceptance:

- Satisfies `SA-001`, `SA-002`, `SA-009`, `SA-010`.

Validation:

- `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json`
- py-compile with `PYTHONPYCACHEPREFIX=/tmp/he-gate-selection-pycache`

Rollback:

- Remove validator if it duplicates existing checks without adding coverage.

## Dependency Order

1. P1 must land before P2-P4.
2. P2 must land before validator finalization.
3. P3 and P4 can proceed after P1.
4. P5 finalizes after all references and evals are in place.

## Validation Gate Matrix

| Gate | Command | Blocks Closure |
| --- | --- | --- |
| Contract wiring | `python3 Plugins/harness-engineering/scripts/check_gate_selection_wiring.py --json` after P5 creates it | yes |
| Deferred context | `python3 Plugins/harness-engineering/scripts/check_deferred_context_index.py --json` | yes |
| Domain wiring regression | `python3 Plugins/harness-engineering/scripts/check_domain_contract_wiring.py --json` | yes |
| Packaging hygiene | `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json` | yes |
| Router audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-router --level strict --json` | yes |
| Spec audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json` | yes |
| Code review audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-code-review --level strict --json` | yes |
| Eval report audit | `./bin/ask skills audit Plugins/harness-engineering/skills/he-eval-report --level strict --json` | yes |
| Diff hygiene | `git diff --check -- Plugins/harness-engineering .harness/specs .harness/plan` | yes |
| Lifecycle smoke | `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode smoke --skill he-router --skill he-spec --skill he-code-review --skill he-eval-report --json` | yes for release-confidence claims; no for static wiring confidence if timeout is recorded as blocked evidence |

## Risks

- The contract could become another always-on gate.
- Negative evals could become brittle if they assert prose instead of behavior.
- `mixed` risk class could become a load-everything loophole.
- The lifecycle eval timeout could be mistaken for this slice failing.
- Expanding beyond four lifecycle skills could increase plugin budget pressure.
- The plan could incorrectly run `check_gate_selection_wiring.py` before P5
  creates it.
- Security-sensitive gate selection could pass with generic validation instead
  of specialist proof or an explicit blocker.

## Rollback Conditions

Rollback or stop if:

- strict skill audits fail after compression;
- gate selector increases default prompt/context load without benefit;
- trivial-work eval starts selecting heavy gates;
- validator duplicates existing checks without new protection;
- implementation attempts to fix eval timeouts inside this slice.
- release confidence is claimed while lifecycle evals still timeout.
- `mixed` risk handling loads all adjacent contracts instead of the smallest
  sufficient set.

## Post-Plan Handoff

Recommended next stage: blocked until authority is confirmed, then `he-work`.

Before implementation, confirm whether this remains an untracked
plugin-hardening slice or should be linked to a Linear project, milestone, or
parent issue.
