---
name: he-code-review
description: "Review Harness Engineering diffs, PRs, commits, and readiness claims for introduced risk. Use when correctness, validation proof, security posture, traceability, closure safety, or review-thread resolution must be assessed before merge or handoff."
metadata:
  skill-type: code_quality_review
---
# Harness Engineering Code Review
## Philosophy
Find introduced risk before summaries. Code review should be precise enough for Codex inline findings and broad enough to catch traceability, validation, readiness gaps, and repeated context failures.
## When to Use
Use when handling PRs, branches, diffs, commits, readiness, and disputed review feedback. Keep scope tight: inspect changed files, direct evidence, and at most the focused surfaces needed for the active review lane before widening.
## Inputs
Diff, repo guidance, Linear issue, spec, plan, PR evidence, validation output.
## Outputs
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, reproduction_status, security_review, real_behavior_proof, work_candidate, repeated_failure, repeated_failure_route, blackboard_delta, next handoff, repeated context-feedback candidates. If writing a durable review artifact, use `.harness/review/**.md` with Artifact Identity frontmatter.

Always make steering and proof searchable in the output: include `interactive_status`, `selection_evidence`, `route`, `stage`, `scope`, `traceability`, `validation`, `safe_to_continue`, and `blocked_reason`. In headless review, record `interactive_status: autonomous_assumption` plus the evidence and confidence; when mutation or readiness mode is ambiguous, ask once with `request_user_input` when available or return `interactive_status: blocked`.

When review finds a repeated failure, recurring bug pattern, or repeated context
feedback candidate, do not leave it as prose. Classify it as:
`linear_required` when executable repair work, bug tracking, owner assignment, or
closure tracking is needed; `compound_required` when lifecycle memory, source
prompt coverage, solved-problem capture, or cross-stage recurrence analysis is
needed; or `both_required` when the failure needs live execution tracking and
durable HE state reconstruction. Include the proposed Linear issue type and
the `he-compound` handoff evidence when applicable.
## Procedure
1. Select mode first: review-only, readiness, repair/autofix, commit review, or investigation. Review-only mode stays byte-clean.
2. Resolve the stage context contract when the review will write artifacts, mutate files, update PR state, or hand off to another stage; ask before mutation when mode is ambiguous.
3. Read changed files plus relevant review threads, CI, Linear, spec, plan, PR, and validation evidence. Lead with severity-ranked `file:line` findings.
4. Use the evidence ladder for disputed behavior or repeated bot feedback; require proof before hypothesizing.
5. Apply policy-index, specialist-skill, external `simplify`, coding-harness, and agent-native compression lenses only when the diff proves their trigger.
6. For diffs that change HE routing, lifecycle gates, closure recommendations,
   specialist selection, domain semantics, security-sensitive behavior, or eval
   proof, apply the gate selection contract; treat missing, keyword-only, or
   over-broad gate profiles as readiness findings.
7. Apply the first-principles contract to HE routing, lifecycle, governance,
   Linear, eval, or artifact-surface diffs; flag false sophistication when a
   change lacks verified-failure evidence or proof impact.
8. Apply the plugin hook capability contract when reviewing plugin manifests, `hooks/hooks.json`, hook commands, or hook-enforced lifecycle claims. Flag hardcoded absolute paths when `${PLUGIN_ROOT}` or `${PLUGIN_DATA}` would preserve plugin portability, and verify fallback behavior while `plugin_hooks` may be disabled.
9. Do not approve readiness from green CI alone when real behavior proof, security review, live PR-thread state, or traceability evidence is missing.
10. When writing `.harness/review/**`, classify by content shape before path, preserve dated Linear prefixes where the repo uses them, and keep the canonical slug aligned with the spec/plan/eval chain.
11. End with approve, request changes, autofix candidate, or follow-up lane for repeated feedback.
12. For repeated failures or bugs, set `repeated_failure_route` before closure:
    route live repair work to `he-linear-plan` or live Linear issue creation
    when tracking is missing, route lifecycle pattern analysis to `he-compound`,
    and use both when execution and memory are both required.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Verify gates, references, subagent evidence, and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Review-only mode must remain byte-clean. Autofix, PR mutation, thread resolution, or tracker updates require explicit repair or mutation authority.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
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
- Domain context: `Plugins/harness-engineering/references/domain-context-contract.md`
- Domain model production: `Plugins/harness-engineering/references/domain-model-production-contract.md`
- Gate selection: `Plugins/harness-engineering/references/gate-selection-contract.md`
- First principles: `Plugins/harness-engineering/references/first-principles-contract.md`
- Plugin hook capability: `Plugins/harness-engineering/references/plugin-hook-capability-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
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
