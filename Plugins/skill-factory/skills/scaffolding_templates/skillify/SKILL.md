---
name: skillify
description: Convert a completed Codex workflow into a reusable validated skill package. Use when the user asks to skillify or operationalize a repeatable process.
metadata:
  skill-type: scaffolding_templates
---

# Skillify

Convert a completed workflow into a reusable skill package with explicit invoke syntax.

Read when: intake and template details are needed: [skill template](./references/skill-template.md)

Interface asset: [skillify icon](./assets/icon.png)

## Philosophy

- Preserve repeatable behavior, not one-off execution details.
- Optimize for future operator clarity with minimal ambiguity.
- Keep generated skills auditable with explicit inputs, outputs, and validation.

## When to use

- Use when a workflow has been repeated enough to justify a reusable skill.
- Use when the user wants a conversation or run converted into durable `SKILL.md` guidance.

## Required inputs

- Source workflow context (session transcript, notes, or commands used).
- Target audience and success criteria for the new skill.
- Destination path and category for where the skill should live.
- Start with 2-3 focused surfaces; widen only after the reusable boundary is clear.

## Deliverables

- A complete skill package centered on `SKILL.md` with clear invoke syntax.
- Any required companion files referenced by the skill (scripts, templates, references).
- Validation notes covering contract and structure checks.
- Structured output with `schema_version`, `mode`, `skill_path`, `validations`, and `blocked_by` when blocked.

## Procedure

1. Capture the source workflow and confirm intended reuse scope.
2. Extract stable triggers, required inputs, deliverables, and failure boundaries.
3. Draft `SKILL.md` using the template and include explicit procedure/validation/constraints sections.
4. Add or update supporting references (contract/evals/task profile) needed for governance gates.
5. Run the relevant structure checks and iterate until clean.

Reference materials:
- [session-collector-intake](./references/session-collector-intake.md)
- [skill-template](./references/skill-template.md)

## Constraints

- Do not codify workflows that are still exploratory or contradictory.
- Do not embed repository secrets, credentials, or private user data in generated skill artifacts.
- Redact sensitive tokens, secret paths, and account identifiers from examples and references.
- Keep scope aligned to the requested category and destination.

## Validation

- Verify trigger text maps to realistic user language.
- Verify required sections and references exist and are internally consistent.
- Verify eval cases include happy, edge, and failure behavior.
- Fail fast: if source workflow context is insufficient, stop and report missing inputs.

## Anti-patterns

- Copying raw session transcripts directly into `SKILL.md`.
- Generating broad triggers that hijack unrelated tasks.
- Treating template completion as success without running validation gates.

## Failure mode

- If the workflow is too incomplete or inconsistent, stop and report what is missing.
- If required destination/category cannot be resolved, pause and request explicit routing.

## Gotchas

- Avoid overfitting to a single run; generalize only repeatable steps.
- Keep prerequisites explicit so the skill is runnable without hidden assumptions.

## Examples

- "Skillify this repeatable release triage process into a reusable lane under `agent-ops`."
- "Convert yesterday's plugin onboarding workflow into a validated skill package."
