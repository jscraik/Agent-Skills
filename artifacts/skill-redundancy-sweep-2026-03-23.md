# Skill Redundancy Sweep

Date: 2026-03-23
Mode: `skill-builder` audit
Scope: canonical skill set only

## Method

- Counted canonical skills by scanning repo `SKILL.md` files and excluding:
  - repo-root `SKILL.md`
  - `skills-antigravity/` projection copies
  - `plugins/` mirrored skill copies
- Canonical skills reviewed: `118`
- Read the highest-overlap families directly instead of trusting description similarity alone.

## Headline finding

There are no strong canonical duplicate skills that obviously need immediate merging.

The main source of apparent redundancy is:

1. projection and mirror copies, not canonical duplication;
2. generic skills intentionally paired with CE-specialized or tracker-specialized variants;
3. router skills intentionally paired with implementation or execution skills.

## Exact redundancy

Exact duplication exists only in distribution layers, not in the canonical skill graph:

- `skills-antigravity/*`
- `plugins/*/skills/*`

These should be treated as projections or packaging mirrors, not merge candidates.

## Healthy neighbor groups

These families overlap in topic, but the boundary is real and currently defensible.

### Browser verification family

- [`frontend/tools/test-browser/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/tools/test-browser/SKILL.md)
- [`utilities/agent-browser/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/agent-browser/SKILL.md)
- [`frontend/tools/playwright-interactive/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/tools/playwright-interactive/SKILL.md)
- [`frontend/ui/ui-visual-regression/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/ui-visual-regression/SKILL.md)

Why they are separate:

- `test-browser` is the QA router for changed routes and flows.
- `agent-browser` is the deterministic operator surface.
- `playwright-interactive` is the persistent local debugging lane.
- `ui-visual-regression` is snapshot/diff specific.

Assessment: keep separate.

### Review family

- [`product/ops/ce-review/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-review/SKILL.md)
- [`product/ops/ce-technical-review/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-technical-review/SKILL.md)
- [`github/greptile/check-pr/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/github/greptile/check-pr/SKILL.md)
- [`github/gh-workflow/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/github/gh-workflow/SKILL.md)
- [`product/review/agent-native-audit/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/review/agent-native-audit/SKILL.md)

Why they are separate:

- `ce-review` is broad readiness and next-step synthesis.
- `ce-technical-review` is findings-first engineering critique.
- `check-pr` is GitHub plus Greptile policy-gated pre-merge readiness.
- `gh-workflow` is lifecycle execution for issues, PRs, checks, and merge actions.
- `agent-native-audit` is architecture/workflow audit against agent-native principles.

Assessment: keep separate.

### Ideation, spec, and planning family

- [`product/strategy/brainstorming/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/strategy/brainstorming/SKILL.md)
- [`product/ops/ce-ideate/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-ideate/SKILL.md)
- [`product/ops/ce-brainstorm/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-brainstorm/SKILL.md)
- [`product/specs/product-spec/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/specs/product-spec/SKILL.md)
- [`product/ops/ce-spec/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-spec/SKILL.md)
- [`utilities/writing-plans/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/writing-plans/SKILL.md)
- [`product/ops/ce-plan/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md)
- [`product/ops/ce-deepen-spec/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-deepen-spec/SKILL.md)
- [`product/ops/ce-deepen-plan/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-deepen-plan/SKILL.md)

Why they are separate:

- `ce-ideate` chooses which ideas deserve deeper exploration.
- `brainstorming` is generic ambiguity and trade-off clarification.
- `ce-brainstorm` is the CE stage with `spec_required`, `risk_level`, and artifact handoff.
- `product-spec` is the multi-mode PRD/UX/API/architecture/test-plan pipeline.
- `ce-spec` is the narrower implementation-grade WHAT contract before planning.
- `writing-plans` is a generic execution-plan writer.
- `ce-plan` is the CE planning stage with phase IDs, traceability, rollout, and UI-specific planning rules.
- `ce-deepen-*` are second-pass hardening stages rather than initial creation stages.

Assessment: keep separate.

### Todo and execution family

