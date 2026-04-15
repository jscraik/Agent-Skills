# CE Spec Prompt Parity Map

Read when: you need to verify that `workflow-spec.md`, `workflow-spec-ui.md`, and `workflow-ui-spec.md` were merged into `ce-spec` without losing behavior, or when packaging this skill into another surface.

## Table of Contents
- [Purpose](#purpose)
- [Source prompts](#source-prompts)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the original specification prompts in `/Users/jamiecraik/dev/configs/codex/prompts/` to the skill at `product/Infrastructure/ops/ce-spec/` so the prompt-to-skill migration stays auditable.

## Source prompts
- `/Users/jamiecraik/dev/configs/codex/prompts/workflow-spec.md`
- `/Users/jamiecraik/dev/configs/codex/prompts/workflow-spec-ui.md`
- `/Users/jamiecraik/dev/configs/codex/prompts/workflow-ui-spec.md`
- Migration target: `/Users/jamiecraik/dev/Agent-Skills/product/Infrastructure/ops/ce-spec/`

## Parity mapping
| Prompt surface | Preserved in skill | Notes |
|---|---|---|
| `workflow-spec` spec-only contract | `SKILL.md` overall structure, `## Constraints`, `## Workflow` | Preserved directly |
| source resolution order and spec-depth decision | `## Workflow` -> `Phase 0` | Preserved directly |
| `none | lite | full` depth logic | `## Workflow` -> `Phase 0`, `## Deliverables` | Preserved directly |
| `ui_required: true` detection in standard specs | `## Workflow` -> `Phase 0`, `## Validation` | Preserved directly |
| local research with `repo-research-analyst` and `learnings-researcher` | `## Workflow` -> `Phase 1` | Preserved with exact role names, hard caps, and updated learnings path |
| conditional external research | `## Workflow` -> `Phase 2` | Preserved directly |
| system-spec contract questions and required sections | `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved directly |
| mandatory `SA` IDs | `## Acceptance criteria`, `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved directly |
| post-write verification | `## Workflow` -> `Phase 5`, `## Validation` | Preserved directly |
| `workflow-spec-ui` design-aware UI contract | `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved and merged into dedicated UI-spec mode |
| `workflow-spec-ui` instrumentation, UX metrics, and decision log | `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved directly |
| `workflow-ui-spec` component inventory, states, tokens, accessibility, responsiveness | `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved directly |
| mandatory `VAC` IDs | `## Acceptance criteria`, `## Workflow` -> `Phase 3`, `Infrastructure/references/spec-artifacts.md` | Preserved directly |
| UI-spec handoff into UI planning and main planning | `## Handoff guidance`, `## Spec modes` | Preserved directly with skill-native routing |
| validation and do-not-do boundaries | `## Validation`, `## Anti-patterns`, `## Constraints` | Preserved directly |

## Intentional modernizations
- The three prompts were merged into one mode-aware skill instead of remaining separate prompt files. This preserves behavior while reducing routing ambiguity.
- Prompt-only control syntax such as `default_mode_request_user_input` was translated into environment-agnostic skill guidance with direct follow-up questions and `request_user_input` when that reduces ambiguity cleanly.
- Prompt references were translated into skill-stage guidance so the workflow stays usable while prompt surfaces are being deprecated.
- The learnings lookup was modernized to check `.harness/memory/LEARNINGS.md` first when present, while keeping `instructions/Learnings.md` as a compatibility fallback.
- UI artifact path handling was made explicit:
  - prefer `docs/ui-specs/` for dedicated UI specs
  - preserve the older `Docs/specs/...-ui-spec.md` form as a compatibility mode when the repo or user requires it
- `Infrastructure/references/contract.yaml` and `Infrastructure/references/evals.yaml` were added to meet current skill quality requirements and strengthen routing reliability.
- Pressure and prompt-injection evals were added because the original prompts relied more on ambient scaffolding than a packaged skill can safely assume.

## No-loss checklist
- Standard specs still answer WHAT, boundaries, lifecycle, failure, observability, and validation.
- Missing source inputs still block progress.
- Spec-depth selection still distinguishes `none`, `lite`, and `full`.
- The exact local research roles are still named and used in parallel.
- Conditional external research is still present for high-risk or externally dependent work.
- `ui_required: true` detection is still present in standard specs.
- Stable `SA` and `VAC` behaviors are still present.
- UI-specific instrumentation, UX metrics, and decision-log requirements are still present.
- The original do-not-do boundaries still exist, now under constraints and anti-patterns.
