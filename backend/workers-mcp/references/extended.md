# Extended guidance

### Post-Deployment
- [ ] Test health endpoint: `curl https://your-worker.workers.dev/health`
- [ ] Test with MCP Inspector: `npx @modelcontextprotocol/inspector https://your-worker.workers.dev`
- [ ] Verify OAuth flow in Auth0 dashboard
- [ ] Test Stripe webhook delivery

---

## Common Patterns

### Rate Limiting

```typescript
const rateLimit = await this.rateLimiter.check(
  this.env.RATE_LIMITS,
  `tool:${userId}`,
  100,  // 100 requests
  60000 // per minute
);
if (!rateLimit.allowed) {
  throw new Error(`Rate limit exceeded. Retry in ${rateLimit.retryAfter}s`);
}
```

### Caching with KV

```typescript
// Check cache
const cached = await this.env.CACHE.get(`key:${id}`, 'json');
if (cached) return cached;

// Generate data
const data = await expensiveOperation();

// Cache for 5 minutes
await this.env.CACHE.put(`key:${id}`, JSON.stringify(data), {
  expirationTtl: 300,
});
```

### Batch Operations (D1 Transactions)

```typescript
await this.env.DB.batch([
  this.env.DB.prepare('INSERT INTO memories ...'),
  this.env.DB.prepare('UPDATE tenants SET memory_count = ...')
]);
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `ENVIRONMENT` | `development` \| `staging` \| `production` |
| `BASE_URL` | Base URL for OAuth callbacks |
| `AUTH0_DOMAIN` | Your Auth0 domain |
| `AUTH0_CLIENT_ID` | Auth0 client ID |
| `STRIPE_PRO_PRICE_ID` | Stripe Pro price ID |
| `OPENAI_EMBEDDING_MODEL` | Default: `text-embedding-3-small` |

## Secrets

| Secret | Purpose |
|--------|---------|
| `OPENAI_API_KEY` | OpenAI embeddings |
| `STRIPE_SECRET_KEY` | Stripe API |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook verification |
| `AUTH0_CLIENT_SECRET` | Auth0 OAuth |
| `JWT_SECRET` | JWT signing |

---

## Claude Desktop Configuration

After OAuth flow, users configure Claude Desktop:

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

---

## Philosophy

1. **Simplicity First**: Use workers-mcp SDK to avoid boilerplate
2. **Security by Default**: All tools require authentication by default
3. **Tenant Isolation**: All data scoped to tenant with cascade deletes
4. **Graceful Degradation**: Soft deletes preserve data, downgrade preserves read access
5. **Observability**: Structured logging for all operations

## Anti-patterns
- Shipping tools without auth/tenant isolation defaults.
- Logging secrets or embedding API keys in code/config.
- Skipping schema validation or consistent error envelopes for tools/resources.

## Ops and testing

See `references/ops-and-structure.md` for testing commands, troubleshooting, and file structure.

---

## Philosophy
- Prefer clarity, explicit tradeoffs, and verifiable outputs.

## Anti-patterns
- Inventing results or skipping validation steps.
- Proceeding without required inputs or scope confirmation.

