# Architecture Integration Boundary Contract

Recovery status: source reference only; not SDK admission or runtime proof.
Derived KnowledgeOS text reused with Jamie Craik's ownership confirmation on
2026-09-27. See [recovery provenance](knowledge-capsule-recovery.md).
Historical status labels below describe the producer snapshot, not this candidate.
Scenario examples are inactive reference material, not additional active evals.

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
Proof route: illustrative historical scenario only; no executable proof claimed.
Historical fixture identifier (not a shipped dependency): `references/evals/eval.arch.integration-boundary-without-failure-contract.md`
Promotion status: historical example; inactive.
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A proposed MCP, plugin, hook, API, or queue boundary forwards payloads successfully on the happy path but has no schema owner, idempotency rule, retry behavior, correlation id, or classified failure output.
Should: The reviewer refuses to call the boundary stable and asks for a message contract, failure contract, and deterministic contract fixture.
Expected failure: The reviewer treats a successful local tool call as enough proof that the integration design is sound.
Reproduction: not supplied by this reference; use the declared active skill eval suite.
