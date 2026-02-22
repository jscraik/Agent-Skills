# Design-System Skill Build Plan

## Table of Contents
- [Goal](#goal)
- [Assumptions](#assumptions)
- [Build steps](#build-steps)
- [Validation gates](#validation-gates)
- [Known follow-ups](#known-follow-ups)

## Goal
Create a repo-local `design-system` skill that can answer and implement design-system tasks using canonical repository sources (tokens, typography, spacing, iconography, and theme variables).

## Assumptions
- Skill target is Codex (repo-local path: `.agents/skills/design-system`).
- Compatibility posture is canonical-first unless user explicitly asks for compatibility bridges.
- Deliverables should be artifact-driven and include validation commands.

## Build steps
1. Scaffold skill structure with `init_skill.py`.
2. Author `SKILL.md` with explicit trigger boundaries and negative triggers.
3. Add references:
   - `contract.yaml` for scope/outputs/non-goals
   - `evals.yaml` for trigger and safety cases
   - `system-map.md` for canonical file map
4. Add output template in `assets/design-system-brief-template.md`.
5. Validate with quick + gate + openclaw checks.

## Validation gates
- `quick_validate.py` must pass.
- `skill_gate.py` must pass.
- `openclaw_skill_guard.py --mode both` should be reviewed; resolve blockers before publish.

## Known follow-ups
- Add scripted extractor under `scripts/` if recurring token snapshot generation becomes noisy.
- Promote evals from draft to reviewed after 1-2 live runs.
