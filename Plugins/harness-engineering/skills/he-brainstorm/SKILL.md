---
name: he-brainstorm
description: "Analyze HE options and choose survivor routes. Use when direction is unsettled before spec or plan work."
metadata:
  skill-type: team_automation
---
# Harness Engineering Brainstorm
## Philosophy
Make ambiguity useful without turning it into ceremony. Preserve what is stated, inferred, and out of scope so the next HE stage can continue without re-litigating context.
## When to Use
Use when before spec writing when intent is fuzzy; preserve Context preservation and assign `scope_tier`.
Use folded `he-ideate` mode when the user asks what to improve, asks for options, or wants strong ideas before choosing one to brainstorm.
## Inputs
User goal, repo evidence, Linear/project hints.
## Outputs
Return schema_version when structured. Stated / Inferred / Out of scope, options, risks, warrant notes, blackboard_delta, durable artifact path when written, and next stage. Brainstorm markdown belongs under `.harness/brainstorm/**.md`; explicit folded `he-ideate` mode belongs under `.harness/ideate/**.md`.
## Procedure
1. Explore first and require an identifiable subject before dispatching ideation or writing artifacts.
2. Resolve only the stage context fields needed for tracker, artifact route, evidence freshness, and coding-harness handoff.
3. Separate stated facts, interpretations, guesses, and out-of-scope work.
4. Route durable brainstorm artifacts to `.harness/brainstorm/**.md`; route explicit folded `he-ideate` artifacts to `.harness/ideate/**.md`.
5. Resolve or block the Linear tracker before durable handoff for tracked work.
6. In folded `he-ideate` mode, use `skills/he-brainstorm/references/ideation-mode.md` for candidate generation, critique, coverage recovery, survivor selection, web research, and specialist-skill steering.
7. Apply the first-principles contract before survivor selection: prefer ideas that prevent verified HE failures or reduce ambiguity; defer copied patterns that lack HE-specific failure evidence.
8. Ask before survivor selection when the chosen survivor would shape downstream spec, plan, Linear work, or implementation scope.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check scope, traceability, and handoff clarity.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Brainstorming is non-mutating except for approved `.harness/brainstorm/**` or `.harness/ideate/**` artifacts. Do not convert survivors into specs, plans, or Linear work without handoff authority.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- Guesses must stay labeled as guesses.
- Survivor selection can be a blocking user choice when it shapes downstream scope.
## Constraints
Redact secrets; do not turn brainstorming into execution. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Jumping straight to implementation when behavior is still unclear.
- Treating guesses as requirements without an evidence or warrant note.
- Creating a durable handoff for tracked work without resolving or blocking the Linear gate.
## Examples
- "Inspect JSC-246 and the three QA notes in `Docs/qa/account-settings.md`; separate stated facts, inferred behavior, and out-of-scope work before filing or updating Linear."
- "Inspect the coding-harness Linear sync idea, compare the tracker-only option with the Project Brain option, and tell me which one should survive before we spec it."
- "Analyze whether the data-sync ambiguity in JSC-310 is spec-ready yet, and if not, hold the handoff until options are clear."
## Assets
Reference `assets/` only for skill packaging and browseability; workflow source of truth stays in this SKILL and references.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Stage context: `Plugins/harness-engineering/references/stage-context-contract.md`
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Domain context: `Plugins/harness-engineering/references/domain-context-contract.md`
- Domain model production: `Plugins/harness-engineering/references/domain-model-production-contract.md`
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Topic coverage: `Plugins/harness-engineering/references/brainstorm-topic-coverage-contract.md`
- First principles: `Plugins/harness-engineering/references/first-principles-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Ideation mode: `Plugins/harness-engineering/skills/he-brainstorm/references/ideation-mode.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Artifact classification: `Plugins/harness-engineering/references/artifact-classification-and-traceability.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
