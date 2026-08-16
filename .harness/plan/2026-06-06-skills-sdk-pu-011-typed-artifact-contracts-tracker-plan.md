---
schema_version: 1
artifact_id: sy-tracker-plan-2026-06-06-skills-sdk-pu-011-typed-artifact-contracts
artifact_type: sy-tracker-plan
canonical_slug: skills-sdk-pu-011-typed-artifact-contracts
harness_stage: sy-tracker-plan
title: "PU-011: Skills SDK Typed Artifact Contracts Tracker Plan"
status: tracker_ready_without_external_mutation
date: 2026-06-06
target_trace_plan: .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md
target_spec: .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md
tracker_mutation_status: not_authorized
external_mutation_status: not_authorized
---

# PU-011: Skills SDK Typed Artifact Contracts Tracker Plan

## Decision

Convert the approved PU-011 trace plan into tracker-ready tasks without creating, updating, assigning, or closing external tracker issues. The work stays bounded to typed artifact contracts for the Skills SDK: Pydantic models, JSON Schema validation, Markdown/YAML/HTML artifact validation, no-`Any` enforcement, fixture provenance, validation-scope wiring, and package-root boundary checks.

The tracker tasks intentionally do not add registry, publish, signing, trust-store, sandbox, marketplace, hosted explorer, or new install/rollback/uninstall mutation semantics.

## Target

- Repo: `/Users/jamiecraik/dev/agent-skills`
- Source trace plan: `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`
- Source spec: `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`
- Current local state: `main...origin/main` with untracked PU-011 planning and review artifacts
- Tracker mutation: blocked because the user requested a tracker plan, not tracker writes

## Tracker Task Plan

