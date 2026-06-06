---
schema_version: 1
artifact_id: sy-execution-plan-2026-06-06-skills-sdk-pu-011-typed-artifact-contracts
artifact_type: sy-execution-plan
canonical_slug: skills-sdk-pu-011-typed-artifact-contracts
harness_stage: sy-execution-plan
title: "PU-011: Skills SDK Typed Artifact Contracts Execution Plan"
status: execution_ready_for_sy_work
date: 2026-06-06
target_tracker_plan: .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-tracker-plan.md
target_trace_plan: .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md
target_spec: .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md
repo_mutation_scope: execution_plan_artifact_only
external_mutation_status: not_authorized
---

# PU-011: Skills SDK Typed Artifact Contracts Execution Plan

## Decision

Implement PU-011 in a clean feature worktree as a bounded contract-hardening slice. The implementation must make Skills SDK artifact truth enforceable across Pydantic models, JSON Schema validation, Markdown/YAML source artifacts, HTML status artifacts, validation-scope routing, no-`Any` enforcement, fixture provenance, and the root package-manager boundary.

This plan does not authorize tracker mutation, PR creation, external service mutation, registry/publish/signing/trust/sandbox work, or new SDK mutation semantics.

## Worktree And Branch

- Worktree: `/private/tmp/agent-skills-skills-sdk-pu-011-typed-artifact-contracts`
- Branch: `codex/skills-sdk-pu-011-typed-artifact-contracts`
- Base: current `origin/main`
- Source artifacts to carry intentionally:
  - `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`
  - `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`
  - `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-tracker-plan.md`
  - `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-execution-plan.md`
  - PU-011 adversarial review artifacts under `.harness/review-artifacts/`
  - PU-011 reviewer manifests under `artifacts/agent-runs/`

Stop if the primary repo has unexpected tracked-file edits before creating the worktree. Preserve existing untracked PU-011 artifacts; do not fold unrelated local artifacts into the branch.

## Execution Slices

