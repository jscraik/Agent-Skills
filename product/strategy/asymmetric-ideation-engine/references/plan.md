# Plan — Asymmetric Ideation Engine

## Objective
Create a skill that converts a broad "radical ideation" prompt into a repeatable, validated workflow with strict novelty constraints and launchability requirements.

## Category selection
- Chosen category: `product/strategy`
- Rationale: this skill is strategic discovery/ideation, not implementation automation.

## Build steps
1. Initialize new skill scaffold with codex target.
2. Define tight trigger boundary (radical ideation from repository context).
3. Encode workflow with hidden-audit + asymmetric ideation + constraint gate.
4. Define contract schema for required output structure and coverage constraints.
5. Add evals (happy, edge, negative, pressure) to enforce routing quality.
6. Validate with quick validators and fix any gate failures.

## Assumptions
- User wants this as a reusable invocation skill.
- Deliverables are markdown-first artifacts.
- Recurring 30-minute mode is optional and only when explicitly requested.

## Success criteria
- Skill validates cleanly.
- Description routes correctly and avoids near-miss triggers.
- Output contract enforces the six required sections per idea.
