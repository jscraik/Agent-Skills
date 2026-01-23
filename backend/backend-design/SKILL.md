---
name: backend-design
description: "Produce a complete, review-ready backend design spec with explicit tradeoffs, compliance checks, and a fixed output contract.. Use when Use this skill when the task matches its description and triggers.."
---

# Backend Design

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md. If missing, use `references/standards-baseline.md`.


## Overview
Produce a complete, review-ready backend design spec with explicit tradeoffs, compliance checks, and a fixed output contract.

Gold standard rule (Jan 2026):
All guidance, decisions, and outputs must align with industry best practices as of Jan 2026.

## Philosophy
- Aim for correctness first, then security, then reliability; speed is a feature, not a priority.
- Prefer explicit tradeoffs over implicit assumptions; call out what you are optimizing for.
- Design for operability: if it cannot be observed and rolled back, it is not ready.

Ask these guiding questions before drafting:
- What is the single most critical user workflow and its failure mode?
- Which data integrity constraints must never be violated?
- Where does trust enter the system and how is it verified?
- What is the minimal viable architecture that still meets reliability goals?

## Empowerment
You are capable of extraordinary rigor here. Push boundaries on clarity and risk coverage while keeping the design practical.

## Decision priority stack (must follow)
1. Correctness and data integrity
2. Security and compliance
3. Reliability and observability
4. Performance and scalability
5. Developer ergonomics and delivery speed

## Inputs (ask only if blocking; max 2 questions)
1. System type: REST, GraphQL, or both
2. Compliance scope: which standards apply (if user says "all", include a superset checklist and flag legal review)

## Workflow (use this order)
1. Confirm scope: product goal, primary workflows, critical path, and integration surfaces.
2. Choose architecture pattern: Clean, Hexagonal, DDD, or hybrid; justify.
3. Define domain model and invariants.
4. Define API contract and versioning strategy.
5. Define data design and migration strategy.
6. Define authN/authZ model and tenanting.
7. Define reliability, observability, and performance targets.
8. Identify risks and edge cases.
9. Produce file plan and next steps.

## Output contract (always in this order)
1. SYSTEM_CONTEXT
2. ARCHITECTURE_PATTERN
3. DOMAIN_MODEL
4. API_CONTRACT
5. DATA_DESIGN
6. AUTHN_AUTHZ
7. RELIABILITY
8. OBSERVABILITY
9. PERFORMANCE
10. INTEGRATION_SURFACES
11. APPS_SDK_REQUIREMENTS
12. RISK_CHECKLIST
13. FILE_PLAN

Use `assets/backend_design_output_template.md` as the default structure.

## Required response headings
Every response must include these headings:
- `## When to use`
- `## Inputs`
- `## Outputs` (place the output contract under this heading)

## Failure-mode template (out of scope)
Use this exact structure when the request is out of scope:

```md
## When to use
- This skill applies to backend architecture and API design requests. The current request is out of scope.

## Outputs
- None (out of scope).

## Inputs
- None (out of scope).
```

## Standards baseline (enforce as of Jan 2026)
- HTTP semantics and status codes per RFC 9110
- OpenAPI latest published version (check `oas/latest`; 3.1.1 as of Oct 24, 2024) for REST contracts (JSON Schema 2020-12 dialect)
- GraphQL spec latest edition (Sep 2025)
- JSON (RFC 8259), JSON Schema 2020-12, YAML 1.2.1 for docs and schemas
- OWASP API Security Top 10 (2023) + OWASP Top 10 (2025)
- Compliance scopes: SOC 2, ISO/IEC 27001:2022, PCI DSS v4.0.1, HIPAA, GDPR, CCPA/CPRA (flag legal review)

Use references:
- `references/standards-baseline.md`

## Architecture pattern selection
- **Clean Architecture** when business rules must stay framework-agnostic and testable.
- **Hexagonal** when many external systems exist and swapability/testing are priorities.
- **DDD** when complex domain logic and bounded contexts are needed.
- **Hybrid** when two or more patterns are needed; explain boundaries.

