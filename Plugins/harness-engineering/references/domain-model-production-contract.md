# Domain Model Production Contract

Read when: HE work affects product behavior, workflow state, permissions,
billing/account concepts, persistence lifecycle, cross-system integration,
model naming, or a production-grade correctness claim.

This contract keeps domain-driven design operational inside HE. It is not a
glossary. It proves that the model, implementation, tests, and handoffs stay
aligned enough for production delivery.

## Core Rule

Domain-sensitive HE output must preserve model integrity, not only vocabulary.
When behavior depends on domain meaning, record the bounded context, model
shape, invariants, translation boundaries, unresolved questions, and closure
impact before moving to the next lifecycle stage.

## Domain Model Envelope

Use this envelope when product semantics, data lifecycle, or integration
boundaries affect acceptance, planning, implementation, review, or closure:

```yaml
domain_model:
  status: stable|ambiguous|conflicted|not_applicable
  bounded_context: ""
  core_domain_relevance: core|supporting|generic|unknown|not_applicable
  entities:
    - name: ""
      identity: ""
      lifecycle_owner: ""
  value_objects:
    - name: ""
      equality_rule: ""
      immutability_expectation: ""
  aggregates:
    - root: ""
      invariants: []
      transaction_boundary: ""
  domain_services:
    - name: ""
      reason_not_entity_or_value_object: ""
  repositories_or_factories:
    - name: ""
      lifecycle_boundary: ""
  integration_contexts:
    - upstream: ""
      downstream: ""
      translation_rule: ""
  unresolved_model_questions: []
  closure_impact: blocks_spec|blocks_plan|blocks_work|blocks_review|blocks_eval|none
```

Keep empty lists only when the concept is genuinely not relevant. Unknown
identity, invariant, lifecycle, or translation ownership is a blocker for the
stage that would otherwise harden behavior.

## Stage Gates

- `he-router`: infer domain-model routing from production semantics, not only
  explicit domain-model wording.
- `he-brainstorm`: ask the blocking question that separates duplicate concepts,
  false cognates, or unclear bounded contexts.
- `he-spec`: express domain invariants as acceptance criteria and name the
  bounded context before planning.
- `he-plan`: slice work so aggregate invariants, lifecycle ownership, and
  translation boundaries are not split accidentally.
- `he-work`: stop when implementation reveals model drift, duplicate concepts,
  or an unplanned boundary crossing.
- `he-code-review`: treat model/code/test language mismatch as a readiness
  finding before green CI is accepted as proof.
- `he-eval-report`: include a Domain Model Integrity gate before recommending
  Linear closure for domain-sensitive work.
- `he-strategy`: compress the core domain, supporting/generic subdomains, and
  context map when they affect moat, architecture, or future-agent guidance.

## Production-Grade Checks

Before downstream hardening, verify:

- the ubiquitous language appears consistently in artifacts, code names, and
  test evidence where relevant;
- entity identity and value-object equality are explicit when persisted or
  compared;
- aggregate roots and invariants define transaction boundaries;
- domain services are justified because the behavior does not belong naturally
  on an entity or value object;
- repositories and factories own lifecycle/reconstitution access rather than
  leaking persistence mechanics into behavior;
- neighboring contexts use explicit translation instead of shared assumptions;
- core-domain behavior is not buried under generic or supporting concerns;
- validation proves domain behavior, not only command success.

## Blocking Signals

Block or route backward when:

- the same term has two meanings in one bounded context;
- two names describe the same model concept with different rules;
- a plan splits one invariant across unrelated implementation units;
- a diff adds persistence, UI, or integration behavior that changes domain
  meaning without a spec or plan update;
- test names, code names, Linear wording, or docs disagree about the behavior;
- closure evidence lacks a domain scenario, invariant proof, or translation
  proof for high-risk domain work.

## Output Discipline

Do not paste broad DDD theory into stage outputs. Include only the domain fields
that affect the current decision, the evidence that supports them, and the next
stage that owns unresolved model work.
