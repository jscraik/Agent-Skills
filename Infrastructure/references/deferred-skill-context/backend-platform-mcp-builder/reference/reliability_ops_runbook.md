# Reliability & Ops Runbook

Use this for production MCP servers (Apps SDK or standalone).

## SLOs and Budgets

- Define availability SLO (e.g., 99.9%)
- Define p95 latency target per tool class
- Define error budget burn alerts

## Timeouts and Retries

- Set upstream timeouts (per request)
- Use exponential backoff with jitter
- Limit retries for non-idempotent tools

## Rate Limiting and Abuse Controls

- Per-client rate limits (token or user)
- Burst limits + sustained limits
- Block repeated invalid schema calls

## Observability

- Structured logs with correlation IDs
- Trace tool calls end-to-end
- Track: latency, errors, retries, timeouts, payload sizes

## Payload Management

- Cap `structuredContent` size
- Use resource links for large data
- Enforce max response size

## Caching

- Cache read-heavy endpoints where safe
- Cache JWKS and OAuth metadata with sane TTL

## Security Ops

- Audit logs for destructive tools
- Secrets rotation policy
- Incident response runbook

## Data Retention

- Log retention and PII handling
- Clear policy for stored widget state

## Incident Response (Quick Steps)

1) Identify scope and impacted tools
2) Roll back if recent deploy
3) Disable destructive tools if needed
4) Capture logs with correlation IDs
5) Post-mortem with root cause + fix
