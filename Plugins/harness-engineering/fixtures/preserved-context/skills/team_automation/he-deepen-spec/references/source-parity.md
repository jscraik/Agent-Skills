# HE Deepen Spec Prompt Parity Map

Read when: you need to verify that the legacy `deepen-spec` prompt was migrated into `he-deepen-spec` without losing behavior, or when packaging this skill into another surface.

## Table of Contents
- [Purpose](#purpose)
- [Source prompts and donor patterns](#source-prompts-and-donor-patterns)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the original spec-deepening prompt in `configs/codex/prompts/` to the skill at `product/Infrastructure/ops/he-deepen-spec/` so the prompt-to-skill migration stays auditable.

## Source prompts and donor patterns
- `configs/codex/prompts/deepen-spec.md`
- donor patterns borrowed intentionally from `product/Infrastructure/ops/he-deepen-plan/`
- spec-structure alignment borrowed intentionally from `product/Infrastructure/ops/he-spec/`
- lightweight review doctrine imported from upstream `ce-doc-review` snapshot commit `d8436b9a3c5b5370e51ec168a251ccb45f0d826e`, now tracked in local Harness Engineering migration notes
- migration target: `product/Infrastructure/ops/he-deepen-spec/`

## Parity mapping
| Prompt behavior | Preserved in skill | Notes |
|---|---|---|
| deepen an existing spec instead of creating a new one | `SKILL.md` overall structure and `## Workflow` | Preserved directly |
| require a valid spec path before proceeding | `## Required inputs`, `Workflow -> Phase 0` | Preserved directly |
| read spec plus linked artifacts (`origin`, linked plan) | `Workflow -> Phase 0` | Preserved directly, with `parent_spec:` support added |
| extract and target core spec sections for enhancement | `Workflow -> Phase 1`, `Infrastructure/references/deepening-modes.md` | Preserved directly |
| identify weak spots like vague entities, missing state, weak observability, and hidden trust assumptions | `Workflow -> Phase 1`, `Infrastructure/references/deepening-modes.md` | Preserved directly |
| run repo research plus learnings research in parallel | `Workflow -> Phase 3` | Preserved directly |
| check `instructions/Learnings.md` before deeper learnings | `Workflow -> Phase 3` | Preserved with `.harness/memory/LEARNINGS.md` first and compatibility fallback retained |
| conditional best-practices and framework-docs research | `Workflow -> Phase 3` | Preserved directly |
| strengthen boundary clarity, state, failure handling, safety, observability, and validation | `Workflow -> Phase 5`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| preserve structure where possible and tighten rather than bloat | `## Working agreement`, `## Constraints`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| add a short Enhancement Summary near the top | `Workflow -> Phase 6`, `Infrastructure/references/rewrite-rules.md` | Preserved directly |
| update in place by default or write `-deepened` variant on request | `Workflow -> Phase 6` | Preserved directly |
| offer next steps after writing | `## Handoff guidance`, `Workflow -> Phase 6` | Preserved directly |

## Intentional modernizations
- The legacy prompt was upgraded into a mode-aware skill:
  - `targeted-confidence` is the safer default
  - `max-coverage` preserves the optional exhaustive path when explicitly requested
- Deepening now explicitly supports both standard specs and UI-spec artifacts, borrowing the stable `SA` and `VAC` handling patterns from `he-spec`.
- Learnings lookup was modernized to check `.harness/memory/LEARNINGS.md` first when present, then `instructions/Learnings.md`, then directly relevant `docs/solutions/` entries.
- The `he-deepen-plan` pattern of `direct` versus `artifact-backed` research execution was adopted so large high-risk deepening passes stay manageable without dropping findings.
- Slash-command references like `/prompts:technical_review` and `/prompts:workflow-plan` were translated into durable handoff guidance such as technical review and `he-plan`.
- `Infrastructure/references/contract.yaml` and `Infrastructure/references/evals.yaml` were added to meet current skill quality requirements and improve routing reliability.
- The upstream `ce-doc-review` workflow was preserved as a lightweight pre-planning refinement pass for requirements/spec docs via `Infrastructure/references/document-review-pass.md`, and is now tracked via local Harness Engineering migration notes rather than an external plugin URL.

## No-loss checklist
- Existing specs are still the required input.
- Deepening still preserves spec intent rather than rewriting from scratch.
- A lightweight document-review pass is now explicitly preserved for spec-quality refinement when full contract deepening would be excessive.
- Linked artifacts are still read when present.
- Weak-spot identification is still central to the workflow.
- Local repo research and prior learnings are still used.
- Conditional external research is still available.
- Enhancement Summary behavior is still present.
- Update-in-place and `-deepened` output options are still present.
- The output is still a stronger spec, not code or a task plan.
- The skill now keeps the original deepen-spec behavior while improving mode selection, ID preservation, and deepening-stage safety.
