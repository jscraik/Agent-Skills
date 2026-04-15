# Agent Skills

A governed repository of **137 skills** for AI coding agents (Codex, Claude, Gemini). Built around the **Agent Skills Kit (`ask`)** CLI.

**What this gives you:**

- **One place for skills** – Author in Markdown, sync to any runtime
- **Quality gates** – 28 automated structural, security, and behavioral validation checks
- **Living skill graph** – Browse skills organized by topic clusters with relationship mapping
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

This table is a human-oriented grouping for quick navigation and is not used for parity enforcement. Canonical catalog parity uses `discover_skill_entries()` and `catalog_parity` and currently expects **137** skills.

| Topic              | Skills | Examples                                           |
| ------------------ | ------ | -------------------------------------------------- |
| agent-ops          | 42     | skill-builder, skill-creator, evals-router         |
| frontend-ui        | 25     | react-ui-patterns, shadcn-ui, agent-browser        |
| backend-platform   | 13     | cli-spec, mcp-builder, backend-engineer            |
| product-ops        | 7      | ce-brainstorm, ce-spec, ce-plan                    |
| product-strategy   | 10     | product-spec, architecture-interview, brainstorming |
| security-ops       | 7      | security-best-practices, security-threat-model     |
| content-publishing | 8      | slides, youtube-titles-thumbnails                  |
| ops-engineering    | 2      | fallback-release, production-deployment            |
| mobile-native      | 2      | atlas, process-watch                               |
| knowledge-ops      | 1      | llm-wiki                                           |
| code-quality       | 1      | simplify                                           |
| infrastructure     | 1      | claude-alias                                       |

## Repository layout

```
agent-skills/
├── bin/ask                   # CLI entry point
├── .agents/skills/           # Flat runtime projection (read-only)
│
├── auth/                     # Authentication and security skills
├── backend/                  # Backend and API skills
├── frontend/                 # Frontend UI, tools, and graphics skills
├── github/                   # GitHub workflow skills
├── interview/                # Structured interview and discovery skills
├── plugins/                  # Plugin packages (coderabbit, skill-factory, ...)
│   └── */skills/**           # Plugin-owned skills
├── product/                  # Product strategy and operations skills
├── skills-system/            # Core system-level skills
├── utilities/                # Agent operations and platform utilities
│
├── scripts/lib/ask/          # CLI implementation
├── docs/cli-specs/           # Command specifications
├── docs/skill-graphs/        # Adjacency map and graph data
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
- **[Skill Index](SKILL.md)** – All 137 skills by category
- **[Implementation Review](docs/cli-specs/2026-04-06-ask-cli-implementation-review.md)** – Architecture details

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for local-first agent workflows. Do not commit credentials, tokens, or personal data. Security and secret checks run in CI, but contributors remain responsible for keeping sensitive values out of commits and generated artifacts.

## Governance

- **License:** Apache 2.0
- **Skills:** 137 canonical total (manual cluster table above is non-canonical)
- **Validation:** 28 automated checks via `ask repo validate`
- **Compatibility:** Codex, Claude Code, Gemini/Antigravity