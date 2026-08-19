---
schema_version: 1
artifact_id: sy-trace-plan-2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall
artifact_type: sy-trace-plan
canonical_slug: skills-sdk-pu-010-receipt-proven-rollback-uninstall
harness_stage: sy-trace-plan
title: "PU-010: Receipt-Proven Rollback and Uninstall Lifecycle Trace Plan"
status: trace_ready_for_plan
date: 2026-06-05
target_spec: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md
repo_mutation_scope: trace_artifact_only
external_mutation_status: not_authorized
---

# PU-010: Receipt-Proven Rollback and Uninstall Lifecycle Trace Plan

## Decision

Trace PU-010 from the hardened spec into implementation-ready proof rows. The next implementation plan must keep rollback and uninstall bounded to project roots, derive cleanup authority from valid install receipts plus lockfile state, preserve user-modified files, and prove every destructive edge case in temp projects before capability truth changes.

## Target

- Spec: `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md`
- Current local capability truth: `real_install` is implemented; `rollback` and `uninstall` are deferred.
- Current local state: primary repo has existing HTML artifact edits plus this PU-010 spec/review/trace lane.
- External lanes: PR, CI, review-thread, tracker, mergeability, and deployment state were not checked.

## Evidence Checked

| Evidence | Observation | Trace consequence |
| --- | --- | --- |
| `git status --short --branch` | Main is aligned with origin, with local HTML artifact edits and PU-010 spec/review artifacts present. | Implementation should start from a clean feature worktree or explicitly stage only the PU-010 trace/planning set. |
| PU-010 spec lines 24-82 | Scope is project rollback/uninstall only; global/workspace/registry/trust/signing/sandbox cleanup stays out of scope. | Trace rows must reject scope expansion during implementation planning. |
| PU-010 spec lines 96-111 | Three adversarial review passes were folded into the spec. | Safety, receipt authority, CLI semantics, and validation rows are first-class requirements. |
| PU-010 spec lines 117-134 | Affected surfaces include SDK CLI, project install helpers, cleanup module, schemas, tests, capability matrix, wrappers, and HTML artifacts. | Owner surfaces are known enough for sy-plan to create slices. |
| `./bin/ask sdk status --json --robot` | `real_install`: implemented; `rollback`: deferred; `uninstall`: deferred. | Capability truth must stay deferred until executable proof exists. |
| Review artifact: filesystem safety | Raised symlink, hardlink, case alias, directory pruning, journal, and unsafe-root gaps. | These become mandatory safety tests and planning slices. |
| Review artifact: receipt/lockfile | Raised receipt identity, duplicate skill id, before-state, and schema-version gaps. | These become schema/authority tests and planning slices. |
| Review artifact: CLI/tests/status | Raised mode exclusivity, preview root semantics, robot JSON, wrapper parity, status ladder, and command validation gaps. | These become CLI and validation trace rows. |
| Trace review artifact: coverage | Raised broad filesystem row, abstract receipt/journal artifacts, and weak capability/artifact sync. | Split trace rows and name concrete proof artifacts before implementation planning. |
| Trace review artifact: validation | Raised generic negative-test bucket, incomplete wrapper parity, missing journal interruption repro, and manual artifact truth. | Enumerate refusal commands and add wrapper/status/artifact proof gates. |
| Trace review artifact: slicing | Raised journal-after-mutation sequencing, unresolved design decisions, and status overclaim risk. | Add a prerequisite decision gate and move journal creation before destructive apply. |

## Traceability Map

