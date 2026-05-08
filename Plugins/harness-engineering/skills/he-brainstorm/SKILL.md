---
name: he-brainstorm
description: "WHAT: Analyze fuzzy HE intent into options and handoff. Use when behavior, success criteria, Linear, or evidence is ambiguous."
metadata:
  skill-type: team_automation
---
# Harness Engineering Brainstorm
## Philosophy
Make ambiguity useful without turning it into ceremony. Preserve what is stated, inferred, and out of scope so the next HE stage can continue without re-litigating context.
## When to Use
Use before spec writing when intent is fuzzy; preserve Context preservation and assign `scope_tier`.
Use folded `he-ideate` mode when the user asks what to improve, asks for options, or wants strong ideas before choosing one to brainstorm.
## Inputs
User goal, repo evidence, Linear/project hints.
## Outputs
Return schema_version when structured. Stated / Inferred / Out of scope, options, risks, warrant notes, blackboard_delta, durable artifact path when written, and next stage. Brainstorm markdown belongs under `.harness/brainstorm/**.md`; explicit folded `he-ideate` mode belongs under `.harness/ideate/**.md`.
## Procedure
Explore first; require an identifiable subject before dispatching ideation or writing artifacts; separate evidence from guesses; before writing durable docs choose the routed `.harness` path from the artifact routing contract; for durable tracked work resolve/create the Linear issue before handoff; in coding-harness-managed repos load the command bridge and record the Harness transition.
For `he-ideate`, ground in repo/Linear/session evidence and current web research unless explicitly skipped, apply the specialist skill steering contract when a proven knowledge domain can improve option quality, generate many candidates internally, critique all candidates, surface only warranted survivors with rejection reasons, then apply the interactive steering contract when survivor selection would shape the downstream spec, plan, Linear work, or implementation slice.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Check scope, traceability, and handoff clarity.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
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
- Interactive steering: `Plugins/harness-engineering/references/interactive-steering-contract.md`
- Specialist skill steering: `Plugins/harness-engineering/references/specialist-skill-steering-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Ideation mode: `Plugins/harness-engineering/skills/he-brainstorm/references/ideation-mode.md`
- Linear tracker gate: `Plugins/harness-engineering/references/linear-tracker-gate.md`
- Coding Harness bridge: `Plugins/harness-engineering/references/coding-harness-command-bridge.md`
- Artifact routing: `Plugins/harness-engineering/references/artifact-routing-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
