# Architecture

This document describes the physical architecture of Agent Skills Kit. It is the
orientation map for humans and agents landing in this repository: what problem
the project solves, where major things live, which paths are canonical, which
paths are generated, and what must stay true as the codebase evolves.

Keep this file short and stable. It should answer "where does the thing that
does X live?" and "what am I looking at?" without becoming a second README, a
procedure manual, or an exhaustive tree dump.

If you are trying to use the project, start with [README.md](README.md). If you
are an agent changing the repository, start with [AGENTS.md](AGENTS.md). If you
are changing terminology, read [UBIQUITOUS_LANGUAGE.md](UBIQUITOUS_LANGUAGE.md).

## How to Read This Map

Read this file top-down once, then use symbol search, file search, and `./bin/ask`
to navigate. It intentionally names important files, directories, commands, and
concepts, but leaves implementation detail to owning docs, tests, validators,
and inline code.

This file should change when the repository shape or architectural boundaries
change. It should not change for every local implementation detail.

## Bird's Eye View

Agent Skills Kit is the governed control plane for authoring, validating,
discovering, packaging, projecting, and proving Codex-compatible skills and
agent workflows.

The repository has three kinds of state:

- Ground state: canonical source and policy authored by humans and agents. This
  includes `Skills/**`, `Plugins/**`, `Infrastructure/**`, `Docs/**`, and
  governed `.harness/**` documents.
- Derived state: projections and generated views produced from ground state.
  This includes `.agents/**`, `.skillsets/**`, generated catalog/index content,
  plugin cache mirrors, and validation artifacts.
- Runtime truth: observed behavior from `./bin/ask`, Codex skill loading,
  validation commands, PR checks, review threads, Linear state, and goal-board
  receipts.

**Architecture Invariant:** Runtime truth outranks documentation. When docs,
plans, generated files, or assumptions disagree with executable evidence, stop
and repair the source of truth before continuing.

## Repository Planes

### Product Plane

The product plane contains skill and plugin capability content that users or
agents consume.

- `Skills/**`: first-party skill source grouped by topic cluster.
- `Plugins/<plugin>/skills/**`: plugin-owned skill source.
- `skills-system/**`: governed system-skill bridge pinned by repository policy.

**Architecture Invariant:** Canonical skill source lives in `Skills/**` and
`Plugins/<plugin>/skills/**`. Runtime projections are pointers or generated
views, not editable skill source.

### Factory Plane

The factory plane builds, validates, syncs, packages, and proves the product
plane.

- `Infrastructure/bin/ask`: implementation target for the public `./bin/ask`
  wrapper.
- `Infrastructure/scripts/lib/ask/**`: Python implementation of the ask CLI and
  SDK-like services.
- `Infrastructure/scripts/lifecycle-and-sync/**`: sync, projection, discovery,
  catalog, and lifecycle mechanics.
- `Infrastructure/scripts/validation-and-linting/**`: validators and lint gates.
- `Infrastructure/scripts/testing/**` and `Infrastructure/tests/**`: regression
  tests for factory and command behavior.

**API Boundary:** `./bin/ask` and its documented JSON contracts are public repo
interfaces. Internal helper functions may move, but command behavior must remain
schema-backed and regression-tested.

### Runtime Projection Plane

The runtime projection plane is generated from canonical source so Codex and
other clients can discover skills.

- `.agents/**`: generated runtime projection.
- `.skillsets/**`: generated rooted manifests and command-surface projections.
- `Plugins/cache/**`: copied or cached plugin runtime mirrors.
- root `SKILL.md`: generated root skill index.

**Architecture Invariant:** Generated projections must be reproducible from
canonical source plus repository tooling. Do not hand-edit projection files to
fix behavior; repair the generator or canonical source and regenerate.

### Governance Plane

The governance plane records why work exists, what has been approved, and what
evidence proves progress.

- `.harness/specs/**`: canonical specifications.
- `.harness/plan/**`: implementation plans.
- `Docs/goals/**`: governed goal boards and receipts.
- `.harness/implementation-notes/**`: runtime reasoning ledgers and delivery
  evidence.
- `.harness/quality/**`: quality ledgers such as steering uptake.

**Architecture Invariant:** A plan, spec, or merged historical PR is not proof
that current-scope behavior exists. Completion claims require receipts,
validation evidence, and current delivery state.

### Documentation Plane

The documentation plane explains durable behavior and project conventions.

- `Docs/**`: canonical durable documentation.
- `Wiki/**`: wiki-oriented knowledge surface.
- root front doors such as `README.md`, `AGENTS.md`, and this file.

**Architecture Invariant:** `Docs/**` is the canonical docs casing. Lowercase
`docs/**` is a drift signal unless an explicit migration or compatibility path
owns it.

