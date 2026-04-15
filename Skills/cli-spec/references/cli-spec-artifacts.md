# CLI Specification Artifacts

## Table of Contents

- [1. Artifact Path & Naming](#1-artifact-path--naming)
- [2. Mandatory Frontmatter](#2-mandatory-frontmatter)
- [3. Required Sections (Full Depth)](#3-required-sections-full-depth)
  - [Strategic Alignment](#strategic-alignment)
  - [Command Hierarchy](#command-hierarchy)
  - [Interface Contract](#interface-contract)
  - [Operation Lifecycle](#operation-lifecycle)
  - [Security & Safety](#security--safety)
  - [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [4. Acceptance Criteria Rubric](#4-acceptance-criteria-rubric)

Every specification produced by the `cli-spec` skill must adhere to the **Implementation-Grade** standard. This ensures that the spec is a binding technical contract that a developer or agent can implement without ambiguity.

## 1. Artifact Path & Naming
Specs must be saved in the `docs/cli-specs/` directory using the following format:
`docs/cli-specs/YYYY-MM-DD-<tool-name>-cli-spec.md`

## 2. Mandatory Frontmatter
```yaml
---
title: <Tool Name> CLI Specification
status: draft | active | deprecated
date: YYYY-MM-DD
spec_depth: lite | full
agent_compatible: true
schema_version: 1
---
```

## 3. Required Sections (Full Depth)

### Strategic Alignment
- **Problem Statement:** What gap does this tool fill?
- **Audience:** Human-first, Agent-first, or Dual-mode.
- **Gold Standard Goal:** Which 2026 industry patterns are being prioritized?

### Command Hierarchy
- **Visual Tree:** A mermaid diagram or indented list of `topic action`.
- **Primary Nouns/Verbs:** Statement on naming consistency.

### Interface Contract
- **Type-Safe Signatures:** TypeScript-style help signatures for every command.
- **JSON Schema:** The machine-readable contract for `CallResult`.
- **Signal Handling:** Behavior for `SIGINT`, `SIGTERM`.

### Operation Lifecycle
- **Input Flow:** Args -> Env -> Config File.
- **Mutation Planning:** Detailed `--dry-run` behavior and "Plan" object schema.
- **Coercion Rules:** Explicit rules for type guessing (e.g., `--raw-strings`).

### Security & Safety
- **Adversarial Validation:** Gating against shell injection and path traversal.
- **Redaction Policy:** How sensitive data is handled in logs/outputs.
- **Confirmation Gates:** Conditions requiring `--yes` or `--force`.

### Acceptance and Test Matrix
Every item must have a stable **`CA`** (CLI Acceptance) ID.
- `CA1`: [Description] -> [Expected Command] -> [Expected Output]
- `CA2`: [Error Case] -> [Trigger Command] -> [Exit Code & JSON Error]

## 4. Acceptance Criteria Rubric
- [ ] Spec answers "What happens when I run this in a non-TTY?"
- [ ] Every mutation has a dry-run plan.
- [ ] JSON schemas are provided for all success/failure envelopes.
- [ ] No absolute local paths are used in examples.
- [ ] `CA` IDs are stable and sequential.