| ID | Title | Owner surface | Dependency | Acceptance criteria | Proof | Non-goals |
| --- | --- | --- | --- | --- | --- | --- |
| PU-011-T01 | Create PU-011 feature worktree and preserve planning artifacts | Git/worktree lane | Current `main` plus untracked PU-011 artifacts | Clean feature worktree exists for PU-011; spec, trace plan, tracker plan, review artifacts, and reviewer manifests are intentionally staged or copied into the worktree; primary repo state is not mixed with implementation edits | `git status --short --branch`; `git worktree list`; staged-file list before commit | Do not push, open PR, or mutate tracker in this task |
| PU-011-T02 | Add `skills-sdk` validation scope and changed-file routing | `Infrastructure/scripts/validate_all_impl.sh`, ask repo validate route, validation-runner tests | T01 | `skills-sdk` is a recognized validation scope; unknown scopes still fail closed; SDK schemas, contract modules, public envelope/output modules, SDK command modules, SDK tests, SDK specs/plans, implementation notes, and SDK HTML artifacts schedule the typed artifact lane; unrelated files do not over-schedule it | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_validation_scope.py Infrastructure/tests/test_ask_repo_validate.py -q`; `./bin/ask repo validate --scope=skills-sdk --json --robot`; unknown-scope negative command | Do not make `skills-sdk` an alias for broad `all` validation |
| PU-011-T03 | Implement typed SDK contract model spine | `Infrastructure/scripts/lib/ask/skills_sdk/typed_contracts.py` or local split modules | T01 | Pydantic models cover SDK status, capability rows, robot envelope, errors, telemetry, install receipts, cleanup receipts, lockfiles, skill source frontmatter, manifest projection, and artifact rows; models use strict extra-field behavior; boundary validators accept `object` and narrow through Pydantic | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_typed_contracts.py -q` | Do not convert unrelated internal dictionaries or dataclasses outside SDK boundary contracts |
| PU-011-T04 | Add no-`Any` AST enforcement for public SDK contracts | `Infrastructure/tests/test_skills_sdk_no_any_contracts.py`, `Infrastructure/scripts/lib/ask/envelope.py`, SDK contract modules | T03 | Focused AST test fails on `typing.Any`, `Any` annotations, `dict[str, Any]`, `Mapping[str, Any]`, and `list[Any]` in covered public SDK contract/output modules; live robot envelope remains format-compatible | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_no_any_contracts.py Infrastructure/tests/test_ask_cli_impl.py -q`; `uv run --project Infrastructure --locked --group lint ruff check Infrastructure/scripts/lib/ask/skills_sdk Infrastructure/scripts/lib/ask/envelope.py Infrastructure/tests` | Do not apply no-`Any` enforcement repo-wide |
| PU-011-T05 | Add JSON Schema validation helper and schema/model parity proof | `Infrastructure/tests/helpers/schema_validator.py`, `Infrastructure/tests/test_skills_sdk_schema_model_parity.py`, schema fixtures | T03 | Shared local JSON Schema helper returns structured diagnostics with schema path, payload source, JSON location, message, and status; schema/model parity tests fail on required-field, enum, nullability, extra-key, and model/schema disagreement fixtures; parity covers status, install receipt, cleanup receipt, lockfile, source frontmatter, manifest projection, artifact row, and schema-backed envelope surfaces where applicable | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_schema_model_parity.py Infrastructure/tests/test_skills_sdk_schema_spine.py -q` | Do not replace JSON Schema with Pydantic or Pydantic with JSON Schema |
| PU-011-T06 | Validate real SDK command outputs and receipt-adjacent surfaces | SDK command tests, status tests, install/cleanup tests | T05 | Real `ask sdk status --json --robot` validates against capability status schema and Pydantic models; check, install, rollback, uninstall, risk, and lifecycle payloads have real or production-constructed validation proof; uninstall preview/apply and cleanup receipt semantics are covered | `./bin/ask sdk status --json --robot`; `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_capability_status.py Infrastructure/tests/test_skills_sdk_project_cleanup.py Infrastructure/tests/test_skills_sdk_typed_contracts.py -q` | Do not mutate the live repo or change install/rollback/uninstall semantics except stricter invalid-shape diagnostics |
| PU-011-T07 | Add source artifact validators for Markdown, YAML, and implementation notes | Markdown/YAML validators, typed artifact fixtures | T05 | `SKILL.md`, SDK specs, SDK plans, and SDK implementation notes parse deterministically; implementation notes require decisions, changed assumptions, tradeoffs, validation/evidence, and open follow-ups; YAML fixtures reject malformed, missing, invalid enum, and extra-key cases | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_typed_contracts.py Infrastructure/tests/test_skills_sdk_schema_spine.py -q` plus the dedicated source-artifact test file created by the implementation slice | Do not impose one universal Markdown heading contract across the entire repo |
| PU-011-T08 | Add fixture provenance sidecar manifests | `Infrastructure/tests/fixtures/skills_sdk/typed_artifacts/**/fixture-manifest.json` | T05, T07 | Every fixture family has one sidecar `fixture-manifest.json`; accepted origins are exactly `real_emitter`, `schema_positive`, `schema_negative`, `visual_projection`, and `source_artifact`; static fixtures record schema version, source command or source artifact class, and static-fixture rationale; embedded-only and inference-only provenance are rejected | Fixture validation tests fail on missing manifest, missing origin, unsupported origin, missing freshness metadata, and stale source metadata | Do not support multiple provenance storage formats in PU-011 |
| PU-011-T09 | Add HTML runtime-vs-visual artifact validation | `Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py`, `artifacts/recommended-skills-sdk-pipeline.html`, `artifacts/skills-sdk-user-lifecycle-one-page.html` | T06, T08 | Recommended pipeline artifact matches runtime capability ids and statuses or declares narrower coverage; lifecycle one-page artifact does not contradict exposed runtime truth; visual completed markers are forbidden for deferred, placeholder, blocked, or out-of-scope runtime rows | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_pipeline_status_artifact.py -q`; `./bin/ask sdk status --json --robot` | Do not update HTML artifacts unless validation proves visual/runtime drift or coverage metadata needs refinement |
| PU-011-T10 | Enforce root package-manager boundary | `Infrastructure/tests/test_skills_sdk_root_package_boundary.py`, validation scope check | T02 | Root package-manager files remain absent unless a separate approved package-root decision exists; temp/scratch negative tests inject forbidden root `package.json`, lockfile, and root `pyproject.toml` and prove the `skills-sdk` validation lane fails closed with each filename; `Infrastructure/pyproject.toml` and `Infrastructure/uv.lock` remain allowed | `uv run --project Infrastructure --locked --group test python -m pytest Infrastructure/tests/test_skills_sdk_root_package_boundary.py -q`; `./bin/ask repo validate --scope=skills-sdk --json --robot` | Do not add a root package manager |
| PU-011-T11 | Document enforcement ownership and evidence boundaries | SDK docs or `Docs/agents/02-tooling-policy.md` when appropriate | T02-T10 | Docs state which artifact families are enforced by Pydantic, JSON Schema, parser checks, DOM checks, shell checks, and package-root checks; docs preserve root wrapper-only package-manager contract and Infrastructure Python boundary; evidence lanes remain separated | Docs check or relevant repo validation lane; review of command examples | Do not claim CI, PR, tracker, mergeability, or deployment readiness from local docs |
| PU-011-T12 | Run focused and aggregate local validation | Local validation lane | T02-T11 | Focused pytest, Ruff, `ask sdk status`, `ask repo validate --scope=skills-sdk`, codestyle, and full repo validation outcomes are recorded as pass, fail, or blocked with exact commands; evidence limits are stated | Full validation block from the trace plan; `bash scripts/validate-codestyle.sh`; `./bin/ask repo validate --json --robot` | Do not collapse local validation into PR/CI/review readiness |
| PU-011-T13 | Prepare PR handoff and green-sweep checklist | PR lane after implementation branch exists | T12 | Branch is ready for intentional commit and PR; PR body follows repo template; PR green-sweep checklist covers live PR status, CI checks, review comments/threads, mergeability, and CodeRabbit/Codex feedback after PR creation | `git status --short --branch`; PR template read; post-PR `gh pr view`, `gh pr checks`, review-thread sweep when authorized | Do not create or mutate PR/tracker unless explicitly authorized for that stage |

