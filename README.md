# Agent Skills

A governed **Agent Skills Kit** repository for Codex and AI coding agents. Author skills once, validate quality, expose SDK skill names, and sync routed skills and plugins into flat runtime projections through the `ask` CLI.

Agent Skills Kit is the governed repository for teaching Codex and other AI
coding agents how this workspace works.

Use it to author skills once, validate them, expose SDK skill names, and project
the right capabilities into flat runtime without turning every workflow into
prompt context.

The short version:

- Canonical skill source lives in `Skills/**` and `Plugins/*/skills/**`.
- Generated runtime surfaces live in `.agents/**`.
- `./bin/ask` is the public repo command surface.
- Runtime counts drift by design. Ask the CLI for current truth instead of
  trusting a README number.
- Catalog parity marker: **82 canonical skills**. Regenerate this marker with
  the repo skill sync when catalog membership changes.

For the product framing and proof contract, read
[Agent Capability Control Plane](Docs/product/agent-capability-control-plane.md).

## Contents

- [First five minutes](#first-five-minutes)
- [Pick the right path](#pick-the-right-path)
- [Everyday commands](#everyday-commands)
- [Runtime surfaces](#runtime-surfaces)
- [Quality and readiness](#quality-and-readiness)
- [Repository layout](#repository-layout)
- [Further reading](#further-reading)
- [Privacy and Data Handling](#privacy-and-data-handling)
- [Governance](#governance)

## First five minutes

On a fresh checkout, prove the repo-local command surface before relying on
`./bin/ask`:

```bash
bash scripts/bootstrap-ask.sh --json
python3 bin/ask repo status --json
```

If the bootstrap wrapper is unavailable in your shell, use
`python3 bin/ask repo status --json` as the fallback. After status passes,
follow the next command reported by `repo doctor`.

For AI coding agents, use this sequence:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <recommended_capability> --json --robot
./bin/ask skills prove <recommended_capability> --json --robot
./bin/ask repo closeout --changed --json --robot
```

That path answers:

- can I work safely here;
- which capability matches the job;
- how should I use it;
- what proof exists;
- what must pass before I claim done.

## Pick the right path

| Reader job              | Start here                                                    | Why                                                                                                      |
| ----------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| Check repo health       | `./bin/ask repo doctor --json --robot`                        | Combines repo status, catalog parity, runtime budget, SDK projection metadata, and surface diagnostics. |
| Find a skill for a task | `./bin/ask skills improve "<goal>" --json --robot`            | Routes the goal to one capability and returns the next useful command.                                   |
| Understand a skill      | `./bin/ask skills explain <handle> --json --robot`            | Resolves the handle to source, usage, limits, and proof.                                                 |
| Prove a skill           | `./bin/ask skills prove <handle> --json --robot`              | Reports reachability, quality, analytics, and outcome-proof state without merging those lanes.           |
| Audit a skill source    | `./bin/ask skills audit <path> --level strict --json --robot` | Runs the strict structural and policy check for one skill.                                               |
| Close out current work  | `./bin/ask repo closeout --changed --json --robot`            | Reports changed-scope validation and readiness blockers.                                                 |

Use `--robot` when an agent is driving the CLI. The wrapper corrects clear
syntax mistakes and returns structured errors when intent is ambiguous.

## Everyday commands

### Discover capabilities

```bash
./bin/ask skills list --json --robot
./bin/ask skills handles --json --no-handles --robot
./bin/ask skills resolve <handle> --json --robot
./bin/ask reviewers resolve <handle> --json --robot
./bin/ask graph find security --tier stable
./bin/ask graph related skill-factory-router --depth 2
```

### Validate and prove

```bash
./bin/ask repo doctor --json --robot
./bin/ask runtime surface --json --robot
./bin/ask runtime budget --json --robot
./bin/ask repo validate --ephemeral
./bin/ask repo closeout --changed --json --robot
```

### Manage skill lifecycle

```bash
./bin/ask skills install https://github.com/owner/repo --remediate
./bin/ask skills fold source-skill target-skill
./bin/ask skills init my-skill --category backend --description "Does X when Y"
./bin/ask plugins init my-plugin --with-marketplace
```

## Runtime surfaces

This repo separates source, generated projections, and live runtime visibility.

| Surface                               | Purpose                                                   | Edit policy            |
| ------------------------------------- | --------------------------------------------------------- | ---------------------- |
| `Skills/<topic>/<skill>/SKILL.md`     | Canonical first-party skill source                        | Edit here              |
| `Plugins/<plugin>/skills/**/SKILL.md` | Canonical plugin-owned skill source                       | Edit here              |
| `.agents/skills/**`                   | Runtime projection consumed by Codex and agent runtimes   | Regenerate only        |
| `~/.agents/skills`, `~/.codex/skills` | User runtime links to the active projection               | Refresh with user sync |

SDK-flat metadata is generated from canonical skill sources. Obsolete rooted
manifests and command-surface files are not SDK inputs and should not be used as
operator handles.

Resolve canonical skill handles with:

```bash
./bin/ask skills resolve improve-agent-native --json --robot
```

Resolve reviewer or subagent handles with:

```bash
./bin/ask reviewers resolve skillinspector --json --robot
```

Before cleanup, projection changes, or runtime ownership decisions, inspect
repo surface ownership:

```bash
./bin/ask repo surface --json --robot
```

Full ownership policy lives in
[Path Ownership Boundaries](Docs/agents/14-path-ownership-boundaries.md) and
[Repo Surface Ownership](Docs/agents/15-repo-surface-ownership.md).

## Quality and readiness

Keep evidence lanes separate when reporting readiness:

- Local commands prove local command behavior only.
- Skill audits prove structural and policy conformance.
- Evals prove dynamic behavior for the cases they run.
- Plugin Eval, Tessl, and Snyk evidence are separate review lanes.
- PR, CI, review-thread, tracker, and merge-readiness truth require current
  external checks before they can be claimed.

For one skill, use the quality ladder from
[Validation and Checks](Docs/agents/04-validation.md):

```bash
./bin/ask skills audit <skill-path> --level strict --json --robot
./bin/ask evals run <skill-path> --mode smoke --json --robot
./bin/plugin-eval analyze <skill-path> --format json
./bin/ask skills external-review <skill-path> --json --robot
```

Stop at the first failed gate unless you are deliberately collecting a full
matrix. Report the exact command, status, blocker class, and next diagnostic.

## Repository layout

```text
agent-skills/
|-- bin/ask                   # Stable public wrapper entrypoint
|-- scripts/                  # Stable wrapper entrypoints
|-- Skills/                   # Canonical first-party skills
|-- Plugins/                  # Canonical plugin packages and plugin-owned skills
|-- Infrastructure/           # CLI implementation, validators, sync, governance
|-- Docs/                     # Agent guidance, architecture, specs, and product docs
|-- Wiki/                     # Skill Ops Wiki notes, playbooks, and learnings
|-- .agents/skills/           # Runtime projection; regenerate only
`-- .workouts/                # Canonical skill workout fixtures
```

Root wrappers under `bin/**` and `scripts/**` forward into
`Infrastructure/**`. Keep those wrappers as real files or directories.

## Further reading

- [Agent Guide](AGENTS.md) - repo workflow contract for AI agents.
- [Agent Instruction Map](Docs/agents/README.md) - map of detailed policy docs.
- [Agent Operating Contract](Docs/agents/16-agent-operating-contract.md) -
  `ask` CLI behavior and robot mode.
- [Tooling and Command Policy](Docs/agents/02-tooling-policy.md) - wrapper and
  package-command rules.
- [Validation and Checks](Docs/agents/04-validation.md) - repo and skill gates.
- [Skill Management](Docs/agents/17-skill-management.md) - install, audit,
  fold, and line-budget policy.
- [Runtime Projection Modes](Docs/architecture/runtime-projection-modes.md) -
  SDK-flat projection, SDK skill names, and sync scope.
- [CLI Specification](Docs/cli-specs/2026-04-06-ask-cli-spec.md) - full command
  reference.
- [Product Golden Path Command Contracts](Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md) -
  namespace-first product command contracts.

## Privacy and Data Handling

This repository stores skill source, docs, and validation artifacts for
local-first agent workflows. Do not commit credentials, tokens, private
telemetry, or personal data.

## Governance

- **License:** Apache 2.0
- **Compatibility:** Codex and compatible Agent Skills runtimes
- **Visible runtime surface:** `./bin/ask skills list --json --robot`
- **Command surface:** `./bin/ask skills handles --json --no-handles --robot`
- **System skills pin:** `Infrastructure/GOVERNANCE/skills-system-upstream.lock.json`
- **Validation:** `./bin/ask repo validate --ephemeral`
