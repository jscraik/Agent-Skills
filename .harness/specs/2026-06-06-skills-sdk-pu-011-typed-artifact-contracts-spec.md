---
schema_version: 1
artifact_id: sy-spec-2026-06-06-skills-sdk-pu-011-typed-artifact-contracts
artifact_type: sy-spec
canonical_slug: skills-sdk-pu-011-typed-artifact-contracts
harness_stage: sy-spec
title: "PU-011: Skills SDK Typed Artifact Contracts Spec"
status: spec_ready_for_plan
date: 2026-06-06
source_previous_spec: .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md
source_capability_matrix: Infrastructure/config/skills-sdk/capability-matrix.v1.json
source_v1_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_v1_plan: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
origin: user_requested_sy_spec
risk: medium
ui: false
traceability_required: true
repo_mutation_scope: spec_artifact_only
external_mutation_status: not_authorized
---

# PU-011: Skills SDK Typed Artifact Contracts Spec

## Command Summary

BLUF: PU-011 turns the Skills SDK's growing artifact set into typed, deterministic contracts across Python, JSON, JSON Schema, Markdown, YAML, HTML, shell, and Node-adjacent surfaces. The slice must validate real SDK command output, source artifacts, generated visual maps, and public contract modules without adding a root package manager or widening SDK mutation authority.

Decision: Build typed boundary enforcement for SDK artifacts. Use Pydantic under `Infrastructure/pyproject.toml` for Python-owned runtime models, JSON Schema for public automation contracts, Markdown/YAML parsers for source artifacts, DOM checks for HTML evidence artifacts, and focused AST tests for public SDK contract modules. Do not rewrite internal SDK logic, add a root `package.json`, add registry/publish behavior, or broaden rollback/install/uninstall mutation in this slice.

Next Action: Hand this spec to `sy-trace-plan`, `sy-execution-plan`, or the repository's governed planning lane to create a PU-011 implementation plan from current `main`.

## Purpose

PU-008 made SDK capability truth visible. PU-009 added real project install. PU-010 added receipt-proven rollback and uninstall. PR #238 added the Infrastructure Python manifest and the first Pydantic typed contract spine.

PU-011 is the hardening slice that makes those contracts systematic. The intended user outcome is that an agent or automation can trust the SDK artifact boundary: command output validates against public schemas, Pydantic models reject malformed runtime payloads, Markdown/YAML source artifacts follow documented shape, HTML maps cannot overclaim runtime truth, and public SDK contract modules avoid loose `Any` typing.

## Problem Statement

The SDK now has enough real behavior that informal artifact discipline is a risk. Install, rollback, uninstall, status, receipts, lockfiles, and visual status maps all carry operational authority. If one surface drifts from another, an agent may make a false claim, mutate the wrong project, or treat a visual artifact as stronger evidence than runtime truth.

The repository already has pieces of the solution: JSON Schemas, Pydantic models, schema-spine tests, capability status tests, pipeline artifact checks, and the new `Infrastructure/pyproject.toml`. PU-011 should connect those pieces into a typed artifact contract lane without turning this into a broad refactor.

## Approved Scope

In scope:

- Pydantic models for SDK status, robot envelopes, skill manifest/frontmatter, install receipts, cleanup receipts, lockfiles, and artifact status rows
- shared JSON Schema validation helper for real SDK command output
- Markdown/frontmatter validation for `SKILL.md`, SDK specs, SDK plans, and implementation notes
- YAML validation for SDK-relevant metadata/config surfaces where present
- HTML artifact validation that cross-checks pipeline status against `ask sdk status`
- focused AST test that forbids `Any` in SDK public contract modules
- valid and invalid fixtures for YAML, JSON, Markdown, and HTML examples
- validation wiring into the existing repo validation lane as an explicit `skills-sdk` scope, including scope-table and unknown-scope behavior updates
- fixture freshness and provenance requirements that tie fixtures back to real emitters, schemas, or source artifact classes
- root package-manager boundary checks that fail if root package manifests or lockfiles are introduced without a separately approved package-root decision
- documentation of the package-manager boundary: root remains wrapper-only; Python SDK typing lives under `Infrastructure/pyproject.toml`
- preservation of existing install, rollback, uninstall, and status behavior

Out of scope:

