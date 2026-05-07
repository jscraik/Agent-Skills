---
name: he-code-review
description: "WHAT: Review HE PRs, diffs, CI, traceability, repeated review feedback, and autofix loops. Use when merge readiness or review fixes need evidence."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Code Review
## Philosophy
Find introduced risk before summaries. Code review should be precise enough for Codex inline findings and broad enough to catch traceability, validation, readiness gaps, and repeated context failures.
## When to Use
Use for PRs, branches, diffs, commits, readiness, and disputed review feedback.
## Inputs
Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.
## Outputs
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, repeated_failure when recurring, blackboard_delta, next handoff, repeated context-feedback candidates.
## Procedure
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix. If CodeRabbit, Codex, or human review feedback repeats across PRs, classify whether the HE context, evals, or skill routing should adapt after the immediate review.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Leading with a summary before severity-ranked findings.
- Approving readiness while review threads, CI, Linear, or north-star evidence are unchecked.
- Inflating confidence when the evidence ladder has missing rungs.
- Calling repeated feedback solved without a follow-up lane.
## Examples
- "Inspect and review PR 154 in coding-harness against JSC-246, `Specs/JSC-246-account-settings.md`, `Plans/JSC-246-account-settings.md`, CircleCI, and CodeRabbit threads."
- "Inspect my uncommitted changes to `Plugins/harness-engineering/skills/he-plan`; findings first, then tell me whether the traceability and validation evidence are enough."
- "CodeRabbit and Codex both flagged missing validation evidence again on this HE branch; review the PR and tell me whether the skill or eval context needs a follow-up."
## Assets
Reference `assets/` only for skill packaging and browseability; review evidence belongs in findings, commands, and PR/thread links.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Review policy index: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
