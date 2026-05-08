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
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, reproduction_status, security_review, real_behavior_proof, work_candidate, repeated_failure, blackboard_delta, next handoff, repeated context-feedback candidates. If writing a durable review artifact, use `.harness/review/**.md` with Artifact Identity frontmatter.
## Procedure
Select mode first: review-only, readiness, repair/autofix, commit review, or investigation; review-only mode stays byte-clean. Read changed files and relevant review threads/comments; lead with file:line findings; Codex-compatible findings must be tight; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`. For disputed behavior or repeated bot feedback, require a proof loop before hypothesizing; see review loop patterns. For cockpit, golden-path, or command-catalog work, block readiness when the diff proves implementation presence but not first-contact compression, fresh-agent usability, or ablation. Do not approve readiness from green CI alone when real behavior proof, security review, or live PR-thread state is missing. When writing `.harness/review/**`, preserve date and Linear issue prefixes when the repo already uses them, but keep the same `canonical_slug` as the spec/plan/eval chain. Then approve/request/autofix. If feedback repeats across PRs, classify whether HE context, evals, or skill routing should adapt after the immediate review.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Leading with a summary before severity-ranked findings.
- Approving readiness while review threads, CI, Linear, or north-star evidence are unchecked.
- Treating green CI as proof of real user behavior.
- Treating command metadata, classification, or catalog filters as proof that the product is cockpit-first.
- Mutating code, resolving threads, or pushing during a review-only pass.
- Deciding from a PR title, branch name, one search hit, or one bot comment.
- Inflating confidence when the evidence ladder has missing rungs.
- Calling repeated feedback solved without a follow-up lane.
## Examples
- "Inspect and review PR 154 in coding-harness against JSC-246, `.harness/specs/JSC-246-account-settings.md`, `.harness/plan/JSC-246-account-settings.md`, CircleCI, and CodeRabbit threads."
- "Inspect my uncommitted changes to `Plugins/harness-engineering/skills/he-plan`; findings first, then tell me whether the traceability and validation evidence are enough."
- "CodeRabbit and Codex both flagged missing validation evidence again on this HE branch; review the PR and tell me whether the skill or eval context needs a follow-up."
- "CodeRabbit says this regression is still broken but CI is green; review the PR, reproduce or identify the missing proof loop, and separate the verdict from any autofix candidate."
## Assets
Reference `assets/` only for skill packaging and browseability; review evidence belongs in findings, commands, and PR/thread links.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Review policy index: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Review loop patterns: `Plugins/harness-engineering/skills/he-code-review/references/review-loop-patterns.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact identity: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
