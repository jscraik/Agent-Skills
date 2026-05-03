---
name: he-improve
description: "WHAT: Analyze and audit one HE skill surface for targeted improvement. Use when hardening, warning cleanup, or evidence-backed refactoring is needed."
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
Return schema_version when structured. Gap list, prioritized improvements, validation, retained references.
## Procedure
Before any new skill package is proposed, inspect existing surfaces; start with 2-3 focused surfaces at most, choose one primary target and at most two supporting references; label path fragments and bundle names as evidence labels; close coverage-gap items; for skill work, run the A/B/C spec-implementation-evaluation loop until the stop rule passes or a concrete blocker remains.
## Validation
Fail fast: stop at the first failed gate and do not proceed. Compare before/after behavior and command outcomes.
## Failure mode
If required evidence, Linear linkage, or next-stage routing is missing, stop and return the blocker with the smallest recovery step.
## Constraints
Redact secrets; preserve important context in references. Do not broaden into unrelated skills unless the evidence shows a shared contract issue. Do not remove important context for budget trimming; move deep context to references.
## Anti-Patterns
- Creating a new skill before checking whether an existing stage should be improved.
- Treating session evidence as a raw transcript dump instead of a bounded bundle.
- Slimming prompts by deleting behavior that should have moved to references.
## Examples
- "Inspect the session collector `skill-refactor-evidence.json` bundle and harden `Plugins/harness-engineering/skills/he-plan` until strict audit has no warnings."
- "Inspect `Plugins/harness-engineering/skills/he-code-review`, then run the A/B/C loop using the current `SKILL.md`, `contract.yaml`, `evals.yaml`, and latest audit output."
## Assets
Reference `assets/` only for skill packaging and browseability; experiment logs and loop artifacts belong in references or repo artifacts.
## References
- Shared subagent call policy: `Plugins/harness-engineering/references/subagent-call-contract.md`
- Deferred context index: `Plugins/harness-engineering/references/deferred-context-index.md`
- Session evidence: `Plugins/harness-engineering/references/session-evidence-skillify-triage.md`
- Skill improvement loop: `Plugins/harness-engineering/references/skill-improvement-loop.md`
