---
schema_version: 1
artifact_id: sy-spec-2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle
artifact_type: sy-spec
canonical_slug: skills-sdk-pu-009-real-project-install-lifecycle
harness_stage: sy-spec
title: "PU-009: Skills SDK Real Project Install Lifecycle Spec"
status: spec_ready_for_plan
date: 2026-06-05
source_previous_spec: .harness/specs/2026-06-04-skills-sdk-pu-008-capability-truth-spec.md
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

# PU-009: Skills SDK Real Project Install Lifecycle Spec

## Command Summary

BLUF: PU-009 moves the Skills SDK install lane from preview-only planning to a real, bounded, project-scoped install lifecycle. The slice must keep preview as the default-safe behavior, add an explicit mutation path, write only inside a validated target project root, emit durable install receipts, update a project lockfile, and update capability truth so the SDK no longer reports real install as merely deferred.

Decision: Build real project install for project scope only. Do not add global installs, workspace installs, registry resolution, marketplace resolution, package signing, trust-store mutation, uninstall execution, or rollback execution in this slice. Rollback and uninstall may receive receipt-backed seed metadata only if that metadata is proven by the install receipt.

Next Action: Hand this spec to sy-execution-plan or the repository's governed planning lane to produce an implementation plan in a fresh PU-009 worktree from current main.

## Purpose

PU-008 made the capability boundary visible: install preview exists, but real install writes do not. PU-009 closes the next largest gap by allowing a user or agent to install a local skill source into a real target project while preserving the SDK's safety posture.

The intended user outcome is a command that can be used against a temporary or explicit project root, writes the expected skill files and lockfile entries, reports exactly what changed, refuses unsafe destinations, and leaves enough receipt data for a later rollback or uninstall slice.

## Problem Statement

The current SDK install command is deliberately read-only. It computes target paths and lockfile deltas, then refuses mutation unless the caller uses preview mode. This is honest, but it leaves the SDK unable to perform the project install lifecycle described by the pipeline artifact.

Without PU-009, agents must either keep treating install as preview-only or bypass the SDK with ad hoc file copies. Bypassing the SDK loses target-root safety, receipt structure, lockfile discipline, and capability truth. PU-009 must provide one safe write path instead of letting every later slice invent its own install behavior.

## Approved Scope

In scope:

- project-scoped install only
- explicit target project root contract
- unsafe or ambiguous destination refusal
- default preview behavior preserved
- explicit mutation flag for real install
- schema-backed install receipt for real writes
- project lockfile write or update
- copy of a local skill source into the project skill root
- write, skipped, and overwritten file accounting
- rollback seed metadata inside the install receipt when it can be proven
- capability matrix and status updates for real_install and lockfile behavior
- temp-project integration tests proving real writes outside the live repo

Out of scope:

- global install writes to the operator home directory
- workspace install writes outside the explicit target project root
- registry, marketplace, or remote package resolution
- package signing
- trust-store mutation
- sandbox execution
- automatic rollback execution
- automatic uninstall execution
- mutation of the live agent-skills repo during tests
- GitHub, Linear, tracker, review-thread, or CI mutation without separate approval

## Current Evidence

| Evidence | Current observation | Spec consequence |
| --- | --- | --- |
| Infrastructure/scripts/lib/ask/commands/sdk.py | sdk install currently accepts --preview and returns an error when --preview is omitted. | PU-009 must add an explicit write flag instead of making omission of --preview mutate. |
| Infrastructure/scripts/lib/ask/skills_sdk/install_preview.py | build_install_preview computes target paths and lockfile delta with mutation_performed false. | Real install should reuse the planning model where possible, then execute a separate write phase. |
| Infrastructure/config/schemas/skills-sdk/install-preview.v1.schema.json | mutation_performed is const false. | Real install requires a separate receipt schema rather than weakening preview truth. |
| Infrastructure/config/schemas/skills-sdk/lockfile-preview.v1.schema.json | lockfile preview reports would_write false. | PU-009 needs a real lockfile write/update contract. |
| Infrastructure/tests/test_skills_sdk_install_preview.py | tests prove preview is schema-valid and does not write watched paths. | PU-009 must preserve these tests and add temp-project mutation tests. |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | real_install, rollback, and uninstall are deferred; lockfile_preview is preview_only. | PU-009 must update real_install truth after proof and only update rollback/uninstall if receipt seed data is implemented. |
| git status --short --branch | main has staged skill-system changes unrelated to PU-009 planning. | Implementation should use a fresh feature branch and worktree to avoid mixing existing staged work. |

