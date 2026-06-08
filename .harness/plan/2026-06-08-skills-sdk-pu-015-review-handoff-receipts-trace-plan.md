# PU-015: Skills SDK Review Handoff Receipts Trace Plan

## Metadata

- schema_version: 1
- stage: sy-trace-plan
- status: implemented
- date: 2026-06-08
- source_spec: .harness/specs/2026-06-08-skills-sdk-pu-015-review-handoff-receipts-spec.md
- branch: codex/skills-sdk-pu-015-review-handoff
- worktree: /private/tmp/agent-skills-pu-015-review-handoff
- target: Skills SDK review handoff surface

## Decision

Start PU-015 as a read-only handoff receipt slice. The slice consumes PU-014 `review_plan` receipts and emits a schema-backed `review_handoff` receipt that records reviewer roles, required artifacts, evidence boundaries, and next commands without executing reviews or claiming external readiness. Handoff requires explicit caller `--target` and `--intent`, then compares them with source receipt provenance so copied receipts fail closed.

## Evidence Checked

- Clean PU-015 branch/worktree exists at `/private/tmp/agent-skills-pu-015-review-handoff`.
- The branch was rebased onto `origin/main` at commit `2a4e5d809f5d079136b3dbd2fc91b89d8467247d` before implementation.
- The HTML PU-015 sync point requires handoff receipts after `sdk_lenses` and `review_plan`, before real agent execution.
- The capability matrix says `review_plan` is implemented and the next slice should hand off bounded reviews without treating the receipt as review completion.
- PU-014 spec and trace plan establish the source receipt fields and non-goals.
- First review loop found that provenance, target/intent mismatch, symlink-resolved output containment, and local-only guard tests must be explicit implementation requirements before code starts.

## Traceability Map

| ID | Source Requirement | Expected Behavior | Owner Files | Artifact / Receipt | Validation | Closeout Proof | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Consume review plan receipts | Parse and validate `sdk-review-plan-receipt.v1` before handoff output; require caller `--target` and `--intent` | `commands/sdk.py`, `review_handoff.py` | Robot JSON envelope | `test_skills_sdk_review_handoff.py` | Valid plan plus matching target/intent produces `data.review_handoff` | implemented |
| R1A | Require source receipt provenance | Extend review-plan receipts with `source_context`; reject missing or mismatched repo root, HEAD, branch policy, target identity, target path, target digest, unresolved handles, or unsupported directory digests | `review_plan.py`, `sdk-review-plan-receipt.v1.schema.json`, `review_handoff.py` | Source review-plan receipt and handoff error envelope | Provenance fixture tests | Copied or provenance-missing plan fails with no write | implemented |
| R1B | Require independent receipt trace integrity | Write paired review-plan trace sidecars keyed by canonical receipt digest; handoff recomputes digest and refuses missing sidecars, mismatched sidecars, mismatched resolved plan paths, or mismatched receipt instance ids | `review_plan.py`, `review_handoff.py`, `sdk-review-plan-trace.v1.schema.json` | Trace sidecar and handoff error envelope | Edited/copy fixture tests | Edited receipt, copied path, mismatched instance id, or missing sidecar fails with no write | implemented |
| R2 | Refuse stale or mismatched inputs | Fail unsupported schema, stale target, target mismatch, intent mismatch, missing lenses, unsafe paths, copied receipts, digest mismatch | `review_handoff.py` | Error envelope | Negative tests | Error status and no receipt write | implemented |
| R3 | Emit handoff fields | Include source plan, source context, target, lenses, reviewer roles, required artifacts, evidence boundaries, not-proven lanes, next commands, mutation metadata | `review_handoff.py`, schema | `sdk-review-handoff-receipt.v1` | Schema validation | Required fields present | implemented |
| R4 | Keep default read-only | No file writes unless explicit output path is supplied | `review_handoff.py` | `receipt_written=false` | Temp path tests | No default output file | implemented |
| R4A | Enforce resolved output containment | Resolve output parent and existing file symlinks before containment checks; reject repo-local symlinks that escape | `review_handoff.py` | Error envelope | Symlink escape test | Escaping output path fails with no write | implemented |
| R5 | Keep execution out of scope | Do not run agents, CodeRabbit, GitHub, CircleCI, subprocess helpers, or network calls | `review_handoff.py` | Handoff receipt text | Guarded tests that trap subprocess/network helpers | Builder remains local-only | implemented |
| R6 | Schema-backed contract | Add public JSON Schema and validate emitted receipts | `sdk-review-handoff-receipt.v1.schema.json` | Public schema | Schema tests | Valid receipt passes schema | implemented |
| R7 | Capability truth update | Add `review_handoff` row to SDK status and matrix | `capability_status.py`, matrix | Status output | Capability status tests | `ask sdk status` row implemented/non-mutating | implemented |
| R8 | Pipeline artifact update | HTML row and sync text match matrix/status | HTML artifact, artifact tests | Local HTML | Pipeline artifact tests | HTML parity passes | implemented |

## Implementation Steps

