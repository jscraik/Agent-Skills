# Gate Selection Contract

Use this contract when an HE stage could load broad review, domain, strategy,
refactor, Linear, security, specialist, or eval gates.

The goal is not maximum governance. The goal is the smallest proof surface that
keeps the current slice production-grade: correct, validated, traceable,
maintainable, safe to continue, and safe to close when closure is requested.

## Required Profile

When gate selection matters, record a compact profile:

```yaml
gate_profile:
  risk_class: trivial|standard|domain_sensitive|architecture_sensitive|closure_sensitive|security_sensitive|mixed
  proven_risks: []
  required_contracts: []
  skipped_contracts:
    - contract: "<reference or skill>"
      reason: "<why it is not needed for this slice>"
  minimum_proof_required:
    continue_to_next_stage: "<proof needed before handoff>"
    safe_to_close: "<proof needed before completion>"
    block_next_stage: "<condition that blocks handoff>"
  evidence_basis: direct|repo|linear|harness|external|reasoned
  downstream_route: he-brainstorm|he-spec|he-plan|he-work|he-code-review|he-eval-report|blocked
```

## Risk Classes

`trivial`

- Local wording, metadata, or artifact hygiene with no behavior, routing,
  validation, external side effect, security, domain, or Linear closure impact.
- Required proof is usually diff inspection plus the smallest relevant static
  validation.

`standard`

- Bounded skill, reference, doc, or script change with ordinary validation and
  traceability needs.
- Required proof includes source traceability, targeted validation, and explicit
  next-stage handoff.

`domain_sensitive`

- Work changes product terms, workflow state, permissions, persistence,
  integration semantics, account/billing concepts, or bounded-context language.
- Load domain context/model references and record non-applicability when skipped.

`architecture_sensitive`

- Work changes lifecycle routing, orchestration, refactor programs, core
  invariants, skill boundaries, or reusable execution contracts.
- Load the relevant architecture/refactor/ADR/core reference only for the
  affected boundary.

`closure_sensitive`

- Work recommends milestone, parent issue, PR, Linear, or execution-slice
  completion.
- Load eval-report and lifecycle-exit proof contracts. Completion requires proof,
  not implementation status.

`security_sensitive`

- Work changes permissions, auth, secrets, sandboxing, external side effects,
  network/file access, dependency trust, or user data exposure.
- Require specialist proof, a concrete blocker, or explicit non-applicability
  before closure.

`mixed`

- Multiple risk classes are genuinely present.
- `mixed` is not permission to load everything. Select the smallest set of
  required contracts and record every skipped adjacent contract with evidence.

## Stage Duties

`he-router`

- Select the next HE stage first.
- If routing words could trigger broad gates, apply this contract before loading
  adjacent context.
- Ask once when the risk class or downstream route is consequential and cannot
  be determined from evidence.

`he-spec`

- Convert the selected risk class into acceptance criteria and validation gates.
- Keep non-applicable heavy gates explicit so future agents do not reintroduce
  them from keyword overlap.

`he-code-review`

- Treat missing, keyword-only, or over-broad gate profiles as readiness findings
  when the diff changes HE routing, closure, domain, specialist, security, or
  lifecycle behavior.

`he-eval-report`

- Use the gate profile to decide whether closure evidence is sufficient.
- Do not recommend `Complete` or `Complete with follow-up` when required
  risk-specific proof is missing.

## Negative Gate Rules

- Do not create a refactor program for small local edits.
- Do not invoke domain model gates for work with no domain semantics.
- Do not select a specialist skill from keyword overlap alone.
- Do not create or mutate Linear when work is explicitly untracked.
- Do not claim release confidence while lifecycle evals time out.
- Do not let `mixed` load every adjacent contract.
- Do not treat a skipped contract as invisible; record the skip reason.

## Minimum Proof Examples

| Situation | Minimum proof |
| --- | --- |
| Trivial docs cleanup | diff inspection, relevant lint/static check, skipped heavy gates |
| Standard skill reference change | source traceability, strict skill audit or targeted validator, eval case if behavior changed |
| Domain-sensitive plan/spec | domain context or explicit non-applicability, acceptance criteria tied to domain language |
| Architecture-sensitive lifecycle change | contract wiring proof, negative eval, lifecycle exit impact |
| Closure-sensitive slice | eval report, validation evidence, drift result, accept/challenge/rework steering |
| Security-sensitive path | security scan, specialist review, or explicit proof that the sensitive path is not affected |

## Drift Signals

- Gate profile always says `mixed`.
- A skill loads strategy, refactor, Linear, domain, and security context without
  evidence.
- Keyword matches select specialists without affected files, workflows, or proof
  needs.
- Release-confidence claims ignore known lifecycle eval timeouts.
- Review artifacts recommend closure while required gate proof is absent.
