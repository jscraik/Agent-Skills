# Plan for recent-code-bugfix

## Goal
Create a production-ready skill that finds and fixes one bug introduced by the current author within the last week, only when attribution is direct.

## Tasks
1. Scaffold skill folder with `init_skill.py` under `utilities/recent-code-bugfix`.
2. Replace template `SKILL.md` with concrete trigger boundaries, workflow, safety constraints, and validation gates.
3. Fill `references/contract.yaml` with explicit purpose/triggers/inputs/outputs/non-goals/risks.
4. Add `references/evals.yaml` with happy, edge, negative, and pressure cases.
5. Run validation gates (`quick_validate.py`, `skill_gate.py`, `openclaw_skill_guard.py`) and fix issues.
6. Sync flat `skills/` symlinks and regenerate root `SKILL.md` index.

## Status
- [x] Scaffolded skill
- [x] Authored SKILL.md
- [x] Wrote contract + evals
- [x] Validation gates complete
- [x] Sync/index updates complete
