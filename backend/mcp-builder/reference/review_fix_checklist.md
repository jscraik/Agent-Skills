# Review & Fix Checklist (Gold Standard, Dec 31 2025)

Use this checklist when auditing an existing MCP server to identify bugs, spec gaps, and improvement opportunities. It applies to both the official TypeScript SDK and FastMCP.

## 1) Protocol & Transport

- Streamable HTTP is primary; stdio for local
- If SSE endpoints exist, treat as legacy/backwards-compat only
- Validate `Origin` header on all HTTP requests (DNS rebinding mitigation)
- Use a single MCP endpoint that supports GET + POST
- Include `MCP-Protocol-Version` on HTTP requests
- If using sessions, handle `MCP-Session-Id` correctly
- Ensure JSON-RPC methods are correct: `tools/list`, `tools/call`, `resources/list`

## 2) Tools, Schemas, and Outputs

- Every tool has `name`, `description`, `inputSchema`
- `inputSchema` and `outputSchema` are JSON Schema 2020-12
- When `outputSchema` exists:
  - `structuredContent` is present and conforms
  - A text JSON fallback is included in `content`
- Tool names are stable, action-oriented, and prefixed to avoid collisions
- Tool names use only allowed characters and reasonable length
- Tool annotations reflect reality (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`)
- If SDKs conflict, prefer the current MCP spec for tool name constraints

## 3) Tool Result Patterns

- Tool results use `isError` consistently and still return a result object
- Pagination: consistent `limit`/`cursor` or `limit`/`offset` across tools
- Resource links: use resource link content items for files/documents (and remember they may not appear in `resources/list`)
- Embedded resources: use when returning inline content and ensure `resources` capability is set

## 4) Auth & Security (HTTP)

- Implement OAuth 2.1 for HTTP transports
- Protected Resource Metadata is exposed and discoverable
- PKCE enforced for public clients (S256) and verified via metadata
- Tokens validated for issuer, audience, expiry, and signature
- Scopes enforced per tool family; do not rely on client hints
- Do not log tokens; log correlation IDs instead

## 4.1 Reliability & Ops

- Timeouts and retry/backoff for upstream calls
- Rate limiting for abusive clients
- Correlation IDs in logs and error payloads
- Payload size caps and stable structured outputs
- Follow the [Reliability & Ops Runbook](./reliability_ops_runbook.md) for production hardening

## 5) Widget/Apps SDK Integration

- UI resources use `mimeType: text/html+skybridge`
- `_meta["openai/outputTemplate"]` points to the correct resource URI
- Widget CSP and domains are minimal and explicit
- Use `_meta` for widget-only data and `structuredContent` for model-readable data

## 6) Regression Testing

- Inspector smoke tests for tool list and tool calls
- Contract tests validate `inputSchema` and `outputSchema`
- Snapshot tests for `structuredContent` and `_meta`
- Tool call retries are safe and idempotent

## 7) FastMCP-Specific Notes

- `httpStream` enables Streamable HTTP (and may also expose SSE for legacy clients)
- Default HTTP stream endpoint is `/mcp` (customizable)
- Validate that returned results match schema expectations, especially for `structuredContent`
- Prefer FastMCP defaults, but override where spec compliance requires stricter behavior

## 8) TypeScript SDK-Specific Notes

- Use strict schema validation and return `structuredContent` for tools with `outputSchema`
- Ensure errors are surfaced as `isError: true` when appropriate
- Avoid throwing before returning a structured error when validation fails