## Affected Surfaces

| Surface | Classification | Required action |
| --- | --- | --- |
| Infrastructure/scripts/lib/ask/commands/sdk.py | change | Add explicit install mutation flags and target project root arguments. |
| Infrastructure/scripts/lib/ask/command_metadata.py | change | Register the real install route and robot-mode correction examples. |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | change | Add real install command execution and response envelope data. |
| Infrastructure/scripts/lib/ask/commands/skills.py | change | Add facade export if a new skills_impl function is introduced. |
| Infrastructure/scripts/lib/ask/skills_sdk/install_preview.py | change | Preserve preview behavior; optionally share planning helpers with real install. |
| Infrastructure/scripts/lib/ask/skills_sdk/project_install.py | change | Add target-root validation, install execution, receipt creation, and lockfile update helpers. |
| Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json | change | Add schema for real install receipts. |
| Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json | change | Add schema for written project lockfile if an existing canonical schema is absent. |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | change | Move real_install from deferred to implemented or another honest status supported by the final vocabulary. |
| Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json | change | Permit mutation_performed true only for explicitly write-capable capabilities proven by PU-009, initially real_install. |
| Infrastructure/tests/test_skills_sdk_install_preview.py | change | Preserve no-write preview guarantees and add explicit non-mutation assertions. |
| Infrastructure/tests/test_skills_sdk_project_install.py | change | Add temp-project integration tests for safe real install writes. |
| Infrastructure/tests/test_skills_sdk_capability_status.py | change | Prove capability truth reflects PU-009 without overclaiming rollback or uninstall. |
| bin/skills-sdk | read_only_or_change_if_needed | Confirm wrapper parity for the real install route. |
| skills.lock.json in target projects | generated_runtime_output | Written only inside caller-provided target project roots during real install. |
| .harness/receipts/skills-sdk/install/*.json in target projects | generated_runtime_output | Written only inside target project roots during real install. |
| Primary repo staged skill-system changes | out_of_scope | Do not include in PU-009 implementation commits unless explicitly requested. |
| GitHub, Linear, review threads, CI | not_checked | Do not claim readiness for these lanes unless checked during implementation closeout. |

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | The SDK MUST keep install preview as the default-safe path. |
| FR-002 | The SDK MUST NOT perform install writes when the caller omits the explicit mutation flag. |
| FR-003 | The SDK MUST expose a real project install path using an explicit mutation flag such as --apply. |
| FR-004 | The SDK MUST require an explicit target project root for real install writes. |
| FR-005 | The SDK MUST resolve and validate the target project root before any write occurs. |
| FR-006 | The SDK MUST refuse unsafe project roots, including filesystem root, the operator home directory, missing directories, files, symlinks that escape the resolved root, and ambiguous relative roots. |
| FR-007 | The SDK MUST write only under the resolved target project root. |
| FR-008 | The SDK MUST install local skill sources into the project skill root, initially .agents/skills/<skill-name>. |
| FR-009 | The SDK MUST preserve source files needed for a runnable skill, including SKILL.md and approved optional directories such as agents, references, scripts, and assets. |
| FR-010 | The SDK MUST reject source paths that are not local skill sources with a readable SKILL.md. |
| FR-011 | The SDK MUST reject symlinked source files, symlinked source directories, device files, sockets, FIFOs, and any source path that resolves outside the declared local skill source root. |
| FR-012 | The SDK MUST write or update a project lockfile that records the installed skill identity, source digest, target path, installed files, receipt reference, and schema version. |
| FR-013 | The SDK MUST emit a schema-valid install receipt for every successful real install. |
| FR-014 | The install receipt MUST include files_written, files_skipped, files_overwritten, conflicts, source_digest, target_root, target_paths, lockfile_before_digest, lockfile_after_digest, rollback_metadata, mutation_performed, and acceptance_trace. |
| FR-015 | The real install command MUST report mutation_performed true when any filesystem mutation has occurred, and MUST report status success only after file writes, lockfile update, and receipt write have completed. |
| FR-016 | The real install command MUST fail before writing if validation detects an unsafe root, missing source, unresolved conflict, unsupported scope, unsafe source entry, or missing project marker. |
| FR-017 | The command MUST handle existing target directories with a conservative default: refuse overwrite unless an explicit overwrite policy is provided. |
| FR-018 | The command MUST support an explicit overwrite policy only if the receipt can record overwritten file digests. |
| FR-019 | Real install writes MUST use deterministic ordering and atomic replace for generated JSON files. |
| FR-020 | If any write step fails after mutation begins, the command MUST return a schema-shaped failure payload that reports mutation_performed true, partial writes, and cleanup guidance rather than claiming a clean refusal. |
| FR-021 | Rollback and uninstall MUST remain deferred unless PU-009 implements receipt-backed seed metadata and capability truth labels them honestly. |
| FR-022 | The capability matrix MUST update real_install with evidence from temp-project integration tests after implementation. |
| FR-023 | The capability status schema and validator MUST allow mutation_performed true only for real_install or another explicitly approved write-capable capability. |
| FR-024 | Existing check, preview install, lifecycle placeholder, and status commands MUST remain compatible. |

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | The install receipt and lockfile MUST be deterministic for stable diffs. |
| NFR-002 | The command MUST be safe for agent execution in temp project roots without writing the live repo. |
| NFR-003 | Error output MUST be machine-readable in robot mode and include a concrete fix_suggestion. |
| NFR-004 | The implementation MUST reuse existing SDK planning, digest, and schema validation patterns where practical. |
| NFR-005 | The implementation MUST avoid network access in the default install path. |
| NFR-006 | The implementation MUST keep local code/test truth separate from PR, CI, review, tracker, and merge readiness truth. |

## Target Root Contract

Real install writes require a target project root argument. The recommended CLI shape is:

    ./bin/ask sdk install <local-skill-source> --project-root <path> --apply --json --robot
    ./bin/skills-sdk install <local-skill-source> --project-root <path> --apply --json --robot

The implementation may choose a different flag name during planning, but it must preserve these semantics:

- preview remains the default-safe behavior
- writes require an explicit mutation flag
- real install writes require an explicit target project root
- project scope is the only approved write scope in PU-009
- target roots must resolve to an existing directory
- target roots must contain an accepted project marker before writes; accepted markers are AGENTS.md, .git, .agents, or another marker explicitly approved in the implementation plan
- relative target roots are refused unless the plan defines a deterministic base and tests it
- resolved target paths must stay under the resolved project root
- target roots must not be the filesystem root, the operator home directory, or the live agent-skills repository in automated tests
- the live agent-skills repo must not be used as a write target in automated tests

The no-flag install behavior must remain non-mutating. Planning may keep the current validation error when neither --preview nor --apply is present, or may make no-flag install return the preview payload. Either choice is acceptable only if robot-mode output points to the explicit preview and real-install commands and tests prove no writes occurred.

## Source Copy Contract

Only local skill sources are approved for PU-009. A valid source root is the parent directory of a readable SKILL.md or a directory that directly contains a readable SKILL.md.

The copy planner MUST:

- resolve the source root before planning writes
- reject source roots that do not contain SKILL.md
- reject symlinked files and directories inside the copied source set
- reject device files, sockets, FIFOs, and other non-regular filesystem entries
- include only approved skill runtime surfaces: SKILL.md, agents, references, scripts, assets, and explicitly approved metadata files
- produce a deterministic source manifest and digest before writing
- refuse remote handles, registry identifiers, and network package sources in PU-009

## Receipt Contract

The real install receipt MUST be separate from install-preview.v1. The recommended schema id is skills-sdk.install-receipt.v1.

Minimum receipt fields:

| Field | Requirement |
| --- | --- |
| schema_version | const skills-sdk.install-receipt.v1 |
| schema_uri | versioned schema URI |
| status | success, blocked, or partial |
| operation | install |
| scope | project |
| source_path | original source path label |
| source_digest | digest of source skill files or deterministic source manifest |
| target_root | resolved target project root |
| target_paths | installed target paths relative to target_root |
| files_written | deterministic list of newly written files with digests |
| files_skipped | deterministic list of skipped files with reason |
| files_overwritten | deterministic list of overwritten files with before and after digests |
| conflicts | deterministic list of unresolved conflicts |
| lockfile_path | project-relative lockfile path |
| lockfile_before_digest | digest or null |
| lockfile_after_digest | digest after write |
| rollback_metadata | data sufficient for a later rollback planning command, or explicit unavailable reason |
| mutation_performed | true when any filesystem mutation occurred |
| acceptance_trace | PU-009 acceptance ids |

Failure payloads may use the same receipt shape with status blocked or partial. A blocked payload before mutation MUST report mutation_performed false. A partial-failure payload after mutation begins MUST report mutation_performed true and list partial files written so operators do not mistake it for a clean refusal.

## Lockfile Contract

The project lockfile SHOULD be named skills.lock.json unless planning identifies an existing canonical project lockfile. It MUST be written inside the target project root.

The lockfile MUST include:

- schema_version
- generated_by
- entries keyed by installed skill handle or package name
- source digest
- target path
- receipt reference
- installed_at timestamp or deterministic test override
- installed files and digests

Tests may use a deterministic timestamp override or compare structure without requiring a fixed wall-clock value.

Generated receipt and lockfile JSON MUST be written through temporary files in the target project root and atomically replaced into their final paths when the platform supports atomic replacement.

## Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-001 | A caller runs sdk install with neither --preview nor --apply | command executes in robot mode | the command performs no writes and returns preview or a validation error that points to --preview or --apply. |
| AC-002 | A caller runs sdk install --preview | command executes | existing install-preview schema and no-write tests still pass. |
| AC-003 | A caller runs sdk install --apply without --project-root | command executes | command fails before writing and includes a project-root fix suggestion. |
| AC-004 | A caller passes filesystem root, home directory, a missing directory, or a file as --project-root | command validates root | command fails before writing with mutation_performed false. |
| AC-005 | A caller passes a temp directory without an accepted project marker | command validates root | command fails before writing with mutation_performed false. |
| AC-006 | A caller passes a marked temp project root and a valid local skill source with --apply | command executes | the skill is copied under <project-root>/.agents/skills/<skill-name>. |
| AC-007 | A real install succeeds | receipt is emitted | receipt is schema-valid and records files_written, target_paths, source_digest, lockfile digests, and mutation_performed true. |
| AC-008 | A real install succeeds | lockfile is read | skills.lock.json exists in the target project root and records the installed skill entry. |
| AC-009 | The target path already exists | command runs without overwrite policy | command fails before overwriting and records a conflict. |
| AC-010 | The target path already exists and overwrite is explicitly allowed | command runs | overwritten files are recorded with before and after digests, or planning marks overwrite out of scope and the command refuses it. |
| AC-011 | A source path tries to escape through symlinks or unsafe relative paths | command validates paths | command refuses before writing. |
| AC-012 | A source contains a symlink, device file, socket, FIFO, or unsupported file type | command validates source entries | command refuses before writing. |
| AC-013 | A generated receipt or lockfile is written | tests inspect filesystem state | JSON is valid, deterministic in structure, and written inside the target project root. |
| AC-014 | The public wrapper runs the same install command | command succeeds in a temp project | wrapper output matches the ask sdk install receipt payload. |
| AC-015 | PU-009 implementation updates capability truth | ask sdk status runs | real_install no longer reports deferred and rollback/uninstall remain honestly classified. |
| AC-016 | Capability truth is updated for real_install | schema validation runs | mutation_performed true is accepted only for approved write-capable capabilities and rejected for preview-only or placeholder rows. |
| AC-017 | Existing SDK regression tests run | validation completes | check, preview, lifecycle, schema spine, and status behavior remain compatible. |

## Validation Plan

| Command | Proves | Does not prove |
| --- | --- | --- |
| uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_install.py -q | Real install writes, root refusal, receipt schema, lockfile updates, and wrapper parity in temp projects. | Full repo health or remote CI. |
| uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_install_preview.py Infrastructure/tests/test_skills_sdk_capability_status.py -q | Preview behavior remains read-only and capability truth is updated honestly. | External review or mergeability. |
| uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_check_facade.py Infrastructure/tests/test_skills_sdk_placeholder_lifecycle.py Infrastructure/tests/test_pr_skills_sdk_artifacts.py -q | Existing SDK regression surface remains intact. | Real install behavior beyond covered temp-project cases. |
| ./bin/ask sdk install Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md --preview --json --robot | Preview path remains available from the CLI. | Mutation behavior. |
| ./bin/ask sdk install Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md --project-root <temp-project> --apply --json --robot | Real install path emits a receipt and writes only inside temp-project. | Safety for arbitrary external filesystems. |
| ./bin/ask sdk install Infrastructure/tests/fixtures/skills_sdk/valid_skill/SKILL.md --project-root <unmarked-temp-dir> --apply --json --robot | Root marker refusal prevents accidental writes to arbitrary directories. | All unsafe path variants. |
| ./bin/ask sdk status --json --robot | Capability truth reflects PU-009. | CI, review, tracker, or merge readiness. |
| bash scripts/validate-codestyle.sh --fast | Fast codestyle lane for non-package root changes. | Full validation or mergeability. |
| ./bin/ask repo validate --json --robot | Repo validation contract when the implementation is ready for PR. | Review-thread closure or CI state. |

## Risks

| Risk | Mitigation |
| --- | --- |
| Real install writes escape the intended project root. | Resolve paths, reject unsafe roots, reject escaping symlinks, and test temp-project boundaries. |
| Preview behavior accidentally mutates. | Keep install-preview schema const false and preserve existing no-write tests. |
| Receipt claims success before all writes complete. | Set mutation_performed true only after file writes, lockfile update, and receipt write complete. |
| Lockfile format becomes another unowned artifact. | Version it, schema-test it, and link it from install receipts. |
| Overwrite policy causes data loss. | Default to refuse; only allow overwrite if before digests are recorded and tests prove accounting. |
| Capability truth overclaims rollback or uninstall. | Keep rollback/uninstall deferred unless executable behavior exists. |
| Existing staged main changes contaminate implementation. | Start implementation in a clean PU-009 worktree from current main and stage only PU-009 files. |

## Rollback

Rollback of PU-009 code is ordinary git revert of the implementation branch.

Runtime rollback of installed skills is not guaranteed by this spec. PU-009 receipts must include enough rollback metadata for a later slice to plan rollback, but automatic rollback execution remains out of scope unless it is explicitly implemented and proven during PU-009 planning.

If a temp-project install test writes files, test teardown must remove the temp directory. The implementation must not require cleanup of the live repo.

## Blocked Inputs

No blocker prevents planning. Implementation planning must choose the final CLI flag spelling for real mutation. The recommended contract is --apply plus --project-root.

Owner input is required before expanding beyond project scope, adding global writes, adding registry resolution, or making rollback/uninstall executable in the same slice.

## Next Stage

Recommended next stage: sy-execution-plan or the repository's governed implementation planning lane.

Handoff objective: produce a PU-009 implementation plan for a clean feature branch and worktree that adds real project install writes, install receipts, lockfile updates, capability truth updates, and temp-project integration tests while preserving preview as the default-safe path.
