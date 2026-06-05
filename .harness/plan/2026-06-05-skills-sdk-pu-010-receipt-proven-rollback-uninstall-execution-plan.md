---
schema_version: 1
artifact_id: sy-execution-plan-2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall
artifact_type: sy-execution-plan
canonical_slug: skills-sdk-pu-010-receipt-proven-rollback-uninstall
harness_stage: sy-execution-plan
title: "PU-010: Receipt-Proven Rollback and Uninstall Lifecycle Execution Plan"
status: execution_plan_ready
date: 2026-06-05
source_spec: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md
source_trace_plan: .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md
source_review_artifacts:
  - .harness/review-artifacts/pu-010-adversarial-filesystem-safety.md
  - .harness/review-artifacts/pu-010-adversarial-receipt-lockfile.md
  - .harness/review-artifacts/pu-010-adversarial-cli-tests-status.md
  - .harness/review-artifacts/pu-010-trace-adversarial-coverage.md
  - .harness/review-artifacts/pu-010-trace-adversarial-validation.md
  - .harness/review-artifacts/pu-010-trace-adversarial-slicing.md
source_pipeline_artifact: artifacts/recommended-skills-sdk-pipeline.html
source_lifecycle_artifact: artifacts/skills-sdk-user-lifecycle-one-page.html
origin: user_requested_sy_execution_plan
risk: high
traceability_required: true
repo_mutation_scope: implementation_plan_artifact_only
external_mutation_status: not_authorized
---

# PU-010: Receipt-Proven Rollback and Uninstall Lifecycle Execution Plan

## Command Summary

BLUF: Implement PU-010 as the recovery half of the real project install lifecycle. The first implementation action is not filesystem mutation; it is a frozen cleanup authority decision gate. The next code path should build a shared planning spine that can preview rollback and uninstall, reject unsafe inputs with robot JSON, and prove no writes happen in preview. Destructive apply work must wait until receipt identity, lockfile authority, cleanup receipt shape, and a pre-mutation cleanup journal are in place.

Decision: Use a clean feature worktree for SDK code and tests. Keep the primary checkout as an orientation surface because it currently has local SDK HTML artifact edits plus PU-010 planning and review artifacts. Do not upgrade rollback or uninstall capability truth until temp-project integration proof, wrapper parity, and artifact/status sync all pass in the same implementation lane.

Next Action: Create or refresh a clean worktree from current main, carry only the approved PU-010 spec/trace/execution artifacts if needed, then complete Slice 0 before touching runtime code.

## Stage Contract

schema_version: 1

stage: sy-execution-plan

target: PU-010: Receipt-Proven Rollback and Uninstall Lifecycle

execution_plan: this artifact

next_stage: governed implementation in a feature worktree

## Evidence Checked

