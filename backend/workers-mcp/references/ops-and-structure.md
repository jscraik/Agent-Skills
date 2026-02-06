# Ops, testing, and file structure

## Testing

### Local Development
```bash
# Start dev server
wrangler dev

# Test with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8787
```

### Remote Testing
```bash
# Test deployed worker
npx @modelcontextprotocol/inspector https://your-worker.workers.dev
```

### Unit Tests
```typescript
import { describe, it, expect } from 'vitest';

describe('MyMCPServer', () => {
  it('should remember a memory', async () => {
    const server = new MyMCPServer(mockState, mockEnv);
    const result = await server.remember({ content: 'Test' });
    expect(result.id).toBeDefined();
  });
});
```

## Troubleshooting

### Common Errors

1. **"Invalid JWT"**: Verify `JWT_SECRET` matches between signing and verification
2. **"Tenant not found"**: Ensure user provisioning runs after OAuth callback
3. **"Rate limit exceeded"**: Check KV namespace is bound correctly
4. **"D1 error"**: Run migrations with `wrangler d1 execute DB --file=migrations/...`

### Debug Logging

```typescript
console.log(JSON.stringify({
  type: 'mcp_tool_execution',
  tool: 'remember',
  userId,
  tenantId,
  timestamp: Date.now(),
}));
```

## File Structure

```
PROJECT_NAME/
├── src/
│   ├── workers/mcp/
│   │   └── index.ts              # Main Worker with ProxyToSelf
│   ├── durable-objects/
│   │   └── embedding-do.ts       # Embedding generation DO
│   ├── lib/
│   │   ├── db/d1.ts              # D1 client wrapper
│   │   ├── kv/cache.ts           # KV cache wrapper
│   │   ├── auth/auth0.ts         # Auth0 integration
│   │   ├── license/verifier.ts   # License verification
│   │   └── embeddings/openai.ts  # OpenAI embeddings
│   └── middleware/auth.ts        # Auth middleware
├── migrations/
│   └── 001_initial.sql           # D1 schema
├── wrangler.toml                 # Workers config
├── package.json
└── tsconfig.json
```
