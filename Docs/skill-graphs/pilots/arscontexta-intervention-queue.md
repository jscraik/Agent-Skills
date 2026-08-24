# Ars Contexta Intervention Queue

Ars Contexta-backed synthesis layer for recursive skill pilot instability. This queue does not replace the shadow gate; it converts repeated failure and recovery patterns into retrieval-ready interventions.

## Table of Contents

- [Overview](#overview)
- [Promotion Rule](#promotion-rule)
- [Profile Queues](#profile-queues)
- [Methodology References](#methodology-references)

## Overview

- Generated: `2026-04-06T13:26:16Z`
- Window: `2026-03-31..2026-04-06`
- Machine-readable queue: `/.harness/evidence/skill-graphs/telemetry/arscontexta-intervention-queue.json`
- Operator use: review the top unstable profile, capture the intervention as a note first, then promote only repeated wins into skill references or hooks.

## Promotion Rule

- `documentation`: pattern is still unstable; capture and retrieve, do not automate.
- `skill`: repeated positive pattern is stable enough to encode in a reusable workflow or reference.
- `hook-candidate`: only for deterministic patterns that remain clean across windows without recovery.

## Profile Queues

### `frontend-ui-design`

- Stage: `documentation`
- Scope skill: `frontend/ui/frontend-ui-design`
- Clean runs: `0/2`
- Recovered runs: `2`
- Evaluator conflicts: `1`
- Low-confidence runs: `2`
- Objective focus: Shadow evaluation run N for frontend-ui-design: produce production-ready frontend UI design guidance for a web screen with one clear primary action, explicit default/loading/empty/error/disabled states, token-backed primitives, keyboard-focus-contrast-reduced-motion behavior, restrained composition without decorative overload, and a concrete verification checklist.
- Weakest criteria:
  - `restraint_and_composition` (Restraint and composition) x7
  - `accessibility_contract` (Accessibility contract) x5
  - `state_completeness` (State completeness) x2
- Regression criteria:
  - `accessibility_contract` (Accessibility contract) x1
  - `state_completeness` (State completeness) x1
- Positive criteria:
  - `restraint_and_composition` (Restraint and composition) x1
  - `visual_distinction` (Visual distinction) x1
- Recommendations:
  - Capture an Ars Contexta note for frontend-ui-design centered on Restraint and composition, Accessibility contract, and State completeness, using run_20260406T132616265769Z_50ef7d_17b84f02 as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Accessibility contract and State completeness; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why frontend-ui-design regresses on Restraint and composition, Accessibility contract, and State completeness during reevaluation?
  - Which prompt clauses or rubric reminders improved Restraint and composition and Visual distinction without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so frontend-ui-design starts from the last stable intervention instead of rediscovering it?

### `interface-craft`

- Stage: `documentation`
- Scope skill: `frontend/ui/ui-ux-creative-coding`
- Clean runs: `1/2`
- Recovered runs: `1`
- Evaluator conflicts: `1`
- Low-confidence runs: `1`
- Objective focus: Shadow evaluation run N for interface-craft: produce folded interface-craft guidance for a polished React interaction surface with clear motion boundaries, concrete implementation notes, explicit safety constraints, and testable validation steps.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x3
  - `specificity` (Concrete implementation detail) x1
  - `clarity` (Instructional clarity) x1
- Regression criteria:
  - `clarity` (Instructional clarity) x1
- Positive criteria:
  - `safety` (Safety/compliance compliance) x1
  - `specificity` (Concrete implementation detail) x1
- Recommendations:
  - Capture an Ars Contexta note for interface-craft centered on Safety/compliance compliance, Concrete implementation detail, and Instructional clarity, using run_20260406T132616151793Z_04dd5b_17b7fd06 as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Instructional clarity; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why interface-craft regresses on Safety/compliance compliance, Concrete implementation detail, and Instructional clarity during reevaluation?
  - Which prompt clauses or rubric reminders improved Safety/compliance compliance and Concrete implementation detail without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so interface-craft starts from the last stable intervention instead of rediscovering it?

### `react-ui-patterns`

- Stage: `documentation`
- Scope skill: `frontend/ui/react-ui-patterns`
- Clean runs: `1/2`
- Recovered runs: `1`
- Evaluator conflicts: `0`
- Low-confidence runs: `1`
- Objective focus: Shadow evaluation run N for react-ui-patterns: produce concrete React UI composition guidance for a TypeScript plus Tailwind plus Radix screen with file-path-specific component structure, explicit state ownership, accessibility rules, and measurable verification checks.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x3
  - `clarity` (Instructional clarity) x3
  - `specificity` (Concrete implementation detail) x1
- Regression criteria:
  - `clarity` (Instructional clarity) x1
- Positive criteria:
  - `specificity` (Concrete implementation detail) x1
  - `clarity` (Instructional clarity) x1
- Recommendations:
  - Capture an Ars Contexta note for react-ui-patterns centered on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail, using recent recovered runs as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Instructional clarity; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why react-ui-patterns regresses on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail during reevaluation?
  - Which prompt clauses or rubric reminders improved Concrete implementation detail and Instructional clarity without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so react-ui-patterns starts from the last stable intervention instead of rediscovering it?

### `ui-ux-creative-coding`

- Stage: `documentation`
- Scope skill: `frontend/ui/ui-ux-creative-coding`
- Clean runs: `1/2`
- Recovered runs: `1`
- Evaluator conflicts: `0`
- Low-confidence runs: `1`
- Objective focus: Shadow evaluation run N for ui-ux-creative-coding: produce implementation-ready UI polish guidance for an existing React or Tauri surface with one clear interaction thesis, reduced-motion parity, concrete accessibility constraints, and measurable validation checks.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x3
  - `clarity` (Instructional clarity) x1
  - `specificity` (Concrete implementation detail) x1
- Regression criteria:
  - `clarity` (Instructional clarity) x1
  - `specificity` (Concrete implementation detail) x1
- Positive criteria:
  - `clarity` (Instructional clarity) x1
  - `safety` (Safety/compliance compliance) x1
- Recommendations:
  - Capture an Ars Contexta note for ui-ux-creative-coding centered on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail, using recent recovered runs as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Instructional clarity and Concrete implementation detail; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why ui-ux-creative-coding regresses on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail during reevaluation?
  - Which prompt clauses or rubric reminders improved Instructional clarity and Safety/compliance compliance without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so ui-ux-creative-coding starts from the last stable intervention instead of rediscovering it?

## Methodology References

- `/Plugins/arscontexta/methodology/retrieval verification loop tests description quality at scale.md`
- `/Plugins/arscontexta/methodology/queries evolve during search so agents should checkpoint.md`
- `/Plugins/arscontexta/methodology/schema enforcement via validation agents enables soft consistency.md`
- `/Plugins/arscontexta/methodology/methodology development should follow the trajectory from documentation to skill to hook as understanding hardens.md`