| ID | Requirement source | Expected behavior | Owner surface | Artifact or task output | Validation command or proof | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TR-001 | Spec lines 24-42 | Implement receipt-proven rollback/uninstall as the recovery half of real project install. | `Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py` plus `sdk.py` routes | Cleanup planner and executor design | Temp-project rollback/uninstall integration tests pass | gap |
| TR-002 | Blocked inputs lines 437-444; trace slicing review | Freeze design decisions before code: cleanup schema shape, before-state policy, receipt identity field, duplicate-install policy, and journal location. | sy-plan implementation plan | Decision gate section in PU-010 implementation plan | Plan review confirms each decision is explicit before S1 begins | gap |
| TR-003 | Spec lines 44-82 | Keep scope project-local; reject global, workspace, registry, trust, signing, sandbox, and live-repo cleanup. | Cleanup root validator | Unsafe-root refusal logic | Separate unsafe-root refusal commands for rollback and uninstall | gap |
| TR-004 | FR-001 to FR-004 | Expose rollback and uninstall commands through `./bin/ask sdk` and `./bin/skills-sdk`. | `Infrastructure/scripts/lib/ask/commands/sdk.py`, `bin/skills-sdk` | CLI routes and wrapper parity | Ask and wrapper rollback/uninstall command tests | gap |
| TR-005 | FR-005, FR-028 | Require exactly one mode flag; preview performs no writes; apply is the only mutation path. | CLI argument parser and cleanup planner | Mode validation branch | Exact no-mode and dual-mode refusal commands for rollback and uninstall | gap |
| TR-006 | FR-006, FR-029, FR-030 | Keep receipt-only rollback preview receipt-derived; require project root for live validation and all apply mutation. | Cleanup planner | Preview validation-level field in JSON output | Rollback preview with and without `--project-root` | gap |
| TR-007 | FR-007 to FR-011 | Validate install receipt schema, operation, scope, mutation state, target root, file metadata, and drift before cleanup. | Receipt loader/validator | Receipt validation result model | Missing, malformed, stale, swapped, and mismatched-root receipt commands | gap |
| TR-008 | FR-038, receipt review | Bind cleanup authority to immutable receipt id or digest, schema version, target-root identity, and lockfile reference. | Install receipt schema, lockfile schema, cleanup receipt schema | Receipt identity fields or compatibility design | Swapped and stale receipt refusal commands | gap |
| TR-009 | FR-016 to FR-020, FR-039 | Resolve uninstall through `skills.lock.json`; refuse unknown, duplicate, ambiguous, or mismatched entries. | Lockfile loader/updater | Lockfile mutation plan | Unknown skill, duplicate skill id, missing receipt, and unrelated entry preservation commands | gap |
| TR-010 | FR-012 to FR-015 | Remove or restore only receipt-proven files; preserve modified files; restore overwritten files only with before-state proof. | Cleanup executor | File action plan and receipt output | Matching digest removal, modified file preservation, and missing before-state manual-action tests | gap |
| TR-011 | FR-031, FR-032, filesystem review | Validate path containment using filesystem identity and `lstat`, not lexical checks alone. | Cleanup filesystem guard | Path identity validator proof | Path traversal and canonicalization refusal commands | gap |
| TR-012 | FR-033, filesystem review | Reject unmodeled symlinked path components and remove only receipt-owned symlink artifacts. | Cleanup filesystem guard | Symlink ownership proof | Rollback and uninstall symlink refusal commands | gap |
| TR-013 | FR-034, filesystem review | Refuse destructive operations on hardlinked files unless exclusive ownership is proven. | Cleanup filesystem guard | Hardlink ownership proof | Rollback and uninstall hardlink refusal commands | gap |
| TR-014 | FR-035, filesystem review | Treat case-colliding path variants as ambiguous until filesystem identity proves the target. | Cleanup filesystem guard | Case-collision proof | Case-alias ambiguity command or platform-gated test | gap |
| TR-015 | FR-036, filesystem review | Prune only receipt-owned directories that are empty after a fresh content scan. | Directory prune planner | Directory ownership and empty-scan proof | Directory-with-user-file preservation command | gap |
| TR-016 | FR-037, AC-027, trace slicing review | Create cleanup journal before first mutation and detect unresolved journals on later cleanup attempts. | Cleanup journal module | Journal schema or staged state marker at an explicit project-local path | Two-step interrupt-and-rerun recovery/blocking test | gap |
| TR-017 | FR-021 to FR-024 | Emit schema-valid rollback/uninstall or shared cleanup receipts with action buckets, lockfile digests, journal, manual actions, and acceptance trace. | Cleanup receipt schema and writer | Named cleanup receipt schema file(s) and receipt writer | Schema validation for rollback/uninstall receipts | gap |
| TR-018 | FR-040 | Blocked robot-mode failures use repository error envelope with stable code, message, fix suggestion, command metadata, and `mutation_performed:false`. | CLI error/envelope helpers | Cleanup error contracts | Exact negative robot JSON assertions per refusal case | gap |
| TR-019 | FR-025 | Preserve PU-009 install behavior while sharing helpers. | `project_install.py` and existing tests | Refactored shared helpers without behavior drift | `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_install.py -q` plus targeted shared-helper regression tests | gap |
| TR-020 | FR-026, FR-027, capability ladder | Move rollback/uninstall above deferred only when executable proof supports preview, partial, or implemented status. | Capability matrix and status generator | Capability matrix update with evidence refs | `./bin/ask sdk status --json --robot`, `./bin/skills-sdk status --json --robot`, and status tests | gap |
| TR-021 | FR-041, trace validation review | Prove `./bin/ask sdk` and `./bin/skills-sdk` parity for status, preview, apply, and blocked apply paths. | Wrapper and CLI tests | Wrapper parity tests | Mirrored ask/wrapper rollback and uninstall commands with JSON comparison | gap |
| TR-022 | AC-001 to AC-032 | Cover success, refusal, partial, modified-file, receipt tamper, duplicate id, journal, wrapper, and artifact truth cases. | `Infrastructure/tests/test_skills_sdk_project_cleanup.py` plus status/artifact tests | Temp-project integration test matrix | Full PU-010 test set with enumerated refusal cases | gap |
| TR-023 | Spec lines 125-133, AC-032, trace coverage review | Keep capability matrix, status output, and both HTML artifacts aligned when labels change. | Capability status and HTML artifacts | Deterministic artifact sync proof for `capability-matrix.v1.json`, status JSON, `recommended-skills-sdk-pipeline.html`, and `skills-sdk-user-lifecycle-one-page.html` | Artifact/status sync command or checksum/diff assertion | gap |
| TR-024 | Spec lines 406-412 | Keep local proof separate from PR, CI, review-thread, tracker, and merge readiness. | PR green-sweep lane after implementation | Closeout proof receipt | Live PR/CI/review/mergeability checks after PR opens | out_of_scope_for_trace |

