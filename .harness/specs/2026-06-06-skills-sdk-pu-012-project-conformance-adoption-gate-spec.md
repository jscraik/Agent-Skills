---
schema_version: 1
artifact_id: sy-spec-2026-06-06-skills-sdk-pu-012-project-conformance-adoption-gate
artifact_type: sy-spec
canonical_slug: skills-sdk-pu-012-project-conformance-adoption-gate
harness_stage: sy-spec
title: "PU-012: Skills SDK Project Conformance And Adoption Gate Spec"
status: spec_ready_for_review
date: 2026-06-06
source_previous_spec: .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md
source_capability_matrix: Infrastructure/config/skills-sdk/capability-matrix.v1.json
source_v1_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_v1_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
origin: user_requested_next_sdk_slice
risk: medium
ui: false
traceability_required: true
repo_mutation_scope: spec_artifact_only
external_mutation_status: not_authorized
---

# PU-012: Skills SDK Project Conformance And Adoption Gate Spec

## Command Summary

BLUF: PU-012 turns the Skills SDK's project install, rollback, uninstall, lockfile, receipt, status, and typed artifact layers into a read-only project conformance gate. A user or agent should be able to point the SDK at a marked project root and get a schema-valid answer about whether the project is SDK-managed, whether installed skills still match the lockfile and receipts, and whether rollback or uninstall is currently provable.

Decision: Build a read-only project conformance and adoption surface. Add project status and doctor commands that inspect a target project root, validate marker/lockfile/receipt/file state, classify drift, and emit typed JSON receipts. Do not mutate files, repair projects, install skills, roll back, uninstall, publish, sign, call external scanners, or require network access in this slice.

Next Action: Hand this spec to the governed trace/execution planning lane, then implement in the clean PU-012 worktree from current `origin/main`.

## Purpose

PU-012 gives the Skills SDK a project supervision surface. After PU-009 and PU-010, the SDK can install into a project and later clean up from receipts. PU-012 answers the next operator question: is this project still coherent enough for the SDK to trust its own lockfile, receipts, and installed file state?

The slice exists to prevent agents from manually inferring project health from scattered files. It produces a single read-only, schema-valid project conformance receipt.

## Problem Statement

The user/operator problem is that a project can now contain SDK-managed skill files, `skills.lock.json`, install receipts, and cleanup receipts, but there is no canonical command that says whether those artifacts still agree. A user may have edited files, deleted receipts, copied a lockfile, moved a project, or partially cleaned up an install. Without PU-012, agents either overclaim rollback/uninstall readiness or fall back to ad hoc filesystem inspection.

PU-012 must make project health explicit, typed, and testable without performing mutation.

## User / Operator Scenarios

| ID | Scenario | Testable Journey |
| --- | --- | --- |
| SA-001 | Empty marked project | The user runs `ask sdk project status --project-root <marked-temp-project> --json --robot` and receives a schema-valid receipt that says the project is SDK-managed, has no installed skills, and performed no mutation. |
| SA-002 | Healthy installed skill | The user installs a fixture skill into a marked temp project, runs project status, and sees the installed skill classified as healthy with rollback and uninstall readiness proven from lockfile and receipt evidence. |
| SA-003 | Missing project marker | The user points project status at an unmarked temp directory and receives a refusal that explains the project root is unmanaged or unsafe. |
| SA-004 | Broken lockfile | The user supplies a marked temp project with invalid or schema-invalid `skills.lock.json` and receives a failure receipt with lockfile diagnostics instead of a crash. |
| SA-005 | Missing or stale receipt | The user supplies a lockfile entry whose receipt is missing or mismatched and receives a conformance failure that blocks cleanup readiness. |
| SA-006 | File drift after install | The user modifies or removes installed skill files, runs project doctor, and receives issue rows plus manual actions without any automatic repair. |
| SA-007 | Missing project root argument | The user runs project status or doctor without `--project-root` and receives a guided robot error before the SDK reads cwd, parent directories, lockfiles, or receipts. |
| SA-008 | Unsupported or stale lockfile | The user supplies a marked temp project with an unsupported lockfile schema version or stale lockfile metadata and receives explicit lockfile issue codes rather than a generic invalid-lockfile result. |
| SA-009 | Broad marked root | The user accidentally points status at a marked filesystem root, home directory, live repo checkout, or other broad root and receives a refusal before conformance inspection. |
| SA-010 | Moved project identity drift | The user points status at a project whose receipt or lockfile root identity no longer matches the canonical resolved project root and receives a blocked conformance result. |

## Goals

