# Rate Limit and Quota Templates

## REST (per user/org)
- Limit: 600 requests/minute
- Burst: 60
- Headers:
  - X-RateLimit-Limit
  - X-RateLimit-Remaining
  - X-RateLimit-Reset
  - Retry-After (on 429)

## GraphQL
- Limit by complexity budget (e.g., 10,000 points/minute)
- Depth limit (e.g., 8)
- Persisted queries for high-traffic operations

## MCP Tools
- Limit: 120 tool calls/minute per workspace
- Burst: 20
- Retry-After on 429
- Enforce per-tool and per-tenant quotas
