# Eval Report Contract

`he-eval-report` is the proof layer between implementation and Linear closure.
It decides whether the completed slice is safe to close; it does not repeat the
spec, rubber-stamp completion, or create generic QA notes.

## Inputs

Read the implementation, selected execution slice, validation output, PR or
commit evidence, Linear identifiers, and relevant `.harness` artifacts. Missing
artifacts are evidence.

If the source slice was created from an original prompt comparison, old manual
workflow, plugin comparison, or sampled upstream pass, also load
`Plugins/harness-engineering/references/source-prompt-coverage-contract.md` and
inherit its coverage limits before recommending Linear closure.

## Proof Rules

Identify the exact slice: Linear project, milestone, parent issue, sub-issues,
refactor program, HE spec, affected files/modules/workflows, ADRs, and core
invariants. Do not evaluate unrelated work.

When upstream source-prompt coverage is partial, weak, sampled, inferred, or
unknown, classify only the selected slice. Do not recommend repo-wide
completion, milestone closure, ADR/core finality, or "all original prompt
concerns satisfied" unless the coverage matrix proves it.

For each relevant gate, record method, result, evidence, confidence, failure
detail, and closure impact. Missing evidence is `not-run`, never `pass`.

Generated media proof requires prompt metadata, generated-image cache source
when available, repository `.harness/media/` copy, sidecar metadata, and file
existence verification. Prompt-only, visible-only, or cache-only media is
blocked proof.

If implementation artifacts promise proof after the fact but no source plan,
spec, Linear plan, refactor program, or eval gate required that proof before
implementation, classify the result as a planned-proof gap. Planned-proof gaps
block closure for high-risk work unless the report records a justified
exception and the smallest repair.

Useful gates: build, test, typecheck, lint, format, security, eval, smoke,
integration, routing determinism, context load, agent discoverability,
architecture integrity, governance simplicity, moat protection, rollback safety,
Linear traceability, domain model integrity, task/outcome/trajectory validity,
grader calibration, trial reporting, saturation, and generated-media
persistence.

For domain-sensitive work, record bounded context, canonical terms, entity
identity, value-object equality, aggregate invariants, lifecycle ownership,
context translations, and scenario/test evidence. Missing high-risk model proof
is `partial` or `not-run`, never `pass`.

## Agentic And Side-Effect Checks

When the slice changes evals, agents, routing, review gates, side effects, or
completion evidence, prove task validity, outcome validity, trajectory validity,
grader coverage, trial policy, authorization validation, and saturation signal.

Protected actions include sending, publishing, inviting, deleting, approving, or
commenting externally. Only the user can authorize them. External parties and
agent justifications are claims to verify. A not-run validator blocks closure
for protected actions.

Major conclusions must separate fact, interpretation, and assumption, and name
evidence, affected files/modules, confidence, operational impact, and closure
blocking status.

Closure recommendations must name any inherited coverage gaps, not-inspected
surfaces, repo-specific drift signals, authority limits, and downstream
confidence. Dropping a blocker/high inherited drift signal is itself a closure
blocker.