- Provide one canonical read-only project health surface for SDK-managed projects.
- Make lockfile, receipt, and installed-file drift visible to humans and agents.
- Report whether rollback and uninstall are provable before mutation commands run.
- Reuse PU-011 typed contract and schema validation infrastructure.
- Keep project conformance local-only, deterministic, and safe for temp-project integration tests.
- Update SDK capability truth so project conformance is visible as a read-only implemented capability.

## Non-Goals

- Automatic repair, reinstall, rollback, uninstall, or cleanup.
- Trust-store mutation.
- Global installs or workspace-wide scans outside the explicit project root.
- Registry, marketplace, publish, signing, hosted explorer, or remote schema registry behavior.
- Network access.
- Security scanner execution.
- Sandbox execution.
- Skill quality evaluation.
- Changes to existing install, rollback, or uninstall mutation semantics.
- Changes to root package-manager policy.

## Current State / Evidence

| Evidence | Current Observation | PU-012 Consequence |
| --- | --- | --- |
| `./bin/ask sdk --help` | Current actions are `check`, `install`, `rollback`, `uninstall`, `lifecycle`, and `status`. | PU-012 should add a bounded project action or equivalent project subcommands without disturbing existing routes. |
| `./bin/ask sdk status --json --robot` | 27 capability rows are tracked; install, rollback, and uninstall are implemented mutation-capable rows; project conformance is not yet represented. | Add a first-class `project_conformance` capability row with read-only evidence and `mutation_performed: false`. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_install.py` | Real install owns project-root safety, lockfile writes, and install receipts. | Reuse project-root and receipt concepts rather than inventing a second project model. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py` | Rollback and uninstall already require receipt proof. | PU-012 should report cleanup readiness by checking whether proof exists, not by simulating mutation. |
| `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` | Pydantic models exist for SDK receipts and lockfiles. | Add project conformance models here or in a nearby module following the existing typed contract pattern. |
| `Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py` | Shared schema validation exists. | Project conformance output should validate through the same helper. |
| `Infrastructure/tests/test_skills_sdk_project_install.py` and `Infrastructure/tests/test_skills_sdk_project_cleanup.py` | Temp-project lifecycle tests exist. | PU-012 should extend temp-project coverage rather than touching live repo state. |
| Primary repo dirty state | Two generated artifacts are modified on main: skill-review HTML and projection-integrity latest JSON. | PU-012 must be developed in the clean feature worktree and must not stage those primary-worktree artifacts. |
| PU-012 worktree setup | The new worktree requires launch-time `MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml"` plus repo-local `MISE_STATE_DIR`/`MISE_CACHE_DIR`/XDG state paths to avoid sandboxed mise trust and tracked-config warnings. | Validation commands must set trusted-config and state paths before classifying runtime setup failures. |

## Authority and Scope Boundary

| Field | Contract |
| --- | --- |
| requested_depth | approved_slice: PU-012 project conformance and adoption gate only. |
| approved_execution_boundary | Read-only project status and doctor behavior for explicit project roots, plus schemas, typed models, fixtures, tests, and capability truth updates. |
| downscope_authority | User approval is required to remove lockfile validation, receipt validation, installed-file digest checks, or cleanup-readiness reporting from the slice. |
| external_mutation_boundary | No external mutation is authorized. GitHub, Linear, registry, marketplace, scanner, signing, sandbox, and hosted docs writes are outside this spec. |
| freshness_required | Refresh branch state, SDK status, and validation command outcomes before implementation closeout. |
| human_acceptance_boundary | Human acceptance is required before adding any repair, install, rollback, uninstall, signing, registry, sandbox, or network behavior. |

PU-012 has read-only authority over an explicit project root. It may read:

- the project marker used by the SDK install lifecycle
- `skills.lock.json`
- install receipt files referenced by the lockfile
- cleanup receipt files only when discoverable from existing SDK metadata
- installed skill files listed in the lockfile or receipts
- local Skills SDK schemas and typed models

PU-012 may not write, delete, restore, repair, or mutate any project file. It may not infer authority from the current working directory when `--project-root` is missing. It may not scan arbitrary parent directories to discover projects.

`--project-root` is required for both status and doctor. If it is omitted, both commands must stop at argument validation and return a guided robot error without reading cwd, parent directories, project markers, lockfiles, receipts, or installed skill files.

Project-root identity must follow the existing install/cleanup lifecycle invariant: the supplied root must be absolute, existing, strictly resolved, marker-backed, and contained within the intended project boundary before conformance metadata is inspected. Relative paths, nonexistent paths, unresolved symlink aliases, symlink escapes, moved checkouts, and receipt roots whose canonical resolved identity differs from the supplied root must fail closed.

Unsafe broad roots are forbidden even when marker files are present. At minimum, PU-012 must refuse filesystem roots, the operator home directory, the live `agent-skills` repository checkout, ancestor directories of the live repo, and any directory whose resolved identity would cause project status to behave like a broad filesystem audit instead of a bounded SDK-managed project inspection. The implementation should reuse the existing install/cleanup project-root resolver where possible so the root-safety floor does not drift.

