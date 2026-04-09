---
title: Skill Authoring Family Contract and Iteration Requirements
date: 2026-04-04
status: draft
spec_required: full
risk_level: medium
complexity: medium
---

# Skill Authoring Family Contract and Iteration Requirements

## Table of Contents
- [Problem Frame](#problem-frame)
- [Approaches](#approaches)
- [Recommendation](#recommendation)
- [Requirements](#requirements)
- [Success Criteria](#success-criteria)
- [Scope Boundaries](#scope-boundaries)
- [Key Decisions](#key-decisions)
- [Dependencies / Assumptions](#dependencies--assumptions)
- [Outstanding Questions](#outstanding-questions)
- [Next Steps](#next-steps)

## Problem Frame

The repo has already improved the skill-authoring family by clarifying the lifecycle split:
- `skill-creator` owns first-draft scaffolding and starter authoring.
- `skill-builder` owns lifecycle hardening, routing, evals, and standalone packaging.
- `skill-installer` owns import, install, and runtime visibility for already-valid skills.
- `plugin-builder` owns plugin packaging once the standalone-skill boundary is settled.

That family split is now in a good place. The remaining gap is the quality of the authoring loop itself.

Current repo evidence shows:
- `skill-creator` still ends largely at `quick_validate.py` plus generic forward-testing guidance.
- `skill-builder` already owns validators, smoke/release evals, and description optimization, but it does not yet present a single explicit iterative loop that compares baseline vs improved skill behavior, captures runtime evidence, and reruns at wider scale.
- the seam between first-draft creation and lifecycle hardening is clear in principle, but not yet strong enough in artifacts and operator flow to feel best-in-class.

The result is a new kind of gap: not role ambiguity, but loop maturity. The family is easier to route than before, yet it still trails the strongest known authoring workflows in how it turns a draft skill into an evidence-backed, benchmarked, trigger-optimized skill.

## Approaches

| Approach | Description | Pros | Cons |
|---|---|---|---|
| A. Handoff-only patch | Add an explicit creator-to-builder handoff checklist, but leave `skill-builder`'s eval and iteration flow largely as-is. | Smallest change, reinforces the current family split, low churn. | Improves the seam but not the maturity of the loop; still lacks clear paired benchmarking and review rhythm. |
| B. Selective Anthropic-inspired loop import | Keep the current family split, add an explicit handoff package to `skill-creator`, and teach `skill-builder` a first-class iterative loop: realistic prompts, with-skill vs baseline runs, timing/token capture, qualitative plus quantitative review, routing optimization, and wider reruns. | Best balance of clarity and leverage, imports the strongest upstream ideas without collapsing local specialization, fits current repo architecture. | Requires coordinated updates across docs, eval contracts, and possibly helper scripts or artifact schemas. |
| C. Full role convergence | Expand `skill-creator` into the primary end-to-end create/improve/benchmark surface, closer to Anthropic's single-skill model. | Maximum parity with the reference workflow, potentially fewer handoffs. | Reopens family-boundary ambiguity, weakens the lifecycle split the repo just finished clarifying, and risks making `skill-installer`/`skill-builder` feel second-class again. |

## Recommendation

Choose **Approach B: selective Anthropic-inspired loop import**.

This preserves the local architecture that now makes sense while importing the highest-value upstream improvements:
- explicit capture of intent from real conversation context before drafting;
- a visible creator-to-builder handoff package rather than an implied escalation;
- paired evaluation against a baseline rather than single-lane validation;
- runtime evidence such as timing and token cost, not just pass/fail assertions;
- qualitative review alongside quantitative grading;
- description and routing optimization as a named phase, not an optional afterthought;
- wider-scale reruns only after a smaller loop shows the direction is working.

This is the smallest durable move that makes the family feel modern and evidence-backed without undoing the lifecycle clarity already achieved.

## Requirements

**Family posture**
- R1. Preserve the current lifecycle split:
  - `skill-creator` for starter authoring and scaffold-bound edits;
  - `skill-builder` for lifecycle hardening, evals, and standalone packaging;
  - `skill-installer` for already-valid install/import/visibility work;
  - `plugin-builder` for plugin packaging.
- R2. Do not merge or rename these family members in this phase unless the upgraded loop proves the split is materially harmful.

**Creator-to-builder handoff**
- R3. `skill-creator` must end with an explicit handoff package whenever the work moves beyond first-draft creation.
- R4. The handoff package must capture the minimum context `skill-builder` needs without rediscovery, including:
  - skill goal and boundary;
  - intended trigger phrases or user contexts;
  - a draft resource inventory;
  - 2-3 realistic starter prompts or prompt candidates;
  - known weak spots, open questions, or likely routing risks;
  - current validation state, including `quick_validate.py` outcome.
- R5. The handoff must be framed as the normal next lifecycle step for non-trivial skills, not as an exception only when something is wrong.

**Builder iterative eval loop**
- R6. `skill-builder` must present one explicit iterative improvement loop for non-trivial skill hardening.
- R7. That loop must include:
  - drafting or refining realistic user prompts;
  - running the candidate skill against an appropriate baseline in the same evaluation round;
  - capturing quantitative evidence beyond assertion outcomes when available, including timing and token usage;
  - presenting both qualitative and quantitative review surfaces;
  - tuning routing and description quality as part of the loop;
  - rerunning at wider scale after promising small-sample results.
- R8. The baseline rule must be explicit:
  - for new skills, compare against no-skill behavior or the best available neutral baseline;
  - for existing skills, compare against the prior version or prior contract-valid snapshot.
- R9. The loop must reuse repo-native validation and reporting surfaces where practical instead of cloning an upstream directory layout or viewer contract wholesale.

**Adoption and evidence**
- R10. The upgraded loop must strengthen evidence quality without forcing heavier process on trivial skills.
- R11. The workflow must stay legible to less technical users by explaining evaluation terminology when needed and avoiding jargon-heavy handoffs by default.
- R12. The durable repo-visible contract must explain the relationship between creator output, builder iteration, and installer/plugin handoff so later stages do not need to rediscover lifecycle boundaries.

## Success Criteria

- A new skill can move from first draft to lifecycle hardening without rediscovering intent, trigger shape, or starter eval prompts.
- `skill-builder` makes it obvious how to judge whether a revision is actually better than the baseline, not just syntactically valid.
- The family preserves clear routing boundaries while still feeling like one coherent authoring system.
- Maintainers can see qualitative output quality, quantitative grading, and cost/performance signals in one loop before deciding a skill is ready.
- The requirements are concrete enough that the next spec can define the contract without inventing the lifecycle stages from scratch.

## Scope Boundaries

- Do not collapse `skill-creator` and `skill-builder` back into one surface in this phase.
- Do not turn this into a generic skill-evals platform redesign for the whole repo.
- Do not make `skill-installer` responsible for lifecycle hardening or benchmark interpretation.
- Do not require a brand-new custom viewer if existing report surfaces can satisfy the first version of qualitative plus quantitative review.
- Do not copy Anthropic's file layout or script names literally when the local repo already has stronger or more canonical equivalents.

## Key Decisions

- Decision: Keep the current family split.
  Rationale: The recent lifecycle clarification is a strength and should not be undone just to mimic an upstream workflow shape.

- Decision: Treat `skill-creator`'s quick validation as an early gate, not the end of the quality story.
  Rationale: First-draft correctness is useful, but it does not prove trigger quality, comparative value, or operational efficiency.

- Decision: Make the creator-to-builder handoff an explicit artifact, not tribal knowledge.
  Rationale: The handoff is now part of the product shape of the family and should be teachable, inspectable, and reusable.

- Decision: Import the strongest parts of Anthropic's loop into `skill-builder`, not `skill-creator`.
  Rationale: The upstream ideas are high-value, but their single-surface model would blur local lifecycle ownership.

- Decision: Prefer paired baseline comparisons, qualitative review, and timing/token evidence over pass/fail-only validation.
  Rationale: The goal is to know whether the skill improved, not merely whether it passes a minimum gate.

## Dependencies / Assumptions

- The current family contract rollout remains the baseline and should be extended rather than reopened.
- Anthropic's `skill-creator` is a useful reference for loop quality, not a canonical source for local file layout, naming, or ownership boundaries.
- The repo can extend existing `skill-builder` eval/reporting surfaces without needing to adopt a brand-new external harness architecture in phase one.
- Upstream-inspired improvements should map into repo-native docs, eval manifests, and validation flows so the family stays locally coherent.

## Outstanding Questions

### Resolve Before Planning

- None. The direction is clear enough to proceed to spec.

### Deferred to Planning

- [Affects R4][Technical] What is the smallest durable schema for the creator-to-builder handoff package: frontmatter block, reference file, or structured artifact generated during creation?
- [Affects R7][Technical] Which existing `skill-builder` reports can carry timing/token and qualitative review signals, and where do we need new helper output rather than new infrastructure?
- [Affects R8][Technical] What is the canonical baseline for brand-new skills in this repo when there is no prior skill version to compare against?
- [Affects R7][UX] Should description optimization be a mandatory final loop phase for non-trivial skills, or a named optional phase triggered by under/over-trigger evidence?

## Next Steps

-> `/ce:spec` for a full spec that defines:
- the creator-to-builder handoff artifact and its required fields
- the `skill-builder` iterative eval-loop contract and minimum evidence set
- the qualitative-plus-quantitative review flow
- the baseline-selection rules for new vs existing skills
- the lowest-churn repo-native implementation path for the upgraded loop