- root-level `package.json`, root-level Python package metadata, or root package-manager install step
- broad conversion of all internal dictionaries or dataclasses across the repo
- replacing JSON Schema with Pydantic or Pydantic with JSON Schema
- registry, marketplace, publish, signing, trust-store, sandbox, or hosted explorer implementation
- changing SDK mutation semantics for install, rollback, or uninstall
- live project mutation outside temp-project tests
- CI, PR, review-thread, tracker, or merge readiness claims unless checked separately during closeout

## Current Evidence

| Evidence | Current observation | Spec consequence |
| --- | --- | --- |
| `git status --short --branch` | `main...origin/main` is clean after pulling PR #238. | PU-011 can be planned from current `main` without carrying dirty local state. |
| `./bin/ask sdk status --json --robot` | Capability truth reports 27 rows: 9 implemented, 3 preview-only, 6 deferred, 4 optional placeholders, 1 placeholder blocked, 1 blocked adapter, and 3 out of scope; install, rollback, and uninstall are implemented mutation-capable rows. | Typed artifact enforcement must protect mutation-adjacent receipts/status and avoid overclaiming deferred lanes. |
| `Infrastructure/pyproject.toml` | The Infrastructure Python project exists and includes Pydantic. | PU-011 should keep Python dependency ownership under `Infrastructure/` and not add root package-manager state. |
| `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` | Initial Pydantic models exist for install receipts, lockfiles, and cleanup receipts. | PU-011 should expand and organize the typed contract layer rather than starting from scratch. |
| `Infrastructure/config/schemas/skills-sdk/*.schema.json` | Public schemas exist for capability status, check receipts, install receipts, cleanup receipts, lockfiles, previews, risk, and lifecycle placeholders. | Real command output should be validated against these schemas and fixtures should cover pass/fail cases. |
| `Infrastructure/tests/test_skills_sdk_schema_spine.py` | Current tests validate schema-spine fixtures. | PU-011 should reuse this pattern and extend it to runtime command output and non-JSON artifacts. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | Pipeline artifact validation already exists. | PU-011 should strengthen this into runtime-vs-HTML status consistency. |
| `artifacts/recommended-skills-sdk-pipeline.html` | The pipeline map carries capability status and visual completion signals. | The HTML artifact must be validated as evidence, not trusted as prose. |
| `artifacts/skills-sdk-user-lifecycle-one-page.html` | The lifecycle map carries user-facing SDK status signals. | The lifecycle map should not claim completion that `ask sdk status` does not support. |

## Affected Surfaces

| Surface | Classification | Required action |
| --- | --- | --- |
| `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` | change | Expand or split Pydantic models for SDK status, robot envelopes, manifests, frontmatter, receipts, lockfiles, cleanup receipts, and artifact rows. |
| `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py` | change_if_existing_contract_owner | Reuse or align with existing SDK contract helpers instead of creating competing validation paths. |
| `Infrastructure/scripts/lib/ask/skills_sdk/capability_status.py` | change_if_needed | Emit payloads that pass Pydantic and JSON Schema validators without adapter-specific exceptions. |
| `Infrastructure/scripts/lib/ask/commands/sdk.py` | read_only_or_change_if_needed | Real command output may need narrow changes if validators expose shape drift. |
| `Infrastructure/scripts/lib/ask/envelope.py` | change | Include the real public robot envelope in typed contract validation and no-`Any` enforcement, or introduce a typed compatibility wrapper with equivalent coverage. |
| `Infrastructure/scripts/lib/ask/**/*.py` public output emitters | change_if_touched | Include modules that construct `--json --robot` output envelopes when changed files affect SDK command output. |
| `Infrastructure/config/schemas/skills-sdk/*.schema.json` | read_only_or_change_if_needed | Keep schemas public-contract canonical; change only when runtime contract is intentionally updated. |
| `Infrastructure/tests/helpers/schema_validator.py` | change | Add or reuse shared JSON Schema validation helper for real command output. |
| `Infrastructure/tests/test_skills_sdk_typed_contracts.py` | change | Extend Pydantic validation tests for status, envelopes, manifest/frontmatter, artifact rows, receipts, and lockfiles. |
| `Infrastructure/tests/test_skills_sdk_schema_spine.py` | change | Add fixture coverage for new schema/runtime output relationships if that remains the canonical schema-spine test. |
| `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py` | change | Cross-check HTML capability/status rows against `ask sdk status`. |
| `Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/**` | change | Add valid and invalid fixtures for JSON, YAML, Markdown, and HTML typed artifact examples. |
| `Infrastructure/scripts/validate_all_impl.sh` | change | Add an explicit `skills-sdk` validation scope and update the scope table, changed-file routing, and unknown-scope failure contract together. |
| `scripts/validate_all_impl.sh` | generated_or_mirrored_wrapper | Keep wrapper/mirror behavior consistent if the repo mirrors Infrastructure scripts at root. |
| `Docs/agents/02-tooling-policy.md` | change_if_needed | Document that SDK Python typing uses `uv run --project Infrastructure` and root remains package-manager-free. |
| `artifacts/recommended-skills-sdk-pipeline.html` | read_only_or_change_if_validation_fails | Update only when the validator proves visual/runtime drift. |
| `artifacts/skills-sdk-user-lifecycle-one-page.html` | read_only_or_change_if_validation_fails | Update only when the validator proves visual/runtime drift. |
| GitHub, Linear, review threads, CI | not_checked | Do not claim readiness for these lanes unless checked during closeout. |