## API contract rules
- Enforce resource naming, HTTP semantics, pagination, versioning, error format, rate limits, and auth.
- REST and GraphQL can coexist; avoid overlapping responsibilities.
- For both, define a stable error schema and client-facing examples.
- Include rate-limit + quota templates for REST/GraphQL and MCP tools.

Use references:
- `references/api-design-checklist.md` for REST + GraphQL validation
- `references/rest-best-practices.md` for REST patterns
- `references/graphql-schema-design.md` for GraphQL patterns

## Data design rules
- Define entities, relationships, constraints, indexing strategy, and migration/versioning.
- Model consistency boundaries (aggregates or transactions).

## Auth and compliance
- Always specify authN (token/session) and authZ (roles/scopes/policies).
- If compliance scope is "all", include a superset checklist for SOC2, ISO 27001, HIPAA, PCI DSS, GDPR, and CCPA and flag legal review.
- If Auth0 is used, enforce OAuth 2.1 aligned flows, PKCE, refresh token rotation, and token storage best practices.

## Reliability and observability
- Define idempotency strategy for writes.
- Include retry, timeout, circuit breaker, and rate-limit policies.
- Specify logs, metrics, traces, and alerting.
- Add idempotency + replay protection for MCP tools (nonce, request_id, dedupe window).

- If clients include React/Vite/Tailwind/TS, Apps SDK UI, OpenAI widgets, MCP, Storybook, or CLI, define contract-first integration. When UI is involved, align with canonical design tokens/guidelines in `references/design-guidelines-canonical.md` (or summary).
- If a Tauri desktop app is in scope, define the Rust command/IPC layer, permission/allowlist boundaries, and data validation rules. Specify how backend services interact with the Tauri layer (local vs remote calls, auth handoff, and error mapping).
- If Cloudflare Workers are used, account for Workers limits, streaming, and security model constraints.
- If Ollama Cloud API or frontier models are used, document provider-specific auth, data handling, and usage constraints.
- Provide guidance for typed clients and schema-driven codegen.
- If CLI is required, follow create-cli conventions (flags, output modes, exit codes).

Use references:
- `references/integration-surfaces.md`
- `references/tech-standards.md`
- `references/tauri-backend.md`
- `references/rust-backend-design.md`
- `references/auth0-oidc-best-practices.md`
- `references/cloudflare-workers-notes.md`
- `references/ollama-cloud-api.md`
- `references/frontier-models.md`
- `references/data-retention-residency.md`
- `references/rate-limit-templates.md`
- `references/mcp-idempotency-replay.md`
- `references/contract-testing.md`
- `references/security-headers.md`
- `references/audit-log-integrity.md`
- `references/feature-flagging-rollout.md`
- `references/apps-sdk-ux.md`
- `references/apps-sdk-use-cases.md`
- `references/apps-sdk-auth.md`
- `references/apps-sdk-state.md`
- `references/apps-sdk-monetization.md`
- `references/apps-sdk-metadata.md`
- `references/apps-sdk-security-privacy.md`

## Output schema templates
- Use `assets/mcp_tool_schema_template.json` for MCP tool contracts.
- Use `assets/cli_output_schema_template.json` for CLI JSON output contracts.

## Anti-patterns to avoid
- Unversioned APIs or breaking changes without deprecation
- Business logic in controllers or route handlers
- Missing idempotency for create or payment flows
- ORM entities leaked across service boundaries
- No telemetry for failures or latency

## Anti-pattern quick warnings
Avoid these anti-patterns. DO NOT ship designs without explicit authZ, versioning, and rollback plans. NEVER propose unsafe defaults (wide-open CORS, plaintext secrets, or unauthenticated admin paths). These mistakes and pitfalls lead to insecure or unreliable systems.

## Variation guidance (prevent convergence)
- Vary structure depth based on system complexity (simple CRUD vs multi-tenant or high-scale).
- Vary tradeoff emphasis (latency vs cost, availability vs consistency, simplicity vs extensibility).
- Vary examples by domain (payments, healthcare, analytics, AI pipelines) to avoid generic patterns.

## Resources
Use the references directory for detailed checklists and patterns. Do not inline large templates in this file.

## Contracts and evals (reference)

- Output contract schema: `references/contract.yaml`
- Evaluation rubric: `references/evals.yaml`

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.


## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
