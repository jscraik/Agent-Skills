# Agent Operator Interface Spec

Use this reference when the deliverable is an operator-facing command or workflow surface for agents rather than a GUI-first product spec.

## Goal

Define a compact, implementation-ready interface that lets agents access key functionality without relying on the UI.

This mode is especially appropriate when the request mentions:

- robot mode
- agent operator
- command surface
- machine-readable outputs
- quick start with no args
- deterministic errors
- output contracts
- workflow or operational spec

## Required outcomes

Every operator-interface spec should cover:

1. Problem statement
2. Goals and non-goals
3. Command taxonomy mapped to user intent
4. Output contracts
5. Error behavior
6. Compatibility policy
7. Workflow or state model when the interface is multi-step

## Default shape

Prefer this order:

1. Problem statement
2. Goals and non-goals
3. Core operator tasks
4. Command taxonomy
5. Quick-start behavior
6. Output contracts
7. Error envelope
8. Compatibility and versioning
9. Operational workflow
10. Validation checklist

## Command taxonomy

Model commands around operator intent, not backend internals.

Recommended table columns:

| Intent | Entry point | Inputs | Default behavior | Machine output | Human output | Notes |
|---|---|---|---|---|---|---|

Good intents:

- inspect status
- list work
- execute one task
- validate inputs
- simulate / dry run
- explain failure
- resume or retry

## Quick-start behavior

For agent operators, a no-arg invocation should be useful and token-dense.

Specify:

- what happens with no args
- what the minimal machine-readable output looks like
- what next actions are suggested
- how the quick-start view avoids excessive prose

Good quick-start defaults usually include:

- current mode
- available top-level intents
- one-line usage examples
- current environment or scope
- a short list of likely next commands

## Output contracts

Default machine-readable mode first.

Machine-readable guidance:

- Prefer `JSON` when strict parsing matters.
- Constrained `Markdown` is acceptable when tables/checklists are the contract and downstream consumers are tolerant of formatting.
- Include top-level `schema_version` for machine-bound outputs.
- Keep required fields stable.
- Distinguish human summaries from machine fields.

Recommended machine-readable envelope:

```json
{
  "schema_version": "1.0",
  "status": "ok",
  "mode": "machine",
  "result": {},
  "errors": [],
  "next_actions": []
}
```

Human-readable guidance:

- Human mode should be explicit, not implicit.
- Optimize for scanning, not parsing.
- Do not promise compatibility for prose layout.

## Deterministic error envelope

Errors should teach correct usage rather than only reporting failure.

Recommended fields:

```json
{
  "schema_version": "1.0",
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Missing required input: workflow_id",
    "hint": "Provide --workflow-id <id> or run without args to list eligible workflows."
  }
}
```

Recommended codes:

- `VALIDATION_ERROR`
- `BLOCKED_DEPENDENCY`
- `POLICY_FAIL`
- `SYSTEM_ERROR`

When the workflow or runtime needs richer coverage, add domain-specific codes without breaking the base envelope.

## Compatibility and versioning

Specify the compatibility policy directly.

Recommended rules:

- additive fields are allowed in machine-readable mode
- existing required fields cannot disappear without a schema-version bump
- field meaning must not drift silently
- human-readable mode is not a stability contract
- examples should match the current schema version

## Operational workflow

If the interface is multi-step, convert it to a compact operational spec.

Choose the most efficient representation:

- transition table
- state machine
- pseudocode
- Mermaid diagram

When using a transition table, make it the source of truth.

Minimum workflow coverage:

- states
- triggering events
- guards
- actions
- failure states
- idempotency
- invariants
- metadata
- logs
- dry-run behavior

## OpenAI-aligned heuristics (March 2026)

These patterns align with current OpenAI Codex guidance:

- keep the main guidance concise and push deep detail into linked references
- make reusable operator behavior explicit instead of repeating it ad hoc
- favor interfaces that map directly to operator intent
- provide quick-start entry points and verification guidance
- keep outputs clean, semantically structured, and machine-consumable when needed

## Validation checklist

- The command taxonomy maps to user intent, not internal modules.
- The no-arg path is useful for an agent operator.
- Machine-readable mode is the default compatibility surface.
- Human-readable mode is explicit.
- Error responses teach the next correct action.
- Schema versioning and forward-compatibility rules are documented.
- Multi-step workflows include a deterministic operational model.
