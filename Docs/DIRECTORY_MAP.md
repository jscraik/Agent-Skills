# Directory Map

Navigation index for the repository root, major directories, and key subdirectories.

## Table of Contents

- [Root Overview](#root-overview)
- [Skill Domains](#skill-domains)
- [Supporting Systems](#supporting-systems)
- [Operational Content](#operational-content)
- [Quick Navigation Commands](#quick-navigation-commands)

## Root Overview

| Path                     | Purpose                                             |
| ------------------------ | --------------------------------------------------- |
| `/README.md`             | Repository overview, quickstart, and core workflows |
| `/SKILL.md`              | Generated catalog index of all skills               |
| `/AGENTS.md`             | Repository-specific operating instructions          |
| `/DIRECTORY_MAP.md`      | This file (root and subdirectory navigation guide)  |
| `/docs/`                 | Contributor and governance documentation            |
| `/Infrastructure/scripts/`              | Sync, validation, and automation scripts            |
| `/Infrastructure/templates/`            | Reusable templates for skills and contracts         |
| `/Infrastructure/scripts/README.md`     | Script index by workflow category                   |
| `/Docs/agents/README.md` | Agent policy map and quick picks                    |

## Skill Domains

Primary skill categories are organized by domain folder:

- `/auth/` (index: [/auth/README.md](/auth/README.md))
- `/backend/` (index: [/backend/README.md](/backend/README.md))
- `/frontend/` (index: [/frontend/README.md](/frontend/README.md))
- `/github/` (index: [/github/README.md](/github/README.md))
- `/interview/` (index: [/interview/README.md](/interview/README.md))
- `/product/` (index: [/product/README.md](/product/README.md))
- `/Skills/` (index: [/Skills/README.md](/Skills/README.md))
- `/Skills/` (index: [/Skills/README.md](/Skills/README.md))

Common subdirectory patterns inside each skill:

- `SKILL.md` - Canonical instruction entrypoint
- `Infrastructure/references/` - Contracts, eval guidance, and supporting specs
- `Infrastructure/scripts/` - Helper scripts used by the skill
- `examples/` or `Infrastructure/templates/` - Optional reusable content

## Supporting Systems

| Path                   | Purpose                                           |
| ---------------------- | ------------------------------------------------- |
| `/Plugins/`            | Plugin packages and plugin manifests              |
| `/skills-antigravity/` | Antigravity projection output                     |
| `/.agents/skills/`     | Flat runtime skill projection                     |
| `/brand/`              | Brand assets and visual references                |
| `/Infrastructure/references/`         | Shared contracts and cross-cutting reference docs |

## Operational Content

| Path          | Purpose                                         |
| ------------- | ----------------------------------------------- |
| `/Infrastructure/artifacts/` | Generated outputs and validation evidence       |
| `/Infrastructure/reports/`   | Summaries and report snapshots                  |
| `/todos/`     | File-based queued work items                    |
| `/Infrastructure/storage/`   | Local state artifacts used by workflows         |
| `/.harness/`  | Harness metadata, plans, and memory scaffolding |

## Quick Navigation Commands

```bash
# Top-level directories
fd -td -d 1 .

# Skill folders two levels deep
fd -td -d 2 . auth backend frontend github interview product utilities skills-system

# Generated catalog + docs entrypoints
ls -la SKILL.md README.md docs/index.md DIRECTORY_MAP.md
```
