# Design-System Skill Improvement Plan

## Table of Contents
- [Goal](#goal)
- [Assumptions](#assumptions)
- [Improvement steps](#improvement-steps)
- [Validation gates](#validation-gates)
- [Known follow-ups](#known-follow-ups)

## Goal
Keep the repo-local `design-system` skill synchronized with current project contracts, protected-surface policy, and practical validation flow.

## Assumptions
- Skill target is Codex (repo-local path: `.agents/skills/design-system`) and should stay routing-first.
- Compatibility posture is canonical-first unless user explicitly asks for compatibility bridges.
- Deliverables should be artifact-driven and include both token-layer and guidance-policy validation commands.
- Preflight is required for path-sensitive runs (`bash -lc 'source scripts/codex-preflight.sh && preflight_repo'`).

## Improvement steps
1. Re-read current contracts (`CHARTER`, `CONTRACT`, `PROFESSIONAL_UI_CONTRACT`, `AGENT_UI_ROUTING`, and guidance scope config).
2. Tighten `SKILL.md` routing boundaries and update required context sources if project doctrine moved.
3. Refresh references:
   - `contract.yaml` for scope/outputs/non-goals and guidance-policy constraints.
   - `evals.yaml` for strong positive/negative trigger coverage.
   - `system-map.md` for canonical file and command map.
4. Keep output template in `assets/design-system-brief-template.md` aligned with current reporting needs.
5. Add a short `FORJAMIE.md` recent-change note when behavior or workflow expectations shift.

## Validation gates
- `pnpm test:policy` should pass for touched skill/docs updates.
- If token-layer files are touched: `pnpm validate:tokens` and `pnpm ds:matrix:check`.
- If guidance scope or protected surfaces are touched: `pnpm design-system-guidance:ratchet` and `pnpm design-system-guidance:check:ci`.

## Known follow-ups
- Add scripted extractor under `scripts/` if recurring token snapshot generation becomes noisy.
- Keep `references/evals.yaml` in reviewed state and refresh it whenever protected-surface boundaries change.
