---
name: he-code-review
description: "Review PRs, branches, diffs, commits, and workflow artifacts for actionable Harness Engineering findings. Use when merge readiness or traceability needs review."
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
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; then approve/request/autofix.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Constraints
Redact secrets. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
No title-only duplicate closure, fabricated context, or destructive commands.
## Philosophy
Review policy index, evidence_ladder, and Codex-compatible findings must be tight.
## Examples
- User says: "Can you inspect this GitHub PR for bugs and traceability before merge?"
- User says: "Validate whether these CodeRabbit comments are still true."
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Assets: `assets/icon-small.png`, `assets/icon-large.png`
- Policy: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
