---
name: skillify
description: Capture a completed Codex workflow as a reusable SKILL.md package by analyzing session context plus optional session-collector evidence, interviewing the user with structured prompts, and writing a validated skill artifact. Use when the user asks to skillify or operationalize a repeatable process.
metadata:
  skill-type: scaffolding_templates
---

# Skillify

Convert a completed workflow into a reusable skill package with explicit invoke syntax.

Read when: intake and template details are needed: [skill template](./references/skill-template.md)

## When to use

- Use when a workflow has been repeated enough to justify a reusable skill.
- Use when the user wants a conversation or run converted into durable `SKILL.md` guidance.

## Required inputs

- Source workflow context (session transcript, notes, or commands used).
- Target audience and success criteria for the new skill.
- Destination path and category for where the skill should live.

## Deliverables

- A complete skill package centered on `SKILL.md` with clear invoke syntax.
- Any required companion files referenced by the skill (scripts, templates, references).
- Validation notes covering contract and structure checks.

## Failure mode

- If the workflow is too incomplete or inconsistent, stop and report what is missing.
- If required destination/category cannot be resolved, pause and request explicit routing.

## Gotchas

- Avoid overfitting to a single run; generalize only repeatable steps.
- Keep prerequisites explicit so the skill is runnable without hidden assumptions.
