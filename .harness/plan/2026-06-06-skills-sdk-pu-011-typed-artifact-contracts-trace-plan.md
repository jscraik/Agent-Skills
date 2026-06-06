---
schema_version: 1
artifact_id: sy-trace-plan-2026-06-06-skills-sdk-pu-011-typed-artifact-contracts
artifact_type: sy-trace-plan
canonical_slug: skills-sdk-pu-011-typed-artifact-contracts
harness_stage: sy-trace-plan
title: "PU-011: Skills SDK Typed Artifact Contracts Trace Plan"
status: trace_ready_for_execution_plan
date: 2026-06-06
target_spec: .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md
source_review_artifacts:
  - .harness/review-artifacts/pu-011-adversarial-contract-runtime.md
  - .harness/review-artifacts/pu-011-adversarial-artifact-validation.md
  - .harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime.md
  - .harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts.md
  - .harness/review-artifacts/pu-011-trace-plan-adversarial-contract-runtime-pass2.md
  - .harness/review-artifacts/pu-011-trace-plan-adversarial-validation-artifacts-pass2.md
repo_mutation_scope: trace_artifact_only
external_mutation_status: not_authorized
---

# PU-011: Skills SDK Typed Artifact Contracts Trace Plan

## Decision

Trace PU-011 from the reviewed spec into implementation-ready proof rows. The next execution plan must make the typed artifact contract enforceable across runtime command output, public schemas, Python Pydantic models, Markdown/YAML source artifacts, HTML visual artifacts, fixture provenance, validation scope wiring, and the root package-manager boundary.

The trace keeps install, rollback, and uninstall mutation behavior out of scope. PU-011 hardens the contracts around those surfaces; it must not widen write authority.

## Target

- Spec: `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`
- Review artifacts:
  - `.harness/review-artifacts/pu-011-adversarial-contract-runtime.md`
  - `.harness/review-artifacts/pu-011-adversarial-artifact-validation.md`
- Current SDK truth: `./bin/ask sdk status --json --robot` reports 27 capabilities, 9 implemented, 3 preview-only, 6 deferred, 4 optional placeholders, 1 blocked placeholder, 1 blocked adapter, 3 out of scope, 12 executable or preview-backed rows, and 3 bounded mutation rows.
- Current local state: primary repo is on `main...origin/main` with untracked PU-011 spec/review/trace artifacts.
- External lanes: PR, CI, review-thread, tracker, mergeability, and deployment state were not checked.

## Evidence Checked

| Evidence | Observation | Trace consequence |
| --- | --- | --- |
| `git status --short --branch` | `main...origin/main` with untracked PU-011 spec and review artifacts. | Implementation should start from a clean PU-011 worktree or explicitly stage only PU-011 artifacts. |
| `./bin/ask sdk status --json --robot` | Install, rollback, and uninstall are implemented mutation-capable rows; several registry/trust/signing/adapter lanes remain deferred or placeholder. | Typed artifact work must guard implemented mutation-adjacent surfaces without overclaiming deferred product capabilities. |
| PU-011 spec approved scope | Scope includes Pydantic, JSON Schema helper, Markdown/YAML validation, HTML artifact validation, no-`Any` AST checks, fixtures, validation scope, package-boundary checks, and docs. | Trace rows can map one-to-one to typed contract slices without adding new SDK product behavior. |
| PU-011 spec out of scope | Root package manager, broad refactor, registry, publish, signing, trust, sandbox, mutation semantics, and external readiness are excluded. | Implementation plan must reject scope creep toward publishing or broad model migration. |
| PU-011 adversarial contract-runtime review | Requested envelope coverage, schema/model authority rules, validation changed-file scope, and split source-frontmatter versus manifest projection. | These become P0 trace rows and must be proven before closeout. |
| PU-011 adversarial artifact-validation review | Requested explicit `skills-sdk` validation scope, implementation-notes fixtures, HTML status matrix, package-boundary negative checks, and fixture provenance/freshness. | These become P0/P1 trace rows and acceptance proof gates. |
| PU-011 trace-plan adversarial contract-runtime review | Found missing executable proof for the live robot envelope, uninstall cleanup path, and forbidden root package-manager negative case. | Trace rows and validation commands must name envelope tests, cleanup tests, and package-boundary negative fixtures explicitly. |
| PU-011 trace-plan adversarial validation-artifacts review | Found missing changed-file routing proof, weak implementation-notes fixtures, and generic fixture provenance language. | Trace rows must prove automatic scheduling, required notes content, and the exact fixture origin taxonomy. |
| PU-011 trace-plan adversarial contract-runtime review pass 2 | Found remaining proof-owner gaps for `skills-sdk` scope routing, schema/model parity, root package-manager negative tests, and no-`Any` AST enforcement. | Trace rows and validation commands must name dedicated test files that fail those regressions. |
| PU-011 trace-plan adversarial validation-artifacts review pass 2 | Found remaining ambiguity in fixture provenance storage. | The trace plan must freeze one provenance storage format before execution planning. |
| `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` | First Pydantic models exist for install, cleanup, and lockfile contracts. | Implementation should extend or split this layer rather than creating an unrelated model stack. |
| `Infrastructure/config/schemas/skills-sdk/*.schema.json` | Public schemas exist for current SDK receipts/status/preview/lifecycle surfaces. | Schema/model parity rows must use existing schema files as public compatibility authority. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | Existing pipeline artifact test surface exists. | HTML runtime-vs-visual checks should extend this lane. |
| `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock` | Infrastructure is the Python package boundary. | Root package-manager absence checks must allow Infrastructure package files only. |