## Type Enforcement Matrix

| Surface | Enforcement | Acceptance evidence |
| --- | --- | --- |
| Python SDK contracts | Pydantic models plus focused AST checks | Public SDK contract modules validate runtime payloads and contain no `Any` annotations. |
| Markdown | Markdown parser plus frontmatter model plus section contract validator | `SKILL.md`, SDK specs, SDK plans, and implementation notes fixtures pass/fail deterministically. |
| YAML | YAML parser plus Pydantic model or JSON Schema | Metadata/config fixtures reject missing required fields, invalid enums, and extra keys. |
| JSON | JSON Schema plus Pydantic model validation | Real SDK command outputs and fixtures validate against both public and runtime contracts. |
| JSON Schema | Meta-schema validation plus valid/invalid fixtures | Schema changes cannot require fields absent from real emitters. |
| HTML/CSS/JS artifacts | DOM parser plus embedded/status data contract | Visual completion/status markers match `ask sdk status`. |
| Shell | Existing shell validation plus wrapper behavior tests | SDK validation wiring preserves wrapper contracts and explicit mutation flags. |
| JavaScript/Node | Package-root discipline plus schema/DOM validation for outputs | PU-011 does not add root Node tooling; any JS artifact validation remains package-root or Python-owned. |

## Contract Authority Rules

PU-011 MUST define how Pydantic runtime models and JSON Schema public contracts stay aligned.

Authority rules:

- JSON Schema is authoritative for public automation compatibility, schema versioning, required public fields, and external consumer expectations.
- Pydantic models are authoritative for Python runtime narrowing, command implementation boundaries, and local typed diagnostics.
- A payload accepted by a public Pydantic model but rejected by the matching public JSON Schema is a contract failure.
- A payload accepted by public JSON Schema but rejected by the matching public Pydantic model is a runtime-contract failure unless a documented compatibility exception exists.
- Required fields, optional fields, nullability, enum values, and extra-key behavior MUST be parity-tested for every SDK model/schema pair covered by PU-011.
- Any intentional divergence MUST be documented next to the model and schema fixture with a compatibility reason and a follow-up owner.

Initial parity pairs:

| Pydantic model family | Public schema |
| --- | --- |
| `CapabilityStatus` / `CapabilityRow` | `Infrastructure/config/schemas/skills-sdk/capability-status.v1.schema.json` |
| `InstallReceipt` | `Infrastructure/config/schemas/skills-sdk/install-receipt.v1.schema.json` |
| `CleanupReceipt` | `Infrastructure/config/schemas/skills-sdk/project-cleanup-receipt.v1.schema.json` |
| `Lockfile` | `Infrastructure/config/schemas/skills-sdk/lockfile.v1.schema.json` |
| `SkillSourceFrontmatter` | Markdown/frontmatter contract fixture and, where applicable, source manifest schema |
| `ManifestProjection` | `Infrastructure/config/schemas/skills-sdk/manifest-source.v1.schema.json` |

## Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | The SDK MUST define Pydantic models for capability status payloads, capability rows, robot response envelopes, SDK errors, telemetry blocks, install receipts, cleanup receipts, lockfiles, skill source frontmatter, manifest projection payloads, and HTML artifact status rows. |
| FR-002 | Public SDK Pydantic models MUST use `extra="forbid"` and reject unknown fields unless a specific compatibility exception is documented in code and tests. |
| FR-003 | Boundary validators MUST accept `object` as untrusted input and narrow to typed models through Pydantic validation. |
| FR-004 | SDK public contract modules MUST NOT use `typing.Any`, `Any` imports, or `dict[str, Any]` in public models, validators, command-output contracts, receipt builders, lockfile contracts, status contracts, or artifact contract modules. |
| FR-005 | The implementation MAY define `JsonScalar`, `JsonValue`, and `JsonObject` aliases for raw JSON compatibility surfaces instead of using `Any`. |
| FR-006 | The SDK MUST provide a shared JSON Schema validation helper that can validate a real SDK command payload against a selected schema path. |
| FR-007 | The validation helper MUST return structured diagnostics that include schema path, payload source, JSON path or equivalent location, message, and validation status. |
| FR-008 | Real `./bin/ask sdk status --json --robot` output MUST be validated against `capability-status.v1.schema.json` and the corresponding Pydantic models. |
| FR-009 | Real install, rollback, uninstall, check, risk, and lifecycle outputs covered by existing schemas MUST have at least one validation test that runs or constructs the production payload and validates it against JSON Schema and Pydantic where a model exists. |
| FR-010 | Schema tests MUST include valid and invalid fixtures for capability status, install receipt, cleanup receipt, lockfile, skill source frontmatter, manifest projection payloads, Markdown document contracts, YAML metadata/config, implementation notes, and HTML artifact rows. |
| FR-011 | Markdown validation MUST parse frontmatter separately from body content. |
| FR-012 | `SKILL.md` validation MUST require schema-approved skill source frontmatter when frontmatter exists and required body sections or equivalents needed by the current skill source contract. |
| FR-013 | SDK spec validation MUST require frontmatter, title, command summary or purpose, approved scope, out of scope, affected surfaces, functional requirements, acceptance criteria, validation commands, risks, rollback, and handoff notes. |
| FR-014 | SDK plan validation MUST require trace to a source spec, slices, affected files, validation commands, rollback or recovery notes, evidence limits, and handoff notes. |
| FR-015 | Implementation notes validation MUST require decisions, changed assumptions, tradeoffs, validation/evidence, and open follow-ups when the file is part of an SDK implementation lane. |
| FR-015A | Implementation notes validation MUST have at least one valid and one invalid fixture for SDK `.html` or `.mdx` notes, and the invalid fixture MUST fail for a missing required notes section or evidence field. |
| FR-016 | YAML validation MUST reject malformed YAML, non-mapping top-level documents for metadata/config contracts, missing required fields, invalid enum values, and undeclared extra keys. |
| FR-017 | HTML artifact validation MUST parse `artifacts/recommended-skills-sdk-pipeline.html` and collect capability rows with ids and statuses. |
| FR-018 | HTML artifact validation MUST compare capability ids and statuses against `./bin/ask sdk status --json --robot` and fail on unsupported statuses, missing required rows, or visual completed markers on rows that runtime truth does not mark implemented or preview-backed according to the accepted status matrix. |
| FR-019 | HTML artifact validation MUST treat runtime SDK status as authority over visual artifact labels. |
| FR-020 | The lifecycle one-page artifact MUST receive the same runtime-vs-visual consistency checks for capability labels it exposes. |
| FR-021 | The SDK validation lane MUST be invokable through `./bin/ask repo validate --scope=skills-sdk --json --robot`, and implementation MUST update the underlying validation scope table so the scope is recognized explicitly. |
| FR-022 | If a dedicated `skills-sdk` validation scope is added, unknown scopes MUST continue to fail through the existing scope-validation contract. |
| FR-023 | Existing full validation MUST include the typed artifact contract check when changed files touch SDK schemas, SDK contract modules, public robot envelope/output modules, SDK command modules, SDK tests, SDK specs/plans, SDK implementation notes, or SDK HTML artifacts. |
| FR-024 | PU-011 MUST preserve the root package-manager contract: the repository root has no package-manager install step and SDK Python typing uses `uv run --project Infrastructure`. |
| FR-025 | PU-011 MUST preserve existing install, rollback, uninstall, check, lifecycle, and status command behavior except for stricter validation errors where payload shape is invalid. |
| FR-026 | Validation diagnostics MUST clearly distinguish local artifact truth, command-output truth, schema truth, PR/CI truth, and visual artifact truth. |
| FR-027 | If a schema and runtime payload disagree, the implementation MUST fix the emitter or schema deliberately and add a regression fixture for that disagreement. |
| FR-028 | The typed artifact validator MUST not require network access. |
| FR-029 | The typed artifact validator MUST avoid mutating the live repo except for deterministic generated validation artifacts already owned by the existing validation lane. |
| FR-030 | The implementation MUST document which artifact families are enforced by Pydantic, JSON Schema, parser checks, DOM checks, shell checks, and package-root checks. |
| FR-031 | The validation lane MUST assert that root package-manager files such as `package.json`, `pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, root `pyproject.toml`, and root lockfiles remain absent unless a separate approved package-root decision explicitly introduces them. |
| FR-032 | Fixtures used by typed artifact validation MUST include provenance metadata or naming that identifies whether they came from a real emitter, a schema-only fixture, or a hand-authored negative case. |
| FR-033 | Runtime-output fixtures MUST include a freshness rule: either regenerate from a real command in the test path or record the command/schema/source artifact version that makes stale fixture drift visible. |
| FR-034 | Skill source frontmatter and manifest projection MUST be separate contracts with separate fixture families, even when they share field names. |

## Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | Validators MUST be deterministic and suitable for CI. |
| NFR-002 | Focused SDK validation MUST complete quickly enough for local pre-PR use. |
| NFR-003 | Diagnostics MUST be actionable for agents and humans. |
| NFR-004 | The implementation MUST prefer small validator modules over a broad architectural rewrite. |
| NFR-005 | The implementation MUST keep current repo validation lanes compatible. |
| NFR-006 | The implementation MUST avoid adding external service dependencies. |
| NFR-007 | Fixture names and failure reasons MUST make the broken contract obvious. |
| NFR-008 | New models MUST use stable field names that align with current JSON Schemas unless an intentional schema migration is documented. |

## Artifact Contract Details

### Pydantic Contract Layer

The implementation SHOULD keep the first pass in or near `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` unless planning finds a cleaner local split such as:

```text
Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py
Infrastructure/scripts/lib/ask/skills_sdk/artifact_contracts.py
Infrastructure/scripts/lib/ask/skills_sdk/schema_validation.py
```

Acceptable model families include:

- `SdkRobotEnvelope`
- `SdkError`
- `SdkTelemetry`
- `CapabilityStatus`
- `CapabilityRow`
- `SkillSourceFrontmatter`
- `ManifestProjection`
- `InstallReceipt`
- `CleanupReceipt`
- `Lockfile`
- `ArtifactStatusRow`
- `MarkdownArtifactContract`
- `YamlArtifactContract`

The implementation MUST avoid a repo-wide model migration. Only SDK boundary payloads and fixtures are in scope.

### JSON Schema Helper

The shared helper SHOULD support:

- schema path
- payload source label
- payload object
- strict success/failure result
- structured issue list
- optional JSON Pointer-style location
- no network access
- local schema files only

The helper may live under tests first if it is only a proving utility. If production commands need the same validation, planning should promote it into the SDK library with tests.

### Validation Scope Contract

PU-011 MUST add or update an explicit validation scope named `skills-sdk`.

The implementation MUST update:

- the scope allowlist or help text in the validation runner
- the `./bin/ask repo validate --scope=skills-sdk --json --robot` route
- tests proving unknown scopes still fail
- tests proving the `skills-sdk` scope runs the typed artifact contract lane
- changed-file routing so SDK schema, SDK contract, public envelope/output, SDK spec/plan/notes, and SDK HTML artifact edits schedule the check

Using `check`, `test`, `lint`, or another existing broad scope as the only PU-011 entrypoint is not sufficient unless `skills-sdk` is intentionally rejected in a spec update before implementation.

### Markdown and YAML Contracts

Markdown validation MUST be artifact-class aware. It should not impose one universal heading structure on every Markdown file in the repo.

Minimum artifact classes for PU-011:

- skill source: `SKILL.md`
- SDK spec: `.harness/specs/*skills-sdk*.md`
- SDK plan: `.harness/plan/*skills-sdk*.md`
- SDK implementation notes: `.harness/implementation-notes/*skills-sdk*.html` and `.mdx` where practical

YAML validation MUST focus on SDK-relevant frontmatter and metadata/config surfaces. It must not become a full-repo YAML migration.

Skill source frontmatter and manifest projection are separate artifact classes:

- skill source frontmatter describes the author-owned `SKILL.md` source boundary
- manifest projection describes the SDK's derived or emitted manifest/source observation payload

The implementation MUST not satisfy both contracts with a single fixture unless that fixture explicitly declares both roles and validates independently under both contracts.

### HTML Artifact Contracts

HTML artifact validation MUST treat visual status as a derived projection. The source of truth is `ask sdk status`.

The validator SHOULD extract:

- capability id
- status
- visible title
- completed/preview/deferred marker classes where present
- embedded JSON capability data if present
- evidence or next-slice fields where present

Failures should read like:

```text
capability rollback: html status=deferred, runtime status=implemented
capability uninstall: completed marker present but runtime status=deferred
capability real_install: runtime row missing from recommended pipeline artifact
```

Status mapping:

| Runtime status | HTML status requirement | Visual marker rule |
| --- | --- | --- |
| `implemented` | Must appear in the recommended pipeline artifact unless explicitly out of the artifact's declared coverage. | May use completed/green marker. |
| `preview_only` | Must appear when the artifact covers preview-backed SDK surfaces. | May use preview marker; may use completed outline only if label makes preview status explicit. |
| `deferred` | May appear as roadmap/deferred or may be omitted only when the artifact declares a narrower implemented-surface view. | Must not use completed marker. |
| `placeholder_optional` | May appear as placeholder/optional or may be omitted with declared coverage. | Must not use completed marker. |
| `placeholder_blocked` | May appear as blocked placeholder or may be omitted with declared coverage. | Must not use completed marker. |
| `blocked_missing_adapter` | Should appear when the artifact covers adapter readiness; otherwise may be omitted with declared coverage. | Must not use completed marker. |
| `out_of_scope` | May appear as out-of-scope or be omitted from user-flow artifacts. | Must not use completed marker. |

Missing-row policy:

- `artifacts/recommended-skills-sdk-pipeline.html` is the broad capability map and MUST include every `ask sdk status` capability id unless its embedded metadata declares a narrower coverage set.
- `artifacts/skills-sdk-user-lifecycle-one-page.html` may omit non-user-facing deferred or out-of-scope rows, but it MUST not contradict runtime truth for any row it exposes.
- Any omission from a broad artifact MUST be reported as `omitted_with_declared_coverage` or `missing_required_row`.

### No-Any Enforcement

The AST test MUST be scoped. It should cover SDK public contract modules, not every Python file in the repository.

Initial path set:

- `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py`
- any new `Infrastructure/scripts/lib/ask/skills_sdk/*contract*.py`
- any new `Infrastructure/scripts/lib/ask/skills_sdk/*schema*.py`
- any new `Infrastructure/scripts/lib/ask/skills_sdk/*artifact*.py`
- `Infrastructure/scripts/lib/ask/envelope.py`
- any module that directly constructs public SDK `--json --robot` output envelopes

The test MUST fail on:

- `from typing import Any`
- `typing.Any`
- annotation name `Any`
- `dict[str, Any]`
- `Mapping[str, Any]`
- `list[Any]`

The test MAY allow third-party compatibility shims only through an explicit allowlist with a comment and a fixture proving the public SDK contract does not expose the loose type.

### Fixture Freshness and Provenance

Every typed artifact fixture family MUST declare one of these origins:

- `real_emitter`: generated from a named command or source file in the test path
- `schema_positive`: hand-authored valid fixture for schema/model coverage
- `schema_negative`: hand-authored invalid fixture proving a refusal path
- `visual_projection`: minimized HTML fixture for DOM/status validation
- `source_artifact`: minimized Markdown/YAML fixture for source parsing

Runtime-output fixtures SHOULD be regenerated by tests from real commands when practical. When static fixtures are used, the fixture or adjacent manifest MUST record the schema version, source command or source artifact class, and the reason a static fixture is acceptable.

### Root Package-Manager Boundary Check

The `skills-sdk` validation scope MUST prove the root package-manager boundary directly. At minimum, it must assert that these files are absent at repository root unless an approved package-root decision exists:

- `package.json`
- `package-lock.json`
- `pnpm-lock.yaml`
- `yarn.lock`
- root `pyproject.toml`
- root Python lockfiles

The check MUST allow `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock`.

## Acceptance Criteria

| ID | Given | When | Then |
| --- | --- | --- | --- |
| AC-001 | Current `main` with PU-010 and PR #238 merged | The focused SDK typed-artifact validation is run | It passes without adding a root package-manager install step. |
| AC-002 | Real `./bin/ask sdk status --json --robot` output | The schema/Pydantic validation helper runs | The payload validates against capability status schema and Pydantic models. |
| AC-003 | A real or fixture install receipt | The typed contract tests run | The receipt validates against install receipt schema and Pydantic model. |
| AC-004 | A real or fixture cleanup receipt | The typed contract tests run | The receipt validates against project cleanup receipt schema and Pydantic model. |
| AC-005 | A real or fixture lockfile | The typed contract tests run | The lockfile validates against lockfile schema and Pydantic model. |
| AC-006 | A valid SDK `SKILL.md` fixture | Markdown/frontmatter validation runs | The fixture passes with typed frontmatter and required body sections. |
| AC-007 | An invalid SDK `SKILL.md` fixture missing required structure | Markdown/frontmatter validation runs | The fixture fails with a specific missing-field or missing-section diagnostic. |
| AC-008 | Valid and invalid YAML metadata/config fixtures | YAML validation runs | Valid fixtures pass and invalid fixtures fail for specific schema reasons. |
| AC-009 | `artifacts/recommended-skills-sdk-pipeline.html` | HTML artifact validation runs with live SDK status | Capability ids and statuses agree with runtime truth. |
| AC-010 | `artifacts/skills-sdk-user-lifecycle-one-page.html` | HTML artifact validation runs with live SDK status | Visual completion/preview/deferred labels agree with runtime truth for exposed SDK capabilities. |
| AC-011 | A public SDK contract module imports or annotates `Any` | The focused AST test runs | The test fails and reports the file and line. |
| AC-012 | Public SDK contract modules use Pydantic models, `object`, or JSON aliases instead of `Any` | The focused AST test runs | The test passes. |
| AC-013 | A schema requires a field that the real command emitter omits | Runtime schema validation runs | The test fails before PR closeout and identifies the missing field. |
| AC-014 | A visual HTML artifact marks a deferred runtime capability as completed | HTML artifact validation runs | The test fails and names the capability id. |
| AC-015 | The repository root has no package manager manifest | PU-011 validation commands run | Commands use `uv run --project Infrastructure` or repo wrappers and do not require root package installation. |
| AC-016 | `./bin/ask repo validate --scope=skills-sdk --json --robot` is invoked | The validation route runs | The scope is recognized and executes the typed artifact contract lane. |
| AC-017 | An unknown validation scope is invoked | The validation route runs | The command fails closed with the existing unknown-scope behavior. |
| AC-018 | `Infrastructure/scripts/lib/ask/envelope.py` or another public output-envelope module uses `Any` in the public SDK envelope path | The focused AST test runs | The test fails and reports the file and line. |
| AC-019 | Pydantic and JSON Schema disagree on required fields, enum values, nullability, or extra-key behavior for a covered SDK contract pair | The parity tests run | The test fails and identifies the model/schema pair. |
| AC-020 | Valid and invalid SDK implementation-notes fixtures are present | Markdown/HTML notes validation runs | The valid fixture passes and the invalid fixture fails with a specific notes-contract diagnostic. |
| AC-021 | Root package-manager files are introduced without an approved package-root decision | The `skills-sdk` validation scope runs | The validation fails and names the forbidden root file. |
| AC-022 | A static fixture lacks provenance or freshness metadata | The typed artifact fixture validation runs | The validation fails and identifies the fixture family and missing provenance field. |

## Validation Plan

Required local validation for the implementation slice:

```bash
git status --short --branch
env UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache \
  XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache \
  XDG_STATE_HOME=/private/tmp/agent-skills-xdg-state \
  MISE_CACHE_DIR=/private/tmp/agent-skills-mise-cache \
  MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" \
  uv run --project Infrastructure --locked --group test python -m pytest \
  Infrastructure/tests/test_skills_sdk_typed_contracts.py \
  Infrastructure/tests/test_skills_sdk_schema_spine.py \
  Infrastructure/tests/test_skills_sdk_capability_status.py \
  Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py \
  -q

env UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache \
  MISE_TRUSTED_CONFIG_PATHS="$PWD/.mise.toml" \
  uv run --project Infrastructure --locked --group lint ruff check \
  Infrastructure/scripts/lib/ask/skills_sdk \
  Infrastructure/tests

./bin/ask sdk status --json --robot
./bin/ask repo validate --scope=skills-sdk --json --robot
bash scripts/validate-codestyle.sh
./bin/ask repo validate --json --robot
```

Validation limits:

- Local tests prove local code, schema, fixture, command-output, and artifact contracts only.
- Local validation does not prove GitHub CI, review-thread, CodeRabbit, tracker, mergeability, or deployment state.
- HTML validation proves static artifact consistency with runtime status at validation time; it does not prove hosted publication.
- Pydantic validation proves Python runtime shape, not external consumer compatibility beyond the covered schemas and fixtures.

## Risks

| Risk | Mitigation |
| --- | --- |
| Validator scope becomes too broad and slows normal repo validation. | Start with focused SDK scope and changed-file routing; add full validation only where repo policy requires it. |
| Pydantic models drift from JSON Schemas. | Validate real outputs through both and add regression fixtures whenever drift is found. |
| Markdown validation overfits current prose style. | Validate artifact contracts and required semantics, not exact wording. |
| HTML artifact validation becomes brittle against harmless layout changes. | Parse semantic ids/statuses/classes instead of visual positioning. |
| No-`Any` enforcement blocks legitimate third-party shims. | Scope enforcement to public SDK contract modules and require explicit allowlist for compatibility shims. |
| Root package-manager drift sneaks in through HTML/JS validation. | Keep DOM validation Python-owned or package-root-owned; do not add root `package.json`. |
| Command-output validation mutates live state. | Use status/check/preview commands and temp-project fixtures only. |
| The real robot envelope remains loosely typed while SDK-specific models are strict. | Include public envelope/output modules in model coverage, no-`Any` enforcement, and changed-file routing. |
| Pydantic and JSON Schema both exist but silently disagree. | Add model/schema parity tests and explicit authority rules for public compatibility versus runtime narrowing. |
| Static fixtures become stale and hide runtime drift. | Require real-emitter fixtures where practical and provenance/freshness metadata for static fixtures. |

## Rollback

If PU-011 implementation causes validation disruption:

1. Revert the validation wiring first so unrelated repo work is not blocked.
2. Keep Pydantic models and fixtures if they are correct but too broadly enforced.
3. Restore previous `validate_all` scope behavior.
4. Re-run `./bin/ask sdk status --json --robot` and existing SDK tests to confirm runtime behavior remains intact.
5. Re-plan a narrower typed-contract slice with only the failing artifact family.

Rollback must not remove the existing PU-009/PU-010 install, rollback, uninstall, receipt, lockfile, or capability truth behavior unless a direct regression is proven there.

## Blocked Inputs

No blocker for planning. Implementation planning should decide:

- exact module split for typed contract models
- whether the JSON Schema helper is test-only or production library code
- exact `repo validate --scope=skills-sdk` wiring point
- Markdown parser dependency strategy under `Infrastructure/pyproject.toml`
- whether HTML parsing uses Python standard library, existing test dependencies, or a lightweight dependency under `Infrastructure/`

## Handoff Notes

Recommended next stage: `sy-trace-plan` or `sy-execution-plan`.

Planning should preserve these boundaries:

- Start from current clean `main`.
- Use a clean PU-011 feature worktree.
- Keep root package-manager contract unchanged.
- Add the explicit `skills-sdk` validation scope or revise this spec before implementation if that scope name is rejected.
- Do not widen install/rollback/uninstall mutation.
- Prefer validators over reminder docs.
- Keep artifact truth, runtime truth, schema truth, PR truth, and CI truth separate.
- Update `artifacts/recommended-skills-sdk-pipeline.html` and `artifacts/skills-sdk-user-lifecycle-one-page.html` only if validation proves they drift or if capability labels are intentionally refined.

## Evidence Checked

- `git status --short --branch`
- `rg --files Infrastructure/scripts/lib/ask/skills_sdk Infrastructure/config/schemas/skills-sdk Infrastructure/tests artifacts .harness/specs .harness/plan .harness/implementation-notes`
- `rg -n "class .*BaseModel|Any|JsonValue|validate_.*receipt|sdk status|capability-status|project-cleanup-receipt|install-receipt|lockfile" Infrastructure/scripts/lib/ask/skills_sdk Infrastructure/tests Infrastructure/config/schemas/skills-sdk`
- `rg -n "scope=.*skills|skills-sdk|repo validate|validate_all|schedule_check|capability-status|pipeline-status" Infrastructure/scripts scripts Infrastructure/tests`
- `sed -n '1,220p' .harness/specs/2026-06-05-skills-sdk-pu-010-receipt-proven-rollback-uninstall-spec.md`
- `sed -n '1,220p' .harness/specs/2026-06-05-skills-sdk-pu-009-real-project-install-lifecycle-spec.md`
- `sed -n '1,220p' Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py`

## Validation

Spec artifact validation in this stage:

- blocked: implementation validation commands were not run because this stage produced a spec artifact only.
- blocked: PR, CI, review-thread, tracker, mergeability, and deployment lanes were not checked in this spec-writing run.
