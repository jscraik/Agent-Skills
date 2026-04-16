# Technical Spec Checklist (Quality Gate)

> Rule: If a section is not applicable, mark it `N/A` and explain why in 1–2 lines.
> Evidence rule: Every paragraph must end with an `Evidence:` line or `Evidence gap:` line.

## 0) Evidence Coverage (Required)
- [ ] Every paragraph ends with `Evidence:` or `Evidence gap:`
- [ ] Evidence Gaps section lists all missing sources
- [ ] Evidence Map table lists all citations

## 1) Overview / Context
- [ ] Problem/context is clear and tied to PRD
- [ ] Constraints are listed (integrations, compliance, ops)
- [ ] Glossary exists if terms are ambiguous

## 2) Template Metadata (Required for template-driven deliverables)
- [ ] name is unique and present
- [ ] description is human-readable
- [ ] title_template includes {variable} placeholders where applicable
- [ ] acceptance_criteria list exists
- [ ] priority is set (defaults to "medium" if not specified)
- [ ] variables list exists (can be empty)
- [ ] metadata object exists (can be empty)
- [ ] template metadata exported to `<spec>.template.json`

## 3) Goals / Non-Goals
- [ ] Goals are specific and testable
- [ ] Non-goals are explicit
- [ ] “Success criteria (engineering)” exists

## 4) Scope
- [ ] In-scope list is explicit
- [ ] Out-of-scope list is explicit
- [ ] Non-goals are stated (if applicable)

## 5) Feature Creep Guardrails
- [ ] Guardrail questions answered with evidence
- [ ] Trade-offs documented for any scope additions
- [ ] 48-hour rule applied or explicitly waived with reason

## 6) Scope Decision Log
- [ ] Log exists with date, decision, rationale, and trade-off
- [ ] Agent/stakeholder requests captured

## 7) Acceptance Criteria
- [ ] Top-level acceptance criteria section exists
- [ ] Criteria are observable, testable, and not duplicates of test cases

## 8) Decision Log / ADRs
- [ ] Decision log exists with rationale, alternatives, and ADR links

## 9) Data Lifecycle & Retention
- [ ] Data created/sources documented
- [ ] Retention and deletion policies documented
- [ ] DSAR/export handling documented or N/A

## 10) System Architecture
- [ ] Architecture diagram exists (Mermaid preferred)
- [ ] Major decisions have rationale + alternatives + tradeoffs
- [ ] Data flow and trust boundaries are clear (where sensitive data goes)

## 11) Component Design
- [ ] Component inventory includes planned/current/future
- [ ] Each component has responsibilities, inputs, outputs, dependencies
- [ ] Failure modes and recovery documented for each critical component
- [ ] Scaling notes exist for any component on the hot path

## 12) State Machines (Required for Stateful Components)
- [ ] Every stateful component has a Mermaid `stateDiagram-v2`
- [ ] Transitions include triggers/conditions
- [ ] Failure, timeout, retry, cancel states included where applicable
- [ ] Invariants noted for critical states (what must always be true)

## 13) API Design
- [ ] Endpoints list is complete
- [ ] Each endpoint has request schema and response schema
- [ ] Error behavior is enumerated (status + meaning)
- [ ] AuthN/AuthZ is specified (including scopes/roles)
- [ ] Idempotency strategy exists where needed

## 14) Data Models
- [ ] Entities/relationships are clear (ER diagram if relational)
- [ ] Field types, constraints, and defaults defined
- [ ] Indexes defined for key queries
- [ ] Retention and PII classification documented
- [ ] Migration plan exists if schema changes are involved

## 15) Security
- [ ] Authentication and authorization are addressed
- [ ] Encryption in transit and at rest addressed (as applicable)
- [ ] Input validation strategy defined
- [ ] Secrets management described
- [ ] Top threats listed with mitigations

## 16) Error Handling / Reliability
- [ ] Timeouts are defined for dependency calls
- [ ] Retry policy defined (limits + backoff)
- [ ] Idempotency considered
- [ ] Degraded mode behavior defined
- [ ] User-facing error mapping defined (if applicable)

## 17) Performance / SLAs (or SLOs)
- [ ] Targets are numeric (latency, throughput, availability)
- [ ] Measurement method specified
- [ ] Capacity assumptions stated (now and 12–24 months)
- [ ] SLOs + error budget window + burn policy documented (or N/A with reason)

## 18) Observability
- [ ] Logging fields defined (IDs, component, latency, error codes)
- [ ] Core metrics listed (counters, histograms, gauges)
- [ ] Dashboards referenced or planned
- [ ] Alerts defined with thresholds and response

## 19) Testing
- [ ] Unit + integration + E2E scope defined
- [ ] Load testing plan exists where performance matters
- [ ] Security testing plan exists (deps/SAST/etc)
- [ ] Test data strategy exists

## 20) Deployment / Rollout
- [ ] Deployment steps are repeatable
- [ ] Rollout strategy defined (canary/phased/flags)
- [ ] Rollback strategy defined (triggers + steps)
- [ ] Post-deploy verification steps defined

## 21) Launch & Rollback Guardrails
- [ ] Go/No-Go metrics are defined
- [ ] Rollback triggers and owners are defined
- [ ] Post-deploy verification steps are listed

## 22) Post-Launch Monitoring Plan
- [ ] Monitoring window is defined
- [ ] Dashboards and owners are listed
- [ ] Alert thresholds are specified

## 23) Support / Ops Impact
- [ ] Runbook links are included
- [ ] Escalation path and manual ops are documented

## 24) Compliance & Regulatory Review Triggers
- [ ] Triggers are listed
- [ ] Required reviews and status are documented

## 25) Ownership & RACI
- [ ] RACI table exists with accountable owners
- [ ] Security/Privacy and Support/Ops ownership included

## 26) Security & Privacy Classification
- [ ] Data sensitivity tier stated
- [ ] PII/PHI/PCI presence documented
- [ ] Required controls listed

## 27) Dependency SLAs & Vendor Risk
- [ ] Third-party dependencies listed
- [ ] SLA/SLO expectations captured
- [ ] Vendor-down fallback documented

## 28) Cost Model & Budget Guardrails
- [ ] Cost drivers listed
- [ ] Budget cap defined
- [ ] Cost alerts and owners defined

## 29) Localization & Internationalization
- [ ] Locales in scope documented or N/A
- [ ] Translation workflow documented
- [ ] Formatting rules documented where relevant

## 30) Backward Compatibility & Deprecation
- [ ] Compatibility constraints documented
- [ ] Deprecation plan and comms documented
- [ ] Migration aids documented

## 31) Experimentation & Feature Flags
- [ ] Experiment plan documented (if applicable)
- [ ] Flag ownership and kill switch documented

## 32) Kill Criteria
- [ ] Stop conditions documented
- [ ] Decision owner documented
- [ ] Communication plan documented

## 33) Evidence Gaps & Map (Required)
- [ ] Evidence Gaps section present with owners/impact
- [ ] Evidence Map table present with sources and confidence

## 34) Open Questions / Future Considerations
- [ ] Open questions have owner + due date
- [ ] Known future considerations captured

## 35) Diagram Hygiene (Recommended)
- [ ] Mermaid diagrams compile and render
- [ ] If PNG/SVG required, rendering pipeline exists (mmdc)
