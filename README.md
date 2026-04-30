# Agent Skills

A governed **Agent Skills Kit** repository of **21 skills** for Codex and AI coding agents. Author skills once, validate quality, expose `$` command handles, and sync routed skills and plugins into runtime projections through the `ask` CLI.

**What this gives you:**

- **Canonical source control** - Author skill and plugin workflows in `Skills/**` and `Plugins/**`, not in generated runtime copies.
- **Command-visible handles** - Make routed skills mentionable as `$handle` entries without loading full latent workflows into the picker.
- **Quality gates** - Run structural, security, context-budget, projection, and behavior validation through `ask`.
- **Agent-native CLI** - Use fuzzy matching, JSON output, trace IDs, helpful errors, and robot mode for automation.
- **Runtime sync** - Refresh workspace projections, user runtime links, plugin mirrors, and generated command-surface metadata from canonical sources.

## Quick start

```bash
# Bash-first setup (recommended): open bash, then load repo environment
bash
source Infrastructure/scripts/codex-preflight/codex_env_common.sh && codex_apply_env

# See what's available
ask graph topics
ask skills list --json
ask skills handles --json --no-handles

# Validate the repository
ask repo validate --ephemeral

# Sync to your runtime
ask skills sync --scope workspace --projection rooted
ask skills sync --scope user --projection rooted
```

## What you can do

### Discover skills

```bash
# List the visible runtime surface
ask skills list

# Check all generated command handles
ask skills handles --check --json

# Resolve a command-visible skill handle
ask skills resolve he-heartbeat --json

# Resolve a reviewer/subagent handle
ask reviewers resolve skillinspector --json

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

# Report the current runtime surface and context budget
ask runtime surface --json
ask runtime budget --json

# Verify generated command handles match rooted manifests
ask skills handles --check --json
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

## Distribution

Official installation instructions are maintained in this repository only.

Third-party indexes or mirrors may list this project, but they are not affiliated with, endorsed by, or maintained by this project unless explicitly stated here.

## Robot mode for AI agents

When intent is clear but syntax is off, use `--robot` (or `-r`):

```bash
# These work and get corrected:
ask skill list --robot          # -> skills list
ask skills ls --robot           # -> skills list
ask graph search X --robot      # -> graph find X
```

Errors include suggestions and examples:

```text
ERROR Unknown topic: 'invalid'

Hint: Did you mean 'ask skills'?
   Valid topics: repo, skills, runtime, plugins, evals, graph, mcp, wiki, workouts

Examples:
   - ask skills list
   - ask graph find security
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

## Runtime and command surfaces

This repo separates source, projection, and live runtime visibility:

| Surface                               | Purpose                                                   | Edit Policy            |
| ------------------------------------- | --------------------------------------------------------- | ---------------------- |
| `Skills/<topic>/<skill>/SKILL.md`     | Canonical first-party skill source                        | Edit here              |
| `Plugins/<plugin>/skills/**/SKILL.md` | Canonical plugin-owned skill source                       | Edit here              |
| `.skillsets/**`                       | Generated rooted manifests and command-surface projection | Regenerate only        |
| `.agents/skills/**`                   | Runtime projection consumed by Codex and agent runtimes   | Regenerate only        |
| `~/.agents/skills`, `~/.codex/skills` | User runtime links to the active projection               | Refresh with user sync |

`ask skills list --json` reports the current visible runtime surface. In the current rooted projection this is a compact first-level list of root routers plus generated command handles. `ask skills handles --json --no-handles` validates the full command surface; it currently reports 109 generated command handles with no violations.

A generated command handle, such as `.agents/skills/he-heartbeat/SKILL.md`, is a small pointer that makes `$he-heartbeat` mentionable. It is not the real workflow. The handle resolves to a canonical source path through:

```bash
ask skills resolve he-heartbeat --json
```

Reviewer handles stay outside the skill command surface and resolve through:

```bash
ask reviewers resolve skillinspector --json
```

## Skill graph (manual topic clusters, non-canonical)

This table is a human-oriented grouping for quick navigation and is not used for parity enforcement. For the current visible runtime list, run `ask skills list --json`. For the full generated command-handle surface, run `ask skills handles --json --no-handles`.

| Topic              | Skills | Examples                                           |
| ------------------ | ------ | -------------------------------------------------- |
| agent-ops          | 42     | docs-expert, autofix, unslopify, simplify          |
| frontend-ui        | 13     | react-ui-patterns, shadcn-ui, frontend-ui-design   |
| backend-platform   | 4      | cli-spec, mcp-builder, backend-engineer            |
| product-strategy   | 4      | architecture-interview, chatgpt-apps, interview-me |
| security-ops       | 7      | 1password, best-practices, create-auth             |
| content-publishing | 8      | beautiful-mermaid, spreadsheet, visual-explainer   |
| mobile-native      | 1      | atlas                                              |

