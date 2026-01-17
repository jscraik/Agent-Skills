# Tool Result Patterns

Use these patterns to keep tool outputs stable, machine-friendly, and easy to debug.

## 1) Error Shape

- Prefer a consistent error payload across tools
- Include a short user-facing message and a stable error code
- Include a correlation id for logs
- Set `isError: true` when the tool result represents an error

Example (text + structuredContent):

```json
{
  "error": {
    "code": "AUTH_SCOPE_MISSING",
    "message": "Token missing scope: read:issues",
    "correlation_id": "req_01HZX..."
  }
}
```

## 2) Pagination Pattern

- Support `limit` and `offset` (or cursor) in inputs
- Return `has_more` and `next_offset` (or `next_cursor`)
- Keep pagination fields stable across tools

Example:

```json
{
  "items": [ ... ],
  "count": 20,
  "total": 150,
  "has_more": true,
  "next_offset": 20
}
```

## 3) Resource Links

Use resource links or embedded resources for files or documents:

```json
{
  "resources": [
    {
      "uri": "resource://files/abc123",
      "name": "report.pdf",
      "mime_type": "application/pdf"
    }
  ]
}
```

Note: Resource links returned by tools are not guaranteed to appear in `resources/list`.

## 4) Structured Output + Text Fallback

Return `structuredContent` plus a JSON text fallback so older clients still work:

- `structuredContent`: typed object matching `outputSchema`
- `content` text: serialized JSON or concise summary

## 5) Stable Fields and Formats

- Use consistent field names and types across tools
- Use ISO-8601 timestamps
- Include IDs alongside display names
- Avoid large blobs when a resource link is better
- Payload size target: keep `structuredContent` well under 4k tokens

## 6) Read-Only vs Destructive

- Set annotations correctly and reflect behavior
- For destructive tools, return an explicit summary of changes

## 7) Idempotency Hints

- For create/update tools, be explicit whether repeated calls are safe
- If idempotent, document which parameters ensure idempotency
