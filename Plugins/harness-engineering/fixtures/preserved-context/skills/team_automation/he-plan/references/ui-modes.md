# Harness Engineering Plan UI Mode Matrix

Read when: you need to choose between `standard-plan`, `ui-enhanced-plan`, and `dedicated-ui-plan`, or when preserving legacy UI-planning behavior during migration.

## Table of Contents
- [Purpose](#purpose)
- [Mode selection](#mode-selection)
- [Artifact paths](#artifact-paths)
- [Prototype planning](#prototype-planning)
- [UI source precedence](#ui-source-precedence)
- [Runtime compatibility note](#runtime-compatibility-note)

## Purpose
This note preserves the nuanced UI-planning differences across `workflow-plan-ui.md` and `workflow-ui-plan.md` without forcing them into one flattened rule set.

## Mode selection
Use `standard-plan` when:
- UI is not a major sequencing concern
- one main delivery plan is enough

Use `ui-enhanced-plan` when:
- the main delivery plan is still the primary artifact
- UI materially affects sequencing, testing, rollout, or stakeholder review
- you need a Prototype Pack brief and prototype-to-production mapping inside the broader plan

Use `dedicated-ui-plan` when:
- the user explicitly asks for a UI implementation plan
- a UI spec is the primary source
- the main challenge is component dependency order, design tokens, accessibility, or visual validation

## Artifact paths
Preferred dedicated UI artifact:
- `docs/ui-plans/YYYY-MM-DD-<descriptive-name>-ui-plan.md`

Compatibility artifact:
- `.harness/plan/YYYY-MM-DD-<topic>-ui-plan.md`

Use the compatibility path only when:
- the repo already stores UI plans that way, or
- the user explicitly asks for it

## Prototype planning
Dedicated UI plan default:
- 3 throwaway direction variants:
  - `A` conservative
  - `B` optimal
  - `C` experimental

UI-enhanced plan default:
- Prototype Pack brief with exactly 4 stakeholder-review variants:
  - `A`
  - `B`
  - `C`
  - `D`

For both modes:
- prototype work is a planned execution phase, not work to perform during the planning turn
- standalone HTML plus notes is the preferred review artifact
- include a prototype-to-production mapping covering components, tokens, interactions, and tests

## UI source precedence
Preferred UI source order:
1. explicit UI spec in `.harness/specs/`
2. explicit legacy UI spec in `.harness/specs/*-ui-spec.md`
3. parent spec with `ui_required: true`
4. raw UI feature description

## Runtime compatibility note
The source prompts referenced runtime-specific preview methods for later execution work, not for this planning turn.

Preserved compatibility guidance:
- if the execution runtime provides a dedicated browser review subagent, note that it may be used to render and compare prototype HTML
- in Codex- or Codex-style local runtimes, note that standalone HTML prototypes should be directly openable in a browser without a build step

Do not build or open the prototypes during the planning stage unless the user explicitly changes the task from planning to execution.
