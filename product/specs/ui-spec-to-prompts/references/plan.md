# Plan for ui-spec-to-prompts

## Goal
Create a Codex skill that converts an existing UI spec into build-order prompts for UI generation tools, aligned with aStudio tokens and UI rules.

## Steps
1) Scaffold the skill folder and references.
2) Author `SKILL.md` with clear triggers, inputs/outputs, prompt template, and validation rules.
3) Add `references/contract.yaml` and `references/evals.yaml`.
4) Run validators (`quick_validate.py`, `skill_gate.py`, `analyze_skill.py`) and fix issues.

## Done when
- The skill triggers on UI spec -> prompts requests.
- At least 3 eval cases exist (happy, edge, failure).
- Validators pass.