## Deep Modules

In this repository, a deep module is a bounded capability region with its own
ownership, routing boundary, validation surface, and runtime projection story.
Deep modules are not always single directories. Some are skill-set families,
some are plugin lifecycle lanes, some are factory subsystems, and some are
governance surfaces.

| Deep module | Where to look | What it owns |
| --- | --- | --- |
| Agent operations | `Skills/agent-ops`, `.skillsets/agent-ops` | Repo operations, validation, review, goal governance, runtime proof, docs, testing, automation, and delivery closeout. |
| First-party capability clusters | `Skills/backend-platform`, `Skills/frontend-ui`, `Skills/product-strategy`, `Skills/security-ops`, `Skills/content-publishing`, `Skills/mobile-native` | Bounded skill clusters that route broad user intent into smaller latent modules. |
| Skill Factory | `Plugins/skill-factory` | Skill creation, hardening, refactoring, evaluation, installation, and proof workflows. |
| Plugin Factory | `Plugins/plugin-factory` | Plugin creation, validation, packaging, installation, and lifecycle workflows. |
| Harness Engineering | `Plugins/harness-engineering` | Brainstorm, spec, plan, work, review, eval, reinforce, reconcile, and closeout lifecycle. |
| Ask CLI | `Infrastructure/scripts/lib/ask` | Public command contracts behind `./bin/ask` and the reusable services that power them. |
| Projection and routing | `Infrastructure/scripts/lifecycle-and-sync`, `.skillsets`, `.agents` | Rooted manifests, command-surface metadata, sync mechanics, picker visibility, and runtime discovery. |
| Validation and tests | `Infrastructure/scripts/validation-and-linting`, `Infrastructure/tests`, `Infrastructure/scripts/testing` | Deterministic guardrails for source, projections, docs, skills, governance, and runtime parity. |
| Governance memory | `.harness`, `Docs/goals`, `Wiki` | Specs, plans, implementation notes, receipts, quality ledgers, and operational memory. |

Deep module levels appear in rooted manifests as `router`, `atom`,
`molecule`, and `compound`. The level describes loading and routing shape,
not importance. Root skill sets route into latent modules, while
command-surface handles make selected modules mentionable without loading the
full workflow into runtime context.

**Architecture Invariant:** Deep modules should have explicit ownership, narrow
entrypoints, and local proof. A change that crosses deep modules should update
the relevant contracts, validators, implementation notes, or routing metadata
instead of relying on conversational memory.

## Code Map

### `Skills/`

First-party skill packages. Each skill should follow the local skill package
contract and progressive disclosure expectations.

**Architecture Invariant:** Product skill edits belong here unless a plugin owns
the capability.

### `Plugins/`

Plugin package source, plugin-owned skills, references, fixtures, and metadata.
Plugin caches under `Plugins/cache/**` are runtime mirrors, not source.

**Architecture Invariant:** Plugin source and plugin runtime mirrors are
different ownership surfaces. Cache edits require an explicit projection-refresh
lane.

### `Infrastructure/`

Factory mechanics: ask CLI implementation, scripts, validators, schemas,
policies, tests, reports, and controlled artifacts.

**Architecture Invariant:** Infrastructure code may generate runtime surfaces,
but generated output does not become the source of truth for the generator.

### `Infrastructure/scripts/lib/ask/`

The Python ask CLI implementation. This is where stable SDK primitives should
move as they become proven enough to sit behind `ask`.

**API Boundary:** Public command output is the contract. Prefer schema-backed
JSON and focused command tests before changing output shape.

### `Infrastructure/scripts/lifecycle-and-sync/`

Skill discovery, command-surface generation, rooted projection, sync, plugin
cache refresh, and lifecycle mechanics.

**Architecture Invariant:** Sync code must prove source identity and projection
freshness. Projection success alone is not runtime parity proof.

### `Infrastructure/scripts/validation-and-linting/`

Deterministic checks for repo policy, path ownership, skill contracts, runtime
budget, docs, steering uptake, and other guardrails.

**Architecture Invariant:** Repeated human steering should become a validator,
runtime check, workflow rule, or other durable guardrail when feasible.

### `Infrastructure/tests/` and `Infrastructure/scripts/testing/`

Regression tests for the ask CLI, validators, projection mechanics, schemas,
and governed workflows.

**Architecture Invariant:** Tests should concentrate on boundaries that catch
real drift: CLI contracts, schema contracts, generator freshness, projection
behavior, and runtime parity models.

### `Docs/`

Canonical documentation. Use this for durable architecture, agent guidance,
goals, plans copied into docs, runbooks, and solutions.

**Architecture Invariant:** Do not add new lowercase `docs/**` content. Use
`Docs/**` unless a migration explicitly says otherwise.

