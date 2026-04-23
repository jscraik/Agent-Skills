# HE Deepen Plan Prompt Parity Map

Read when: you need to verify that the legacy `deepen-plan` and `deepen-plan-beta` prompts were merged into `he-deepen-plan` without losing behavior.

## Table of Contents
- [Purpose](#purpose)
- [Source prompts](#source-prompts)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the original plan-deepening prompts to `product/Infrastructure/ops/he-deepen-plan/` so the prompt-to-skill migration stays auditable.

## Source prompts
- `configs/codex/prompts/deepen-plan.md`
- user-provided legacy `deepen-plan` prompt body with broad skill/agent discovery
- user-provided `deepen-plan-beta` prompt body with selective, risk-weighted deepening
- lightweight review doctrine imported from upstream `ce-doc-review` snapshot commit `d8436b9a3c5b5370e51ec168a251ccb45f0d826e`, now tracked in local Harness Engineering migration notes
- migration target: `product/Infrastructure/ops/he-deepen-plan/`

## Parity mapping
| Prompt behavior | Preserved in skill | Notes |
|---|---|---|
| deepen an existing plan instead of creating a new one | `SKILL.md` overall structure and `## Workflow` | Preserved directly |
| require a valid plan path before proceeding | `## Required inputs`, `Workflow -> Phase 0` | Preserved directly |
| read plan plus linked artifacts (`origin`, spec) | `Workflow -> Phase 0` | Preserved directly |
| preserve original plan structure and intent | `## Working agreement`, `## Constraints`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| identify weak sections before rewriting | `Workflow -> Phase 1`, `Infrastructure/references/deepening-modes.md` | Preserved directly from beta |
| classify plan depth and topic risk | `Workflow -> Phase 0`, `Infrastructure/references/deepening-modes.md` | Preserved directly from beta |
| selective deepening of only the weakest 2-5 sections | `Workflow -> Phase 2`, `Infrastructure/references/deepening-modes.md` | Preserved directly from beta |
| broad section manifest and enhancement-summary behavior | `Workflow -> Phases 1 and 5`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| local repo research plus learnings research | `Workflow -> Phase 3` | Preserved directly |
| deeper learnings under `docs/solutions/` | `Workflow -> Phase 3`, `max-coverage` mode | Preserved directly from legacy prompt |
| conditional external research and Context7 grounding | `Workflow -> Phase 3` | Preserved directly |
| broad skill discovery and reviewer fan-out | `Workflow -> Phase 2`, `max-coverage` mode | Preserved as explicit legacy-compatible mode |
| direct vs artifact-backed synthesis | `Workflow -> Phase 4`, `Infrastructure/references/deepening-modes.md` | Preserved directly from beta |
| strengthen sequencing, validation, risks, rollout, and operational detail | `Workflow -> Phase 5`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| update plan in place by default or `-deepened` on request | `Workflow -> Phase 6` | Preserved directly |
| post-deepening next-step options | `## Handoff guidance` | Preserved directly |

## Intentional modernizations
- The two prompt variants were merged into one mode-aware skill:
  - `targeted-confidence` is the modern default
  - `max-coverage` preserves the legacy exhaustive fan-out path
- Hardcoded Codex-specific cache paths and plugin-file discovery were generalized into current-platform/project/plugin-registry discovery guidance so the behavior survives prompt deprecation and works outside a single runtime layout.
- Learnings lookup was modernized to check `.harness/memory/LEARNINGS.md` first when present, then `instructions/Learnings.md`, then deeper `docs/solutions/` entries.
- The beta prompt's section scoring, selective fan-out, and artifact-backed mode were kept as the safer default because they reduce context bloat without losing the ability to run a legacy-style broad pass when explicitly requested.
- `document-review` / workflow slash-command references were translated into workflow-stage guidance and `he-work` handoff language so the skill remains usable while prompt surfaces are being deprecated.
- `Infrastructure/references/contract.yaml` and `Infrastructure/references/evals.yaml` were added to meet current skill quality requirements and improve routing reliability.
- The upstream `ce-doc-review` workflow was preserved as a lightweight pre-execution refinement pass for plan docs via `Infrastructure/references/document-review-pass.md`, and is now tracked via local Harness Engineering migration notes rather than an external plugin URL.

## No-loss checklist
- Existing plans are still the required input.
- Deepening still preserves plan intent rather than rewriting from scratch.
- A lightweight document-review pass is now explicitly preserved for plan-quality refinement when full deepening would be excessive.
- Enhancement Summary behavior is still present.
- Linked origin/spec artifacts are still read when present.
- Local repo research and prior learnings are still used.
- `docs/solutions/` learning scans are still available.
- Broad skill and reviewer fan-out is still available in `max-coverage` mode.
- Selective, risk-weighted deepening is still available and is now the default.
- Artifact-backed synthesis is still available for bulky research.
- The output is still a stronger plan, not implementation code.
