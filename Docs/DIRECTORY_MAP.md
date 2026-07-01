# Directory Map

Navigation index for the repository root, major directories, and key subdirectories.

## Table of Contents

- [Root Overview](#root-overview)
- [Skill Domains](#skill-domains)
- [Supporting Systems](#supporting-systems)
- [Operational Content](#operational-content)
- [Quick Navigation Commands](#quick-navigation-commands)

## Root Overview

| Path                                | Purpose                                             |
| ----------------------------------- | --------------------------------------------------- |
| `/README.md`                        | Repository overview, quickstart, and core workflows |
| `/SKILL.md`                         | Generated visible runtime index                     |
| `/AGENTS.md`                        | Repository-specific operating instructions          |
| `/Docs/DIRECTORY_MAP.md`            | This file (root and subdirectory navigation guide)  |
| `/Docs/`                            | Contributor and governance documentation            |
| `/Infrastructure/scripts/`          | Sync, validation, and automation scripts            |
| `/Infrastructure/templates/`        | Reusable templates for skills and contracts         |
| `/Infrastructure/scripts/README.md` | Script index by workflow category                   |
| `/Docs/agents/README.md`            | Agent policy map and quick picks                    |

## Skill Domains

Primary first-party skills are organized by topic cluster under `Skills/`.
Plugin-owned skills live under `Plugins/<plugin>/skills/**`. The generated
command surface currently exposes 109 `$` handles across first-party and plugin
sources.

- `/Skills/agent-ops/` - Agent operations, tooling, and general dev skills (42)
- `/Skills/frontend-ui/` - Frontend UI, design, and browser automation (13)
- `/Skills/backend-platform/` - Backend, CI, and platform infrastructure (4)
- `/Skills/product-strategy/` - Product planning, interviews, and research (4)
- `/Skills/security-ops/` - Security, auth, and recon workflows (7)
- `/Skills/mobile-native/` - macOS/iOS native apps and process monitoring (1)
- `/Skills/content-publishing/` - Content conversion and publishing (8)

Common subdirectory patterns inside each skill:

- `SKILL.md` - Canonical instruction entrypoint
- `Infrastructure/references/` - Contracts, eval guidance, and supporting specs
- `Infrastructure/scripts/` - Helper scripts used by the skill
- `examples/` or `Infrastructure/templates/` - Optional reusable content

## Supporting Systems

| Path                          | Purpose                                           |
| ----------------------------- | ------------------------------------------------- |
| `/Plugins/`                   | Plugin packages and plugin manifests              |
| `/.agents/skills/`            | Generated runtime projection                      |
| `/.skillsets/`                | Generated rooted manifests and command surface    |
| `/skills-sdk/brand/`          | Brand assets and visual references                |
| `/Infrastructure/references/` | Shared contracts and cross-cutting reference docs |

## Operational Content

| Path                         | Purpose                                         |
| ---------------------------- | ----------------------------------------------- |
| `/Infrastructure/artifacts/` | Generated outputs and validation evidence       |
| `/Infrastructure/reports/`   | Summaries and report snapshots                  |
| `/todos/`                    | File-based queued work items                    |
| `/Infrastructure/storage/`   | Local state artifacts used by workflows         |
| `/.harness/`                 | Harness metadata, plans, and memory scaffolding |

## Quick Navigation Commands

```bash
# Top-level directories
fd -td -d 1 .

# Skill folders two levels deep
fd -td -d 2 . Skills

# Generated runtime index + docs entrypoints
ls -la SKILL.md README.md Docs/DIRECTORY_MAP.md

# Command-surface health
python3 ./bin/ask skills handles --check --json
```
