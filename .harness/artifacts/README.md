# Harness Artifacts

## Table of Contents

- [Sync Receipts](#sync-receipts)

Curated artifacts here are repo truth only when they are tracked, current, and tied to source evidence.
Runtime dumps, bulky traces, local databases, and unredacted transcripts stay out of the repository.

## Sync Receipts

Use `.harness/artifacts/sync-receipts.jsonl` when a task updates or observes multiple memory surfaces.
Each JSONL row must use `schema_version: harness-sync-receipt/v1` and separate these fields instead of collapsing them into one success claim:

- `schema_version`
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
Chronicle remains observational until corroborated by repo, runtime, PR, tracker, artifact, or owner evidence.
