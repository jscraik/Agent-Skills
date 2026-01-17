# API Design Checklist

## REST Core
- Resources are nouns; plural collection names
- Consistent naming and shallow nesting (<= 2 levels)
- CRUD mapped to HTTP methods
- Status codes: 200/201/204, 400/401/403/404/409/422/429/5xx
- Pagination on collections (default + max), include metadata
- Filtering, sorting, search, and sparse fields
- Versioning strategy defined and documented
- Consistent error format with field-level details and timestamps
- AuthN/AuthZ on all endpoints; 401 vs 403 correct
- Rate limits with headers and Retry-After
- OpenAPI docs with examples
- Unit + integration tests; edge cases covered
- Security: input validation, SQLi/XSS prevention, HTTPS, CORS
- Performance: avoid N+1, cache strategy, paginated large payloads
- Monitoring: logs, metrics, traces, health checks, alerts

## GraphQL Core
- Schema-first design
- Non-null vs nullable explicit
- Use interfaces/unions where appropriate
- Relay or offset pagination chosen
- Input and payload types with error fields
- Depth/complexity limits, DataLoaders to avoid N+1
- Deprecation strategy documented
- Field-level docs and examples

Use this as a pre-implementation review checklist.
