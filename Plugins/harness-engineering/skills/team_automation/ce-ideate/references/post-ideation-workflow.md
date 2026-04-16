# Post-Ideation Workflow

Read when: Phase 2 candidate generation and merge are complete, and you are ready to filter, present, preserve, and hand off.

## Table of Contents
- [Phase 3: Adversarial filtering](#phase-3-adversarial-filtering)
- [Phase 4: Review checkpoint and artifact timing](#phase-4-review-checkpoint-and-artifact-timing)
- [Phase 5: Write the ideation artifact](#phase-5-write-the-ideation-artifact)
- [Phase 6: Refine or hand off](#phase-6-refine-or-hand-off)

## Phase 3: Adversarial filtering

Critique every generated idea critically.

Prefer a two-layer critique:
1. skeptical subagents attack the merged list from different angles when delegation was explicitly requested or approved
2. the orchestrator applies one consistent rubric and decides the final ranking

If delegation was not explicitly requested or approved, perform the skeptical critique inline before final ranking.

Do not let critique agents generate replacement ideas unless the user explicitly requested refinement.

### Rejection criteria

Common rejection reasons:
- too vague
- not actionable
- duplicates a stronger idea
- not grounded in the current repo
- too expensive relative to likely value
- already covered by current workflows or docs
- better handled as a brainstorm variant instead of a project-improvement direction
- novelty theater: surprising on paper but weakly connected to real repo pain or leverage
- template trap: one of the same fashionable ideas that would appear in almost any project review
- adds complexity, maintenance burden, or workflow overhead that the upside does not justify
- difficult to stage, test, or roll back without strong enough value to compensate

### Survivor rubric

Score survivors against:
- `user_value`
- `agent_value`
- `differentiation`
- `implementation_cost`
- `complexity_burden`
- `reliability_impact`
- `adoption_likelihood`
- `reversibility`
- `evidence_fit`

Interpretation guidance:
- prefer practical brilliance over speculative novelty
- reject ideas whose upside is real but too small for the complexity they introduce
- favor ideas that help both humans and agents when the repo clearly benefits from both
- do not reward novelty if it weakens clarity, reliability, or maintainability
- use cross-cutting leverage as a tiebreaker when two ideas score similarly

Default target:
- keep 5-7 survivors
- if too many survive, run a stricter second pass
- if fewer survive, report that honestly

## Phase 4: Review checkpoint and artifact timing

Present the surviving ideas before the main repo artifact is finalized.

For each survivor show:
- title
- description
- rationale
- downsides
- confidence score
- estimated complexity
- optional bucket:
  - `quick win`
  - `high leverage`
  - `strategic bet`

Also include a short rejection summary.

Allow brief follow-up questions and lightweight clarification before finalizing the main repo artifact when that improves survivor quality.

### Artifact timing rule

The source prompt carries two good instincts:
- preserve the work early so it is not lost
- do not freeze weak survivors before review

Resolve that tension this way:
- prepare preservation-ready content as the workflow runs
- present survivors first as the review checkpoint
- write or update the durable repo artifact once the candidate set is good enough to preserve
- always write before handoff, sharing, or session end

## Phase 5: Write the ideation artifact

Ensure `docs/ideation/` exists.

Use:
- `docs/ideation/YYYY-MM-DD-<topic>-ideation.md`
- `docs/ideation/YYYY-MM-DD-open-ideation.md` when no focus exists

Template:

```markdown
---
date: YYYY-MM-DD
topic: <kebab-case-topic>
focus: <optional focus hint>
---

# Ideation: <Title>

## Codebase Context
[Grounding summary]

## Ranked Ideas

### 1. <Idea Title>
**Description:** [Concrete explanation]
**Rationale:** [Why this improves the project]
**Downsides:** [Tradeoffs or costs]
**Confidence:** [0-100%]
**Complexity:** [Low / Medium / High]
**Status:** [Unexplored / Explored]

## Rejection Summary

| # | Idea | Reason Rejected |
|---|------|-----------------|
| 1 | <Idea> | <Reason rejected> |

## Session Log
- YYYY-MM-DD: Initial ideation — <candidate count> generated, <survivor count> survived
```

If resuming:
- update the existing file in place
- append to the session log
- preserve explored markers

## Phase 6: Refine or hand off

Offer:
1. brainstorm a selected idea
2. refine the ideation
3. share to Proof
4. end the session

### Brainstorm a selected idea

If the user picks a survivor:
- write or update the ideation doc first
- mark that idea `Explored`
- note the brainstorm date in the session log
- invoke `ce-brainstorm` with the selected idea as the seed

### Refine the ideation

Map refinement intent like this:
- `add more ideas` or `explore new angles` -> back to divergent ideation
- `re-evaluate` or `raise the bar` -> back to adversarial filtering
- `dig deeper on idea #N` -> deepen only that idea

After each refinement:
- update the ideation doc before handoff, sharing, or session end
- append a session log entry

### Share to Proof

If the user requests it:
- write or update the ideation doc first
- share using the standard Proof markdown upload pattern already used in the broader workflow ecosystem
- return to next-step options after sharing

### End the session

When ending:
- offer to commit only the ideation doc
- do not create a branch
- do not push
- if the user declines, leave the file uncommitted
