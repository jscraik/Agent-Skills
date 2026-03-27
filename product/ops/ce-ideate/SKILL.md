---
name: ce-ideate
description: Generate and rank grounded improvement ideas for the current project before committing to one direction. Use when the user wants CE-stage idea generation before brainstorming in depth, not a general product brainstorm.
metadata:
  skill-type: team_automation
---

# CE Ideate

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Acceptance criteria](#acceptance-criteria)
- [Standards snapshot (March 2026)](#standards-snapshot-march-2026)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Focus modes](#focus-modes)
- [Execution rules](#execution-rules)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Encouraging variation](#encouraging-variation)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Gotchas](#gotchas)

## Working agreement
- Treat `ce-ideate` as the compound-engineering stage that decides which ideas are worth exploring next, not as generic brainstorming, planning, or implementation.
- Ground ideation in the actual repo first. Do not generate detached product advice that ignores the current codebase, docs, or issue signals.
- Preserve the core mechanism: generate many ideas first, critique the full combined list second, explain only the survivors in detail.
- Use subagents to widen idea diversity and critique quality, not to replace orchestrator judgment.
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

## Standards snapshot (March 2026)
- Keep the skill scoped to one reusable job with routing-first frontmatter that says what it does and when to use it.
- Use progressive disclosure: keep `SKILL.md` focused on route-critical behavior and move templates, frame logic, and artifact details into `references/`.
- Prefer realistic positive and negative examples plus eval-backed routing tests over hidden prompt assumptions.
- Preserve strong internal reasoning loops with explicit critique and verification rather than one-pass idea dumping.
- Keep external research out of the default runtime path for this stage; repo evidence comes first, while the skill package itself should still be built and maintained against current OpenAI and Codex guidance.

## Philosophy
- Good ideation is grounded divergence plus disciplined rejection.
- The first obvious ideas are rarely the best ideas.
- The artifact matters because good directions are easy to lose between sessions.
- Issue themes can sharpen ideation, but they should not imprison it inside reported pain alone.
- The orchestrator's real job is not to think of a lot of ideas. It is to identify which ideas survive skeptical scrutiny and deserve deeper exploration.
- Prefer practical brilliance over speculative novelty. A strong survivor should feel unusually useful, not merely interesting.

Guiding questions:
- What improvements are actually supported by the repo's current shape and pain points?
- Which ideas create leverage for future work instead of isolated local wins?
- Which candidates are merely plausible, and which ones are worth spending a brainstorm on?
- If a future teammate opened the ideation doc cold, would they understand why the survivors won?

## Workflow
### Phase 0: Resume and scope
Check `docs/ideation/` for relevant ideation docs from the last 30 days. If one clearly matches the current focus or subsystem, offer `continue | start fresh`.

Infer:
- focus context
- volume override
- issue-tracker intent

Use the exact issue-intent and resume rules in `references/ideation-workflow.md`.

### Phase 1: Codebase scan
Gather a short grounding summary before ideating:
- shallow repo context scan
- learnings search
- optional issue intelligence when the request is really about issue themes or bug patterns

Keep issue intelligence distinct from code-observed context. Use the bounded repo and issue scan rules in `references/ideation-workflow.md`.

### Phase 2: Divergent ideation
Generate the full candidate pool before critique.

By default:
- each ideation subagent targets about 7-8 raw ideas
- the merged list usually lands around 20-30 unique candidates after dedupe
- the orchestrator may synthesize a few stronger cross-cutting combinations

Use the frame-selection, merge, dedupe, and cross-cutting synthesis rules in `references/ideation-workflow.md`.

### Phase 3: Adversarial filtering
Attack the merged list skeptically.

Prefer a two-layer critique:
- skeptical critique subagents
- orchestrator-owned final scoring and ranking

Use the rejection criteria and survivor rubric in `references/ideation-workflow.md`, including value, complexity, reliability, adoption, reversibility, and evidence-fit checks.

### Phase 4: Review checkpoint
Present only the surviving ideas in structured form before final preservation:
- title
- description
- rationale
- downsides
- confidence
- estimated complexity
- optional bucket:
  - `quick win`
  - `high leverage`
  - `strategic bet`

Also include a short rejection summary so the user can see that the list was challenged, not merely ranked.

### Phase 5: Write the ideation artifact
Write or update the durable ideation doc when the candidate set is good enough to preserve, and always before:
- `ce-brainstorm`
- Proof sharing
- session end

Use the artifact path, markdown structure, and session-log rules in `references/ideation-workflow.md`.

### Phase 6: Refine or hand off
After the review checkpoint, route to one of:
1. brainstorm a selected idea
2. refine the ideation
3. share to Proof
4. end the session

Do not skip from ideation directly to planning or implementation.

## Focus modes
- `open-ended`: no focus hint, broad repo-grounded ideation
- `focused`: path, subsystem, capability, or constraint narrows the search space
- `issue-grounded`: issue or bug pattern analysis shapes the grounding and ideation frames
- `resume`: continue an existing ideation doc, preserve statuses, and append to the session log

## Execution rules
- Use blocking question tools when available and ask one question at a time.
- Keep the initial codebase scan shallow; do not do deep implementation analysis before ideating.
- Use `repo-research-analyst` and `learnings-researcher` when available for bounded grounding.
- If an issue-intelligence helper exists, use it for issue-theme clustering. Otherwise do a bounded direct issue-theme pass with available repo and issue tools, and clearly note the fallback.
- Run ideation subagents in the foreground because their outputs are needed before the next phase.
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

## Encouraging variation
IMPORTANT: Outputs should vary with focus, repo shape, and evidence quality.
- Open-ended ideation should feel wider and more exploratory.
- Focused ideation should lean harder into local leverage and adjacent opportunities.
- Issue-grounded ideation should visibly distinguish user-reported themes from code-observed pain points.
- High-signal repos may justify bolder survivors; low-signal repos should show more conservative confidence.
- Rejection summaries should reflect the actual weaknesses of the discarded ideas, not a canned reason list.

## Examples
When the user asks things like:
- "Use `ce:ideate` and tell me what this repo should improve next."
- "Give me the top 3 improvements for the auth subsystem before we brainstorm one."
- "Surprise me with grounded improvements for this project."
- "What would you change in `plugins/compound-engineering/skills/`?"
- "Look at the open issues and tell me which product directions are actually worth exploring."
- "Resume the ideation doc we started last week and raise the bar on the survivors."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Prompt parity map: `references/source-parity.md`
- Detailed ideation workflow: `references/ideation-workflow.md`

## See Also

| Skill | When to use together |
|---|---|
| [[ce-brainstorm]] | Take one selected survivor from ranked ideation into clarified problem framing and approach shaping |
| [[ce-compound]] | Route broader CE lifecycle work or preserve learning after implementation rather than before exploration |
| [[ce-plan]] | Use only after a brainstormed direction has been selected and specified enough to plan |

**Topic map:** [[product-ops]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
