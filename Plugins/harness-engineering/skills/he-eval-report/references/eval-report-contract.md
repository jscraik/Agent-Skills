# Eval Report Contract

The eval report is the proof layer between implementation and completion.

It must prove whether the completed change satisfies the approved execution
slice, preserves architectural invariants, preserves deterministic routing,
preserves cognition quality, preserves moat-critical behavior, reduces or avoids
drift, and is safe to mark complete in Linear.

## Source Artifacts

Read the completed implementation, the selected execution slice, and available
source artifacts:

```text
.harness/linear/*.md
.harness/refactors/*.md
.harness/decisions/*.md
.harness/core/*.md
.harness/strategy/*.md
.harness/triage/*.md
.harness/brainstorm/*.md
.harness/spec/*.md
.harness/plan/*.md
.harness/solutions/*.md
```

If a path is absent, record that as evidence. Do not invent source artifacts.

## Evaluated Slice

Identify the Linear project, milestone, parent issue, sub-issues, refactor
program, plugin HE spec, affected files/modules, affected workflows, related
ADRs, and related core invariants. Do not evaluate unrelated work.

## Validation

Run or inspect relevant project commands: build, test, typecheck, lint, format,
security scan, eval, doctor, smoke test, or integration test. Only include gates
that matter to the slice.

For each validation item include command or method, result, evidence,
confidence, failure details, and whether it blocks closure. If a command cannot
run, say why, provide manual inspection evidence, lower confidence accordingly,
and classify whether the blocker prevents Linear closure.

## Gate Matrix

Use this structure for relevant gates:

```text
Gate:
Expected:
Actual:
Status: pass | fail | partial | not-run
Evidence:
Confidence:
Blocks Closure: yes | no
Required Action:
```

Common categories include Build, Test, Typecheck, Lint, Format, Security, Eval,
Runtime Smoke, Integration, Routing Determinism, Context Load, Agent
Discoverability, Architecture Integrity, Governance Simplicity, Moat Protection,
Rollback Safety, and Linear Traceability.

## Evidence Rules

Every major conclusion must include fact, interpretation, assumption, evidence,
affected files/modules, command output or inspection method, confidence,
operational impact, and whether it blocks completion.

Never mark unavailable evidence as passing.
