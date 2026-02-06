---
name: workers-mcp
description: Create production-ready MCP servers on Cloudflare Workers with:. Use
  when Use this skill when the task matches its description and triggers..
metadata:
  short-description: Create production-ready MCP servers on Cloudflare Workers with:.
---
# Workers MCP
Avoid skipping validation steps or inventing results.
Principle: Favor clarity, explicit tradeoffs, and verifiable outputs.


## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview

Create production-ready MCP servers on Cloudflare Workers with:
- **workers-mcp SDK** for zero-boilerplate MCP protocol
- **Auth0** for OAuth 2.1 authentication
- **Stripe** for subscription licensing
- **D1** for SQLite database
- **Durable Objects** for stateful operations
- **Vectorize** for semantic vector search

---

## Quick Start

### Scaffold New Project

```bash
cd /path/to/skill/assets
# Replace PROJECT_NAME with actual name
sed 's/PROJECT_NAME/my-server/g' wrangler.template.toml > ../../wrangler.toml
```

Then create project structure:
```bash
mkdir -p src/{workers/mcp,durable-objects,lib/{db,kv,auth,license,embeddings,monitoring,types},middleware}
mkdir -p migrations tests/{unit,integration,contract}
```

### Core Dependencies

```json
{
  "dependencies": {
    "workers-mcp": "^1.0.0",
    "@cloudflare/workers-types": "^4.20241218.0",
    "stripe": "^17.0.0"
  },
  "devDependencies": {
    "wrangler": "^3.0.0",
    "typescript": "^5.0.0",
    "vitest": "^2.0.0"
  }
}
```

### Minimal Worker Entry Point

```typescript
// src/workers/mcp/index.ts
import { ProxyToSelf } from 'workers-mcp';

export default class MyMCPServer extends WorkerEntrypoint<Env> {
  // This becomes an MCP tool automatically!
  async hello(input: { name: string }): Promise<{ message: string }> {
    return { message: `Hello, ${input.name}!` };
  }

  async fetch(request: Request): Promise<Response> {
    return new ProxyToSelf(this).fetch(request);
  }
}
```

---

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│              CLOUDFLARE EDGE (300+ PoPs)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │     WORKERS MCP SERVER (workers-mcp SDK)            │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  ProxyToSelf Pattern                           │  │  │
│  │  │  ├─ free_tool()     [FREE]                     │  │  │
│  │  │  ├─ another_free()   [FREE]                     │  │  │
│  │  │  └─ pro_feature()    [PRO LICENSED]             │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └───────────────────────────┬──────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────┘
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  Workers KV    │  │ Durable Objects│  │ D1 Database    │
│  (Cache/Auth)  │  │ (Stateful)     │  │ (SQLite)       │
└────────────────┘  │ • Embeddings   │  │ • Memories     │
                   │ • Sessions     │  │ • Tenants      │
                   └────────────────┘  │ • Users        │
         │                     │        └────────────────┘
         ▼                     ▼
┌────────────────┐  ┌────────────────┐
│  R2 Storage    │  │ External APIs  │
│  (Data export) │  │ • OpenAI       │
│                │  │ • Auth0        │
│                │  │ • Stripe       │
│                │  │ • Vectorize    │
└────────────────┘  └────────────────┘
```

---

## MCP Tool Pattern

### Free Tool (No License Required)

```typescript
async recall(
  input: { query: string; limit?: number }
): Promise<{ memories: any[]; total: number }> {
  const userId = await this.getUserId();
  const tenantId = await this.getTenantId(userId);

  const stmt = this.env.DB.prepare(`
    SELECT * FROM memories
    WHERE tenant_id = ? AND deleted_at IS NULL
    AND content LIKE ?
    LIMIT ?
  `);

  const result = await stmt.bind(
    tenantId,
    `%${input.query}%`,
    input.limit || 10
  ).all();

  return { memories: result.results, total: result.results.length };
}
```

### Licensed Tool (Pro Feature)

```typescript
async semanticSearch(
  input: { query: string; limit?: number }
): Promise<{ memories: any[]; total: number }> {
  const userId = await this.getUserId();
  const license = await this.license.verify(this.env, userId);

  // Check license
  if (!this.license.hasFeature(license, 'semantic_search')) {
    throw new Error(
      'semantic_search requires Pro subscription. ' +
      'Upgrade at https://app.yourdomain.com/upgrade'
    );
  }

  // Execute feature...
  return { memories: [], total: 0 };
}
```

### Helper Methods

```typescript
private async getUserId(): Promise<string> {
  const authHeader = this.request?.headers?.get('Authorization');
  const token = authHeader?.replace('Bearer ', '');
  if (!token) throw new Error('Authentication required');
  const payload = await this.verifyJWT(token);
  return payload.userId;
}

