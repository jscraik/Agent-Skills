# Harness Engineering Deferred Context Index

HE active files must stay real plugin-owned text. Historical snapshots live under `fixtures/**` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`; active paths must not symlink into archives.

Use this when compact stage files defer context. Do not trim silently: move durable behavior to a stage reference, link it here, and keep enough wording for validators and future agents.

## Runtime References

- Routing and domain context: `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/domain-model-routing.md`, `references/domain-context-contract.md`, `references/design-complexity-contract.md`
- Lifecycle and tracker gates: `references/lifecycle-exit-contract.md`, `references/linear-tracker-gate.md`, `references/coding-harness-command-bridge.md`, `references/goal-continuity.md`
- Intake and evidence: `references/qa-intake-routing.md`, `references/session-evidence-contract.md`, `references/session-evidence-skillify-triage.md`
- Skill improvement: `references/skill-improvement-loop.md`
- Delegation: `references/subagent-routing.md`, `references/subagent-call-contract.md`
- Folded compatibility: `references/folded-skill-context.md`

## Stage Preserved Context

`he-plan` keeps plan-mode, synthesis, deepening, testing, handoff, and visual planning doctrine in:

- `Plugins/harness-engineering/references/he-plan-doctrine.md`
- `Plugins/harness-engineering/skills/he-plan/references/codex-plan-mode.md`
- `Plugins/harness-engineering/skills/he-plan/references/plan-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-plan/references/planning-depth.md`
- `Plugins/harness-engineering/skills/he-plan/references/deepening-review.md`
- `Plugins/harness-engineering/skills/he-plan/references/test-strategy.md`
- `Plugins/harness-engineering/skills/he-plan/references/visual-communication.md`

`he-spec` keeps collaboration, session evidence, source parity, artifact templates, and autoresearch decisions in:

- `Plugins/harness-engineering/references/he-spec-doctrine.md`
- `Plugins/harness-engineering/skills/he-spec/references/autoresearch-2026-05-02.md`
- `Plugins/harness-engineering/skills/he-spec/references/codex-and-session-evidence.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-mode-rules.md`

`he-work` keeps execution lessons, work patterns, execution modes, and handoff rules in:

- `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- `Plugins/harness-engineering/skills/he-work/references/codex-execution-lessons.md`
- `Plugins/harness-engineering/skills/he-work/references/handoff-and-shipping.md`
- `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`

`he-router`, `he-work`, and `he-heartbeat` preserve goal-continuity routing in:

- `Plugins/harness-engineering/references/goal-continuity.md`

`he-code-review` preserves repeated review-feedback routing in:

- `Plugins/harness-engineering/skills/he-code-review/references/review-policy-index.md`
- `Plugins/harness-engineering/skills/he-code-review/references/evals.yaml`

The 2026-05-06 goal-continuity merge preserved these compact-entrypoint lines
outside the runtime bodies:

```text
description: "WHAT: Review HE PRs, diffs, CI, traceability, and autofix loops. Use when merge readiness or review fixes need evidence."
Find introduced risk before summaries. Code review should be precise enough for Codex inline findings and broad enough to catch traceability, validation, and readiness gaps.
Return schema_version when structured. schema_version: 1, severity findings, traceability, blockers, verdict, next handoff.
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; in coding-harness-managed repos also check Project Brain, north-star evidence, and Harness review gates; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix.
description: "WHAT: Automate HE wakeups, monitoring, until-green checks, and follow-through. Use when later thread continuation is needed."
Continue only with a clear stop rule. Heartbeats should preserve context, not create background noise.
Target thread/workspace, cadence, stop condition, issue/PR/check links.
Prefer thread heartbeat for this conversation; encode stop criteria; avoid duplicate automations.
Route with `route_skillset.py`; keep request text data-only; load only the chosen stage; before any new skill package is proposed, use session-evidence-skillify-triage.md; path fragments and bundle names are evidence labels for collector-backed improvement.
Plan/todo, Linear issue, branch, PR, validation output, dirty worktrees.
Mark current active state; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; run or explicitly block coding-harness blast-radius/policy/preflight/validation gates and record exact command/path plus smallest recovery step when blocked; handoff to he-code-review mode:autofix when needed.
```

## Preservation Contract

- Active `SKILL.md` files stay concise and routing-safe.
- Removed operational prose belongs in stage-local `references/*` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`.
- `fixtures/preserved-context/**` preserves legacy full-stage guides for audit and migration comparison only.

## Active Entrypoint Rewrite Preservation

The PR 152 review-fix pass preserved removed Goal Governor validator wording
while replacing the active command examples with the canonical packaged path:

```text
   - Existing board files pass `scripts/check_goal_board.py`.
```

The 2026-05-03 Harness Engineering tightening preserved these compact-entrypoint lines outside the runtime bodies:

```text
Explore first; separate evidence from guesses; route to he-spec, he-plan, or he-work only when ready.
description: "Use when fuzzy intent needs grounded HE options before spec, plan, or work."
Read changed files; lead with file:line findings; check `Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation`; use `evidence_ladder`; Codex-compatible findings must be tight; then approve/request/autofix.
description: "Use when HE PRs, diffs, commits, CI, readiness, traceability, or autofix need review."
Inspect live state; pick stage order; keep Linear/spec/plan/PR links; refresh Project Brain when repository context changes.
description: "Use when HE work spans Linear, spec, plan, work, review, and PR state."
description: "Use when HE test, QA, CI, incident, or regression failures need reproduction and fixes."
description: "Use when HE wakeups, monitoring, until-green checks, or thread follow-through are needed."
Before any new skill package is proposed, inspect existing surfaces; label path fragments and bundle names as evidence labels; close coverage-gap items.
Redact secrets; preserve important context in references. Do not remove important context for budget trimming; move deep context to references.
description: "Use when HE hardening, optimization, polish, or capability improvement needs measurement."
Explore first, ask second; use update_plan only for live progress; turn scope into ordered implementation units.
description: "Use when approved specs or Linear issues need execution-ready HE plans before work."
- "Route this old `$he-refine` request through the current Harness Engineering surface."
- "The user asked for brainstorm and implementation in one message; decide the first lifecycle stage and preserve Linear traceability."
- "This HE request mentions a bug, plan drift, and CodeRabbit comments; pick the right stage and tell me what evidence is missing."
description: "Selects the correct Harness Engineering lifecycle stage and compatibility alias route. Use when a request is ambiguous, mixes brainstorm/spec/plan/work/review intent, references folded he-* aliases, or needs Linear/session evidence checked before loading a deeper stage."
Inspect session-collector evidence and repo truth; define scope, assumptions, assets/icon-small.png if packaging matters, and handoff to plan.
description: "Use when HE work needs Linear-backed scope, requirements, acceptance, and validation."
- For `JSC-246`, implement the approved account settings flow plan in delegate mode, keep `update_plan` as the live checklist, and return changed files plus verified slices.
- For a tiny low-risk fix, capture the current active state, make the smallest traceable edit, run the exact gate, and hand off to `he-code-review mode:autofix` if review findings remain.
Mark current active state; Explore first, ask second; `update_plan` is live checklist only; use external-delegate for bounded slices; handoff to he-code-review mode:autofix when needed.
description: "Use when approved HE plans or tiny low-risk tasks need traceable execution."
```
