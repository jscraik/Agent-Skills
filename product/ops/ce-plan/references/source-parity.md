# CE Plan Prompt Parity Map

Read when: you need to verify that `workflow-plan.md`, `workflow-plan-ui.md`, `workflow-ui-plan.md`, and `ce:plan-beta` were merged into `ce-plan` without losing behavior, or when packaging this skill into another surface.

## Table of Contents
- [Purpose](#purpose)
- [Source prompts](#source-prompts)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the original planning prompts in `/Users/jamiecraik/dev/config/codex/prompts/` to the skill at `product/ops/ce-plan/` so the prompt-to-skill migration stays auditable.

## Source prompts
- `/Users/jamiecraik/dev/config/codex/prompts/workflow-plan.md`
- `/Users/jamiecraik/dev/config/codex/prompts/workflow-plan-ui.md`
- `/Users/jamiecraik/dev/config/codex/prompts/workflow-ui-plan.md`
- `/Users/jamiecraik/dev/config/codex/prompts/ce:plan-beta` (prompt body provided by user during merge/update)
- Migration target: `/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-plan/`

## Parity mapping
| Prompt surface | Preserved in skill | Notes |
|---|---|---|
| `workflow-plan` general planning contract | `SKILL.md` overall structure, `## Workflow`, `## Artifact contracts`, `## Planning-mode handshake` | Preserved directly |
| planning answers HOW, not contract invention | `## Working agreement`, `## Constraints` | Preserved directly |
| source resolution order | `## Workflow` -> `Phase 0` | Preserved and split by general vs UI mode |
| spec-first and brainstorm fallback logic | `## Workflow` -> `Phase 0` | Preserved directly |
| `ui_required: true` gate | `## Workflow` -> `Phase 0` and `## Plan modes` | Preserved as explicit UI-enhanced branch |
| local research with `repo-research-analyst` and `learnings-researcher` | `## Workflow` -> `Phase 1` | Preserved with exact role names, hard caps, and updated learnings path |
| conditional external research | `## Workflow` -> `Phase 2` | Preserved directly |
| consolidate constraints, non-goals, invariants, and learnings | `## Workflow` -> `Phase 3` | Preserved directly |
| stable `P` and `AC` IDs | `## Workflow` -> `Phase 4`, `## Acceptance criteria` | Preserved directly |
| traceability matrix and execution control | `## Workflow` -> `Phase 4`, `## Artifact contracts` | Preserved directly |
| Execution Ledger + planning-mode sync | `## Artifact contracts`, `## Planning-mode handshake` | Preserved directly |
| spec-flow gap analysis | `## Workflow` -> `Phase 6` | Preserved directly |
| post-write verification and fail-fast patching | `## Workflow` -> `Phase 8`, `## Validation` | Preserved directly |
| `workflow-plan-ui` Prototype Pack brief | `## Workflow` -> `Phase 5` | Preserved as the `ui-enhanced-plan` prototype-pack branch |
| `workflow-plan-ui` prototype-to-production mapping | `## Workflow` -> `Phase 5` | Preserved directly |
| `workflow-ui-plan` dedicated UI artifact and `UP` / `UAC` / `VAC` rules | `## Workflow` -> `Phase 5`, `## Artifact contracts` | Preserved as the `dedicated-ui-plan` branch |
| `workflow-ui-plan` prototype-first direction phase | `## Workflow` -> `Phase 5` | Preserved directly as the dedicated UI mode default |
| `ce:plan-beta` WHAT/HOW/WORK framing | `## Working agreement` | Preserved directly |
| `ce:plan-beta` existing-plan resume/update behavior | `## Workflow` -> `Phase 0` | Preserved directly |
| `ce:plan-beta` recent `*-requirements.md` search and source-document carry-forward | `## Workflow` -> `Phase 0`, `## Validation` | Preserved directly |
| `ce:plan-beta` no-doc planning bootstrap | `## Workflow` -> `Phase 0` | Preserved directly |
| `ce:plan-beta` blocker reclassification (product vs planning-owned) | `## Workflow` -> `Phase 0`, `## Validation` | Preserved directly |
| `ce:plan-beta` plan depth (`lightweight | standard | deep`) | `## Workflow` -> `Phase 0`, `references/plan-artifacts.md` | Preserved directly |
| `ce:plan-beta` execution posture signals (`test-first`, `characterization-first`, `external-delegate`) | `## Workflow` -> `Phase 1`, `references/plan-artifacts.md` | Preserved directly |
| `ce:plan-beta` sharper external-research decisioning based on repo maturity | `## Workflow` -> `Phase 2` | Preserved in condensed form |
| `ce:plan-beta` planning-time vs implementation-time unknown separation | `## Workflow` -> `Phase 3`, `references/plan-artifacts.md` | Preserved directly |
| `ce:plan-beta` optional high-level technical design and per-unit technical design | `## Workflow` -> `Phase 4`, `references/plan-artifacts.md` | Preserved directly |
| `ce:plan-beta` richer implementation-unit contract | `## Workflow` -> `Phase 4`, `references/plan-artifacts.md` | Preserved directly |
| `ce:plan-beta` deep-plan optional extensions | `references/plan-artifacts.md` | Preserved directly |
| old post-generation options | `## Handoff guidance` | Preserved as one merged option set |
| validation and do-not-do boundaries | `## Validation`, `## Anti-patterns`, `## Constraints` | Preserved directly |

## Intentional modernizations
- The three prompts were merged into a single mode-aware skill instead of remaining separate prompt files. This preserves behavior while reducing routing ambiguity.
- Prompt-only control syntax such as `default_mode_request_user_input` was translated into environment-agnostic skill guidance with direct follow-up questions and `request_user_input` when that reduces ambiguity cleanly.
- `/prompts:...` references were translated into workflow-stage guidance so the skill remains usable while prompt surfaces are being deprecated.
- The learnings lookup was modernized to check `.harness/memory/LEARNINGS.md` first when present, while keeping `instructions/Learnings.md` as a compatibility fallback.
- UI artifact path handling was made explicit:
  - prefer `docs/ui-plans/` for dedicated UI plans
  - preserve the older `docs/plans/...-ui-plan.md` form as a compatibility mode when the repo or user requires it
- Prototype planning differences were preserved as mode-specific rules rather than flattened away:
  - 3 variants for dedicated UI-direction planning
  - 4-variant Prototype Pack brief for broader UI+technical delivery plans
- `references/contract.yaml` and `references/evals.yaml` were added to meet current skill quality requirements and strengthen routing reliability.
- Pressure and prompt-injection evals were added because the original prompts relied more on ambient scaffolding than a packaged skill can safely assume.
- Tracker creation was modernized into an explicit `[[linear]]` handoff so plan generation and issue mutation stay separated while still preserving the original post-plan issue workflow intent.
- The beta prompt's `-beta-plan.md` filename pattern was not adopted into stable `ce-plan`; the canonical skill keeps the existing stable plan filename convention to avoid unnecessary artifact churn across the repo. This is an intentional portability decision, not a loss of planning behavior.
- The beta prompt's inline Proof-share and tracker-mutation branches were not moved into the core planning skill. `ce-plan` remains focused on producing the plan artifact, then handing off to dedicated tracker workflows such as `[[linear]]`.

## No-loss checklist
- General planning still answers HOW and not the contract-level WHAT.
- Missing planning sources still block progress.
- Spec-first behavior still wins when a spec exists.
- Brainstorms that still require a spec still block planning.
- The exact local research roles are still named and used in parallel.
- Conditional external research is still present for high-risk or externally dependent work.
- Stable `P` / `AC` and `UP` / `UAC` / `VAC` behaviors are still present.
- Execution Ledger and planning-mode synchronization are still present.
- Prototype planning, accessibility, visual validation, and rollout work are still present.
- The original do-not-do boundaries still exist, now under constraints and anti-patterns.
- Existing-plan revision, requirements-doc sourcing, plan-depth classification, execution-posture signals, and richer implementation-unit contracts are all present after the beta merge.
