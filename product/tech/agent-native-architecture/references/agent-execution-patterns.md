# Agent Execution Patterns

## Completion model

Define explicit completion semantics.

Preferred pattern:
- Success and continue are separate dimensions.
- A successful tool call may still continue loop work.
- A blocked status can terminate loop with explanation.

## Completion contract

Use a terminal signal when the objective is met or blocked:

- `status`: success | partial | blocked
- `summary`: concise account of work done
- `next_action`: optional follow-up when blocked/partial

## Partial completion

For multi-step tasks, track stage progress in a resumable form:

- stage id
- current state
- pending steps
- blocking reason

## Retry and timeout policy

Define bounded retries and escalation behavior:

- transient errors: limited retries + jitter/backoff
- permanent errors: fail fast with explanation
- repeated unknown errors: stop and request clarification

## Context window discipline

Plan for bounded context from the start:

- summarize old context
- keep latest authoritative state references
- rehydrate critical constraints before irreversible actions

## Anti-patterns

- Heuristic-only completion detection.
- Infinite loops on repeated failures.
- Partial results with no resumable state.
- Silent termination without explicit status.
