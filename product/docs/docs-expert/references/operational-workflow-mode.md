# Operational workflow mode

## Table of Contents
- [When to use](#when-to-use)
- [Core model](#core-model)
- [Required rules](#required-rules)
- [Required sections](#required-sections)
- [Diagram rules](#diagram-rules)

## When to use

Use this mode when the user wants a workflow, runbook, approval flow, or agent procedure converted into a compact operational spec.

Do not use this mode for ordinary README cleanup or generic prose editing.

## Core model

Model:
- `S = state`
- `E = event`
- `G = guard`
- `A = action`
- `N = next`

Transition format:

`S | E | G | A | N`

Transition table rules:
- the transition table is the source of truth;
- non-terminal states require at least one transition;
- events must resolve deterministically;
- failures must transition to explicit `fail` or `blocked` states;
- terminal states must have no outbound transitions.

## Required rules

Always include:
- `errors {VALIDATION_ERROR, BLOCKED_DEPENDENCY, POLICY_FAIL, SYSTEM_ERROR}`
- idempotency notes
- invariants
- `metadata {owner, max_duration, escalation}`
- `logs {workflow_id, transition_code, from_state, to_state, correlation_id, result}`
- mode behavior when `STRICT` or `ADVISORY` is requested
- dry-run simulation behavior when requested

Choose the most efficient representation:
- transition table
- state machine
- pseudocode
- diagram

Preferred default:
- transition table first
- add state machine or pseudocode only when it improves clarity

## Required sections

For a complete operational spec, include:
- scope
- assumptions
- transition table
- errors
- idempotency
- invariants
- metadata
- logs
- dry-run behavior

## Diagram rules

If a diagram is included:
- use Mermaid syntax;
- derive it strictly from the transition table;
- include only states and transitions defined in the table;
- do not add inferred start or end nodes, guards, or extra transitions;
- prefer `stateDiagram-v2` unless the user explicitly asks for another format.
