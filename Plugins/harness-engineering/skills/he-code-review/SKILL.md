---
name: he-code-review
description: "Use when HE PRs, diffs, commits, CI, readiness, traceability, or autofix need review."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Code Review
## When to Use
Use for PRs, branches, diffs, commits, readiness, and disputed review feedback.
## Inputs
Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.
## Outputs
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, next handoff.
## Procedure
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets. Do not remove important context for budget trimming; move deep context to references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Review policy index: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
