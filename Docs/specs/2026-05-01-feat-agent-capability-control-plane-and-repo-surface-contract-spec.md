---
schema_version: 1
title: Agent Capability Control Plane and Repo Surface Contract
type: feat
status: ready_for_plan
date: 2026-05-01
origin: conversation: blunt product critique, deadcode assessment, and infra-backed cleanup consolidation
linear_project: agent-skills
linear_issue: JSC-246
linear_status: Open
traceability_required: true
risk: medium-high
spec_depth: full
ui_required: false
---

# Agent Capability Control Plane and Repo Surface Contract

## Table of Contents

- [Spec Mode Decision](#spec-mode-decision)
- [Problem Statement](#problem-statement)
- [Product Thesis](#product-thesis)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Linear Work Item Contract](#linear-work-item-contract)
- [System Boundary](#system-boundary)
- [Current-State Baseline](#current-state-baseline)
- [Core Domain Model](#core-domain-model)
- [Domain Consistency Pass](#domain-consistency-pass)
- [Main Flow / Lifecycle](#main-flow--lifecycle)
- [Interfaces and Dependencies](#interfaces-and-dependencies)
- [Interface Design Pass](#interface-design-pass)
- [Repo Surface Contract](#repo-surface-contract)
- [Product Golden Paths](#product-golden-paths)
- [Invariants / Safety Requirements](#invariants--safety-requirements)
- [Failure Model and Recovery](#failure-model-and-recovery)
- [Observability](#observability)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Linear Acceptance Traceability](#linear-acceptance-traceability)
- [Planning-Ready First Slice](#planning-ready-first-slice)
- [Open Questions](#open-questions)
- [Definition of Done](#definition-of-done)
- [Handoff to `he-plan`](#handoff-to-he-plan)

## Spec Mode Decision

Use `standard-spec` with `spec_depth: full`.

This is a system and product contract for the Agent Skills Kit. It touches
repository ownership, generated/runtime surfaces, validation gates, `ask` CLI
behavior, progressive disclosure, and agent/human usability. It is not a UI
contract, so `ui_required: false`.

This spec is tracked by Linear issue `JSC-246`. The issue owns delivery
coordination for the repo surface contract, non-destructive inventory gate, and
agent capability control-plane golden paths.

## Problem Statement

The Agent Skills Kit has the right underlying architecture but the wrong first
impression. It is stronger than "a repo of skills"; it is an agent capability
control plane: author capabilities once, route them intelligently, validate their
quality, project them safely into runtime, and make them usable by both humans
and AI coding agents.

The current repository already contains the machinery for that control plane:
canonical skill source, generated command handles, runtime projection, `ask`
CLI operations, strict audits, runtime budget checks, sync, routing, workouts,
artifacts, and deferred context. The problem is that source, generated state,
historical evidence, runtime mirrors, archived material, and product workflows
are not consistently separated at the filesystem or CLI level.

That causes three kinds of friction:

- Humans see too many concepts before they see the value.
- Agents must infer which surface is canonical, generated, archived, or safe to
  edit.
- Deadcode cleanup risks becoming a taste-based deletion pass instead of a
  repeatable, validated repository operation.

The next improvement should therefore consolidate product clarity and deadcode
cleanup around one infrastructure-backed principle:

> Every tracked file must be source, fixture, policy, reference, or intentional
> archive. Everything else must be generated, ignored, or deleted.

## Product Thesis

The public promise should be:

> Teach your coding agents how your work actually works, then prove they
> remembered.

The repository should lead with outcomes rather than internal taxonomy:

- Make agents remember local workflows.
- Keep agent context small.
- Prevent skill and projection drift.
- Prove capability quality with validation, workouts, and reproducible evidence.

The product should feel task-first:

```text
Tell Agent Skills Kit what kind of work you do
-> it proposes capabilities
-> it installs, routes, validates, and projects them
-> it proves the runtime behavior changed
```

The internal model can remain infrastructure-grade, but the front door should not
ask users to understand the whole machine before receiving value.

## Goals

- Define a repo surface ownership contract that distinguishes source, fixtures,
  policy, references, generated outputs, runtime state, historical artifacts,
  vendored snapshots, and unknown files.
- Add an inventory gate that classifies tracked files and reports policy
  violations before any destructive cleanup.
- Route the inventory through `./bin/ask`, with machine-readable JSON for agents
  and concise human output for operators.
- Remove or archive historical generated evidence only after classification and
  reference scans prove it is not active source, fixture, policy, or intentional
  preserved context.
- Preserve context by moving needed long-form material into references and
  indexing it, not by trimming important context out of existence.
- Make generated/runtime surfaces explicit: either tracked canonical snapshots,
  reproducible outputs, vendored snapshots, or ignored local state.
- Introduce product golden paths that make the control plane usable without
  requiring users to learn the whole taxonomy first.
- Reduce interaction bloat by exposing fewer first-level concepts and stronger
  "what should I do next?" contracts for both humans and agents.
- Prevent regression with validation checks that fail on newly tracked generated
  artifacts, runtime databases, plugin caches, duplicate infra paths, and broken
  active/archive/deferred references.

## Non-Goals

- Do not delete files in the first implementation slice.
- Do not hand-edit runtime projections such as `.agents/skills/**` when a sync or
  projection path owns them.
- Do not collapse deferred context just to reduce line count; preserve it behind
  references and indexes.
- Do not rebrand or rewrite every skill as part of this spec.
- Do not change Codex desktop runtime behavior.
- Do not replace plugin marketplace behavior or OpenAI-curated plugin semantics.
- Do not treat validation pass/fail as the only proof of product value; outcome
  proof is a later but required capability.

## Linear Work Item Contract

Linear issue: `JSC-246`

Title: Build repo surface contract and agent capability control-plane golden
paths.

Status: Open.

Project: `agent-skills`.

Team: `Jscraik`.

Priority: High.

Labels: `Roadmap: Next`, `Agent`, `Infra`, `Feature`, `Improvement`.

The Linear issue tracks the full contract in this spec, but the first delivery
slice is intentionally non-destructive: add policy, inventory, `ask` routing,
JSON shape, tests, and a live report before deleting any tracked artifacts.

## System Boundary

### Owned Surfaces

- `./bin/ask` command surface and its repo-level subcommands.
- `Infrastructure/scripts/lib/ask/**` command implementations.
- `Infrastructure/scripts/validation-and-linting/**` validation scripts.
- `Infrastructure/scripts/lifecycle-and-sync/**` discovery, sync, selection, and
  projection scripts.
- `Docs/agents/**`, `Docs/architecture/**`, `Docs/specs/**`, and related
  operator documentation.
- `.gitignore` policy for generated and runtime surfaces.
- Artifact and evidence directories when they are tracked in git.
- Skill source and plugin source only where ownership metadata or reference
  routing must be clarified.

### Referenced Surfaces

- `Skills/**`
- `Plugins/*/skills/**`
- `.agents/skills/**`
- `.skillsets/**`
- `Plugins/cache/**`
- `Infrastructure/artifacts/**`
- `artifacts/**`
- `.harness/**`
- `skills-system/**`
- `Infrastructure/references/deferred-skill-context/**`

### Out of Scope

- Provider runtime internals.
- Non-Agent Skills Kit repositories.
- Large-scale content rewrites of skill bodies.
- Unrelated branch, CI, or release automation changes.

## Current-State Baseline

This spec is anchored to the observed repository state from the product critique
and cleanup investigation on 2026-05-01.

Known evidence:

- `./bin/ask repo status --json --robot` reported the repo as synced during the
  critique pass.
- Runtime budget passed mechanically, with no collisions or unresolved mappings.
- Runtime surface still appeared cognitively large:
  - `advanced_visible_count`: `162`
  - advisory threshold: `60`
  - first-level default entries: `109`
  - estimated description tokens: `3172`
- `artifacts/` was approximately `51M`.
- `Infrastructure/artifacts/` was approximately `29M`.
- `git ls-files artifacts Infrastructure/artifacts | wc -l` reported `3690`
  tracked files.
- `.gitignore` already ignores many generated artifact paths, so much of the
  tracked artifact mass appears to be historical state that predates the ignore
  policy or escaped cleanup.
- `Infrastructure/Infrastructure/artifacts/**` appeared as a suspicious nested
  infra path that should be audited before any retention decision.
- `.skillsets/**`, `.harness/context-compound.db`, and `skills-system/**` need an
  explicit tracked-vs-generated-vs-vendored ownership decision.

These numbers are evidence for the spec, not constants. The first implementation
slice must regenerate the inventory from live repository state.

## Core Domain Model

### Agent Capability Control Plane

The governed system for authoring, routing, validating, projecting, and proving
agent capabilities across human and AI-agent workflows.

### Canonical Skill Source

The editable source of a skill under `Skills/**` or an authored plugin skill
tree. Canonical source is tracked and reviewed.

### Generated Command Handle

A small `.agents/skills/<handle>/SKILL.md` pointer that makes `$<handle>`
mentionable and resolves to canonical source. It is not the real workflow.

### Runtime Projection

Generated runtime material consumed by Codex or another agent runtime. Runtime
projection must be reproducible and should not be hand-edited.

### Repo Surface

The set of tracked and untracked filesystem paths that a human or agent sees
while working in the repository.

### Surface Classification

The policy category assigned to a path:

- `source`
- `fixture`
- `policy`
- `reference`
- `intentional_archive`
- `vendored_snapshot`
- `generated_tracked`
- `generated_ignored`
- `runtime_state`
- `historical_artifact`
- `unknown`

### Preserved Deferred Context

Long-form context that remains available by reference but is not loaded by
default. Deferred context is not bloat when it is indexed, intentionally
referenced, and excluded from first-level runtime pressure.

### Interaction Bloat

Excess visible handles, first-level concepts, or docs that make the system harder
to operate even if the files are technically valid.

### Outcome Proof

Evidence that a capability improved agent behavior on a real or representative
task, not merely that its markdown structure passed validation.

## Domain Consistency Pass

This spec uses the repo's existing runtime vocabulary from `CONTEXT.md` and
`UBIQUITOUS_LANGUAGE.md`.

Canonical terms for this work:

- Use **Agent Skills Kit** for the repository and CLI system, not "skills repo"
  or "prompt library".
- Use **Canonical Skill Source** for editable skill files.
- Use **Generated Command Handle** for `$`-mentionable runtime pointers such as
  `$he-spec`; do not call these the real workflow.
- Use **Runtime Projection** for generated runtime skill layouts.
- Use **Root Skill Set** and **Latent Skill Module** when describing rooted
  runtime selection.
- Use **Advanced Catalog** when discussing expanded inspection surfaces; avoid
  "full dump" because the goal is controlled discovery, not unbounded exposure.
- Use **Repo Surface** for the filesystem and command-facing set of paths a
  human or agent must reason about in this repository.
- Use **Surface Inventory** for the proposed classification report; avoid making
  "bloat" the canonical internal term, because the command must classify files
  before judging them.

Resolved ambiguity:

- `ask doctor` already appears as an alias shape for `ask repo doctor-catalog`.
  This spec selects namespace-first product commands for implementation:
  `ask repo doctor`, `ask repo onboard`, `ask skills improve`, `ask skills
  explain`, `ask skills prove`, `ask repo next`, and
  `ask repo closeout --changed`. Top-level aliases are compatibility/product
  follow-ons only after evidence shows they reduce operator friction.
- `repo bloat` is useful operator language, but the canonical P0-P2 command is
  `ask repo surface`. `ask repo bloat` is a post-P2 alias candidate, not an
  acceptance command for the first slice.
- `.skillsets/**`, `.harness/*.db`, and `skills-system/**` remain unresolved
  ownership terms until the first inventory report classifies them from live
  evidence.

Planning readiness condition:

- If implementation discovers a conflict between this spec and `CONTEXT.md`,
  `UBIQUITOUS_LANGUAGE.md`, or existing `ask` command terminology, update the
  spec and the relevant context source before planning proceeds to code changes.

## Main Flow / Lifecycle

### 1. Inventory

The first slice scans tracked files from `git ls-files` and classifies them by
policy category. Later report-only discovery may add selected ignored/generated
paths, but those paths must not influence cleanup decisions until the policy
adds explicit ownership rules for them.

Required outputs:

- human summary
- JSON report
- violation list
- allowlist references
- recommended next command

### 2. Policy Decision

Unknown or ambiguous surfaces are resolved into one of:

- keep as source, fixture, policy, reference, or intentional archive
- document as vendored snapshot
- convert to generated output
- ignore going forward
- delete after reference scan

### 3. Reference Scan

Before any destructive cleanup, the system checks whether a candidate path or
retired skill name is referenced by active source, docs, fixtures, generated
handles, or deferred context indexes.

### 4. Cleanup

Only classified, unreferenced, or explicitly archived generated material is
removed from git. Cleanup must avoid active skill source, active plugin source,
runtime source of truth, and preserved deferred context.

### 5. Validation

The repository runs focused checks for:

- surface inventory policy
- broken active/archive/deferred links
- runtime budget
- handle resolution
- skill sync/projection health
- repo validation closeout

### 6. Product Simplification

After the filesystem contract is enforced, the CLI should reduce cognitive load
with stronger task-first workflows:

- `ask repo doctor`
- `ask repo onboard`
- `ask skills improve "<goal>"`
- `ask skills explain <handle>`
- `ask skills prove <skill-or-goal>`
- `ask repo next --json`
- `ask repo closeout --changed`

## Interfaces and Dependencies

### CLI Interfaces

The following commands define the target user and agent experience:

```bash
./bin/ask repo surface --json
./bin/ask repo doctor
./bin/ask repo onboard
./bin/ask skills improve "<goal>"
./bin/ask skills explain <handle>
./bin/ask skills prove <skill-or-goal>
./bin/ask repo next --json
./bin/ask repo closeout --changed
```

Naming may change during planning, but the behavioral contracts must survive:

- classify the repo surface
- recommend the next safe action
- explain capabilities in human terms
- map goals to capabilities
- validate changed surfaces
- prove outcome improvement

### Validation Interfaces

Target validation surfaces:

```bash
./bin/ask repo surface --json
./bin/ask runtime budget --json --robot
./bin/ask skills handles --check --json
./bin/ask repo validate
```

The implementation may route to lower-level scripts, but `ask` remains the
public interface.

### Script Interfaces

A new inventory script should be added under validation infrastructure, for
example:

```text
Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py
```

The exact filename can change in planning, but it must provide:

- JSON output
- non-zero exit on policy violations when strict mode is enabled
- allowlist support with reasons
- enough detail for agents to repair or report findings without reading every
  path manually

Allowlist contract:

- Canonical path: `Infrastructure/policy/repo_surface_allowlist.json`.
- Shape: a JSON object with `schema_version: 1` and an `entries` array.
- Each entry must include `id`, `match_type`, `pattern`, `classification`,
  `reason`, `owner`, and `expires` or `review_after`.
- `match_type` must be one of `exact`, `glob`, or `prefix`; regex matching is
  excluded from the first slice to keep matching deterministic.
- Allowlist entries can downgrade a finding from blocking to warning only when
  the entry classification matches the classifier result and the reason is
  non-empty.
- More specific entries win in this order: `exact`, then longest `prefix`, then
  longest `glob` pattern. Ties sort by `id`.

## Interface Design Pass

This spec introduces two caller-facing boundaries:

- the inventory/reporting boundary for repo surface classification
- the task-first product boundary for humans and agents using `ask`

### Boundary 1: Surface Inventory Command Shape

#### Shape A: `ask repo bloat` Post-P2 Alias Candidate

Call shape:

```bash
./bin/ask repo bloat --json
./bin/ask repo bloat --strict
```

Caller usage example:

```bash
./bin/ask repo bloat --json
```

What it hides internally:

- `git ls-files` scans
- ignore-policy checks
- generated/runtime path classification
- allowlist matching
- size estimation
- violation formatting

Tradeoffs:

- Strong human language for the visible pain: "what can we cut?"
- Easy to remember during cleanup work.
- Slightly too judgmental for policy enforcement, because not every flagged path
  is actually bloat.
- Risks encouraging deletion-first thinking unless the output is explicitly
  classification-first.

#### Shape B: `ask repo surface`

Call shape:

```bash
./bin/ask repo surface --json
./bin/ask repo surface --strict
```

Caller usage example:

```bash
./bin/ask repo surface --json
```

What it hides internally:

- all Shape A internals
- policy category assignment
- owned-vs-generated-vs-runtime decision hints
- next-command recommendation

Tradeoffs:

- Better canonical domain language for policy and validation.
- Scales beyond deadcode into repo ownership, projection, and runtime safety.
- Less emotionally obvious to users who simply want to remove junk.
- May need an alias or summary mode to feel discoverable.

Selected contract:

- Implement the canonical boundary as `ask repo surface`.
- Treat `ask repo bloat` as a post-P2 human-friendly alias candidate only if
  later planning confirms the command router can support it without
  command-surface confusion.
- JSON must use policy language: `classification`, `status`, `code`,
  `severity`, `blocking`, `reason`, `recommendation`, `allowlist_entry`, and
  `next_command`.
- `allowlist_entry` is required and must be either `null` or the matching
  allowlist entry `id`.
- Human output may use bloat language, but it must never recommend deletion
  before reference scan and classification.

### Boundary 2: Product Golden Path Command Shape

#### Shape A: Deferred Top-Level Alias Sketch

This shape is not selected for implementation. It records possible future
aliases only after namespace-first commands prove lower friction.

Future alias sketch: top-level shortcuts could forward to the selected
namespace-first commands after P4 proves the alias reduces real friction. The
first-slice acceptance contract must not depend on any top-level alias.

What it hides internally:

- repo status
- skill discovery
- overlap/conflict checks
- runtime projection checks
- validation recommendations
- next safe action

Tradeoffs:

- Excellent human memorability.
- Strong product feel.
- Risks expanding the top-level command surface if each command is implemented
  as a peer.
- Requires careful alias handling because parts of `doctor` already exist under
  `repo`.

#### Shape B: Grouped Product Commands Under Existing Namespaces

Call shape:

```bash
./bin/ask repo doctor
./bin/ask repo onboard
./bin/ask skills improve "<goal>"
./bin/ask skills explain <handle>
./bin/ask skills prove <skill-or-goal>
./bin/ask repo next --json
./bin/ask repo closeout --changed
```

Caller usage example:

```bash
./bin/ask skills improve "make my agents better at fixing PR comments"
```

What it hides internally:

- same internals as Shape A, routed through existing namespaces

Tradeoffs:

- Better fit with current command taxonomy.
- Lower risk of top-level command sprawl.
- Slightly less compelling as a product front door.
- Users must know whether a goal belongs under `repo` or `skills`.

Selected contract:

- Keep implementation under existing namespaces first: `repo`, `skills`, and
  closeout/reporting routes.
- Add memorable top-level aliases only where they demonstrably reduce first-run
  friction and do not conflict with existing aliases.
- `ask next --json` can be implemented as a cross-namespace recommendation
  endpoint only if it does not duplicate every command's own `next_steps`
  envelope.
- `ask repo closeout --changed` should be designed as the agent-native completion
  contract because it spans repo state, changed files, generated sync needs, and
  validation.

## Repo Surface Contract

Tracked files must be one of:

- `source`: authored implementation, skill, plugin, script, or documentation.
- `fixture`: explicit test fixture or golden sample used by tests or validation.
- `policy`: governance, selection, routing, validation, or ownership contract.
- `reference`: intentionally preserved supporting material loaded through
  progressive disclosure.
- `intentional_archive`: historical material retained with an index, reason, and
  retention boundary.
- `vendored_snapshot`: third-party or runtime mirror material retained with an
  update command and ownership note.

Files should not be tracked when they are:

- generated evidence with no fixture role
- runtime state
- plugin cache output
- local telemetry
- timestamped run logs
- JSONL event streams from historical runs
- nested accidental copies
- unknown ownership residue

### Initial Path Policy

| Path Pattern                                          | Default Classification            | Required Behavior                                                   |
| ----------------------------------------------------- | --------------------------------- | ------------------------------------------------------------------- |
| `Skills/**`                                           | `source`                          | Tracked; edit canonical source only.                                |
| `Plugins/*/skills/**`                                 | `source`                          | Tracked when authored plugin source.                                |
| `.agents/skills/**`                                   | `generated_tracked` or projection | Do not hand-edit; regenerate through sync.                          |
| `Plugins/cache/**`                                    | `generated_ignored`               | Never newly track.                                                  |
| `Infrastructure/artifacts/**`                         | `historical_artifact`             | Ignore by default; track only allowlisted fixtures or indexes.      |
| `artifacts/**`                                        | `historical_artifact`             | Ignore by default; keep summaries, not full event streams.          |
| `.skillsets/**`                                       | undecided                         | Decide generated output vs canonical snapshot; validate either way. |
| `.harness/*.db`                                       | `runtime_state` by default        | Do not track unless moved under fixtures and documented.            |
| `skills-system/**`                                    | undecided                         | Decide vendored snapshot vs generated mirror vs removable.          |
| `Infrastructure/references/deferred-skill-context/**` | `reference`                       | Preserve when indexed and intentionally referenced.                 |
| `Infrastructure/Infrastructure/**`                    | `unknown` violation               | Audit; likely accidental nested output unless allowlisted.          |

## Product Golden Paths

### `ask repo doctor`

One remembered health command for humans and agents.

Expected output:

- repo health
- sync health
- runtime budget status
- handle status
- bloat/surface policy status
- known blockers
- recommended repair command

### `ask repo onboard`

Guided first-run flow.

Expected output:

- current repo identity
- active runtime links
- available root routers
- existing capability families
- missing setup steps
- recommended next move

### `ask skills improve "<goal>"`

Goal-to-capability workflow.

Expected output:

- interpreted goal
- candidate skills/plugins/workflows
- overlap with OpenAI or local plugin capabilities
- recommended install, audit, routing, or sync action
- validation command

### `ask skills explain <handle>`

Human explanation of a generated command handle or canonical skill.

Expected output:

- what it does
- when to use it
- when not to use it
- canonical source path
- runtime projection path
- loaded references
- validation commands
- overlap/conflict notes
- example prompts

### `ask skills prove <skill-or-goal>`

Outcome proof workflow.

Expected output:

- baseline behavior
- improved behavior
- workout/eval/transcript evidence
- validation status
- remaining gaps

### `ask repo closeout --changed`

Agent-native closeout contract.

Expected output:

- changed canonical files
- generated surfaces needing sync
- focused validation commands
- pass/fail/blocker status
- whether commit is safe
- next recommended command

## Invariants / Safety Requirements

- Cleanup must be classification-first, never deletion-first.
- Unknown ownership is a policy failure, not a deletion instruction.
- Active skill source and active plugin source must not be removed by bloat
  cleanup.
- Deferred context must remain available through references and an index when it
  carries important decision history.
- Generated runtime surfaces must declare their source of truth.
- Runtime projection must be reproducible.
- Generated artifacts must not re-enter git after cleanup unless allowlisted as
  fixtures, summaries, or intentional archives.
- `ask` remains the stable public interface for humans and agents.
- JSON output must include enough detail for agents to take the next safe action.
- Any destructive cleanup requires a reference scan and validation evidence.
- Validation must report both file bloat and interaction bloat.

## Failure Model and Recovery

### Historical Artifacts Mistaken For Source

Failure: a cleanup pass deletes a historical artifact that a test, doc, or skill
still references.

Recovery:

- reference scan before deletion
- fixture allowlist
- report exact references
- keep summary/index files for archived evidence

### Generated State Masquerades As Canonical Source

Failure: agents edit `.agents/skills/**`, `.skillsets/**`, caches, or generated
manifests directly.

Recovery:

- path ownership policy
- sync/projection commands
- generated-file headers where appropriate
- validation failures for hand-edited generated surfaces

### Deferred Context Is Treated As Bloat

Failure: important context is removed because it is long or old.

Recovery:

- classify as `reference`
- index in deferred context surfaces
- keep out of default runtime loading
- add direct links from active specs or routing maps

### Product Work Adds More Surface Area

Failure: new commands and docs improve architecture but increase cognitive load.

Recovery:

- task-first command grouping
- `ask repo doctor` and `ask repo onboard` as front doors
- runtime budget and first-level surface reporting
- strict distinction between default and advanced surfaces

### Inventory Gate Blocks Legitimate Fixtures

Failure: the inventory script flags real fixtures or intentional archives.

Recovery:

- allowlist with required reason
- fixture path convention
- policy doc update
- test proving the fixture is used

## Observability

The system must report:

- counts by surface classification
- tracked generated artifact count
- historical artifact count and size estimate
- unknown path count
- allowlist count with reasons
- runtime budget counts
- first-level/default-visible counts
- advanced-visible counts
- broken active/archive/deferred references
- generated files changed by sync
- recommended next command

The JSON report must be stable enough for agents to parse without screen-scraping
human prose.

## Acceptance and Test Matrix

| ID   | Acceptance Criteria                                                                                                                                                                                               | Verification                                                                                              |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| SA1  | A repo surface ownership policy exists and defines source, fixture, policy, reference, intentional archive, vendored snapshot, generated output, runtime state, historical artifact, and unknown classifications. | `rg 'source|fixture|historical_artifact|runtime_state|unknown' Docs/agents/15-repo-surface-ownership.md` |
| SA2  | A surface inventory command reports tracked files by classification with JSON output.                                                                                                                             | `./bin/ask repo surface --json`                                                                           |
| SA3  | The inventory command flags tracked generated artifacts under `artifacts/**` and `Infrastructure/artifacts/**` unless they are allowlisted fixtures, summaries, or intentional archives.                          | Add a fixture test and run the inventory command in strict mode                                           |
| SA4  | The inventory command flags `Infrastructure/Infrastructure/**` unless explicitly allowlisted with a reason.                                                                                                       | Run inventory against the live tree and verify the nested path is reported or absent                      |
| SA5  | `.skillsets/**`, `.harness/*.db`, and `skills-system/**` have explicit ownership decisions before cleanup changes touch them.                                                                                     | Policy doc contains path rows and validation emits no `unknown` classification for those paths            |
| SA6  | Historical artifact cleanup preserves required fixtures and summaries while removing unreferenced run logs, JSONL event streams, timestamped validation output, and stale generated reports.                      | Reference scan passes; `git ls-files artifacts Infrastructure/artifacts` returns only allowlisted paths   |
| SA7  | Retired skill debris is cleaned only after active route, deferred context, and docs references are scanned.                                                                                                       | `rg` reference scan for retired skill names is attached to cleanup evidence                               |
| SA8  | Deferred context remains reachable through indexed references and is not loaded by default.                                                                                                                       | Deferred context index check passes; runtime budget does not count deferred bodies as first-level context |
| SA9  | `ask repo doctor` provides one human-readable health summary plus JSON-compatible status for repo, sync, runtime budget, handles, surface policy, blockers, and next command.                                     | `./bin/ask repo doctor --json`                                                                            |
| SA10 | `ask repo onboard` explains the current repo/runtime state and recommends the next useful action without requiring users to read architecture docs first.                                                         | Manual transcript or CLI test fixture for first-run output                                                |
| SA11 | `ask skills improve "<goal>"` maps a user goal to candidate capabilities, conflict/overlap notes, and validation or sync actions.                                                                                  | CLI fixture with at least one coding-agent improvement goal                                               |
| SA12 | `ask skills explain <handle>` distinguishes generated command handle, canonical skill source, runtime projection, loaded references, and validation commands.                                                     | CLI fixture for `he-spec` or another generated command handle                                             |
| SA13 | `ask repo closeout --changed` infers changed canonical files and reports focused validation, generated sync needs, blocker status, and commit readiness.                                                          | CLI fixture on a controlled changed-file set                                                              |
| SA14 | Runtime surface reporting remains part of closeout and reports default-visible, first-level, advanced-visible, and advisory-threshold status.                                                                     | `./bin/ask runtime budget --json --robot`                                                                 |
| SA15 | The cleanup and product improvements are presented as an agent capability control plane, not merely as a prompt or skill library.                                                                                 | README or start-here copy includes the product thesis and outcome framing                                 |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs                          | Planning handoff                                                                                                                                                                           |
| ------------ | --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| JSC-246      | SA1, SA2, SA3, SA4, SA5                 | First slice: repo surface ownership policy, non-destructive inventory gate, stable JSON output, `ask` route, tests, and live report.                                                       |
| JSC-246      | SA6, SA7, SA8                           | Follow-on cleanup: reference-scanned historical artifact removal, retired skill debris audit, and deferred context preservation.                                                           |
| JSC-246      | SA9, SA10, SA11, SA12, SA13, SA14, SA15 | Product golden paths: `ask repo doctor`, `ask repo onboard`, `ask skills improve`, `ask skills explain`, `ask skills prove`, `ask repo next --json`, `ask repo closeout --changed`, and outcome-oriented README/start-here framing. |

## Planning-Ready First Slice

The first slice should not delete files.

Implement only:

- repo surface ownership policy
- inventory script
- `ask` route for `repo surface` reporting
- JSON schema or stable JSON shape
- focused tests for classification
- live report against the current tree

First-slice success means the repository can answer:

- what is source
- what is generated
- what is runtime state
- what is archived evidence
- what is unknown
- what is violating policy
- what command should run next

Deletion, archive movement, and product golden-path commands should follow only
after that inventory is trusted.

## Open Questions

- Should `ask repo bloat` be added as a human-friendly alias for the selected
  `ask repo surface` command?
- Should `.skillsets/**` remain a tracked canonical generated snapshot or become
  reproducible ignored output?
- Is `.harness/context-compound.db` a runtime database, fixture, or accidental
  tracked state?
- Is `skills-system/**` a vendored snapshot, generated mirror, or stale legacy
  surface?
- Which historical artifact summaries are worth retaining as intentional
  archives?
- What is the minimum outcome proof format for `ask skills prove`?

## Definition of Done

- The repo has a documented surface ownership policy.
- The repo has an inventory gate reachable through `./bin/ask`.
- The inventory gate emits stable JSON and useful human output.
- Unknown and generated-tracked surfaces are visible in reports.
- Cleanup candidates are reference-scanned before deletion.
- Historical artifact retention is explicit and bounded.
- Generated/runtime ownership is explicit for `.skillsets/**`,
  `.harness/*.db`, `skills-system/**`, and `Plugins/cache/**`.
- Runtime surface bloat remains visible through budget reporting.
- Product golden paths are specified enough for `he-plan` to split into
  implementation units.
- No implementation slice relies on deleting context that should instead be
  preserved behind references.

## Handoff to `he-plan`

Recommended first plan unit:

```text
Add repo surface ownership policy plus a non-destructive inventory gate routed
through ./bin/ask, with tests and live JSON output against the current tree.
```

Recommended follow-on plan units:

```text
1. Remove tracked historical artifacts after reference scan and allowlist policy.
2. Audit retired skill debris and fix stale active/deferred references.
3. Resolve generated/runtime ownership for .skillsets, .harness databases, and skills-system.
4. Add task-first product commands: ask repo doctor, ask repo onboard, ask skills improve, ask skills explain, ask skills prove, ask repo closeout --changed.
5. Reframe the README around the agent capability control plane promise and outcome proof.
```
