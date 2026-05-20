---
schema_version: 1
artifact_type: sdk_apparatus_lens
status: implementation_ready
date: 2026-05-20
schema: Infrastructure/config/schemas/skill-doctor.v1.schema.json
---

# Skill SDK Apparatus Lens

## Purpose

This lens defines what counts as proof for the first Skill SDK readiness seam.
It keeps the SDK agent-native: schema, command output, fixtures, evals, and
validation evidence outrank prose review.

## RF-1 Signoff Table

| Claim | Required proof |
| --- | --- |
| Command exists | `./bin/ask skills --help` lists `doctor`, and `./bin/ask skills doctor context7 --json --robot` dispatches. |
| Guidance is truthful | Parser actions, help text, command metadata, and unknown-action suggestions expose the same `ask skills` action set; `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py::test_skills_action_metadata_matches_parser -q` passes. |
| Payload is stable | `data.skill_doctor` snapshots at `artifacts/skill-doctor/context7.after.json` and `artifacts/skill-doctor/<second-skill>.after.json` validate against `Infrastructure/config/schemas/skill-doctor.v1.schema.json` through `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py::test_skill_doctor_snapshots_validate_schema -q`. |
| Status is deterministic | Tests prove blocked outranks warning, warning outranks pass, and pass has no blockers or warnings. |
| Existing consumers are protected | `skills prove` and `skills proof` keep their current public semantics; doctor maps from them without replacing them. |
| Representative coverage exists | Fixtures cover `context7` and at least one additional non-`context7` skill class. |
| Package readiness is honest | Until package commands exist, doctor emits an explicit unavailable/not_implemented package readiness check instead of pass. |
| Eval learning is bounded | Eval outcomes can create classified deltas only with affected paths, rerun commands, before/after evidence, and promotion or rollback decision. |
| Rollback is safe | After RF-1 acceptance, ordinary rollback preserves the `skills doctor` command with degraded/blocking output; command removal requires an emergency waiver and reopens RF-1. |

## Required Status Vocabulary

- Readiness status: `pass`, `warning`, `blocked`.
- Check status: `pass`, `warning`, `blocked`, `fail`, `not_run`.
- Blocker class: `blocked_runtime`, `blocked_missing_source`,
  `permission_gap`, `package_metadata_gap`, `runtime_projection_gap`,
  `outcome_proof_missing`, `telemetry_projection_unavailable`,
  `command_surface_gap`, `schema_contract_gap`.
- Package readiness before package seams exist: `not_implemented` or
  `unavailable`, never `pass`.

## Review Rule

AI review reports are advisory evidence. RF-1 is ready to proceed only when the
signoff table is encoded into implementation tasks, validation commands, and
the eval artifact.