## Priority Gaps

| Priority | Gap | Why it matters | Recommended closure stage |
| --- | --- | --- | --- |
| P0 | Cleanup authority is not executable yet. | Rollback/uninstall are still deferred in local status. | `sy-plan` then `sy-work` |
| P0 | Pre-code decisions are unresolved. | Receipt identity, duplicate-id policy, before-state policy, cleanup schema shape, and journal location affect every later slice. | `sy-plan` decision gate |
| P0 | Receipt identity, root identity, and lockfile identity need one coherent design. | Cleanup safety depends on provenance, not just path strings. | `sy-plan` |
| P0 | Filesystem safety tests must cover symlink, hardlink, case alias, directory pruning, and unsafe roots. | These are destructive edge cases. | `sy-plan` then `sy-work` |
| P0 | Journal/recovery behavior must exist before destructive apply. | Partial cleanup without recovery can strand project state. | `sy-plan` then first mutation slice |
| P1 | CLI mode and robot JSON shape must be pinned before implementation. | Agents and scripts need deterministic failure semantics. | `sy-plan` then `sy-work` |
| P1 | Capability status ladder and HTML artifact sync must prevent overclaiming. | The SDK map should show truth only after proof exists. | `sy-work` plus closeout |
| P2 | External readiness lanes remain unchecked. | Local trace does not prove PR/CI/review/merge state. | `pr-green-sweep` after PR exists |

## Recommended Implementation Slices

| Slice | Goal | Trace rows | Stop condition |
| --- | --- | --- | --- |
| S0 | Decision gate before code | TR-002 | Cleanup schema, before-state policy, receipt identity, duplicate-id policy, and journal path are frozen in the implementation plan. |
| S1 | Shared cleanup planning spine | TR-001, TR-004, TR-005, TR-006, TR-007, TR-018 | Preview routes and blocked robot errors work without mutation. |
| S2 | Receipt and lockfile authority | TR-008, TR-009, TR-017 | Cleanup authority is receipt-id/digest-bound and duplicate-active installs are handled. |
| S3 | Journal foundation before mutation | TR-016 | Apply path cannot perform destructive actions until the cleanup journal or staged marker exists and is detected on rerun. |
| S4 | Filesystem safety executor | TR-003, TR-010, TR-011, TR-012, TR-013, TR-014, TR-015 | Apply cleanup removes/restores only safe owned files and blocks every enumerated unsafe filesystem case. |
| S5 | CLI parity, status, artifacts, and regression proof | TR-019, TR-020, TR-021, TR-022, TR-023 | Full refusal/recovery matrix, wrapper parity, status truth, and artifact truth agree without overclaiming. |
| S6 | PR closeout lane | TR-024 | PR/CI/review/mergeability are checked in the same closeout window. |

## Validation Matrix