| Slice | Tracker tasks | Outcome | Primary files | Validation gate | Stop condition |
| --- | --- | --- | --- | --- | --- |
| S0 | T01 | Clean implementation lane exists and planning artifacts are preserved intentionally. | Git worktree plus `.harness/**` PU-011 artifacts | `git status --short --branch`; `git worktree list` | Stop if the branch cannot be created from current `origin/main` or if unrelated dirty state would be staged. |
| S1 | T02, T10 | `skills-sdk` validation scope exists, changed-file routing schedules it, unknown scopes fail closed, and root package boundary has scratch negative proof. | `Infrastructure/scripts/validate_all_impl.sh`, root wrapper if mirrored, `Infrastructure/tests/test_skills_sdk_validation_scope.py`, `Infrastructure/tests/test_skills_sdk_root_package_boundary.py`, `Infrastructure/tests/test_ask_repo_validate.py` | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_validation_scope.py Infrastructure/tests/test_skills_sdk_root_package_boundary.py Infrastructure/tests/test_ask_repo_validate.py -q`; `./bin/ask repo validate --scope=skills-sdk --json --robot`; unknown-scope negative check | Stop if the scope only aliases broad validation or if root package negative fixtures mutate the live repo. |
| S2 | T03, T04 | Typed Pydantic spine and focused no-`Any` AST enforcement cover public SDK contracts and the live robot envelope path. | `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py`, optional local split modules, `Infrastructure/scripts/lib/ask/envelope.py`, `Infrastructure/tests/test_skills_sdk_typed_contracts.py`, `Infrastructure/tests/test_skills_sdk_no_any_contracts.py`, `Infrastructure/tests/test_ask_cli_impl.py` | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_typed_contracts.py Infrastructure/tests/test_skills_sdk_no_any_contracts.py Infrastructure/tests/test_ask_cli_impl.py -q`; Ruff over SDK contract modules and envelope module | Stop if no-`Any` enforcement expands beyond public SDK contract/output modules without a documented reason. |
| S3 | T05, T06 | JSON Schema helper validates real SDK payloads and schema/model parity has negative fixtures. | `Infrastructure/tests/helpers/schema_validator.py`, `Infrastructure/tests/test_skills_sdk_schema_model_parity.py`, `Infrastructure/tests/test_skills_sdk_schema_spine.py`, `Infrastructure/tests/test_skills_sdk_capability_status.py`, `Infrastructure/tests/test_skills_sdk_project_cleanup.py`, relevant SDK command emitters only if validators expose drift | `./bin/ask sdk status --json --robot`; `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_schema_model_parity.py Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_project_cleanup.py -q` | Stop if schema and emitter disagree and the fix would change public behavior beyond stricter invalid-shape diagnostics. |
| S4 | T07, T08 | Markdown, YAML, implementation-notes, and fixture provenance contracts are enforced with sidecar manifests. | `Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/**`, source artifact validator module or tests, `Infrastructure/tests/test_skills_sdk_typed_contracts.py`, `Infrastructure/tests/test_skills_sdk_schema_spine.py`, a dedicated source-artifact test file if created | Focused pytest for typed contracts, schema spine, and the dedicated source-artifact/provenance tests created by the slice | Stop if validators impose a universal Markdown shape on non-SDK artifact classes or if provenance uses embedded-only or inference-only storage. |
| S5 | T09 | HTML capability/status artifacts are checked against runtime SDK status without treating visual artifacts as authority. | `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py`, `artifacts/recommended-skills-sdk-pipeline.html`, `artifacts/skills-sdk-user-lifecycle-one-page.html` | `./bin/ask sdk status --json --robot`; `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q` | Stop if fixing an HTML artifact would overclaim runtime capability truth or if runtime status cannot be read. |
| S6 | T11, T12 | Docs/evidence boundaries are updated and focused plus aggregate local validation has explicit outcomes. | SDK docs or `Docs/agents/02-tooling-policy.md` when touched, validation evidence notes, all changed implementation files | Focused PU-011 pytest block, Ruff, `./bin/ask sdk status --json --robot`, `./bin/ask repo validate --scope=skills-sdk --json --robot`, `bash scripts/validate-codestyle.sh`, `./bin/ask repo validate --json --robot` | Stop on first required gate failure and classify it as introduced, pre-existing, unrelated dirty worktree, or environment/tooling. |
| S7 | T13 | PR handoff is ready after implementation validation, but external readiness is kept separate. | Git branch, PR template, validation notes | `git status --short --branch`; repo PR template read; PR green-sweep commands only after PR creation is authorized | Stop before push/PR if user has not authorized delivery actions in that stage. |

## Detailed Implementation Notes

### S1: Validation Scope First

Implement `skills-sdk` as a real validation scope before relying on it.

Required behavior:

- `Infrastructure/scripts/validate_all_impl.sh --scope skills-sdk` is accepted.
- `./bin/ask repo validate --scope=skills-sdk --json --robot` forwards into that scope.
- Unknown scopes still fail closed with existing error semantics.
- Changed-file routing schedules the typed artifact lane for:
  - `Infrastructure/config/schemas/skills-sdk/**`
  - `Infrastructure/scripts/lib/ask/skills_sdk/**`
  - `Infrastructure/scripts/lib/ask/envelope.py`
  - SDK command emitters under `Infrastructure/scripts/lib/ask/commands/**`
  - SDK tests under `Infrastructure/tests/test_skills_sdk*.py`
  - SDK specs and plans under `.harness/specs/*skills-sdk*.md` and `.harness/plan/*skills-sdk*.md`
  - SDK implementation notes under `.harness/implementation-notes/*skills-sdk*`
  - SDK HTML artifacts under `artifacts/*skills-sdk*.html`
- Unrelated file fixtures should not schedule the scope.

Root package boundary proof must use scratch/temp injection only. Never create forbidden root manifests in the live repo.

### S2: Typed Contract And No-`Any` Spine

Prefer extending `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` unless the module becomes hard to scan. If splitting, keep names local and obvious, such as:

- `Infrastructure/scripts/lib/ask/skills_sdk/artifact_contracts.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py`

Model families must cover:

- SDK robot envelope, error, metadata, telemetry, and JSON-compatible aliases
- capability status and capability row
- skill source frontmatter
- manifest projection
- install receipt
- cleanup receipt
- lockfile
- artifact status row
- Markdown/YAML artifact contract rows where useful

