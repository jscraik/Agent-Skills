# Agent Skills

A governed repository of **109 skills** for AI coding agents (Codex, Claude, Gemini). Built around the **Agent Skills Kit (`ask`)** CLI.

**What this gives you:**

- **One place for skills** – Author in Markdown, sync to any runtime
- **Quality gates** – Structural, security, and behavioral validation for every skill
- **Living skill graph** – Browse 109 skills across 7 topic clusters with relationship mapping
- **Agent-native CLI** – Fuzzy matching, JSON output, trace IDs, helpful errors

## Quick start

```bash
# One-time per shell: load repo environment and add ask to PATH
source scripts/codex_env_common.sh && codex_apply_env

# See what's available
ask graph topics

# Validate the repository
ask repo validate --ephemeral

# Sync to your runtime
ask skills sync --scope user
```

## What you can do

### Discover skills

```bash
# Search skills
ask graph find security --tier stable

# See related skills
ask graph related skill-builder --depth 2

# Find path between skills
ask graph chain skill-creator skill-installer
```

### Validate quality

```bash
# Quick structural check
ask skills audit backend/cli-spec --level compat

# Full security audit
ask skills audit backend/cli-spec --level strict

# Run evaluation suite
ask evals run backend/cli-spec --mode smoke

# Validate entire repository
ask repo validate --ephemeral
```

### Manage lifecycle

```bash
# Install from GitHub with auto-remediation
ask skills install https://github.com/owner/repo --remediate

# Check for overlap
ask skills fold source-skill target-skill

# Create new skill
ask skills init my-skill --category backend --description "Does X when Y"

# Create plugin scaffold
ask plugins init my-plugin --with-marketplace
```

## Robot mode for AI agents

When intent is clear but syntax is off, use `--robot` (or `-r`):

```bash
# These work and get corrected:
ask skill list --robot          # → skills list
ask skills ls --robot           # → skills list
ask graph search X --robot      # → graph find X
```

Errors include suggestions and examples:

```
❌ Unknown topic: 'invalid'

💡 Did you mean 'ask skills'?
   Valid topics: repo, skills, plugins, evals, graph

📚 Examples:
   • ask skills list
   • ask graph find security
```

## Programmatic usage

```bash
# JSON output with trace IDs
ask repo status --json --trace-id "build-123"

# Check for corrections
ask skill list --robot --json | jq '.metadata.correction_note'

# Ephemeral validation (read-only)
ask repo validate --ephemeral
```

**Response envelope** (all commands):

```json
{
  "status": "success",
  "trace_id": "uuid",
  "metadata": {
    "next_steps": ["ask skills audit ..."],
    "correction_note": "..."
  },
  "data": { ... }
}
```

## Skill graph (manual topic clusters, non-canonical)

This table is a human-oriented grouping for quick navigation and is not used for parity enforcement. Canonical catalog parity uses `discover_skill_entries()` and `catalog_parity` and currently expects **109** skills.

| Topic              | Skills | Examples                                       |
| ------------------ | ------ | ---------------------------------------------- |
| frontend-ui        | 28     | react-ui-patterns, shadcn-ui, design-system    |
| agent-ops          | 38     | skill-builder, skill-creator, evals-router     |
| backend-platform   | 13     | cli-spec, mcp-builder, backend-engineer        |
| product-strategy   | 12     | product-spec, ce-spec, ce-plan                 |
| security-ops       | 7      | security-best-practices, security-threat-model |
| content-publishing | 8      | slides, youtube-titles-thumbnails              |
| mobile-native      | 3      | atlas, process-watch                           |

## Repository layout

```
agent-skills/
├── bin/ask                   # CLI entry point
├── .agents/skills/           # Flat runtime projection
│
├── auth/                     # Authentication and security skills
├── backend/                  # Backend and API skills
├── frontend/                 # Frontend UI, tools, and graphics skills
├── github/                   # GitHub workflow skills
├── interview/                # Structured interview and discovery skills
├── product/                  # Product strategy and operations skills
├── skills-system/            # Core system-level skills
├── utilities/                # Agent operations and platform utilities
│
├── scripts/lib/ask/          # CLI implementation
├── docs/cli-specs/           # Command specifications
└── ops/metrics/graph/        # Skill relationship data
```

Ownership boundaries:
- Canonical authoring: domain folders plus `plugins/<plugin>/skills/**`
- Factory mechanics: `scripts/**`, validation/governance contracts
- Runtime/projection surfaces: `.agents/**`, `.agent/skills/**`, `skills-antigravity/**`, `plugins/cache/**`, `runtime/**` (read-only by policy)
- Full policy: [docs/agents/14-path-ownership-boundaries.md](docs/agents/14-path-ownership-boundaries.md)

## Documentation

- **[CLI Specification](docs/cli-specs/2026-04-06-ask-cli-spec.md)** – Complete command reference
- **[Agent Guide](AGENTS.md)** – AI agent workflow patterns
- **[Skill Index](SKILL.md)** – All 109 skills by category
- **[Implementation Review](docs/cli-specs/2026-04-06-ask-cli-implementation-review.md)** – Architecture details

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for local-first agent workflows. Do not commit credentials, tokens, or personal data. Security and secret checks run in CI, but contributors remain responsible for keeping sensitive values out of commits and generated artifacts.

## Governance

- **License:** Apache 2.0
- **Skills:** 109 canonical total (manual cluster table above is non-canonical)
- **Validation:** 10+ automated checks via `ask repo validate`
- **Compatibility:** Codex, Claude Code, Gemini/Antigravity
