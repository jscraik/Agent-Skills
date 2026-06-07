# PU-014: Skills SDK Lens-Routed Review Receipts Trace Plan

## Metadata

- schema_version: 1
- stage: sy-trace-plan
- status: implemented_pending_pr
- date: 2026-06-07
- source_spec: .harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md
- branch: codex/skills-sdk-pu-014-lens-routed-review
- worktree: /private/tmp/agent-skills-skills-sdk-pu-014-lens-routed-review
- target: Skills SDK review planning surface

## Decision

Implement and harden a read-only `ask sdk review plan` command that turns existing deterministic SDK lens selection into a schema-backed review route receipt. In the current PU-014 worktree, the route, schema, status row, and HTML row exist; the remaining trace contract is to keep those surfaces aligned, parsed-envelope-proven, repo-root-bounded for receipt writes, and clearly advisory. The receipt recommends review focus, checks, evidence, risk flags, and next commands without running reviewers, CI, external services, or mutation.

## Evidence Checked

- PU-014 spec exists at `.harness/specs/2026-06-07-skills-sdk-pu-014-lens-routed-review-spec.md`.
- `Infrastructure/scripts/lib/ask/commands/sdk.py` has `sdk review plan` parser and dispatcher in the PU-014 worktree.
- `Infrastructure/scripts/lib/ask/skills_sdk/lenses.py` exposes `select_lenses(...)` with deterministic selected lens ids, scores, paths, and reasons.
- `Infrastructure/tests/test_skills_sdk_lenses.py` proves current lens selector behavior and CLI envelopes.
- `Infrastructure/tests/test_skills_sdk_review_plan.py` proves parsed robot envelopes, schema validity, stable handoff commands, repo-file propagation, local-only builder behavior, target-path refusal, and catalog-failure error envelopes.
- Public SDK schemas live under `Infrastructure/config/schemas/skills-sdk/`.
- Current SDK capability truth has `sdk_lenses`, `review_plan`, and `determinism_audit` as implemented in the PU-014 worktree.

## Traceability Map

| ID | Source Requirement | Expected Behavior | Owner Files | Artifact / Receipt | Validation | Closeout Proof | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Provide read-only review plan command | `./bin/ask sdk review plan --target <target> --intent <intent> --json --robot` emits parsed robot JSON with `data.review_plan` | `Infrastructure/scripts/lib/ask/commands/sdk.py`, `Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py` | Robot JSON envelope | `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_plan.py -q` | Parsed CLI output has `status=success`, contains `data.review_plan`, validates `data.review_plan` against `sdk-review-plan-receipt.v1.schema.json`, and asserts `mutation_performed=false` plus selected lens evidence | covered_by_work |
| R2 | Use existing lens selection | Review plan calls `select_lenses`, preserves selected lens ids, paths, scores, reasons, and propagates `--repo-file` signals | `review_plan.py`, `lenses.py` read-only | `selected_lenses` in review receipt | Unit tests compare selector output and patch selector to capture `repo_files` | Same input selects stable lens ids and same `next_commands` | covered_by_work |
| R3 | Emit review route fields | Receipt includes schema_version, schema_uri, target, target_kind, task_intent, review_focus, checks, evidence, risk flags, next commands, mutation metadata | `review_plan.py`, schema | `sdk-review-plan-receipt.v1` | Schema validation test | Public schema requires all receipt fields | covered_by_work |
| R4 | Default path non-mutating | No file writes unless `--receipt-out` is supplied | `review_plan.py`, command dispatcher | `receipt_written=false` by default | Temp dir test for no output file | Default CLI smoke reports no write | covered_by_work |
| R5 | Refuse ambiguous or unsafe inputs | Invalid max lenses, bad intent, typoed repo paths, unsafe receipt paths, and catalog failures return error envelopes | `commands/sdk.py`, `review_plan.py` | Error envelope | Negative tests | Error status plus no receipt file | covered_by_work |
| R6 | Schema-backed public contract | Add JSON Schema and validate receipts against it for every known lens task intent | `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json` | Public schema | Schema helper in tests | Every accepted CLI intent emits schema-valid receipt | covered_by_work |
| R7 | Capability truth update | `ask sdk status` contains `review_plan` implemented read-only capability | `capability-matrix.v1.json`, `capability_status.py` | Capability status row | Status tests | `ask sdk status --json --robot` row shows implemented, `feature_executed=true`, non-mutating | covered_by_work |
| R8 | Pipeline artifact update | Pipeline HTML shows `review_plan` as implemented advisory/read-only | `artifacts/recommended-skills-sdk-pipeline.html`, artifact tests | HTML artifact | `test_skills_sdk_pipeline_status_artifact.py` | HTML row exists and matches status | covered_by_work |
| NG1 | Do not run reviewers or external services | Command recommends review routes only and uses local inputs | `review_plan.py` | Receipt text and no service calls | Test guards subprocess and network helpers during builder execution | PR body states review completion is out of scope | covered_by_work |
| NG2 | Do not promote determinism candidates | Determinism audit remains advisory and unchanged | `determinism.py` out of scope | n.a. | No tests changed for candidate promotion except existing regression lane | No determinism behavior change | out_of_scope |

