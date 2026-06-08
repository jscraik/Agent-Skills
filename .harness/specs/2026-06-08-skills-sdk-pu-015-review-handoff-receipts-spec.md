# PU-015: Skills SDK Review Handoff Receipts Spec

## Metadata

- schema_version: 1
- stage: sy-spec
- status: implemented
- date: 2026-06-08
- branch: codex/skills-sdk-pu-015-review-handoff
- worktree: /private/tmp/agent-skills-pu-015-review-handoff
- target: Skills SDK review handoff surface
- source_slice: PU-014 lens-routed review plan receipts
- owner surfaces:
  - Infrastructure/scripts/lib/ask/commands/sdk.py
  - Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py
  - Infrastructure/scripts/lib/ask/skills_sdk/review_handoff.py
  - Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json
  - Infrastructure/config/schemas/skills-sdk/sdk-review-handoff-receipt.v1.schema.json
  - Infrastructure/tests/test_skills_sdk_review_handoff.py
  - Infrastructure/config/skills-sdk/capability-matrix.v1.json
  - artifacts/recommended-skills-sdk-pipeline.html

## Approved Intent

PU-014 made `sdk review plan` a deterministic, read-only advisory receipt. PU-015 should consume those review-plan receipts and produce a bounded review handoff receipt that is safe to give to a human reviewer, a Codex reviewer, or a later governed review lane.

The handoff receipt must preserve the distinction between planning a review and completing a review. It must validate input receipt shape, source provenance, freshness, explicit caller target and intent, selected lens evidence, reviewer roles, required artifacts, and next commands. It must not claim CodeRabbit status, Codex review completion, GitHub review-thread state, CI state, mergeability, or external service readiness.

## User Outcome

A maintainer can convert a proven `review_plan` receipt into a stable handoff packet that says who or what should review, what evidence they must produce, where that evidence belongs, and which boundaries are still unproven.

## Current Evidence Checked

- The PU-015 worktree was rebased onto `origin/main` at commit `2a4e5d809f5d079136b3dbd2fc91b89d8467247d` before implementation.
- `artifacts/recommended-skills-sdk-pipeline.html` marks the PU-015 sync point: consume `review_plan` receipts, validate freshness and mismatch boundaries, record reviewer roles and required artifacts, and avoid claiming review completion.
- `Infrastructure/config/skills-sdk/capability-matrix.v1.json` marks `review_plan` as implemented and says the next slice is handoff without treating the receipt as review completion.
- PU-014 spec and trace plan define the input receipt contract and explicitly exclude running reviewers, CI, external services, or mergeability checks.

## Requirements

### R1: Consume Review Plan Receipts

Given a `sdk-review-plan-receipt.v1` JSON file, when the operator runs:

```bash
./bin/ask sdk review handoff --plan <receipt-path> --target <path-or-handle> --intent <intent> --json --robot
```

then the SDK must parse and validate the receipt before producing any handoff output. `--target` and `--intent` are required first-class handoff inputs; mismatch detection must not depend on optional caller context.

### R1A: Require Source Receipt Provenance

PU-015 must extend the review-plan receipt contract so every new review-plan receipt contains a `source_context` object with enough immutable local provenance to reject copied or stale receipts:

- `repo_root`: the resolved repository root used when the review-plan receipt was created.
- `head_sha`: the Git HEAD SHA used when the review-plan receipt was created.
- `branch`: the current branch name or detached-head marker.
- `branch_policy`: the policy used by handoff, initially `same_head_required`; branch name is diagnostic, while HEAD SHA is the authoritative freshness check.
- `receipt_instance_id`: a generated stable identifier for this written review-plan receipt instance.
- `target_input`: the exact target argument supplied to `sdk review plan`.
- `target_identity`: canonical identity for the target. Path-backed targets use the resolved path. Handle-backed targets must be resolved through the same SDK target resolver into a canonical source path before handoff is allowed.
- `target_kind`: the review-plan target kind after resolution.
- `target_resolved_path`: the resolved target path when `target_kind` is path-backed.
- `target_content_digest`: digest of the target file or a deterministic directory digest when practical.
- `target_digest_status`: `available`, `unsupported_directory`, or `not_applicable_unresolved_handle`.
- `provenance_risk_flags`: non-empty when digesting or handle resolution is incomplete.
- `receipt_created_at`: an RFC 3339 timestamp for diagnostic freshness only; timestamp alone must not prove freshness.

Handle-backed targets are allowed only when the active resolver maps the handle to a canonical source path and the receipt records that resolved identity. Unresolved handles are allowed in PU-014 review plans but are not eligible for PU-015 handoff; handoff must fail closed with no receipt write.

Directory targets are eligible only when the implementation defines a deterministic directory digest. If directory digesting is unsupported, `target_digest_status` must be `unsupported_directory`, `provenance_risk_flags` must explain the unsupported state, and handoff must fail closed. The handoff receipt schema must include `source_context.provenance_risk_flags` so this state is not represented by ad hoc text.