- [`product/ops/triage/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/triage/SKILL.md)
- [`product/ops/resolve-todo-parallel/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/resolve-todo-parallel/SKILL.md)
- [`product/ops/ce-work/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-work/SKILL.md)
- [`utilities/simple-tasks/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/simple-tasks/SKILL.md)

Why they are separate:

- `triage` approves or skips file-based `todos/` items.
- `resolve-todo-parallel` executes a bounded todo sweep.
- `ce-work` is the general CE execution lane for plans, todo files, or small specs.
- `simple-tasks` installs a separate local `tasks/TASKS.md` workflow and does not execute product work itself.

Assessment: keep separate.

### Debugging and tracker family

- [`utilities/systematic-debugging/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/systematic-debugging/SKILL.md)
- [`utilities/reproduce-bug/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/reproduce-bug/SKILL.md)
- [`product/ops/linear/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/linear/SKILL.md)

Why they are separate:

- `systematic-debugging` is generic root-cause diagnosis before code changes.
- `reproduce-bug` is tracker-led reproduction and investigation, preferably from Linear.
- `linear` is issue/project/document operations, not reproduction or debugging.

Assessment: keep separate.

### Frontend design family

- [`frontend/ui/frontend-design/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/SKILL.md)
- [`frontend/ui/frontend-ui-design/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-ui-design/SKILL.md)
- [`frontend/ui/ui-ux-creative-coding/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/ui-ux-creative-coding/SKILL.md)
- [`frontend/ui/design-system/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/design-system/SKILL.md)

Why they are separate:

- `frontend-design` is an ambiguity router and compatibility front door.
- `frontend-ui-design` owns production-ready UI design work.
- `ui-ux-creative-coding` owns post-direction motion and polish.
- `design-system` owns token and theme architecture.

Assessment: keep separate.

## Highest trigger-blur risks

These are not merge recommendations, but they are the places where a caller could plausibly trigger the wrong skill.

### 1. `gh-workflow` vs `check-pr`

Why it blurs:

- both can be invoked for PR checks, review state, and pre-merge questions;
- `gh-workflow` is broad enough to absorb readiness review requests;
- `check-pr` is only clearly distinct if the caller understands the Greptile and policy-gate layer.

Why not merge:

- `check-pr` is a governance review skill;
- `gh-workflow` is an operations skill.

Recommendation:

- tighten `gh-workflow` examples to emphasize action-taking lifecycle work;
- tighten `check-pr` opening line to emphasize policy-gated readiness classification, not generic PR handling.

### 2. `ce-review` vs `ce-technical-review`

Why it blurs:

- both accept PRs, branches, diffs, specs, and plans;
- both produce readiness guidance and findings.

Why not merge:

- `ce-review` is package-level readiness synthesis;
- `ce-technical-review` is engineering-risk-first critique.

Recommendation:

- keep both, but make the first sentence of each description even more contrastive:
  - `ce-review`: broad readiness and next-step decision
  - `ce-technical-review`: findings-first technical critique

### 3. `brainstorming` vs `ce-brainstorm`

Why it blurs:

- both clarify direction before planning;
- both compare 2-3 options and recommend one.

Why not merge:

- `brainstorming` is a general-purpose clarifier;
- `ce-brainstorm` is a formal CE stage with artifact, `spec_required`, `risk_level`, and `complexity`.

Recommendation:

- add “generic/non-CE” language to `brainstorming`;
- add “artifact-producing CE workflow stage” language to `ce-brainstorm`.

### 4. `writing-plans` vs `ce-plan`

Why it blurs:

- both create execution-ready implementation plans.

Why not merge:

- `writing-plans` is a generic planner;
- `ce-plan` carries CE-specific artifact rules, stable IDs, rollout, UI planning modes, and planning-stage handoff.

Recommendation:

- make the generic-vs-CE distinction more explicit in the description line of both skills.

### 5. `product-spec` vs `ce-spec`

Why it blurs:

- both produce implementation-ready specs from ideas or existing docs.

Why not merge:

- `product-spec` is a multi-mode product planning pipeline;
- `ce-spec` is a narrower implementation contract stage for CE handoff into planning.

Recommendation:

- keep separate, but consider sharper frontmatter phrasing:
  - `product-spec`: product-planning artifact pipeline
  - `ce-spec`: implementation-grade system/UI contract before CE planning

## Weak merge candidates

No merge candidate looks urgent.

The closest optional fold candidate is:

- `check-pr` into `gh-workflow` as a strict `pr_readiness` mode.

Why it is still better left separate for now:

- `check-pr` has a different authority model, review posture, and policy gate;
- keeping it separate prevents the operational GitHub skill from swallowing review-governance behavior.

## Recommendations

### Recommendation 1

Do not merge canonical skills right now.

The graph is more specialized than redundant.

### Recommendation 2

Run a wording-tightening pass on the five highest trigger-blur pairs:

- `gh-workflow` vs `check-pr`
- `ce-review` vs `ce-technical-review`
- `brainstorming` vs `ce-brainstorm`
- `writing-plans` vs `ce-plan`
- `product-spec` vs `ce-spec`

### Recommendation 3

Prefer overlap matrices for the blurriest families.

This pattern already exists and works well in:

- [`frontend/ui/frontend-design/references/overlap-matrix.md`](/Users/jamiecraik/dev/Agent-Skills/frontend/ui/frontend-design/references/overlap-matrix.md)
- [`product/ops/triage/references/overlap-matrix.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/triage/references/overlap-matrix.md)

