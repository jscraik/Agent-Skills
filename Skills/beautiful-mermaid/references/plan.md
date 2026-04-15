# Plan: beautiful-mermaid skill hardening

1) Add required sections to SKILL.md (philosophy, when to use, inputs/outputs, constraints, validation, antipatterns, examples).
2) Gate dependency auto-install with an explicit flag in render.ts; document it in SKILL.md.
3) Add Infrastructure/references/contract.yaml and Infrastructure/references/evals.yaml.
4) Validate with quick_validate.py and skill_gate.py via `~/.venvs/pyyaml/bin/python`; fix any failures.
