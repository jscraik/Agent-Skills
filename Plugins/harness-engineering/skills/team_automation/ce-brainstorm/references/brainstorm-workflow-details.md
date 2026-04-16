# Brainstorm Workflow Details

Read when: you need the fuller scope rubric or product pressure-test prompts while running `ce-brainstorm`.

## Scope rubric

- `lightweight`: small, well-bounded, low ambiguity
- `standard`: normal feature or bounded refactor with some decisions to make
- `deep`: cross-cutting, strategic, or highly ambiguous

If scope is unclear, ask one targeted question to disambiguate and then continue.

## Product pressure test prompts

Use the lightest set that gives a trustworthy recommendation.

`lightweight`:
- Is this solving the real user problem?
- Are we duplicating something that already covers this?
- Is there a clearly better framing with near-zero extra cost?

`standard`:
- Is this the right problem, or a proxy for a more important one?
- What user or business outcome actually matters here?
- What happens if we do nothing?
- Is there a nearby framing that creates more user value without more carrying cost?
- Given the current project state, user goal, and constraints, what is the highest-leverage move right now: the request as framed, a reframing, one adjacent addition, a simplification, or doing nothing?

`deep`:
- ask the standard questions
- add: what durable capability should this create in 6-12 months?
- add: does this move the product toward that, or is it only a local patch?

Use these prompts to sharpen the conversation, not to bulldoze user intent.

## Approach card format

For each approach in Phase 2, include:
- brief description (2-3 sentences)
- pros and cons
- key risks or unknowns
- when it is best suited

Present all approaches first, then recommendation, to avoid early anchoring.
Use at least one non-obvious angle when helpful (inversion, constraint removal, analogy).

## Closeout templates

Completion closeout:
- `Brainstorm complete!`
- requirements path under `docs/brainstorms/` (when one exists)
- chosen `spec_required`, `risk_level`, `complexity`
- recommended next workflow stage

Pause closeout:
- `Brainstorm paused.`
- requirements path and remaining blockers (when they exist)
- instruction to resume `ce-brainstorm` before planning

## Validation checklist

Run fail-fast validation before completion:
- verify task-domain classification happened before deeper brainstorm phases
- verify brainstorming is actually the right stage
- verify recommendation includes `spec_required`, `risk_level`, `complexity`
- verify requirements artifact path for new docs
- verify legacy brainstorm docs are resumed intentionally
- verify requirements are concrete enough that planning will not invent behavior
- verify multiple plausible approaches were shown before recommendation when the option space was open
- verify handoff recommendation matches risk, complexity, and blocker state
- verify research roles are named exactly when subagent support is recommended
- report exact failures and the smallest safe fix
