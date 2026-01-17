# workers-mcp SDK Reference

The `workers-mcp` SDK provides zero-boilerplate MCP protocol implementation for Cloudflare Workers using the **ProxyToSelf pattern**.

## Installation

```bash
npm install workers-mcp
```

## Core Pattern: ProxyToSelf

Instead of manually registering tools, resources, and prompts, you simply export public methods from your Worker class. The SDK automatically discovers and exposes them as MCP tools.

```typescript
import { ProxyToSelf } from 'workers-mcp';

export default class MyMCPServer extends WorkerEntrypoint<Env> {
  // This becomes an MCP tool automatically!
  async myTool(input: { arg1: string }): Promise<{ result: string }> {
    return { result: `processed: ${input.arg1}` };
  }

  async fetch(request: Request): Promise<Response> {
    // ProxyToSelf routes MCP requests to your methods
    return new ProxyToSelf(this).fetch(request);
  }
}
```

## Tool Definition Patterns

### Basic Tool

```typescript
async simpleTool(input: { query: string }): Promise<{ results: any[] }> {
  return { results: [] };
}
```

### Licensed Tool (Pro Feature)

```typescript
async proFeature(input: { data: string }): Promise<{ enhanced: any }> {
  const license = await this.license.verify(this.env, userId);
  if (!license.hasFeature('proFeature')) {
    throw new Error('proFeature requires Pro subscription');
  }
  return { enhanced: processData(data) };
}
```

### Tool with Rate Limiting

```typescript
async rateLimitedTool(input: { query: string }): Promise<any> {
  const userId = await this.getUserId();
  const rateLimit = await this.rateLimiter.check(
    this.env.RATE_LIMITS,
    `tool:${userId}`,
    100, // 100 requests
    60000 // per minute
  );
  if (!rateLimit.allowed) {
    throw new Error(`Rate limit exceeded. Retry in ${rateLimit.retryAfter}s`);
  }
  return await processQuery(query);
}
```

## Resources Pattern

Expose read-only data as MCP resources:

```typescript
// Resource: memories:///all
async getAllMemoriesResource(): Promise<string> {
  const userId = await this.getUserId();
  const tenantId = await this.getTenantId(userId);
  const memories = await this.env.DB.prepare(
    'SELECT * FROM memories WHERE tenant_id = ?'
  ).bind(tenantId).all();
  return JSON.stringify(memories.results);
}
```

Resource naming convention:
- Method suffix: `Resource`
- Return type: `string` (JSON or text)

## Environment Interface

```typescript
interface Env {
  // D1 Database
  DB: D1Database;

  // Workers KV
  CACHE: KVNamespace;
  RATE_LIMITS: KVNamespace;

  // R2 Storage
  R2: R2Bucket;

  // Durable Objects
  EMBEDDING_DO: DurableObjectNamespace;

  // Vectorize
  VECTORIZE_INDEX: VectorizeIndex;

  // External APIs (secrets)
  OPENAI_API_KEY: string;
  STRIPE_SECRET_KEY: string;
  AUTH0_CLIENT_SECRET: string;

  // Environment variables
  ENVIRONMENT: 'development' | 'production';
  BASE_URL: string;
}
```

## Helper Methods

Common patterns extracted from Local Memory specification:

```typescript
private async getUserId(): Promise<string> {
  const authHeader = this.request?.headers?.get('Authorization');
  const token = authHeader?.replace('Bearer ', '');
  if (!token) throw new Error('Authentication required');
  const payload = await this.verifyJWT(token);
  return payload.userId;
}

private async getTenantId(userId: string): Promise<string> {
  const stmt = this.env.DB.prepare('SELECT tenant_id FROM users WHERE id = ?');
  const result = await stmt.bind(userId).first();
  if (!result) throw new Error('User not found');
  return result.tenant_id;
}
```

## Streaming HTTP (Optional)

For long-running operations, use streaming responses:

```typescript
async streamData(input: { query: string }): Promise<Response> {
  const stream = new ReadableStream({
    async start(controller) {
      for await (const chunk of fetchChunks(query)) {
        controller.enqueue(new TextEncoder().encode(chunk));
      }
      controller.close();
    }
  });
  return new Response(stream);
}
```

## Best Practices

1. **Input Validation**: Always validate inputs and provide clear error messages
2. **Rate Limiting**: Check rate limits before expensive operations
3. **License Checks**: Verify feature access before executing paid features
4. **Error Handling**: Use try-catch with structured error responses
5. **Logging**: Use structured logging with MCPObserver
6. **Caching**: Use KV cache for frequently accessed data

## Transport Configuration

workers-mcp supports multiple transports:

- **stdio** (default): For local development and Claude Desktop
- **streamable HTTP**: For remote deployment with automatic streaming
- **SSE** (legacy): Backward compatibility only

Configure in `wrangler.toml`:

```toml
[vars]
MCP_TRANSPORT = "streamable-http"  # Recommended for production
```

## Testing

Use MCP Inspector for local testing:

```bash
npx @modelcontextprotocol/inspector wrangler dev
```

For remote testing:

```bash
npx @modelcontextprotocol/inspector https://your-worker.workers.dev
```
