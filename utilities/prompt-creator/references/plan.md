# Plan for Prompt Creator

## Goal
Create a Codex skill that helps users create/update **Codex skills** (preferred) stored under `.agents/skills/` (repo) or `~/.agents/skills/` (user), so they can be invoked explicitly (e.g. `$skill-name`) or implicitly.

## Plan (executed)
1) Scaffold an instruction-only skill folder and required `references/` structure.
2) Author `SKILL.md` with required sections for skill_gate: When to use, Inputs, Outputs, Philosophy, Procedure, Validation, Anti-patterns, Constraints, plus Examples.
3) Add `references/contract.yaml` + `references/evals.yaml` (>= 3 cases).
4) Add a `skills/` symlink for discovery consistency in this repo.
5) Run validation gates (`quick_validate.py`, `skill_gate.py`, `run_skill_evals.py`) and fix any failures.
