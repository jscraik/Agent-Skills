# Integration Boundary Contract

Treat APIs, tools, plugins, hooks, events, and queues as explicit message contracts with ownership, routing, idempotency, and failure semantics.

Pack id: pack.codebase-architecture
Facet id: integration_boundary_contract
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.integration-contracts-need-message-shape: Integration Contracts Need Message Shape

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Tool, API, plugin, event, and queue boundaries need explicit message shape, routing, ownership, retry, idempotency, and failure classification before they can be treated as stable architecture.

Interpretation notes:
- This claim supports integration-boundary review for MCP tools, hooks, queues, APIs, and plugin contracts.
- It should be grounded in local payload schemas, call sites, and failure paths.

## Checklists

### checklist.arch.integration-boundary-contract: Integration Boundary Contract Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.integration-contracts-need-message-shape

- [ ] Name the producer, channel, payload envelope, router or filter, transformer, handler, and consumer owner.
- [ ] Identify the source of truth for the payload schema and compatibility promise.
- [ ] Require correlation or trace identity for asynchronous or cross-process boundaries.
- [ ] Classify retries, timeouts, poison messages, duplicate delivery, and partial failure.
- [ ] State whether the receiver is idempotent and where idempotency keys are stored or checked.
- [ ] Keep transformations explicit and testable instead of hidden inside orchestration glue.
- [ ] Map observable failure outputs to recovery actions.
- [ ] Add contract or fixture tests before calling the boundary agent-safe.

## Eval Scenarios

### eval.arch.integration-boundary-without-failure-contract: Integration Boundary Without Failure Contract

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.integration-contracts-need-message-shape

Knowledge claim: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Behavior under test: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Failure mode: The reviewer treats a successful local tool call as enough proof that the integration design is sound.
Expected agent move: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Skill lift target: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.integration-boundary-without-failure-contract.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A proposed MCP, plugin, hook, API, or queue boundary forwards payloads successfully on the happy path but has no schema owner, idempotency rule, retry behavior, correlation id, or classified failure output.
Should: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Expected failure: The reviewer treats a successful local tool call as enough proof that the integration design is sound.
Reproduce with: references/evals/eval.arch.integration-boundary-without-failure-contract.md
