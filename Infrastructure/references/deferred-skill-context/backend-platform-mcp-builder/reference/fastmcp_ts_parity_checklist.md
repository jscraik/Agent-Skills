# FastMCP vs TS SDK Parity Checklist

Use this when you maintain both implementations or migrate between them.

## Transport

- Streamable HTTP enabled and reachable at `/mcp`
- SSE (if present) is legacy only
- `MCP-Protocol-Version` header is included
- Session handling is consistent (`MCP-Session-Id` behavior)

## Tool Surface

- Identical tool names, descriptions, titles
- Same `inputSchema` and `outputSchema`
- Same annotations for readOnly/destructive/idempotent/openWorld
- Same `_meta` for `openai/outputTemplate` and widget metadata

## Output Consistency

- `structuredContent` shape matches in both implementations
- Text JSON fallback included where `structuredContent` exists
- Error shape is consistent and uses `isError` properly

## Auth

- Same OAuth flow and token validation rules
- Same scope-to-tool mapping
- Same 401/403 behavior and error messaging

## Widgets

- Same template URIs and bundle versions
- Same CSP allowlists
- Same widget runtime assumptions
