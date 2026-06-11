# PU-017: Skills SDK Governed Review Execution Spec

## Metadata

- schema_version: 1
- stage: sy-spec
- status: implemented
- date: 2026-06-11
- branch: main
- target: Skills SDK governed local review execution surface
- source_slice: PU-016 review artifact verification receipts
- owner surfaces:
  - Infrastructure/scripts/lib/ask/commands/sdk.py
  - Infrastructure/scripts/lib/ask/skills_sdk/review_execute.py
  - Infrastructure/config/schemas/skills-sdk/sdk-review-execution-receipt.v1.schema.json
  - Infrastructure/tests/test_skills_sdk_review_execute.py
  - Infrastructure/config/skills-sdk/capability-matrix.v1.json

## Approved Intent

PU-015 creates a review handoff receipt that names reviewer roles and required
local artifacts. PU-016 verifies those required artifacts after they exist.
PU-017 fills the bounded gap between those two surfaces by materializing the
required local review artifact packet from the handoff receipt.

The execution receipt proves only that the SDK-local executor wrote or
preserved the required repo-contained artifacts declared by the handoff. It
does not prove independent reviewer approval, substantive human review, CI,
CodeRabbit, GitHub review-thread state, tracker state, PR mergeability, hosted
explorer readiness, or external service state.

## Requirements

### R1: Consume Review Handoff Receipts

Given a `sdk-review-handoff-receipt.v1` JSON file, when the operator runs
`./bin/ask sdk review execute --handoff <handoff-receipt> --json --robot`,
then the SDK must parse and validate the handoff receipt before writing any
artifact path.

### R2: Write Only Required Repo-Contained Artifacts

The command must use `required_artifacts` from the handoff receipt as the
source of truth. Each required artifact path must resolve inside the repository
root. The command may create parent directories for those paths, write missing
or empty artifact files, and preserve existing non-empty files. It must not
write paths outside the repository root.

### R3: Emit Schema-Backed Execution Receipts

The receipt must include the source handoff path and digest, target identity,
reviewer roles, required artifacts, execution mode, runner metadata, per
artifact write status, failed artifact paths, evidence boundaries, not-proven
lanes, next commands, and mutation metadata.

### R4: Preserve Evidence Boundaries

The execution receipt must keep independent reviewer approval, substantive
human review, CI, PR mergeability, review-thread state, tracker state, and
external service state unproven.

### R5: Keep Execution Local

The command must not invoke external services, hosted review systems, CI, PR
APIs, or tracker APIs. It is a local artifact materialization step that prepares
the existing PU-016 verification surface.

## Acceptance Criteria

1. Given a valid review handoff receipt, `sdk review execute` emits
   `data.review_execution.status=pass` and writes every required artifact.
2. Given existing non-empty required artifacts, the command preserves them
   instead of overwriting them.
3. Given a required artifact path escaping the repository root, the command
   fails closed.
4. Given `--receipt-out`, the command writes a schema-valid execution receipt
   inside the repository.
5. Given `ask sdk status --json --robot`, `review_execution` appears as
   implemented, feature-executed, and bounded-mutating.

## Non-Goals

- Do not run external review agents or review swarms.
- Do not claim independent reviewer approval.
- Do not inspect GitHub review threads, CircleCI, CodeRabbit, PR checks,
  tracker state, or mergeability.
- Do not publish, host, or update the HTML explorer.
- Do not mutate target source files.
- Do not add external service calls.
