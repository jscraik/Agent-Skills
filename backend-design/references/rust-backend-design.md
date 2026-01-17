# Rust backend design reference

## Scope
Use when the backend service is implemented in Rust or uses a Rust command layer.

## Service structure
- Prefer explicit module boundaries (api, domain, persistence, services).
- Keep data models separate from transport DTOs.
- Define error types per layer and map them at boundaries.

## API contracts
- Use OpenAPI or equivalent for REST; ensure JSON Schema 2020-12 compatibility.
- Enforce stable error codes and consistent pagination patterns.
- Prefer explicit versioning and deprecation policies.

## Data safety
- Validate all external inputs at the boundary.
- Avoid unsafe deserialization defaults; reject unknown fields when possible.
- Keep secrets out of logs; use structured logging with redaction.

## Concurrency and performance
- Use async runtimes responsibly; avoid blocking the runtime for CPU-bound work.
- Offload heavy work to background jobs where appropriate.
- Document backpressure, retry, and timeout policies.

## Security baseline
- Apply least privilege in database and service credentials.
- Use mTLS or signed tokens for service-to-service auth when needed.
- Include rate limiting and abuse prevention strategies.

## Testing
- Unit test domain logic and input validation.
- Add integration tests for data storage and API boundaries.
- Include contract tests for clients where applicable.
