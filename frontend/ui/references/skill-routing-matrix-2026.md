# Frontend Skill Routing Matrix 2026

## Table of Contents
- [Purpose](#purpose)
- [Primary ownership](#primary-ownership)
- [Tie-breaker rules](#tie-breaker-rules)
- [Fast decision flow](#fast-decision-flow)
- [Prompt examples by owner](#prompt-examples-by-owner)
- [Verification contract](#verification-contract)

## Purpose
Provide a single routing contract so Codex and Claude choose the correct `frontend/ui/*` skill consistently.

## Primary ownership
| Intent signal | Skill owner | Notes |
|---|---|---|
| Broad, ambiguous "frontend design" request | `frontend-design` | Thin router, not long-term owner. |
| Build, redesign, or fix production UI screens/components | `frontend-ui-design` | Default execution owner for standard product UI. |
| Token aliases, mapped theme vars, typography/spacing/icon governance | `design-system` | System-level visual language and token architecture owner. |
| Post-direction polish, interaction rhythm, motion feel tuning | `ui-ux-creative-coding` | Use after core visual direction already exists. |
| Snapshot/diff triage and baseline decisions | `ui-visual-regression` | Visual evidence owner. |
| Guardrail scoring and anti-pattern audits | `baseline-ui` | QA-style review owner. |
| shadcn component setup/adaptation | `shadcn-ui` | Framework/tool-specific owner. |
| React composition patterns and structure guidance | `react-ui-patterns` | Code-structure and composition owner. |
| Remotion composition/video guidance | `remotion` | Video composition owner. |
| Stitch-to-Remotion walkthrough generation | `stitch-remotion` | Stitch video pipeline owner. |

## Tie-breaker rules
1. Narrow skill beats broad skill.
2. Explicit build verbs (`build`, `implement`, `redesign`, `fix layout`, `create screen`) route to `frontend-ui-design` unless token governance or motion-only polish is primary.
3. Token/theme governance beats UI implementation when both appear in one request.
4. Motion-only refinement after direction is set routes to `ui-ux-creative-coding`.
5. If the prompt already names a narrower skill or unmistakable scope, skip `frontend-design`.

## Fast decision flow
1. Does the prompt request token/theme/icon governance across surfaces?
Route to `design-system`.
2. Does the prompt request motion polish only, with existing layout/direction already decided?
Route to `ui-ux-creative-coding`.
3. Does the prompt request component/screen build, redesign, hierarchy, spacing, state coverage, or CTA clarity?
Route to `frontend-ui-design`.
4. Is the prompt broad or unclear about ownership?
Start with `frontend-design`, then hand off quickly.

## Prompt examples by owner
- `frontend-design`: "Help with frontend design for our app, not sure where to start."
- `frontend-ui-design`: "Redesign this settings page and improve spacing rhythm, hierarchy, and states."
- `design-system`: "Update token aliases and mapped variables for button typography and spacing."
- `ui-ux-creative-coding`: "Tune micro-interactions and motion timing on this existing dashboard."

## Verification contract
- Keep overlap tests in both:
  - `frontend/ui/frontend-design/references/evals.yaml`
  - `frontend/ui/frontend-ui-design/references/evals.yaml`
- Include positive and negative near-neighbor cases for:
  - broad vs explicit implementation asks;
  - token governance vs UI execution;
  - motion-only polish vs full UI redesign.
- If routing boundaries change in any frontend skill, update this matrix and rerun skill gates.
