# Technical Spec Checklist (Quality Gate)

> Rule: If a section is not applicable, mark it `N/A` and explain why in 1–2 lines.

## 1) Overview / Context
- [ ] Problem/context is clear and tied to PRD
- [ ] Constraints are listed (integrations, compliance, ops)
- [ ] Glossary exists if terms are ambiguous

## 2) Goals / Non-Goals
- [ ] Goals are specific and testable
- [ ] Non-goals are explicit
- [ ] “Success criteria (engineering)” exists

## 3) System Architecture
- [ ] Architecture diagram exists (Mermaid preferred)
- [ ] Major decisions have rationale + alternatives + tradeoffs
- [ ] Data flow and trust boundaries are clear (where sensitive data goes)

## 4) Component Design
- [ ] Component inventory includes planned/current/future
- [ ] Each component has responsibilities, inputs, outputs, dependencies
- [ ] Failure modes and recovery documented for each critical component
- [ ] Scaling notes exist for any component on the hot path

## 5) State Machines (Required for Stateful Components)
- [ ] Every stateful component has a Mermaid `stateDiagram-v2`
- [ ] Transitions include triggers/conditions
- [ ] Failure, timeout, retry, cancel states included where applicable
- [ ] Invariants noted for critical states (what must always be true)

## 6) API Design
- [ ] Endpoints list is complete
- [ ] Each endpoint has request schema and response schema
- [ ] Error behavior is enumerated (status + meaning)
- [ ] AuthN/AuthZ is specified (including scopes/roles)
- [ ] Idempotency strategy exists where needed

## 7) Data Models
- [ ] Entities/relationships are clear (ER diagram if relational)
- [ ] Field types, constraints, and defaults defined
- [ ] Indexes defined for key queries
- [ ] Retention and PII classification documented
- [ ] Migration plan exists if schema changes are involved

## 8) Security
- [ ] Authentication and authorization are addressed
- [ ] Encryption in transit and at rest addressed (as applicable)
- [ ] Input validation strategy defined
- [ ] Secrets management described
- [ ] Top threats listed with mitigations

## 9) Error Handling / Reliability
- [ ] Timeouts are defined for dependency calls
- [ ] Retry policy defined (limits + backoff)
- [ ] Idempotency considered
- [ ] Degraded mode behavior defined
- [ ] User-facing error mapping defined (if applicable)

## 10) Performance / SLAs (or SLOs)
- [ ] Targets are numeric (latency, throughput, availability)
- [ ] Measurement method specified
- [ ] Capacity assumptions stated (now and 12–24 months)
- [ ] SLOs + error budget window + burn policy documented (or N/A with reason)

## 11) Observability
- [ ] Logging fields defined (IDs, component, latency, error codes)
- [ ] Core metrics listed (counters, histograms, gauges)
- [ ] Dashboards referenced or planned
- [ ] Alerts defined with thresholds and response

## 12) Testing
- [ ] Unit + integration + E2E scope defined
- [ ] Load testing plan exists where performance matters
- [ ] Security testing plan exists (deps/SAST/etc)
- [ ] Test data strategy exists

## 13) Deployment / Rollout
- [ ] Deployment steps are repeatable
- [ ] Rollout strategy defined (canary/phased/flags)
- [ ] Rollback strategy defined (triggers + steps)
- [ ] Post-deploy verification steps defined

## 14) Open Questions / Future Considerations
- [ ] Open questions have owner + due date
- [ ] Known future considerations captured

## 15) Diagram Hygiene (Recommended)
- [ ] Mermaid diagrams compile and render
- [ ] If PNG/SVG required, rendering pipeline exists (mmdc)