The handoff command must refuse source review-plan receipts that lack `source_context`, whose `repo_root` does not resolve to the active repository root, whose `head_sha` differs from current HEAD, whose target identity does not resolve to the caller-supplied `--target`, whose target digest no longer matches, whose digest status is not `available`, or whose provenance risk flags are non-empty.

### R1B: Require Independent Receipt Trace Integrity

The source review-plan receipt body is mutable JSON, so provenance must not be trusted only because it appears in the receipt. When `sdk review plan --receipt-out <path>` writes a receipt, it must also write a paired trace sidecar under a repo-local trace directory, recommended:

```text
.harness/artifacts/sdk-review-plan/traces/<receipt-sha256>.trace.json
```

The trace sidecar must include:

- `schema_version: skills-sdk.review-plan-trace.v1`
- `receipt_path`
- `receipt_instance_id`
- `receipt_sha256`
- `repo_root`
- `head_sha`
- `branch_policy`
- `target_identity`
- `target_content_digest`
- `created_by_command`

The handoff command must recompute the canonical source receipt digest, load the matching trace sidecar, and compare the trace fields to the receipt, the caller-supplied plan path, and current repository state before building a handoff. The resolved `--plan` path must match the trace sidecar's resolved `receipt_path`, and `receipt_instance_id` must match between receipt and sidecar. A copied or edited receipt without a matching repo-local trace sidecar, matching original receipt path, and matching instance id must fail closed. The sidecar is an integrity guard against accidental copied or hand-edited receipts, not a cryptographic trust or anti-malicious-tamper claim.

### R2: Refuse Stale Or Mismatched Inputs

The command must refuse handoff creation when:

- the input receipt schema version is unsupported;
- the receipt target no longer exists when the target kind requires a repo path;
- the required caller `--target` or `--intent` conflicts with the receipt target or intent;
- selected lenses are missing;
- the receipt claims mutation or an unsafe output path;
- the receipt lacks provenance or was produced outside the current repository root;
- the receipt HEAD SHA, branch policy, resolved target path, or target digest is stale or mismatched.
- the receipt digest, resolved plan path, or receipt instance id does not match its repo-local trace sidecar, or no matching trace sidecar exists.

### R3: Emit Review Handoff Fields

The handoff receipt must include:

- `schema_version`
- `schema_uri`
- `status`
- `source_review_plan`
- `source_context`
- `source_trace`
- `target`
- `target_kind`
- `task_intent`
- `selected_lenses`
- `reviewer_roles`
- `required_artifacts`
- `evidence_boundaries`
- `next_commands`
- `not_proven`
- `mutation_performed: false`
- `receipt_written`
- `receipt_path`

### R4: Keep Handoff Read-Only By Default

The default path must not write files. It may write the handoff receipt only when an explicit repo-root-local output path is supplied. Output containment must be enforced after symlink resolution, not by string prefix checks:

- resolve the repository root;
- resolve the requested output parent directory and reject missing parents unless the implementation explicitly creates repo-local parents;
- if the output path already exists, resolve the existing path and reject symlinks that point outside the repository;
- reject any resolved parent or existing file outside the resolved repository root;
- test a repo-local symlink that points outside the checkout and prove the write is refused.

### R5: Keep Review Execution Out Of Scope

PU-015 must not run review agents, CodeRabbit, GitHub, CircleCI, external services, or mergeability checks. It can prepare reviewer instructions and artifact contracts only.

This boundary must be tested with explicit guards. The builder tests must monkeypatch or otherwise trap subprocess and network entry points used elsewhere in the SDK command layer and assert the handoff builder does not call them. The implementation must keep any command-smoke invocation separate from the pure builder path so local-only proof remains deterministic.

### R6: Schema-Backed Public Contract

Add `Infrastructure/config/schemas/skills-sdk/sdk-review-handoff-receipt.v1.schema.json` and validate emitted handoff receipts against it in tests.

### R7: Capability Truth Update

Update `ask sdk status` and `artifacts/recommended-skills-sdk-pipeline.html` with a new capability row, recommended id:

`review_handoff`

The row must make clear that the surface creates handoff receipts, not review completion proof.

### R8: Deterministic Tests

Add focused tests that prove:

- valid PU-014 review-plan receipts produce schema-valid handoff receipts;
- review-plan receipts without `source_context` fail closed;
- review-plan receipts without a matching repo-local trace sidecar fail closed;
- edited review-plan receipts whose canonical digest differs from the sidecar fail closed;
- byte-identical copied review-plan receipts at a different path fail closed because the resolved plan path no longer matches the sidecar;
- trace sidecars whose `receipt_instance_id` differs from the receipt fail closed;
- copied review-plan receipts from another repo root, branch/HEAD, target path, or target digest fail closed;
- unresolved handle-backed receipts fail closed; resolved handles must compare against canonical source path provenance;
- unsupported directory digests fail closed with `provenance_risk_flags`;
- invalid schema, stale target, target mismatch, intent mismatch, missing lenses, and unsafe output paths fail;
- default command path is non-mutating;
- explicit repo-root-local receipt writes are allowed;
- symlinked repo-local output paths resolving outside the checkout fail;
- selected lens ids, reviewer roles, required artifacts, and next commands are stable;
- status and pipeline artifacts include `review_handoff`;
- no subprocess, network, or external review service is called by the builder.

