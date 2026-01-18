---
name: pm-interview
description: "Plan and review product scope, value, metrics, and rollout via a structured interview. Use when product direction or scope must be clarified."
---

# pm-interview (wrapper)

Use **Interview Kernel** rules, state model, synthesis, and approval gate.
Kernel-enforced: Question validity gate, DISCOVER vs DECIDE intent switch, Decisions table, and Assumptions register + approval.

## Philosophy
- Product clarity beats feature volume. Focus on the smallest scope that proves value.

## Anti-patterns
- Expanding scope without a tradeoff or measurable outcome.
- Accepting “just one more” without cutting something else.
- Treating stakeholder requests as requirements without validation.
- Shipping without an explicit “out-of-scope” list.
- Letting roadmap items override core user value.
- Anti-pattern: framing scope as additive without a compensating cut.

## Variation
- Tailor questions to the product surface and user segment; avoid generic prompts.
- Vary which tradeoff is forced first based on current risk (time, UX, tech debt).

## Empowerment
- Make tradeoffs explicit so stakeholders choose with full context.
- Provide a “defer to v2” path that records the decision and impact.
- Require stakeholders to pick what gets removed when scope expands.
- Empower stakeholders to say “no” with a documented rationale.

## Default mode + intent

* Mode: `standard`
* Intent: start `DISCOVER`, then `DECIDE` for scope/tradeoffs

## When to use

- Use when defining product scope, value, and success metrics.
- Use when a roadmap item needs validation before committing.
- Use when stakeholders want more features without tradeoffs.

## Constraints / Safety
- Redact secrets/PII by default.

- Do not expand scope without removing something else.
- Do not proceed without an explicit out-of-scope list.

## Example prompts

- "We have too many ideas — help me pick an MVP."
- "Stakeholders want more features. Can you force tradeoffs?"
- "I need a PRD-lite before we commit."

## PM spine (8 prompts)

1. **User + context**

* “Who is the primary user (or segment) for this, and what are they doing when this matters?”

2. **PAS: Amplify**

* “What’s the cost of the problem (time, money, churn, frustration)? Pick one.”

3. **Value hypothesis**

* “What changes in user behavior/outcome if we succeed?”

4. **Success metric**

* “Pick one primary success metric (and optionally one guardrail).”

5. **Scope boundary**

* “What’s the minimal version that delivers the value? (One sentence.)”

6. **Non-goals**

* “Name one thing we will NOT do in this iteration.”

7. **Tradeoff (DECIDE)**

* “Optimize for: fastest ship, best UX polish, or most future-proof?”

8. **Rollout posture**

* “Release strategy: everyone immediately vs staged rollout vs behind a flag?”

## PM synthesis add-on (append after Kernel synthesis)

```md
## PRD-lite Addendum
- Target user:
- Job-to-be-done:
- Primary metric:
- Guardrail metric (optional):
- Release strategy:
- Open questions for later:
```

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
