# REST API Best Practices

## URL Structure
- Use plural nouns: /api/users, /api/orders
- Avoid verbs in URLs
- Prefer shallow nesting

## Methods and Status Codes
- GET: 200
- POST: 201
- PUT/PATCH: 200
- DELETE: 204
- 400/401/403/404/409/422/429/500 as appropriate

## Pagination
- Offset or cursor-based; define defaults and max page size
- Include metadata (total, page, page_size, pages) or cursor info

## Filtering, Sorting, Searching
- filter params: status=active
- sort params: sort=created_at or sort=-created_at
- search params: search=term
- sparse fields: fields=id,name

## Versioning
- Prefer URL versioning: /api/v1/...
- Document deprecation policy

## Errors
- Consistent error schema with code, message, details, timestamp, path

## Auth
- Bearer tokens or API keys
- 401 missing/invalid, 403 insufficient permissions

## Rate Limiting
- X-RateLimit-* headers and Retry-After

## Caching
- Cache-Control and ETag for conditional requests

## Health
- /health and optional /health/detailed
