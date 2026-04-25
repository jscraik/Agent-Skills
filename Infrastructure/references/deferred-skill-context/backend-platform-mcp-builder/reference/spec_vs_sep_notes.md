# Spec vs SEP Notes

Use this when SDK guidance or proposals disagree with the published MCP spec.

## Tool Name Constraints

- **Spec (2025-11-25)**: 1–128 chars, case-sensitive, allowed `A-Z a-z 0-9 _ - .`
- **SEP proposal**: suggests 1–64 and allows `/` (proposal, not binding)

**Guidance**: follow the current published spec for production servers.

## Transport

- **Spec**: Streamable HTTP and stdio are current
- **Legacy**: SSE is present for backward compatibility

## Output Schemas

- **Spec**: JSON Schema 2020-12 for `inputSchema`/`outputSchema`
- **SDKs**: may allow looser validation; still follow spec
