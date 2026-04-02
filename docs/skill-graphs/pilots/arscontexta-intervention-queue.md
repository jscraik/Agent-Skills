# Ars Contexta Intervention Queue

Ars Contexta-backed synthesis layer for recursive skill pilot instability. This queue does not replace the shadow gate; it converts repeated failure and recovery patterns into retrieval-ready interventions.

## Table of Contents
- [Overview](#overview)
- [Promotion Rule](#promotion-rule)
- [Profile Queues](#profile-queues)
- [Methodology References](#methodology-references)

## Overview
- Generated: `2026-03-31T15:28:27Z`
- Window: `2026-03-25..2026-03-31`
- Machine-readable queue: `/artifacts/skill-graphs/telemetry/arscontexta-intervention-queue.json`
- Operator use: review the top unstable profile, capture the intervention as a note first, then promote only repeated wins into skill references or hooks.

## Promotion Rule
- `documentation`: pattern is still unstable; capture and retrieve, do not automate.
- `skill`: repeated positive pattern is stable enough to encode in a reusable workflow or reference.
- `hook-candidate`: only for deterministic patterns that remain clean across windows without recovery.

## Profile Queues
### `frontend-ui-design`
- Stage: `documentation`
- Scope skill: `frontend/ui/frontend-ui-design`
- Clean runs: `6/20`
- Recovered runs: `14`
- Evaluator conflicts: `4`
- Low-confidence runs: `14`
- Objective focus: Shadow evaluation run N for frontend-ui-design: produce production-ready frontend UI design guidance for a web screen with one clear primary action, explicit default/loading/empty/error/disabled states, token-backed primitives, keyboard-focus-contrast-reduced-motion behavior, restrained composition without decorative overload, and a concrete verification checklist.
- Weakest criteria:
  - `restraint_and_composition` (Restraint and composition) x40
  - `accessibility_contract` (Accessibility contract) x21
  - `safety` (Safety) x17
- Regression criteria:
  - `accessibility_contract` (Accessibility contract) x9
  - `clarity` (Clarity) x4
  - `safety` (Safety) x2
- Positive criteria:
  - `restraint_and_composition` (Restraint and composition) x9
  - `specificity` (Specificity) x6
  - `clarity` (Clarity) x5
- Recommendations:
  - Capture an Ars Contexta note for frontend-ui-design centered on Restraint and composition, Accessibility contract, and Safety, using run_20260331T143101180026Z_2ac1a9_bffd74d5, run_20260331T141226543802Z_fc9894_15c48010, run_20260331T141225956402Z_bb9acb_15c37bdd as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Accessibility contract, Clarity, and Safety; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why frontend-ui-design regresses on Restraint and composition, Accessibility contract, and Safety during reevaluation?
  - Which prompt clauses or rubric reminders improved Restraint and composition, Specificity, and Clarity without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so frontend-ui-design starts from the last stable intervention instead of rediscovering it?

### `interface-craft`
- Stage: `documentation`
- Scope skill: `frontend/ui/ui-ux-creative-coding`
- Clean runs: `4/19`
- Recovered runs: `15`
- Evaluator conflicts: `2`
- Low-confidence runs: `15`
- Objective focus: Shadow evaluation run N for interface-craft: produce folded interface-craft guidance for a polished React interaction surface with clear motion boundaries, concrete implementation notes, explicit safety constraints, and testable validation steps.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x36
  - `clarity` (Instructional clarity) x5
  - `specificity` (Concrete implementation detail) x2
- Regression criteria:
  - `clarity` (Instructional clarity) x11
  - `specificity` (Concrete implementation detail) x9
  - `safety` (Safety/compliance compliance) x4
- Positive criteria:
  - `safety` (Safety/compliance compliance) x13
  - `specificity` (Concrete implementation detail) x8
  - `clarity` (Instructional clarity) x4
- Recommendations:
  - Capture an Ars Contexta note for interface-craft centered on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail, using run_20260331T141225453996Z_7bff1d_15c27f41, run_20260331T141225594250Z_2b9eeb_15c2b824 as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Instructional clarity, Concrete implementation detail, and Safety/compliance compliance; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why interface-craft regresses on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail during reevaluation?
  - Which prompt clauses or rubric reminders improved Safety/compliance compliance, Concrete implementation detail, and Instructional clarity without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so interface-craft starts from the last stable intervention instead of rediscovering it?

### `react-ui-patterns`
- Stage: `documentation`
- Scope skill: `frontend/ui/react-ui-patterns`
- Clean runs: `8/19`
- Recovered runs: `11`
- Evaluator conflicts: `5`
- Low-confidence runs: `11`
- Objective focus: Shadow evaluation run N for react-ui-patterns: produce concrete React UI composition guidance for a TypeScript plus Tailwind plus Radix screen with file-path-specific component structure, explicit state ownership, accessibility rules, and measurable verification checks.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x34
  - `clarity` (Instructional clarity) x16
  - `specificity` (Concrete implementation detail) x12
- Regression criteria:
  - `clarity` (Instructional clarity) x7
  - `safety` (Safety/compliance compliance) x3
  - `specificity` (Concrete implementation detail) x2
- Positive criteria:
  - `specificity` (Concrete implementation detail) x13
  - `clarity` (Instructional clarity) x7
  - `safety` (Safety/compliance compliance) x7
- Recommendations:
  - Capture an Ars Contexta note for react-ui-patterns centered on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail, using run_20260331T143705798653Z_f4298e_f6846cbf, run_20260331T142550250609Z_82ecf7_6bdae6fc, run_20260331T141226620193Z_82ecf7_15c4be6f as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Instructional clarity, Safety/compliance compliance, and Concrete implementation detail; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why react-ui-patterns regresses on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail during reevaluation?
  - Which prompt clauses or rubric reminders improved Concrete implementation detail, Instructional clarity, and Safety/compliance compliance without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so react-ui-patterns starts from the last stable intervention instead of rediscovering it?

### `ui-ux-creative-coding`
- Stage: `documentation`
- Scope skill: `frontend/ui/ui-ux-creative-coding`
- Clean runs: `12/19`
- Recovered runs: `7`
- Evaluator conflicts: `0`
- Low-confidence runs: `7`
- Objective focus: Shadow evaluation run N for ui-ux-creative-coding: produce implementation-ready UI polish guidance for an existing React or Tauri surface with one clear interaction thesis, reduced-motion parity, concrete accessibility constraints, and measurable validation checks.
- Weakest criteria:
  - `safety` (Safety/compliance compliance) x33
  - `clarity` (Instructional clarity) x19
  - `specificity` (Concrete implementation detail) x17
- Regression criteria:
  - `safety` (Safety/compliance compliance) x5
  - `clarity` (Instructional clarity) x4
  - `specificity` (Concrete implementation detail) x1
- Positive criteria:
  - `clarity` (Instructional clarity) x11
  - `specificity` (Concrete implementation detail) x6
  - `safety` (Safety/compliance compliance) x4
- Recommendations:
  - Capture an Ars Contexta note for ui-ux-creative-coding centered on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail, using recent recovered runs as the seed evidence set.
  - At each reevaluation checkpoint, explicitly reassess whether the objective should pivot toward Safety/compliance compliance, Instructional clarity, and Concrete implementation detail; treat that as search refinement, not failure.
  - Keep these interventions at documentation level for now, and only promote a pattern upward once it repeats cleanly without reopening regressions.
- Retrieval checkpoints:
  - What recurring evidence explains why ui-ux-creative-coding regresses on Safety/compliance compliance, Instructional clarity, and Concrete implementation detail during reevaluation?
  - Which prompt clauses or rubric reminders improved Instructional clarity, Concrete implementation detail, and Safety/compliance compliance without weakening safety or non-regression?
  - What should be retrieved before iteration 1 so ui-ux-creative-coding starts from the last stable intervention instead of rediscovering it?

## Methodology References
- `/plugins/arscontexta/methodology/retrieval verification loop tests description quality at scale.md`
- `/plugins/arscontexta/methodology/queries evolve during search so agents should checkpoint.md`
- `/plugins/arscontexta/methodology/schema enforcement via validation agents enables soft consistency.md`
- `/plugins/arscontexta/methodology/methodology development should follow the trajectory from documentation to skill to hook as understanding hardens.md`
