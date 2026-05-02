# Harness Engineering Deferred Context Index

Harness Engineering active files must stay real plugin-owned text. Historical snapshots live under `fixtures/**` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`; active paths must not symlink into archives.

Use this index when a compact stage says context was moved for budget reasons. Do not trim context silently: move it to a stage reference, link it here, and keep enough wording for validators and future agents to recover the source.

## Runtime References

- Routing: `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/domain-model-routing.md`
- Lifecycle and tracker gates: `references/lifecycle-exit-contract.md`, `references/linear-tracker-gate.md`
- Intake and evidence: `references/qa-intake-routing.md`, `references/session-evidence-contract.md`, `references/session-evidence-skillify-triage.md`
- Delegation: `references/subagent-routing.md`, `references/subagent-call-contract.md`
- Folded compatibility: `references/folded-skill-context.md`

## Plan Preserved Context

The active `he-plan` entrypoint keeps Codex plan-mode lessons, synthesis, deepening, testing, handoff, and visual planning doctrine in:

- `Plugins/harness-engineering/references/he-plan-doctrine.md`
- `Plugins/harness-engineering/skills/he-plan/references/codex-plan-mode.md`
- `Plugins/harness-engineering/skills/he-plan/references/plan-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-plan/references/planning-depth.md`
- `Plugins/harness-engineering/skills/he-plan/references/deepening-review.md`
- `Plugins/harness-engineering/skills/he-plan/references/test-strategy.md`
- `Plugins/harness-engineering/skills/he-plan/references/visual-communication.md`

## Spec Preserved Context

The active `he-spec` entrypoint keeps Codex collaboration lessons, session evidence intake, source-parity rules, artifact templates, and autoresearch decisions in:

- `Plugins/harness-engineering/references/he-spec-doctrine.md`
- `Plugins/harness-engineering/skills/he-spec/references/autoresearch-2026-05-02.md`
- `Plugins/harness-engineering/skills/he-spec/references/codex-and-session-evidence.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-mode-rules.md`

## Work Preserved Context

The active `he-work` entrypoint keeps Codex execution lessons, Harness Engineering work-execution patterns, execution mode rules, and handoff requirements in:

- `Plugins/harness-engineering/skills/he-work/references/work-execution-contract.md`
- `Plugins/harness-engineering/skills/he-work/references/codex-execution-lessons.md`
- `Plugins/harness-engineering/skills/he-work/references/handoff-and-shipping.md`
- `Plugins/harness-engineering/skills/he-work/references/execution-modes.md`

## Preservation Contract

- Active `SKILL.md` files stay concise and routing-safe.
- Removed operational prose belongs in stage-local `references/*` or `Infrastructure/references/harness-engineering/deferred-context-index.full.md`.
- `fixtures/preserved-context/**` preserves legacy full-stage guides for audit and migration comparison only.
