---
name: brainstorming
description: Clarify ambiguous product or implementation directions by comparing a few viable approaches and recommending one. Use when the user wants general brainstorming before planning or building, not the compound-engineering stage artifact.
metadata:
  skill-type: team_automation
---

# Brainstorming

Use this skill to clarify what to build before committing to how to build it in the general, non-CE case.

## Table of Contents
- [When to use](#when-to-use)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Core process](#core-process)
- [Optional visual companion](#optional-visual-companion)
- [YAGNI principles](#yagni-principles)
- [Incremental validation](#incremental-validation)
- [Anti-patterns](#anti-patterns)
- [Integration with planning](#integration-with-planning)
- [References](#references)
- [Examples](#examples)
- [Variation](#variation)
- [Remember](#remember)
- [Decision feedback protocol](#decision-feedback-protocol)

## When to use

Use brainstorming when:
- requirements are unclear or ambiguous
- multiple approaches could solve the problem
- trade-offs need exploration with the user
- the user has not fully articulated what they want
- feature scope needs refinement before planning

Skip brainstorming when:
- requirements are explicit and detailed
- the user already knows exactly what they want
- the task is a straightforward bug fix or tightly defined change

## Standards snapshot (March 2026)
- Keep brainstorming focused on intent, scope, and trade-offs rather than premature implementation detail.
- Ask one focused question at a time when clarification is needed.
- Prefer small decision-oriented summaries over long ideation dumps.
- End with a recommended direction or a clear handoff into planning.
- Decompose oversized projects before refining low-level details.
- Use visual aids only when the user would understand the choice better by seeing it than reading it.

## Required inputs

- user request or draft idea that needs clarification before planning
- relevant constraints already known: timeline, platform, dependencies, scope
- optional existing artifacts: PRD, ticket, screenshots, prior brainstorm notes

## Deliverables

- a concise decision-oriented brainstorm summary
- 2-3 approaches with trade-offs
- a recommended direction
- open questions that must be settled before planning
- a handoff artifact at `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md` when asked
- when a structured status report is requested, include a `schema_version` field

## Failure mode

If the request is already clear enough for planning or implementation, say so directly, explain why brainstorming is not needed, and recommend moving to planning instead of forcing an ideation loop.

## Constraints

- keep questions incremental, one focused question at a time when clarification is needed
- prioritize clarity of intent over implementation details
- redact secrets and sensitive data by default in summaries, examples, and notes
- avoid inventing requirements; explicitly label assumptions
- prefer recommendation-first output over endless ideation branches

## Core process

### Phase 0: Assess requirement clarity

Before asking questions, assess whether brainstorming is actually needed.

Signals that requirements are clear:
- the user provided specific acceptance criteria
- the user referenced existing patterns to follow
- the user described exact expected behavior
- scope is constrained and well-defined

Signals that brainstorming is needed:
- the user used vague terms like "make it better" or "add something like"
- multiple reasonable interpretations exist
- trade-offs have not been discussed
- the user seems unsure about the approach

If requirements are already clear, say: "Your requirements seem clear. Consider proceeding directly to planning or implementation."

### Phase 1: Understand the idea

Ask questions one at a time to understand intent without overwhelming the user.

Question techniques:

1. Prefer multiple choice when natural options exist.
2. Start broad, then narrow.
3. Validate assumptions explicitly.
4. Ask about success criteria early.

Key topics to explore:

| Topic | Example questions |
|---|---|
| Purpose | What problem does this solve? What is the motivation? |
| Users | Who uses this? What is their context? |
| Constraints | Any technical limitations, timeline, or dependencies? |
| Success | How will you know this is working well? |
| Edge cases | What should not happen? Any failure states to consider? |
| Existing patterns | Are there similar features in the codebase to follow? |

If the request describes multiple loosely-coupled subsystems, pause and decompose before refining details. Examples:
- "Build a platform with chat, billing, file storage, and analytics."
- "Redesign onboarding, notifications, permissions, and reporting."

For oversized requests:
- identify the independent workstreams
- recommend the smallest valuable first slice
- brainstorm that first slice instead of forcing one giant design

Exit when the idea is clear or the user says to proceed.

### Phase 2: Explore approaches

After understanding the idea, propose 2-3 concrete approaches.

For each approach, include:
- short description
- pros
- cons
- best-fit circumstances

Lead with a recommendation and explain why. Be honest about trade-offs and prefer simpler, proven paths unless the problem clearly needs more.

### Phase 3: Capture the design

Summarize key decisions in a compact structure:

```md
# <Topic Title>

## What We're Building

## Why This Approach

## Key Decisions
- Decision: rationale

## Open Questions

## Next Steps
```

Default output location when requested:
- `docs/brainstorms/YYYY-MM-DD-<topic>-brainstorm.md`

For larger or riskier work, expand the design summary to explicitly cover:
- architecture and boundaries
- key components or actors
- data flow and state transitions
- failure handling and fallback behavior
- testing or validation expectations

When the brainstorm is substantial enough to write down, prefer a lightweight spec note rather than a mandatory formal process. Suggested structure:

```md
# <Topic Title>

## What We're Building

## Why This Direction

## Architecture

## Components

## Data Flow

## Failure Handling

## Testing Notes

## Open Questions

## Next Steps
```

### Phase 4: Handoff

Present clear next options:

1. Proceed to planning.
2. Refine further.
3. Stop here and return later.

When the design is approved:
- use `[[ce-plan]]` for implementation sequencing
- use `[[product-spec]]` if the user wants a fuller implementation-ready spec
- use `[[architecture-interview]]` if the brainstorm surfaced a significant architecture choice that needs deeper review

## Optional visual companion

Use an optional visual companion only when the topic is genuinely visual and the browser will reduce ambiguity faster than text alone.

Good fits:
- wireframes or layout comparisons
- architecture diagrams
- side-by-side visual directions
- flows that are easier to understand spatially than verbally

Keep the discussion in the terminal for:
- scope clarification
- conceptual trade-offs
- requirements and acceptance criteria
- text-first option comparison

Offer it as an opt-in aid, not a default step. If accepted, use the guidance in `Infrastructure/references/visual-companion.md`.

## YAGNI principles

- do not design for hypothetical future requirements
- choose the simplest approach that solves the stated problem
- prefer boring, proven patterns over clever ones
- ask "Do we really need this?" when complexity appears
- defer decisions that do not need to be made now

## Incremental validation

Keep outputs compact. After each section of substantive output, validate direction with short checks like:
- "Does this match what you had in mind?"
- "Any adjustments before we continue?"
- "Is this the direction you want to go?"

## Anti-patterns

- asking too many questions at once
- jumping to implementation details too early
- proposing overly complex solutions for unclear problems
- refining details before checking whether the request should be decomposed
- ignoring existing codebase or product patterns
- making assumptions without validating them
- using visual artifacts for text-only decisions
- producing long design documents when a short decision summary would do

## Integration with planning

Brainstorming answers what to build:
- requirements and acceptance criteria
- chosen direction and rationale
- key decisions and trade-offs

Planning answers how to build it:
- implementation steps and file changes
- technical details and code patterns
- testing and verification strategy

When brainstorm output exists, planning should use it as input instead of redoing clarification.

## References
- Contract: `Infrastructure/references/contract.yaml`
- Evals: `Infrastructure/references/evals.yaml`
- Visual companion: `Infrastructure/references/visual-companion.md`

## Examples
- "Let's brainstorm the onboarding flow before we build it."
- "Help me think through options for the dashboard redesign."
- "Explore approaches for adding collaboration to this feature."

## Variation
- adapt question depth to request clarity and user confidence
- offer different framing styles such as user-journey, systems, or constraints-first
- avoid reusing identical approach sets across unrelated brainstorming sessions

## Remember
Good brainstorming reduces ambiguity. If it is not narrowing the decision space, it is not doing its job.

## See Also

| Skill | When to use together |
|---|---|
| [[interview-me]] | Use when the idea needs deeper requirements discovery beyond a quick brainstorm |
| [[product-spec]] | Hand off the chosen direction to this skill to produce implementation-ready specs |
| [[ce-plan]] | After spec is agreed, use to turn it into a sequenced execution plan |
| [[architecture-interview]] | When the brainstorm reveals a significant architecture decision needing structured review |

**Topic map:** [[product-strategy]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
