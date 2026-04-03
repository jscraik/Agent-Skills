# Ideation Workflow

Read when: the request has routed to `ce-ideate`.

## Table of Contents
- [Interaction method](#interaction-method)
- [Phase 0: Resume and scope](#phase-0-resume-and-scope)
- [Phase 1: Codebase scan](#phase-1-codebase-scan)
- [Phase 2: Divergent ideation](#phase-2-divergent-ideation)
- [Phase 3: Adversarial filtering](#phase-3-adversarial-filtering)
- [Phase 4: Review checkpoint and artifact timing](#phase-4-review-checkpoint-and-artifact-timing)
- [Phase 5: Write the ideation artifact](#phase-5-write-the-ideation-artifact)
- [Phase 6: Refine or hand off](#phase-6-refine-or-hand-off)

## Interaction method

- Use the runtime's blocking question tool when available.
- If the blocking question tool is unavailable, present numbered options in chat and wait for the user's reply before proceeding.
- Ask one question at a time.
- Prefer concise single-select choices when natural options exist.
- When a clear recommendation exists, lead with it.

## Phase 0: Resume and scope

### Check for recent ideation work

Inspect `docs/ideation/` for ideation docs from the last 30 days.

Treat a doc as relevant when:
- the topic matches the requested focus
- the path or subsystem overlaps
- the request is open-ended and there is an obvious recent open ideation doc
- the issue-grounded status matches

If a relevant doc exists, offer:
1. continue from it
2. start fresh

If continuing:
- read the doc
- summarize what was already explored
- preserve idea statuses and session log entries
- update the same file rather than duplicating it

### Interpret focus and volume

Infer three things from the argument:
- focus context
- volume override
- issue-tracker intent

Issue-tracker intent applies when the user's main intent is about issue or bug theme analysis:
- `bugs`
- `github issues`
- `open issues`
- `issue patterns`
- `what users are reporting`
- `bug reports`
- `issue themes`

Do not trigger issue-tracker intent for a simple bug focus like:
- `bug in auth`
- `fix the login issue`
- `the signup bug`

When signals are combined, interpret them in this order:
1. detect issue-tracker intent first
2. detect volume override second
3. treat the remainder as the focus hint

The focus narrows which issues or repo areas matter; the volume override controls how many survivors to keep.

Default volume:
- each ideation subagent generates about 7-8 ideas
- merged and deduped output usually yields 20-30 unique candidates
- keep the top 5-7 survivors

Honor clear overrides like:
- `top 3`
- `100 ideas`
- `go deep`
- `raise the bar`

## Phase 1: Codebase scan

Before generating ideas, gather repo context.

Run in the foreground because the results are needed immediately:

1. quick context scan
2. learnings search
3. issue intelligence when issue-tracker intent is active

### Quick context scan

Use a bounded subagent or equivalent direct workflow to gather:
- project shape
- language and framework
- top-level directory layout
- notable patterns or conventions
- obvious pain points or gaps
- likely leverage points

Keep this scan shallow. Prefer:
- `AGENTS.md` first
- `CLAUDE.md` only as a compatibility fallback
- `README.md` when neither instruction file exists

Read top-level documentation and directory structure only. Do not do deep code search, issue analysis, or contribution-process review in this pass.

### Learnings search

Use `learnings-researcher` when available to search `docs/solutions/` and related institutional memory for relevant patterns, repeated pain, or prior fixes.

### Issue intelligence

When issue-tracker intent is active:
- use the dedicated issue-intelligence helper if the runtime has one
- otherwise run a bounded direct issue-theme pass with available issue tools

If issue analysis fails because auth, remote, or tooling is unavailable:
- warn briefly
- continue with standard ideation

If there are fewer than 5 total issues:
- note `Insufficient issue signal for theme analysis`
- continue with default ideation frames

Keep the grounding summary split into:
- `Codebase context`
- `Past learnings`
- `Issue intelligence` when present

When issue intelligence is present, preserve the returned:
- theme titles
- theme descriptions
- issue counts
- trend directions

Do not do external research by default in this runtime workflow.

## Phase 2: Divergent ideation

Preserve this exact mechanism:
1. generate many ideas first
2. critique the combined list second
3. explain only the survivors in detail

Push past the safe obvious layer before critique begins. The first few ideas are often the least useful.

### Per-agent expectations

Give each ideation subagent:
- the same grounding summary
- the same focus hint
- the per-agent volume target
- instruction to return raw candidates only

Each idea should return a compact structure with:
- `title`
- `summary`
- `why_it_matters`
- `evidence`
- optional local signals like `boldness` or `focus_fit`

### Default ideation frames

When issue-tracker intent is not active:
- user or operator pain and friction
- unmet need or missing capability
- inversion, removal, or automation of a painful step
- assumption-breaking or reframing
- leverage and compounding effects
- extreme cases, edge cases, or power-user pressure

### Issue-grounded frames

When issue intelligence is active and themes were returned:
- use high-confidence and medium-confidence themes as ideation frames
- if fewer than 4 such frames exist, pad with:
  - leverage and compounding effects
  - assumption-breaking or reframing
  - inversion, removal, or automation of a painful step
- cap total frames at 6
- if more than 6 themes qualify, keep the top 6 by issue count and note the rest as minor themes

### Merge and synthesis

After any approved ideation subagents return, or after inline ideation completes:
1. merge outputs
2. dedupe overlapping ideas
3. synthesize stronger cross-cutting combinations when two or more ideas naturally combine into a better direction

Expect 3-5 cross-cutting additions at most.

Spread ideas across dimensions when justified:
- workflow and DX
- reliability
- extensibility
- missing capabilities
- docs and knowledge compounding
- quality and maintenance
- leverage on future work

If a focus hint was provided, weight the merged list toward it without excluding stronger adjacent ideas that the repo evidence clearly supports.

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
