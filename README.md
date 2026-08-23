# Agent Skills Kit

Agent Skills Kit is the governed workspace for authoring, validating, and
projecting skills and plugins for Codex and compatible AI coding agents. Its
public command surface is `./bin/ask`: use it to find a skill, check its source,
prove the relevant behavior, and refresh generated runtime views.

The short version:

- Active SDK candidate source may live in `Skills/**` or
  `Plugins/*/skills/**`. Retained package source lives in Skills Foundry. An
  explicit owner decision determines which source is canonical.
- Generated runtime surfaces live in `.agents/**`.
- `./bin/ask` is the public repo command surface.
- Runtime counts drift by design. Ask the CLI for current truth instead of
  trusting a README number.
- Catalog parity marker: **84 canonical skills**. Regenerate this marker with
  the repo skill sync when catalog membership changes.

For the product framing and proof boundary, read
[the Skills SDK local journey](Docs/product/agent-capability-control-plane.md).

## Contents

- [First five minutes](#first-five-minutes)
- [Pick the right path](#pick-the-right-path)
- [Expert and repository commands](#expert-and-repository-commands)
- [Runtime surfaces](#runtime-surfaces)
- [Quality and readiness](#quality-and-readiness)
- [Repository layout](#repository-layout)
- [Further reading](#further-reading)
- [Privacy and Data Handling](#privacy-and-data-handling)
- [Governance](#governance)

## First five minutes

You need Git, Bash, and either `uv` or Python 3.12 or newer. The repository root
has no package-manager install step.

From a fresh checkout, bootstrap and diagnose the repo-local command surface:

```bash
bash scripts/bootstrap-ask.sh --json
./bin/ask repo doctor --json --robot
```

The bootstrap verifies both `./bin/ask` and the documented fallback. If the
wrapper cannot run, use `python3 bin/ask repo status --json` to inspect the
repository without assuming the managed environment is available.

`repo doctor` separates blocking failures from diagnostic advice and reports
one next command when action is useful. A linked worktree may intentionally
report an unmaterialized workspace projection; that warning does not block
source-only documentation or skill work. Commands that require runtime
reachability, including `sdk check`, will remain blocked there until the
reported workspace-sync action is deliberately run or the check is repeated in
the materialized checkout.

For a local skill journey, replace `<skill>` with a handle such as
`technical-writer`. Run the commands in order, and stop if a result reports a
blocker or no further action:

```bash
./bin/ask sdk start <skill> --json --robot
./bin/ask sdk check <skill> --json --robot
./bin/ask skills package verify <skill> --strict --json --robot
./bin/ask skills prove <skill> --json --robot
```

This path answers:

- is this the skill I meant;
- is its source structurally valid;
- can it be packaged without changing the runtime;
- what truth has, and has not, been proved locally.

## Pick the right path

| Goal | Command | What it proves |
| --- | --- | --- |
| Find the next action | `./bin/ask sdk start <skill> --json --robot` | Resolves the target and reports its current local state. |
| Inspect structure | `./bin/ask sdk check <skill> --json --robot` | Summarizes structural evidence and any actionable follow-up. |
| Verify packaging | `./bin/ask skills package verify <skill> --strict --json --robot` | Checks target-bound package readiness without installing it or changing runtime state. |
| Prove behavior | `./bin/ask skills prove <skill> --json --robot` | Reports structural, behavioral, and runtime evidence as separate claims. |

Use `--robot` when an agent is driving the CLI. Combine it with `--json` for a
stable machine-readable envelope, including errors and suggested next steps.
When a command returns `status: error` or `status: blocked`, follow its
`fix_suggestion` or `next_command`; do not treat partial evidence as readiness.

## Expert and repository commands

The following operations serve specific discovery, maintenance, and lifecycle
needs. They are not prerequisites for the four-command local skill journey
above; use them only when a command result or owning runbook directs you here.

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

| Surface                               | Purpose                                                 | Edit policy            |
| ------------------------------------- | ------------------------------------------------------- | ---------------------- |
| `Skills/<topic>/<skill>/SKILL.md`     | Active SDK candidate source owned by this repository    | Edit only when selected |
| `Plugins/<plugin>/skills/**/SKILL.md` | Active SDK plugin candidate source owned by this repo   | Edit only when selected |
| `~/dev/skills-foundry/**`             | Source-only retained package, provenance, and licences  | Copy-first admission    |
| `.agents/skills/**`                   | Runtime projection consumed by Codex and agent runtimes | Regenerate only        |
| `~/.agents/skills`, `~/.codex/skills` | Curated or accepted user runtime skill availability     | Refresh with user sync |
| `~/.agents/plugins`, `~/.codex/plugins` | Curated or accepted user runtime plugin availability  | Refresh with plugin sync |

An explicit owner decision chooses between Skills Foundry retention and an
active SDK candidate in this repository. SDK-flat metadata is generated only
from the selected canonical skill source. Obsolete rooted
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
