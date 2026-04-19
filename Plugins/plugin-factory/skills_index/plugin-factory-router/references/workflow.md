# Plugin Factory Router Entrypoint Workflow

## Route Map

- create scaffolds -> `Plugins/plugin-factory/skills/scaffolding_templates/plugin-creator/SKILL.md`
- harden or convert packages -> `Plugins/plugin-factory/skills/code_quality_review/plugin-builder/SKILL.md`
- install or repair plugin visibility -> `Plugins/plugin-factory/skills/infrastructure_ops/plugin-installer/SKILL.md`
- classify mixed requests first -> `Plugins/plugin-factory/skills/team_automation/plugin-router/SKILL.md`

## Procedure

1. Classify intent (`create|harden|convert|install|troubleshoot`).
2. Hand off to exactly one lane.
3. Ask one clarification question only when lane choice is ambiguous.
4. Stop after routing handoff.
