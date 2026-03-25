# Coding-harness skill build plan

## Table of Contents
- [Objective](#objective)
- [Task graph](#task-graph)
- [Acceptance criteria](#acceptance-criteria)

## Objective
Create a distributable Codex skill inside the coding-harness npm package that helps agents:
- install and initialize coding-harness correctly,
- explain what coding-harness can and cannot do,
- run the right setup and validation commands,
- keep .codex/environments/environment.toml action blocks aligned with project scripts.

## Task graph

- **T1 (depends_on: [])** - Scaffold skill bundle under .agents/skills/coding-harness.
- **T2 (depends_on: [T1])** - Author SKILL.md with trigger boundary, workflow, and explicit can and cannot guidance.
- **T3 (depends_on: [T1])** - Add references/setup-and-commands.md with install/setup/update command map and environment sync behavior.
- **T4 (depends_on: [T2, T3])** - Define references/contract.yaml and references/evals.yaml with happy, edge, negative, and pressure prompts.
- **T5 (depends_on: [T4])** - Configure agents/openai.yaml metadata for Codex discovery.
- **T6 (depends_on: [T4, T5])** - Update package payload config so the skill ships in npm artifacts.
- **T7 (depends_on: [T6])** - Run skill validators and repo checks, then fix first failing gate.

## Acceptance criteria

- Skill is present at .agents/skills/coding-harness/SKILL.md with production-ready trigger logic.
- References include concrete setup commands and boundary documentation.
- Evals include happy, edge, pressure, and non-trigger cases.
- npm pack --dry-run shows skill files in the package.
- Repository validation commands pass after changes.
