# Apps SDK Requirements (Official)

Use this when building or reviewing MCP servers intended for ChatGPT Apps SDK.

## Core Server Requirements

- Local dev can be HTTP, but deployment must be HTTPS on a stable public domain
- `/mcp` endpoint must be publicly accessible for production and submissions
- Apps SDK supports SSE and Streamable HTTP, but recommends Streamable HTTP
- MCP JSON-RPC methods used by Apps SDK: `tools/list`, `tools/call`, `resources/list`
- Define a CSP that allows the exact domains your widget fetches from (required for submission)

## Widget + Resource Requirements

- Widget resources must use `mimeType: text/html+skybridge`
- Tool metadata should include `_meta["openai/outputTemplate"]` to link the widget template
- Use `_meta` for widget-only data and `structuredContent` for model-readable data
- `_meta` is not visible to the model; only the widget reads it
- Use `_meta["openai/widgetCSP"]` on the widget resource
- Use `_meta["openai/widgetDomain"]` if you need a dedicated origin
- Use `_meta["openai/widgetDescription"]` to reduce redundant text under widgets

## Tool Behavior Expectations

- Tool calls may be retried; handlers should be idempotent where possible
- Keep `structuredContent` concise; the model reads it directly
- Use `_meta["openai/widgetAccessible"]` to allow widget-initiated tool calls
- Use `_meta["openai/visibility"]` = `private` for widget-only tools
- Use `_meta["openai/fileParams"]` for file inputs (top-level fields only)

## Widget Runtime (window.openai)

- The widget runs in a sandboxed iframe with `window.openai` APIs
- Use `toolOutput` for `structuredContent` and `toolResponseMetadata` for `_meta`
- Use `callTool` for widget-initiated tool calls
- Widget state (`setWidgetState`) is visible to the model; keep payloads small and intentional (well under 4k tokens)

## Submission Constraints (Directory)

- Server must not use localhost or test endpoints for submission
- MCP server must be on a publicly accessible domain
- CSP is required for submission

## Auth (Apps SDK)

- For authenticated tools, implement OAuth 2.1 per MCP authorization spec
- Host protected resource metadata on your MCP server
- Expose OAuth/OIDC discovery metadata for your authorization server
- Ensure PKCE (S256) is advertised and supported
