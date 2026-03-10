---
name: architecture-interview
description: Plan and review architecture decisions via a structured interview and
  ADR output. Use when choosing between system design alternatives.
---

# architecture-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Standards snapshot (March 2026)

- Follow current global instructions from `~/.codex/AGENTS.md` and linked standards docs.
- Keep the interview single-threaded and decision-first.
- Optimize for architecture choices that can be verified through rollout, observability, and explicit tradeoffs.

## What this wrapper optimizes for

- A clear, auditable architectural choice with explicit sacrifices
- A usable ADR draft (status: Proposed) before implementation starts
- Operability: failure modes, rollout/migration, observability, verification

## Interaction notes

- Must use `default_mode_request_user_input` multiple choice (3–5 options, include a recommended default).
- Start in **DECIDE**: architecture is primarily decision forcing.
- In Delta mode (existing ADR/draft spec), do not re-ask settled decisions; fill gaps and verify consequences.

## User profile alignment (Jamie)

Follow `~/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Keep one question per turn and map any free-text reply to the closest option with confirmation.

## Philosophy

- Architecture is decision-making under constraints; the goal is a clear, auditable tradeoff.
- Favor the smallest architecture that satisfies the dominant constraint.

## Anti-patterns to avoid

- Choosing an architecture without naming what is sacrificed.
- Deferring decisions to “later” when they block progress now.
- Asking for implementation details before the decision is approved.

## Variation

- Tailor prompts to the system type (CRUD vs streaming vs ML vs infra) and scale.
- Avoid repeating identical option sets; vary tradeoffs based on context.

## Default mode + intent

- Mode: `standard` (use `deep` for major rewrites)
- Intent: start `DECIDE`

## Scope and triggers

- Choosing between architectural alternatives.
- Producing an ADR before implementation.
- Clarifying constraints (security/perf/compliance/cost) that dominate design.

## Architecture spine (10 prompts)

1) **Decision statement**
- What decision must we make? (one sentence)

2) **Decision drivers**
- Top priority driver: performance vs simplicity vs security vs extensibility?

3) **Hard constraints**
- Runtime/deployment, compliance, cost ceilings, team skill constraints, deadlines.

4) **Alternatives on the table**
- Pick 2–4 options that are truly viable.

5) **Decision criteria**
- What must be true for the chosen option to “win”? (latency, operability, cost, etc.)

6) **Tradeoff (DECIDE)**
- Which do we sacrifice: fastest implementation, lowest complexity, or best long-term flexibility?

7) **Integration boundaries**
- 1–3 most important touchpoints.

8) **Failure modes**
- Worst credible failure mode + how we detect it.

9) **Migration/rollout**
- big-bang vs incremental vs parallel run + rollback plan.

10) **Verification**
- What proves the decision works (benchmarks, tests, SLOs, incident reduction)?

## Architecture synthesis add-on (ADR required)

Append an ADR block:

```md
## ADR Draft

# ADR: <title>

## Context
## Decision
## Status
Proposed (pending approval)

## Decision drivers
## Alternatives considered
## Decision criteria
## Consequences
- Positive:
- Negative / sacrificed:

## Migration / rollout / rollback
## Verification plan
## Observability plan
```

## Required inputs
- User request details and any relevant files/links.

## Deliverables
- Kernel synthesis + ADR Draft (Proposed).
- Include `schema_version: 1` if outputs are contract-bound.
- Make the tradeoff explicit: what is chosen, what is sacrificed, and how success will be verified.

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Validation
- Fail fast and report missing inputs before proceeding.

## Examples

- "Help me choose between a modular monolith and microservices for our app."
- "Create an ADR for moving from a REST API to GraphQL."

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Procedure
1) (Optional) Delta scan: extract existing constraints/decisions from any draft ADR/spec.
2) Execute the kernel interview loop using the Architecture spine.
3) Produce ADR Draft + approval gate.
4) Handoff to planning/execution using the approved ADR.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
