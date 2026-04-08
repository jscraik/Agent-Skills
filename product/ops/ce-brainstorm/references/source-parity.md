# CE Brainstorm Source Parity Map

Read when: you need to verify that `ce-brainstorm` preserves the legacy brainstorm prompt behavior while incorporating the newer upstream `compound-engineering-plugin` skill updates without losing repo-local contracts.

## Table of Contents
- [Purpose](#purpose)
- [Source inputs](#source-inputs)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the legacy brainstorm prompt plus the upstream `compound-engineering-plugin` `ce-brainstorm` skill to the local skill at `product/ops/ce-brainstorm/` so upstream-sync and prompt-to-skill migration remain auditable.

## Source inputs
- legacy prompt: `/Users/jamiecraik/dev/configs/codex/prompts/workflow-brainstorm.md`
- upstream donor skill: `https://raw.githubusercontent.com/EveryInc/compound-engineering-plugin/0ae91dcc298721e5b2c4ab6d1fc6f76a13b6f67c/plugins/compound-engineering/skills/ce-brainstorm/SKILL.md`
- migration target: `/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-brainstorm/`
- lightweight review doctrine adapted locally in `references/document-review-pass.md`

## Parity mapping
| Source behavior | Preserved in skill | Notes |
|---|---|---|
| brainstorm answers WHAT to build before HOW | `## Working agreement`, `## Constraints`, `## Workflow` | Preserved directly |
| block when the feature description is missing | `## Required inputs` | Preserved as a direct blocking question |
| resume an existing brainstorm or requirements document instead of duplicating it | `## Workflow` -> `Phase 0.1` | Preserved from upstream, with legacy brainstorm compatibility retained |
| classify software vs non-software tasks before deep brainstorming | `## Workflow` -> `Phase 0.1b` | Preserved and adapted to local routing via `brainstorming` |
| assess whether brainstorming is even needed | `## Workflow` -> `Phase 0.2` | Preserved directly |
| classify scope as lightweight, standard, or deep | `## Workflow` -> `Phase 0.3` | Preserved from upstream |
| run a light repo scan before substantive brainstorming | `## Workflow` -> `Phase 1.1` | Preserved directly |
| optional bounded internal support for deeper work | `## Workflow` -> `Phase 1.1` | Preserved via `references/bounded-subagent-support.md` with explicit approval gate |
| pressure-test the request before locking in options | `## Workflow` -> `Phase 1.2` | Preserved from upstream |
| one-question-at-a-time collaborative dialogue | `## Workflow` -> `Phase 1.3` | Preserved directly, including "ask what the user is already thinking" |
| compare 2-3 options and recommend one | `## Workflow` -> `Phase 2` | Preserved with non-obvious-angle exploration and anti-anchoring order (options first, then recommendation) |
| decide `spec_required`, `risk_level`, and `complexity` | `## Workflow` -> `Phase 3` | Preserved directly |
| create a durable requirements doc with stable IDs and blocking/deferred questions | `## Workflow` -> `Phase 4` | Preserved from upstream and aligned to local planning contracts |
| include visual aids when they materially improve comprehension | `## Workflow` -> `Phase 4` | Preserved from upstream |
| run a lightweight document-review pass after writing the requirements doc | `## Workflow` -> `Phase 5`, `references/document-review-pass.md` | Preserved from upstream via local adaptation |
| hand off into spec, planning, or direct work only when blocker state permits it | `## Workflow` -> `Phase 6` | Preserved and adapted to local CE skill names |
| concise completion or pause summary | `## Output summary` | Preserved directly |
| fail-fast validation and anti-pattern boundaries | `## Validation`, `## Anti-patterns`, `references/brainstorm-workflow-details.md` | Preserved and upgraded with repo-specific checks |

## Intentional modernizations
- Prompt-only control syntax such as `argument-hint` and slash-command handoffs were translated into durable skill guidance plus local `ce-spec`, `ce-plan`, and `ce-work` handoff language.
- The upstream `requirements doc` contract was adopted for new substantial work because local `ce-plan` already prefers `docs/brainstorms/*-requirements.md` as the primary planning source.
- Legacy `docs/brainstorms/*-brainstorm.md` artifacts remain supported for resume-in-place compatibility rather than forced renames.
- The upstream `document-review` step was preserved via the local `references/document-review-pass.md` adaptation, matching how other CE skills in this repo keep lightweight review behavior without creating a duplicate sibling skill.
- Internal delegation guidance was retained, but made explicit that it only applies when the runtime and session policy permit it.
- Detailed pressure-test prompts, output closeout templates, and validation checklist remain preserved in `references/brainstorm-workflow-details.md` to keep `SKILL.md` routing-focused without context loss.
- `references/contract.yaml` and `references/evals.yaml` remain the local source of truth for packaging-grade validation.

## No-loss checklist
- The brainstorm stage still focuses on WHAT and WHY rather than implementation sequencing.
- Missing feature descriptions still block progress.
- The "already clear" branch still exists.
- Existing requirements or brainstorm docs are resumable rather than duplicated.
- Scope is still classified before the main conversation deepens.
- Optional bounded internal support is still constrained by explicit approval and runtime policy.
- The product pressure test is now preserved explicitly.
- `spec_required`, `risk_level`, and `complexity` are still required.
- Durable output is still captured in `docs/brainstorms/`, now aligned to local requirements-doc naming for new work.
- Lightweight document review is explicitly preserved before handoff.
- The original "do not do" boundaries still exist, now under anti-patterns and constraints.
