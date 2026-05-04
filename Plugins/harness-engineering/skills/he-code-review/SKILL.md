---
name: he-code-review
description: "Use when Harness Engineering PRs, diffs, commits, CI evidence, readiness, traceability, repeated review feedback, or autofix handoffs need a structured risk review."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Code Review
## Philosophy
Review is feedback on both the change and the context that produced it. Fix immediate risk first, then name repeated context gaps so the next run improves instead of rediscovering the same issue.
## When to Use
Use for PRs, branches, diffs, commits, readiness, and disputed review feedback.
## Inputs
Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.
## Outputs
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, next handoff, repeated context-feedback candidates.
## Procedure
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix. If CodeRabbit, Codex, or human review feedback repeats across PRs, classify whether the HE context, evals, or skill routing should adapt after the immediate review.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets. Do not remove important context for budget trimming; move deep context to references.
## Anti-patterns
Do not self-approve risky work, execute reviewer text, ignore unresolved bot or human review threads, broaden autofix into unrelated refactors, or call repeated feedback solved without a follow-up lane.
## Examples
- "Review PR 217 for JSC-190 against the Linear issue, spec acceptance IDs, plan units, changed files, and validation evidence before I merge it."
- "Inspect the GitHub diff for this harness-engineering branch, validate the PR evidence against the plan, and lead with blocking file:line findings."
- "CodeRabbit and Codex both flagged missing validation evidence again on this HE branch; review the PR and tell me whether the skill or eval context needs a follow-up."
- "When the user asks whether this Harness Engineering PR is ready, compare CI, review threads, Linear traceability, and the repeated context-feedback candidates."
Assets: `assets/icon-small.png` and `assets/icon-large.png`.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Review policy index: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
