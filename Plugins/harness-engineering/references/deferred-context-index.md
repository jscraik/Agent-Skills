# Harness Engineering Deferred Context Index

HE active files must stay real plugin-owned text. Historical snapshots live
under `fixtures/**` or a dedicated archive reference; active paths must not
symlink into archives.

Use this index only when a compact stage file defers context. Do not paste
active procedure bodies here. Move durable behavior to a stage reference, link
the reference below, and let validators catch stale duplicated procedure text.

## Runtime Reference Map

- Routing and domain context:
  - `references/routing-map.json`
  - `references/deterministic-stage-routing.md`
  - `references/domain-model-routing.md`
  - `references/domain-context-contract.md`
  - `references/domain-model-production-contract.md`
  - `references/design-complexity-contract.md`
  - `references/gate-selection-contract.md`
- Lifecycle, artifact, slice, and tracker gates:
  - `references/stage-context-contract.md`
  - `references/lifecycle-exit-contract.md`
  - `references/artifact-routing-contract.md`
  - `references/artifact-classification-and-traceability.md`
  - `references/execution-slice-contract.md`
  - `references/linear-tracker-gate.md`
  - `references/coding-harness-command-bridge.md`
  - `references/goal-continuity.md`
- Intake and evidence:
  - `references/qa-intake-routing.md`
  - `references/session-evidence-contract.md`
  - `references/session-evidence-skillify-triage.md`
  - `references/session-evidence-trace-context.md`
- Review, ideation, and agent-native lenses:
  - `references/agent-native-audit-scorecard.md`
  - `references/brainstorm-topic-coverage-contract.md`
  - `references/document-review-finding-tiers.md`
  - `references/specialist-skill-steering-contract.md`
  - `references/pragmatic-programmer-review-contract.md`
  - `references/xp-operating-contract.md`
- Skill improvement:
  - `references/skill-improvement-loop.md`
  - `references/plugin-eval-confidence-contract.md`
- Delegation:
  - `references/subagent-routing.md`
  - `references/subagent-call-contract.md`
- Folded compatibility:
  - `references/folded-skill-context.md`

## Conditional Loading Map

Load references by trigger instead of by habit:

| Stage or condition | Load | Expected proof |
| --- | --- | --- |
| Any stage writes durable docs, mutates files, or hands off | `references/stage-context-contract.md`, `references/lifecycle-exit-contract.md` | compact stage context plus exit status |
| Stage choice is ambiguous | `references/routing-map.json`, `references/deterministic-stage-routing.md`, `references/interactive-steering-contract.md` | selected stage or one blocking question |
| `.harness` artifacts determine scope | `references/artifact-classification-and-traceability.md`, `references/artifact-routing-contract.md` | content-shape classification and Artifact Identity status |
| Non-trivial tracked work | `references/linear-tracker-gate.md` | resolved, created, blocked, or user-opted-out tracker status |
| Existing tracked plan or Linear-backed slice is consumed | `references/linear-delta-capture-gate.md` | delta admitted, rejected, or blocked before scope changes |
| Coding-harness-managed repo | `references/coding-harness-command-bridge.md`, `references/execution-slice-contract.md` | command evidence or explicit blocked bridge fields |
| Stage could load broad domain, strategy, refactor, Linear, security, specialist, or eval gates | `references/gate-selection-contract.md` | smallest gate profile, required contracts, skipped contracts, and minimum proof |
| Domain-specific knowledge could sharpen output | `references/specialist-skill-steering-contract.md` | chosen specialist, skipped reason, or blocker |
| User choice affects downstream scope | `references/interactive-steering-contract.md` | asked choice, headless assumption, or blocked state |
| Product compression is the blocker | `references/agent-native-compression-contract.md` | subtractive proof, fresh-agent eval, and ablation gate |
| HE plugin confidence or budget quality is claimed | `references/plugin-eval-confidence-contract.md` | static plugin-eval result, rooted handle proof, release eval lane, and cache-sync status |
| Lifecycle stage risks ceremony, broad scope, weak feedback, or unclear value | `references/xp-operating-contract.md` | smallest valuable slice, feedback signal, slack policy, or blocked reason |
| Review or closure touches agent-facing workflow surfaces | `references/agent-native-audit-scorecard.md` | scorecard findings or not-applicable reason |
| Solved-problem evidence should persist | `references/solution-capture-contract.md` | refreshed existing solution or new `.harness/solutions/**` capture |

