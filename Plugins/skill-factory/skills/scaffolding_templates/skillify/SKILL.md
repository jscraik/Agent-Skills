---
name: skillify
description: "WHAT: Convert repeatable Codex workflows into validated SKILL.md packages. WHEN: Use when a completed workflow is ready to become durable skill guidance."
metadata:
  skill-type: scaffolding_templates
---

# Skillify

Capture a completed Codex workflow as a reusable skill package with explicit triggers, inputs, outputs, validation, and failure boundaries.

## Philosophy

Preserve repeatable behavior, not one-off transcript noise. Generated skills should be clear, auditable, and runnable.

Package context only when the workflow has a path through generate, test, distribute, observe, and adapt.

## When To Use

- User asks to skillify, operationalize, or package a repeatable process.
- A workflow has repeated enough to justify durable skill guidance.
- Prior session or collector evidence should become a validated skill artifact.

## Required inputs

- Source workflow context: transcript, notes, commands, or session-collector evidence.
- Target audience, destination path, category, and success criteria.
- Any required scripts, templates, references, or eval cases.

## Workflow

1. Capture the source workflow and intended reuse scope.
2. Prefer bounded session-collector evidence over raw transcripts.
3. Extract stable triggers, prerequisites, inputs, deliverables, and safety boundaries.
4. Define how the new skill will be tested, distributed, observed, and adapted after future failures.
5. Draft `SKILL.md` from the repository template.
6. Add references, contract, evals, and task profile needed by governance gates.
7. Run structure and quality validation until clean.

Read when: choosing whether the requested factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).

For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

## Deliverables

Return the skill path, package files created or changed, context routes, findings, validations, and any missing inputs. Structured output should include `schema_version: 1`.

When source evidence comes from a transcript, PR review, or session bundle, summarize the reusable pattern and keep raw text in bounded evidence artifacts only.

## Safety

- Do not codify exploratory or contradictory workflows.
- Do not embed secrets, credentials, private user data, or raw transcripts.
- Keep the first pass to 2-3 focused surfaces unless the user asks for a broader package.
- Stop if destination, category, or source workflow context is insufficient.

Assets: `assets/icon.png` and `assets/icon-small.png`.

## Anti-Patterns

- Copying raw session transcripts directly into `SKILL.md`.
- Codifying exploratory or contradictory workflows.
- Treating template completion as success without validation.

## Examples

- "Skillify this release triage workflow into a reusable agent-ops skill."
- "Convert the successful PR cleanup session into a validated skill package."

## Failure mode

If the workflow is not repeatable, the destination is unclear, or required evidence is missing, stop and report the blocker before creating package files.

## Gotchas

- Do not turn one-off exploration into durable instructions.
- Do not package a workflow unless the observation source and adaptation owner are clear.
- Keep heavy examples, templates, and collector detail in references.

## Progressive Disclosure

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Skill template and intake detail: `Infrastructure/references/deferred-skill-context/skill-factory-skillify/references/`
- Archived full package: `Infrastructure/references/deferred-skill-context/skill-factory-skillify/`
- Context development lifecycle: `Plugins/skill-factory/references/context-development-lifecycle.md`

## Validation

Verify trigger text maps to realistic user language, required references exist, evals cover happy/edge/negative/pressure cases, and all repository structure checks pass. Fail fast: stop at the first failed gate and do not proceed until the blocker is fixed.