## Proposed Behavior

Preferred CLI:

~~~bash
./bin/ask sdk project status --project-root <path> --json --robot
./bin/ask sdk project doctor --project-root <path> --json --robot
./bin/skills-sdk project status --project-root <path> --json --robot
./bin/skills-sdk project doctor --project-root <path> --json --robot
~~~

Acceptable alternative if the command router strongly prefers flat verbs:

~~~bash
./bin/ask sdk project-status --project-root <path> --json --robot
./bin/ask sdk project-doctor --project-root <path> --json --robot
~~~

`status` should produce the conformance summary needed for automation. `doctor` should include the same core receipt plus expanded diagnostics and manual actions. Both commands must remain non-mutating, and the operation-specific output difference must be schema-visible rather than only described in prose.

## Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | The SDK MUST provide a read-only project conformance command for an explicit project root. |
| FR-002 | The command MUST refuse missing, relative, nonexistent, ambiguous, symlink-escaping, or unsafe project roots before reading project metadata deeply. |
| FR-003 | The command MUST never mutate files, lockfiles, receipts, trust stores, or generated artifacts. |
| FR-004 | The command MUST identify whether the project root is SDK-managed according to the existing marker/root contract. |
| FR-005 | The command MUST validate `skills.lock.json` when present and classify missing, invalid, unsupported, or stale lockfile states. |
| FR-006 | The command MUST inspect each lockfile entry and produce one project skill status row per installed skill entry. |
| FR-007 | The command MUST validate referenced install receipts when receipt paths are present. |
| FR-008 | The command MUST classify missing receipts separately from invalid receipts. |
| FR-009 | The command MUST detect receipt/project-root mismatch and report it as a blocking conformance issue. |
| FR-010 | The command MUST detect receipt tampering when digest or schema validation evidence proves mismatch. |
| FR-011 | The command MUST verify installed files listed in receipts or lockfile metadata exist under the project root. |
| FR-012 | The command MUST compare current file digests with expected digests when expected digests are available. |
| FR-013 | The command MUST classify digest mismatches as user-modified or tampered/unknown according to available evidence. |
| FR-014 | The command MUST report rollback readiness per installed skill without performing rollback. |
| FR-015 | The command MUST report uninstall readiness per installed skill without performing uninstall. |
| FR-016 | The command MUST emit a schema-valid project conformance receipt in robot JSON mode. |
| FR-017 | The command MUST use existing SDK typed contract and schema validation patterns. |
| FR-018 | The command MUST update `ask sdk status` capability truth with project conformance evidence. |
| FR-019 | The command MUST preserve existing check, install, rollback, uninstall, lifecycle, and status behavior. |
| FR-020 | The command MUST be covered by temp-project integration tests. |
| FR-021 | The skills-sdk validation scope MUST include a dedicated PU-012 project-conformance validation slug or check. |
| FR-022 | `ask sdk status --json --robot` MUST expose project conformance as a first-class machine-readable `project_conformance` capability row rather than free-text notes. |

## Interfaces

| Interface | Shape | Notes |
| --- | --- | --- |
| Project status CLI | `ask sdk project status --project-root <path> --json --robot` | Read-only compact conformance receipt. |
| Project doctor CLI | `ask sdk project doctor --project-root <path> --json --robot` | Read-only receipt with expanded issues/manual actions. |
| Wrapper parity | `./bin/skills-sdk project status|doctor ...` | Required if the wrapper already delegates generic SDK routes. |
| Capability truth | `ask sdk status --json --robot` | Add a `project_conformance` row with read-only evidence, `mutation_performed: false`, and schema-backed source evidence. |
| Validation scope | `./bin/ask repo validate --scope=skills-sdk --json --robot` | Must schedule an explicit PU-012 validation check, such as `skills-sdk-project-conformance`, in addition to existing typed-artifact checks. |

## Data / Domain Contract

Recommended schema id:

~~~text
skills-sdk.project-conformance-receipt.v1
~~~

Top-level conformance receipt fields:

| Field | Rule |
| --- | --- |
| `schema_version` | const `skills-sdk.project-conformance-receipt.v1` |
| `schema_uri` | versioned local schema URI |
| `operation` | `project_status` or `project_doctor` |
| `project_root_identity` | canonical resolved identity for the inspected absolute, existing, marker-backed project root |
| `mutation_performed` | const false |
| `conformance_status` | `pass`, `warn`, `fail`, or `blocked` |
| `lockfile_status` | structured lockfile classification with explicit status code |
| `skill_statuses` | array of installed skill status rows |
| `issues` | severity-ranked conformance issues |
| `manual_actions` | user actions required before lifecycle commands can be trusted |
| `evidence_refs` | local relative evidence references |
| `acceptance_trace` | PU-012 requirement or acceptance IDs covered by this command path |

