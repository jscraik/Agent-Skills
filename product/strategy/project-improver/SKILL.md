---
name: project-improver
description: Analyze an existing project and propose or implement high-leverage improvements with strong product judgment. Use when the user wants grounded improvement opportunities ranked and refined, not a single-feature spec.
metadata:
  skill-type: team_automation
---

# Project Improver

Use this skill when the user wants genuinely strong ideas for improving an existing project, not generic brainstorming: generate many candidate improvements, filter them hard, pressure-test the plan, and implement the best practical upgrades when asked.

Grounding rule:
- if the target is a live project or repo, inspect the current codebase and adjacent docs before proposing major improvements
- if the target is a plan or spec for a live project, inspect that artifact first and then check the current codebase before recommending major changes or implementation
- do not rely on abstract ideation alone when current repository evidence is available

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Core principles](#core-principles)
- [Workflow](#workflow)
- [Evaluation rubric](#evaluation-rubric)
- [Implementation policy](#implementation-policy)
- [Output structure](#output-structure)
- [Constraints](#constraints)
- [Examples](#examples)
- [Resources](#resources)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use

Use this skill when the user asks for any of the following:
- improve this project, product, repo, app, workflow, or system
- come up with the best ideas for making something more useful, compelling, intuitive, reliable, or powerful
- generate many candidate improvements, then shortlist only the best ones
- critically review or reject weak ideas instead of cheerleading them
- compare your plan with competing LLM plans and produce a better hybrid
- run a premortem on an improvement plan and revise it for likely failure modes
- say what you actually think about whether the project is good, useful, pragmatic, or well designed
- implement the top improvements now

Do not use this skill for:
- straightforward bug fixes with already-known solutions
- narrow implementation tasks that do not require product judgment
- generic brainstorming where 2-3 options are enough
- pure architecture review with no improvement prioritization

## Required inputs

- the project or artifact to improve: repo, doc, spec, product surface, or code path
- the improvement goal if known: growth, usefulness, UX, agent ergonomics, reliability, maintainability, differentiation, or speed
- constraints when available: time, scope, team size, tech stack, risk tolerance
- any comparison material if provided: competitor plans, prior proposals, external reviews, user complaints, metrics

Reasonable defaults:
- assume the user wants practical, high-leverage improvements rather than moonshots
- assume complexity cost matters and weak ideas should be rejected
- assume implementation should favor the top 1-3 ideas, not everything

## Deliverables

Produce the smallest set that fits the request:
- a candid assessment of the project's strengths, weaknesses, and opportunity surface
- 30 visible brief ideas when broad ideation is requested
- up to 100 internal candidates when the user wants only the very best shortlist
- explicit keep/reject reasoning and a final shortlist, usually 5-10 ideas
- for each kept idea: concrete plan, upside, downsides, and confidence percentage
- a premortem, hybrid revision, or git-diff plan update when the request calls for it
- direct implementation of the top ideas when the user explicitly asks to implement now

## Failure mode

If the request is too vague to evaluate a real project, say so directly and ask for the smallest missing anchor:
- repo or path
- spec or plan file
- screenshots or workflow
- pasted competing plans

If the task is really a bug fix or narrowly scoped implementation task, say that this skill is overkill and recommend direct implementation instead.

## Standards snapshot (March 2026)

- Optimize for real-world usefulness, not idea volume alone.
- Generate many candidates, but be ruthless about rejection.
- Prefer durable leverage: clearer flows, better defaults, stronger observability, safer automation, faster onboarding, tighter contracts.
- Do not hide uncertainty; explain why an idea may fail.

## Core principles

### 1. Ideas are cheap; filtering is the product
The value of this skill is not merely generating ideas. The value is generating many candidates, then rejecting weak ones with honest reasoning.

### 2. Prefer practical brilliance over speculative novelty
Favor ideas that feel unusually strong yet remain implementable without turning the project into a science fair.

### 3. Improve the whole system
Look across user experience, agent experience, product positioning, architecture, reliability, defaults, onboarding, and feedback loops.

### 4. Be intellectually honest
If the project is confusing, weakly differentiated, overbuilt, underpowered, or not yet a strong idea, say so plainly and constructively.

## Workflow

### Phase 0: Baseline understanding

Build a grounded view before ideating:
- what the project is
- who it serves
- what problem it solves
- current strengths worth preserving
- current friction, ambiguity, or underperformance

Evidence source order:
- for `project` or `repo` improvement: current codebase, current docs, current workflows, then prior plans
- for `plan` improvement tied to a live repo: referenced plan first, then current codebase and docs
- for pasted standalone plans with no repo context: improve the plan directly and label repo-specific assumptions

If the user asks for your actual opinion, include a clear direct take before or alongside ideation.

### Phase 1: Candidate generation

Start broad. Generate a wide candidate set across killer features, UX simplifications, agent-native workflows, onboarding, trust and safety, reliability, collaboration, integrations, automation, observability, packaging, and differentiation.

Default generation behavior:
- produce 30 visible one-line ideas when the user asks for a broad list
- if the user asks for the very best ideas, silently expand to up to 100 internal candidates before ranking

IMPORTANT: do not treat the first plausible ideas as the finalists, and do not let different projects converge on the same favorite patterns unless the requirements are actually identical.

### Phase 2: Systematic filtering

Evaluate every candidate against the rubric in `references/improvement-rubric.md`.

Hard-reject ideas that:
- add major complexity for small gain
- duplicate existing capabilities without meaningful differentiation
- are too expensive relative to expected value
- are exciting in theory but weak in actual user pull
- require speculative dependencies or unrealistic integrations
- worsen clarity, reliability, or maintainability

The rejection pass should be explicit. Name the weak idea and say why it did not survive.

### Phase 3: Shortlist the best ideas

Keep only ideas that survive critical review. For each kept idea, provide:
- title
- problem it solves
- concrete action plan
- why it is a strong improvement
- possible downsides or failure modes
- confidence from 0-100 percent

When useful, sort kept ideas by:
- `quick win`
- `high leverage`
- `strategic bet`

Encourage variation:
- adapt the shortlist to the specific project rather than forcing the same ten ideas every time
- consider different mixes for different maturity levels, user types, and technical constraints
- no two improvement plans should be identical unless the project realities are identical

### Phase 4: Hybrid revision mode

When competing plans or other model outputs are provided:
- analyze them with an open mind
- say which parts are genuinely better than your current plan
- preserve good ideas regardless of origin
- revise your plan into a better hybrid

When the user asks to update an existing plan, produce diff-style edits against the original plan rather than rewriting blindly.

### Phase 5: Premortem

If requested, or if the plan is ambitious enough to justify it, imagine the effort failed six months later. Ask:
- what assumptions were false
- which edge cases were missed
- what users hated
- which integration or rollout issues were overlooked
- what made the system harder, not better

Then revise the plan to reduce the most plausible failure modes.

### Phase 6: Implementation

If the user asks to implement now:
- choose the top 1-3 ideas with the best impact-to-complexity ratio
- prefer concrete wins over sprawling roadmaps
- explain why these are the first ideas to ship
- implement them directly
- note which strong ideas were deferred and why

Do not attempt to implement every shortlisted idea in one pass unless the user explicitly asks for a broad sweep.

## Evaluation rubric

Use the detailed rubric in `references/improvement-rubric.md` and score ideas on user value, agent value, differentiation, implementation cost, complexity burden, reliability impact, adoption likelihood, reversibility, and evidence fit.

## Implementation policy

When coding is in scope:
- keep the repo's current patterns unless a change is part of the improvement
- preserve working behavior unless the improvement intentionally changes it
- choose improvements that can be explained and defended with evidence
- prefer staged rollout when risk is non-trivial
- before implementing a shortlisted idea, verify that it still fits the actual repository structure, dependencies, and constraints

## Output structure

Adapt to the request, but this structure is the default for non-trivial runs:

```md
## Honest assessment

## 30 candidate ideas

## Rejected ideas

## Final shortlist

## Detailed plans for kept ideas

## Premortem

## Revised plan

## Ideas to implement now
```

If the user specifically asks for a git-diff style revision, render the plan update as a patch against the earlier plan.

When you emit a structured artifact, include `schema_version: 1.0`.

## Constraints

- do not confuse idea count with quality
- do not keep weak ideas to pad the shortlist
- avoid giant speculative platform bets unless the user explicitly wants them
- label assumptions clearly
- stay candid and specific; avoid generic praise
- when implementation is requested, favor practical wins that materially improve the project now
- redact secrets, tokens, credentials, personal data, and other sensitive material by default in summaries, examples, and improvement plans

## Validation

Fail fast:
- if the target is a live project and you have not inspected the current codebase or adjacent docs yet, stop before making major recommendations
- if the target is a live-project plan and the recommendations have not been checked against the current repository shape, stop before implementation
- if a proposed improvement depends on unsupported infrastructure, missing data, or unclear ownership, label it as an assumption or reject it

Quality checks:
- verify that each kept idea clearly beats its complexity cost
- verify that rejected ideas have explicit reasons rather than silent omission
- verify that implementation recommendations still fit the actual repository structure and dependencies
- verify that the final shortlist favors practical leverage over novelty theater

## Anti-patterns

- treating flashy ideas as automatically strong
- keeping weak ideas just to reach a round number
- proposing major repo changes without checking the current codebase
- improving a live plan in abstraction while ignoring real implementation constraints
- recommending features that users are unlikely to adopt
- letting premortem concerns become generic fear instead of concrete plan revisions
- template trap: reusing the same improvement playbook regardless of context
- context blindness: ignoring the actual architecture, team capacity, or user workflow
- over-specification: turning a strong idea into an overbuilt roadmap before evidence justifies it

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential; they do not constrain it.
Use judgment, adapt to context, and push for the strongest practical improvements instead of the safest generic ones.

## Examples

- "Use project-improver on this repo and give me 30 ideas, then keep only the strongest."
- "Think of 100 improvements internally and tell me your top 10 best ones."
- "Read competing plans, then revise your plan into a better hybrid."
- "Tell me what you actually think of this project, then implement the best improvements now."

## Resources

- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Rubric: `references/improvement-rubric.md`

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[product-spec]] | Produce a revised spec after high-leverage improvements are identified |
| [[brainstorming]] | Brainstorm improvement ideas before running the improver |
| [[architecture-interview]] | Validate architectural improvements via structured interview |
| [[ce-plan]] | Convert approved improvements into an execution-ready plan |
| [[security-threat-model]] | Include security improvements in the improvement scope |

**Topic map:** [[product-strategy]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
