# Agent Skills

A governed repository of 123+ skills for AI coding agents (Codex, Claude, Gemini). Built around the **Agent Skills Kit (`ask`)** CLI—designed for both humans and autonomous agents.

## Why this exists

**The problem:** AI agents need reliable, versioned skills with validation, provenance, and discoverability. Ad-hoc prompts fail at scale.

**The solution:** This repository provides:
- **Author once, project everywhere** – Write skills in standard Markdown, sync to multiple runtime formats
- **Quality gates** – Every skill passes structural, security, and behavioral validation
- **Living skill graph** – 123 skills organized in 7 topic clusters with relationship mapping
- **Agent-native CLI** – Fuzzy matching, JSON output, trace IDs, helpful errors

## Quick start (60 seconds)

```bash
# Health check
./bin/ask repo status

# See what skills exist
./bin/ask graph topics

# Validate the repository
./bin/ask repo validate --ephemeral

# Sync to your runtime
./bin/ask skills sync --scope user
```

## What the CLI can do

### Discover skills
```bash
# Search across 123 skills
./bin/ask graph find security --tier stable

# See related skills
./bin/ask graph related skill-builder --depth 2

# Find path between skills
./bin/ask graph chain skill-creator skill-installer

# Browse by topic cluster
./bin/ask graph topics
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

# Check for duplicate functionality
./bin/ask skills fold source-skill target-skill

# Create new skill scaffold
./bin/ask skills init my-skill --category backend --description "Does X when Y"

# Create plugin scaffold
./bin/ask plugins init my-plugin --with-marketplace
```

### Robot mode (for AI agents)

When your intent is clear but syntax is off, use `--robot` (or `-r`):

```bash
# These all work and get corrected:
./bin/ask skill list --robot          # → skills list
./bin/ask skills ls --robot           # → skills list  
./bin/ask graph search X --robot      # → graph find X
```

**Error handling:** When intent is unclear, you get helpful errors with examples:
```
❌ Unknown topic: 'invalid'

💡 Did you mean 'ask skills'?
   Valid topics: repo, skills, plugins, evals, graph

📚 Examples:
   • ask skills list
   • ask graph find security
```

## Programmatic usage (CI/agents)

```bash
# JSON output with trace IDs
./bin/ask repo status --json --trace-id "build-123"

# Fuzzy matching with corrections
./bin/ask skill list --robot --json | jq '.metadata.correction_note'

# Ephemeral validation (no repo mutation)
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

## Repository layout

```
agent-skills/
├── bin/ask                   # CLI entry point
├── ask skills sync           # Flat projection to .agents/skills/
│
├── backend/                  # Backend platform skills (16)
├── frontend/                 # Frontend UI skills (27)
├── product/                  # Product strategy skills (13)
├── auth/                     # Security operations skills (7)
├── skills-system/            # Meta-skills (installer, creator, etc.)
│
├── scripts/lib/ask/          # CLI implementation
├── docs/cli-specs/           # Implementation contracts
└── ops/metrics/graph/        # Skill relationship data
```

## Documentation

| Document | Purpose |
|----------|---------|
| [CLI Specification](docs/cli-specs/2026-04-06-ask-cli-spec.md) | Full command reference |
| [Agent Guide](AGENTS.md) | AI agent workflow patterns |
| [Skill Index](SKILL.md) | All 123 skills by category |
| [Implementation Review](docs/cli-specs/2026-04-06-ask-cli-implementation-review.md) | Architecture details |

## Governance

- **License:** Apache 2.0
- **Skills:** 123 total across 7 topic clusters
- **Validation:** 10+ automated checks via `ask repo validate`
- **Compatibility:** Codex, Claude Code, Gemini/Antigravity