`lockfile_status.status` values:

| Value | Conformance Meaning | Required Issue Code When Non-Passing |
| --- | --- | --- |
| `empty_not_installed` | Marked SDK project has no lockfile and no installed skills yet; conformance status should be `pass` with an empty `skill_statuses` array. | none |
| `valid` | Lockfile parses, validates, and matches supported schema/version. | none |
| `missing_with_installed_evidence` | Installed SDK evidence exists but the lockfile is absent. | `missing_lockfile` |
| `invalid_json` | Lockfile cannot be parsed as JSON. | `invalid_lockfile_json` |
| `schema_invalid` | Lockfile JSON parses but fails schema validation. | `invalid_lockfile_schema` |
| `unsupported_version` | Lockfile schema/version is not supported by the running SDK. | `unsupported_lockfile_version` |
| `stale` | Lockfile metadata or entries conflict with current receipt/file evidence. | `stale_lockfile` |

Per-skill status row fields:

| Field | Rule |
| --- | --- |
| `skill_id` | installed skill id or lockfile key |
| `install_status` | `healthy`, `missing_files`, `modified_files`, `missing_receipt`, `invalid_receipt`, `stale_receipt`, `unknown` |
| `receipt_status` | receipt proof state |
| `file_status` | installed file proof state |
| `rollback_ready` | boolean |
| `rollback_blockers` | array of blocker codes |
| `uninstall_ready` | boolean |
| `uninstall_blockers` | array of blocker codes |

Cleanup readiness matrix:

| Receipt/File Proof State | `rollback_ready` | `uninstall_ready` | Required Blocker Codes |
| --- | --- | --- | --- |
| healthy receipt, matching root, matching files | true | true | none |
| `missing_receipt` | false | false | `missing_receipt` |
| `invalid_receipt` | false | false | `invalid_receipt` |
| `stale_receipt` | false | false | `stale_receipt` |
| `receipt_project_root_mismatch` | false | false | `receipt_project_root_mismatch` |
| `tampered_receipt` | false | false | `tampered_receipt` |
| `missing_files` | false | false | `missing_files` |
| `modified_files` | false | false | `modified_files` |
| `tamper_unknown` | false | false | `tamper_unknown` |
| `unknown` proof | false | false | `unknown_proof` |

Readiness may only be true when receipt proof, project-root identity, lockfile state, and installed-file proof all agree. Every non-healthy receipt or file proof state must include at least one explicit blocker code in both readiness blocker arrays.

Operation-specific field contract:

| Operation | Required Detail Level | Schema Rule |
| --- | --- | --- |
| `project_status` | Summary receipt for automation. | Must include `conformance_status`, `lockfile_status`, `skill_statuses`, `issues` summary, `manual_actions` summary, `evidence_refs`, and `acceptance_trace`; issue rows may be compact but must remain typed. |
| `project_doctor` | Diagnostic receipt for remediation planning. | Must include every `project_status` field plus expanded issue diagnostics with severity, code, evidence refs, affected skill/file where known, and manual action text. |
| shared rule | Non-mutation proof. | Both operations must emit `mutation_performed: false` and pass schema validation; making status and doctor byte-identical must fail unless the expanded diagnostic arrays are genuinely empty. |

Conformance rules:

- If `mutation_performed` is not false, schema validation must fail.
- If `--project-root` is omitted, the command must return a guided robot error before any cwd or parent-directory project discovery.
- If the supplied project root is relative, nonexistent, unresolved, symlink-escaping, or not marker-backed, conformance status must be `blocked`.
- If the supplied project root is a filesystem root, the operator home directory, the live repo checkout, a live repo ancestor, or another broad audit root, conformance status must be `blocked` before lockfile or receipt inspection.
- If project root is unmanaged, conformance status must be `blocked`.
- If a marked project has no lockfile and no installed SDK evidence, `lockfile_status.status` must be `empty_not_installed`, `conformance_status` must be `pass`, and `skill_statuses` must be empty.
- If installed SDK evidence exists but the lockfile is absent, `lockfile_status.status` must be `missing_with_installed_evidence` and conformance status must be `fail`.
- If lockfile JSON is invalid, conformance status must be `fail`.
- Unsupported lockfile versions must emit `unsupported_lockfile_version`; stale lockfile evidence must emit `stale_lockfile`; neither may be collapsed into generic invalid-lockfile handling.
- If an installed skill has missing receipt proof, rollback and uninstall readiness must be false.
- If an installed skill has invalid, stale, mismatched, tampered, or unknown receipt proof, rollback and uninstall readiness must be false.
- If installed file digests differ from expected proof, rollback and uninstall readiness must be false unless an existing cleanup rule explicitly proves safety.
- Unknown proof must not be reported as healthy.
- Receipt and lockfile project-root references must compare against the canonical resolved `project_root_identity`; string-normalized but identity-mismatched roots must fail closed.

