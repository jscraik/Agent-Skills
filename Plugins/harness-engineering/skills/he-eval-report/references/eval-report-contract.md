# Eval Report Contract

`he-eval-report` is the proof layer between implementation and Linear closure.
It decides whether the completed slice is safe to close; it does not repeat the
spec, rubber-stamp completion, or create generic QA notes.

## Inputs

Read the implementation, selected execution slice, and relevant `.harness`
artifacts: `linear`, `refactors`, `decisions`, `core`, `strategy`, `triage`,
`brainstorm`, `spec`, `plan`, and `solutions`. Missing artifacts are evidence.

## Proof Rules

Identify exactly what is evaluated: Linear project, milestone, parent issue,
sub-issues, refactor program, HE spec, affected files/modules/workflows, ADRs,
and core invariants. Do not evaluate unrelated work.

For each relevant gate, record method, result, evidence, confidence, failure
detail, and closure impact. Missing evidence is `not-run`, never `pass`.
For domain-sensitive work, include domain model integrity: bounded context,
aggregate invariants, translation boundaries, model/code/test language match,
and closure impact. Missing domain model integrity proof blocks closure when the
slice changes production behavior.

If implementation artifacts promise proof after the fact but no source plan,
spec, Linear plan, refactor program, or eval gate required that proof before
implementation, classify the result as a planned-proof gap. Planned-proof gaps
block closure for high-risk or closure-critical work unless the report records
a justified exception and the smallest repair.

Useful gates: build, test, typecheck, lint, format, security, eval, smoke,
integration, routing determinism, context load, agent discoverability,
architecture integrity, governance simplicity, moat protection, rollback safety,
Linear traceability, domain model integrity, task/outcome/trajectory validity,
grader calibration, trial reporting, and saturation.

For domain-sensitive work, domain model integrity is closure evidence. Record
bounded context, canonical terms, entity identity, value-object equality,
aggregate invariants, lifecycle ownership, context translations, and the domain
scenario or test evidence that proves the implementation still matches the
approved model. Missing high-risk model proof is `partial` or `not-run`; it is
not a pass.

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
