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
- Mode: `read_only_review`, `auto_tighten_until_pass_or_blocked`, `session_evidence_analysis`, `artifact_generation`, or `install_visibility`.
- Optional `next_handoff` when a second lane must consume the primary lane's
  output; keep `selected_lane` singular and deterministic.
- For automation, include `schema_version: "1"`, `mode: "route"`, `validation_evidence`, and `blocked_by` when blocked.

`next_handoff` must use this shape when present:

- `lane`: one of the Skill Factory lanes
- `mode`: the target lane mode
- `condition`: the concrete completion condition for the primary lane
- `expected_input`: structured artifacts the target lane must receive
- `blocked_by`: blockers that prevent the handoff, or an empty list

If a second lane is required and `next_handoff` is omitted, the route is
incomplete.

## Procedure

1. Classify request intent: create, harden, analyze, install, or skillify.
2. Select exactly one primary lane.
3. Apply the OpenAI-style design contract to any create, harden, audit, or
   refactor handoff: every skill must have one primary user intent, explicit
   inputs/outputs, side-effect class, progressive-disclosure boundary,
   validation evidence, and headless/interactive behavior.
4. Classify execution mode before handoff:
   - `read_only_review` for review, audit, or evaluate requests that do not ask for edits.
   - `auto_tighten_until_pass_or_blocked` for update, harden, improve, fix, tighten, make acceptable, or release-readiness requests against an existing skill.
   - `session_evidence_analysis` when session-collector, prior-run evidence, repeated failures, routing gaps, or keep/improve/merge/retire decisions are the main input.
   - `artifact_generation` when the user asks for a generated media or concrete artifact output.
   - `install_visibility` for install, list, sync, prove, or runtime visibility work.
5. Return one primary lane + mode + rationale + next step. If the work requires
   a second lane after the primary result, include `next_handoff` with `lane`,
   `mode`, `condition`, and expected input from the primary lane.
6. If ambiguity is material, request clarification.

## First-Principles Gate

Before create, harden, refactor, or skillify handoff, identify the user
outcome, copied assumption, smallest effective mechanism, artifact decision,
and proof needed. Prefer `IMPROVE_EXISTING`, `DOCS_ONLY`, or `DO_NOT_BUILD`
when a new skill would only copy a template or increase context load.

## Deterministic Decision Order

1. Explicit lane names (`skill-creator`, `skill-builder`, `skill-installer`, `skill-refactor`, `skillify`) win unless multiple lanes are named; multiple named lanes stay with this router.
2. Create, author, or reshape a draft skill package -> `skill-creator`.
3. Capture, operationalize, or convert a completed workflow/session into a reusable skill -> `skillify`.
4. Update, harden, improve, fix, tighten, validate, benchmark, gate, or fix warnings on an existing skill -> `skill-builder`. Default to `auto_tighten_until_pass_or_blocked` unless the user explicitly asked for read-only review.
5. Install, list, import, or verify runtime visibility for external/curated skills -> `skill-installer`.
6. Analyze skill reliability, failures, coverage gaps, merge/prune/retire options, or portfolio improvement evidence -> `skill-refactor`.

Session-evidence boundary: route completed workflow capture into a new durable skill to `skillify`; route portfolio/session evidence about which existing skills fail, overlap, or should merge/retire to `skill-refactor`. When `skill-refactor` produces concrete repair items for an existing skill, return `selected_lane: skill-refactor` and include `next_handoff: {lane: skill-builder, mode: auto_tighten_until_pass_or_blocked, condition: repair_items_ready}` rather than leaving the result as advisory prose.

## Hardening Trigger Stack

Treat prompts that combine reviewer, harness engineer, systems architect, Skill Factory validation, adversarial hardening, validator alignment, or media artifact operator language as an existing-skill hardening request unless the user explicitly asks for read-only analysis. Route to `skill-builder` with `auto_tighten_until_pass_or_blocked`; if the prompt also asks why repeated iterations happened, make `skill-refactor` the primary lane and set `next_handoff` to `skill-builder` for actionable fixes.

If the current request is a follow-up to an already completed session-evidence
diagnosis and asks to proceed, select `skill-builder` as the primary lane and
treat the prior `skill-refactor` output as required evidence input.

For generated media or concrete artifact requests, do not downgrade the ask to prompt writing. Use `artifact_generation` mode and map the primary lane by target:

- existing skill package -> `skill-builder`
- new skill package -> `skill-creator`
- completed workflow capture -> `skillify`

Require the target lane to produce artifact evidence or a precise blocked status.

## Evidence Route Selection

For create, update, harden, refactor, or generated-artifact work, choose the
smallest evidence route that can prove the claim:

- repo contracts and canonical source for ownership, path, and workflow truth
- session collector for repeated failures, prior-run behavior, or "why does
  this keep happening" requests
- memory for durable prior decisions and known recurring patterns
- `openai-docs` for official OpenAI, Codex, Responses API, Agents SDK, model,
  hosted-tool, plugin, or skill behavior
- `context7` for current non-OpenAI library, framework, CLI, or external API
  documentation
- validators and evals for readiness claims

Do not load external docs by default. Route to `openai-docs` or `context7` only
when the research decision depends on current external behavior, official docs,
or version-sensitive APIs. Capture retrieved docs as evidence for a claim rather
than as ambient prompt context.

## Validation

- Fail fast: if routing uncertainty could cause wrong or unsafe actions, stop and ask.
- Confirm lane matches user outcome.
- Ensure the next step is executable in-repo.
- For skill creation or hardening, verify the selected lane will check trigger
  precision, side-effect class, structured output shape, disclosure boundary,
  and validation/eval coverage before the skill is considered ready.
- For hardening, Plugin Eval success cannot override strict audit, eval realism,
  docs/prose/spelling, media persistence, or runtime visibility failures.

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
- An edit/hardening request must not become a report-only response unless edits
  are blocked by ownership, permissions, missing evidence, or explicit user
  constraint.
- Runtime projections are generated surfaces; route repair to the canonical
  source lane before any sync.
- Session-collector evidence is an input to root-cause grouping, not a reason to
  read broad raw transcripts before bounded extracts.

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
- "Make this skill acceptable; I keep needing iteration prompts." ->
  `skill-refactor` with `next_handoff` to `skill-builder` for repair.
- "Install this curated skill from GitHub into this repo." -> `skill-installer`

## References

- [references/contract.yaml](./references/contract.yaml)
- [references/evals.yaml](./references/evals.yaml)
- Shared design contract:
  `Infrastructure/references/openai-style-plugin-design-contract.md`
- Local skill shape contract:
  `Infrastructure/references/agent-native-skill-contract.md`