### `Wiki/`

Skill-ops knowledge surface for browsable notes, playbooks, and maintained
knowledge. Use it for operational memory and knowledge navigation, not as a
replacement for executable contracts, validators, or canonical docs.

**Architecture Invariant:** Wiki knowledge can explain an operating model, but
repo behavior still needs source, tests, or validation gates.

### `.harness/`

Governed work artifacts: specs, plans, implementation notes, receipts, research,
quality ledgers, and review records. Some subtrees are canonical; timestamped
runtime outputs are ignored unless explicitly curated.

**Architecture Invariant:** `.harness/**` can contain source-of-truth governance
documents, but not every `.harness/**` file is canonical. Follow the path
ownership rules before committing generated evidence.

### `.agents/` and `.skillsets/`

Generated runtime and rooted projection surfaces.

**Architecture Invariant:** `.agents/**` and `.skillsets/**` are generated in
this repository. Edit canonical source or projection code instead.

### `.workouts/` and `.skill-telemetry/`

Workout fixtures and observed skill-exercise evidence. `.workouts/**` is the
canonical workout harness source. `.skill-telemetry/**` is runtime output and
should not be treated as committed product source.

**Architecture Invariant:** Exercise evidence is valuable, but it must stay
separate from the fixtures and contracts that generate it.

### `bin/`

Thin executable front doors. `./bin/ask` is the normal user and agent entrypoint
for repository operations.

**API Boundary:** Agents should prefer `./bin/ask` over ad hoc script calls when
the wrapper has a documented command.

### Root Files

The root is a front door and contract boundary. Root files should be one of:

- orientation docs: `README.md`, `ARCHITECTURE.md`, `AGENTS.md`.
- governance and contribution docs: `CONTRIBUTING.md`, `CODEOWNERS`,
  `SECURITY.md`, `SUPPORT.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`.
- repository contracts and vocabulary: `SKILL.md`, `UBIQUITOUS_LANGUAGE.md`,
  `CONTEXT.md`, `WORKFLOW.md`.
- package/tool entrypoints and config: `Makefile`, `justfile`,
  `harness.contract.json`, `memory.json`, `package-lock.json`, and dotfile
  tool configuration.
- first-class source directories: `Infrastructure/`, `Skills/`, `Plugins/`,
  `Docs/`, `Wiki/`, `bin/`, `brand/`, and `skills-system/`.

Root files should not be one-off migration scripts, local logs, scratch files,
stale proposal documents, or generated runtime output.

## Main Flow

The dominant path through the repository is:

```text
canonical source -> factory tooling -> generated projection -> runtime proof
        ^                                                     |
        |                                                     v
        +------------- governance evidence and fixes ----------+
```

Canonical source starts in `Skills/**`, plugin-owned paths under `Plugins/**`,
or factory code under `Infrastructure/**`. Factory tooling validates and projects
that source into `.skillsets/**`, `.agents/**`, plugin mirrors, and generated
indexes. Runtime proof comes from `./bin/ask`, tests, scorecards, dashboards,
receipts, Browser previews, CI, review state, and tracker truth.

Treat each step as a separate proof. Source existence does not prove projection;
projection does not prove runtime visibility; runtime visibility does not prove
the work is ready to close.

## Cross-Cutting Concerns

### Generated Projections

Generated projections may be committed when the repository contract says they
are compatibility surfaces. They must have a generator and a freshness check.

### Context Budget

The runtime surface is deliberately smaller than the source tree. Root skill
sets and latent manifests keep high-level routing visible while
command-surface metadata resolves selected large workflows only when needed.

### Validation

Prefer deterministic checks over process memory. If a root-surface rule,
projection rule, or package contract matters, encode it in validation.

### Error Handling and Recovery

Treat broken skill input, missing optional metadata, and stale runtime state as
ordinary operating conditions. Recovery paths should classify the blocker and
leave replayable evidence.

### Observability

Implementation notes, receipts, validation artifacts, and review reports are
operational evidence. They should identify the command, outcome, blocker, and
runtime state they observed.

### Governance and Delivery

Governed goal work is complete only when implementation, validation, review
state, PR/CI truth, tracker state, and receipts agree. Do not continue to the
next slice when merge safety or runtime truth is stale.

## See Also

- [Docs/agents/14-path-ownership-boundaries.md](Docs/agents/14-path-ownership-boundaries.md)
- [Docs/agents/15-repo-surface-ownership.md](Docs/agents/15-repo-surface-ownership.md)
- [Docs/architecture/context-budgeted-skill-trees.md](Docs/architecture/context-budgeted-skill-trees.md)
- [Docs/architecture/runtime-projection-modes.md](Docs/architecture/runtime-projection-modes.md)
- [Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md](Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md)
