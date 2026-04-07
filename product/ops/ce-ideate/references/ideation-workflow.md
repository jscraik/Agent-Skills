# Ideation Workflow

Read when: the request has routed to `ce-ideate`.

## Table of Contents
- [Interaction method](#interaction-method)
- [Phase 0: Resume and scope](#phase-0-resume-and-scope)
- [Phase 1: Codebase scan](#phase-1-codebase-scan)
- [Phase 2: Divergent ideation](#phase-2-divergent-ideation)
- [Phase 3-6 handoff](#phase-3-6-handoff)

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

## Phase 3-6 handoff

After candidate generation and merge are complete, continue with:
- adversarial filtering
- review checkpoint
- artifact write/update
- refine or handoff routing

Use `references/post-ideation-workflow.md` for the canonical post-ideation contract.
Do not load it before Phase 2 dispatch and merge are complete.