private async getTenantId(userId: string): Promise<string> {
  const stmt = this.env.DB.prepare(
    'SELECT tenant_id FROM users WHERE id = ?'
  );
  const result = await stmt.bind(userId).first();
  if (!result) throw new Error('User not found');
  return result.tenant_id;
}
```

---

## Resources (Load as Needed)

### workers-mcp SDK
See [references/workers-mcp-sdk.md](references/workers-mcp-sdk.md) for:
- ProxyToSelf pattern details
- Tool definition patterns
- Environment interface
- Helper methods
- Testing with MCP Inspector

**Load when:** Implementing MCP tools or configuring workers-mcp SDK

### D1 Schema Patterns
See [references/d1-schema-patterns.md](references/d1-schema-patterns.md) for:
- Tenant isolation pattern
- Soft delete pattern
- Full-text search (FTS5)
- JSON storage pattern
- Audit log pattern
- Index strategy

**Load when:** Designing D1 database schema or writing migrations

### Auth0 Integration
See [references/auth0-integration.md](references/auth0-integration.md) for:
- OAuth 2.1 flow implementation
- JWT validation
- User provisioning
- Authentication middleware
- Claude Desktop configuration

**Load when:** Setting up authentication or handling OAuth callbacks

### Stripe Licensing
See [references/stripe-licensing.md](references/stripe-licensing.md) for:
- License verifier implementation
- Stripe client for webhooks
- Subscription management
- Feature-based access control
- Upgrade flow

**Load when:** Implementing licensing or handling Stripe webhooks

### Vectorize Integration
See [references/vectorize-integration.md](references/vectorize-integration.md) for:
- Vectorize client wrapper
- Embedding generation with Durable Objects
- Tenant-namespaced vector search
- Soft delete pattern for vectors

**Load when:** Adding semantic search or managing embeddings

---

## Wrangler Configuration

Copy and customize [assets/wrangler.template.toml](assets/wrangler.template.toml):

1. Replace `PROJECT_NAME` with actual project name
2. Set `account_id` from `wrangler whoami`
3. Create D1 database: `wrangler d1 create PROJECT_NAME`
4. Create KV namespaces: `wrangler kv:namespace create CACHE`
5. Create Vectorize index: `wrangler vectorize create PROJECT_NAME-index --dimensions=1536 --metric=cosine`
6. Set secrets: `wrangler secret put OPENAI_API_KEY`

---

## Deployment Checklist

### Pre-Deployment
- [ ] Create D1 database: `wrangler d1 create <name>`
- [ ] Create KV namespaces: `wrangler kv:namespace create CACHE`
- [ ] Create R2 bucket: `wrangler r2 bucket create <name>`
- [ ] Create Vectorize index: `wrangler vectorize create <name> --dimensions=1536`
- [ ] Set all secrets: `wrangler secret put <NAME>`
- [ ] Run migrations: `wrangler d1 execute DB --file=migrations/001_initial.sql`

### Deployment
```bash
# Deploy to production
wrangler deploy

# Deploy to staging
wrangler deploy --env staging

# Test locally
wrangler dev
```

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Examples
- "Provide a concise response for this task."
- "Follow the workflow and summarize outputs."

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Scripts
- `scripts/init_workers_mcp.sh`

## Extended guidance
See `references/extended.md` for additional examples, workflows, and appendices.