## Dependency Order

1. T01 creates the clean implementation boundary.
2. T02 establishes the validation entrypoint and changed-file scheduling before other tasks rely on it.
3. T03 to T05 create the typed contract and schema authority spine.
4. T06 proves real SDK command outputs and mutation-adjacent receipts.
5. T07 and T08 add source artifact validation and one canonical fixture provenance format.
6. T09 and T10 enforce visual truth and package-root boundaries.
7. T11 documents ownership after enforcement exists.
8. T12 performs local closeout validation.
9. T13 moves into PR handoff only after local proof exists.

## Evidence Checked

- `sed -n '1,260p' Plugins/synaipse-harness/skills/sy-tracker-plan/SKILL.md`
- `git status --short --branch`
- `sed -n '1,280p' .harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`
- `sed -n '1,430p' .harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`

## Validation

Tracker-plan validation in this stage:

- pass: source skill contract was loaded from `Plugins/synaipse-harness/skills/sy-tracker-plan/SKILL.md`.
- pass: source trace plan was read from `.harness/plan/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-trace-plan.md`.
- pass: source spec was read from `.harness/specs/2026-06-06-skills-sdk-pu-011-typed-artifact-contracts-spec.md`.
- pass: pass-two review artifacts are present and non-empty by `wc -l`.
- blocked: implementation validation commands were not run because this stage produced tracker-ready planning only.
- blocked: external tracker mutation was not authorized.
- blocked: PR, CI, review-thread, tracker, mergeability, and deployment lanes were not checked.

## Open Risks

- The tracker plan is local-file evidence only until tracker issues are created or linked in an authorized tracker-mutation stage.
- The named future tests in the trace plan do not exist yet; they are proof owners for the implementation slice, not current validation evidence.
- The `skills-sdk` scope is still implementation work, so `./bin/ask repo validate --scope=skills-sdk --json --robot` should not be treated as a current passing command until T02 lands.
- Fixture provenance is frozen to sidecar manifests for PU-011, but the exact manifest schema is an implementation detail for T08.
- PR/CI/review-thread/mergeability readiness remains unknown until after implementation PR creation and green-sweep.

## Next Stage

Recommended next stage: `sy-execution-plan` for this tracker plan and the approved trace plan, followed by `sy-work` in a clean feature worktree.

