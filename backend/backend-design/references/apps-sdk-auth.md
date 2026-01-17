# Apps SDK: Authentication (Condensed)

## OAuth 2.1 for MCP
- Use Authorization Code + PKCE (S256).
- Publish protected resource metadata on MCP server.
- Publish OAuth/OIDC discovery metadata on the auth server.
- Echo the `resource` parameter throughout the flow.
- Allowlist ChatGPT redirect URIs.

## Token verification
- Validate signature, issuer, audience/resource, expiry, scopes.
- Return WWW-Authenticate with resource metadata on 401.

## Notes
- Dynamic client registration required; CMID is in draft.
