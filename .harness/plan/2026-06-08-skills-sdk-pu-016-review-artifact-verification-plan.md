# PU-016: Skills SDK Review Artifact Verification Plan

## Metadata

- schema_version: 1
- stage: sy-trace-plan
- status: implemented
- date: 2026-06-08
- source_spec: .harness/specs/2026-06-08-skills-sdk-pu-016-review-artifact-verification-spec.md
- branch: codex/skills-sdk-pu-016-review-verify
- target: Skills SDK review verification surface

## Decision

Add a local, read-only review artifact verification slice after PU-015. The slice consumes a verified review handoff receipt and emits a schema-backed verification receipt that checks the required local artifact files. It must not execute reviewers or infer external readiness from local files.

## Traceability

- R1 consume review handoff receipts: implemented in `commands/sdk.py` and `review_verify.py`.
- R2 verify required artifacts: implemented by repo-contained path checks plus non-empty file and digest checks.
- R3 emit verification receipts: implemented by `sdk-review-verification-receipt.v1.schema.json` and focused schema tests.
- R4 keep external lanes unproven: implemented by preserving PR, CI, review-thread, tracker, and external service boundaries.
- R5 keep default read-only: implemented by optional `--receipt-out` only.
- R6 update capability truth: implemented by capability matrix and HTML pipeline rows.

## Validation Commands

```bash
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_verify.py -q
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q
./bin/ask sdk status --json --robot
```

## Evidence Boundary

A passing PU-016 receipt proves local artifact presence, containment, non-empty content, and digestability only. It does not prove reviewer execution quality, GitHub review-thread state, CI state, CodeRabbit state, tracker state, PR mergeability, or release readiness.
