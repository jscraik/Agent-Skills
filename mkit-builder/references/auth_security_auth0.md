# Auth + Security (Auth0)

Use this when your MCP server is HTTP-based and you use Auth0 as the IdP.

## Goals

- OAuth 2.1 with Authorization Code + PKCE
- Protected Resource Metadata discovery support
- Strict token validation (issuer, audience, expiry, signature)
- No token passthrough; the MCP server validates before any tool execution

## Auth0 Setup (Typical)

1) Create an API (Resource Server)
- Set an **Identifier** (this becomes your `aud` / audience)
- Define scopes that map to tool groups (e.g., `read:issues`, `write:issues`)
- Enable RBAC and add permissions to tokens if you use role-based controls

2) Create an Application for the MCP client
- Use an app type that supports **Authorization Code + PKCE** (SPA or Native)
- Disable implicit grants
- Set Allowed Callback URLs for the MCP client

3) Configure discovery endpoints
- Issuer: `https://YOUR_TENANT_DOMAIN/`
- OIDC metadata: `https://YOUR_TENANT_DOMAIN/.well-known/openid-configuration`
- JWKS: `https://YOUR_TENANT_DOMAIN/.well-known/jwks.json`

4) Tokens
- Use short-lived access tokens
- Use refresh tokens only when required by client UX
- Enforce HTTPS only

## MCP Server Validation Rules

- Validate JWT signature using JWKS
- Validate `iss` (exact issuer), `aud` (resource identifier), `exp` and `nbf`
- Reject tokens with missing or mismatched audience
- Reject tokens not scoped for the requested tool
- Never accept tokens in query parameters
- Require `resource` to match your API identifier in OAuth requests

## Resource Indicators and PRM

- If your client supports Resource Indicators, set the requested resource to your API identifier
- If not supported, ensure the audience is still your API identifier
- If Protected Resource Metadata is supported by your server, publish it and validate incoming tokens against it
- Ensure metadata advertises PKCE (`S256`) support and required OAuth endpoints

## Tool Authorization Mapping

- Map scopes to tool families (e.g., `read:*` for list/get tools, `write:*` for create/update)
- Enforce scope checks in a shared auth middleware before tool handlers
- Return `403` with a helpful message when the scope is insufficient

## Operational Security Defaults

- Log auth failures with a correlation id
- Do not log raw access tokens
- Rate limit token validation failures
- Use structured audit logs for destructive operations

## Quick Checklist

- [ ] API created in Auth0 with identifier (audience)
- [ ] App supports Authorization Code + PKCE and implicit disabled
- [ ] Issuer and JWKS endpoints configured
- [ ] Strict JWT validation (iss, aud, exp, nbf)
- [ ] Scope checks per tool family
- [ ] No token passthrough or query param tokens
- [ ] Auth failures are logged without secrets
