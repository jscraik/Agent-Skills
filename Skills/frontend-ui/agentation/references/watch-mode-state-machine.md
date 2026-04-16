# Agentation Watch-Mode State Model

Use this reference when the request is about hands-free processing, `"watch mode"`, critique mode, or self-driving flows.

## Core loop

1. Verify the Agentation MCP tools are available.
2. Call `agentation_watch_annotations`.
3. For each new annotation in the returned batch:
   - inspect stable identifiers;
   - de-duplicate against already processed annotation and session IDs;
   - call `agentation_acknowledge`;
   - make the requested fix;
   - use `agentation_reply` if interim clarification or progress is needed;
   - call `agentation_resolve` with a concise summary when fixed;
   - call `agentation_dismiss` with a reason when the change is intentionally not being applied.
4. Call `agentation_watch_annotations` again until a stop condition is reached.

## State buckets

- `ui_mount`
  - `missing`
  - `ready`
- `endpoint`
  - `unknown`
  - `reachable`
  - `failing`
- `mcp`
  - `disconnected`
  - `connected`
  - `degraded`
- `webhook`
  - `unknown`
  - `synthetic_only`
  - `real_submit_verified`
  - `failing`
- `queue`
  - `unknown`
  - `idle`
  - `pending`
  - `degraded`
- `runner`
  - `manual`
  - `watch_mode`
  - `critique`
  - `self_driving`
  - `stopped`

## Partial and blocked outcomes

Report `blocked` when:
- `agentation_watch_annotations` is unavailable;
- MCP auth or registration is broken;
- the session cannot be identified safely;
- repeated acknowledge, resolve, or dismiss calls fail and bounded retries are exhausted.

Report `partial` when:
- only synthetic webhook traffic was verified;
- no real pending annotations were observed yet;
- queue state is inferred but not confirmed by MCP tools;
- a fix was applied but resolve or dismiss reporting could not be completed.

## Reporting contract

When the loop ends, report:
- last processed annotation ID if known;
- number of processed items if known;
- current queue state (`idle`, `pending`, `unknown`, or `degraded`);
- stop reason (`user_stop`, `timeout`, `mcp_failure`, `tool_failure`, `unsafe_payload`, or `unknown`).

## Anti-rationalization reminders

- Do not infer queue success from MCP connection alone.
- Do not claim watch mode is working if only webhook transport was tested.
- Do not keep retrying the same broken acknowledge or resolve path indefinitely.
- Do not treat `no pending annotations` as completed work.