The review and planning families would benefit from the same treatment.

## Bottom line

The canonical graph is not suffering from major duplicate-skill bloat.

It is suffering more from boundary clarity risk than from true redundancy.

If cleanup time is limited, the highest-leverage next move is not merging skills. It is tightening routing language in the few pairs where generic and specialized lanes sit very close together.

## Re-review after planning fold

Update after the second pass on 2026-03-23:

- `writing-plans` has been folded into [`product/ops/ce-plan/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/SKILL.md) as the canonical planning owner.
- [`utilities/writing-plans/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/utilities/writing-plans/SKILL.md) now acts as a compatibility wrapper that routes to `ce-plan` in `generic-plan` mode.
- direct cross-skill references that previously pointed to `[[writing-plans]]` were updated to `[[ce-plan]]` in neighboring skills and topic maps.

Revised assessment for the planning family:

- `writing-plans` vs `ce-plan`: no longer a true redundancy risk in practice.
- residual overlap remains only as compatibility surface area, not as competing doctrine.
- `product-spec` vs `ce-spec` remains intentionally separate and still should not be folded.

Net result:

- one real redundancy cluster has been reduced;
- the planning family is now cleaner;
- the remaining graph risk is concentrated in wording and boundary clarity, especially `gh-workflow` vs `check-pr` and `ce-review` vs `ce-technical-review`.

## Re-review after description hardening

Update after the third pass on 2026-03-23:

- [`github/gh-workflow/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/github/gh-workflow/SKILL.md) now frames itself explicitly as the GitHub operations lane that changes or advances GitHub state.
- [`github/greptile/check-pr/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/github/greptile/check-pr/SKILL.md) now frames itself explicitly as a readiness-classification lane that does not advance the lifecycle.
- [`product/ops/ce-review/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-review/SKILL.md) now emphasizes package-level readiness, go/no-go synthesis, and stage-aware next actions.
- [`product/ops/ce-technical-review/SKILL.md`](/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-technical-review/SKILL.md) now emphasizes a findings-first engineering issue list with exact locations and minimal fixes.

Revised assessment:

- `gh-workflow` vs `check-pr`: still adjacent, but materially less blurry than before. The boundary is now understandable from the first paragraph.
- `ce-review` vs `ce-technical-review`: still close in input shape, but the output intent is now much clearer and should route more reliably.

Current highest-risk blur after this pass:

- `gh-workflow` vs `check-pr` remains the blurriest pair in the repo, but it has moved from "likely mis-trigger" to "manageable with current wording".
- `ce-review` vs `ce-technical-review` now looks acceptable without an immediate structural change.
