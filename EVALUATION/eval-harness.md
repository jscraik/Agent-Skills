# Evaluation Harness

## Goal

Define lightweight, repeatable checks for model/tool-related behavior and governance controls.

## Baseline checks

- [ ] Regression prompts executed from `EVALUATION/regression-prompts.md`
- [ ] Governance gate workflow still enforces evidence sections for sensitive PRs
- [ ] Secret scan and dependency scan behavior validated in CI or local dry-run

## Run record template

| Date | Scope | Checks run | Result | Follow-up |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | baseline | prompts + gates | pass/fail | link to issue/PR |
