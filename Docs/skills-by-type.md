# Skill Type Index

Generated from `metadata.skill-type` tags in skill frontmatter.

## Table of Contents
- [Summary](#summary)
- [Validation Notes](#validation-notes)
- [Canonical Values](#canonical-values)
- [Semantic Types](#semantic-types)

## Summary

- `library_api_reference`: 3
- `product_verification`: 4
- `data_fetch_analysis`: 4
- `team_automation`: 35
- `scaffolding_templates`: 19
- `code_quality_review`: 25
- `ci_cd_deployment`: 1
- `runbook`: 11
- `infrastructure_ops`: 4
- `invalid`: 0
- `total_tagged`: 106

## Validation Notes

- Regeneration command:
  - `python3 Infrastructure/scripts/lifecycle-and-sync/skill_scan.py write-skill-type-index --output Docs/skills-by-type.md`
- Source scope: `Skills Plugins/harness-engineering Plugins/plugin-factory Plugins/skill-factory`.
- Companion mode: sandbox-safe (no protected runtime path mutations).
- Validation command:
  - `bash Infrastructure/scripts/validation-and-linting/lint_skill_types.sh`
  - `bash Infrastructure/scripts/validation-and-linting/check-doc-style.sh --changed`

## Canonical Values

- `library_api_reference`
- `product_verification`
- `data_fetch_analysis`
- `team_automation`
- `scaffolding_templates`
- `code_quality_review`
- `ci_cd_deployment`
- `runbook`
- `infrastructure_ops`

## Semantic Types

### Library Api Reference

- context7 (Skills/agent-ops)
- oak-api (Skills/backend-platform)
- react-ui-patterns (Skills/frontend-ui)

### Product Verification

- agentation (Skills/frontend-ui)
- design-system (Skills/frontend-ui)
- playwright-interactive (Skills/frontend-ui)
- ui-visual-regression (Skills/frontend-ui)

### Data Fetch Analysis

- insight-report (Skills/agent-ops)
- security-ownership-map (Skills/security-ops)
- skill-refactor (Plugins/skill-factory/skills/data_fetch_analysis)
- spreadsheet (Skills/content-publishing)

### Team Automation

- alignment-checkpoint (Skills/agent-ops)
- architecture-interview (Skills/product-strategy)
- atlas (Skills/mobile-native)
- autoresearch (Skills/agent-ops)
- codex-automation-architect (Skills/agent-ops)
- coding-harness (Skills/agent-ops)
- decide-build-primitive (Skills/agent-ops)
- deep-interview (Skills/product-strategy)
- he-brainstorm (Plugins/harness-engineering/skills/team_automation)
- he-compound (Plugins/harness-engineering/skills/team_automation)
- he-compound-refresh (Plugins/harness-engineering/skills/team_automation)
- he-deepen-plan (Plugins/harness-engineering/skills/team_automation)
- he-deepen-spec (Plugins/harness-engineering/skills/team_automation)
- he-fix-bugs (Plugins/harness-engineering/skills/team_automation)
- he-heartbeat (Plugins/harness-engineering/skills/team_automation)
- he-ideate (Plugins/harness-engineering/skills/team_automation)
- he-improve (Plugins/harness-engineering/skills/team_automation)
- he-plan (Plugins/harness-engineering/skills/team_automation)
- he-prune-branches (Plugins/harness-engineering/skills/team_automation)
- he-refine (Plugins/harness-engineering/skills/team_automation)
- he-router (Plugins/harness-engineering/skills)
- he-spec (Plugins/harness-engineering/skills/team_automation)
- he-tdd (Plugins/harness-engineering/skills/team_automation)
- he-work (Plugins/harness-engineering/skills/team_automation)
- interview-me (Skills/product-strategy)
- plugin-factory-router (Plugins/plugin-factory/skills)
- plugin-router (Plugins/plugin-factory/skills/team_automation)
- production-deployment (Skills/agent-ops)
- skill-factory-router (Plugins/skill-factory/skills)
- skill-pr-delivery (Skills/agent-ops)
- slides (Skills/content-publishing)
- triage (Skills/agent-ops)
- ubiquitous-language (Skills/agent-ops)
- video-transcript-downloader (Skills/content-publishing)
- visual-explainer (Skills/content-publishing)
- youtube-hooks-scripts (Skills/content-publishing)

### Scaffolding Templates

- backend-engineer (Skills/backend-platform)
- beautiful-mermaid (Skills/content-publishing)
- better-icons (Skills/frontend-ui)
- bootstrap (Skills/agent-ops)
- chatgpt-apps (Skills/product-strategy)
- cli-spec (Skills/backend-platform)
- codex-agent-creator (Skills/agent-ops)
- codex-hooks-builder (Skills/agent-ops)
- create-auth (Skills/security-ops)
- frontend-design (Skills/agent-ops)
- frontend-ui-design (Skills/frontend-ui)
- llm-wiki (Skills/content-publishing)
- mcp-builder (Skills/backend-platform)
- og-image-creator (Skills/frontend-ui)
- plugin-creator (Plugins/plugin-factory/skills/scaffolding_templates)
- shadcn-ui (Skills/frontend-ui)
- skill-creator (Plugins/skill-factory/skills/scaffolding_templates)
- skillify (Plugins/skill-factory/skills/scaffolding_templates)
- ui-ux-creative-coding (Skills/frontend-ui)

### Code Quality Review

- agents-md (Skills/agent-ops)
- autofix (Skills/agent-ops)
- baseline-ui (Skills/frontend-ui)
- best-practices (Skills/security-ops)
- docs-expert (Skills/agent-ops)
- elixir-pro (Skills/agent-ops)
- evals-router (Skills/agent-ops)
- fixing-accessibility (Skills/frontend-ui)
- fixing-metadata (Skills/frontend-ui)
- go (Skills/agent-ops)
- he-code-review (Plugins/harness-engineering/skills/code_quality_review)
- he-reliability-review (Plugins/harness-engineering/skills/code_quality_review)
- he-technical-review (Plugins/harness-engineering/skills/code_quality_review)
- improve-codebase-architecture (Skills/agent-ops)
- javascript-pro (Skills/agent-ops)
- plugin-builder (Plugins/plugin-factory/skills/code_quality_review)
- rust-pro (Skills/agent-ops)
- security-best-practices (Skills/security-ops)
- simplify (Skills/agent-ops)
- skill-builder (Plugins/skill-factory/skills/code_quality_review)
- swift-development (Skills/agent-ops)
- toml (Skills/agent-ops)
- typescript (Skills/agent-ops)
- verification-before-completion (Skills/agent-ops)
- yaml (Skills/agent-ops)

### Ci Cd Deployment

- gh-workflow (Skills/agent-ops)

### Runbook

- bash-hygiene (Skills/agent-ops)
- biome-linting (Skills/agent-ops)
- diagram-cli (Skills/agent-ops)
- npm-release (Skills/agent-ops)
- pnpm-manager (Skills/agent-ops)
- prek-pro (Skills/agent-ops)
- project-brain (Skills/agent-ops)
- recon-workbench (Skills/security-ops)
- security-threat-model (Skills/security-ops)
- uv-python-project-setup (Skills/agent-ops)
- vale (Skills/agent-ops)

### Infrastructure Ops

- 1password (Skills/security-ops)
- fix-mise (Skills/agent-ops)
- plugin-installer (Plugins/plugin-factory/skills/infrastructure_ops)
- skill-installer (Plugins/skill-factory/skills/infrastructure_ops)
