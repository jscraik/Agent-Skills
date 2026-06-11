# Codex-Native Memory Baseline

Use this reference whenever Harness Engineering work creates, migrates, or validates repo-local memory, artifact, goal, decision, review, or sync surfaces.

## Required Greenfield Surfaces

A Codex-native harness baseline includes:

- `.harness/memory/LEARNINGS.md` for repo-scoped durable fixes.
- `.harness/knowledge/**` and `.harness/decisions/**` for Project Brain facts, hypotheses, rules, and accepted decisions.
- `.harness/review-log.md` for periodic review evidence.
- `.harness/active-artifacts.md` for active execution-input routing.
- `.harness/artifacts/README.md` for artifact policy.
- `.harness/artifacts/sync-receipts.jsonl` for sync receipts.
- `.harness/artifacts/brownfield-memory-inventory.md` when adopting an existing repository.
- `Docs/goals/README.md` plus `Docs/goals/<goal-slug>/goal.md`, `state.yaml`, and `receipts.jsonl` for long-running goal boards.

## Sync Receipt Shape

When a stage updates or observes memory surfaces, write or verify a JSONL receipt with `schema_version: harness-sync-receipt/v1` and separate these fields:

- `receipt_id`
- `timestamp`
- `runtime_action`
- `project_brain`
- `vault`
- `local_memory_cli`
- `local_memory_mcp`
- `chronicle`
- `native_citation`
- `artifact_state`
- `source_evidence`
- `redaction`
- `reason`

Allowed status classes are `updated`, `observed`, `not_applicable`, `deferred`, and `blocked`.
Never collapse these surfaces into a single generic success claim.

## Brownfield Rule

Before replacing existing memory, artifact, goal, review, or decision material, inventory each surface as one of:

- `canonical`
- `mirror`
- `legacy`
- `optional`
- `blocked`

Resolve canonical and blocked conflicts before replacement. For mirror, legacy, optional, and deferred surfaces, record the mapping or skip reason in the inventory and sync receipt.

## Evidence Boundary

Chronicle is observational only until corroborated by repo files, validation output, runtime artifacts, PR or tracker state, or explicit owner direction.
Native goal state is useful runtime context, but durable goal coordination belongs in the repo goal board and append-only receipts.
Vault, Local Memory CLI, and Local Memory MCP status must be reported separately because they can fail or be intentionally deferred independently.