| Command | Expected outcome | Trace rows | Proof limit |
| --- | --- | --- | --- |
| `./bin/ask sdk rollback --receipt <temp-receipt> --preview --json --robot` | pass | TR-003, TR-005 | Receipt-derived preview only. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot` | pass | TR-005, TR-006, TR-010 | Live project validation without writes. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot` | pass | TR-001, TR-009, TR-011, TR-012 | Rollback apply in temp project only. |
| `./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot` | pass | TR-003, TR-008 | Uninstall preview only. |
| `./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot` | pass | TR-001, TR-008, TR-009, TR-012 | Uninstall apply in temp project only. |
| `./bin/skills-sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot` | pass | TR-021 | Wrapper parity for rollback. |
| `./bin/skills-sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot` | pass | TR-021 | Wrapper parity for uninstall. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root <live-repo>` | fail before writing | TR-003, TR-018 | Unsafe-root refusal for rollback. |
| `./bin/ask sdk uninstall <skill-id> --project-root <live-repo> --apply --json --robot` | fail before writing | TR-003, TR-018 | Unsafe-root refusal for uninstall. |
| Rollback and uninstall no-mode commands | fail before planning | TR-005, TR-018 | Missing mode refusal. |
| Rollback and uninstall dual-mode commands | fail before planning | TR-005, TR-018 | Conflicting mode refusal. |
| Rollback with missing, malformed, stale, swapped, and mismatched-root receipts | fail before writing | TR-007, TR-008, TR-018 | Receipt refusal semantics. |
| Uninstall with unknown skill id, duplicate active skill id, missing receipt, and mismatched receipt binding | fail before writing | TR-009, TR-018 | Lockfile authority refusal semantics. |
| Rollback and uninstall with symlinked target paths | fail or skip without destructive action | TR-012, TR-018 | Symlink containment semantics. |
| Rollback and uninstall with hardlinked files | fail or skip without destructive action | TR-013, TR-018 | Hardlink ownership semantics. |
| Rollback and uninstall with case-colliding target aliases | fail or platform-gated skip with reason | TR-014, TR-018 | Case-alias ambiguity semantics. |
| Rollback and uninstall where owned directory contains user-added file | preserve directory and report manual action | TR-015, TR-018 | Directory prune safety. |
| Two-step journal interruption: begin apply, interrupt after journal write, rerun same cleanup command | resume safely or block with recovery payload | TR-016, TR-018 | Journal recovery semantics. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q` | pass | TR-001 to TR-023 | Local temp-project integration proof. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_install.py -q` | pass | TR-019 | PU-009 compatibility only. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` | pass | TR-020, TR-023 | Local status/artifact truth only. |
| `./bin/ask sdk status --json --robot` | pass | TR-020 | Local status truth only. |
| `./bin/skills-sdk status --json --robot` | pass | TR-020, TR-021 | Wrapper status truth only. |
| `./bin/skills-sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot` | pass | TR-021 | Wrapper parity for rollback apply. |
| `./bin/skills-sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot` | pass | TR-021 | Wrapper parity for uninstall apply. |
| `./bin/skills-sdk rollback --receipt <bad-receipt> --apply --project-root <temp-project> --json --robot` | fail before writing | TR-018, TR-021 | Wrapper parity for blocked apply. |
| Deterministic artifact truth sync for capability matrix, ask status JSON, `recommended-skills-sdk-pipeline.html`, and `skills-sdk-user-lifecycle-one-page.html` | pass | TR-023 | Local artifact truth only. |
| `bash scripts/validate-codestyle.sh --fast` | pass or documented blocker | General local codestyle lane | Does not prove runtime cleanup. |
| `./bin/ask repo validate --scope=check` | pass or documented blocker | Repo validation lane | Does not prove PR/CI/review/merge state. |

## Open Risks

- Current PU-009 install receipts may not contain enough before-state evidence to restore overwritten files automatically.
- Install receipt identity may need a schema extension or a compatibility decision before rollback authority can be strict.
- Duplicate active install handling may be better refused than modeled in the first cleanup slice; sy-plan should decide explicitly.
- Journal recovery could become too large if designed as a full transaction engine; keep the first mechanism as a small staged-state guard.
- HTML artifacts already have local truth-visualization edits. Keep those separate from PU-010 capability truth until rollback/uninstall proof exists.

## Next Stage

Recommended next stage: `sy-plan`.

Plan input: this trace plan plus the hardened PU-010 spec and three adversarial review artifacts.

Suggested plan artifact:

    .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-implementation-plan.md
