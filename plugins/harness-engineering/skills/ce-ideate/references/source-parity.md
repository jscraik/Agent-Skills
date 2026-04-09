# Source Parity Notes

## Table of Contents
- [Source input](#source-input)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)
- [Known constraints](#known-constraints)

## Source input
This package preserves and restructures the upstream `ce:ideate` skill while retaining local governance hardening.

Pinned donor snapshot:
- repo: `EveryInc/compound-engineering-plugin`
- commit: `0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c`
- path: `plugins/compound-engineering/skills/ce-ideate/SKILL.md`

## Preserved behaviors
- `ce:ideate` explicitly precedes `ce:brainstorm`
- stage boundary remains explicit:
  - ideate what is worth exploring
  - brainstorm what one chosen idea should mean
  - plan how to build it
- optional focus hint handling:
  - concept
  - path
  - constraint
  - volume hint
- recent-ideation resume flow with continue/start-fresh behavior and status preservation
- issue-tracker intent detection stays distinct from simple bug-focus phrasing
- combined intent parsing order remains:
  - issue-tracker intent first
  - volume override second
  - remainder treated as focus hint
- codebase scan and learnings search occur before idea generation
- conditional issue-intelligence lane is preserved with bounded fallback behavior
- many-ideas -> critique -> survivors mechanism is preserved
- frame-based ideation remains starting-bias, not hard-constraint
- orchestrator-owned merge, dedupe, and cross-cutting synthesis are preserved
- durable ideation artifact behavior in `docs/ideation/` remains required before handoff/sharing/session end
- handoff remains `ce-brainstorm` (not direct planning/implementation)

## Intentional modernizations
- aligned donor parity to `0ae91dcc...`, including deferred-load behavior where post-merge workflow details live in a dedicated reference (`post-ideation-workflow.md`) loaded only after Phase 2 completes
- kept `SKILL.md` route-critical and moved richer standards/philosophy/variation guidance into `references/style-and-operating-guidance.md`
- split workflow references into:
  - `ideation-workflow.md` for interaction + Phases 0-2
  - `post-ideation-workflow.md` for Phases 3-6
- retained realistic trigger examples and strengthened deterministic wording for execution boundaries
- preserved context depth by relocation (not deletion), consistent with progressive-disclosure governance

## Known constraints
- blocking question tool names remain runtime-specific (`AskUserQuestion`, `request_user_input`, `ask_user`), but behavior remains one-question-at-a-time
- helper-role availability still varies by runtime; bounded inline fallback remains mandatory
- Proof sharing remains a workflow hook and assumes the runtime has a standard markdown-sharing path