## Traceability Map

| ID | Requirement source | Expected behavior | Owner surface | Artifact or task output | Validation command or proof | Status |
| --- | --- | --- | --- | --- | --- | --- |
| TR-001 | FR-001 to FR-003 | Define strict Pydantic boundary models for SDK status, capability rows, robot envelopes, errors, telemetry, receipts, lockfiles, skill source frontmatter, manifest projection, and artifact rows. | `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` or split contract modules | Typed model layer with `extra="forbid"` and object-to-model validators | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_typed_contracts.py -q` | gap |
| TR-002 | FR-004, AC-011, AC-012, AC-018 | Forbid `Any` in public SDK contract and output-envelope modules, including the live robot envelope emitter. | `Infrastructure/tests/test_skills_sdk_no_any_contracts.py`, `Infrastructure/scripts/lib/ask/envelope.py`, SDK contract modules, and any module directly constructing SDK `--json --robot` output | Focused no-`Any` AST validator and negative fixture/module case | `Infrastructure/tests/test_skills_sdk_no_any_contracts.py` fails on `Any` import/annotation in covered modules; `Infrastructure/tests/test_ask_cli_impl.py` proves the live envelope format still validates | gap |
| TR-003 | Contract Authority Rules, FR-027, AC-019 | Establish Pydantic/JSON Schema authority and parity tests for required fields, optional fields, nullability, enums, and extra-key behavior. | `Infrastructure/tests/test_skills_sdk_schema_model_parity.py` plus schema/model fixture pairs | Parity test table for capability status, install receipt, cleanup receipt, lockfile, source frontmatter, manifest projection, cleanup receipt, artifact row, and robot envelope where schema-backed | `Infrastructure/tests/test_skills_sdk_schema_model_parity.py` fails on intentional mismatch fixtures for required fields, enum values, nullability, extra-key behavior, and model/schema required-field disagreement; it passes for current public pairs | gap |
| TR-004 | FR-006 to FR-009, AC-002 to AC-005, AC-013 | Add shared JSON Schema validation helper for real SDK command output and fixture payloads. | `Infrastructure/tests/helpers/schema_validator.py` or SDK library helper | Structured schema validation result with path/message/source diagnostics | Real `ask sdk status`, install/cleanup/lockfile fixtures, and schema drift negative tests | gap |
| TR-005 | FR-008 | Validate real `./bin/ask sdk status --json --robot` output against capability status schema and Pydantic models. | Capability status tests | Runtime status validation test | `./bin/ask sdk status --json --robot` plus focused pytest assertion | gap |
| TR-006 | FR-009 | Validate real or production-constructed check, install, rollback, uninstall, risk, and lifecycle outputs covered by schemas, with install, rollback, and uninstall each receiving named executable proof. | SDK command tests and fixtures, including `Infrastructure/tests/test_skills_sdk_project_cleanup.py` | Runtime output contract tests per command family | Focused pytest builds/runs each payload without mutating live repo; uninstall preview/apply and cleanup receipt semantics are covered by project cleanup tests | gap |
| TR-007 | FR-010, FR-032, FR-033, AC-022 | Add valid/invalid fixtures with provenance/freshness metadata for JSON, YAML, Markdown, implementation notes, and HTML using the approved origins `real_emitter`, `schema_positive`, `schema_negative`, `visual_projection`, and `source_artifact`. | `Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/**/fixture-manifest.json` sidecar manifests plus fixture files | One canonical sidecar manifest per fixture family; embedded or inference-only provenance is out of scope for PU-011 | Fixture validation fails on missing manifest, missing origin, unsupported origin, missing schema version, missing source command or source artifact class, missing static-fixture rationale, or stale source metadata; it passes for accepted sidecar manifests | gap |
| TR-008 | FR-011 to FR-015, AC-006, AC-007 | Validate Markdown/frontmatter for `SKILL.md`, SDK specs, SDK plans, and SDK implementation notes. | Markdown parser/contract tests | Artifact-class-aware Markdown validator | Valid/invalid skill/spec/plan fixtures and current PU-011 spec parse proof | gap |
| TR-009 | FR-015, FR-015A, AC-020 | Add implementation-notes-specific positive and negative fixtures that enforce decisions, changed assumptions, tradeoffs, validation/evidence, and open follow-ups for SDK implementation lanes. | Implementation notes validation tests | Valid `.html` or `.mdx` fixture and invalid fixtures for each required notes element | Notes validator passes valid fixture and fails invalid fixtures with specific diagnostics for the missing required element | gap |
| TR-010 | FR-016 | Validate SDK-relevant YAML metadata/config surfaces with typed models or schema. | YAML contract validator | YAML fixture models and invalid enum/extra-key cases | Valid/invalid YAML fixture tests | gap |
| TR-011 | FR-017 to FR-020, HTML status mapping, missing-row policy, AC-009, AC-010, AC-014 | Cross-check `recommended-skills-sdk-pipeline.html` and lifecycle one-page artifact against runtime `ask sdk status`. | Pipeline artifact tests and DOM parser | Runtime-vs-HTML status validator with status matrix and missing-row classifications | HTML tests fail on deferred row completed marker and pass for current artifacts or intentional coverage omissions | gap |
| TR-012 | FR-021 to FR-023, AC-016, AC-017 | Add explicit `skills-sdk` repo validation scope and preserve unknown-scope failure behavior. | `Infrastructure/scripts/validate_all_impl.sh`, mirrored root wrapper if required, ask repo validate route, `Infrastructure/tests/test_skills_sdk_validation_scope.py`, and `Infrastructure/tests/test_ask_repo_validate.py` | Recognized `skills-sdk` scope, tests for unknown scope, and route proof from `./bin/ask repo validate` into the typed artifact lane | `Infrastructure/tests/test_skills_sdk_validation_scope.py` asserts `skills-sdk` is accepted, selects the typed artifact lane, records the expected check slug, and unknown scopes fail closed; `./bin/ask repo validate --scope=skills-sdk --json --robot` passes | gap |
| TR-013 | FR-024, FR-031, AC-015, AC-021 | Enforce root package-manager boundary structurally with a scratch-copy injection proof. | `Infrastructure/tests/test_skills_sdk_root_package_boundary.py` and validation scope check | Root package-manager absence check allowing `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock` | `Infrastructure/tests/test_skills_sdk_root_package_boundary.py` writes forbidden root `package.json`, lockfile, and root `pyproject.toml` into a temp repo/scratch copy and asserts the `skills-sdk` validation scope fails closed with each file named | gap |
| TR-014 | FR-025 | Preserve install, rollback, uninstall, check, lifecycle, and status behavior except stricter invalid-shape diagnostics. | Existing SDK command tests | Regression run of current SDK test families | Existing install/cleanup/status tests continue to pass | gap |
| TR-015 | FR-026 | Diagnostics distinguish local artifact truth, command-output truth, schema truth, PR/CI truth, and visual artifact truth. | Validation result model or diagnostics | Structured issue fields for truth lane/source | Negative fixture diagnostics include lane and source surface | gap |
| TR-016 | FR-028, FR-029 | Typed artifact validator requires no network and avoids live repo mutation. | Validation runner and tests | No-network/no-live-mutation validation contract | Tests use status/check/preview/temp fixtures only; no live project mutation | gap |
| TR-017 | FR-030 | Document enforcement family ownership: Pydantic, JSON Schema, parser checks, DOM checks, shell checks, package-root checks. | `Docs/agents/02-tooling-policy.md` or SDK doc surface | Documentation update tied to validation lane | Docs lint plus review of command examples | gap |
| TR-018 | Out-of-scope lines 61-68 | Avoid root package manager, broad repo model migration, registry/publish/signing/trust/sandbox, mutation semantic changes, and live project mutation. | Implementation plan scope guard | Non-goals section and changed-file review | Git diff contains only PU-011 contract/validator/doc/fixture surfaces | gap |
| TR-019 | Validation Plan | Run focused and aggregate validation with Infrastructure package boundary. | PR closeout lane | Validation evidence block | Focused pytest, ruff, `ask sdk status`, `ask repo validate --scope=skills-sdk`, codestyle, full repo validate | gap |
| TR-020 | External readiness limits | Keep PR, CI, review-thread, tracker, mergeability, and deployment separate from local proof. | PR green-sweep after implementation PR exists | Closeout lanes report checked vs unchecked external truth | Live PR/CI/review/mergeability checked only after PR opens | out_of_scope_for_trace |
| TR-021 | FR-023 | Prove changed-file routing schedules the `skills-sdk` lane for SDK schemas, contract modules, public envelope/output modules, SDK command modules, SDK tests, SDK specs/plans, SDK implementation notes, and SDK HTML artifacts. | `Infrastructure/scripts/validate_all_impl.sh` changed-file routing and `Infrastructure/tests/test_skills_sdk_validation_scope.py` | Routing table plus changed-file fixture cases for every required SDK file family | `Infrastructure/tests/test_skills_sdk_validation_scope.py` fails if any required changed-file family does not schedule the `skills-sdk` typed artifact lane; unrelated files do not over-schedule it | gap |

## Priority Gaps

| Priority | Gap | Why it matters | Recommended closure stage |
| --- | --- | --- | --- |
| P0 | `skills-sdk` validation scope does not yet exist as a recognized repo validation scope. | The central acceptance command would fail or force undocumented fallback. | `sy-execution-plan` then `sy-work` |
| P0 | Changed-file routing for the `skills-sdk` lane needs executable proof. | Manual scope invocation can pass while ordinary changed-file validation omits the new lane. | `sy-execution-plan` then `sy-work` |
| P0 | Public robot envelope currently needs explicit typed/no-`Any` coverage. | SDK-specific models do not protect the top-level `--json --robot` contract by themselves. | `sy-execution-plan` |
| P0 | Pydantic and JSON Schema parity is not yet enforced. | Two validators can both exist while disagreeing on public contract shape. | `sy-execution-plan` |
| P0 | HTML status mapping and missing-row policy need implementation proof. | Visual maps can overclaim or underclaim runtime capability truth. | `sy-work` |
| P1 | Implementation-notes fixtures are required and not yet covered by the validator. | A declared artifact family would otherwise remain unprotected. | `sy-work` |
| P1 | Fixture provenance/freshness needs deterministic checks. | Static fixtures can drift from real emitters while tests stay green. | `sy-work` |
| P1 | Root package-manager boundary needs a negative check. | The repo can accidentally grow a root package manager despite prose saying not to. | `sy-work` |
| P1 | Fixture provenance storage must use sidecar manifests only. | Mixed embedded, inferred, and sidecar formats would make validators ambiguous across slices. | `sy-execution-plan` |
| P2 | External readiness remains unchecked. | Local trace does not prove PR/CI/review/merge state. | `pr-green-sweep` after implementation PR |

## Recommended Implementation Slices

| Slice | Goal | Trace rows | Stop condition |
| --- | --- | --- | --- |
| S0 | Validation-scope and contract authority design | TR-003, TR-012, TR-018, TR-021 | Execution plan freezes `skills-sdk` scope wiring, schema/model authority rules, changed-file triggers, and non-goals before code. |
| S1 | Typed model and no-`Any` spine | TR-001, TR-002, TR-013 | Pydantic model layer covers public SDK contracts and no-`Any` AST tests include robot envelope/output modules. |
| S2 | Schema/runtime command validation | TR-003, TR-004, TR-005, TR-006, TR-015 | Real SDK status and schema-covered command payloads validate through JSON Schema and Pydantic with structured diagnostics. |
| S3 | Source artifact validators and fixtures | TR-007, TR-008, TR-009, TR-010 | Markdown/YAML/spec/plan/notes fixtures pass/fail with provenance and freshness checks. |
| S4 | HTML runtime-truth validator | TR-011 | Pipeline and lifecycle HTML artifacts are cross-checked against live `ask sdk status` with status matrix and missing-row policy. |
| S5 | Validation wiring, docs, and regression closeout | TR-012, TR-014, TR-016, TR-017, TR-019, TR-021 | `ask repo validate --scope=skills-sdk`, changed-file routing tests, focused tests, lint, codestyle, and full repo validate pass locally. |
| S6 | PR green-sweep after implementation | TR-020 | Live PR status, CI, review comments, CodeRabbit/Codex feedback, and mergeability are checked in the PR lane. |

## Acceptance Coverage Map

| Acceptance | Covered by trace rows | Status |
| --- | --- | --- |
| AC-001 focused validation passes without root package install | TR-012, TR-013, TR-019 | gap |
| AC-002 status output schema/Pydantic validation | TR-005 | gap |
| AC-003 install receipt schema/Pydantic validation | TR-003, TR-004, TR-006 | gap |
| AC-004 cleanup receipt schema/Pydantic validation | TR-003, TR-004, TR-006 | gap |
| AC-005 lockfile schema/Pydantic validation | TR-003, TR-004, TR-006 | gap |
| AC-006 valid `SKILL.md` fixture passes | TR-008 | gap |
| AC-007 invalid `SKILL.md` fixture fails | TR-008 | gap |
| AC-008 YAML fixtures pass/fail | TR-010 | gap |
| AC-009 recommended pipeline HTML matches runtime truth | TR-011 | gap |
| AC-010 lifecycle one-page HTML matches exposed runtime truth | TR-011 | gap |
| AC-011 no-`Any` negative case fails | TR-002 | gap |
| AC-012 no-`Any` positive case passes | TR-002 | gap |
| AC-013 schema/emitter disagreement fails | TR-003, TR-004 | gap |
| AC-014 deferred runtime capability marked completed fails | TR-011 | gap |
| AC-015 no root package manager | TR-013 | gap |
| AC-016 `skills-sdk` validation scope recognized | TR-012 | gap |
| AC-017 unknown validation scope fails closed | TR-012 | gap |
| AC-018 envelope/output `Any` fails | TR-002 | gap |
| AC-019 model/schema disagreement fails | TR-003 | gap |
| AC-020 implementation-notes fixtures pass/fail | TR-009 | gap |
| AC-021 root package file introduction fails | TR-013 | gap |
| AC-022 static fixture lacks provenance fails | TR-007 | gap |
| AC-023 SDK changed-file families schedule typed artifact validation | TR-021 | gap |

## Validation Plan

Focused implementation validation should use the Infrastructure package boundary and repo wrappers:

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

Validation limits:

- Focused tests prove local contract behavior only.
- `ask sdk status` proves runtime status output at command time only.
- HTML artifact validation proves checked static artifacts match current runtime truth; it does not prove hosted publication.
- Local validation does not prove GitHub CI, review-thread state, CodeRabbit/Codex feedback, tracker state, mergeability, or deployment readiness.
- Slices should report `pass`, `fail`, or `blocked` per validation lane and should not collapse those lanes into one readiness claim.

## Trace Gaps To Close Before Work

| Gap | Required decision before implementation |
| --- | --- |
| Scope wiring | Confirm that `skills-sdk` is the dedicated validation scope and update runner allowlists/tests accordingly. |
| Changed-file routing | Define the exact SDK file-family patterns that schedule `skills-sdk` validation and prove each with a validation-runner fixture. |
| Model organization | Decide whether to keep models in `typed_contracts.py` or split into `artifact_contracts.py` and `schema_validation.py`. |
| Schema helper ownership | Decide whether JSON Schema validation helper remains test-only or moves into SDK library code. |
| Markdown parser strategy | Decide whether to use existing dependencies, Python stdlib parsing, or add a small Infrastructure dependency. |
| HTML parser strategy | Decide whether to use Python stdlib/HTMLParser, BeautifulSoup if already available, or a small Infrastructure dependency. |
| Fixture provenance format | Use one sidecar `fixture-manifest.json` per fixture family. Embedded-only provenance and inference-only provenance are out of scope for PU-011. |
| Root package boundary decision file | Decide whether an approved package-root exception is represented by a decision artifact, allowlist, or absence-only rule for PU-011. |

## Risks

| Risk | Mitigation |
| --- | --- |
| The `skills-sdk` validation scope becomes too broad. | Keep the scope focused on SDK contracts, schemas, fixtures, command-output validation, and artifact truth checks. |
| Changed-file routing misses contract drift. | Require fixture cases for every SDK file family in FR-023 and a negative unrelated-file case. |
| No-`Any` enforcement touches too much repo code. | Scope it to public SDK contract/output modules and require explicit allowlist for compatibility shims. |
| Markdown/HTML validators become brittle. | Validate semantic artifact contracts, ids, statuses, and required sections rather than exact prose or layout. |
| Fixture provenance adds ceremony without runtime proof. | Prefer real-emitter fixtures where practical and use provenance only for hand-authored negative or minimized cases. |
| Fixture provenance storage forks between slices. | Require one sidecar `fixture-manifest.json` per fixture family and reject embedded-only or inference-only provenance. |
| Schema/Pydantic parity produces noisy failures. | Start with explicit parity pairs and expand only when a model/schema pair is public and stable. |
| Root package boundary check blocks legitimate future package roots. | Allow only separately approved package-root decision artifacts, out of scope for PU-011. |

## Handoff Notes

Recommended next stage: `sy-execution-plan`.

The execution plan should:

- create a clean PU-011 worktree from current `main`
- stage the spec, two adversarial review artifacts, reviewer manifests, and this trace plan intentionally
- implement `skills-sdk` validation scope before relying on it as proof
- prove changed-file routing schedules the `skills-sdk` lane for every SDK file family named in FR-023
- include `test_skills_sdk_validation_scope.py`, `test_skills_sdk_no_any_contracts.py`, `test_skills_sdk_schema_model_parity.py`, and `test_skills_sdk_root_package_boundary.py` in the first execution slice that claims those surfaces
- include live envelope tests, project cleanup/uninstall tests, and root package-manager negative tests in the first execution slice that claims those surfaces
- use sidecar `fixture-manifest.json` files as the only PU-011 fixture provenance storage format
- keep the root package-manager contract unchanged
- avoid registry, trust, signing, sandbox, publish, and mutation-semantics work
- run the focused validation commands before aggregate validation
- update HTML artifacts only if the new validator proves drift or the implementation intentionally refines coverage metadata
- keep PR/CI/review-thread/tracker/mergeability evidence separate until the PR lane exists

## Evidence Checked

- `sed -n '1,260p' Plugins/synaipse-harness/skills/sy-trace-plan/SKILL.md`
- `sed -n '1,220p' .harness/plan/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-trace-plan.md`
- `sed -n '1,220p' .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`
- `./bin/ask sdk status --json --robot`
- `git status --short --branch`

## Validation

Trace artifact validation in this stage:

- blocked: implementation validation commands were not run because this stage produced a trace plan artifact only.
- blocked: PR, CI, review-thread, tracker, mergeability, and deployment lanes were not checked in this trace-planning run.
