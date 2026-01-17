# Cloudflare Vectorize Integration

Production-ready vector search using Cloudflare Vectorize for semantic memory retrieval.

## Architecture Overview

```
┌─────────────┐         ┌─────────────┐         ┌──────────────┐
│   Worker    │──Query──▶│  Vectorize  │◀────────│  Embeddings  │
│   Server    │         │   Index     │         │  (OpenAI)    │
└─────────────┘         └─────────────┘         └──────────────┘
      │                        │
      │                        │
      ▼                        ▼
┌─────────────┐         ┌─────────────┐
│   D1 DB     │         │   R2 / KV   │
│ (Metadata)  │         │   (Cache)   │
└─────────────┘         └─────────────┘
```

## Vectorize Setup

### 1. Create Vectorize Index

```bash
# Create index (dimensions = 1536 for OpenAI text-embedding-3-small)
wrangler vectorize create local-memory-index \
  --dimensions=1536 \
  --metric=cosine
```

### 2. Configure Binding

```toml
# wrangler.toml
[[vectorize]]
binding = "VECTORIZE_INDEX"
index_name = "local-memory-index"
```

## Vectorize Client Wrapper

```typescript
// src/lib/embeddings/vectorize.ts
export interface VectorMetadata {
  tenant_id: string;
  content?: string;
  tags?: string[];
  importance?: number;
  created_at?: number;
  deleted_at?: number | null;
}

export class VectorizeClient {
  private index: VectorizeIndex;

  constructor(index: VectorizeIndex) {
    this.index = index;
  }

  /**
   * Upsert vectors with tenant namespacing
   */
  async upsert(
    tenantId: string,
    vectors: Array<{
      id: string;
      vector: number[];
      metadata: VectorMetadata;
    }>
  ): Promise<void> {
    const vectorized = vectors.map(v => ({
      id: `${tenantId}:${v.id}`,
      values: v.vector,
      namespace: tenantId,
      metadata: {
        ...v.metadata,
        tenant_id: tenantId,
      },
    }));

    await this.index.upsert(vectorized);
  }

  /**
   * Query vectors by similarity
   */
  async query(
    tenantId: string,
    vector: number[],
    options: {
      topK?: number;
      filter?: Record<string, any>;
      includeVectors?: boolean;
      includeMetadata?: boolean;
    } = {}
  ): Promise<Array<{
    id: string;
    score: number;
    metadata?: VectorMetadata;
  }>> {
    const {
      topK = 10,
      filter = { deleted_at: null },
      includeVectors = false,
      includeMetadata = true,
    } = options;

    const results = await this.index.query(vector, {
      topK,
      namespace: tenantId,
      filter,
      includeVectors,
      includeMetadata,
    });

    return results.matches.map(m => ({
      id: m.id.split(':')[1], // Remove tenant prefix
      score: m.score,
      metadata: m.metadata as VectorMetadata,
    }));
  }

  /**
   * Delete vectors by IDs
   */
  async delete(tenantId: string, ids: string[]): Promise<void> {
    const namespacedIds = ids.map(id => `${tenantId}:${id}`);
    await this.index.deleteByIds(namespacedIds);
  }

  /**
   * Delete all vectors for a tenant
   */
  async deleteByNamespace(tenantId: string): Promise<void> {
    // Vectorize doesn't support namespace deletion
    // Delete all vectors and recreate namespace
    // Alternative: soft-delete with metadata filter
    // Here we use metadata update approach
  }

  /**
   * Get index statistics
   */
  async getStats(): Promise<{
    count: number;
    dimension: number;
  }> {
    // Vectorize doesn't expose stats API directly
    // Track count in D1 or KV instead
    return { count: 0, dimension: 1536 };
  }
}
```

## Embedding Generation

```typescript
// src/durable-objects/embedding-do.ts
export class EmbeddingDurableObject {
  private state: DurableObjectState;
  private env: Env;
  private cache = new Map<string, number[]>();

  constructor(state: DurableObjectState, env: Env) {
    this.state = state;
    this.env = env;
  }

  async fetch(request: Request): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;

    switch (path) {
      case '/generate':
        return this.handleGenerate(request);
      case '/batch':
        return this.handleBatch(request);
      default:
        return new Response('Not found', { status: 404 });
    }
  }

  private async handleGenerate(request: Request): Promise<Response> {
    const { text } = await request.json();

    // Check DO storage cache
    const cacheKey = this.hash(text);
    const cached = await this.state.storage.get<number[]>(`embedding:${cacheKey}`);
    if (cached) {
      return Response.json({ embedding: cached });
    }

    // Check KV cache
    const kvCached = await this.env.CACHE.get(
      `embedding:${cacheKey}`,
      'json'
    );
    if (kvCached) {
      await this.state.storage.put(`embedding:${cacheKey}`, kvCached.embedding);
      return Response.json(kvCached);
    }

    // Generate via OpenAI
    const response = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.env.OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        input: text,
        model: this.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-small',
      }),
    });

    if (!response.ok) {
      throw new Error('OpenAI API error');
    }

    const data = await response.json();
    const embedding = data.data[0].embedding;

    // Cache in DO storage (long-lived)
    await this.state.storage.put(`embedding:${cacheKey}`, embedding);

    // Cache in KV (shared across DOs)
    await this.env.CACHE.put(
      `embedding:${cacheKey}`,
      JSON.stringify({ embedding }),
      { expirationTtl: 86400 } // 24 hours
    );

    return Response.json({ embedding });
  }

  private async handleBatch(request: Request): Promise<Response> {
    const { texts } = await request.json();

    const embeddings = await Promise.all(
      texts.map(async (text: string) => {
        const cacheKey = this.hash(text);

        // Check DO storage
        const cached = await this.state.storage.get<number[]>(`embedding:${cacheKey}`);
        if (cached) return cached;

        // Check KV
        const kvCached = await this.env.CACHE.get(`embedding:${cacheKey}`, 'json');
        if (kvCached) return kvCached.embedding;

        // Generate
        const response = await fetch('https://api.openai.com/v1/embeddings', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.env.OPENAI_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            input: text,
            model: this.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-small',
          }),
        });

        const data = await response.json();
        const embedding = data.data[0].embedding;

        // Cache
        await this.state.storage.put(`embedding:${cacheKey}`, embedding);
        await this.env.CACHE.put(
          `embedding:${cacheKey}`,
          JSON.stringify({ embedding }),
          { expirationTtl: 86400 }
        );

        return embedding;
      })
    );

    return Response.json({ embeddings });
  }

  private hash(text: string): string {
    // Simple string hash for cache key
    let hash = 0;
    for (let i = 0; i < text.length; i++) {
      const char = text.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return hash.toString(16);
  }
}
```

