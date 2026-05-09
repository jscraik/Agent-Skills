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
- For automation, include `schema_version: "1"`, `mode: "route"`, `validation_evidence`, and `blocked_by` when blocked.

## Procedure

1. Classify request intent: create, harden, analyze, install, or skillify.
2. Select exactly one primary lane.
3. Apply the OpenAI-style design contract to any create, harden, audit, or
   refactor handoff: every skill must have one primary user intent, explicit
   inputs/outputs, side-effect class, progressive-disclosure boundary,
   validation evidence, and headless/interactive behavior.
4. Return lane + rationale + next step.
5. If ambiguity is material, request clarification.

## Deterministic Decision Order

1. Explicit lane names (`skill-creator`, `skill-builder`, `skill-installer`, `skill-refactor`, `skillify`) win unless multiple lanes are named; multiple named lanes stay with this router.
2. Create, author, update, or reshape a draft skill package -> `skill-creator`.
3. Capture, operationalize, or convert a completed workflow/session into a reusable skill -> `skillify`.
4. Harden, audit, validate, benchmark, gate, or fix warnings on an existing skill -> `skill-builder`.
5. Install, list, import, or verify runtime visibility for external/curated skills -> `skill-installer`.
6. Analyze skill reliability, failures, coverage gaps, merge/prune/retire options, or portfolio improvement evidence -> `skill-refactor`.

Session-evidence boundary: route completed workflow capture into a new durable skill to `skillify`; route portfolio/session evidence about which existing skills fail, overlap, or should merge/retire to `skill-refactor`.

## Validation

- Fail fast: if routing uncertainty could cause wrong or unsafe actions, stop and ask.
- Confirm lane matches user outcome.
- Ensure the next step is executable in-repo.
- For skill creation or hardening, verify the selected lane will check trigger
  precision, side-effect class, structured output shape, disclosure boundary,
  and validation/eval coverage before the skill is considered ready.

## Execution Boundaries

This router is read-only. It selects one skill-factory lane and returns the next
handoff. It must not edit skill files, install packages, sync projections, or
mutate external trackers from the routing step.

Start with the smallest relevant surface: request text, explicit paths, and the
design contract. Load child lane details only after route selection.

## Failure Mode

If lane choice, target skill path, authority to mutate, or side-effect class is
unclear, stop with `blocked_by` and the smallest missing input. Do not choose a
lane from keyword overlap alone.

## Gotchas

- A skill can be too broad even when every individual section looks useful.
- A read-only audit request must not become an edit or install action.
- Runtime projections are generated surfaces; route repair to the canonical
  source lane before any sync.

## Constraints

- Map requests strictly to lane purpose.
- Do not execute unrelated coding work from this router.
- Redact secrets, tokens, credentials, and sensitive data.

## anti-patterns

- Do not pick multiple primary lanes.
- Do not send install/distribution work to authoring lanes.
- Do not route ordinary coding/debug tasks here.
- Do not bless vague triggers, hidden side effects, or always-loaded prompt
  bodies as "agent-native."

## Examples

- "Create a new skill scaffold from this workflow note." -> `skill-creator`
- "Harden this existing skill and run strict audit." -> `skill-builder`
- "Install this curated skill from GitHub into this repo." -> `skill-installer`

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- Shared design contract:
  `Infrastructure/references/openai-style-plugin-design-contract.md`
- Local skill shape contract:
  `Infrastructure/references/agent-native-skill-contract.md`
