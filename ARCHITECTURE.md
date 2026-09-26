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

Agent Skills Kit is a transitional migration repository, not the permanent
authoring or tooling home. Complete the separation before refining either
destination product:

| Destination | Ownership |
| --- | --- |
| Skills SDK (`../skills-sdk`) | Reusable Python lifecycle tooling for creation, repair, validation, evaluation, judging, review, packaging, and handoff. |
| Skills Foundry (`../skills-foundry`) | Retained editable skill and plugin packages, including package-specific scripts, references, assets, eval data, and provenance. |
| Agent-Skills (this repository) | Temporary source and compatibility responsibilities until each recorded transfer and consumer replacement is proved. |

Host credentials, installed runtime configuration, and external services retain
their explicit owners; they do not become SDK core merely because tooling uses
them. A copied package is not an ownership transfer or runtime activation.

The repository has three kinds of state:

- Ground state: canonical source and policy authored by humans and agents. This
  includes `Skills/**`, `Plugins/**`, `Infrastructure/**`, `Docs/**`, and
  governed `.harness/**` documents and authored `.agents/workflows/**` and
  `.agents/PLANS.md`, subject to each package's recorded owner decision.
- Derived state: projections and generated views produced from ground state.
  This includes `.agents/skills/**`, generated catalog/index content,
  plugin cache mirrors, and validation artifacts.
- Evidence: local command and validation results, installed-runtime observations,
  and hosted CI, review, tracker, and delivery records. Each proves only its own
  lane; none grants authority to change an owner or mutate a runtime.

**Architecture Invariant:** Check claims against current implementation and
lane-specific evidence. Resolve conflicting instructions by authority and scope.
Pause only the affected action or claim; repair within authorized scope and
continue independent work.

## Repository Planes

### Product Plane

The product plane contains skill and plugin capability content that users or
agents consume.

- `Skills/**`: first-party skill source grouped by topic cluster.
- `Plugins/<plugin>/skills/**`: plugin-owned skill source.
- `skills-system/**`: governed system-skill bridge pinned by repository policy.

**Architecture Invariant:** These paths describe remaining local source, not
permanent destination ownership. Keep the recorded source authoritative until a
rights-cleared transfer establishes the Foundry owner. Runtime projections are
not editable skill source. See [path ownership](Docs/agents/14-path-ownership-boundaries.md).

### Factory Plane

The transitional factory plane contains the existing local implementation.
Reusable lifecycle tooling belongs in Skills SDK; package-specific behavior
belongs with its package in Foundry. Do not expand this plane into a competing SDK.

- `Infrastructure/bin/ask`: implementation target for the public `./bin/ask`
  wrapper.
- `Infrastructure/scripts/lib/ask/**`: Python implementation of the ask CLI and
  transitional services.
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

- `.agents/skills/**`: generated runtime projection; other `.agents` paths have
  separate ownership.
- `.skillsets/**`: historical rooted metadata, unused by the flat runtime
  resolver but still read by the static explorer. Do not remove its manifests
  until that consumer has migrated.
- `Plugins/cache/**`: copied or cached plugin runtime mirrors.
- root `SKILL.md`: generated root skill index.

**Architecture Invariant:** Generated projections must be reproducible from
canonical source plus repository tooling. Do not hand-edit projection files to
fix behavior; repair the owning generator or canonical source. Regeneration
that mutates an installed runtime requires a separately authorized lane.

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
| Agent operations | `Skills/agent-ops` | Remaining local packages for repo operations, validation, review, docs, and delivery closeout, pending their recorded transfers. |
| First-party capability clusters | `Skills/backend-platform`, `Skills/frontend-ui`, `Skills/product-strategy`, `Skills/security-ops`, `Skills/content-publishing`, `Skills/mobile-native` | Bounded skill clusters that route broad user intent into smaller latent modules. |
| Skill Factory | `Plugins/skill-factory` | Skill creation, hardening, refactoring, evaluation, installation, and proof workflows. |
| Plugin Factory | `Plugins/plugin-factory` | Plugin creation, validation, packaging, installation, and lifecycle workflows. |
| Harness Engineering | `Plugins/harness-engineering` | Brainstorm, spec, plan, work, review, eval, reinforce, reconcile, and closeout lifecycle. |
| Ask CLI | `Infrastructure/scripts/lib/ask` | Transitional command contracts behind `./bin/ask`; reusable tooling transfers to Skills SDK. |
| Projection and routing | `Infrastructure/scripts/lifecycle-and-sync`, `.agents/skills` | Flat-registry discovery, sync mechanics, and runtime projection checks. Historical rooted metadata is not an active routing contract. |
| Validation and tests | `Infrastructure/scripts/validation-and-linting`, `Infrastructure/tests`, `Infrastructure/scripts/testing` | Deterministic guardrails for source, projections, docs, skills, governance, and runtime parity. |
| Governance memory | `.harness`, `Docs/goals`, `Wiki` | Specs, plans, implementation notes, receipts, quality ledgers, and operational memory. |