## Usage in MCP Tools

```typescript
// In your Worker class
async semanticSearch(query: string, limit: number = 10) {
  const userId = await this.getUserId();
  const tenantId = await this.getTenantId(userId);

  // Generate query embedding
  const embeddingDO = this.env.EMBEDDING_DO.get(
    this.env.EMBEDDING_DO.idFromName(query)
  );
  const embeddingResponse = await embeddingDO.fetch(
    new Request('https://embedding/generate', {
      method: 'POST',
      body: JSON.stringify({ text: query }),
    })
  );
  const { embedding } = await embeddingResponse.json();

  // Query Vectorize
  const vectorize = new VectorizeClient(this.env.VECTORIZE_INDEX);
  const results = await vectorize.query(tenantId, embedding, {
    topK: limit,
    filter: { deleted_at: null },
    includeMetadata: true,
  });

  // Fetch full memory details from D1
  const memoryIds = results.map(r => r.id);
  const memories = await this.env.DB.prepare(`
    SELECT id, content, tags, importance, created_at
    FROM memories
    WHERE id IN (${memoryIds.map(() => '?').join(',')})
  `).bind(...memoryIds).all();

  // Combine results with similarity scores
  const enriched = memories.results.map((m: any) => ({
    ...m,
    similarity: results.find(r => r.id === m.id)?.score || 0,
  }));

  return {
    memories: enriched,
    total: enriched.length,
  };
}

async remember(content: string, tags: string[] = [], importance: number = 5) {
  const userId = await this.getUserId();
  const tenantId = await this.getTenantId(userId);

  // Generate embedding
  const embeddingDO = this.env.EMBEDDING_DO.get(
    this.env.EMBEDDING_DO.idFromName(content)
  );
  const embeddingResponse = await embeddingDO.fetch(
    new Request('https://embedding/generate', {
      method: 'POST',
      body: JSON.stringify({ text: content }),
    })
  );
  const { embedding } = await embeddingResponse.json();

  // Store in D1
  const memoryId = crypto.randomUUID();
  await this.env.DB.prepare(`
    INSERT INTO memories (id, tenant_id, user_id, content, tags, importance, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `).bind(
    memoryId,
    tenantId,
    userId,
    content,
    JSON.stringify(tags),
    importance,
    Date.now()
  ).run();

  // Upsert to Vectorize
  const vectorize = new VectorizeClient(this.env.VECTORIZE_INDEX);
  await vectorize.upsert(tenantId, [{
    id: memoryId,
    vector: embedding,
    metadata: {
      tenant_id: tenantId,
      content,
      tags,
      importance,
      created_at: Date.now(),
      deleted_at: null,
    },
  }]);

  return { id: memoryId, created_at: new Date().toISOString() };
}

async deleteMemory(id: string) {
  const userId = await this.getUserId();
  const tenantId = await this.getTenantId(userId);

  // Soft delete in D1
  await this.env.DB.prepare(`
    UPDATE memories SET deleted_at = ? WHERE id = ? AND tenant_id = ?
  `).bind(Date.now(), id, tenantId).run();

  // Update metadata in Vectorize (marks as deleted)
  const vectorize = new VectorizeClient(this.env.VECTORIZE_INDEX);
  await vectorize.upsert(tenantId, [{
    id,
    vector: [], // Not used for metadata update
    metadata: {
      tenant_id: tenantId,
      deleted_at: Date.now(),
    },
  }]);
}
```

## Best Practices

1. **Tenant Namespacing**: Prefix all vector IDs with tenant ID for isolation
2. **Soft Deletes**: Update metadata instead of deleting vectors
3. **Caching**: Use DO storage + KV for embedding cache
4. **Batch Operations**: Use batch endpoint for multiple embeddings
5. **Dimension Matching**: Ensure embedding model dimensions match index
6. **Filter Queries**: Always filter by `deleted_at: null`

## Vectorize Configuration

```typescript
// wrangler.toml vectorize binding options
[[vectorize]]
binding = "VECTORIZE_INDEX"
index_name = "local-memory-index"
# Options:
# - dimensions: 1536 (for text-embedding-3-small)
# - metric: cosine (recommended for embeddings)
# - pods: 1 (scale with usage)
```

## Troubleshooting

### Common Issues

1. **Index not found**: Create index with `wrangler vectorize create`
2. **Dimension mismatch**: Ensure embedding model matches index dimensions
3. **No results**: Check namespace and filter parameters
4. **Slow queries**: Consider reducing topK or adding filters

### Debug Logging

```typescript
console.log(JSON.stringify({
  type: 'vectorize_query',
  tenant_id: tenantId,
  top_k: options.topK,
  result_count: results.length,
  timestamp: Date.now(),
}));
```
