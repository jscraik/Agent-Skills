# D1 Database Schema Patterns

Cloudflare D1 is SQLite-based. Use these patterns for production-ready schemas.

## Core Schema Patterns

### Tenant Isolation Pattern

Multi-tenant data isolation with cascade deletes:

```sql
CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL CHECK(plan IN ('free', 'pro', 'team')),
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER
);

CREATE TABLE users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    auth0_id TEXT UNIQUE,
    created_at INTEGER NOT NULL,
    deleted_at INTEGER
);

CREATE TABLE data_items (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL,
    deleted_at INTEGER
);
```

### Soft Delete Pattern

Preserve data with `deleted_at` timestamps:

```sql
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    deleted_at INTEGER  -- NULL = active, timestamp = deleted
);

-- Query only active items
SELECT * FROM items WHERE deleted_at IS NULL;

-- Soft delete
UPDATE items SET deleted_at = ? WHERE id = ?;
```

### Full-Text Search Pattern (FTS5)

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    created_at INTEGER NOT NULL
);

-- Create FTS5 virtual table
CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    content=memories,
    content_rowid=rowid
);

-- Triggers to keep FTS in sync
CREATE TRIGGER memories_fts_insert AFTER INSERT ON memories BEGIN
  INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
END;

CREATE TRIGGER memories_fts_delete AFTER DELETE ON memories BEGIN
  INSERT INTO memories_fts(memories_fts, rowid, content) VALUES ('delete', old.rowid, old.content);
END;

CREATE TRIGGER memories_fts_update AFTER UPDATE ON memories BEGIN
  INSERT INTO memories_fts(memories_fts, rowid, content) VALUES ('delete', old.rowid, old.content);
  INSERT INTO memories_fts(rowid, content) VALUES (new.rowid, new.content);
END;

-- Query with FTS
SELECT * FROM memories
WHERE id IN (SELECT rowid FROM memories_fts WHERE content MATCH ?)
AND deleted_at IS NULL;
```

### JSON Storage Pattern

Store structured data as JSON in TEXT columns:

```sql
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    tags TEXT NOT NULL DEFAULT '[]',      -- JSON array
    metadata TEXT,                         -- JSON object
    embedding TEXT                         -- JSON array (for storage)
);

-- Query tags (SQLite JSON operators)
SELECT * FROM memories
WHERE tags LIKE '%"important"%';

-- Update tags
UPDATE memories
SET tags = json_array(tags, 'new-tag')
WHERE id = ?;
```

### Audit Log Pattern

Track all data changes:

```sql
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,                  -- 'create', 'update', 'delete'
    resource_type TEXT NOT NULL,           -- 'memory', 'user', etc.
    resource_id TEXT,
    old_values TEXT,                       -- JSON object
    new_values TEXT,                       -- JSON object
    ip_address TEXT,
    user_agent TEXT,
    created_at INTEGER NOT NULL
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
```

### Session Management Pattern

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mcp_client_id TEXT,
    connected_at INTEGER NOT NULL,
    last_activity_at INTEGER NOT NULL,
    metadata TEXT,                         -- JSON object
    expired_at INTEGER
);

CREATE INDEX idx_sessions_tenant ON sessions(tenant_id);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expired ON sessions(expired_at);
```

## Index Strategy

Create indexes on:
- Foreign keys (`tenant_id`, `user_id`)
- Query columns (`created_at DESC` for sorting)
- Filter columns (`deleted_at` for soft deletes)
- Search columns (composite indexes for common queries)

```sql
-- Common query: WHERE tenant_id = ? AND deleted_at IS NULL ORDER BY created_at DESC
CREATE INDEX idx_memories_tenant_created ON memories(tenant_id, created_at DESC);
CREATE INDEX idx_memories_deleted ON memories(deleted_at);

-- Join optimization
CREATE INDEX idx_users_tenant ON users(tenant_id);
```

## Constraint Patterns

### CHECK Constraints

```sql
-- Enum values
CHECK(plan IN ('free', 'pro', 'team'))

-- Numeric ranges
CHECK(importance BETWEEN 1 AND 10)

-- Conditional logic
CHECK(
    (access_scope = 'private' AND user_id IS NOT NULL) OR
    (access_scope IN ('session', 'global'))
)
```

### UNIQUE Constraints

```sql
-- Single column
UNIQUE(email)

-- Composite (tenant-scoped uniqueness)
UNIQUE(tenant_id, name)

-- With nullable
UNIQUE(auth0_id)  -- Allows multiple NULLs
```

## Migration Pattern

Version your migrations with numbered prefixes:

```
migrations/
├── 001_initial.sql
├── 002_add_subscriptions.sql
├── 003_add_sessions.sql
└── 004_add_analytics.sql
```

Each migration should be:
- Idempotent (can run multiple times safely)
- Backward compatible (old code continues to work)
- Forward compatible (new code works with old schema)

```sql
-- Example: Add new column safely
ALTER TABLE memories ADD COLUMN source TEXT;
-- No DEFAULT needed - new column is nullable
```

## D1-Specific Considerations

1. **Write Limits**: D1 has write throughput limits. Use batch inserts for bulk operations.

2. **Foreign Keys**: D1 supports FKs but validation is in application layer. Always validate in code:

   ```typescript
   const tenant = await env.DB.prepare('SELECT id FROM tenants WHERE id = ?')
     .bind(tenantId).first();
   if (!tenant) throw new Error('Tenant not found');
   ```

3. **Transactions**: Use D1 transactions for multi-step operations:

   ```typescript
   await env.DB.batch([
     env.DB.prepare('INSERT INTO memories ...'),
     env.DB.prepare('UPDATE tenants SET memory_count = ...')
   ]);
   ```

4. **Query Limits**: D1 returns max 10,000 rows per query. Use pagination:

   ```sql
   SELECT * FROM memories
   WHERE tenant_id = ? AND deleted_at IS NULL
   ORDER BY created_at DESC
   LIMIT ? OFFSET ?;
   ```
