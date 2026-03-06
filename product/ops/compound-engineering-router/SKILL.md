---
name: compound-engineering-router
description: "Route Codex compound-engineering requests to the correct workflow prompt or meta-mode in the config repo, with optional NotebookLM evidence for spec quality, agent orchestration, and Codex operating patterns. Use when a user wants brainstorm, spec, plan, work, review, technical review, compound workflow guidance, context compaction, or guardrail extraction rather than direct feature coding."
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
- Treat `/Users/jamiecraik/dev/config` as the canonical target repo for this skill unless the user explicitly says the same prompt pack has been installed elsewhere.
- Prefer the smallest route or meta-mode that fits.
- Route to existing prompts and configured agents instead of duplicating their instructions.
- Use NotebookLM only as optional evidence enrichment, not as a substitute for repo truth.

## Scope and triggers
Use this skill when the user wants to enter or steer the compound-engineering workflow and needs help choosing the correct stage, review mode, or workflow-support meta-mode.

Primary triggers:
- "help me route this into the workflow"
- "should this be brainstorm/spec/plan/work/review?"
- "use the compound engineering workflow"
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
- target repo context; default to `/Users/jamiecraik/dev/config`
- enough signal to choose one route safely; ask a single concise follow-up only if the route is ambiguous
- for `technical-review`, at least one of: file set, diff, PR, branch, stack, or focus area
- for `context-compaction` or `guardrail-extract`, the current state summary, failure note, or artifact set to compress or convert

## Deliverables
- a `schema_version: 1` route or meta-mode brief
- the exact prompt file under `codex/prompts/` when the selection is prompt-backed
- the recommended background agents to fan out, using exact configured role names when relevant
- a compact execution brief with:
  - objective
  - route rationale
  - prompt path or explicit meta-mode name
  - agent fan-out
  - safeguards and validation gates
  - optional NotebookLM-derived heuristics
- a refusal or clarification when the request is outside scope or too ambiguous

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

## Empowerment principles
- Empower the user with a clear next action, not just a label.
- Empower future runs by leaving behind compact, reusable route rationale.
- Empower reviewers by naming exact specialist roles and validation gates.
- Empower maintainers by converting recurring failures into prompt, agent, or instruction hardening recommendations.

## Prerequisites
Before routing:
1. confirm the target repo contains the prompt pack under `codex/prompts/`
2. confirm the target repo contains matching role configs under `codex/agents/` and `codex/config.toml`
3. confirm shell and tooling preflight for any repo inspection or validation work
4. if NotebookLM enrichment is requested or clearly helpful, use the canonical NotebookLM skill and its `run.py` wrapper

## Route map
See `workflows/route-selection.md` for the canonical route table and `workflows/meta-modes.md` for the support modes.

Prompt-backed routes:
- `brainstorm` -> `codex/prompts/workflow-brainstorm.md`
- `spec` -> `codex/prompts/workflow-spec.md`
- `deepen-spec` -> `codex/prompts/deepen-spec.md`
- `plan` -> `codex/prompts/workflow-plan.md`
- `deepen-plan` -> `codex/prompts/deepen-plan.md`
- `work` -> `codex/prompts/workflow-work.md`
- `review` -> `codex/prompts/workflow-review.md`
- `technical-review` -> `codex/prompts/technical_review.md`
- `compound` -> `codex/prompts/workflow-compound.md`

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
8. End with the selected prompt path or meta-mode, route rationale, recommended agents, and validation gates.

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
- verify the selected route exists on disk before recommending it
- for technical-review and review, verify referenced agent names exist in `codex/config.toml` and on disk where feasible
- for meta-modes, verify that the output explicitly says no backing prompt file applies
- keep route reasoning explicit and short
- fail fast on missing prompt files or mismatched role names

## Anti-patterns
- do not collapse `technical-review` into generic `review`
- do not duplicate prompt bodies inside this skill
- do not spawn multiple parallel routes without explicit user approval
- do not use NotebookLM as a replacement for checking the repo
- do not over-ask; one route question maximum before choosing or surfacing candidates
- do not pretend a meta-mode has a prompt path when it does not
- do not leave the user with only a classification and no next action

## Examples
Happy-path examples:
- "Use the compound engineering workflow to turn this idea into a spec."
- "Which prompt should I use for a deep PR critique on this Rails branch?"
- "I have a rough plan; should this go to deepen-plan or work?"
- "Route this task into the right stage and tell me which agents should fan out."

Meta-mode examples:
- "Compact this thread so the next run can continue without losing the plan."
- "Turn this repeated failure into a durable guardrail recommendation."

Edge cases:
- "I need a review, but I only know it touches migrations and performance."
- "We already have a spec and plan. Should I go straight to work or do a technical review first?"

Negative controls:
- "Implement this feature now."
- "Just answer this NotebookLM question."

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
- For non-trivial outcomes, collect user feedback via AskQuestion parity before closing the run.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 scripts/record_skill_feedback.py` when operating inside the skill-authoring environment.
