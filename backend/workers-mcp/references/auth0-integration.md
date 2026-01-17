# Auth0 OAuth 2.1 Integration

Production-ready OAuth 2.1 authentication using Auth0 for Cloudflare Workers MCP servers.

## Architecture Overview

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Claude    │──OAuth──▶│  Auth0      │──Token──▶│   Worker     │
│   Desktop   │         │  Provider   │         │   Server     │
└─────────────┘         └─────────────┘         └──────────────┘
                              │                        │
                              │                        │
                              ▼                        ▼
                        ┌─────────────┐         ┌──────────────┐
                        │  Auth0      │         │   D1 / KV    │
                        │  Database   │         │   Storage    │
                        └─────────────┘         └──────────────┘
```

## Auth0 Application Setup

### 1. Create Auth0 Application

In Auth0 Dashboard:
1. Go to **Applications** → **Applications** → **Create Application**
2. Choose **Regular Web Application**
3. Settings:
   - **Name**: `Your MCP Server`
   - **Allowed Callback URLs**: `https://your-worker.workers.dev/oauth/callback`
   - **Allowed Logout URLs**: `https://app.yourdomain.com`
   - **Allowed Web Origins**: `https://app.yourdomain.com`

### 2. Configure OAuth 2.1 Settings

In **Application** → **Advanced Settings** → **Grant Types**:
- ✅ **Authorization Code**
- ✅ **Refresh Token** (for token rotation)

In **Application** → **Advanced Settings** → **Endpoint**:
- Set **Token Endpoint Auth Method** to `post`

## Worker Implementation

### Environment Configuration

```toml
# wrangler.toml
[vars]
AUTH0_DOMAIN = "your-tenant.auth0.com"
AUTH0_CLIENT_ID = "your-client-id"
BASE_URL = "https://your-worker.workers.dev"
```

Secrets (set via CLI):
```bash
wrangler secret put AUTH0_CLIENT_SECRET
wrangler secret put JWT_SECRET
```

### Auth0 Client Class

