# Agentation Watch-Mode State Model

Use this reference when the request is about self-driving, hands-free, or `"watch mode"` behavior.

## Core loop

1. Verify MCP tools are available.
2. Start `agentation_watch_annotations`.
3. For each new annotation:
   - inspect stable identifiers;
   - de-duplicate against already processed items;
   - call `agentation_acknowledge`;
   - make the requested fix;
   - optionally call `agentation_reply` for interim progress;
   - call `agentation_resolve` with a concise summary;
   - continue polling.
4. Stop on explicit user stop, timeout, or repeated transport/tool failure.

## State buckets

- `ui_mount`
  - `missing`
  - `ready`
- `mcp`
  - `disconnected`
  - `connected`
  - `degraded`
- `webhook`
  - `unverified`
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
  - `critique`
  - `autopilot`
  - `watch_mode`
  - `stopped`

## Partial and blocked outcomes

Report `blocked` when:
- `agentation_watch_annotations` is unavailable;
- MCP auth/registration is broken;
- the session cannot be identified safely;
- repeated acknowledge/resolve calls fail and bounded retries are exhausted.

Report `partial` when:
- only synthetic webhook traffic was verified;
- no real pending annotations were observed yet;
- queue state is inferred but not confirmed by MCP tools;
- a fix was applied but resolve/reporting could not be completed.

## Reporting contract

When watch mode ends, report:
- last processed annotation ID if known;
- number of processed items if known;
- current queue state (`idle`, `pending`, `unknown`, or `degraded`);
- stop reason (`user_stop`, `timeout`, `mcp_failure`, `tool_failure`, `unsafe_payload`, or `unknown`).

## Anti-rationalization reminders

- Do not infer queue success from MCP connection alone.
- Do not claim watch mode is working if only webhook transport was tested.
- Do not keep retrying the same broken acknowledge/resolve path indefinitely.
- Do not treat "no pending annotations" as completed work.
