# Agent Skills

A governed repository of **116 skills** for AI coding agents (Codex, Claude, Gemini). Built around the **Agent Skills Kit (`ask`)** CLI.

**What this gives you:**

- **One place for skills** – Author in Markdown, sync to any runtime
- **Quality gates** – Structural, security, and behavioral validation for every skill
- **Living skill graph** – Browse 116 skills across 7 topic clusters with relationship mapping
- **Agent-native CLI** – Fuzzy matching, JSON output, trace IDs, helpful errors

## Quick start

```bash
# See what's available
./bin/ask graph topics

# Validate the repository
./bin/ask repo validate --ephemeral

# Sync to your runtime
./bin/ask skills sync --scope user
```

## What you can do

### Discover skills

```bash
# Search 116 skills
./bin/ask graph find security --tier stable

# See related skills
./bin/ask graph related skill-builder --depth 2

# Find path between skills
./bin/ask graph chain skill-creator skill-installer
```

### Validate quality

```bash
# Quick structural check
./bin/ask skills audit backend/cli-spec --level compat

# Full security audit
./bin/ask skills audit backend/cli-spec --level strict

# Run evaluation suite
./bin/ask evals run backend/cli-spec --mode smoke

# Validate entire repository
./bin/ask repo validate --ephemeral
```

### Manage lifecycle

```bash
# Install from GitHub with auto-remediation
./bin/ask skills install https://github.com/owner/repo --remediate

# Check for overlap
./bin/ask skills fold source-skill target-skill

# Create new skill
./bin/ask skills init my-skill --category backend --description "Does X when Y"

# Create plugin scaffold
./bin/ask plugins init my-plugin --with-marketplace
```

## Robot mode for AI agents

When intent is clear but syntax is off, use `--robot` (or `-r`):

```bash
# These work and get corrected:
./bin/ask skill list --robot          # → skills list
./bin/ask skills ls --robot           # → skills list
./bin/ask graph search X --robot      # → graph find X
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
./bin/ask repo status --json --trace-id "build-123"

# Check for corrections
./bin/ask skill list --robot --json | jq '.metadata.correction_note'

# Ephemeral validation (read-only)
./bin/ask repo validate --ephemeral
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

## Skill graph (7 topic clusters)

| Topic              | Skills | Examples                                       |
| ------------------ | ------ | ---------------------------------------------- |
| frontend-ui        | 27     | react-ui-patterns, shadcn-ui, figma            |
| agent-ops          | 22     | skill-builder, skill-creator, evals-router     |
| backend-platform   | 16     | cli-spec, mcp-builder, workers-mcp             |
| product-strategy   | 13     | product-spec, ce-spec, ce-plan                 |
| security-ops       | 7      | security-best-practices, security-threat-model |
| content-publishing | 5      | slides, youtube-titles-thumbnails              |
| mobile-native      | 4      | xcode-makefiles, test-xcode                    |

## Repository layout

```
agent-skills/
├── bin/ask                   # CLI entry point
├── .agents/skills/           # Flat runtime projection
│
├── backend/                  # Backend platform (16 skills)
├── frontend/                 # Frontend UI (27 skills)
├── product/                  # Product strategy (13 skills)
├── auth/                     # Security operations (7 skills)
├── skills-system/            # Meta-skills (installer, creator)
│
├── scripts/lib/ask/          # CLI implementation
├── docs/cli-specs/           # Command specifications
└── ops/metrics/graph/        # Skill relationship data
```

## Documentation

- **[CLI Specification](docs/cli-specs/2026-04-06-ask-cli-spec.md)** – Complete command reference
- **[Agent Guide](AGENTS.md)** – AI agent workflow patterns
- **[Skill Index](SKILL.md)** – All 116 skills by category
- **[Implementation Review](docs/cli-specs/2026-04-06-ask-cli-implementation-review.md)** – Architecture details

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for local-first agent workflows. Do not commit credentials, tokens, or personal data. Security and secret checks run in CI, but contributors remain responsible for keeping sensitive values out of commits and generated artifacts.

## Governance

- **License:** Apache 2.0
- **Skills:** 116 total across 7 topic clusters
- **Validation:** 10+ automated checks via `./bin/ask repo validate`
- **Compatibility:** Codex, Claude Code, Gemini/Antigravity