| Evidence | Observation | Planning consequence |
| --- | --- | --- |
| .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md | Scope is rollback and uninstall from valid project install receipts. Global cleanup, registry, publishing, trust, signing, sandbox, and live-repo mutation are outside PU-010. | Keep the plan bounded to project-local cleanup and temp-project proof. |
| .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md | Trace rows TR-001 through TR-024 split decisions, CLI, receipt authority, lockfile authority, filesystem safety, journal behavior, status truth, artifacts, and PR closeout. | Use the trace rows as slice acceptance IDs and avoid merging safety concerns into broad buckets. |
| .harness/review-artifacts/pu-010-trace-adversarial-coverage.md | Review required concrete filesystem, journal, receipt, and artifact-sync proof. | Add separate implementation gates for each destructive edge case and truth surface. |
| .harness/review-artifacts/pu-010-trace-adversarial-validation.md | Review required explicit negative commands, wrapper parity, and two-step journal interruption proof. | Validation must include refusal commands and recovery semantics, not only success-path tests. |
| .harness/review-artifacts/pu-010-trace-adversarial-slicing.md | Review required journal-before-mutation sequencing and frozen design decisions before implementation. | Slice 0 blocks later slices until cleanup schema, receipt identity, duplicate install policy, before-state policy, and journal location are decided. |
| UBIQUITOUS_LANGUAGE.md | ask CLI, Feature Worktree, Runtime Projection, and Canonical Skill Source have repo-specific meanings. | Use repo vocabulary and avoid hand-editing runtime projections. |
| Infrastructure/scripts/lib/ask/commands/sdk.py | SDK dispatch is centralized here; current actions include check, install, lifecycle, and status. | Add rollback and uninstall parser branches here, with exact preview/apply mode validation. |
| Infrastructure/scripts/lib/ask/skills_sdk/project_install.py | PU-009 install already owns project-root refusal, path metadata checks, digest helpers, atomic JSON writes, install receipts, and lockfile writes. | Reuse or extract helpers rather than inventing a parallel authority model. |
| Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json | Install receipt schema exists and is the source record for rollback. | Treat existing receipts as authority only when metadata is sufficient; otherwise emit manual actions or partial capability truth. |
| Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json | Lockfile entries point to receipt refs and file records. | Uninstall must resolve through lockfile state and refuse ambiguous duplicate active installs unless a compatible install-instance id is added. |
| Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py | Capability matrix currently treats mutating capability ids as a small allow-list. | Rollback/uninstall status upgrades must include schema/test updates for mutation truth only after apply proof exists. |
| Current git status | Primary checkout is on main with local HTML artifact edits and untracked PU-010 planning/review/agent-run artifacts. | Implementation should occur in a clean feature worktree and stage only intentional PU-010 files. |

## Slice Boundaries

| Slice | Purpose | Primary output | Required proof before next slice |
| --- | --- | --- | --- |
| 0 | Prepare isolated implementation surface and freeze cleanup authority decisions. | Feature worktree plus written decision record in the implementation notes or plan appendix. | Each blocked input from TR-002 has a named decision and owner file before runtime code changes begin. |
| 1 | Build non-mutating cleanup planning spine and CLI route. | rollback/uninstall parsers, shared planner, receipt loader, and robot-mode blocked errors. | Preview and refusal commands pass with mutation_performed false and no project writes. |
| 2 | Bind cleanup authority to receipt and lockfile identity. | Receipt digest/id checks, lockfile lookup/update plan, and cleanup receipt schema choice. | Missing, malformed, stale, swapped, mismatched-root, unknown skill, duplicate skill, missing receipt, and mismatched lockfile commands refuse before writing. |
| 3 | Add cleanup journal foundation before any destructive apply. | Project-local journal or staged-state marker and interruption detection. | Two-step interruption test proves rerun either resumes safely or blocks with recovery payload. |
| 4 | Implement filesystem-safe rollback/uninstall apply. | Cleanup executor that removes/restores only receipt-proven files and preserves user changes. | Temp-project apply tests pass for success, modified files, missing before-state, symlink, hardlink, case alias, directory pruning, and unsafe roots. |
| 5 | Prove CLI parity, status truth, artifacts, and regression safety. | Wrapper parity tests, capability matrix/status update, HTML truth sync, and install regression proof. | Full PU-010 local test matrix, codestyle, status, wrapper, and artifact sync pass or have classified blockers. |
| 6 | Prepare PR handoff and green-sweep lane. | PR-ready branch with validation evidence. | Live PR, CI, review-thread, mergeability, and external feedback lanes are checked only after a PR exists. |

## Files Likely To Change

