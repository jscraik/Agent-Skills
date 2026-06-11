# PU-016: Skills SDK Review Artifact Verification Spec

## Metadata

- schema_version: 1
- stage: sy-spec
- status: implemented
- date: 2026-06-08
- branch: codex/skills-sdk-pu-016-review-verify
- target: Skills SDK review verification surface
- source_slice: PU-015 review handoff receipts
- owner surfaces:
  - Infrastructure/scripts/lib/ask/commands/sdk.py
  - Infrastructure/scripts/lib/ask/skills_sdk/review_verify.py
  - Infrastructure/config/schemas/skills-sdk/sdk-review-verification-receipt.v1.schema.json
  - Infrastructure/tests/test_skills_sdk_review_verify.py
  - Infrastructure/config/skills-sdk/capability-matrix.v1.json
  - artifacts/recommended-skills-sdk-pipeline.html

## Approved Intent

PU-015 creates a `review_handoff` receipt that names reviewer roles, required local artifacts, evidence boundaries, and not-proven lanes. PU-016 must consume that handoff receipt and verify the local required artifacts without running reviewers or claiming external readiness.

The verification receipt proves only that the required local artifact files listed by the handoff receipt are present, repo-contained, non-empty, and digestable. It must preserve the distinction between local artifact verification and review completion. It must not claim CI, CodeRabbit, GitHub review-thread state, tracker state, PR mergeability, or external service readiness.

## Requirements

### R1: Consume Review Handoff Receipts

Given a `sdk-review-handoff-receipt.v1` JSON file, when the operator runs:

```bash
./bin/ask sdk review verify --handoff <handoff-receipt> --json --robot
```

then the SDK must parse and validate the handoff receipt before inspecting artifact paths.

### R2: Verify Required Local Artifacts

The command must use `required_artifacts` from the handoff receipt as the source of truth. Each required artifact path must resolve inside the repository root. A verified artifact must exist, be a regular file, be non-empty, and produce a SHA-256 digest.

### R3: Emit Schema-Backed Verification Receipts

The receipt must include the source handoff path and digest, target identity, reviewer roles, required artifacts, per-artifact status, missing or invalid artifact paths, evidence boundaries, not-proven lanes, next commands, and mutation metadata.

### R4: Keep External Lanes Unproven

The verification receipt must keep CI, PR mergeability, review-thread state, tracker state, and external service state unproven. Local artifact verification must not become a proxy for reviewer execution or merge readiness.

### R5: Keep Default Read-Only

The command must not write files unless `--receipt-out` is supplied. Optional receipt output paths must resolve inside the repository root.

## Acceptance Criteria

1. Given a valid review handoff receipt and all required artifacts present, `sdk review verify` emits `data.review_verification.status=pass`.
2. Given missing required artifacts, the command emits a structured verification receipt with `status=fail` and `review_artifacts_verified=false`.
3. Given a required artifact path escaping the repository root, the builder fails closed.
4. Given `--receipt-out`, the command writes a schema-valid verification receipt inside the repository.
5. Given `ask sdk status --json --robot`, `review_verification` appears as implemented, feature-executed, and non-mutating.

## Non-Goals

- Do not run review agents or review swarms.
- Do not claim review completion.
- Do not inspect GitHub review threads, CircleCI, CodeRabbit, PR checks, tracker state, or mergeability.
- Do not mutate target source files.
- Do not add external service calls.