Use strict model behavior for public contracts. Boundary validators should accept `object` and narrow through Pydantic.

No-`Any` enforcement is scoped. It should cover public SDK contract/output modules and `Infrastructure/scripts/lib/ask/envelope.py`, not the whole repo.

### S3: Schema And Runtime Output Proof

Create a shared JSON Schema validation helper that returns structured diagnostics with:

- schema path
- payload source
- JSON path or equivalent location
- message
- status
- truth lane/source surface

Schema/model parity must include negative fixtures for:

- missing required field
- unsupported enum
- nullability mismatch
- extra-key behavior mismatch
- model requires a field schema allows absent, or schema requires a field model allows absent

Real or production-constructed command payload validation must cover status, check, install, rollback, uninstall, risk, and lifecycle surfaces where schemas exist. Use temp-project tests for mutation-adjacent flows.

### S4: Source Artifacts And Fixture Provenance

Markdown validation is artifact-class aware. Do not enforce one global heading layout.

Minimum artifact classes:

- `SKILL.md`
- SDK specs
- SDK plans
- SDK implementation notes
- YAML metadata/config fixtures where present

Implementation notes must cover:

- decisions
- changed assumptions
- tradeoffs
- validation/evidence
- open follow-ups

Fixture provenance storage is fixed for PU-011:

- one `fixture-manifest.json` sidecar per fixture family
- accepted origins only: `real_emitter`, `schema_positive`, `schema_negative`, `visual_projection`, `source_artifact`
- static fixtures must record schema version, source command or source artifact class, and static-fixture rationale
- embedded-only provenance and inference-only provenance are outside this slice

### S5: HTML Runtime Truth

Runtime `ask sdk status` is authority. HTML artifacts are projections.

Validator behavior:

- Broad pipeline map should include every runtime capability id unless it declares narrower coverage.
- Lifecycle one-page may omit non-user-facing rows, but must not contradict exposed runtime truth.
- Visual completed markers are allowed for implemented rows and carefully labelled preview rows only.
- Deferred, placeholder, blocked, and out-of-scope runtime rows must not show completed markers.

Only edit HTML artifacts when the validator proves drift or needs explicit coverage metadata.

## Files Likely To Change

- `Infrastructure/scripts/validate_all_impl.sh`
- root validation wrapper only if it mirrors the Infrastructure implementation
- `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py`
- optional SDK local split modules under `Infrastructure/scripts/lib/ask/skills_sdk/`
- `Infrastructure/scripts/lib/ask/envelope.py`
- `Infrastructure/scripts/lib/ask/commands/sdk.py` only if command output shape drift is proven
- `Infrastructure/tests/helpers/schema_validator.py`
- `Infrastructure/tests/test_skills_sdk_validation_scope.py`
- `Infrastructure/tests/test_skills_sdk_no_any_contracts.py`
- `Infrastructure/tests/test_skills_sdk_schema_model_parity.py`
- `Infrastructure/tests/test_skills_sdk_root_package_boundary.py`
- `Infrastructure/tests/test_skills_sdk_typed_contracts.py`
- `Infrastructure/tests/test_skills_sdk_schema_spine.py`
- `Infrastructure/tests/test_skills_sdk_capability_status.py`
- `Infrastructure/tests/test_skills_sdk_project_cleanup.py`
- `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py`
- `Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/**`
- `artifacts/recommended-skills-sdk-pipeline.html` only if validation proves drift or missing coverage metadata
- `artifacts/skills-sdk-user-lifecycle-one-page.html` only if validation proves drift or missing coverage metadata
- SDK docs or `Docs/agents/02-tooling-policy.md` when needed
- PU-011 planning and review artifacts under `.harness/**` and `artifacts/agent-runs/**`

## Files That Must Not Change Without A New Decision

- root `package.json`
- root `package-lock.json`
- root `pnpm-lock.yaml`
- root `yarn.lock`
- root `pyproject.toml`
- root Python lockfiles
- registry, publish, signing, trust-store, sandbox, marketplace, or hosted explorer implementation files
- unrelated skills, plugins, docs, and generated artifacts outside PU-011 evidence
- live project install targets outside temp-project tests