| Path | Intended change |
| --- | --- |
| Infrastructure/scripts/lib/ask/commands/sdk.py | Add rollback and uninstall subcommands with exact preview/apply/project-root/receipt arguments and mode exclusivity. |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | Add command facade functions that return repository-standard CallResult envelopes for rollback and uninstall. |
| Infrastructure/scripts/lib/ask/skills_sdk/project_install.py | Extract or reuse project-root, digest, receipt, path metadata, lockfile, and atomic JSON helpers where practical. Preserve PU-009 behavior. |
| Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py | Recommended new module for cleanup planning, receipt/lockfile validation, journal handling, safe apply execution, and receipt writing. |
| Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json | Preferred single discriminated cleanup receipt schema unless separate rollback/uninstall schemas prove simpler. |
| Infrastructure/config/schemas/skills-sdk/rollback-receipt.v1.schema.json | Change only if the implementation chooses separate operation-specific schemas. |
| Infrastructure/config/schemas/skills-sdk/uninstall-receipt.v1.schema.json | Change only if the implementation chooses separate operation-specific schemas. |
| Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json | Read as authority; extend only with compatibility-safe identity or before-state fields if current metadata cannot satisfy cleanup proof. |
| Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json | Read/update during uninstall and rollback; extend only if install-instance identity is required and compatibility is explicit. |
| Infrastructure/config/skills-sdk/capability-matrix.v1.json | Move rollback/uninstall from deferred only after proof supports implemented or partial status. |
| Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py | Update mutating capability invariants only if rollback/uninstall have proven apply paths. |
| Infrastructure/tests/test_skills_sdk_project_cleanup.py | New temp-project integration tests for rollback/uninstall preview, apply, refusal, journal, filesystem safety, and receipts. |
| Infrastructure/tests/test_skills_sdk_project_install.py | Preserve PU-009 behavior and add shared-helper regression tests if helpers are extracted. |
| Infrastructure/tests/test_skills_sdk_capability_status.py | Prove capability truth and mutation flags do not overclaim rollback/uninstall. |
| Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py | Prove HTML artifacts and capability matrix/status truth stay aligned. |
| bin/skills-sdk | Confirm wrapper delegation; change only if parity fails because wrapper arguments are incomplete. |
| artifacts/recommended-skills-sdk-pipeline.html | Update green/status visualization only after rollback/uninstall status truth changes. |
| artifacts/skills-sdk-user-lifecycle-one-page.html | Update lifecycle visualization only after rollback/uninstall status truth changes. |
| .harness/implementation-notes/2026-06-04-skills-sdk-v1-0-product-implementation-notes.html | Append implementation decisions and trade-offs if continuing the existing browser-visible notes lane. |

## Files That Must Not Change In This Slice

