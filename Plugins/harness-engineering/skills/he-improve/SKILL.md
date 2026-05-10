---
name: he-improve
description: "Improve existing Harness Engineering skills, references, contracts, and evals from concrete evidence such as failed evals, repeated review findings, usage traces, or documented regressions. Use when a bounded hardening pass is required; do not use for speculative redesign."
metadata:
  skill-type: team_automation
---
# Harness Engineering Improve
## Philosophy
Improve with evidence, not vibes. Keep scope tight, preserve useful context in references, measure the delta, and make the stop rule explicit so future agents know whether to continue or ship.
## When to Use
Use when hardening, optimising, polishing, or capability-lifting existing code/skills/workflows.
## Inputs
Current artifact, evidence, session-collector evidence, metrics, constraints.
## Outputs
Return schema_version when structured. Gap list, red_signal, prioritized improvements, validation, blackboard_delta, retained references.
## Procedure
1. Before proposing a new skill package, inspect existing surfaces for a durable owner.
2. Start with 2-3 focused surfaces at most; choose one primary target and at most two supporting references.
3. Treat path fragments and bundle names as evidence labels, not routing authority.
4. Close coverage-gap items and translate external source material into invariants, evals, references, contracts, or an explicit rejection.
5. For skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains.
6. When evidence is really about product-surface compression, update the shared compression contract and enforcing stage evals before creating another visible skill.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Compare before/after behavior and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Execution Boundaries
Improve only the selected skill or shared contract surface. Do not create new visible skills, broaden scope, or mutate runtime projections without explicit authority.
For direct-handle use, apply the OpenAI-style design contract: classify the strongest side effect and separate read-only analysis, artifact writes, repo edits, external updates, destructive actions, and completion-gating recommendations before proceeding.
## Gotchas
- Path fragments and bundle names are evidence labels, not routing authority.
- Product-surface compression usually belongs in shared contracts and evals before new skill surfaces.
## Constraints
Redact secrets; preserve important context in references. Do not broaden into unrelated skills unless the evidence shows a shared contract issue. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Creating a new skill before checking whether an existing stage should be improved.
- Treating session evidence as a raw transcript dump instead of a bounded bundle.
- Slimming prompts by deleting behavior that should have moved to references.
- Adding a new surface when the durable fix is to hide, merge, demote, or gate an existing one.
## Examples
- "Inspect the session collector `skill-refactor-evidence.json` bundle and harden `Plugins/harness-engineering/skills/he-plan` until strict audit has no warnings."
- "Inspect `Plugins/harness-engineering/skills/he-code-review`, then run the A/B/C loop using the current `SKILL.md`, `contract.yaml`, `evals.yaml`, and latest audit output."
## Assets
Reference `assets/` only for skill packaging and browseability; experiment logs and loop artifacts belong in references or repo artifacts.
## References
- OpenAI-style plugin design: `Infrastructure/references/openai-style-plugin-design-contract.md`
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Session evidence: `Plugins/harness-engineering/references/session-evidence-skillify-triage.md`
- Skill improvement loop: `Plugins/harness-engineering/references/skill-improvement-loop.md`
- Agent-native compression: `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- Pragmatic operating invariants: `Plugins/harness-engineering/references/pragmatic-operating-invariants.md`
- XP operating contract: `Plugins/harness-engineering/references/xp-operating-contract.md`
