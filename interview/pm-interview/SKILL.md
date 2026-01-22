---
name: pm-interview
description: "Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified."
metadata:
  short-description: "Product scope interview for value, metrics, and rollout."
---

# pm-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## What this wrapper optimizes for

- Minimal scope that proves value (MVP discipline)
- Measurable outcomes (primary metric + guardrail)
- Explicit non-goals
- Rollout and stakeholder tradeoffs

## Interaction notes

- Must use AskUserQuestion-style multiple choice (3–5 options, include a recommended default).
- In Delta mode (existing PRD/notes), do not re-ask settled decisions; fill gaps and force tradeoffs.

## User profile alignment (Jamie)

Follow `/Users/jamiecraik/.codex/USER_PROFILE.md`: single-threaded, explicit steps, low cognitive load. Keep one question per turn and map any free-text reply to the closest option with confirmation.

## Philosophy

- Product clarity beats feature volume. Focus on the smallest scope that proves value.

## Anti-patterns

- Expanding scope without a tradeoff or measurable outcome.
- Accepting “just one more” without cutting something else.
- Treating stakeholder requests as requirements without validation.
- Shipping without an explicit “out-of-scope” list.
- Letting roadmap items override core user value.

## Variation

- Tailor questions to the product surface and user segment; avoid generic prompts.
- Force the tradeoff that matches the current dominant risk (time, UX, tech debt, adoption).

## Empowerment

- Make tradeoffs explicit so stakeholders choose with full context.
- Provide a “defer to v2” path that records the decision and impact.
- Require stakeholders to pick what gets removed when scope expands.

## Default mode + intent

- Mode: `standard`
- Intent: start `DISCOVER`, then `DECIDE` for scope/tradeoffs

## When to use

- Defining product scope, value, and success metrics.
- Validating a roadmap item before committing engineering time.
- Forcing tradeoffs with stakeholders.

## Constraints / Safety

- Redact secrets/PII by default.
- Do not expand scope without removing something else.
- Do not proceed without an explicit out-of-scope list.

## PM spine (10 prompts)

Ask in order, skipping anything already answered by context.

1) **Target user / segment**
- Who is this for?

2) **Situation / trigger**
- When does the problem occur (what are they doing when this matters)?

3) **PAS: Problem (observable)**
- What is the observable problem?

4) **PAS: Amplify (cost of problem)**
- Options: time saved / revenue risk / churn / frustration / support load / compliance risk.

5) **Value hypothesis**
- What changes in user outcome if we succeed?

6) **Success metric**
- Pick one primary success metric + optionally one guardrail metric.

7) **Activation / distribution path**
- How will users discover/start using this? (in-product, docs, sales-led, ops process, other)

8) **Scope boundary (MVP one sentence)**
- Minimal version that delivers value.

9) **Non-goals**
- Name one thing we will NOT do in this iteration.

10) **Tradeoff + rollout posture (DECIDE)**
- Optimize for: fastest ship vs best UX polish vs most future-proof  
- Release: everyone immediately vs staged rollout vs behind a flag

## PM synthesis add-on (append after Kernel synthesis)

```md
## PRD-lite Addendum
- Target user:
- Job-to-be-done:
- Problem (observable):
- Value hypothesis:
- Primary metric:
- Guardrail metric (optional):
- Activation/distribution:
- Release strategy:
- Open questions for later:
```

## Inputs
- User request details and any relevant files/links.

## Outputs
- Kernel synthesis + PRD-lite Addendum.
- Include `schema_version: 1` if outputs are contract-bound.

## Validation
- Fail fast and report missing inputs before proceeding.

## Examples

- "Help me scope a new onboarding flow and define success metrics."
- "Pressure-test this roadmap item and force tradeoffs."

## References
- `references/contract.yaml` (output contract)
- `references/evals.yaml` (quality checks)

## Procedure
1) (Optional) Delta scan: extract what’s already decided.
2) Execute the kernel interview loop using the PM spine.
3) Synthesize outputs + approval gate.
4) Handoff to planning/execution using the approved PRD-lite.

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