| Path or surface | Boundary |
| --- | --- |
| .agents/skills/** | Runtime Projection; do not hand-edit. |
| Trust stores, user runtime links, global skill installs | PU-010 is project cleanup only. |
| Registry, marketplace, publishing, signing, sandbox providers, external eval services | Out of scope for this slice. |
| Live agent-skills repository as a cleanup target | Tests and commands must refuse it as an unsafe root. |
| GitHub, Linear, review threads, CI settings | External mutation is outside this plan until PR handoff. |
| Existing local HTML artifact truth edits in primary checkout | Keep separate unless intentionally carried into the PU-010 feature branch as truth-sync work after proof. |

## Slice 0: Worktree Setup And Decision Gate

1. Record the primary checkout state: git status --short --branch.
2. Fetch current main: git fetch origin main.
3. Create the feature worktree from current main:

        git worktree add /private/tmp/agent-skills-skills-sdk-pu-010-receipt-proven-cleanup -b codex/skills-sdk-pu-010-receipt-proven-cleanup origin/main

4. Copy or recreate only the approved PU-010 spec, trace plan, execution plan, and review artifacts into the feature worktree if they are not on main.
5. Write a short implementation decision record before code changes. Required decisions:
   - cleanup receipt schema: one discriminated project-cleanup-receipt.v1 schema or separate rollback/uninstall schemas
   - before-state policy: restore only from inline before-content or approved before-state reference with digest proof; otherwise manual action
   - receipt identity: use receipt digest as minimum authority; add receipt id only if compatible with PU-009 receipts
   - duplicate install policy: refuse duplicate active skill ids unless a compatible install-instance id is added and proven
   - journal path: project-local path under .harness/receipts/skills-sdk/cleanup/ or adjacent .harness/state/skills-sdk/cleanup/, never outside project root
6. Verify the worktree is isolated: git status --short --branch.

Validation:

    git status --short --branch
    rg -n "cleanup receipt schema|before-state policy|receipt identity|duplicate install|journal path" <decision-record>

Stop condition: If a clean feature worktree cannot be created or any required decision remains unresolved, stop before editing runtime code.

Rollback: Remove the worktree and branch only after confirming no intended PU-010 artifacts live solely there.

## Slice 1: Non-Mutating Planning Spine And CLI Routes

1. Add rollback and uninstall parser branches to Infrastructure/scripts/lib/ask/commands/sdk.py.
2. Enforce exactly one mode flag for both commands before loading receipts, lockfiles, planning, or writing.
3. Add facade functions in Infrastructure/scripts/lib/ask/commands/skills_impl.py that return stable CallResult envelopes and place cleanup payloads under operation-specific keys.
4. Create Infrastructure/scripts/lib/ask/skills_sdk/project_cleanup.py with deterministic data models for cleanup source, planned file actions, blocked reasons, manual actions, and command metadata.
5. Implement receipt-only rollback preview:
   - --receipt <path> --preview loads and validates receipt JSON.
   - without --project-root, it emits a receipt-derived plan and marks live project validation unavailable.
   - with --project-root, it runs the same root/path/digest validation as apply without writing.
6. Implement uninstall preview through skills.lock.json in the supplied project root.
7. Add blocked robot JSON for no-mode, dual-mode, missing receipt, invalid root, and unsupported command state with mutation_performed:false.

Validation:

    ./bin/ask sdk rollback --receipt <temp-receipt> --preview --json --robot
    ./bin/ask sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot
    ./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot
    uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q

Stop condition: If the existing ask envelope shape conflicts with the spec's ideal robot JSON, follow the repository envelope and record the exact accepted shape in tests.

Rollback: Revert parser/facade/planner changes and the new cleanup test file from this slice.

## Slice 2: Receipt And Lockfile Authority

1. Implement install receipt validation:
   - readable JSON
   - supported schema version and schema URI
   - operation is install
   - scope is project
   - source status is accepted for cleanup
   - mutation_performed is true for cleanup authority
   - target root matches supplied project root when present
   - installed file records and target paths are internally consistent
2. Compute and bind the source receipt digest. Use it as the minimum immutable authority for rollback and uninstall.
3. Validate receipt-root and lockfile-root identity using resolved project root plus filesystem identity checks.
4. Implement lockfile lookup for uninstall:
   - unknown skill id refuses
   - duplicate active entries refuse unless Slice 0 chose and implemented install-instance identity
   - missing receipt ref refuses
   - receipt ref outside project root refuses
   - lockfile entry files and receipt files must agree before planning apply
5. Add cleanup receipt writer with operation, status, target_root, source receipt, files_removed, files_restored, files_skipped, files_blocked, lockfile changes, mutation_performed, manual_actions, journal, and acceptance_trace.
6. Add or update JSON schemas for cleanup receipts and schema subset tests.

Validation:

    ./bin/ask sdk rollback --receipt <missing-receipt> --preview --json --robot
    ./bin/ask sdk rollback --receipt <malformed-receipt> --preview --json --robot
    ./bin/ask sdk rollback --receipt <swapped-receipt> --apply --project-root <temp-project> --json --robot
    ./bin/ask sdk uninstall <unknown-skill-id> --project-root <temp-project> --preview --json --robot
    uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q

Stop condition: If PU-009 install receipts do not carry enough identity or before-state data for full automatic cleanup, keep rollback/uninstall partial or preview-backed and encode the missing proof instead of widening authority.

Rollback: Remove schema additions and authority checks from this slice; keep Slice 1 only if preview/refusal behavior still passes.

## Slice 3: Journal Foundation Before Mutation

1. Add a cleanup journal or staged-state marker that is written atomically before the first destructive filesystem or lockfile mutation.
2. Store enough data to identify operation, mode, project root identity, source receipt digest, planned action list, completed actions, pending actions, and command metadata.
3. On command start, detect unresolved journals for the same project/receipt/skill and either:
   - resume safely when every completed action can be verified, or
   - block with a recovery payload and mutation_performed reflecting the journal state.
4. Add a test-only interruption hook or injectable executor point so the integration test can stop after journal write and before first mutation.
5. Prove the two-step interruption path: first command writes the journal and interrupts; second command reruns the same cleanup and reports safe recovery or a blocked recovery envelope.

Validation:

    uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q -k journal

Stop condition: If the journal starts becoming a broad transaction engine, reduce it to a staged-state guard that blocks safely with manual recovery details.

Rollback: Remove journal module and tests; do not keep apply mutation code that lacks pre-mutation journal proof.

## Slice 4: Filesystem-Safe Apply Executor

1. Implement rollback apply from a validated install receipt:
   - remove files only when current digest matches installed digest or another explicit safe digest
   - preserve user-modified files as skipped or blocked
   - restore overwritten files only with before-content or approved before-state reference plus digest proof
   - report manual action when before-state proof is absent
2. Implement uninstall apply from lockfile entry plus referenced receipt:
   - remove only files present in both lockfile and receipt authority
   - update skills.lock.json atomically after successful cleanup
   - preserve unrelated lockfile entries
   - report partial state when cleanup cannot fully complete after mutation begins
3. Add filesystem identity checks for each target parent and leaf using canonical resolution and lstat-style metadata checks.
4. Reject or block unmodeled symlink components; remove only receipt-owned symlink artifacts when ownership of the link itself is proven.
5. Reject hardlinked files unless exclusive ownership is proven.
6. Treat case-colliding path variants as ambiguous unless filesystem identity proves the intended target. Platform-gate the test when the filesystem cannot express the case.
7. Prune directories only when receipt/lockfile ownership and fresh emptiness scan prove no unowned entries remain.
8. Refuse unsafe roots, including filesystem root, operator home, live agent-skills repo/worktree, missing path, file path, ambiguous relative path, and roots without project markers.

Validation:

    ./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot
    ./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot
    ./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root /Users/jamiecraik/dev/agent-skills --json --robot
    ./bin/ask sdk uninstall <skill-id> --project-root /Users/jamiecraik/dev/agent-skills --apply --json --robot
    uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py -q

Stop condition: Any case that cannot prove ownership must skip, block, or emit manual action. Do not delete or restore from inference.

Rollback: Revert executor changes while keeping non-mutating planner tests if they remain useful.

## Slice 5: CLI Parity, Status Truth, Artifacts, And Regression Proof

1. Prove ./bin/ask sdk and ./bin/skills-sdk parity for:
   - status
   - rollback preview
   - rollback apply
   - rollback blocked apply
   - uninstall preview
   - uninstall apply
   - uninstall blocked apply
2. Update Infrastructure/config/skills-sdk/capability-matrix.v1.json only after executable proof exists.
3. Update Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py mutating capability invariants only if rollback/uninstall have proven apply paths.
4. Update artifacts/recommended-skills-sdk-pipeline.html and artifacts/skills-sdk-user-lifecycle-one-page.html so their visual truth matches the capability matrix and status JSON.
5. Add or update tests that compare capability matrix rows, ask status output, wrapper status output, and the two HTML artifacts.
6. Run PU-009 install regression tests to prove shared-helper extraction did not break real install.

Validation:

    ./bin/ask sdk status --json --robot
    ./bin/skills-sdk status --json --robot
    ./bin/skills-sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot
    ./bin/skills-sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot
    ./bin/skills-sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot
    ./bin/skills-sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot
    uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py Infrastructure/tests/test_skills_sdk_project_install.py Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q

Stop condition: If rollback or uninstall cannot reach full apply proof, use an honest partial or preview-backed status and make the HTML artifacts show that state instead of marking completion.

Rollback: Revert status/artifact changes first; runtime cleanup code can remain only if its own tests pass and status truth stays honest.

## Slice 6: Final Local Validation And PR Handoff

Run validation from the PU-010 feature worktree in this order:

1. ./bin/ask sdk rollback --receipt <temp-receipt> --preview --json --robot
2. ./bin/ask sdk rollback --receipt <temp-receipt> --preview --project-root <temp-project> --json --robot
3. ./bin/ask sdk rollback --receipt <temp-receipt> --apply --project-root <temp-project> --json --robot
4. ./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --preview --json --robot
5. ./bin/ask sdk uninstall <skill-id> --project-root <temp-project> --apply --json --robot
6. ./bin/skills-sdk status --json --robot
7. uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_project_cleanup.py Infrastructure/tests/test_skills_sdk_project_install.py Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q
8. bash scripts/validate-codestyle.sh --fast
9. ./bin/ask repo validate --json --robot

Closeout must report each lane as pass, fail, or blocked. Local validation does not prove external PR, CI, review-thread, tracker, merge, deployment, registry, marketplace, signing, sandbox, or hosted explorer readiness.

## Review And Green Sweep Handoff

After local validation passes or blockers are classified:

1. Stage only PU-010 feature worktree changes.
2. Commit on the PU-010 feature branch with a conventional commit subject.
3. Push the branch and open a PR.
4. Run the project PR green-sweep lane:
   - live PR status
   - CI checks
   - review comments and threads
   - mergeability
   - CodeRabbit or Codex feedback when present
5. Classify every PR or CI finding as introduced by PU-010, pre-existing, unrelated dirty worktree, or environment/tooling.
6. After merge, pull main back into the primary repo before planning the next capability slice.

## Open Risks

| Risk | Control |
| --- | --- |
| PU-009 install receipts may lack before-state data for automatic restoration. | Restore only with before-state proof; otherwise emit manual actions and mark capability truth honestly. |
| Receipt path could be mistaken for authority. | Bind cleanup to digest/id, schema version, target root identity, and lockfile reference. |
| Duplicate skill ids could uninstall the wrong instance. | Refuse duplicate active entries unless install-instance identity is explicitly added and tested. |
| Journal work could expand into complex transaction machinery. | Keep the first mechanism a small staged-state guard that blocks safely. |
| Filesystem aliasing could escape project ownership. | Use path identity, lstat metadata, symlink, hardlink, case alias, and directory pruning tests. |
| Capability status or HTML artifacts could overclaim cleanup readiness. | Update truth surfaces only after executable proof and artifact/status sync tests pass. |
| Shared helper extraction could regress install. | Run Infrastructure/tests/test_skills_sdk_project_install.py in the same closeout window. |
| Dirty primary checkout could contaminate implementation. | Use a clean feature worktree and stage only intended PU-010 files. |

## Rollback Plan

Rollback is an ordinary git revert of the PU-010 branch or selected slice commits. Because cleanup apply can mutate temp projects during tests, rollback of code changes is separate from test fixture cleanup. The implementation must never target the live agent-skills checkout; any test project state should be under temp directories and disposable.

If a later slice fails:

- revert status and HTML truth updates first to prevent overclaiming
- revert apply executor changes if destructive semantics are unsafe
- keep non-mutating preview/refusal code only when tests still prove it is safe and status truth remains partial or preview-backed
- remove cleanup journal state from temp projects during tests only, never from live repositories

## Completion Criteria

PU-010 implementation is complete when:

- ./bin/ask sdk rollback --receipt <path> --preview --json --robot returns a schema-valid non-mutating plan.
- ./bin/ask sdk rollback --receipt <path> --apply --project-root <path> --json --robot performs receipt-proven rollback in a temp project.
- ./bin/ask sdk uninstall <skill-id> --project-root <path> --preview --json --robot returns a schema-valid non-mutating plan from lockfile plus receipt authority.
- ./bin/ask sdk uninstall <skill-id> --project-root <path> --apply --json --robot performs receipt-proven uninstall in a temp project.
- Missing, stale, tampered, swapped, wrong-root, ambiguous, unsafe-root, symlink, hardlink, case-alias, directory-with-user-file, modified-file, and journal-interruption cases are proven.
- Cleanup receipts list restored, removed, skipped, blocked, lockfile changes, manual actions, mutation truth, source receipt, journal state, and acceptance trace.
- skills.lock.json updates are atomic and preserve unrelated entries.
- ./bin/ask sdk and ./bin/skills-sdk produce equivalent cleanup behavior.
- PU-009 install tests still pass.
- Capability matrix, ask status JSON, wrapper status JSON, and both HTML artifacts agree.
- Repo validation gates either pass or have classified blockers with evidence.

## Next Stage

Recommended next stage: governed implementation in codex/skills-sdk-pu-010-receipt-proven-cleanup using /private/tmp/agent-skills-skills-sdk-pu-010-receipt-proven-cleanup.
