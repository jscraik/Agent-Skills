# Agent Skills

A governed repository of **21 skills** for AI coding agents. Built around the **Agent Skills Kit (`ask`)** CLI.

**What this gives you:**

- **One place for skills** – Author in Markdown, sync to any runtime
- **Quality gates** – 28 automated structural, security, and behavioral validation checks
- **Living skill graph** – Browse skills organized by topic clusters with relationship mapping
- **Agent-native CLI** – Fuzzy matching, JSON output, trace IDs, helpful errors

## Quick start

```bash
# Bash-first setup (recommended): open bash, then load repo environment
bash
source Infrastructure/scripts/codex-preflight/codex_env_common.sh && codex_apply_env

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

This table is a human-oriented grouping for quick navigation and is not used for parity enforcement. For the current surfaced catalog size, run `python3 Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py --count --source catalog --visibility default`.

| Topic              | Skills | Examples                                           |
| ------------------ | ------ | -------------------------------------------------- |
| agent-ops          | 44     | coding-harness, evals-router, simplify             |
| frontend-ui        | 15     | react-ui-patterns, shadcn-ui, frontend-ui-design   |
| backend-platform   | 4      | cli-spec, mcp-builder, backend-engineer            |
| product-strategy   | 4      | architecture-interview, chatgpt-apps, interview-me |
| security-ops       | 7      | 1password, best-practices, create-auth             |
| content-publishing | 9      | markdown-converter, spreadsheet, visual-explainer  |
| mobile-native      | 1      | atlas                                               |

## Repository layout

```
agent-skills/
├── bin/ask                   # Stable public wrapper entry point
├── scripts/                  # Stable wrapper entry points for canonical scripts
├── .agents/skills/           # Flat runtime projection (read-only)
│
├── Skills/                   # All canonical skills organised by topic cluster
│   ├── agent-ops/            # 44 skills: coding-harness, evals-router, simplify, …
│   ├── frontend-ui/          # 15 skills: react-ui-patterns, shadcn-ui, frontend-ui-design, …
│   ├── backend-platform/     #  4 skills: cli-spec, mcp-builder, backend-engineer, …
│   ├── product-strategy/     #  4 skills: architecture-interview, chatgpt-apps, interview-me, …
│   ├── security-ops/         #  7 skills: 1password, best-practices, create-auth, …
│   ├── mobile-native/        #  1 skill: atlas
│   └── content-publishing/   #  9 skills: markdown-converter, spreadsheet, visual-explainer
│
├── Plugins/                  # Plugin packages (skills live inside plugins)
│   ├── skill-factory/        #   skill-builder, skill-creator, skill-installer, …
│   ├── plugin-factory/       #   plugin-builder, plugin-creator, plugin-installer
│   ├── harness-engineering/  #   he-brainstorm, he-plan, he-spec, …
│   ├── coderabbit/
│   └── browser-use/
│
├── Infrastructure/
│   ├── bin/ask               # Canonical CLI implementation entrypoint (internal)
│   ├── scripts/lib/ask/      # CLI implementation
│   ├── GOVERNANCE/           # Runtime separation & policy
│   └── ops/metrics/graph/    # Skill relationship data
├── Docs/                     # Plans, specs, guides, cli-specs
├── Wiki/                     # Skill Ops Wiki (notes, playbooks, learnings)
```

Ownership boundaries:
- Canonical authoring: `Skills/<topic-cluster>/**` (7 clusters: agent-ops, frontend-ui, backend-platform, product-strategy, security-ops, content-publishing, mobile-native) plus `Plugins/<plugin>/skills/**`
- Factory mechanics: `Infrastructure/scripts/**`, validation/governance contracts
- Root command wrappers: `bin/**` and `scripts/**` are stable wrappers that forward into `Infrastructure/**`; keep these as real files/directories (not symlinks)
- `bin/ask` is the only public CLI entrypoint and must remain a thin forwarder to `Infrastructure/bin/ask`.
- Runtime/projection surfaces: `.agents/**`, `.agents/skills/**`, `Plugins/cache/**`, `runtime/**` (read-only by policy)
- Full policy: [Docs/agents/14-path-ownership-boundaries.md](Docs/agents/14-path-ownership-boundaries.md)

## Documentation

- **[CLI Specification](Docs/cli-specs/2026-04-06-ask-cli-spec.md)** – Complete command reference
- **[Agent Guide](AGENTS.md)** – AI agent workflow patterns
- **[Skill Index](SKILL.md)** – Current surfaced skill catalog by category
- **[Implementation Review](Docs/cli-specs/2026-04-06-ask-cli-implementation-review.md)** – Architecture details

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for local-first agent workflows. Do not commit credentials, tokens, or personal data. Security and secret checks run in CI, but contributors remain responsible for keeping sensitive values out of commits and generated artifacts.

## Governance

- **License:** Apache 2.0
- **Skills catalog:** `python3 Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py --count --source catalog --visibility default`
- **System skills pin:** `Infrastructure/GOVERNANCE/skills-system-upstream.lock.json` (upstream `openai/skills` `.system` ref `e940b8a86138adf03972802b990a1dfc57fcbf09`)
- **Validation:** 28 automated checks via `ask repo validate`
- **Compatibility:** Codex
