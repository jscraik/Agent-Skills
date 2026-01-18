---
name: code-plan
description: "Turn a user prompt into a **single, actionable plan** delivered in the final assistant message.. Use when When a user explicitly asks for a plan or roadmap.."
---

# Create Plan

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Goal

Turn a user prompt into a **single, actionable plan** delivered in the final assistant message.

## Philosophy
- Optimize for clarity and execution, not exhaustive detail.
- Prefer assumptions with transparency over blocking on trivia.
- Keep plans testable and reversible.

## Guiding questions
- What is the smallest plan that achieves the user’s goal?
- Why is each step necessary and ordered this way?
- What risks or edge cases could derail the plan?
- How will success be verified?

## When to use
- When a user explicitly asks for a plan or roadmap.
- When a multi-step implementation needs scoped action items.
- When you need a concise, ordered checklist with validation.

## ExecPlan rule (for multi-hour work)
- If the task is multi-hour, high-risk, or explicitly references PLANS.md / ExecPlan, switch to ExecPlan mode.
- First, look for a repository PLANS.md (or .agent/PLANS.md) and follow it exactly.
- If no PLANS.md exists, ask whether to proceed using the bundled reference or to add PLANS.md first.

## Minimal workflow

Throughout the entire workflow, operate in read-only mode. Do not write or update files.

1. **Scan context quickly**
   - Read `README.md` and any obvious docs (`docs/`, `CONTRIBUTING.md`, `ARCHITECTURE.md`).
   - Skim relevant files (the ones most likely touched).
   - Identify constraints (language, frameworks, CI/test commands, deployment shape).

2. **Ask follow-ups only if blocking**
   - Ask **at most 1–2 questions**.
   - Only ask if you cannot responsibly plan without the answer; prefer multiple-choice.
   - If unsure but not blocked, make a reasonable assumption and proceed.

3. **Create a plan using the template below**
   - Start with **1 short paragraph** describing the intent and approach.
   - Clearly call out what is **in scope** and what is **not in scope** in short.
   - Then provide a **small checklist** of action items (default 6–10 items).
      - Each checklist item should be a concrete action and, when helpful, mention files/commands.
      - **Make items atomic and ordered**: discovery → changes → tests → rollout.
      - **Verb-first**: “Add…”, “Refactor…”, “Verify…”, “Ship…”.
   - Include at least one item for **tests/validation** and one for **edge cases/risk** when applicable.
   - If there are unknowns, include a tiny **Open questions** section (max 3).

4. **Do not preface the plan with meta explanations; output only the plan as per template**

## Variation rules
- Vary plan depth by task size (small: 4–6 items, large: 8–12).
- Vary validation steps by risk (unit tests vs full suite).
- Use a different structure when the user requests it explicitly.

## Empowerment principles
- Empower the user to accept or modify scope before execution.
- Empower reviewers with explicit validation steps.

## Anti-patterns to avoid
- Over-planning or creating multi-page plans for small tasks.
- Ordering steps out of dependency order.
- Omitting validation or rollback steps when risk exists.

## Plan template (follow exactly)

```markdown
# Plan

<1–3 sentences: what we’re doing, why, and the high-level approach.>

## Scope
- In:
- Out:

## Action items
[ ] <Step 1>
[ ] <Step 2>
[ ] <Step 3>
[ ] <Step 4>
[ ] <Step 5>
[ ] <Step 6>

## Open questions
- <Question 1>
- <Question 2>
- <Question 3>
```

## ExecPlan reference
- For ExecPlan structure and requirements, open `references/execplan.md`.

## Checklist item guidance
Good checklist items:
- Point to likely files/modules: src/..., app/..., services/...
- Name concrete validation: “Run npm test”, “Add unit tests for X”
- Include safe rollout when relevant: feature flag, migration plan, rollback note

Avoid:
- Vague steps (“handle backend”, “do auth”)
- Too many micro-steps
- Writing code snippets (keep the plan implementation-agnostic)

## Example prompts
- “Create a plan to refactor the authentication flow.”
- “Give me a plan to add a new settings screen.”
- “Outline steps to debug the failing CI pipeline.”

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Inputs
- User request details and any relevant files/links.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