Historical rooted manifests used `router`, `atom`, `molecule`, and `compound`
levels. The current resolver uses a flat registry and canonical skill names;
those historical levels do not select active runtime routing. See
[runtime projection modes](Docs/architecture/runtime-projection-modes.md).

**Architecture Invariant:** Deep modules should have explicit ownership, narrow
entrypoints, and local proof. A change that crosses deep modules should update
the relevant contracts, validators, implementation notes, or routing metadata
instead of relying on conversational memory.

## Code Map

### `Skills/`

First-party skill packages. Each skill should follow the local skill package
contract and progressive disclosure expectations.

**Architecture Invariant:** Edit the recorded canonical package owner. A package
still awaiting transfer remains repairable here; a transferred package belongs
in Foundry, not in a new competing copy here.

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

The transitional Python ask CLI implementation. Reusable lifecycle primitives
belong in the separate Skills SDK repository, not permanently in this directory.
Keep remaining compatibility responsibilities explicit until consumers migrate.

**API Boundary:** Public command output is the contract. Prefer schema-backed
JSON and focused command tests before changing output shape.

### `Infrastructure/scripts/lifecycle-and-sync/`

Skill discovery, flat-registry projection, sync, plugin cache refresh, and
remaining lifecycle mechanics. Historical rooted artifacts do not establish an
active projection mode.

**Architecture Invariant:** Sync code must prove source identity and projection
freshness. Projection success alone is not runtime parity proof.

### `Infrastructure/scripts/validation-and-linting/`

Deterministic checks for repo policy, path ownership, skill contracts, runtime
budget, docs, steering uptake, and other guardrails.

**Architecture Invariant:** Feedback is diagnostic input, not automatic authority
to add process. Prefer the smallest existing check or local repair. Select new
durable controls only under the named conditions in
[high-signal steering feedback](Docs/agents/19-high-signal-steering-feedback.md).

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

Mixed ownership and historical routing surfaces.

**Architecture Invariant:** `.agents/skills/**` is generated, while tracked
`.agents/workflows/**` and `.agents/PLANS.md` are authored guidance. Do not
overwrite the latter during projection cleanup. `.skillsets/**` retains
historical metadata still consumed by the static explorer, not the flat runtime
resolver. Preserve it until consumer cutover. Check path ownership
before editing or removing any of these surfaces.

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
  `harness.contract.json`, `memory.json`, and dotfile
  tool configuration.
- first-class source directories: `Infrastructure/`, `Skills/`, `Plugins/`,
  `Docs/`, `Wiki/`, `bin/`, `skills-sdk/brand/`, and
  `skills-system/`.

Root files should not be one-off migration scripts, local logs, scratch files,
stale proposal documents, or generated runtime output.

## Main Flow

For remaining local consumers, the transitional runtime path is:

```text
canonical source -> factory tooling -> generated projection -> runtime proof
        ^                                                     |
        |                                                     v
        +------------- governance evidence and fixes ----------+
```

Source comes from the recorded canonical owner. Existing local source may remain
under `Skills/**`, `Plugins/**`, or `Infrastructure/**` pending transfer. Selected
tooling can validate source or, in an authorized runtime lane, project it into
`.agents/skills/**`, plugin mirrors, and generated indexes. Source-only validation
does not require runtime mutation. Tests, installed-runtime observations, and
hosted delivery records remain separate evidence lanes.

Treat each step as a separate proof. Source existence does not prove projection;
projection does not prove runtime visibility; runtime visibility does not prove
the work is ready to close. Retire Agent-Skills only after destination replacements
are delivered and retained consumers demonstrate success, failure, and recovery
without this repository, with matching retirement authority. One pilot or merged
PR does not prove programme completion.

## Cross-Cutting Concerns

### Generated Projections

Generated projections may be committed when the repository contract says they
are compatibility surfaces. They must have a generator and a freshness check.

### Context Budget

Use progressive disclosure within packages to keep entrypoints small. Current
discovery uses flat-registry skill names; do not rely on historical rooted or
latent manifests to provide active context-budget enforcement.

### Validation

Prefer existing deterministic checks over process memory. Add enforcement only
when the authorized change and risk justify it; a documentation correction does
not automatically require new validation machinery.

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
dependent delivery action when its required evidence is stale. Missing hosted
or runtime proof blocks that claim, not independent authorized local repairs.

## See Also

- [Docs/agents/14-path-ownership-boundaries.md](Docs/agents/14-path-ownership-boundaries.md)
- [Docs/agents/15-repo-surface-ownership.md](Docs/agents/15-repo-surface-ownership.md)
- [Docs/architecture/context-budgeted-skill-trees.md](Docs/architecture/context-budgeted-skill-trees.md)
- [Docs/architecture/runtime-projection-modes.md](Docs/architecture/runtime-projection-modes.md)
- [Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md](Docs/goals/jsc-351-agent-skills-codex-abi-conformance/goal.md)