Deterministic status and exit semantics:

| Class | `conformance_status` | Exit Family | Notes |
| --- | --- | --- | --- |
| Healthy or empty marked project | `pass` | success | Includes `empty_not_installed`. |
| Non-blocking advisory with trusted proof | `warn` | success_with_warnings | Reserved for future advisory-only states; PU-012 should avoid using `warn` unless cleanup readiness remains safely false where needed. |
| Project-state drift after a valid root is accepted | `fail` | validation_failure | Invalid/stale/missing lockfile with installed evidence, missing receipt, invalid receipt, stale receipt, mismatched receipt, missing files, modified files, tamper evidence. |
| Authority or runtime refusal before project inspection | `blocked` | usage_or_environment_blocker | Missing `--project-root`, relative/nonexistent/unsafe/broad root, unmanaged root, symlink escape, identity mismatch that prevents authoritative inspection, unsupported lockfile version, controlled mise setup failure. |

The same fixture must always map to the same `conformance_status` and exit family for both status and doctor. Implementations must not choose between `fail` and `blocked` case-by-case when this table pins the class.

Capability truth contract:

| Field | Contract |
| --- | --- |
| capability id | `project_conformance` |
| status source | project conformance implementation evidence, not prose-only release notes |
| mutation flag | `mutation_performed: false` |
| evidence | schema, typed model, CLI route, temp-project tests, and validation-scope check references |
| failure mode | If the row is missing, hidden in notes, or lacks machine-readable evidence, PU-012 validation fails. |

## Enforcement Contract

| Field | Contract |
| --- | --- |
| essential_decisions | Project conformance is read-only; unknown proof fails closed; cleanup readiness is reported from lockfile and receipt evidence rather than inferred from optimism. |
| fillable_gaps | The execution plan may choose nested `project status/doctor` commands or flat `project-status/project-doctor` verbs if tests prove help output and wrapper parity. |
| guardrails | No mutation, no network, no broad filesystem crawl, explicit project root only, schema-valid receipt output, and temp-project tests only. |
| refusal_triggers | Missing project root, unsafe root, unmanaged root, symlink escape, invalid lockfile, mismatched receipt root, missing receipt, tampered receipt, and unsupported schema version. |
| durable_memory | Encode the durable rule in SDK status, schemas, tests, and validation scope rather than relying on PR prose. |
| professional_output | Robot output must classify status, issues, blockers, manual actions, and evidence refs without leaking secrets or claiming external readiness. |

PU-012 enforcement belongs in deterministic code and validation, not operator memory.

Required enforcement surfaces:

- Pydantic model for project conformance receipt.
- JSON Schema for project conformance receipt.
- CLI robot-output validation test.
- Temp-project fixtures for healthy, unmanaged, invalid lockfile, missing receipt, mismatched receipt, missing file, and modified file states.
- Temp-project fixtures for unsupported lockfile version, stale lockfile state, empty marked project with no lockfile, missing lockfile with installed evidence, broad marked root refusal, moved/canonical identity drift, and omitted-root no-read instrumentation.
- `skills-sdk` validation scope coverage.
- Validation-scope router test proving `skills-sdk-project-conformance` or the chosen PU-012 slug is scheduled by `--scope=skills-sdk`.
- Capability truth row that prevents hidden project-conformance drift.
- Capability matrix/status test requiring the `project_conformance` row with read-only evidence and `mutation_performed: false`.
- No-mutation tests that compare temp-project file inventory before and after status/doctor commands.

## Proof and Runtime Boundary

| Field | Contract |
| --- | --- |
| proof_boundary | Completion is proven by schema-valid command output, typed model tests, temp-project non-mutation tests, SDK regression tests, and skills-sdk scoped validation. |
| non_proof_sources | HTML maps, chat summaries, local confidence, and PR prose do not prove project conformance behavior. |
| runtime_state | PU-012 implementation must run in the clean feature worktree and keep primary-worktree generated artifact drift out of scope. |
| resumption_key | `/private/tmp/agent-skills-skills-sdk-pu-012-project-conformance` on branch `codex/skills-sdk-pu-012-project-conformance`. |
| runtime_invocation_receipt | Record exact command outcomes in the plan/PR once implementation begins. |
| artifact_chain_key | Spec -> trace plan -> execution plan -> implementation branch -> validation receipts -> PR. |
| persistent_artifacts | Spec, plan, schema, typed models, tests, fixtures, status matrix update, and validation logs where repo-owned. |
| live_state_refresh | Refresh `git status`, `ask sdk status`, and validation outputs before claiming closeout. |
| session_evidence_status | Current spec artifact only; implementation evidence remains pending. |

