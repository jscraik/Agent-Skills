---
name: ce-ideate
description: Generate and rank grounded improvement ideas for the current project before committing to one direction. Use when the user wants CE-stage idea generation before brainstorming in depth, not a general product brainstorm.
metadata:
  skill-type: team_automation
---

# CE Ideate

**Note: The current year is 2026.** Use this when dating ideation documents and checking recent ideation artifacts.

`ce-ideate` precedes `ce-brainstorm`.
- `ce-ideate` answers: "What are the strongest ideas worth exploring?"
- `ce-brainstorm` answers: "What exactly should one chosen idea mean?"
- `ce-plan` answers: "How should it be built?"

This workflow produces a ranked ideation artifact in `docs/ideation/`. It does **not** produce requirements, plans, or code.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Acceptance criteria](#acceptance-criteria)
- [Interaction Method](#interaction-method)
- [Core Principles](#core-principles)
- [Workflow](#workflow)
- [Focus modes](#focus-modes)
- [Execution rules](#execution-rules)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Gotchas](#gotchas)

## Interaction Method

Use the platform's blocking question tool when available (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.

Ask one question at a time. Prefer concise single-select choices when natural options exist.

## Core Principles

1. **Ground before ideating** - Scan the actual codebase first. Do not generate abstract product advice detached from the repository.
2. **Diverge before judging** - Generate the full idea set before evaluating any individual idea.
3. **Use adversarial filtering** - The quality mechanism is explicit rejection with reasons, not optimistic ranking.
4. **Preserve the original prompt mechanism** - Generate many ideas, critique the whole list, then explain only the survivors in detail. Do not let extra process obscure this pattern.
5. **Use agent diversity to improve the candidate pool** - Parallel sub-agents are a support mechanism for richer idea generation and critique, not the core workflow itself.
6. **Preserve the artifact early** - Write the ideation document before presenting results so work survives interruptions.
7. **Route action into brainstorming** - Ideation identifies promising directions; `ce-brainstorm` defines the selected one precisely enough for planning.
Read when: you need April 2026 standards rationale, ideation philosophy, or output variation guidance -> `Infrastructure/references/style-and-operating-guidance.md`.

## Working agreement
- Treat `ce-ideate` as the compound-engineering stage that decides which ideas are worth exploring next, not as generic brainstorming, planning, or implementation.
- Ground ideation in the actual repo first. Do not generate detached product advice that ignores the current codebase, docs, or issue signals.
- Preserve the core mechanism: generate many ideas first, critique the full combined list second, explain only the survivors in detail.
- Use subagents to widen idea diversity and critique quality only when the user has explicitly asked for delegation; otherwise widen the pool and critique inline without delegating.
- Keep the stage boundary explicit: `ce-ideate` ranks candidate directions, `ce-brainstorm` defines one chosen direction, and later CE stages turn that direction into specs and plans.
- Stay repo-first by default. Use repo context, `docs/solutions/`, and issue-tracker evidence when relevant. Do not add external market or web research unless the user explicitly asks for it.
- Be candid. Do not keep weak ideas out of politeness, novelty bias, or a desire to pad the shortlist.

## When to use
Use this skill when the user wants grounded improvement ideas generated, filtered, and ranked before committing to one direction.

Primary triggers:
- "use `ce:ideate` on this repo"
- "what should I improve?"
- "give me ideas for this project"
- "surprise me with improvements"
- "what would you change here?"
- "ideate on this project before we brainstorm one path"
- "top 3 improvements for developer experience"
- "what are users reporting that we should attack next?"

Non-triggers:
- the user already has one chosen idea and wants it shaped in depth; use `ce-brainstorm`
- the user wants a spec, plan, review, or direct implementation
- the user wants generic market research with no repo grounding
- the user wants a single bug fixed rather than ranked improvement directions

## Required inputs
- optional focus hint, which may be:
  - a concept
  - a path or subsystem
  - a constraint
  - a volume hint
- access to the current repo and any existing ideation docs under `docs/ideation/`
- optional issue-tracker intent if the user wants issue or bug patterns included in ideation
- optional recent context about constraints, audience, or success criteria

If the user provides no focus hint, proceed with open-ended ideation grounded in the repo.

## Deliverables
- a chosen ideation route: `fresh | resume`
- a grounding summary with:
  - codebase context
  - relevant past learnings
  - issue intelligence when present
- a merged candidate list generated before filtering
- explicit rejection reasons for cut ideas
- a ranked survivor set, usually 5-7 ideas unless the user requested a different volume
- optional survivor buckets when useful:
  - `quick win`
  - `high leverage`
  - `strategic bet`
- a durable ideation artifact in `docs/ideation/` before any handoff, sharing, or session end
- a next-step choice:
  - `ce-brainstorm`
  - refine ideation
  - share to Proof
  - end
- `schema_version: 1` in structured summaries when the user requests structured output

## Failure mode
If the repo cannot be scanned enough to ground ideas safely, stop and say what context is missing rather than inventing generic suggestions.

If the focus hint is so ambiguous that ideation would be misleading, ask one scoped clarification question.

If fewer than 5 strong survivors remain after adversarial filtering, report that honestly. Do not lower the bar just to fill a quota.

If no `docs/ideation/` directory exists, create it before writing the durable artifact.

## Constraints
- redact secrets, tokens, credentials, and sensitive user data in ideation artifacts, issue summaries, and examples
- do not skip repo grounding just because the user asks for speed
- do not turn ideation into requirements, implementation tasks, or code edits
- do not critique individual ideas before the combined candidate list exists
- do not let subagents replace orchestrator-owned ranking and survivor selection
- do not collapse issue-tracker intent into generic "bug focus" when the user actually wants issue-theme analysis
- do not route a selected survivor directly to planning or implementation; the next stage is `ce-brainstorm`
- do not treat external docs as default ideation input in this stage

## Acceptance criteria
- the request is clearly treated as ideation-before-brainstorm rather than brainstorm, planning, or implementation
- the repo is scanned before idea generation
- many ideas are generated before adversarial filtering begins
- the merged list is critiqued consistently with explicit rejection reasons
- survivors are materially stronger than a naive "give me ideas" list
- issue-tracker intent changes the grounding and frame selection when relevant
- the ideation artifact is written or updated before any handoff, Proof sharing, or session end
- if any required check fails, stop at the first failed gate and do not proceed until it is fixed or triaged

## Workflow
### Phase 0: Resume and scope
Check `docs/ideation/` for relevant ideation docs from the last 30 days. If one clearly matches the current focus or subsystem, offer `continue | start fresh`.

Infer:
- focus context
- volume override
- issue-tracker intent

Use the exact issue-intent and resume rules in `Infrastructure/references/ideation-workflow.md`.

### Phase 1: Codebase scan
Gather a short grounding summary before ideating:
- shallow repo context scan
- learnings search
- optional issue intelligence when the request is really about issue themes or bug patterns

Keep issue intelligence distinct from code-observed context. Use the bounded repo and issue scan rules in `Infrastructure/references/ideation-workflow.md`.

### Phase 2: Divergent ideation
Generate the full candidate pool before critique.

By default, generate the candidate pool inline in the main thread.

If the user has explicitly asked for delegation and wider parallel ideation would materially improve coverage:
- each ideation subagent targets about 7-8 raw ideas
- the merged list usually lands around 20-30 unique candidates after dedupe
- the orchestrator may synthesize a few stronger cross-cutting combinations

If delegation was not explicitly requested, the tool is unavailable, or subagents are unnecessary, generate the full candidate pool inline before critique.

Use the frame-selection, merge, dedupe, and cross-cutting synthesis rules in `Infrastructure/references/ideation-workflow.md`.

### Phases 3-6: Filter, present, preserve, hand off
After Phase 2 merge and synthesis are complete, load `Infrastructure/references/post-ideation-workflow.md` and run:
- adversarial filtering
- review checkpoint formatting
- artifact write and resume semantics
- refine or handoff routing

Do not load `Infrastructure/references/post-ideation-workflow.md` before Phase 2 candidate generation completes.
Do not skip from ideation directly to planning or implementation.

## Focus modes
- `open-ended`: no focus hint, broad repo-grounded ideation
- `focused`: path, subsystem, capability, or constraint narrows the search space
- `issue-grounded`: issue or bug pattern analysis shapes the grounding and ideation frames
- `resume`: continue an existing ideation doc, preserve statuses, and append to the session log

## Execution rules
- Use the platform's blocking question tool (`AskUserQuestion`, `request_user_input`, or `ask_user`) and ask one question at a time.
- Keep the initial codebase scan shallow; do not do deep implementation analysis before ideating.
- Use `repo-research-analyst` and `learnings-researcher` for bounded grounding only when delegation was explicitly requested; otherwise perform the equivalent grounding inline.
- If an issue-intelligence helper exists, use it for issue-theme clustering. Otherwise, do a bounded direct issue-theme pass with available repo and issue tools, and clearly note the fallback.
- When ideation subagents are explicitly requested, run them in the foreground because their outputs are needed before the next phase.
- Give ideation subagents starting biases, not hard fences. Cross-cutting ideas are allowed.
- Keep final survivor scoring in the orchestrator so ranking remains consistent.
- Prepare the preservation-ready content as you go, but keep the main repo artifact write after the review checkpoint unless handoff, sharing, or session end would otherwise risk losing the work.

## Validation
- fail fast: stop at the first failed gate, fix or report it, rerun that gate, then continue
- verify the repo was scanned before idea generation
- verify the candidate pool was generated before critique
- verify every rejected idea has a one-line reason
- verify the survivors are grounded in current repo evidence
- verify issue-tracker intent changed the grounding path when present
- verify a selected survivor routes to `ce-brainstorm`, not directly to planning or implementation
- verify the ideation artifact exists or is updated before any handoff, sharing, or session end

## Anti-patterns
- asking for deep design decisions before identifying whether any candidate direction is worth exploring
- dumping generic product advice with no repo grounding
- critiquing or ranking ideas before the combined candidate list exists
- letting one ideation frame dominate when a stronger cross-cutting idea is emerging
- mistaking issue-tracker intent for a single-bug debugging request
- writing requirements, plans, or code inside the ideation stage
- routing a chosen idea straight to `ce-plan` or `ce-work`
- keeping weak ideas just to pad the shortlist
- novelty theater: rewarding surprising ideas that do not fit the repo's actual constraints
- template trap: producing the same fashionable ideas regardless of project evidence
- NEVER skip the rejection step just because the first few ideas feel good
- DO NOT let issue themes erase higher-leverage opportunities outside the reported pain
- AVOID writing the durable artifact so early that it freezes weak survivors before review

## Examples
User says:
- "Use `ce:ideate` and tell me what this repo should improve next."
- "Give me the top 3 improvements for the auth subsystem before we brainstorm one."
- "Surprise me with grounded improvements for this project."
- "What would you change in `Plugins/compound-engineering/skills/`?"
- "Look at the open issues and tell me which product directions are actually worth exploring."
- "Resume the ideation doc we started last week and raise the bar on the survivors."

## References
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`
- Prompt parity map: `Infrastructure/references/source-parity.md`
- Phase 0-2 ideation workflow: `Infrastructure/references/ideation-workflow.md`
- Phase 3-6 post-ideation workflow: `Infrastructure/references/post-ideation-workflow.md`
- Standards and operating guidance: `Infrastructure/references/style-and-operating-guidance.md`

## See Also

| Skill | When to use together |
|---|---|
| [[ce-brainstorm]] | Take one selected survivor from ranked ideation into clarified problem framing and approach shaping |
| [[ce-compound]] | Route broader CE lifecycle work or preserve learning after implementation rather than before exploration |
| [[ce-plan]] | Use only after a brainstormed direction has been selected and specified enough to plan |

**Topic map:** [[product-ops]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
