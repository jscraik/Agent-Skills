---
schema_version: 1
artifact_id: agent-skills-first-principles-contract-plan-technical-review
artifact_type: he-code-review
canonical_slug: agent-skills-first-principles-contract
title: First-Principles Contract Plan Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-09
traceability_required: false
origin: .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md
linear_issue: not_created
linear_milestone: HE First-Principles Gate (proposed)
risk: architecture_sensitive
depth: standard
ui: false
---

# First-Principles Contract Plan Technical Review

## Findings

No blocking or non-blocking findings remain after the deepen-plan pass.

## Review Verdict

Approved for implementation.

The deepened plan is specific enough for another agent to implement without inventing the lifecycle shape. It names the canonical source files, preserves the no-standalone-skill constraint, resolves eval ownership, requires negative behavioral evals, and includes validation gates that can prove source, routing, projection, and closure behavior.

Do not treat this as implementation approval for Linear completion. It approves moving into source edits only. Linear closure remains blocked until the future eval report exists and validates the implemented change.

## Evidence Reviewed

| Evidence | Review Result |
|---|---|
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:21` | The summary preserves the core goal: add a first-principles gate without creating `he-first-principles`. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:46` | The synthesis checkpoint separates stated facts, implementation inferences, and out-of-scope work. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:84` | Eval routing is resolved by stage ownership, with cross-stage behavior isolated to lifecycle tracer evals. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:102` | The plan now preserves existing eval schemas instead of introducing a second eval format. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:142` | File ownership and editing order correctly keep canonical source edits ahead of generated projections. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:250` | Lifecycle skill wiring is explicit and bounded to seven approved HE skills. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:307` | Negative eval coverage is mapped to specific files and required behavior. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:369` | Static validator requirements are concrete enough to implement deterministically. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:528` | Validation gates cover artifact lints, validator syntax, wiring, sync, handles, projection integrity, audits, diff hygiene, and future eval proof. |
| `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:618` | Remaining unknowns are explicit and include repair paths. |

## Corrected During Review

| Issue | Fix Applied | Evidence |
|---|---|---|
| Validation fallback wording was inconsistent: the validation gates listed `skills explain`, while the unknowns table referenced `skills prove` or parser validation. | Updated the unknowns table to use `./bin/ask skills explain <handle> --json --robot` as the fallback. | `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:623` |
| Validator syntax was specified inside `PU-005` but was not listed as a top-level validation gate. | Added `python3 -m py_compile Plugins/harness-engineering/scripts/check_first_principles_contract_wiring.py` to the gate matrix. | `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md:536` |
| Deferred index wiring could have been half-complete because the live index has both a Runtime Reference Map and a Conditional Loading Map. | Required `first-principles-contract.md` in both maps and required the new validator to check both contexts. | `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` |
| Skill-facing implementation could skip the repo vocabulary front door. | Added a pre-implementation gate to read `UBIQUITOUS_LANGUAGE.md` before changing skills, sync policy, runtime projections, or agent-facing docs. | `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` |
| New lifecycle wiring could accidentally regress domain, XP, or gate-selection contracts. | Added existing `check_domain_contract_wiring.py` and `check_xp_contract_wiring.py` beside the gate-selection wiring validator. | `.harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md` |

## Risk Review

| Risk Area | Status | Evidence | Operational Impact |
|---|---|---|---|
| Scope creep | controlled | The plan forbids a standalone skill and broad lifecycle rewrites. | Implementation can stay focused on contract, wiring, evals, validator, and sync. |
| Hot-path context growth | controlled | The plan requires thin hooks and deferred reference loading. | Changed `SKILL.md` files should not become bloated prompt copies. |
| Eval theater | controlled | Eval cases must assert behavior, not keyword presence. | Reduces risk that evals pass while the skill only mentions first principles. |
| Projection drift | controlled | The plan requires canonical edits before sync and forbids hand-editing `.skillsets/**`. | Runtime projections can be tied back to source changes. |
| Closure overclaiming | controlled | Future eval report is required before Linear closure. | Implementation cannot be marked complete from file changes alone. |
| Linear ambiguity | accepted | No Linear issue exists; proposed mapping remains non-mutating. | Work can proceed locally, but Linear state should not be updated without explicit instruction. |

## Validation Evidence

Commands run against the deepened plan:

```text
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md -> pass
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md -> pass
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md -> pass
git diff --check -- .harness/plan/2026-05-09-agent-skills-first-principles-contract-plan.md -> pass
```

Review artifact lints still need to be run after this review file is saved.

## Implementation Handoff

Recommended next stage: `he-phase-heartbeat` or the normal implementation workflow.

Implementation should execute the plan units in order:

1. `PU-001`: add `first-principles-contract.md`
2. `PU-002`: add deferred-context routing
3. `PU-003`: wire the seven lifecycle skill hooks
4. `PU-004`: add negative eval cases
5. `PU-005`: add the static wiring validator
6. `PU-006`: sync projections and validate
7. `PU-007`: produce the eval report before any Linear closure recommendation

## Completion Boundary

This review approves the plan for implementation. It does not approve:

- creating Linear objects
- closing Linear work
- skipping the future eval report
- creating a standalone first-principles skill
- broad HE lifecycle refactors outside the approved slice