## Non-Goals

- Do not run reviewers or review swarms.
- Do not claim review completion.
- Do not inspect GitHub review threads, CircleCI, CodeRabbit, PR checks, or mergeability.
- Do not mutate target source files.
- Do not add external service calls.
- Do not change PU-014 lens selection or review-plan scoring.

## Affected Surface Map

| Surface | Disposition | Notes |
| --- | --- | --- |
| `Infrastructure/scripts/lib/ask/commands/sdk.py` | change | Add `sdk review handoff` parser and dispatcher. |
| `Infrastructure/scripts/lib/ask/skills_sdk/review_handoff.py` | add | New read-only handoff receipt builder. |
| `Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py` | change | Emit `source_context`, `receipt_instance_id`, and paired trace sidecars for explicit receipt writes. |
| `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json` | change | Add required `source_context` provenance for new receipts. |
| `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-trace.v1.schema.json` | add | Public schema for paired review-plan trace sidecars. |
| `Infrastructure/config/schemas/skills-sdk/sdk-review-handoff-receipt.v1.schema.json` | add | Public handoff receipt schema. |
| `Infrastructure/config/skills-sdk/capability-matrix.v1.json` | change | Add `review_handoff` implemented row after implementation. |
| `Infrastructure/tests/test_skills_sdk_review_handoff.py` | add | Focused command/schema/negative-path tests. |
| `Infrastructure/tests/test_skills_sdk_capability_status.py` | change | Assert required capability row. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | change | Assert HTML parity. |
| `artifacts/recommended-skills-sdk-pipeline.html` | change | Visual truth update. |
| GitHub/CircleCI/CodeRabbit | out_of_scope | Separate PR green-sweep lane only. |

## Acceptance Criteria

1. Given a valid review-plan receipt with matching `source_context`, when `ask sdk review handoff --plan <path> --target <same-target> --intent <same-intent> --json --robot` runs, then parsed robot JSON contains `data.review_handoff.status=pass` and `mutation_performed=false`.
2. Given identical inputs, when the command runs twice, then selected lens ids, reviewer roles, required artifact paths, and next commands are stable.
3. Given no receipt output path, when the command runs, then no file is written and `receipt_written=false`.
4. Given a repo-root-local output path, when the command runs, then the handoff receipt is written and validates against `sdk-review-handoff-receipt.v1.schema.json`.
5. Given stale, mismatched, copied, edited-without-trace-match, provenance-missing, unsupported, unresolved-handle, unsupported-directory, symlink-escaping, or unsafe inputs, when the command runs, then it returns an error envelope and writes no receipt.
6. Given `ask sdk status --json --robot`, when implementation is complete, then `review_handoff` appears as implemented, feature-executed, and non-mutating.
7. Given the pipeline artifact tests, when they run, then the HTML and capability matrix agree on `review_handoff`.

## Validation Commands

Focused implementation validation:

```bash
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_handoff.py -q
uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q
./bin/ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --receipt-out .harness/artifacts/sdk-review-plan/pu015-input.json --json --robot
./bin/ask sdk review handoff --plan .harness/artifacts/sdk-review-plan/pu015-input.json --target Skills/agent-ops/simplify --intent validation_review --json --robot
./bin/ask sdk review handoff --plan .harness/artifacts/sdk-review-plan/pu015-input.json --target Skills/agent-ops/simplify --intent validation_review --receipt-out .harness/artifacts/sdk-review-handoff/pu015-output.json --json --robot
./bin/ask sdk status --json --robot
bash scripts/validate-codestyle.sh --fast
```

Closeout validation, separate lane:

```bash
./bin/ask repo validate --json --robot
```

PR/CI/review state must be checked only after a PR exists.

## Evidence Limits

- Local tests prove only local SDK command behavior and schema contracts.
- A handoff receipt proves review instructions and artifact requirements, not review completion.
- Local validation does not prove GitHub CI, CircleCI, CodeRabbit, review-thread state, mergeability, or external service readiness.

## Risks

- Handoff wording could blur the boundary between requested review and completed review.
- Receipt writes could escape the repository if path checks are incomplete.
- Capability truth drift can recur if HTML, matrix, and status tests are not updated together.

## Rollback

Revert the PU-015 commit. This removes the handoff command, schema, tests, status row, and artifact update without affecting PU-014 review-plan receipts.

## Blocked Inputs

None for this draft spec. Implementation should stop if the PU-014 review-plan receipt contract changes or if full-repo projection drift reappears and cannot be synced with the repo-prescribed command.