```typescript
// src/lib/auth/auth0.ts
export class Auth0Client {
  private domain: string;
  private clientId: string;
  private clientSecret: string;
  private redirectUri: string;

  constructor(env: Env) {
    this.domain = env.AUTH0_DOMAIN;
    this.clientId = env.AUTH0_CLIENT_ID;
    this.clientSecret = env.AUTH0_CLIENT_SECRET;
    this.redirectUri = `${env.BASE_URL}/oauth/callback`;
  }

  /**
   * Generate authorization URL for OAuth flow
   */
  getAuthorizationURL(state: string): string {
    const params = new URLSearchParams({
      client_id: this.clientId,
      redirect_uri: this.redirectUri,
      scope: 'openid profile email',
      response_type: 'code',
      state: state,
      // PKCE parameters (recommended)
      code_challenge: generateCodeChallenge(codeVerifier),
      code_challenge_method: 'S256',
    });

    return `https://${this.domain}/authorize?${params}`;
  }

  /**
   * Exchange authorization code for access token
   */
  async exchangeCodeForToken(code: string): Promise<{
    accessToken: string;
    refreshToken?: string;
    idToken: string;
    expiresIn: number;
  }> {
    const response = await fetch(`https://${this.domain}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'authorization_code',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        code,
        redirect_uri: this.redirectUri,
        code_verifier: codeVerifier,  // For PKCE
      }),
    });

    if (!response.ok) {
      throw new Error('Token exchange failed');
    }

    return await response.json();
  }

  /**
   * Get user info from Auth0
   */
  async getUserInfo(accessToken: string): Promise<{
    sub: string;           // Auth0 user ID
    email: string;
    name: string;
    picture?: string;
  }> {
    const response = await fetch(`https://${this.domain}/userinfo`, {
      headers: { 'Authorization': `Bearer ${accessToken}` },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user info');
    }

    return await response.json();
  }

  /**
   * Refresh access token using refresh token
   */
  async refreshAccessToken(refreshToken: string): Promise<{
    accessToken: string;
    refreshToken: string;
    expiresIn: number;
  }> {
    const response = await fetch(`https://${this.domain}/oauth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grant_type: 'refresh_token',
        client_id: this.clientId,
        client_secret: this.clientSecret,
        refresh_token: refreshToken,
      }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    return await response.json();
  }
}
```

### JWT Validation

```typescript
// src/lib/auth/jwt.ts
import { verify } from '@cloudflare/workers-jwt';

export async function verifyJWT(token: string, secret: string): Promise<{
  userId: string;
  tenantId: string;
  exp: number;
}> {
  try {
    const payload = await verify(token, secret, {
      algorithm: 'HS256',
      requiredClaims: ['exp', 'userId', 'tenantId'],
    });

    // Check expiration
    if (payload.exp && payload.exp < Date.now() / 1000) {
      throw new Error('Token expired');
    }

    return {
      userId: payload.userId as string,
      tenantId: payload.tenantId as string,
      exp: payload.exp as number,
    };
  } catch (error) {
    throw new Error('Invalid JWT token');
  }
}

export function generateJWT(
  userId: string,
  tenantId: string,
  secret: string,
  expiresIn: number = 3600
): string {
  const payload = {
    userId,
    tenantId,
    iat: Math.floor(Date.now() / 1000),
    exp: Math.floor(Date.now() / 1000) + expiresIn,
  };

  return sign(payload, secret, { algorithm: 'HS256' });
}
```

### User Provisioning

```typescript
// src/lib/auth/provisioning.ts
export async function createOrUpdateUser(
  env: Env,
  auth0User: { sub: string; email: string; name?: string }
): Promise<{ userId: string; tenantId: string }> {
  const auth0Id = auth0User.sub;

  // Check if user exists
  const existing = await env.DB.prepare(
    'SELECT * FROM users WHERE auth0_id = ?'
  ).bind(auth0Id).first();

  if (existing) {
    // Update last login
    await env.DB.prepare(
      'UPDATE users SET last_login_at = ? WHERE id = ?'
    ).bind(Date.now(), existing.id).run();

    return {
      userId: existing.id,
      tenantId: existing.tenant_id,
    };
  }

  // Create new tenant and user
  const tenantId = crypto.randomUUID();
  const userId = crypto.randomUUID();

  // Use batch for transaction
  await env.DB.batch([
    // Create tenant
    env.DB.prepare(`
      INSERT INTO tenants (id, name, plan, created_at, updated_at)
      VALUES (?, ?, 'free', ?, ?)
    `).bind(
      tenantId,
      auth0User.email?.split('@')[0] || 'user',
      Date.now(),
      Date.now()
    ),
    // Create user
    env.DB.prepare(`
      INSERT INTO users (id, tenant_id, email, name, auth0_id, created_at, last_login_at)
      VALUES (?, ?, ?, ?, ?, ?, ?)
    `).bind(
      userId,
      tenantId,
      auth0User.email,
      auth0User.name,
      auth0Id,
      Date.now(),
      Date.now()
    ),
  ]);

  return { userId, tenantId };
}
```

## OAuth Flow Handler

```typescript
// In your Worker class
async fetch(request: Request): Promise<Response> {
  const url = new URL(request.url);

  // Handle OAuth callback
  if (url.pathname === '/oauth/callback') {
    return this.handleOAuthCallback(request);
  }

  // Handle MCP requests
  return new ProxyToSelf(this).fetch(request);
}

private async handleOAuthCallback(request: Request): Promise<Response> {
  const url = new URL(request.url);
  const code = url.searchParams.get('code');
  const state = url.searchParams.get('state');

  if (!code) {
    return new Response('Missing authorization code', { status: 400 });
  }

  // Exchange code for token
  const auth0 = new Auth0Client(this.env);
  const tokens = await auth0.exchangeCodeForToken(code);
  const userInfo = await auth0.getUserInfo(tokens.accessToken);

  // Create or update user
  const { userId, tenantId } = await createOrUpdateUser(this.env, userInfo);

  // Generate JWT
  const jwt = generateJWT(userId, tenantId, this.env.JWT_SECRET);

  // Return token to client
  return Response.json({
    access_token: jwt,
    refresh_token: tokens.refreshToken,
    expires_in: tokens.expiresIn,
  });
}
```

## Authentication Middleware

```typescript
// src/middleware/auth.ts
export async function withAuth(
  request: Request,
  env: Env
): Promise<{ userId: string; tenantId: string }> {
  const authHeader = request.headers.get('Authorization');
  const token = authHeader?.replace('Bearer ', '');

  if (!token) {
    throw new Error('Authentication required');
  }

  const payload = await verifyJWT(token, env.JWT_SECRET);
  return {
    userId: payload.userId,
    tenantId: payload.tenantId,
  };
}
```

## Best Practices

1. **Use PKCE**: Always use Proof Key for Code Exchange for public clients
2. **Short-Lived Tokens**: Keep access tokens valid for 1 hour or less
3. **Refresh Token Rotation**: Implement refresh token rotation for security
4. **State Parameter**: Use and verify state parameter to prevent CSRF
5. **Token Storage**: Store tokens securely (httpOnly cookies or secure storage)
6. **Rate Limiting**: Rate limit OAuth endpoints to prevent abuse

## Claude Desktop Configuration

After OAuth flow, users configure Claude Desktop with the JWT:

```json
{
  "mcpServers": {
    "your-server": {
      "url": "https://your-worker.workers.dev",
      "headers": {
        "Authorization": "Bearer YOUR_JWT_TOKEN"
      }
    }
  }
}
```

## Troubleshooting

### Common Errors

1. **"Invalid grant"**: Check redirect URI matches exactly in Auth0
2. **"Token expired"**: Implement refresh token flow
3. **"Invalid JWT"**: Verify JWT_SECRET matches between signing and verification
4. **"User not found"**: Ensure user provisioning runs after OAuth callback

### Debug Logging

```typescript
console.log(JSON.stringify({
  type: 'oauth_flow',
  event: 'callback',
  auth0Id: userInfo.sub,
  userId,
  tenantId,
  timestamp: Date.now(),
}));
```