Local proof can establish:

- project status/doctor command behavior
- schema-valid robot output
- non-mutation in temp projects
- lockfile/receipt/file drift classification
- compatibility with existing SDK lifecycle tests
- skills-sdk scoped validation coverage

Local proof cannot establish:

- live PR mergeability
- external CI truth
- CodeRabbit or Codex review state
- production adoption in arbitrary external projects
- hosted docs or registry readiness
- security scanner readiness
- sandbox provider readiness

## Coding and Testing Lenses

| Field | Contract |
| --- | --- |
| coding_lens | Add the smallest read-only SDK project conformance module that reuses project install/cleanup helpers, typed contracts, and schema validation. Keep existing lifecycle command behavior stable. |
| testing_lens | Build temp-project tests for healthy, empty, unmanaged, invalid lockfile, missing receipt, mismatched receipt, missing file, modified file, and no-mutation paths. |

- Reuse existing SDK helper patterns before adding new abstractions.
- Keep project conformance read-only and side-effect tested.
- Prefer typed models and schema validation over ad hoc dictionary assertions.
- Keep fixtures small and explicit.
- Use temp-project integration tests, not the live repo.
- Preserve wrapper parity where existing wrappers already route SDK commands.
- Keep root package-manager policy unchanged.
- Set `MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml"`, `MISE_STATE_DIR`, `MISE_CACHE_DIR`, and `XDG_STATE_HOME` at command launch in temporary worktree validation commands before classifying mise trust or tracked-config warnings.
- Treat any remaining mise trust or tracked-config warning after launch-time env setup as `blocked_environment` or equivalent tooling/setup classification, not as an SDK conformance failure.

## Security, Privacy, and Safety

PU-012 reads local project metadata and installed files under an explicit project root. It must not read secrets intentionally, walk arbitrary parent trees, call network services, or upload evidence. It should report relative evidence paths where possible and avoid leaking local absolute paths in public PR artifacts.

Unsafe project roots, symlink escapes, stale receipts, tampered receipts, and digest mismatches must fail closed. A conformance command must never become a repair or cleanup command by accident.

## Failure and Recovery

| Failure | Required Behavior |
| --- | --- |
| Missing `--project-root` | Return guided robot error; perform no reads beyond argument validation. |
| Relative or nonexistent `--project-root` | Return guided robot error; perform no lockfile, receipt, or installed-file reads. |
| Symlink alias or escaped `--project-root` | Resolve strictly, compare canonical identity, and fail closed when identity or containment is unsafe. |
| Filesystem root, home directory, live repo root, or live repo ancestor | Refuse even when marker files are present; do not treat broad roots as SDK-managed project targets. |
| Moved project or canonical identity drift | Compare canonical resolved root identity against lockfile/receipt authority and block readiness when identities differ. |
| Unmanaged project root | Return blocked/unmanaged classification; perform no mutation. |
| Empty marked project with no lockfile | Return `lockfile_status.status=empty_not_installed`, `conformance_status=pass`, and empty `skill_statuses`. |
| Missing lockfile with installed SDK evidence | Return `missing_lockfile` issue and block cleanup readiness. |
| Invalid lockfile JSON | Return schema-shaped failure with parse diagnostic. |
| Schema-invalid lockfile | Return invalid_lockfile issue with schema evidence. |
| Unsupported lockfile version | Return `unsupported_lockfile_version` issue and block cleanup readiness. |
| Stale lockfile | Return `stale_lockfile` issue and block cleanup readiness. |
| Missing receipt | Return missing_receipt issue and block cleanup readiness. |
| Invalid receipt | Return `invalid_receipt` issue and block cleanup readiness. |
| Stale receipt | Return `stale_receipt` issue and block cleanup readiness. |
| Receipt project-root mismatch | Return receipt_project_root_mismatch and block cleanup readiness. |
| Missing installed file | Return missing_files and manual action guidance. |
| Modified installed file | Return modified_files or tamper_unknown and block unsafe cleanup readiness. |
| MISE trust or tracked-config warning in temp worktree | Retry validation with launch-time `MISE_TRUSTED_CONFIG_PATHS`, `MISE_STATE_DIR`, `MISE_CACHE_DIR`, and `XDG_STATE_HOME`; do not classify as SDK failure until runtime setup is controlled. |

## Validation Plan

Temp-worktree validation commands must be launched with the sandbox-safe mise environment. The examples below show the required prefix inline so the runtime setup is executable, not prose-only:

