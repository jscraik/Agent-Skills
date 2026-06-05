---
schema_version: 1
artifact_id: sy-spec-2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall
artifact_type: sy-spec
canonical_slug: skills-sdk-pu-010-receipt-proven-rollback-uninstall
harness_stage: sy-spec
title: "PU-010: Skills SDK Receipt-Proven Rollback and Uninstall Lifecycle Spec"
status: spec_ready_for_plan
date: 2026-06-05
source_previous_spec: .harness/specs/2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle-spec.md
source_capability_matrix: Infrastructure/config/skills-sdk/capability-matrix.v1.json
source_v1_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_v1_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
origin: user_requested_sy_spec
risk: high
ui: false
traceability_required: true
repo_mutation_scope: spec_artifact_only
external_mutation_status: not_authorized
---

# PU-010: Skills SDK Receipt-Proven Rollback and Uninstall Lifecycle Spec

## Command Summary

BLUF: PU-010 closes the project-install mutation loop by adding rollback and uninstall commands that operate only from receipt-proven install state. The SDK must refuse cleanup when it cannot prove exactly what it owns, preserve user-modified files, update `skills.lock.json` safely, and emit rollback or uninstall receipts that explain every restored, removed, skipped, blocked, or manual action.

Decision: Build rollback and uninstall for bounded project installs only. Rollback and uninstall must derive authority from a valid PU-009 install receipt plus the target project's lockfile state. Do not add global uninstall, workspace uninstall, registry uninstall, trust-store mutation, package signing, sandbox execution, or remote package cleanup in this slice.

Next Action: Hand this spec to `sy-plan` or the repository's governed planning lane to produce a PU-010 implementation plan in a clean feature worktree from current `main`.

## Purpose

PU-009 made the Skills SDK capable of real bounded project install writes. That moved the SDK from read-only planning into project mutation. PU-010 is the recovery and cleanup slice that makes those writes trustworthy.

The intended user outcome is simple: after a project install, a user or agent can ask the SDK what it would remove or restore, then explicitly apply rollback or uninstall only when the install receipt and project state prove the SDK owns the files it plans to touch.

## Problem Statement

Real install writes without executable rollback or uninstall leave the SDK with an incomplete mutation story. A failed or unwanted install can currently be understood from receipts, but there is no SDK-owned command that converts those receipts into a safe cleanup plan.

Without PU-010, later slices such as trust-store mutation, signing, registry installs, hosted explorer install flows, and package hardening would each need to invent their own cleanup behavior. PU-010 should create the durable recovery contract now, while the mutation surface is still narrow and project-scoped.

## Approved Scope

In scope:

- project-scoped rollback from a valid install receipt
- project-scoped uninstall from a skill id recorded in `skills.lock.json`
- preview-first rollback and uninstall planning
- explicit `--apply` mutation path for rollback and uninstall
- explicit `--project-root <path>` contract for mutating commands
- explicit mode validation requiring exactly one of `--preview` or `--apply`
- receipt-only rollback preview as a receipt-derived plan, with project-root validation only when `--project-root` is supplied
- receipt validation before any cleanup mutation
- project-root and receipt-root consistency checks
- target-path containment checks under the resolved project root using filesystem identity, not string matching alone
- unsafe-root refusal for filesystem root, home directories, live repo/worktree roots, file paths, missing roots, and ambiguous relative roots
- symlink, hardlink, case-alias, and directory-pruning safety rules
- cleanup mutation journaling so interrupted cleanup can be diagnosed and safely resumed or blocked
- immutable receipt identity and lockfile-bound receipt references
- install-instance identity or explicit duplicate-active-install refusal
- tamper detection using recorded file digests
- preservation of user-modified files unless an exact receipt-backed expected hash proves safe mutation
- safe `skills.lock.json` update during rollback or uninstall
- rollback and uninstall receipt schemas or a shared cleanup receipt schema
- temp-project integration tests proving cleanup behavior outside the live repo
- capability matrix and `ask sdk status` updates for rollback and uninstall
- local HTML artifact truth updates if capability labels change

Out of scope:

- global uninstall from `~/.codex`, `~/.agents`, or other home-directory surfaces
- workspace uninstall outside an explicit target project root
- remote registry, marketplace, or publish state cleanup
- trust-store mutation or trust revocation
- package signing or signature verification
- sandbox execution
- uninstall of files not proven by install receipts or lockfile entries
- destructive cleanup of user-modified files
- live agent-skills repo mutation in automated tests
- GitHub, Linear, tracker, review-thread, CI, or merge-state mutation without separate approval

