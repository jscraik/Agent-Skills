# Review & Fix Recipes (TS SDK + FastMCP)

Use these recipes to diagnose issues quickly and apply reliable fixes.

## A) Tools not discoverable by the model

Symptoms:
- Tool never appears in selection
- Model picks wrong tool

Checks:
- Description starts with "Use this when..."
- Name is action-oriented, unique, and prefixed
- Tool has valid `inputSchema` with clear parameter descriptions

Fix:
- Rewrite description for intent alignment
- Split multi-purpose tools into focused tools
- Add `title` and `icons` for UI discoverability

## B) Tool calls fail with schema errors

Symptoms:
- Invalid params or missing fields
- Model sends malformed args repeatedly

Checks:
- `inputSchema` is JSON Schema 2020-12
- Required fields are in `required`
- `additionalProperties` set explicitly

Fix:
- Add defaults and enums where possible
- Use tight validation and return helpful error text

## C) Structured outputs missing or inconsistent

Symptoms:
- Widget renders empty data
- Model ignores tool results

Checks:
- `outputSchema` exists for structured outputs
- `structuredContent` matches schema
- Text fallback includes JSON

Fix:
- Add `outputSchema` and align fields
- Return `structuredContent` and text fallback in every tool

## D) Widget does not render

Symptoms:
- `window.openai` undefined
- Blank widget area

Checks:
- Resource `mimeType` is `text/html+skybridge`
- `_meta["openai/outputTemplate"]` matches resource URI
- CSP allows asset domains

Fix:
- Correct `mimeType`
- Update template URI on breaking changes
- Tighten CSP and allow only required domains

## E) Auth failures with Auth0

Symptoms:
- 401/403 on all requests
- Tokens accepted but tools fail

Checks:
- Validate `iss`, `aud`, `exp`, `nbf`
- `aud` matches Auth0 API identifier
- Scope mapping enforced per tool

Fix:
- Correct audience and JWKS configuration
- Add scope checks in shared middleware

## F) Pagination inconsistencies

Symptoms:
- Different tools use different pagination fields
- Model loops or misses data

Checks:
- Standardize `limit` + `offset` or `limit` + `cursor`

Fix:
- Normalize responses to a single pagination pattern
- Always return `has_more` and `next_offset`/`next_cursor`

## G) FastMCP specifics

- Ensure `httpStream` is enabled for Streamable HTTP
- Confirm the MCP endpoint is reachable at `/mcp`
- Validate `structuredContent` for tools with `outputSchema`

## H) TS SDK specifics

- Ensure `structuredContent` is returned when `outputSchema` is defined
- Use `isError: true` for tool errors instead of throwing
- Avoid throwing before crafting a meaningful error response
