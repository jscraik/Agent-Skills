---
title: ask (Agent Skills Kit) CLI Implementation Plan
status: draft
date: 2026-04-06
spec: docs/cli-specs/2026-04-06-ask-cli-spec.md
type: tool_delivery
plan_depth: standard
---

# ask (Agent Skills Kit) CLI Implementation Plan

## Table of Contents

- [Problem Statement](#problem-statement)
- [Implementation Strategy](#implementation-strategy)
- [Proposed Structure](#proposed-structure)
- [P0: Scaffolding and Core Envelope](#p0-scaffolding-and-core-envelope)
- [P1: Context and Repo Commands](#p1-context-and-repo-commands)
- [P2: Skill Lifecycle (Read-Only)](#p2-skill-lifecycle-read-only)
- [P3: Skill Operations (Mutations)](#p3-skill-operations-mutations)
- [Verification-First Strategy](#verification-first-strategy)
- [Rollout & Safety](#rollout--safety)
- [Task Graph (id and depends_on)](#task-graph-id-and-depends_on)
- [Definition of Done](#definition-of-done)

## Problem Statement
The `agent-skills` project needs a unified, agent-native CLI to replace the current fragmented set of shell and Python scripts. This plan sequences the creation of the `ask` CLI, following the technical contract defined in `docs/cli-specs/2026-04-06-ask-cli-spec.md`.

## Implementation Strategy
- **Language:** Python 3.12+ (matches repo standard).
- **Core Library:** `argparse` for command/flag handling.
- **Data Model:** `dataclasses` for the `CallResult` envelope.
- **Execution Model:** Wrapper-first. The CLI will primarily coordinate existing logic from `Infrastructure/scripts/` and `Skills/` to minimize code duplication.

## Proposed Structure
- `bin/ask`: Main entry point (shebang script).
- `Infrastructure/scripts/lib/ask/`: Core logic and data models.
  - `envelope.py`: `CallResult` and `ErrorRegistry` definitions.
  - `context.py`: `.git` discovery and root resolution.
  - `commands/`: Subcommand implementations.

## P0: Scaffolding and Core Envelope
Goal: Create the CLI entry point and ensure it returns valid JSON envelopes.

- [x] **P0.1: Entrypoint & Argparse Skeleton.** Create `bin/ask` with basic `<topic> <action>` routing.
- [x] **P0.2: CallResult Implementation.** Implement the standard response envelope in `Infrastructure/scripts/lib/ask/envelope.py`.
- [x] **P0.3: JSON/TUI Dispatcher.** Logic to toggle between human-readable logs and deterministic JSON based on `--json`.
- [x] **AC1:** `ask --json` returns a valid `CallResult` with `SUCCESS`. (Traceable to spec CA1).

## P1: Context and Repo Commands
Goal: Implement context discovery and repository-level health checks.

- [x] **P1.1: Git Root Discovery.** Implement the `.git` search logic in `Infrastructure/scripts/lib/ask/context.py`.
- [x] **P1.2: `repo status`.** Port logic from `Infrastructure/scripts/lifecycle-and-sync/status.sh` to the new CLI.
- [ ] **P1.3: `repo validate`.** Wrap `Infrastructure/scripts/validate_all.sh` with structured JSON error reporting.
- [x] **AC2:** `ask repo status` correctly identifies `<REPO_ROOT>`. (Traceable to spec CA1).

## P2: Skill Lifecycle (Read-Only)
Goal: Implement listing and auditing skills with high-fidelity output.

- [x] **P2.1: `skills list`.** Wrap `Infrastructure/scripts/lifecycle-and-sync/skill_catalog.py` to support category filtering and JSON output.
- [ ] **P2.2: `skills audit`.** Integrate `skill_gate.py` and `diagnose_skill.py`.
- [ ] **P2.3: Type-Safe Signatures.** Ensure `ask --help` and `ask <cmd> --help` display the TS-style signatures from the spec.
- [ ] **AC3:** `ask skills audit <path>` returns `ERR_PI_GUARD` string code on security failure. (Traceable to spec CA4).

## P3: Skill Operations (Mutations)
Goal: Implement state-changing operations with dry-run and atomic promotion.

- [x] **P3.1: `skills sync`.** Port `sync_skills.sh` logic with mandatory `--dry-run` support. (Planning phase complete).
- [ ] **P3.2: `skills install`.** Port the hardened `install-skill-from-github.py` logic, ensuring atomic promotion.
- [ ] **P3.3: `skills fold`.** Implement the semantic redundancy check (0.2 threshold).
- [x] **AC4:** `ask skills install --dry-run` returns a `plan` object in JSON mode. (Traceable to spec CA2).

## Verification-First Strategy

| Layer | Tool | Requirement |
| :--- | :--- | :--- |
| **Unit** | `unittest` | Validate `CallResult` serialization and redaction logic. |
| **Contract** | `Infrastructure/scripts/validation-and-linting/verify_ask_cli.py` | Verify every command returns schema-valid JSON. |
| **E2E** | `bats` or `pytest` | Run the `CA1` through `CA6` scenarios defined in the spec. |

## Rollout & Safety
- **Adherence:** All mutations must use the `QUARANTINE` -> `ATOMIC PROMOTION` state model.
- **Rollback:** `SIGINT` handler must trigger immediate cleanup of temporary directories.
- **Sanitization:** Centralized `redact()` function applied to all `CallResult` outputs.

## Task Graph (id and depends_on)

```yaml
tasks:
  - id: P0
    title: Scaffold the ask entrypoint and enforce CallResult envelope semantics.
    depends_on: []
  - id: P1
    title: Implement repo context resolution plus repo status and validation commands.
    depends_on: [P0]
  - id: P2
    title: Deliver read-only skill lifecycle surfaces with structured audit output.
    depends_on: [P0, P1]
  - id: P3
    title: Add mutation workflows with dry-run, quarantine, and atomic promotion guarantees.
    depends_on: [P1, P2]
  - id: V1
    title: Run contract, unit, and end-to-end verification gates for CA1 through CA6.
    depends_on: [P3]
```

## Definition of Done
- [ ] `bin/ask` is in the user's path and executable.
- [ ] Every command in the Hierarchy is implemented.
- [ ] Automated CI tests pass for all `AC` items.
- [ ] `ask --help` is complete and TS-aligned.
