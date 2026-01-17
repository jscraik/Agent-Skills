# Auth0 / OAuth Best Practices

## Baseline
- Use OAuth 2.1 guidance (PKCE required; implicit flow discouraged).
- Use OIDC for identity and standardized ID token claims.

## Auth0-specific guidance
- Enable Refresh Token Rotation for SPAs and public clients.
- Use short-lived access tokens and rotate refresh tokens on use.
- Prefer Authorization Code + PKCE for browser and mobile apps.
- Monitor reuse detection events for rotated refresh tokens.

## References
- OAuth 2.1: https://oauth.net/2.1/
- PKCE (RFC 7636): https://www.rfc-editor.org/rfc/rfc7636
- OpenID Connect Core 1.0: https://openid.net/specs/openid-connect-core-1_0.html
- OpenID Connect Core 1.0 (final): https://openid.net/specs/openid-connect-core-1_0-18.html
- Auth0 Refresh Token Rotation: https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation
- Auth0 reuse detection log events: https://auth0.com/docs/secure/tokens/refresh-tokens/refresh-token-rotation#token-reuse-detection