1. Add a focused failing test file for `review_handoff`.
   - Fixture: generate or embed a minimal valid PU-014 review-plan receipt.
   - Required happy path: `--plan`, `--target`, and `--intent` all match source receipt provenance.
   - Negative fixtures: missing `source_context`, missing trace sidecar, edited receipt digest mismatch, byte-identical copied plan path mismatch, mismatched `receipt_instance_id`, copied repo root, stale HEAD, unsupported branch policy, stale target digest, mismatched target, mismatched intent, unresolved handle, unsupported directory digest, missing selected lenses, unsupported schema, unsafe output.
   - Output safety fixture: repo-local symlink pointing outside the checkout must be rejected after symlink resolution.
   - Local-only fixture: monkeypatch subprocess and network entry points and assert the pure builder does not call them.

2. Add the public handoff schema.
   - Require all receipt fields.
   - Require `source_context` to be echoed into the handoff receipt.
   - Require `source_trace` summary with trace path and receipt digest.
   - Constrain `mutation_performed` to false.
   - Model `not_proven` lanes explicitly.

3. Extend `review_plan` receipt provenance and trace output.
   - Add `source_context` to newly emitted `sdk-review-plan-receipt.v1` receipts.
   - Capture resolved repo root, current HEAD SHA, branch, `branch_policy=same_head_required`, `receipt_instance_id`, target input, target identity, path-backed target resolution, digest status, provenance risk flags, and target content digest.
   - Resolve handles to canonical source paths before handoff eligibility; unresolved handles remain valid for planning but fail closed for handoff.
   - Define deterministic directory digesting or mark directories unsupported with `provenance_risk_flags`; unsupported directory digests fail closed for handoff.
   - Add `sdk-review-plan-trace.v1.schema.json`.
   - When `--receipt-out` writes a plan receipt, also write `.harness/artifacts/sdk-review-plan/traces/<receipt-sha256>.trace.json` with resolved `receipt_path`, `receipt_instance_id`, `receipt_sha256`, `repo_root`, `head_sha`, `branch_policy`, `target_identity`, `target_content_digest`, and `created_by_command`.
   - Update the review-plan receipt schema and tests before handoff accepts the field.

4. Implement `review_handoff.py`.
   - Load JSON with structured errors.
   - Validate source review-plan shape.
   - Require caller `--target` and `--intent`; compare both against receipt target and task intent.
   - Recompute the source receipt canonical digest and require a matching repo-local trace sidecar.
   - Compare resolved caller `--plan` path to trace `receipt_path`.
   - Compare `receipt_instance_id` between receipt and trace.
   - Re-check source provenance, current HEAD, resolved target identity/path, and target digest.
   - Resolve output paths through symlinks before repo-root containment checks.
   - Build deterministic reviewer role and artifact lists from selected lenses and intent.
   - Keep builder local-only.

5. Add `sdk review handoff` command wiring.
   - Required `--plan <path>`.
   - Required `--target <path-or-handle>`.
   - Required `--intent <known-intent>`.
   - Optional `--receipt-out <path>` with repo-root containment.

6. Update capability truth and HTML.
   - Add `review_handoff` after `review_plan`.
   - Preserve the boundary that handoff is not review completion.
   - Keep matrix, required ids, status summary, and HTML order aligned.

7. Run focused validation.
   - Review-handoff tests.
   - Review-plan provenance tests.
   - Review-plan trace sidecar tests.
   - Capability/status artifact parity.
   - CLI smoke for plan then handoff without `--receipt-out`.
   - CLI smoke for handoff with `--receipt-out .harness/artifacts/sdk-review-handoff/pu015-output.json`.
   - SDK status.
   - Codestyle fast gate.

## Review Plan

Before closeout, run a bounded review pass:

- Simplify: no duplicate review-plan parsing frameworks or broad abstractions.
- Architecture: handoff receipt remains separate from review execution.
- Testing: schema, CLI, provenance, symlink containment, negative paths, and local-only guards covered.
- Language: use `review handoff receipt`, `required artifacts`, and `not proven` consistently.
- Security/adversarial: copied receipts, edited receipts without matching trace sidecars, stale HEAD, stale target digest, unresolved handles, unsupported directory digests, and symlink escape paths fail closed.

## Validation Status

- Clean branch/worktree setup: pass.
- Spec artifact: pass, created by this file pair.
- Implementation validation: not run; implementation not started.
- PR/CI/review/mergeability: not checked and out of scope until PR exists.

## Started Evidence

- Command: `git worktree add -b codex/skills-sdk-pu-015-review-handoff /private/tmp/agent-skills-pu-015-review-handoff HEAD` -> pass.
- Command: `git status --short --branch` in the PU-015 worktree -> pass, clean branch.
- Command: `rg -n "PU-015|review handoff|review_plan|review plan" .harness/plan/2026-06-07-skills-sdk-main-reconciliation-route-tracker.md artifacts/recommended-skills-sdk-pipeline.html Infrastructure/config/skills-sdk/capability-matrix.v1.json` with temp `MISE_*` state -> pass.

## Open Risks

- The handoff receipt could overclaim if `not_proven` lanes are not first-class fields.
- The command could accidentally become a review runner if reviewer execution and handoff packaging are not kept separate.
- Status drift can recur unless the same matrix/HTML parity tests are kept in the PU-015 validation lane.
- Provenance drift can recur unless review-plan source context is schema-required and handoff refuses legacy or copied receipts.
- Self-reported provenance is not enough; handoff must verify the paired trace sidecar digest before accepting a source receipt.
- Output containment can regress unless symlink escape tests are part of the focused test file.

## Next Stage

Implement the focused `review_handoff` schema, builder, command route, tests, capability row, and HTML row in this PU-015 worktree.