## Implemented Tasks

1. Add `Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py`.
   - Build `build_review_plan(...)`.
   - Resolve `target_kind` as `repo_path`, `skill_source`, or `unresolved_handle`.
   - Reject path-like targets that are missing or resolve outside the repository instead of treating typoed paths as handles.
   - Reuse `select_lenses`.
   - Build deterministic review focus, recommended checks, evidence, risk flags, and next commands from target kind, task intent, and selected lenses.
   - Support optional explicit repo-root-local receipt write.

2. Add `sdk review plan` parser and dispatcher.
   - New nested `review` parser under `sdk`.
   - New `plan` action under `review`.
   - Validate mutually safe arguments and return robot envelopes.
   - Keep the accepted intent set aligned with the public receipt schema.

3. Add public schema.
   - `Infrastructure/config/schemas/skills-sdk/sdk-review-plan-receipt.v1.schema.json`.
   - Require all public fields and constrain status, target_kind, task intent, mutation flag, receipt flags.

4. Add focused tests.
   - New `Infrastructure/tests/test_skills_sdk_review_plan.py`.
   - Cover direct builder, parsed CLI envelope, schema validation, all accepted intents, no-write default, explicit repo-root receipt write, unsafe path refusal, invalid max lenses, typoed path refusal, catalog failure, local-only behavior, `--repo-file` propagation, and handle-like missing target classification.

5. Update command metadata.
   - Add `review` to `VALID_ACTIONS["sdk"]` and public command examples.

6. Update capability truth.
   - Add `review_plan` capability row.
   - Add validation command refs.
   - Update status tests.

7. Update pipeline HTML.
   - Add summary and table row for `review_plan`.
   - Keep wording advisory/read-only and avoid review-complete claims.
   - Update artifact tests.

8. Run focused validation.
   - `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_plan.py -q`
   - `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py Infrastructure/tests/test_skills_sdk_lenses.py -q`
   - `./bin/ask sdk review plan --target Skills/agent-ops/simplify --intent validation_review --json --robot`
   - `./bin/ask sdk status --json --robot`
   - `bash scripts/validate-codestyle.sh --fast`

## Review Plan

Perform a local self-review after tests:

- Simplify check: verify no duplicate lens scoring logic or broad framework abstraction was introduced.
- Architecture check: verify receipt writing is explicit, bounded, and separated from review execution.
- Testing check: verify schema, CLI, and negative paths are covered.
- Ubiquitous language check: use `review plan receipt`, `review route`, and `read-only advisory` consistently.

External PR review, CodeRabbit, CircleCI, GitHub checks, and mergeability are separate PR green-sweep lanes after implementation and push.

## Validation Status

- Local discovery: pass.
- Spec artifact: pass, created.
- Trace plan artifact: pass, created by this file.
- Implementation validation: pass for focused local lane, with evidence listed below.
- PR/CI/review/mergeability: not checked and out of scope until PR exists.

## Validation Evidence

- Command: `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_review_plan.py Infrastructure/tests/test_skills_sdk_lenses.py Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` -> pass (`46 passed, 97 subtests passed`).
- Command: `python Infrastructure/bin/ask sdk review plan --target Skills/agent-ops/simplify --intent architecture_review --repo-file Infrastructure/tests/test_skills_sdk_review_plan.py --json --robot` -> pass (parsed robot JSON contains `data.review_plan`, `schema_version=skills-sdk.review-plan-receipt.v1`, `task_intent=architecture_review`, and `mutation_performed=false`).
- Command: `python Infrastructure/bin/ask sdk review plan --target Skills/agent-ops/simplifie --intent validation_review --json --robot` -> pass as negative proof (robot error envelope refuses the missing repo-relative path).
- Command: `python Infrastructure/bin/ask sdk status --json --robot` -> pass (status output contains `review_plan` as implemented and non-mutating).
- Command: `uv run --python 3.12 ruff check Infrastructure/scripts/lib/ask/skills_sdk/review_plan.py Infrastructure/scripts/lib/ask/commands/sdk.py Infrastructure/scripts/lib/ask/command_metadata.py Infrastructure/tests/test_skills_sdk_review_plan.py Infrastructure/tests/test_skills_sdk_capability_status.py` -> pass.
- Command: `bash scripts/validate-codestyle.sh --fast` -> pass.

## Open Risks

- A future reviewer could mistake a review plan receipt for review completion; wording and tests must keep that boundary explicit.
- Receipt-out path safety must be strict enough to prevent accidental writes outside intended paths.
- Capability status drift can recur unless status tests and pipeline artifact tests are updated with the new row.

## Next Stage

Prepare PR green-sweep: stage only PU-014 worktree changes, commit, push `codex/skills-sdk-pu-014-lens-routed-review`, open the PR, and then check PR status, CI, review comments, mergeability, and external review feedback as separate readiness lanes.
