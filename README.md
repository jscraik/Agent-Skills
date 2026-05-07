# Agent Skills

Agent Skills Kit is an **agent capability control plane** for Codex and AI
coding agents.

Teach your coding agents how your work actually works, then prove they
remembered.

This repository manages **71 skills** across 7 topic clusters (agent-ops: 42,
backend-platform: 4, content-publishing: 6, frontend-ui: 10, mobile-native: 1,
product-strategy: 3, security-ops: 5) routed through root-level skill surfaces,
generated `$` command handles, and a larger latent skill/plugin catalog behind
rooted projections. Author a capability once, route it intelligently, validate
quality, project it safely into runtime, and keep the human and agent command
surface small enough to use.

**What this gives you:**

- **Remember workflows** - Keep local review, validation, delivery, and
  operator judgment in canonical skill/plugin source instead of relying on
  agent memory.
- **Keep context small** - Expose root routers and generated `$handle` pointers
  without loading every workflow body into the picker.
- **Prevent drift** - Separate canonical source from generated manifests,
  runtime projections, plugin caches, and historical evidence.
- **Prove quality** - Use `ask` for audits, runtime budget checks, repo surface
  ownership, workout/eval evidence, and machine-readable closeout.

Start with the product framing and proof contract:
[Agent Capability Control Plane](Docs/product/agent-capability-control-plane.md).

## Quick start

```bash
# Bash-first setup (recommended): open bash, then load repo environment
bash
source Infrastructure/scripts/codex-preflight/codex_env_common.sh && codex_apply_env

# See what's available
./bin/ask graph topics
./bin/ask skills list --json
./bin/ask skills handles --json --no-handles

# Validate the repository
./bin/ask repo validate --ephemeral

# Inspect repo surface ownership and runtime budget
./bin/ask repo surface --json
./bin/ask runtime budget --json --robot

# Sync to your runtime
./bin/ask skills sync --scope workspace --projection rooted
./bin/ask skills sync --scope user --projection rooted

# Agent-facing golden paths
./bin/ask repo doctor --json --robot                          # Health check with JSON output
./bin/ask skills improve "improve test coverage" --json --robot
./bin/ask skills explain he-heartbeat --json --robot
```

## What you can do

### Discover skills

```bash
# List the visible runtime surface
./bin/ask skills list

# Check all generated command handles
./bin/ask skills handles --check --json

# Resolve a command-visible skill handle
./bin/ask skills resolve he-heartbeat --json

# Resolve a reviewer/subagent handle
./bin/ask reviewers resolve skillinspector --json

# Search skills
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

# Report the current runtime surface and context budget
./bin/ask runtime surface --json
./bin/ask runtime budget --json

# Verify generated command handles match rooted manifests
./bin/ask skills handles --check --json
```

### Agent-facing golden paths

```bash
# Repository health and diagnostics
./bin/ask repo doctor --json --robot

# Skill improvement workflow
./bin/ask skills improve "improve test coverage" --json --robot
./bin/ask skills improve "add error handling" --json --robot

# Skill explanation and understanding
./bin/ask skills explain he-heartbeat --json --robot
./bin/ask skills explain skill-builder --json --robot

# Skill proof and validation evidence
./bin/ask skills proof backend/cli-spec --json

# Next action suggestions
./bin/ask skills next-action he-heartbeat --json

# Plan closeout workflow
./bin/ask skills closeout my-plan-id --json
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

## Distribution

Official installation instructions are maintained in this repository only.

Third-party indexes or mirrors may list this project, but they are not affiliated with, endorsed by, or maintained by this project unless explicitly stated here.

## Robot mode for AI agents

When intent is clear but syntax is off, use `--robot` (or `-r`):

```bash
# These work and get corrected:
./bin/ask skill list --robot          # -> skills list
./bin/ask skills ls --robot           # -> skills list
./bin/ask graph search X --robot      # -> graph find X
```

Errors include suggestions and examples:

```text
ERROR Unknown topic: 'invalid'

Hint: Did you mean 'ask skills'?
   Valid topics: repo, skills, runtime, plugins, evals, graph, mcp, wiki, workouts

Examples:
   - ./bin/ask skills list
   - ./bin/ask graph find security
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
./bin/ask skills resolve he-heartbeat --json
```

Reviewer handles stay outside the skill command surface and resolve through:

```bash
./bin/ask reviewers resolve skillinspector --json
```

Repo surface ownership is part of the same control-plane contract. Before
cleanup, projection changes, or runtime ownership decisions, use:

```bash
./bin/ask repo surface --json
```

The policy for classifying source, fixtures, generated state, runtime state,
historical artifacts, and unknown ownership lives in
[Repo Surface Ownership](Docs/agents/15-repo-surface-ownership.md).
Namespace-first product command contracts for current and future health,
onboarding, improvement, explanation, proof, next-action, and closeout flows
live in
[ask Product Golden Path Command Contracts](Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md).

## Skill graph (manual topic clusters, non-canonical)

This table is a human-oriented grouping for quick navigation and is not used for parity enforcement. For the current visible runtime list, run `ask skills list --json`. For the full generated command-handle surface, run `ask skills handles --json --no-handles`.

| Topic              | Skills | Examples                                              |
| ------------------ | ------ | ----------------------------------------------------- |
| agent-ops          | 42     | docs-expert, autofix, unslopify, simplify             |
| frontend-ui        | 10     | baseline-ui, frontend-ui-design, ui-visual-regression |
| backend-platform   | 4      | cli-spec, mcp-builder, backend-engineer               |
| product-strategy   | 3      | architecture-interview, deep-interview, interview-me  |
| security-ops       | 5      | 1password, best-practices, create-auth                |
| content-publishing | 6      | beautiful-mermaid, llm-wiki, visual-explainer         |
| mobile-native      | 1      | atlas                                                 |

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
|   |-- frontend-ui/          # 10 skills: baseline-ui, frontend-ui-design, ui-visual-regression, ...
|   |-- backend-platform/     #  4 skills: cli-spec, mcp-builder, backend-engineer, ...
|   |-- product-strategy/     #  3 skills: architecture-interview, deep-interview, interview-me
|   |-- security-ops/         #  5 skills: 1password, best-practices, create-auth, ...
|   |-- mobile-native/        #  1 skill: atlas
|   `-- content-publishing/   #  6 skills: beautiful-mermaid, llm-wiki, visual-explainer
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
- **[Agent Capability Control Plane](Docs/product/agent-capability-control-plane.md)** - Product promise, golden path, and outcome-proof format
- **[Repo Surface Ownership](Docs/agents/15-repo-surface-ownership.md)** - Source, generated, runtime, artifact, and cleanup ownership policy
- **[Product Golden Path Command Contracts](Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md)** - Namespace-first `ask` contracts for doctor, onboard, improve, explain, prove, next, and closeout
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
