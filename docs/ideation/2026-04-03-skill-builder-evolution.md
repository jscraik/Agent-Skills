---
date: 2026-04-03
topic: skill-builder-evolution
focus: repo-grounded improvement directions for utilities/skill-builder after overlap and spec-drift review
route: fresh
---

# Ideation: Skill Builder Evolution

## Table of Contents
- [Codebase Context](#codebase-context)
- [Candidate Pool](#candidate-pool)
- [Ranked Ideas](#ranked-ideas)
- [Refinement Checkpoint](#refinement-checkpoint)
- [Recommended Sequence](#recommended-sequence)
- [Rejection Summary](#rejection-summary)
- [Session Log](#session-log)

## Codebase Context

This repo currently has three relevant surfaces in play:
- `utilities/skill-builder/` is an opinionated, repo-native lifecycle skill with quality gates, evals, graph contracts, install-distribute behavior, and packaging guidance.
- `skills-system/skill-creator/` is still present as the starter authoring surface for first-draft skill creation.
- `skills-system/skill-installer/` is still present as a focused install and curated-import surface.

Observed leverage signals:
- `skill-builder` has become a mature operational package rather than a light wrapper: it carries extensive `references/`, many scripts, templates, workflows, evals, graph-profile data, and UI metadata.
- `skill-builder` now explicitly claims creation, improvement, auditing, packaging, and install-distribute responsibilities in one surface.
- `skill-creator` and `skill-installer` remain separately discoverable, and both still position `skill-builder` as a companion rather than a replacement.
- `skill-builder` has real validator credibility already: repo format lint passes, progressive-disclosure lint passes, `quick_validate.py` passes, `skill_gate.py` passes, analyzer score is strong, and graph profile checks are clean.
- The main correctness drift found in this review is not execution quality but standards drift: `skill-builder` and the repo linter still describe the official frontmatter whitelist too narrowly.
- The main product risk is routing ambiguity: a broad expert skill now overlaps with narrower starter and install skills while still presenting narrow UI metadata.

Past learnings:
- repo memory already stresses that long skill docs should keep route-critical guidance in `SKILL.md` and push detail into `references/`.
- repo memory also emphasizes validating against current official docs before declaring completion for utility skills.
- earlier work in this repo already treated `skill-builder` as the method for improving other skills, which reinforces its value as an expert maintainer surface rather than a starter abstraction.

Issue intelligence:
- not requested for this run

## Candidate Pool

1. Update `skill-builder` and repo validators to support current official frontmatter keys, including `compatibility`
2. Reposition `skill-builder` explicitly as an expert lifecycle maintainer skill rather than a default starter skill
3. Remove install-distribute behavior from `skill-builder` and hand it back to `skill-installer`
4. Keep install-distribute in `skill-builder`, but downgrade it to a delegated wrapper that routes to `skill-installer` when the task is primarily installation
5. Add an overlap matrix and routing truth table across `skill-builder`, `skill-creator`, `skill-installer`, and `plugin-builder`
6. Add routing regression evals that pressure-test ambiguous prompts across the overlapping skill set
7. Introduce a two-tier experience: starter path via `skill-creator`, expert path via `skill-builder`
8. Make `skill-builder` explicit-only in `agents/openai.yaml` and widen its UI description to match its real scope
9. Build a single “skill lifecycle” plugin that bundles creator, builder, installer, and plugin-conversion workflows with clear internal handoffs
10. Add a generated standards-sync check that diff-checks repo assumptions against `references/official-spec.md` and current official docs
11. Split `skill-builder` into two repo-native skills: `skill-authoring-review` and `skill-distribution-governor`
12. Keep one broad skill, but add mode-specific entry prompts and response contracts so the first turn immediately narrows scope
13. Add a “recommended next skill” footer to `skill-builder`, `skill-creator`, and `skill-installer` so handoffs become explicit and discoverable
14. Narrow `skill-builder` frontmatter description so implicit triggering happens only for advanced lifecycle tasks
15. Add a maintenance rubric for deciding when a starter skill graduates into an expert maintainer surface

## Ranked Ideas

### 1. Expert-position `skill-builder` and make its routing honest
**Description:** Keep `skill-builder` broad, but explicitly position it as the repo's expert lifecycle maintainer skill instead of a de facto replacement for `skill-creator`. Update `agents/openai.yaml`, frontmatter wording, and invocation policy so its discoverability matches its actual scope.
**Rationale:** The strongest evidence in the repo is that `skill-builder` is already valuable in its broader form. The problem is not that it grew; the problem is that its current presentation still reads like a narrow create-or-update skill. Fixing positioning preserves its power without pretending it is the default starter surface.
**Downsides:** Better positioning alone will not solve all overlap confusion if the surrounding skills keep vague boundaries.
**Confidence:** 93%
**Complexity:** Low
**Bucket:** quick win
**Status:** Unexplored

### 2. Add a canonical overlap and delegation contract across the skill-authoring family
**Description:** Create one explicit routing matrix covering `skill-creator`, `skill-builder`, `skill-installer`, and `plugin-builder`, then encode that contract in descriptions, See Also guidance, and examples so ambiguous prompts resolve more consistently.
**Rationale:** The repo's current problem is really family-level product shape, not just one stale paragraph. A visible overlap contract would reduce routing ambiguity, preserve specialization, and let `skill-builder` stay powerful without forcing a brittle split too early.
**Downsides:** A written matrix can drift unless evals and docs are updated alongside it.
**Confidence:** 91%
**Complexity:** Medium
**Bucket:** high leverage
**Status:** Unexplored

### 3. Ship routing regression evals for ambiguous creator-builder-installer prompts
**Description:** Add eval cases that intentionally pressure ambiguous requests like “make me a skill,” “upgrade this skill and install it,” and “package this for reuse” so the skill family is tested as a system rather than as isolated artifacts.
**Rationale:** The repo already values evaluators and validator evidence. Once overlap exists, the highest-leverage protection is regression coverage for prompt-routing seams, not more hand-written doctrine alone.
**Downsides:** Cross-skill eval harnesses can be fiddly and may expose broader repo runtime inconsistencies that take time to normalize.
**Confidence:** 88%
**Complexity:** Medium
**Bucket:** high leverage
**Status:** Unexplored

### 4. Fix standards drift by making official-spec sync testable, not advisory
**Description:** Update the frontmatter claims and validators to support current official keys, then add a lightweight standards-sync check so future official-spec drift is caught before repo guidance goes stale again.
**Rationale:** The concrete P1 finding is real and easy to justify from current docs. Treating this as a repeatable sync problem rather than a one-off text fix gives the repo a stronger maintenance pattern.
**Downsides:** Official docs can move faster than a local sync check can elegantly model, so the check should be narrow and intentional.
**Confidence:** 95%
**Complexity:** Low
**Bucket:** quick win
**Status:** Unexplored

### 5. Preserve breadth, but turn install-distribute into a delegated companion path
**Description:** Keep `skill-builder` capable of managing distribution concerns, but make install-heavy requests explicitly route or delegate to `skill-installer` once the task crosses from lifecycle judgment into install execution.
**Rationale:** Your stated intent is that `skill-builder` has folded in installer concerns. A full rollback may be unnecessary. A delegated-companion model preserves the broader lifecycle view while restoring crisp ownership for install mechanics.
**Downsides:** This still requires careful wording so users understand why both skills exist.
**Confidence:** 84%
**Complexity:** Medium
**Bucket:** strategic bet
**Status:** Unexplored

### 6. Introduce a two-tier authoring experience instead of forcing one default
**Description:** Make the repo explicitly support two legitimate entrypoints: `skill-creator` for first drafts and simple authoring, `skill-builder` for expert improvement, governance, packaging, and distribution decisions.
**Rationale:** This aligns most closely with current official guidance while respecting the repo's evolved internal tooling. It treats your enhanced `skill-builder` as a deliberate expert tool rather than a failed clone of the starter path.
**Downsides:** Two-tier systems can still confuse users unless the handoff language becomes very explicit.
**Confidence:** 90%
**Complexity:** Medium
**Bucket:** high leverage
**Status:** Unexplored

## Refinement Checkpoint

The first pass produced six strong survivors, but they cluster into three more actionable bundles. These bundles are easier to choose between than the raw list because each one implies a different product posture for the repo.

### Bundle A: Honest Expert Maintainer

Combines:
- Idea 1: expert-position `skill-builder`
- Idea 4: fix standards drift and make official-spec sync testable
- part of Idea 8 from the candidate pool: widen metadata and consider explicit-only invocation

What it changes:
- `skill-builder` keeps its broad lifecycle scope
- repo-facing copy stops pretending it is only a create-or-update surface
- the concrete correctness gap around `compatibility` gets fixed immediately

Why this bundle is strong:
- lowest implementation cost
- directly addresses the live correctness issue
- matches the repo reality visible in `utilities/skill-builder/agents/openai.yaml`, where the UI description is currently too narrow

What it does not solve alone:
- family-level overlap remains partly implicit
- `skill-creator` and `skill-installer` still need clearer relationship language

Decision test:
- choose this first if the main goal is to make the current broad design honest, accurate, and safe without restructuring the family yet

### Bundle B: Skill Family Contract

Combines:
- Idea 2: overlap and delegation contract
- Idea 3: routing regression evals
- Idea 6: two-tier authoring experience

What it changes:
- the repo formally recognizes a starter path and an expert path
- overlapping skill triggers are documented as a system rather than left to implication
- evals protect the routing seams against future drift

Why this bundle is strong:
- highest leverage on long-term clarity
- best fit if the real pain is ambiguity between skill surfaces rather than the quality of any one skill
- gives `skill-builder` permission to stay broad without becoming the accidental answer to every authoring prompt

What it does not solve alone:
- the frontmatter/spec drift still needs a concrete patch
- metadata can remain misleading unless Bundle A is also adopted

Decision test:
- choose this first if the main goal is to make the whole authoring family legible and stable, even if it takes more work than a narrow fix

### Bundle C: Delegated Installer Companion

Combines:
- Idea 5: preserve breadth but delegate install-heavy execution
- supporting parts of Idea 2: explicit handoff rules

What it changes:
- `skill-builder` remains lifecycle-aware
- `skill-installer` regains crisp ownership for execution-heavy install flows
- overlap becomes intentional rather than accidental

Why this bundle is strong:
- best compromise if you want to keep the fold-in concept without letting it erase the installer's reason to exist
- reduces the risk that one broad skill becomes bloated operationally

What it does not solve alone:
- it depends on clearer positioning work
- without family-level routing doctrine, delegation can still feel arbitrary

Decision test:
- choose this if your strongest instinct is "keep the bigger shape, but restore a clean installer handoff"

## Recommended Sequence

If the goal is to improve the repo with the least regret, the best sequence is:

1. Bundle A first
2. Bundle B second
3. Bundle C only if install overlap still feels noisy after A and B

Why this sequence wins:
- Bundle A fixes the only confirmed standards error and aligns presentation with reality.
- Bundle B then turns that clearer posture into a durable family contract with eval coverage.
- Bundle C is a policy refinement, not the first move; it is easier to judge once positioning and routing rules are explicit.

Current recommendation:
- if you want the fastest confident move, brainstorm Bundle A
- if you want the biggest structural payoff, brainstorm Bundle B
- if you already know install overlap is the pain point, brainstorm Bundle C

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | Remove install-distribute from `skill-builder` entirely | Too destructive relative to the user's stated intent. The repo already reflects deliberate broadening, so a full rollback is not the strongest first move. |
| 2 | Keep one broad skill and solve it only with mode-specific response contracts | Helpful supporting tactic, but weaker than fixing positioning and family-level overlap contracts. |
| 3 | Split `skill-builder` into two new repo-native skills | Plausible later, but premature without first testing whether clearer positioning and overlap rules solve the main confusion. |
| 4 | Build a single lifecycle plugin immediately | Attractive packaging move, but second-order. The routing and contract issues should be clarified before bundling them more tightly. |
| 5 | Add a “recommended next skill” footer only | Useful, but too small on its own. It feels like a component of the overlap-contract work rather than a top-level direction. |
| 6 | Narrow `skill-builder` description alone | Valuable, but too incomplete by itself; metadata changes without family-level routing doctrine would leave hidden ambiguity intact. |
| 7 | Add a maintenance rubric for starter-to-expert graduation | Good governance support, but not as urgent as fixing the current live overlap and standards drift. |

## Session Log

- 2026-04-03: Fresh ideation run focused on `utilities/skill-builder` after review findings identified one correctness drift and broader scope/routing ambiguity. Generated 15 candidates, kept 6 survivors. No issue-theme pass requested.
- 2026-04-03: Evidence base emphasized current overlap with `skills-system/skill-creator` and `skills-system/skill-installer`, strong existing validator quality for `skill-builder`, and a concrete standards drift around frontmatter key support.
- 2026-04-03: Resume refinement pass collapsed the six survivors into three decision bundles so the next stage can choose between posture correction, family-level routing clarity, or installer delegation instead of comparing isolated ideas.