## Repository layout

```
agent-skills/
|-- bin/ask                   # Stable public wrapper entry point
|-- scripts/                  # Stable wrapper entry points for canonical scripts
|-- .agents/skills/           # Runtime projection: flat or rooted (read-only)
|-- .skillsets/               # Generated rooted manifests and command surface (read-only)
|-- .workouts/                # Canonical skill workout fixtures
|
|-- Skills/                   # All canonical skills organised by topic cluster
|   |-- agent-ops/            # 42 skills: docs-expert, autofix, unslopify, simplify, ...
|   |-- frontend-ui/          # 13 skills: react-ui-patterns, shadcn-ui, frontend-ui-design, ...
|   |-- backend-platform/     #  4 skills: cli-spec, mcp-builder, backend-engineer, ...
|   |-- product-strategy/     #  4 skills: architecture-interview, chatgpt-apps, interview-me, ...
|   |-- security-ops/         #  7 skills: 1password, best-practices, create-auth, ...
|   |-- mobile-native/        #  1 skill: atlas
|   `-- content-publishing/   #  8 skills: beautiful-mermaid, spreadsheet, visual-explainer
|
|-- Plugins/                  # Canonical plugin packages (skills live inside plugins)
|   |-- skill-factory/        #   skill-builder, skill-creator, skill-installer, ...
|   |-- plugin-factory/       #   plugin-builder, plugin-creator, plugin-installer
|   |-- harness-engineering/  #   he-brainstorm, he-plan, he-spec, ...
|   |-- browser-use/
|   `-- cache/
|
|-- Infrastructure/
|   |-- bin/ask               # Canonical CLI implementation entrypoint (internal)
|   |-- scripts/lib/ask/      # CLI implementation
|   |-- GOVERNANCE/           # Runtime separation & policy
|   `-- ops/metrics/graph/    # Skill relationship data
|-- Docs/                     # Plans, specs, guides, cli-specs
`-- Wiki/                     # Skill Ops Wiki (notes, playbooks, learnings)
```

Ownership boundaries:

- Canonical authoring: `Skills/<topic-cluster>/**` (7 clusters: agent-ops, frontend-ui, backend-platform, product-strategy, security-ops, content-publishing, mobile-native) plus `Plugins/<plugin>/skills/**`
- Factory mechanics: `Infrastructure/scripts/**`, validation/governance contracts
- Root command wrappers: `bin/**` and `scripts/**` are stable wrappers that forward into `Infrastructure/**`; keep these as real files/directories (not symlinks)
- `bin/ask` is the only public CLI entrypoint and must remain a thin forwarder to `Infrastructure/bin/ask`.
- Runtime/projection surfaces: `.agents/**`, `.agents/skills/**`, `.skillsets/**`, `Plugins/cache/**`, `runtime/**` (read-only by policy)
- Plugin runtime mirrors: copied profile-local plugin trees are refreshed from canonical `Plugins/**`; replace them after plugin source or marketplace changes rather than editing mirrors.
- Workout evidence: `.skill-telemetry/**` is local runtime output and is ignored by git.
- Full policy: [Docs/agents/14-path-ownership-boundaries.md](Docs/agents/14-path-ownership-boundaries.md)

## Documentation

- **[CLI Specification](Docs/cli-specs/2026-04-06-ask-cli-spec.md)** - Complete command reference
- **[Agent Guide](AGENTS.md)** - AI agent workflow patterns
- **[Skill Index](SKILL.md)** - Generated visible runtime index
- **[Runtime Projection Modes](Docs/architecture/runtime-projection-modes.md)** - Flat/rooted projection modes, command handles, and sync scope
- **[Context-Budgeted Skill Trees](Docs/architecture/context-budgeted-skill-trees.md)** - Rooted projection, generated command handles, and latent routing model
- **[Skill Workouts](Docs/architecture/skill-workouts.md)** - Workout CLI, telemetry, and scorecard model
- **[Implementation Review](Docs/cli-specs/2026-04-06-ask-cli-implementation-review.md)** - Architecture details

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for local-first agent workflows. Do not commit credentials, tokens, or personal data. Security and secret checks run in CI, but contributors remain responsible for keeping sensitive values out of commits and generated artifacts.

## Governance

- **License:** Apache 2.0
- **Visible runtime surface:** `ask skills list --json`
- **Command surface:** `ask skills handles --json --no-handles`
- **System skills pin:** `Infrastructure/GOVERNANCE/skills-system-upstream.lock.json` (upstream `openai/skills` `.system` ref `e940b8a86138adf03972802b990a1dfc57fcbf09`)
- **Validation:** automated checks via `ask repo validate --ephemeral`
- **Compatibility:** Codex