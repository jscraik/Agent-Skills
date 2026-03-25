# CE Brainstorm Prompt Parity Map

Read when: you need to verify that the `workflow-brainstorm.md` prompt was converted into `ce-brainstorm` without losing behavior, or when you are packaging this skill into another distribution surface.

## Table of Contents
- [Purpose](#purpose)
- [Source prompt](#source-prompt)
- [Parity mapping](#parity-mapping)
- [Intentional modernizations](#intentional-modernizations)
- [No-loss checklist](#no-loss-checklist)

## Purpose
This document maps the original prompt at `/Users/jamiecraik/dev/config/codex/prompts/workflow-brainstorm.md` to the skill at `product/ops/ce-brainstorm/` so prompt-to-skill migration stays auditable.

## Source prompt
- Source file: `/Users/jamiecraik/dev/config/codex/prompts/workflow-brainstorm.md`
- Migration target: `/Users/jamiecraik/dev/Agent-Skills/product/ops/ce-brainstorm/`
- Goal: preserve the brainstorm-stage behavior while expressing it as a reusable Codex skill with contracts, evals, and clearer trigger boundaries

## Parity mapping
| Prompt section | Preserved in skill | Notes |
|---|---|---|
| frontmatter `name`, `description`, argument-hint intent | `SKILL.md` frontmatter and `## Required inputs` | `argument-hint` became explicit required-input guidance rather than prompt placeholder syntax |
| Brainstorming answers WHAT to build | `## Working agreement` and `## Constraints` | Preserved directly |
| Feature Description and "do not proceed until provided" | `## Required inputs` | Preserved as a direct blocking question |
| Required Inputs | `## Required inputs` | Preserved directly |
| Constraints | `## Constraints` | Preserved directly, including untrusted-input and no auto-advance behavior |
| Acceptance Criteria | `## Acceptance criteria` | Preserved with artifact path, decision fields, and next-step options |
| Phase 0 assess whether brainstorming is needed | `## Workflow` -> `Phase 0` | Preserved, including the "already clear" branch |
| Phase 1 gather lightweight local context | `## Workflow` -> `Phase 1` | Preserved and made more explicit as bounded parallel subagent use |
| exact use of `repo-research-analyst` and `learnings-researcher` | `## Workflow` -> `Phase 1` | Preserved with exact role names and intent |
| Phase 2 collaborative dialogue | `## Workflow` -> `Phase 2` | Preserved, including one-question-at-a-time and topic coverage |
| Phase 3 explore 2-3 approaches | `## Workflow` -> `Phase 3` | Preserved directly |
| Phase 4 decide whether a spec is required | `## Workflow` -> `Phase 4` | Preserved with `spec_required`, `risk_level`, and `complexity` defaults |
| Phase 5 write brainstorm document | `## Workflow` -> `Phase 5` and `## Brainstorm artifact` | Preserved with frontmatter and required sections |
| rule to resolve material open questions before handoff | `## Workflow` -> `Phase 5` | Preserved directly |
| Phase 6 handoff options | `## Handoff guidance` | Preserved with the same option set |
| Output Summary | `## Output summary` | Preserved as a skill closeout contract |
| Validation | `## Validation` | Preserved and upgraded with explicit fail-fast wording |
| Do Not Do | `## Anti-patterns` | Preserved as skill-native anti-patterns |

## Intentional modernizations
- Prompt-only control syntax such as `default_mode_request_user_input` was translated into environment-agnostic skill guidance, mainly direct questions and `request_user_input` when that reduces ambiguity cleanly.
- `/prompts:workflow-plan` and `/prompts:workflow-spec` style references were translated into workflow-stage guidance so the skill remains usable while prompt surfaces are being deprecated.
- The parallel research step was made more explicit as bounded internal subagent usage because that is easier to preserve reliably in a reusable skill than prompt shorthand.
- The learnings lookup was modernized to check `.harness/memory/LEARNINGS.md` first when present, while retaining `instructions/Learnings.md` as a compatibility fallback so prior prompt behavior is not lost in repos that still use the older path.
- `references/contract.yaml` and `references/evals.yaml` were added to meet the repository’s current skill quality contract.
- Pressure and prompt-injection evals were added because the original prompt relied more on ambient prompt scaffolding than a packaged skill can safely assume.

## No-loss checklist
- The brainstorm stage still focuses on WHAT and WHY rather than implementation sequencing.
- Missing feature descriptions still block progress.
- The "already clear" branch still exists.
- The exact research roles are still named and used in parallel when repo context matters.
- The artifact path and frontmatter expectations are still present.
- `spec_required`, `risk_level`, and `complexity` are still required.
- The same handoff choices still exist.
- The original "do not do" boundaries still exist, now under anti-patterns and constraints.
