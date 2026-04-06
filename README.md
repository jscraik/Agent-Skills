# Agent Skills

Canonical skill repository for Codex, Claude Code, and Gemini/Antigravity.

This repo gives you one place to author skills, validate quality,
and sync runtime-ready projections using the **Agent Skills Kit (`ask`)** CLI.

## Table of Contents
- [Unified CLI (`ask`)](#unified-cli-ask)
- [Why teams use this repo](#why-teams-use-this-repo)
- [Quickstart](#quickstart)
- [Common workflows](#common-workflows)
- [Repository layout](#repository-layout)
- [Documentation](#documentation)

## Unified CLI (`ask`)

The `ask` CLI is the authoritative interface for this repository, designed for both human developers and autonomous agents.

- **Dual-Mode DX:** Use standard terminal commands for humans, or `--json` for deterministic, machine-readable output.
- **Safety First:** Mandatory `--dry-run` for all state mutations.
- **Gold Standard:** Adheres to 2026 industry standards for lifecycle provenance and error recovery.

## Quickstart

```bash
# 1) Install/Update the CLI entry point
chmod +x bin/ask

# 2) Health check
./bin/ask repo status

# 3) Validate repo state
./bin/ask repo validate

# 4) Sync skills to runtime projections
./bin/ask skills sync --scope user
```

## Common workflows

### 1) Add and Audit a Skill

```bash
# Install a skill from GitHub with auto-remediation
./bin/ask skills install https://github.com/owner/repo --dest github --remediate

# Run a strict security and quality audit
./bin/ask skills audit github/new-skill --level strict
```

### 2) Maintain a Lean Skill Graph

```bash
# List all skills in a specific category
./bin/ask skills list --category frontend

# Detect semantic overlap between two skills
./bin/ask skills fold source-skill target-skill
```

### 3) Programmatic Usage (Agents)

```bash
# Get machine-readable status with trace-id tracking
./bin/ask repo status --json
```

## Why teams use this repo

- **Single source of truth**: author a skill once, then project it to multiple runtimes with `ask skills sync`.
- **Lower review risk**: every change can run through deterministic validation with per-check logs.
- **Safer automation**: routing and recursive improvement workflows include explicit control files and artifact verification.

## Repository layout

```text
agent-skills/
├── bin/ask                   # Unified CLI entry point
├── auth/ backend/ ...        # Domain-specific skill folders
├── skills-system/            # system-level skills
├── .agents/skills/           # flat projection surface
├── scripts/lib/ask/          # CLI implementation logic
├── artifacts/                # generated reports and telemetry
└── docs/cli-specs/           # Implementation-grade CLI contracts
```

## Documentation

- [Skills index](SKILL.md)
- [ask CLI Specification](docs/cli-specs/2026-04-06-ask-cli-spec.md)
- [Contributor docs](docs/index.md)
- [Governed solutions](docs/solutions/README.md)

## Governance

- License: Apache 2.0 (`LICENSE`)
- Contributing: `CONTRIBUTING.md`
- Security: `SECURITY.md`

<!-- AGENT-FIRST-WORKFLOW:START -->
## Agent-first workflow

1. Create or update a plan in `.agent/PLANS.md`
2. Validate: `python3 ~/.codex/scripts/plan-graph-lint.py .agent/PLANS.md`
3. Verify: `./bin/ask repo validate --ephemeral`
<!-- AGENT-FIRST-WORKFLOW:END -->
