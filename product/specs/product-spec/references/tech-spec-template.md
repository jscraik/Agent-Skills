# Technical Specification Template (RNIA = required unless not applicable—if N/A, state why in 1–2 lines)

## Overview / Context
- Summary, goals, non-goals, constraints; link to PRD if applicable.

## System Architecture
- Diagram (Mermaid/PlantUML) showing components, data stores, external services, trust boundaries.
- Rationale for chosen architecture and alternatives considered.

## Component Design
- Per component: responsibility, inputs/outputs, failure modes.
- “Component Behavior / State Model” subsection with Mermaid state diagrams for stateful components/workflows (≥3 states); use flow/sequence diagrams for stateless flows.

## API Design
- For each endpoint: method, path, purpose, request schema, response schema, error codes, auth requirements, idempotency, rate limits.
- Include versioning strategy and backward compatibility.

## Data Models / Database Schema
- Entities with fields, types, constraints, indexes, relationships; migration notes.

## Infrastructure Requirements
- Hosting/runtime, networking, storage, queues, CDN, secrets management, environment separation.

## Security Considerations
- AuthN/Z model, encryption (in transit/at rest), input validation, logging redaction, threat modeling notes.

## Error Handling Strategy
- Expected errors, retries/backoff, circuit breakers, fallbacks; user-facing vs internal errors.

## Performance Requirements / SLAs
- Latency, throughput, availability targets; capacity assumptions and sizing; caching strategy.

## Observability
- Logging, metrics (with names/units), traces; alert policies and runbooks.

## Testing Strategy
- Unit, integration, contract, load/perf, security, chaos/failure injection; test data strategy.

## Deployment Strategy
- CI/CD steps, feature flags, rollout/rollback plan, environment promotion, smoke tests.
- Runbook notes: ops contacts, dashboards, common failure signals, manual fallback steps.

## Migration Plan (if applicable)
- Data backfill, dual-write/read, cutover, rollback.

## Open Questions / Future Considerations
- Known gaps, phased improvements, experiments.

## Visuals
- Required: architecture diagram.  
- Required for stateful components: state diagrams.  
- Optional: sequence diagrams for key flows; deployment topology.

## Diagram Rendering Plan (if needed)
- If distribution requires images/PDF, render Mermaid via `mermaid-cli` (mmdc) or Kroki and store outputs (e.g., `docs/assets/diagrams/*.png`). Specify input/output paths.