~~~bash
env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" \
  MISE_STATE_DIR="$PWD/.cache/mise-state" \
  MISE_CACHE_DIR="$PWD/.cache/mise-cache" \
  XDG_STATE_HOME="$PWD/.cache/xdg-state" \
  <validation-command>
~~~

| Command | Proves | Does Not Prove |
| --- | --- | --- |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask sdk project status --project-root <marked-temp-project> --json --robot` | CLI emits project conformance receipt for healthy or empty project. | Live repo safety. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask sdk project doctor --project-root <marked-temp-project> --json --robot` | Doctor output includes issues/manual actions and remains non-mutating. | Automatic repair. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask sdk project doctor --project-root <unsafe-or-drift-fixture> --json --robot` | Doctor rejects unsafe roots and reports drift with expanded typed diagnostics while preserving no-read/no-mutation guarantees. | Status parity by itself. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask sdk project status --json --robot` | Missing `--project-root` fails closed before cwd or parent discovery. | Healthy project behavior. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask sdk project doctor --json --robot` | Missing `--project-root` fails closed before cwd or parent discovery. | Healthy project behavior. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_project_conformance.py -q` | Temp-project conformance cases, strict root identity, broad-root refusal, moved identity drift, unsupported/stale lockfiles, empty-project lockfile semantics, omitted-root no-read instrumentation, operation-specific status/doctor shape, and no-mutation checks. | Full repo validation. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_project_conformance_doctor.py -q` | Doctor parity on broad-root refusal, moved identity drift, unsupported/stale lockfiles, missing/mismatched/invalid/stale receipts, missing files, modified files, expanded diagnostics, and no-mutation behavior. | Compact status behavior. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_project_conformance_status_semantics.py -q` | Deterministic `conformance_status`, exit family, and readiness blocker mappings for every refusal/drift fixture. | Full command routing. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_project_conformance_no_discovery.py -q` | Omitted `--project-root` fails before `Path.cwd()`, parent traversal, marker reads, lockfile reads, receipt reads, or installed-file reads. | Healthy project behavior. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_project_install.py Infrastructure/tests/test_skills_sdk_project_cleanup.py Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_typed_contracts.py -q` | Regression surface for existing SDK lifecycle, capability row, and typed contracts. | External CI or PR review. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" python3 Infrastructure/scripts/validation-and-linting/validate_skills_sdk_typed_artifacts.py --repo-root . --json` | Typed artifact validator still accepts SDK artifacts. | Runtime project conformance logic. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask repo validate --scope=skills-sdk --json --robot` | Scoped SDK validation route schedules the PU-012 slug/check as well as existing SDK checks. | Full repo health. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" python3 -m pytest Infrastructure/tests/test_skills_sdk_validation_scope.py -q` | Validation router test proves the `skills-sdk` scope includes the PU-012 project-conformance check. | Runtime command behavior. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" bash scripts/validate-codestyle.sh` | Repo codestyle and projection gates. | Mergeability or review state. |
| `env MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" MISE_STATE_DIR="$PWD/.cache/mise-state" MISE_CACHE_DIR="$PWD/.cache/mise-cache" XDG_STATE_HOME="$PWD/.cache/xdg-state" ./bin/ask repo validate --json --robot` | Aggregate local validation. | Live CI, CodeRabbit, or Snyk state. |

## Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| VAC-001 | A marked temp project has no lockfile | project status runs | output is schema-valid and reports SDK-managed but no installed skills. |
| VAC-002 | An unmarked temp directory is supplied | project status runs | command refuses with unmanaged/unsafe root classification and no mutation. |
| VAC-003 | A temp project has a valid lockfile and matching install receipt | project status runs | conformance status is pass and the skill row reports rollback/uninstall readiness. |
| VAC-004 | A lockfile references a missing install receipt | project status runs | conformance status is fail and the skill row reports missing_receipt. |
| VAC-005 | A receipt points at a different project root | project status runs | command reports receipt_project_root_mismatch and does not treat cleanup as ready. |
| VAC-006 | An installed file is missing | project status runs | command reports missing_files and blocks rollback/uninstall readiness as appropriate. |
| VAC-007 | An installed file digest differs from proof | project status runs | command reports modified_files or tamper_unknown and blocks unsafe cleanup. |
| VAC-008 | `skills.lock.json` is invalid JSON | project status runs | command returns schema-shaped failure with conformance status fail and does not crash. |
| VAC-009 | `skills.lock.json` is schema-invalid | project status runs | command reports invalid_lockfile with schema validation evidence. |
| VAC-010 | A valid project is inspected through doctor | command runs | output includes manual_actions and issue severity while remaining non-mutating. |
| VAC-011 | Existing install, rollback, uninstall, lifecycle, and status tests run | validation completes | behavior remains compatible. |
| VAC-012 | `ask sdk status` runs after PU-012 | status output includes project conformance with evidence and mutation_performed false. |
| VAC-013 | `./bin/ask repo validate --scope=skills-sdk --json --robot` runs | validation completes | PU-012 conformance coverage is included through an explicit validation slug/check, not only inherited typed-artifact checks. |
| VAC-014 | `--project-root` is omitted | project status and doctor run | each command returns a guided robot error before reading cwd, parent directories, project markers, lockfiles, receipts, or installed files. |
| VAC-015 | A relative path, nonexistent path, symlink alias, or symlink escape is supplied | project status runs | command resolves root identity strictly and fails closed before trusting lockfile or receipt state. |
| VAC-016 | `ask sdk status` runs after PU-012 | status output includes a first-class `project_conformance` capability row with schema-backed evidence rather than free-text notes. |
| VAC-017 | `Infrastructure/tests/test_skills_sdk_validation_scope.py` runs | validation completes | the `skills-sdk` scope schedules the PU-012 project-conformance check. |
| VAC-018 | A marked temp project has no lockfile and no installed SDK evidence | project status runs | `lockfile_status.status` is `empty_not_installed`, `conformance_status` is `pass`, and `skill_statuses` is empty. |
| VAC-019 | Installed SDK evidence exists but `skills.lock.json` is missing | project status runs | command emits `missing_lockfile` and blocks rollback/uninstall readiness. |
| VAC-020 | `skills.lock.json` uses an unsupported schema/version | project status runs | command emits `unsupported_lockfile_version` and blocks cleanup readiness. |
| VAC-021 | Lockfile metadata or entries are stale relative to receipt/file evidence | project status runs | command emits `stale_lockfile` and blocks cleanup readiness. |
| VAC-022 | A marked filesystem root, home directory, live repo checkout, or live repo ancestor is supplied | project status runs | command refuses the broad root before lockfile or receipt inspection. |
| VAC-023 | A moved project or canonical identity drift fixture is supplied | project status runs | command reports root identity mismatch and does not treat cleanup as ready. |
| VAC-024 | `--project-root` is omitted under an instrumented no-discovery harness | project status and doctor run | tests prove the refusal happens before cwd lookup, parent traversal, marker reads, lockfile reads, receipt reads, or installed-file reads. |
| VAC-025 | Status and doctor inspect the same project | both commands run | both share the core receipt, doctor includes expanded typed diagnostics/manual actions, and schema validation fails if the operation-specific shape contract is not met. |
| VAC-026 | Receipt proof is missing, invalid, stale, mismatched, tampered, or unknown | project status and doctor run | rollback_ready and uninstall_ready are false and both blocker arrays include the specific receipt blocker code. |
| VAC-027 | Broad roots, moved identity drift, unsupported/stale lockfiles, invalid/stale receipts, missing/mismatched receipts, missing files, or modified files are inspected through doctor | project doctor runs | doctor enforces the same refusal/drift outcome as status and adds expanded typed diagnostics/manual actions without mutation. |
| VAC-028 | Each refusal or drift fixture is exercised | status and doctor run | `conformance_status` and exit family match the deterministic status table exactly. |

## Visual References / Diagrams

```mermaid
flowchart LR
  User["User or agent"] --> CLI["ask sdk project status/doctor"]
  CLI --> Root["Project root marker check"]
  Root --> Lock["skills.lock.json validation"]
  Lock --> Receipts["Install receipt validation"]
  Receipts --> Files["Installed file digest checks"]
  Files --> Receipt["Project conformance receipt"]
  Receipt --> Status["ask sdk status project_conformance row"]
```

## Evidence and References

| Reference | Purpose |
| --- | --- |
| `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md` | Previous slice and typed artifact foundation. |
| `.harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md` | Cleanup readiness and receipt proof boundary. |
| `.harness/specs/2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle-spec.md` | Project install, lockfile, and receipt source of truth. |
| `.harness/specs/2026-06-04-skills-sdk-pu-008-capability-truth-spec.md` | Capability truth status vocabulary. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_install.py` | Existing project install behavior to inspect and reuse. |
| `Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py` | Existing rollback/uninstall proof model to inspect and reuse. |
| `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` | Pydantic model home for SDK public contracts. |
| `Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py` | JSON Schema helper from PU-011. |
| `Infrastructure/tests/test_skills_sdk_project_install.py` | Temp-project install proof surface. |
| `Infrastructure/tests/test_skills_sdk_project_cleanup.py` | Temp-project cleanup proof surface. |

## Rollback Plan

Rollback is ordinary git revert of the PU-012 branch. Because PU-012 is read-only, rollback should remove only the project conformance route, receipt schema/model additions, tests, validation wiring, and capability truth updates.
