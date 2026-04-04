---
title: Skill Authoring Family Contract Requirements
date: 2026-04-03
status: draft
spec_required: lite
risk_level: medium
complexity: medium
---

# Skill Authoring Family Contract Requirements

## Problem Frame

The repo now has a capable but increasingly ambiguous skill-authoring family:
- `skill-creator` still reads as the starter path for first-draft skill creation.
- `skill-builder` has evolved into a broad lifecycle maintainer covering creation, improvement, audit, packaging, and install-distribute work.
- `skill-installer` still owns focused installation and curated import flows.
- `codex-plugin-builder` remains the correct path when the deliverable should ship as a plugin instead of a bare skill.

This is useful for power users, but it is no longer self-explanatory. Current repo evidence shows:
- the broadest surface, `skill-builder`, still presents itself like a narrow creator in UI metadata
- the repo still has stale frontmatter assumptions around `compatibility`
- there is no explicit family-level routing contract that says which surface should win for ambiguous prompts

The result is a gap between capability and usability: the repo has strong skill-building machinery, but weaker routing clarity than current April 2026 best practice recommends.

## Approaches

| Approach | Description | Pros | Cons |
|---|---|---|---|
| A. Documentation-first posture correction | Update descriptions, See Also guidance, and repo docs so each skill is easier to choose, but stop short of adding system-level eval enforcement. | Fastest path, lowest coordination cost, improves readability quickly. | Too easy to drift, weak protection against future overlap regressions. |
| B. Family contract plus routing evals | Define one explicit contract across `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder`, then protect it with routing regression evals. | Best match for April 2026 best practice, durable, measurable, preserves specialization without forced consolidation. | More work than a narrow copy fix, requires coordinated updates across multiple surfaces. |
| C. Consolidation-first merge or rename | Collapse or rename surfaces to reduce overlap structurally before tightening routing. | Simpler surface area in theory, could reduce long-term confusion if done well. | High churn, premature, risks destroying useful specialization before the contract is proven. |

## Recommendation

Choose **Approach B: family contract plus routing evals**.

This is the smallest durable move that makes the repo feel industry-standard rather than just internally powerful. It matches current OpenAI guidance to keep each skill focused on one job while still respecting the fact that `skill-builder` has already grown into an expert maintainer surface.

Important companion decision:
- apply the narrow standards fix from the earlier review as a prerequisite or phase-zero patch
- specifically, update stale `compatibility` assumptions before presenting the new family contract as complete

## Requirements

**Family routing contract**
- R1. Define one canonical routing contract for `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder`.
- R2. The contract must state each skill's primary job, strongest trigger phrases, and explicit non-triggers.
- R3. The contract must establish a two-tier authoring model:
  - starter authoring via `skill-creator`
  - expert lifecycle improvement via `skill-builder`
- R4. The contract must preserve `skill-installer` as the focused execution path for installation and curated import work.
- R5. The contract must preserve `codex-plugin-builder` as the packaging path when the deliverable is a plugin rather than a standalone skill.

**Discoverability and copy**
- R6. Each skill in the family must expose routing copy that matches its real scope in both frontmatter and any `agents/openai.yaml` metadata.
- R7. `skill-builder` must be described as an expert lifecycle maintainer surface rather than a default create-or-update entrypoint.
- R8. Each family member must include explicit handoff guidance to the adjacent skills when a request crosses boundaries.

**Validation and enforcement**
- R9. Add routing regression evals that pressure-test ambiguous prompts across the family, including create-only, improve-only, install-only, and mixed lifecycle requests.
- R10. The family contract must live in one repo-visible durable place so future edits have a canonical reference point.
- R11. The repo's frontmatter-validation guidance must be brought back into sync with the current official skill spec, including support for `compatibility`, before the contract rollout is considered complete.

**Adoption posture**
- R12. Preserve current skill names for this phase unless contract/eval work proves that naming alone is blocking correct routing.
- R13. Favor explicit routing clarity and evaluation evidence over structural consolidation in phase one.

## Success Criteria

- A maintainer can tell which authoring-family skill should be used for a given request without reading all four skills end to end.
- `skill-builder` no longer appears to be a narrow starter skill in metadata while behaving like an expert lifecycle tool in practice.
- The repo no longer contains stale frontmatter guidance that rejects spec-valid `compatibility` usage.
- Ambiguous prompts such as "make me a skill", "improve and install this skill", and "package this for reuse" have defined expected routing outcomes and regression coverage.
- The family contract is clear enough that a later `ce-spec` or `ce-plan` stage does not need to invent ownership boundaries from scratch.

## Scope Boundaries

- Do not merge or rename the family in this phase unless the contract work clearly fails.
- Do not turn this phase into a plugin packaging initiative.
- Do not refactor unrelated skills across the wider repo.
- Do not overfit the family contract around one temporary validator quirk; the contract should describe roles, not implementation accidents.
- Do not treat installer delegation mechanics as the first-order problem unless routing clarity work leaves a real residual gap.

## Key Decisions

- Decision: Treat this as a family-level product-shape problem, not as a single-skill wording fix.
  Rationale: The main weakness is overlap ambiguity across multiple surfaces, not poor quality inside `skill-builder` alone.

- Decision: Keep the current family members and clarify their jobs before considering structural consolidation.
  Rationale: Current specialization is still useful; the repo lacks a contract more than it lacks surfaces.

- Decision: Use a two-tier authoring model.
  Rationale: This aligns with current best practice while preserving the user's deliberate expert expansion of `skill-builder`.

- Decision: Treat the `compatibility` support fix as a prerequisite patch, not as the entirety of the effort.
  Rationale: It is necessary for correctness, but insufficient for long-term routing quality.

- Decision: Protect the family contract with evals, not documentation alone.
  Rationale: Routing drift is predictable when multiple skills overlap; measured regression coverage is the durable control.

## Dependencies / Assumptions

- Official April 2026 OpenAI/Codex guidance remains the routing baseline: one-job skills, clear trigger descriptions, and explicit use boundaries.
- The current repo continues to keep `skill-creator`, `skill-builder`, `skill-installer`, and `codex-plugin-builder` as separate discoverable surfaces during this phase.
- Repo validators and examples can be updated incrementally without requiring a large migration event.

## Outstanding Questions

### Resolve Before Planning

- None. The direction is clear enough to proceed to spec.

### Deferred to Planning

- [Affects R9][Technical] Which eval harness and fixture shape should own cross-skill routing regression cases?
- [Affects R10][Information architecture] Should the canonical family contract live in a dedicated reference doc, shared README, or one anchor skill reference with mirrored summaries elsewhere?
- [Affects R8][Technical] Should `skill-builder` become explicit-only immediately, or should invocation policy change wait until routing evals establish a baseline?

## Next Steps

-> `/ce:spec` for a lite spec that defines:
- the canonical routing matrix
- required description and metadata updates by skill
- the regression-eval contract
- the phase-zero `compatibility` sync patch