## Validation Commands

Focused validation for implementation closeout:

```bash
git status --short --branch
env UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache \
  XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache \
  XDG_STATE_HOME=/private/tmp/agent-skills-xdg-state \
  MISE_CACHE_DIR=/private/tmp/agent-skills-mise-cache \
  MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" \
  uv run --project Infrastructure --locked --group test python -m pytest \
  Infrastructure/tests/test_ask_cli_impl.py \
  Infrastructure/tests/test_ask_repo_validate.py \
  Infrastructure/tests/test_skills_sdk_validation_scope.py \
  Infrastructure/tests/test_skills_sdk_no_any_contracts.py \
  Infrastructure/tests/test_skills_sdk_schema_model_parity.py \
  Infrastructure/tests/test_skills_sdk_root_package_boundary.py \
  Infrastructure/tests/test_skills_sdk_typed_contracts.py \
  Infrastructure/tests/test_skills_sdk_schema_spine.py \
  Infrastructure/tests/test_skills_sdk_capability_status.py \
  Infrastructure/tests/test_skills_sdk_project_cleanup.py \
  Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py \
  -q

env UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache \
  MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" \
  uv run --project Infrastructure --locked --group lint ruff check \
  Infrastructure/scripts/lib/ask/skills_sdk \
  Infrastructure/scripts/lib/ask/envelope.py \
  Infrastructure/tests

./bin/ask sdk status --json --robot
./bin/ask repo validate --scope=skills-sdk --json --robot
bash scripts/validate-codestyle.sh
./bin/ask repo validate --json --robot
```

Record each command as `pass`, `fail`, or `blocked` with exact output summary and ownership classification.

## Rollback And Recovery

- If validation-scope wiring breaks full validation, revert only the `skills-sdk` scope additions and associated tests, leaving planning artifacts intact.
- If schema/model parity exposes real contract drift, stop and choose deliberately between schema migration and emitter fix; add a regression fixture either way.
- If no-`Any` enforcement requires broad envelope surgery, stop and narrow to compatibility aliases/models for public SDK output only.
- If HTML validation proves artifact drift, update only the status/coverage metadata needed to match runtime truth.
- If root package boundary tests require live root manifest writes, reject that approach and use temp/scratch injection instead.
- If aggregate validation fails on pre-existing unrelated lanes, classify the failure and keep PU-011 evidence separate from repo-wide readiness.

## Handoff Checklist For Sy Work

- Create the clean feature worktree and branch named above.
- Carry PU-011 planning/review artifacts intentionally.
- Implement S1 before relying on `ask repo validate --scope=skills-sdk`.
- Add the four named proof-owner test files before claiming scope/no-`Any`/parity/package-boundary closure.
- Keep fixture provenance in sidecar `fixture-manifest.json` files only.
- Use temp-project or scratch-copy tests for mutation-adjacent behavior.
- Keep PR/CI/review-thread/tracker/mergeability evidence out of local validation claims.
- Do not add a root package manager.

## Evidence Checked

- `sed -n '1,300p' Plugins/synaipse-harness/skills/sy-execution-plan/SKILL.md`
- `git status --short --branch`
- `sed -n '1,220p' .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-tracker-plan.md`
- `sed -n '1,280p' .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`
- `sed -n '1,220p' .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`

## Validation

Execution-plan validation in this stage:

- pass: source skill contract was loaded from `Plugins/synaipse-harness/skills/sy-execution-plan/SKILL.md`.
- pass: tracker plan was read from `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-tracker-plan.md`.
- pass: trace plan was read from `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`.
- pass: spec was read from `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`.
- blocked: implementation validation commands were not run because this stage produced an execution-plan artifact only.
- blocked: external tracker, PR, CI, review-thread, mergeability, and deployment lanes were not checked.

## Open Risks

- The named proof-owner test files are plan targets; they still need implementation.
- The `skills-sdk` validation scope is not a current passing lane until S1 lands.
- The exact schema for `fixture-manifest.json` sidecars is left to S4, but the storage format is fixed.
- Local implementation validation will not prove GitHub CI, PR review, tracker state, or mergeability.

## Next Stage

Recommended next stage: `sy-work` in the clean feature worktree.

