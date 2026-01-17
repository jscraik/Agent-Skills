# MCP Idempotency and Replay Protection

## Idempotency
- Require an idempotency key per tool call (client-provided).
- Store dedupe window (e.g., 24h) keyed by workspace + tool + idempotency key.
- Return cached response on duplicates.

## Replay Protection
- Include nonce and request_id in tool input.
- Verify nonce freshness and uniqueness within dedupe window.
- Reject stale or reused nonces.
