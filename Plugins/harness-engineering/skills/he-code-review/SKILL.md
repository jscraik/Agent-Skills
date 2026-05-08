---
name: he-code-review
description: "Review HE diffs for closure risk. Use when PR, commit, or readiness evidence is needed."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Code Review
## Philosophy
Find introduced risk before summaries. Code review should be precise enough for Codex inline findings and broad enough to catch traceability, validation, readiness gaps, and repeated context failures.
## When to Use
Use when handling PRs, branches, diffs, commits, readiness, and disputed review feedback.
## Inputs
Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.
## Outputs
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, reproduction_status, security_review, real_behavior_proof, work_candidate, repeated_failure, blackboard_delta, next handoff, repeated context-feedback candidates. If writing a durable review artifact, use `.harness/review/**.md` with Artifact Identity frontmatter.
## Procedure
1. Select mode first: review-only, readiness, repair/autofix, commit review, or investigation. Review-only mode stays byte-clean.
2. Resolve the stage context contract when the review will write artifacts, mutate files, update PR state, or hand off to another stage; ask before mutation when mode is ambiguous.
3. Read changed files plus relevant review threads, CI, Linear, spec, plan, PR, and validation evidence. Lead with severity-ranked `file:line` findings.
4. Use the evidence ladder for disputed behavior or repeated bot feedback; require proof before hypothesizing.
5. Apply policy-index, specialist-skill, external `simplify`, coding-harness, and agent-native compression lenses only when the diff proves their trigger.
6. Do not approve readiness from green CI alone when real behavior proof, security review, live PR-thread state, or traceability evidence is missing.
7. When writing `.harness/review/**`, classify by content shape before path, preserve dated Linear prefixes where the repo uses them, and keep the canonical slug aligned with the spec/plan/eval chain.
8. End with approve, request changes, autofix candidate, or follow-up lane for repeated feedback.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Review-only mode must remain byte-clean. Autofix, PR mutation, thread resolution, or tracker updates require explicit repair or mutation authority.
## Gotchas
- Green CI is not readiness when behavior proof, live review state, security, or traceability is missing.
- Repeated feedback may require skill/eval follow-up after the immediate review verdict.
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
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Review policy index: `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- Review loop patterns: `Plugins/harness-engineering/skills/he-code-review/references/review-loop-patterns.md`
- Agent-native audit scorecard: `Plugins/harness-engineering/references/agent-native-audit-scorecard.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Artifact identity: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- Doctrine: `Infrastructure/references/harness-engineering/he-code-review-doctrine.md`
- Pragmatic Programmer review: `Plugins/harness-engineering/references/pragmatic-programmer-review-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
