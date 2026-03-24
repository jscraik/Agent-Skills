---
name: compound-engineering-router
description: Route compound-engineering requests to the correct CE stage or support meta-mode. Use when the user wants CE ideation, spec, planning, work, review, compound learning, or context compaction and the right stage is not yet explicit.
metadata:
  skill-type: team_automation
---

# Compound Engineering Router

## Table of Contents
- [Working agreement](#working-agreement)
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowerment principles](#empowerment-principles)
- [Prerequisites](#prerequisites)
- [Route map](#route-map)
- [Workflow](#workflow)
- [NotebookLM enrichment](#notebooklm-enrichment)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [Decision feedback protocol](#decision-feedback-protocol)

## Working agreement
- Keep `SKILL.md` as the map; keep durable detail in `references/` and `workflows/`.
- Treat `/Users/jamiecraik/dev/Agent-Skills` as the primary target repo for packaged CE skills. Use `/Users/jamiecraik/dev/config` only as a legacy compatibility source when the user explicitly wants the original prompt-pack mapping.
- Prefer the smallest route or meta-mode that fits.
- Keep scope tight: choose one route, or at most 2-3 focused candidates when ambiguity remains after one question.
- Route to existing packaged CE skills and configured agents instead of duplicating their instructions.
- Use NotebookLM only as optional evidence enrichment, not as a substitute for repo truth.

## Standards snapshot (March 2026)
- Prefer routing to the smallest safe workflow stage, not the most elaborate one.
- Verify prompt paths, agent role names, and config presence before recommending them.
- Make the handoff executable: one route, one rationale, one next step, and explicit safeguards.
- Treat context compaction and guardrail extraction as first-class operational modes, not fallback dumping grounds.
- For behavior-changing implementation lanes, prefer plans and work prompts that enforce TDD, tracer bullets, and public-interface validation rather than generic "write tests" advice.
- Default to one supervisor agent owning the task end-to-end; recommend specialist roles only as bounded internal support when they clearly reduce risk or cycle time.

## When to use
Use this skill when the user wants to enter or steer the compound-engineering workflow and needs help choosing the correct stage, review mode, or workflow-support meta-mode.

Primary triggers:
- "help me route this into the workflow"
- "should this be ideate/brainstorm/spec/plan/work/review?"
- "use the compound engineering workflow"
- "route this UI request with design and frontend agents"
- "do a technical review"
- "which prompt and agents should this use?"
- "I have a task, PR, spec, or review ask and want the right workflow entrypoint"
- "compact this context so the next run can continue cleanly"
- "turn this failure or lesson into a guardrail"

Non-triggers:
- direct feature implementation with clear scope and no routing need
- generic coding help unrelated to the compound workflow
- pure NotebookLM querying with no workflow-routing goal
- repo changes that only need one known specialized skill and no workflow selection

## Required inputs
- user request or artifact to route: idea, spec, plan, task, branch, PR, diff, postmortem, or review ask
- target repo context; default to `/Users/jamiecraik/dev/Agent-Skills`
- enough signal to choose one route safely; ask a single concise follow-up only if the route is ambiguous
- for `technical-review`, at least one of: file set, diff, PR, branch, stack, or focus area
- for `context-compaction` or `guardrail-extract`, the current state summary, failure note, or artifact set to compress or convert

## Deliverables
- a `schema_version: 1` route or meta-mode brief
- the exact packaged CE skill name and path when the selection is skill-backed
- the legacy prompt alias only when compatibility context is relevant
- the recommended background agents to fan out, using exact configured role names when relevant
- a compact execution brief with:
  - objective
  - route rationale
  - prompt path or explicit meta-mode name
  - agent fan-out
  - execution posture
  - safeguards and validation gates
  - TDD / tracer-bullet obligations when the selected route leads toward implementation
  - optional NotebookLM-derived heuristics
- a refusal or clarification when the request is outside scope or too ambiguous
- when relevant, a short "why not the nearby alternatives" note so the next run does not re-open the same routing debate

## Failure mode
If the request is out of scope, do not force a route. Say why, name the closest next step, and point to the better skill or direct execution path.

If the route is ambiguous after one concise question, stop and surface the smallest set of route candidates instead of guessing.

## Constraints
- Redact secrets, credentials, tokens, and sensitive data by default.
- Prefer read-only discovery before any mutating follow-up steps.
- Do not invent prompt names, role names, or NotebookLM conclusions.
- Treat NotebookLM as optional supporting evidence only.
- For meta-modes, explicitly say when there is no backing prompt file.

## Philosophy
- Route with the smallest sufficient decision.
- Keep prompts canonical and specialist roles exact.
- Prefer explicit safeguards and validation gates over vague recommendations.
- Turn repeated failure patterns into durable workflow improvements.
- Optimize for low operator load: Jamie should not need to manually coordinate multiple top-level agents for routine work.

Guiding questions:
- Is this really a stage-selection problem, or is it a meta-mode problem?
- What is the smallest route that keeps the user moving safely?
- Which exact specialist roles materially reduce risk here?
- Would NotebookLM evidence improve the decision, or just add noise?
- What should remain outside the skill so the prompt pack stays canonical?

## Variation and adaptation
- Vary depth by route type: short for obvious routing, deeper for review or compound asks.
- Adapt to artifact quality: rough ideas should bias toward brainstorm or spec, while mature artifacts should bias toward plan, work, or review.
- Use different review mixes for Rails, TypeScript, Python, frontend, security, data, and performance-heavy asks.
- When context is bloated, prefer `context-compaction` over forcing another route explanation.
- When a lesson should become reusable repo guidance, prefer `guardrail-extract` over ad hoc advice.
- Avoid cookie-cutter outputs; different starting states should produce meaningfully different route briefs.
- Prefer a single execution owner even when multiple specialist reviewers are recommended.

## Empowerment principles
- Empower the user with a clear next action, not just a label.
- Empower future runs by leaving behind compact, reusable route rationale.
- Empower reviewers by naming exact specialist roles and validation gates.
- Empower maintainers by converting recurring failures into prompt, agent, or instruction hardening recommendations.

## Prerequisites
Before routing:
1. confirm the target repo contains the packaged CE skills under `product/ops/`
2. confirm the target repo contains matching role configs when the route recommends specialist agents
3. confirm shell and tooling preflight for any repo inspection or validation work
4. if NotebookLM enrichment is requested or clearly helpful, use the canonical NotebookLM skill and its `run.py` wrapper

## Route map
See `workflows/route-selection.md` for the canonical route table and `workflows/meta-modes.md` for the support modes.

Packaged CE routes:
- `ideate` -> `product/ops/ce-ideate`
- `brainstorm` -> `product/ops/ce-brainstorm`
- `spec` -> `product/ops/ce-spec`
- `deepen-spec` -> `product/ops/ce-deepen-spec`
- `plan` -> `product/ops/ce-plan`
- `deepen-plan` -> `product/ops/ce-deepen-plan`
- `work` -> `product/ops/ce-work`
- `review` -> `product/ops/ce-review`
- `technical-review` -> `product/ops/ce-technical-review`
- `compound` -> `product/ops/ce-compound`
- `compound-refresh` -> `product/ops/ce-compound-refresh`

Meta-modes:
- `context-compaction` -> summarize state for a clean continuation; no backing prompt file
- `guardrail-extract` -> convert a resolved failure or lesson into a durable instruction/update recommendation; no backing prompt file

## Workflow
1. Read the user request and identify whether this is a routing problem, a review-selection problem, or a workflow-support meta-mode problem.
2. Resolve the smallest correct route using `workflows/route-selection.md` and `workflows/meta-modes.md`.
3. If a route is still ambiguous, ask one concise disambiguation question.
4. Build an execution brief using `references/contract.yaml` as the output contract.
5. For review routes, list the exact specialist agents that match the stack or risk areas.
6. For meta-modes, explicitly state that no backing prompt path applies.
7. Use NotebookLM enrichment only when it will materially improve the brief:
   - notebook 1 for spec and orchestration quality
   - notebook 2 for context injection, planning mode, hooks, and drift recovery
   - notebook 3 for Codex operating patterns, review loops, doc gardening, and eval patterns
8. End with the selected packaged skill path or meta-mode, route rationale, recommended agents, and validation gates.
9. For UI-first asks, route into `ce-spec` or `ce-plan` instead of a separate `ui-workflow` lane:
   - choose `ce-spec` when the UI contract, states, accessibility rules, or companion UI spec still need to be defined
   - choose `ce-plan` when the UI contract already exists and the next need is prototype-first sequencing, build order, validation, or rollout planning
10. When routing to `plan`, `deepen-plan`, or `work` for behavior-changing tasks, call out the expected TDD/tracer-bullet contract explicitly so later runs do not silently downgrade it.
11. If the route depends on a missing packaged skill or required repo asset, stop with a precise blocker instead of suggesting an imaginary path.
12. When recommending any agents beyond the main lane owner, state that they are internal bounded support and not peer operators Jamie is expected to coordinate manually.

UI route fan-out defaults:
- start with `ui-ux-design` for implementation-oriented UI planning and delivery
- add `design-implementation-reviewer` when visual parity or implementation fidelity is requested
- add `julik-frontend-races-reviewer` for async or motion-heavy UI interactions
- add `kieran-typescript-reviewer` when TypeScript-heavy UI code quality is a core risk

## NotebookLM enrichment
Use NotebookLM selectively; see `references/notebooklm-sources.md`.

Good uses:
- spec-writing heuristics
- agent orchestration or harness patterns
- context or window hygiene tactics
- deterministic review or remediation loop patterns
- compaction and guardrail-extraction heuristics

Do not use NotebookLM to override repo-local truth about:
- current prompt wording
- configured agent names
- current config values

## Validation
- verify the selected packaged route exists on disk before recommending it
- for technical-review and review, verify referenced agent names exist in `codex/config.toml` and on disk where feasible
- for meta-modes, verify that the output explicitly says no backing prompt file applies
- keep route reasoning explicit and short
- fail fast on missing packaged skill paths, missing legacy prompt files, or mismatched role names
- verify the route brief does not imply unnecessary multi-agent orchestration for routine work

## Anti-patterns
- do not collapse `technical-review` into generic `review`
- do not duplicate prompt bodies inside this skill
- do not spawn multiple parallel routes without explicit user approval
- do not use NotebookLM as a replacement for checking the repo
- do not over-ask; one route question maximum before choosing or surfacing candidates
- do not pretend a meta-mode has a prompt path when it does not
- do not leave the user with only a classification and no next action
- do not route behavior-changing work into plan or work without mentioning the TDD/tracer-bullet expectation
- do not equate "more agents" with a better route

## Examples
When the user asks things like:

Happy-path examples:
- "Can you route this rough feature idea into the right CE stage so we know whether to ideate, brainstorm, or spec it?"
- "Please point me at the right CE skill for a deep PR critique on this Rails branch."
- "Should this start with ideation first, or is it already ready for brainstorming?"
- "I have a rough plan draft. Help me decide whether it needs deepen-plan or is ready for work."
- "Route this task into the right CE stage and tell me which internal support agents are actually worth using."
- "We need to build a new screen. Should this go to `ce-spec` for the UI contract first, or is it already ready for `ce-plan`?"

Meta-mode examples:
- "Can you compact this thread so the next run can continue without losing the plan?"
- "Help me turn this repeated workflow failure into a durable guardrail recommendation."

Edge cases:
- "I need a review, but I only know it touches migrations and performance."
- "We already have a spec and plan. Should I go straight to work or do a technical review first?"

Negative controls:
- "Implement this feature now."
- "Just answer this NotebookLM question."

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[brainstorming]] | Start with brainstorming before routing to a compound workflow |
| [[ce-plan]] | Generate the implementation plan the compound mode targets |
| [[product-spec]] | Produce a spec before routing to the work or review mode |
| [[architecture-interview]] | Route architecture decisions through the structured interview |
| [[skill-builder]] | Build skills that compound workflows will invoke |

**Topic map:** [[product-strategy]]

<!-- decision-feedback-protocol:v2 -->
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 scripts/record_skill_feedback.py` when operating inside the skill-authoring environment.

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