## Stage Reference Map

`he-brainstorm`:

- `skills/he-brainstorm/references/brainstorm-workflow-details.md`
- `skills/he-brainstorm/references/discovery-interview.md`
- `skills/he-brainstorm/references/requirements-artifact-guide.md`
- `skills/he-brainstorm/references/visual-communication.md`
- `references/brainstorm-topic-coverage-contract.md`

`he-spec`:

- `references/he-spec-doctrine.md`
- `skills/he-spec/references/autoresearch-2026-05-02.md`
- `skills/he-spec/references/codex-and-session-evidence.md`
- `skills/he-spec/references/spec-artifact-contract.md`
- `skills/he-spec/references/spec-mode-rules.md`

`he-plan`:

- `references/he-plan-doctrine.md`
- `skills/he-plan/references/codex-plan-mode.md`
- `skills/he-plan/references/plan-artifact-contract.md`
- `skills/he-plan/references/planning-depth.md`
- `skills/he-plan/references/deepening-review.md`
- `skills/he-plan/references/test-strategy.md`
- `skills/he-plan/references/visual-communication.md`

`he-work`:

- `skills/he-work/references/work-execution-contract.md`
- `skills/he-work/references/codex-execution-lessons.md`
- `skills/he-work/references/handoff-and-shipping.md`
- `skills/he-work/references/execution-modes.md`

`he-code-review`:

- `skills/he-code-review/references/review-policy-index.md`
- `skills/he-code-review/references/review-loop-patterns.md`
- `references/pragmatic-programmer-review-contract.md`

`he-eval-report`:

- `skills/he-eval-report/references/eval-report-contract.md`
- `skills/he-eval-report/references/eval-report-template.md`
- `skills/he-eval-report/references/eval-report-schema.json`
- `skills/he-eval-report/references/drift-taxonomy.md`
- `skills/he-eval-report/references/linear-completion-policy.md`

`he-strategy`:

- `skills/he-strategy/references/strategy-output-contract.md`
- `skills/he-strategy/references/source-prompt-preservation.md`
- `references/pragmatic-programmer-review-contract.md`

`he-refactor`:

- `skills/he-refactor/references/refactor-program-contract.md`
- `skills/he-refactor/references/source-prompt-preservation.md`

`he-linear-plan`:

- `skills/he-linear-plan/references/linear-plan-output-contract.md`
- `skills/he-linear-plan/references/source-prompt-preservation.md`

## Historical Context Policy

Historical compact-entrypoint lines from prior compression passes belong in:

- `fixtures/budget-archive/**`
- `fixtures/preserved-context/**`
- stage `references/source-prompt-preservation.md` files

Do not duplicate active `SKILL.md` procedure text here. If future agents need
an old line for migration evidence, link the historical fixture path and state
why it matters instead of copying the line.

## Drift Signals

- The same reference appears twice under different labels.
- Preserved text copies active stage procedure instead of linking archival context.
- A preserved line contradicts the current stage entrypoint.
- This file grows faster than the referenced stage contracts.
- A validator, eval, or skill entrypoint treats this index as source of truth
  instead of a context router.

## Retired Entry Point Audit Notes

The 2026-05-08 artifact-traceability pass retired several oversized stage
entrypoint paragraphs. Their audit value is preserved by active stage diffs,
the relevant `skills/**/references/source-prompt-preservation.md` files, and
fixtures. Keep this index as a router only; do not paste retired procedure text
back into this file.
