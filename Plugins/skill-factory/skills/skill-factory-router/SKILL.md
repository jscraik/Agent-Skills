---
name: skill-factory-router
description: Route skill lifecycle requests to a Skill Factory lane. Use when users ask to create, harden, install, audit, or skillify skills.
metadata:
  skill-type: team_automation
---

# Skill Factory Router

Route skill lifecycle requests to one primary lane before execution.

## When To Use

- Use when the user asks to create, harden, audit, install, or skillify a Codex skill.
- Use when lane choice is not already explicit.

## Philosophy

- Choose the narrowest safe lane.
- Route first, execute second.
- Return deterministic, actionable handoff steps.

## Inputs

- User request text.
- Optional paths or source URLs.
- Current repo context.

## Outputs

- Selected lane: `skill-creator`, `skill-builder`, `skill-refactor`, `skill-installer`, or `skillify`.
- One-sentence rationale.
- Immediate next command or step.

## Procedure

1. Classify request intent: create, harden, analyze, install, or skillify.
2. Select exactly one primary lane.
3. Return lane + rationale + next step.
4. If ambiguity is material, request clarification.

## Deterministic Decision Order

1. Explicit lane names (`skill-creator`, `skill-builder`, `skill-installer`, `skill-refactor`, `skillify`) win unless multiple lanes are named; multiple named lanes stay with this router.
2. Create, author, update, or reshape a draft skill package -> `skill-creator`.
3. Capture, operationalize, or convert a completed workflow/session into a reusable skill -> `skillify`.
4. Harden, audit, validate, benchmark, gate, or fix warnings on an existing skill -> `skill-builder`.
5. Install, list, import, or verify runtime visibility for external/curated skills -> `skill-installer`.
6. Analyze skill reliability, failures, coverage gaps, merge/prune/retire options, or portfolio improvement evidence -> `skill-refactor`.

## Validation

- Fail fast: if routing uncertainty could cause wrong or unsafe actions, stop and ask.
- Confirm lane matches user outcome.
- Ensure the next step is executable in-repo.

## Constraints

- Map requests strictly to lane purpose.
- Do not execute unrelated coding work from this router.
- Redact secrets, tokens, credentials, and sensitive data.

## anti-patterns

- Do not pick multiple primary lanes.
- Do not send install/distribution work to authoring lanes.
- Do not route ordinary coding/debug tasks here.

## Examples

- "Create a new skill scaffold from this workflow note." -> `skill-creator`
- "Harden this existing skill and run strict audit." -> `skill-builder`
- "Install this curated skill from GitHub into this repo." -> `skill-installer`

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
