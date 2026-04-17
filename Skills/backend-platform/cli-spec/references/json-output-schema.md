# JSON Output Schema Template

Use a stable, versioned schema for `--json` outputs.

## Template (example)
```json
{
  "schema": "tool.command.v1",
  "meta": {
    "tool": "mycli",
    "version": "x.y.z",
    "timestamp": "ISO-8601",
    "request_id": "optional"
  },
  "summary": "short human summary",
  "status": "success|warn|error",
  "data": {},
  "errors": [
    {
      "code": "stable.error.code",
      "message": "human-readable message",
      "details": {},
      "hint": "optional fix or next step"
    }
  ]
}
```

## Minimal JSON Schema (validation)
Use this as a starting point for automated validation. Extend as needed.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": ["schema", "status", "data", "errors"],
  "properties": {
    "schema": { "type": "string" },
    "meta": {
      "type": "object",
      "properties": {
        "tool": { "type": "string" },
        "version": { "type": "string" },
        "timestamp": { "type": "string" },
        "request_id": { "type": "string" }
      },
      "additionalProperties": true
    },
    "summary": { "type": "string" },
    "status": { "type": "string", "enum": ["success", "warn", "error"] },
    "data": {},
    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["code", "message"],
        "properties": {
          "code": { "type": "string" },
          "message": { "type": "string" },
          "details": { "type": "object", "additionalProperties": true },
          "hint": { "type": "string" }
        },
        "additionalProperties": true
      }
    }
  },
  "additionalProperties": true
}
```

## Rules
- `--json` must emit a single JSON object, no logs or color.
- Keys are stable; add new keys only additively.
- Include a schema version string and tool version.
- `errors[].code` is stable and machine-parseable; `message` is human-readable.
