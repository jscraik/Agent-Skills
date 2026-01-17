-- ============================================================================
-- PROJECT_NAME D1 Database Schema
-- Migration: 001_initial.sql
-- ============================================================================

-- ============================================================================
-- TENANTS
-- ============================================================================
CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    plan TEXT NOT NULL CHECK(plan IN ('free', 'pro', 'team')),
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER
);

CREATE INDEX idx_tenants_plan ON tenants(plan);

-- ============================================================================
-- USERS
-- ============================================================================
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    auth0_id TEXT UNIQUE,
    created_at INTEGER NOT NULL,
    last_login_at INTEGER,
    deleted_at INTEGER
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_auth0 ON users(auth0_id);

-- ============================================================================
-- MAIN DATA TABLE
-- ============================================================================
CREATE TABLE items (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    tags TEXT NOT NULL DEFAULT '[]',
    metadata TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL,
    deleted_at INTEGER
);

-- Full-text search
CREATE VIRTUAL TABLE items_fts USING fts5(
    content,
    content=items,
    content_rowid=rowid
);

CREATE TRIGGER items_fts_insert AFTER INSERT ON items BEGIN
  INSERT INTO items_fts(rowid, content) VALUES (new.rowid, new.content);
END;

CREATE TRIGGER items_fts_delete AFTER DELETE ON items BEGIN
  INSERT INTO items_fts(items_fts, rowid, content) VALUES ('delete', old.rowid, old.content);
END;

CREATE TRIGGER items_fts_update AFTER UPDATE ON items BEGIN
  INSERT INTO items_fts(items_fts, rowid, content) VALUES ('delete', old.rowid, old.content);
  INSERT INTO items_fts(rowid, content) VALUES (new.rowid, new.content);
END;

CREATE INDEX idx_items_tenant ON items(tenant_id);
CREATE INDEX idx_items_user ON items(user_id);
CREATE INDEX idx_items_created ON items(created_at DESC);
CREATE INDEX idx_items_deleted ON items(deleted_at);

-- ============================================================================
-- SUBSCRIPTIONS (Stripe)
-- ============================================================================
CREATE TABLE subscriptions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    stripe_subscription_id TEXT UNIQUE,
    stripe_customer_id TEXT,
    plan TEXT NOT NULL CHECK(plan IN ('free', 'pro', 'team')),
    status TEXT NOT NULL CHECK(status IN ('active', 'canceled', 'past_due')),
    current_period_start INTEGER,
    current_period_end INTEGER,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);

CREATE INDEX idx_subscriptions_tenant ON subscriptions(tenant_id);
CREATE INDEX idx_subscriptions_stripe ON subscriptions(stripe_subscription_id);

-- ============================================================================
-- SESSIONS (MCP)
-- ============================================================================
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mcp_client_id TEXT,
    connected_at INTEGER NOT NULL,
    last_activity_at INTEGER NOT NULL,
    metadata TEXT,
    expired_at INTEGER
);

CREATE INDEX idx_sessions_tenant ON sessions(tenant_id);
CREATE INDEX idx_sessions_user ON sessions(user_id);
CREATE INDEX idx_sessions_expired ON sessions(expired_at);

-- ============================================================================
-- AUDIT LOGS
-- ============================================================================
CREATE TABLE audit_logs (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id TEXT REFERENCES users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    old_values TEXT,
    new_values TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at INTEGER NOT NULL
);

CREATE INDEX idx_audit_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