## Current Evidence

| Evidence | Current observation | Spec consequence |
| --- | --- | --- |
| `git status --short --branch` | `main` is clean against origin except local HTML artifact edits that mark SDK completion visually. | PU-010 implementation should start from a clean feature worktree or explicitly carry artifact-truth edits in a separate commit. |
| `.harness/specs/2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle-spec.md` | PU-009 approved project-scoped real install, install receipts, lockfile writes, and rollback seed metadata, while rollback and uninstall execution stayed out of scope. | PU-010 must build only on PU-009 receipts and not widen install authority. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_install.py` | Project install owns the current bounded mutation path and install receipt production. | Rollback and uninstall should reuse its path validation, receipt loading, digest, and lockfile helpers where practical. |
| `Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json` | Install receipts include installed files, target root, lockfile digests, rollback metadata, and mutation state. | Rollback must treat the install receipt as the authority source and reject receipts that lack enough metadata. |
| `Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json` | Project lockfile entries record installed skill identity, source digest, target path, receipt reference, timestamp, and file digests. | Uninstall can be keyed by skill id only when the lockfile entry points to a valid receipt and current project root. |
| `./bin/ask sdk status --json --robot` | `real_install` is implemented with `mutation_performed: true`; `rollback` and `uninstall` remain deferred. | PU-010 acceptance must update rollback and uninstall truth only after executable temp-project proof exists. |
| `artifacts/recommended-skills-sdk-pipeline.html` and `artifacts/skills-sdk-user-lifecycle-one-page.html` | Local artifacts were updated with green visual outlines for completed and preview-backed surfaces. | If PU-010 changes capability truth, these artifacts should be updated or explicitly deferred with a truth-sync follow-up. |

## Adversarial Review Corrections

Three adversarial-reviewer passes were run against this spec before planning. Their accepted corrections are part of the PU-010 contract:

| Reviewer lens | Accepted gap | Spec correction |
| --- | --- | --- |
| filesystem safety | Lexical containment can miss symlink, hardlink, case-alias, and inode escapes. | Cleanup must use filesystem-aware canonicalization plus `lstat`/identity checks before deleting, restoring, pruning, or updating lock state. |
| filesystem safety | Directory cleanup could delete user-added content or leave ambiguous orphan state. | Cleanup may prune only directories proven install-owned and empty after a fresh content check. Unowned entries stop pruning and become skipped or manual action. |
| filesystem safety | Atomic JSON writes alone do not make rollback or uninstall transactional. | Apply mode must create a cleanup journal or equivalent staged state before the first filesystem mutation and define recovery behavior for interrupted cleanup. |
| filesystem safety | The live repo or another sensitive root could be targeted accidentally. | Rollback and uninstall must reuse unsafe-root refusal from project install and reject live worktrees, home roots, filesystem roots, file paths, missing roots, and ambiguous relative roots. |
| receipt and lockfile | A path label is not authoritative receipt identity. | Cleanup authority must be bound to receipt digest or receipt id, schema version, resolved target root, and lockfile reference. |
| receipt and lockfile | Duplicate skill ids can make uninstall target the wrong install instance. | Lockfile state must include an install-instance id or refuse duplicate active installs for the same skill id before cleanup can proceed. |
| receipt and lockfile | Overwritten-file restoration needs machine-checkable before-state. | Restoration requires before-content or an approved before-state reference with digest proof; otherwise the path becomes manual action with a structured reason. |
| CLI and tests | Preview/apply mode selection was ambiguous. | Exactly one mode flag is required; both flags or neither flag must fail before planning or writing. |
| CLI and tests | Rollback preview without project root could overclaim live-tree validation. | Receipt-only preview may emit a receipt-derived plan, but must mark live project validation as unavailable. Project-root validation requires `--project-root`. |
| CLI and tests | Error envelopes, wrapper parity, and validation commands were too loose. | Blocked robot JSON shape, `./bin/ask`/`./bin/skills-sdk` parity, explicit cleanup command validation, and capability-status thresholds are now required. |

## Affected Surfaces

| Surface | Classification | Required action |
| --- | --- | --- |
| `Infrastructure/scripts/lib/ask/commands/sdk.py` | change | Add `rollback` and `uninstall` subcommands with preview/apply/project-root/receipt arguments. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_install.py` | change | Extract or reuse receipt, path containment, digest, atomic JSON, and lockfile helpers for cleanup operations. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py` | change | Recommended new module for rollback and uninstall planning/execution. |
| `Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json` | read_only_or_change_if_needed | Read as rollback authority; extend only if current metadata is insufficient and migration is explicit. |
| `Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json` | read_only_or_change_if_needed | Read/update lock entries during uninstall and rollback; extend only with compatibility-safe fields. |
| `Infrastructure/config/schemas/skills-sdk/rollback-receipt.v1.schema.json` | change | Add if separate rollback receipt schema is chosen. |
| `Infrastructure/config/schemas/skills-sdk/uninstall-receipt.v1.schema.json` | change | Add if separate uninstall receipt schema is chosen. |
| `Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json` | change | Alternative to separate rollback/uninstall schemas if one discriminated schema is simpler. |
| `Infrastructure/config/skills-sdk/capability-matrix.v1.json` | change | Move rollback and uninstall from deferred to implemented or partial only when evidence supports the label. |
| `Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json` | read_only_or_change_if_needed | Permit cleanup capabilities to report mutation_performed true only when explicit apply behavior exists. |
| `Infrastructure/tests/test_skills_sdk_project_install.py` | change | Preserve install proof and add shared fixtures if useful. |
| `Infrastructure/tests/test_skills_sdk_project_cleanup.py` | change | Recommended temp-project integration tests for rollback and uninstall. |
| `Infrastructure/tests/test_skills_sdk_capability_status.py` | change | Prove rollback/uninstall capability truth changes without overclaiming unrelated lanes. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | change | Update if HTML capability truth is required to match the capability matrix. |
| `bin/skills-sdk` | read_only_or_change_if_needed | Confirm wrapper parity for rollback/uninstall routes. |
| `artifacts/recommended-skills-sdk-pipeline.html` | change_if_truth_changes | Keep visual capability truth aligned with rollback/uninstall status. |
| `artifacts/skills-sdk-user-lifecycle-one-page.html` | change_if_truth_changes | Keep visual capability truth aligned with rollback/uninstall status. |
| GitHub, Linear, review threads, CI | not_checked | Do not claim readiness for these lanes unless checked during closeout. |

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | The SDK MUST expose `ask sdk rollback --receipt <path> --preview --json --robot`. |
| FR-002 | The SDK MUST expose `ask sdk rollback --receipt <path> --apply --project-root <path> --json --robot`. |
| FR-003 | The SDK MUST expose `ask sdk uninstall <skill-id> --project-root <path> --preview --json --robot`. |
| FR-004 | The SDK MUST expose `ask sdk uninstall <skill-id> --project-root <path> --apply --json --robot`. |
| FR-005 | Preview mode MUST be non-mutating for rollback and uninstall. |
| FR-006 | Apply mode MUST require explicit `--apply` and an explicit resolved project root. |
| FR-007 | Rollback MUST require a readable, schema-valid install receipt before planning any mutation. |
| FR-008 | Rollback MUST refuse receipts with missing required metadata, invalid schema, unsupported operation, unsupported scope, missing installed files, or missing target root. |
| FR-009 | Rollback MUST refuse receipts whose target root does not match the supplied project root after resolution. |
| FR-010 | Rollback MUST refuse receipts whose target paths escape the resolved project root. |
| FR-011 | Rollback MUST refuse receipts whose lockfile digests or installed file digests prove the project state has drifted beyond safe automatic cleanup. |
| FR-012 | Rollback MUST remove only files proven by the install receipt and safe by current digest comparison. |
| FR-013 | Rollback MUST preserve user-modified files unless the current digest exactly matches the digest recorded as installed or otherwise explicitly safe in receipt metadata. |
| FR-014 | Rollback MUST restore overwritten files only when the install receipt contains before-content or an approved before-state reference with digest proof. |
| FR-015 | If before-content is unavailable, rollback MUST report manual action for overwritten files rather than inventing restoration. |
| FR-016 | Uninstall MUST resolve the skill id through `skills.lock.json` in the supplied project root. |
| FR-017 | Uninstall MUST refuse unknown skill ids, duplicate or ambiguous lock entries, missing receipt references, or receipt references outside the project root. |
| FR-018 | Uninstall MUST validate the referenced install receipt before planning mutation. |
| FR-019 | Uninstall MUST remove only files recorded in the lockfile entry and receipt and safe by current digest comparison. |
| FR-020 | Uninstall MUST update `skills.lock.json` atomically after successful cleanup or report partial state when cleanup cannot fully complete. |
| FR-021 | Rollback and uninstall MUST emit schema-valid receipts with operation, status, target_root, source receipt, files_removed, files_restored, files_skipped, files_blocked, lockfile changes, mutation_performed, manual_actions, and acceptance_trace. |
| FR-022 | A blocked preview or apply before mutation MUST report `mutation_performed: false`. |
| FR-023 | A partial failure after mutation begins MUST report `mutation_performed: true` and list every completed and unresolved action. |
| FR-024 | Generated receipt and lockfile JSON MUST be written through deterministic, atomic write helpers. |
| FR-025 | The SDK MUST keep PU-009 install behavior compatible. |
| FR-026 | The SDK MUST update capability truth so rollback and uninstall no longer remain deferred when implementation evidence exists. |
| FR-027 | If rollback or uninstall cannot be fully implemented from current install receipts, the capability matrix MUST use an honest partial or preview-backed status and explain the missing proof. |
| FR-028 | The CLI MUST require exactly one of `--preview` or `--apply` for rollback and uninstall; both flags or neither flag MUST fail before planning or writing. |
| FR-029 | Rollback preview without `--project-root` MUST be limited to receipt-derived planning and MUST report that live project validation was not performed. |
| FR-030 | Rollback preview with `--project-root` MUST perform the same project-root, unsafe-root, receipt-root, path-identity, and current-digest checks as apply without writing. |
| FR-031 | Rollback and uninstall MUST reject unsafe roots, including filesystem root, home directory roots, the live agent-skills repo/worktree, missing paths, file paths, ambiguous relative paths, and roots that cannot be resolved to one filesystem identity. |
| FR-032 | Cleanup path validation MUST use filesystem-aware canonicalization plus `lstat` or equivalent identity checks for every parent and target path. |
| FR-033 | Cleanup MUST reject symlinked path components unless the receipt explicitly modeled the symlink as the installed artifact and cleanup can prove the link itself, not its target, is owned. |
| FR-034 | Cleanup MUST refuse destructive operations on hardlinked files unless exclusive ownership is proven; otherwise the file becomes blocked or manual action. |
| FR-035 | Cleanup MUST treat case-colliding path variants as ambiguous until filesystem identity proves they reference the intended project root and target. |
| FR-036 | Cleanup MAY prune directories only when the receipt or lockfile proves directory ownership and a fresh content check proves the directory is empty of unowned entries. |
| FR-037 | Apply mode MUST create a cleanup journal or equivalent staged state before the first filesystem mutation and MUST use it to report or recover interrupted cleanup states. |
| FR-038 | Cleanup authority MUST be bound to an immutable receipt id or receipt digest, schema version, resolved target root, and lockfile reference, not a path string alone. |
| FR-039 | Lockfile entries MUST identify an install instance or cleanup MUST refuse duplicate active entries for the same skill id. |
| FR-040 | Blocked robot-mode failures MUST use the repository error envelope with `status:error`, an error code, message, fix suggestion, command metadata, and `mutation_performed:false` when no mutation occurred. |
| FR-041 | `./bin/ask sdk` and `./bin/skills-sdk` MUST be proven equivalent for rollback and uninstall preview, apply refusal, and at least one successful temp-project cleanup path. |

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | Cleanup planning MUST be deterministic for stable tests and diffs. |
| NFR-002 | Cleanup commands MUST be safe for agent execution in temporary project roots. |
| NFR-003 | Default cleanup commands MUST require no network access. |
| NFR-004 | Robot-mode failures MUST include blocker class, fix suggestion, and receipt or lockfile evidence path when available. |
| NFR-005 | The implementation MUST reuse existing SDK path, digest, receipt, schema, and lockfile patterns where practical. |
| NFR-006 | The implementation MUST not mutate the live agent-skills repo in tests. |
| NFR-007 | Local validation MUST stay separate from PR, CI, review, tracker, and merge readiness. |

## Command Contract

Rollback preview:

    ./bin/ask sdk rollback --receipt <path> --preview --json --robot
    ./bin/skills-sdk rollback --receipt <path> --preview --json --robot

Rollback apply:

    ./bin/ask sdk rollback --receipt <path> --apply --project-root <path> --json --robot
    ./bin/skills-sdk rollback --receipt <path> --apply --project-root <path> --json --robot

Uninstall preview:

    ./bin/ask sdk uninstall <skill-id> --project-root <path> --preview --json --robot
    ./bin/skills-sdk uninstall <skill-id> --project-root <path> --preview --json --robot

Uninstall apply:

    ./bin/ask sdk uninstall <skill-id> --project-root <path> --apply --json --robot
    ./bin/skills-sdk uninstall <skill-id> --project-root <path> --apply --json --robot

Required semantics:

- `--preview` performs no writes.
- `--apply` is the only mutation path.
- exactly one of `--preview` or `--apply` is required.
- both mode flags or neither mode flag fail before receipt loading, lockfile loading, planning, or writing.
- apply commands require an explicit resolved project root.
- rollback preview without `--project-root` may return only a receipt-derived plan and must mark live filesystem validation as unavailable.
- rollback preview with `--project-root` must perform live project validation without writing.
- no command may infer a project root from the live repo during tests.
- rollback derives authority from the receipt.
- uninstall derives authority from lockfile entry plus referenced receipt.
- cleanup paths must remain under the resolved project root.
- user-modified files must be skipped or blocked, not removed.

Blocked robot JSON semantics:

- blocked argument, receipt, root, path, digest, lockfile, or journal failures return `status:error`.
- the first error includes a stable code, human message, fix suggestion, and evidence path when available.
- command metadata identifies the invoked cleanup command and mode.
- no-mutation failures include `mutation_performed:false`.
- partial failures after mutation begins return `status:partial` or an equivalent repository-approved partial envelope with `mutation_performed:true` and the cleanup receipt or journal path.

## Receipt Validation Contract

Before rollback or uninstall can plan writes, the SDK MUST verify:

- receipt file exists and is readable
- receipt JSON is valid and schema-conformant
- `schema_version` is supported
- `operation` is `install`
- `scope` is `project`
- `status` is `success` or another explicitly supported cleanup source state
- `mutation_performed` is true for a cleanup source receipt
- `target_root` resolves to the supplied project root when `--project-root` is present
- receipt-only preview reports project-root validation as unavailable rather than inferred
- the receipt has an immutable identity, such as receipt id or digest, that matches the lockfile reference when a lockfile is part of the operation
- the receipt schema version and schema URI are supported by the cleanup implementation
- `files_written`, `files_overwritten`, and `target_paths` are internally consistent
- every planned target path is relative to or contained by the project root after filesystem-aware canonicalization
- no planned target traverses an unmodeled symlink, unsafe hardlink, case-colliding alias, or ambiguous path identity
- every current file planned for removal has a digest matching install evidence
- overwritten files have enough before-state evidence to restore; otherwise they become manual actions

## Lockfile Update Contract

The canonical project lockfile for PU-010 is `skills.lock.json` at the resolved project root. Alternate lockfile paths require an explicit migration rule before cleanup can use them as authority.

Rollback and uninstall MUST:

- load and validate the lockfile before apply when it exists
- refuse ambiguous or duplicate active lock entries for the same skill id unless an install-instance id selects exactly one entry
- refuse to remove a lock entry that does not match the source receipt identity, install-instance id when present, and skill id
- bind receipt references by digest or receipt id, not by mutable path label alone
- compute lockfile before and after digests
- write the lockfile atomically inside the project root
- remove the skill entry only after file cleanup succeeds, or record partial status if cleanup partially succeeds
- preserve unrelated lockfile entries
- keep deterministic key ordering

## Filesystem Safety Contract

Before any apply mutation, rollback and uninstall MUST:

- resolve the project root to one filesystem identity and reject unsafe roots
- validate every parent directory and target with `lstat` or an equivalent non-following metadata call before mutation
- reject lexical containment as insufficient unless backed by resolved filesystem identity
- reject unmodeled symlinks in parent paths
- remove a symlink only when the symlink itself is the receipt-proven installed artifact
- refuse hardlinked files unless exclusive ownership is proven by receipt and current filesystem metadata
- handle case-insensitive filesystems by detecting case collisions and requiring a single unambiguous identity
- plan directory pruning separately from file removal
- prune only receipt-owned directories that are empty after a fresh content scan
- stop pruning when any unowned file, directory, symlink, or special entry is present

## Cleanup Journal Contract

Apply mode MUST persist a cleanup journal or equivalent staged marker before the first filesystem mutation. The journal MUST record:

- operation and mode
- source install receipt identity
- target project root identity
- planned file, directory, lockfile, and receipt writes
- current operation phase: `planned`, `mutating_files`, `updating_lockfile`, `writing_receipt`, `complete`, or `blocked`
- completed actions with digest or identity evidence
- unresolved actions and manual actions
- recovery instruction for a later cleanup attempt

If cleanup is interrupted, the next cleanup command MUST detect the journal and either resume safely from recorded evidence or fail with a blocked recovery payload. It MUST NOT silently re-plan over an unresolved journal.

## Capability Status Ladder

Rollback and uninstall capability truth MUST use this ladder:

| Status | Required evidence |
| --- | --- |
| deferred | Command route absent or intentionally postponed. |
| preview | Receipt-derived preview exists, but apply mutation is absent. |
| partial | Apply exists for a bounded subset, but restoration, duplicate-instance handling, journal recovery, or safety refusal paths are incomplete. |
| implemented | Preview and apply pass temp-project integration tests for success, refusal, modified-file preservation, lockfile update, wrapper parity, journal recovery, artifact truth, and status truth. |

Parser-only routes, status-only matrix edits, or receipt schema changes alone MUST NOT move rollback or uninstall above `deferred` or `preview`.

## Cleanup Receipt Contract

The implementation may choose separate rollback and uninstall receipt schemas or one discriminated cleanup receipt schema. In either design, the receipt MUST include:

| Field | Requirement |
| --- | --- |
| schema_version | Versioned cleanup schema. |
| schema_uri | Versioned schema URI. |
| status | `success`, `blocked`, or `partial`. |
| operation | `rollback` or `uninstall`. |
| source_install_receipt | Project-relative or absolute label for the validated install receipt. |
| source_install_receipt_digest | Digest of the exact validated install receipt. |
| source_install_receipt_id | Immutable receipt id when available. |
| skill_id | Skill id when known. |
| install_instance_id | Install-instance id when available, or null with duplicate-active-install refusal evidence. |
| target_root | Resolved project root label. |
| target_root_identity | Filesystem identity used for containment and unsafe-root checks. |
| mutation_performed | Boolean with true only after filesystem mutation. |
| files_removed | Files removed with prior digest evidence. |
| files_restored | Files restored with before and after digest evidence. |
| files_skipped | Files left untouched with reason. |
| files_blocked | Files that prevented automatic cleanup. |
| directories_pruned | Directories removed with ownership and empty-directory proof. |
| directories_skipped | Directories left in place with reason. |
| lockfile_before_digest | Digest before lockfile update or null. |
| lockfile_after_digest | Digest after lockfile update or null. |
| cleanup_journal | Journal path or journal digest used by apply mode. |
| manual_actions | Human-readable cleanup tasks for unsafe automatic actions. |
| acceptance_trace | PU-010 acceptance ids. |

## Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-001 | A valid PU-009 install receipt exists in a marked temp project | rollback preview runs with `--receipt` | command emits a cleanup plan, performs no writes, and reports `mutation_performed: false`. |
| AC-002 | A valid PU-009 install receipt exists in a marked temp project | rollback apply runs with matching `--project-root` | installed files with matching digests are removed or restored according to receipt evidence. |
| AC-003 | A rollback receipt is emitted | schema validation runs | receipt is schema-valid and records removed/restored/skipped/blocked/manual actions. |
| AC-004 | Rollback apply is called without `--project-root` | command validates arguments | command fails before writing with a project-root fix suggestion. |
| AC-005 | Rollback receives a missing, unreadable, malformed, or schema-invalid receipt | command validates receipt | command fails before writing with `mutation_performed: false`. |
| AC-006 | Rollback receives a receipt whose target root differs from supplied project root | command validates root | command fails before writing with `mutation_performed: false`. |
| AC-007 | Rollback receives a receipt with target paths escaping the project root | command validates paths | command fails before writing with `mutation_performed: false`. |
| AC-008 | A file installed by PU-009 was modified by a user after install | rollback or uninstall apply runs | command preserves the file, records it as skipped or blocked, and reports manual action. |
| AC-009 | A file installed by PU-009 still matches the install digest | rollback or uninstall apply runs | command may remove the file and records the exact prior digest. |
| AC-010 | An overwritten file lacks before-state content or approved restoration evidence | rollback apply runs | command does not invent restoration and reports manual action. |
| AC-011 | A skill id exists in `skills.lock.json` with a valid receipt reference | uninstall preview runs | command emits a cleanup plan and performs no writes. |
| AC-012 | A skill id exists in `skills.lock.json` with a valid receipt reference | uninstall apply runs | command removes safe owned files, updates lockfile, and emits an uninstall receipt. |
| AC-013 | Uninstall receives an unknown skill id | command checks lockfile | command fails before writing with `mutation_performed: false`. |
| AC-014 | Uninstall finds a missing or invalid receipt referenced by lockfile | command validates receipt | command fails before writing and preserves lockfile. |
| AC-015 | Uninstall cleanup succeeds | lockfile is read | unrelated entries are preserved and the target skill entry is removed or marked according to the final design. |
| AC-016 | Cleanup partially fails after mutation begins | command exits | payload reports `status: partial`, `mutation_performed: true`, and lists completed and unresolved actions. |
| AC-017 | Existing PU-009 project install tests run | test suite executes | install behavior, install receipts, and lockfile writes remain compatible. |
| AC-018 | Capability status runs after implementation | `./bin/ask sdk status --json --robot` executes | rollback and uninstall report implemented or partial with evidence; unrelated deferred/out-of-scope capabilities remain honest. |
| AC-019 | Static artifact truth tests run, if required | HTML artifacts are checked | capability status and visual artifact labels do not contradict rollback/uninstall truth. |
| AC-020 | Rollback or uninstall is called with both `--preview` and `--apply`, or with neither mode | command validates arguments | command fails before loading receipts, planning, or writing. |
| AC-021 | Rollback preview is called without `--project-root` | command validates receipt | command emits only a receipt-derived plan and marks live project validation as unavailable. |
| AC-022 | Rollback preview is called with a mismatched `--project-root` | command validates root | command fails before writing with `mutation_performed:false`. |
| AC-023 | Apply targets the live repo, filesystem root, home directory, missing path, file path, or ambiguous relative path | command validates root | command fails before writing with an unsafe-root code and fix suggestion. |
| AC-024 | A planned target path traverses an unmodeled symlink or unsafe hardlink | command validates filesystem identity | command blocks the path and performs no destructive action on it. |
| AC-025 | A case-colliding path alias exists in the target project | command validates filesystem identity | command treats the target as ambiguous unless one identity is proven. |
| AC-026 | A receipt-owned directory contains a user-added entry | cleanup apply runs | command preserves the directory, records it as skipped, and reports manual action. |
| AC-027 | Cleanup is interrupted after file mutation starts | next cleanup command runs | command detects the journal and resumes safely or blocks with recovery instructions. |
| AC-028 | A receipt path is swapped for another schema-valid receipt | rollback or uninstall validates authority | command rejects the receipt because digest/id or lockfile binding does not match. |
| AC-029 | A duplicate active skill id exists in the lockfile | uninstall resolves skill id | command fails as ambiguous unless an install-instance id selects exactly one entry. |
| AC-030 | A blocked cleanup path returns robot JSON | JSON is inspected | payload uses the repository error envelope with stable code, message, fix suggestion, command metadata, and `mutation_performed:false`. |
| AC-031 | `./bin/ask sdk` and `./bin/skills-sdk` run equivalent rollback/uninstall scenarios | outputs are compared | JSON payloads and command metadata are equivalent aside from accepted wrapper identity fields. |
| AC-032 | Capability labels change for rollback or uninstall | artifact truth is checked | capability matrix, status output, and HTML artifacts are updated together or the mismatch is blocked. |

## Validation Plan

| Command | Expected result | Proves | Does not prove |
| --- | --- | --- | --- |
| `./bin/ask sdk status --json --robot` | pass | Local capability truth reports rollback/uninstall status honestly. | Does not prove CI, PR, review, tracker, or merge readiness. |
| `./bin/skills-sdk status --json --robot` | pass | Wrapper parity for capability status. | Does not prove every subcommand wrapper path. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_install.py -q` | pass | PU-009 install behavior remains compatible. | Does not prove rollback/uninstall unless tests are added there. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q` | pass | Temp-project rollback/uninstall behavior and refusal paths. | Does not prove live repo cleanup or external services. |
| `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` | pass | Capability truth and artifact truth stay aligned. | Does not prove CI or browser rendering. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --preview --json --robot` | pass | Receipt-derived rollback preview route works without mutation. | Does not prove live project validation. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot` | pass | Rollback preview validates the target project without mutation. | Does not prove apply writes. |
| `./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot` | pass | Rollback apply performs safe receipt-proven cleanup. | Does not prove uninstall. |
| `./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot` | pass | Uninstall preview route works without mutation. | Does not prove apply writes. |
| `./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot` | pass | Uninstall apply removes safe owned files and updates lockfile. | Does not prove rollback restoration. |
| `./bin/skills-sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot` | pass | Wrapper parity for rollback. | Does not prove every refusal path. |
| `./bin/skills-sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot` | pass | Wrapper parity for uninstall. | Does not prove every refusal path. |
| Negative cleanup command set for missing mode, dual mode, unsafe root, swapped receipt, modified file, symlink, hardlink, directory with user file, duplicate skill id, and interrupted journal | pass | High-risk refusal paths are executable and evidence-bearing. | Does not prove external PR/CI state. |
| `bash scripts/validate-codestyle.sh --fast` | pass or documented pre-existing failure | Repo fast codestyle gate after scoped changes. | Does not prove full PR pipeline. |
| `./bin/ask repo validate --scope=check` | pass or documented pre-existing failure | Repository check lane if runtime-budget gates permit. | Does not prove PR, review, or merge state. |

## Evidence Limits

- This spec is based on local repository evidence only.
- `./bin/ask sdk status --json --robot` proves local SDK status output, not live PR or CI state.
- Temp-project tests prove cleanup safety in controlled project roots, not arbitrary user workspaces.
- HTML artifact updates prove local visual truth only, not hosted documentation or browser rendering unless separately checked.
- GitHub, Linear, CodeRabbit, Codex review, CI, and mergeability are not checked or mutated by this spec stage.

## Risks

| Risk | Mitigation |
| --- | --- |
| Cleanup removes user-modified files. | Require digest match before removal; skip or block modified files with manual action. |
| Rollback restores incorrect overwritten content. | Restore only when before-state evidence exists and validates; otherwise report manual action. |
| Receipt tampering causes unsafe cleanup. | Validate schema, root, path containment, lockfile linkage, and digests before mutation. |
| Partial cleanup leaves inconsistent lockfile state. | Emit partial receipt, preserve unrelated lockfile entries, and update lockfile only after safe steps or record partial state explicitly. |
| Symlink, hardlink, or case-alias paths escape the project root. | Require filesystem identity checks and block ambiguous or unowned targets. |
| Directory pruning removes user content. | Prune only receipt-owned directories that are empty after a fresh content scan. |
| Crashes strand half-mutated cleanup. | Require a cleanup journal before the first mutation and block or resume from journal evidence. |
| Duplicate skill ids target the wrong install instance. | Require install-instance identity or explicit duplicate-active-install refusal. |
| Implementation widens into global/workspace uninstall. | Keep project-root contract as the only mutation authority in PU-010. |
| Status overclaims full lifecycle completion. | Use implemented only for executable proven cleanup; use partial if receipt metadata cannot support all restoration paths. |

## Rollback Plan For This Spec

If the spec is wrong before implementation, revert this file only:

    .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md

If implementation later proves current install receipts are insufficient, preserve this spec as the desired target and plan a narrower compatibility slice that first enriches install receipts without enabling cleanup mutation.

## Blocked Inputs

- None for planning.
- Implementation must decide whether to use separate rollback/uninstall receipt schemas or one discriminated cleanup receipt schema.
- Implementation must decide whether rollback can restore overwritten files from current PU-009 receipts or must mark those paths as manual actions until install receipts store before-content or approved before-state references.
- Implementation must decide the exact receipt identity field name, but it must bind cleanup to digest or immutable id rather than a mutable path label.
- Implementation must decide whether repeated installs of the same skill id are refused at install time or represented with install-instance ids before uninstall can safely target them.
- Implementation must decide the cleanup journal file location under the project root and the recovery behavior for interrupted journals.

## Handoff Notes

- Start from a clean feature worktree because the primary repo currently has local HTML artifact edits.
- Keep PU-010 scoped to project roots and receipt-proven cleanup.
- Prefer a shared cleanup planner that produces the same plan for preview and apply; apply should execute the already validated plan.
- Keep receipt-only rollback preview available, but label it as receipt-derived and not live-validated unless `--project-root` is present.
- Treat rollback and uninstall as high-risk mutation commands even though their target is cleanup.
- Update capability truth only after temp-project tests prove the command behavior.

## Next Stage

Recommended next stage: `sy-plan` for a PU-010 implementation plan.

Suggested plan title:

    PU-010: Receipt-Proven Rollback and Uninstall Lifecycle Implementation Plan
