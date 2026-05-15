---
name: he-compound
description: "WHAT: Diagnose deprecated he-compound compatibility requests and redirect them to he-reconcile or he-reinforce. WHEN: Use when older Harness prompts need lifecycle recovery, solved-problem capture, or learning refresh compatibility."
metadata:
  version: 1.0.0
  skill-type: team_automation
  lifecycle: deprecated
---
# Skill: Harness Engineering Compound Compatibility

## Philosophy

`he-compound` is no longer the owning Harness Engineering skill. It is retained
only as a compatibility handle so older prompts can be routed without losing
intent.

## When to Use

Use only when a user, artifact, or generated handle explicitly invokes
`he-compound` and the caller has not yet selected the replacement skill.

## When Not to Use

Do not use as a primary stage. Use `he-reconcile` for lifecycle state refresh,
resume routing, source-prompt coverage, and repeated-failure state recovery. Use
`he-reinforce` for solved-problem capture, stale learning refresh,
`he-compound-refresh` style maintenance, and Project Brain learning sync.

## Preconditions

Resolve the user's actual intent before handoff. Do not write artifacts,
mutate trackers, edit code, or claim completion from this compatibility handle.

## Procedure

1. If the request asks to refresh, resume, reconcile, compare source prompts,
   recover lifecycle state, or identify the earliest incomplete HE stage, hand
   off to `he-reconcile`.
2. If the request asks to remember, capture, compound, refresh learnings,
   maintain solution docs, sync Project Brain, or document a solved problem,
   hand off to `he-reinforce`.
3. If intent is mixed or ambiguous, return one narrow clarification question or
   route to `he-router`.

## Validation

Fail fast: stop at the first failed gate, do not continue through replacement
routing as if validation passed, and report the blocked gate.

- Validate this compatibility skill with
  `./bin/ask skills audit Plugins/harness-engineering/skills/he-compound --level strict --json --robot`.
- Validate the selected replacement skill after handoff:
  - `he-reconcile` for lifecycle recovery.
  - `he-reinforce` for solved-problem capture or learning refresh.
- If replacement validation is unavailable, return `missing_input` and
  `recommended_next_step` instead of claiming completion.

## Gotchas

- This handle is a compatibility router, not an execution stage.
- Do not create new compound artifacts from this skill.
- Do not treat a routing recommendation as proof that lifecycle state or
  learning capture was completed.
- Older prompts may use `he-compound` to mean either reconciliation or
  reinforcement; classify the intent before handoff.

## Examples

- When the user asks to inspect the JSC-301 harness state with the deprecated
  `he-compound` handle, route lifecycle recovery to `he-reconcile`.
- When the user asks to validate a solved auth preflight failure for future runs,
  route learning capture to `he-reinforce`.
- When the user asks to diagnose a failed phase without enough context, route to
  `he-router` or ask one clarification question.

## Safety Boundaries

Redact secrets, credentials, private transcript text, tokens, PII, and sensitive
business data by default before summarizing or handing off. This handle has
routing authority only. It cannot authorize implementation, artifact writes,
external mutation, deletion, closure proof, or learning capture.
Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
references and index it in `../../references/deferred-context-index.md`.
Apply the context-disposition policy by moving important still-valid context to
references and intentionally discarding stale, duplicated, unsafe, superseded,
or low-signal text.

## Handoff Rules

- `he-reconcile`: lifecycle state, resume routing, source-prompt coverage,
  tracker/artifact conflicts, repeated-failure state.
- `he-reinforce`: solved-problem learning, stale learning refresh,
  Project Brain learning sync, overlap-aware solution capture.
- `he-router`: unclear replacement.

## Output Format

Return `schema_version`, `selected_replacement`, `matched_intent`,
`authority_limit`, `missing_input`, and `recommended_next_step`.

## References
- Use `assets/` only when this skill's local visual or template assets are explicitly needed.

Replacement skills:

- `../he-reconcile/SKILL.md`
- `../he-reinforce/SKILL.md`

Supporting references:

- `contract.yaml`
- `evals.yaml`
- Shared subagent call policy: `../../references/subagent-call-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
