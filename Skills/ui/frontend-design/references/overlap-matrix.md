# Frontend Design Overlap Matrix

Use this matrix to keep `frontend-design` narrow and deconflicted. The wrapper should trigger only when the request is broad enough that the downstream owner still needs to be chosen.

## Table of Contents
- [Boundary rule](#boundary-rule)
- [Matrix](#matrix)
- [Notes](#notes)

## Boundary rule
- Trigger `frontend-design` only when the user is asking for frontend design in broad terms and the main job is to classify the work before deeper execution.
- If the narrower owner is already obvious from the prompt, skip this wrapper and use that skill directly.

## Matrix

| Request shape | Primary outcome | Owner |
|---|---|---|
| "Design the frontend for this new product." | Classify system maturity, choose direction, decide who should own implementation guidance | `frontend-design` |
| "We need a premium dashboard but I'm not sure whether to extend the current system or go more bespoke." | Decide existing-system vs bespoke path, then route | `frontend-design` |
| "Design a settings flow with accessible tabs, validation, and error states." | Production-ready UI structure, states, and accessibility behavior | `frontend-ui-design` |
| "Create a visually strong landing page with one dominant hero composition and restrained motion." | Visually led surface with production-ready hierarchy | `frontend-ui-design` |
| "Improve the motion rhythm on this existing panel." | Post-direction interaction polish | `ui-ux-creative-coding` |
| "Tighten the interaction feel on these two screens without changing the structure." | Focused refinement and motion system | `ui-ux-creative-coding` |
| "Update token aliases, theme slots, and spacing scale usage." | Token-layer and theme architecture work | `design-system` |
| "Audit our typography tokens and how they map into components." | Evidence-backed design-system analysis | `design-system` |

## Notes
- `frontend-design` is the compatibility front door for imported CE doctrine, not a replacement for the stronger local specialist skills.
- If a request mixes multiple areas, choose the skill that owns the center of gravity:
  - states, accessibility, and component structure -> `frontend-ui-design`
  - motion, rhythm, and feel after direction exists -> `ui-ux-creative-coding`
  - tokens, aliases, themes, and styling system structure -> `design-system`
- Revisit this matrix whenever the local frontend skills change their descriptions or scope.
