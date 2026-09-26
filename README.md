# Agent Skills Kit

Agent Skills Kit is the transitional `agent-skills` repository being separated
into Skills SDK and Skills Foundry. Complete the separation before refining
either product:

- **Skills SDK** owns reusable Python tooling for creation, repair, validation,
  evaluation, judging, review, packaging, and handoff.
- **Skills Foundry** owns retained editable skill and plugin packages, including
  package-specific scripts, eval data, references, assets, provenance, and rights.
- **Agent-Skills** retains existing source, commands, and compatibility surfaces
  only until their replacements and consumer cutovers are proved.

`./bin/ask` remains this repository's transitional command surface, not the
permanent Skills SDK implementation. Host credentials, installed runtime
configuration, and third-party services retain their explicit owners.

The short version:

- Existing package source may remain in `Skills/**` or `Plugins/*/skills/**`
  until recorded transfer. A tooling candidate does not change source ownership.
- `.agents/skills/**` is generated runtime projection; tracked
  `.agents/workflows/**` and `.agents/PLANS.md` are authored guidance.
- `./bin/ask` is the public repo command surface.
- Runtime counts drift by design. Ask the CLI for current truth instead of
  trusting a README number.
- Catalog parity marker: **85 canonical skills**. Regenerate this marker with
  the repo skill sync when catalog membership changes.

For current ownership and cutover rules, read
[Path Ownership Boundaries](Docs/agents/14-path-ownership-boundaries.md).
[The Skills SDK local journey](Docs/product/agent-capability-control-plane.md)
describes the existing transitional CLI journey, not proof that separation or
the destination product backlog is complete.

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

For the existing Agent-Skills local skill journey, replace `<skill>` with a handle such as
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

| Goal                 | Command                                                           | What it proves                                                                         |
| -------------------- | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Find the next action | `./bin/ask sdk start <skill> --json --robot`                      | Resolves the target and reports its current local state.                               |
| Inspect structure    | `./bin/ask sdk check <skill> --json --robot`                      | Summarizes structural evidence and any actionable follow-up.                           |
| Verify packaging     | `./bin/ask skills package verify <skill> --strict --json --robot` | Checks target-bound package readiness without installing it or changing runtime state. |
| Inspect proof        | `./bin/ask skills prove <skill> --json --robot`                   | Reports structural, behavioral, and runtime evidence as separate claims.               |

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

| Surface                                 | Purpose                                                 | Edit policy              |
| --------------------------------------- | ------------------------------------------------------- | ------------------------ |
| `Skills/<topic>/<skill>/SKILL.md`       | Transitional source pending recorded transfer | Follow explicit owner and rights |
| `Plugins/<plugin>/skills/**/SKILL.md`   | Transitional plugin source pending recorded transfer | Follow explicit owner and rights |
| `~/dev/skills-foundry/**`               | Retained editable packages after source transfer | Rights-cleared admission and repairs |
| `~/dev/skills-sdk/**`                   | Reusable Python lifecycle tooling | Follow SDK repository guidance |
| `.agents/skills/**`                     | Runtime projection consumed by Codex and agent runtimes | Regenerate only          |
| `.agents/workflows/**`, `.agents/PLANS.md` | Authored workflow and planning guidance | Edit in its applicable scope |
| `~/.agents/skills`, `~/.codex/skills`   | Curated or accepted user runtime skill availability     | Refresh with user sync   |
| `~/.agents/plugins`, `~/.codex/plugins` | Curated or accepted user runtime plugin availability    | Refresh with plugin sync |

An explicit owner decision records source authority and transfer; selecting a
package for SDK tooling does not move its editable source. Rights-cleared copies
alone do not complete transfer or authorize runtime installation. Flat metadata
is generated from the accepted source inputs. Rooted manifests and legacy
command-surface files are not inputs to the flat runtime resolver and should not
be used as operator handles. However, `ask sdk explorer static --preview` still
reads `.skillsets/*/manifest.jsonl`; preserve those manifests until that consumer
has migrated. Flat discovery does not prove all legacy consumers are retired.

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

For a source-only correction, start with static source admission and the
applicable package and focused behavioral checks:

```bash
./bin/ask skills audit <skill-path> --level strict --source-only --json --robot
./bin/ask skills package verify <skill-path> --json --robot
```

These commands do not prove behavior or installed runtime readiness. Run the
declared focused behavioral proof when required and authorized. Use the runtime
or promotion ladder in [Validation and Checks](Docs/agents/04-validation.md)
only when that lane is selected. Source edits alone do not authorize runtime
sync, model calls, or external services. Stop dependent checks at the first
failed required gate; report the exact command, status, and next diagnostic.

Separation requires delivered destination replacements, every retained consumer's
success/failure/recovery proof without Agent-Skills dependencies, and authorized
retirement of old operational surfaces. Merged PRs or one successful pilot do
not prove the whole separation complete.

## Repository layout

```text
agent-skills/
|-- bin/ask                   # Stable public wrapper entrypoint
|-- scripts/                  # Stable wrapper entrypoints
|-- Skills/                   # Transitional skill sources pending transfer
|-- Plugins/                  # Transitional plugin sources and separate caches
|-- Infrastructure/           # Existing CLI/mechanics pending extraction or retirement
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
