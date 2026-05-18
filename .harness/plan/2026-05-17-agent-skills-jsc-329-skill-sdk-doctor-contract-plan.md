---
schema_version: 1
artifact_id: agent-skills-jsc-329-skill-sdk-doctor-contract-plan
artifact_type: he-plan
type: he-plan
canonical_slug: jsc-329-skill-sdk-doctor-contract
title: Agent Skills Kit JSC-329 Skill SDK Doctor Contract Plan
harness_stage: he-plan
status: ready_for_he_work
date: 2026-05-17
origin: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
source_spec: .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
source_review: .harness/review/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec-technical-review.md
layered_sdk_technical_review: .harness/review/2026-05-17-agent-skills-jsc-329-layered-sdk-plan-technical-review.md
risk: medium-high
depth: bounded-execution-slice
ui: false
traceability_required: true
linear_mutation_status: created
linear_status: Triage
linear_issue: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
linear_team: JSC
linear_workspace: Jscraik
linear_priority: 2
linear_labels: [agent-skills, Governance, Reliability, Developer Experience, Roadmap: Next, Feature]
plan_deepening_status: completed_layered_sdk_update
review_status: layered_sdk_technical_review_approved
confidence_review_status: updated_after_adversarial_plan_review
confidence_ceiling: implementation_not_yet_tested
decision_deepening_status: updated_for_waiver_schema_layer_imagegen_decisions
apparatus_lens_status: integrated
apparatus_lens: Infrastructure/references/skills-sdk-apparatus-lens.md
---

# Agent Skills Kit JSC-329 Skill SDK Doctor Contract Plan

## Command Summary

BLUF: This plan gives Jamie, future Codex agents, and harness consumers a bounded implementation contract for hardening ./bin/ask skills doctor context7 --json --robot as the first fixture-backed Skill SDK readiness surface. It matters because they must trust data.skill_doctor without parsing skill prose, package summaries, AI review, or runtime projections. The execution decision is to work only in ask doctor implementation, focused tests, fixture/evidence artifacts, and closeout docs needed to prove the contract through the Skills SDK apparatus lens.

The main risk is overfitting context7, hiding SDK ownership behind generic buckets, treating polished artifacts as readiness, or applying transferable API feedback too locally. The plan counters that with dynamic-field normalization, SDK layer mapping, counterexample-style assertions, one representativeness probe, and a pattern-sweep disposition before handoff to he-work.

Decision Needed: Approve PU-001 through PU-006 for he-work, with PU-001 as the first implementation unit.

Top Risks: A command-shape test can accidentally assert the outer ask envelope instead of data.skill_doctor; presence-only field checks can let semantically empty or wrong-typed payloads pass; skipped critical checks can be smoothed into pass; generic app-layer names can hide SDK ownership; broad SDK migration can creep into a fixture slice; a non-zero doctor exit from blocked readiness can be misclassified as command failure; a coherent skill artifact or AI review can be mistaken for the apparatus that must verify readiness.

Next Action: Hand PU-001 to he-work, then execute units in order until the focused test and changed-file validation pass.

## Objective

Implement JSC-329 as the smallest reversible proof that skills doctor exposes a professional SDK readiness contract for context7.

The plan must produce implementation steps that prove:

- required doctor fields are present at data.skill_doctor with enforceable JSON shapes and minimum semantic content;
- observable checks, blockers, warnings, and evidence groups map to the layered Skill SDK vocabulary where safe;
- status precedence is deterministic and critical skipped/not-run checks cannot produce pass;
- runtime reachability, package readiness, and outcome proof remain separate;
- next_command is selected by a deterministic blocker-first ladder and is intentionally nullable only with evidence that no safe command exists;
- dynamic fields do not make tests flaky;
- RF-0 steering uptake remains part of closeout;
- transferable review feedback triggers a bounded pattern sweep instead of a one-line-only edit.

## Source Contract

| Source | Contract Consumed |
| --- | --- |
| .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md | FR-001 through FR-026, NFR-001 through NFR-006, SA-001 through SA-021. |
| Infrastructure/references/skills-sdk-apparatus-lens.md | Applies Jamie's mantra to the apparatus model: Thin surface. Strong guardrails. Durable memory. Professional output. |
| .harness/review/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec-technical-review.md | Required fields must be asserted at data.skill_doctor inside the ask robot envelope. |
| artifacts/reviews/jsc329_round1_adversarial_reviewer.md | Presence-only fields, skipped critical checks, exit semantics, and weak representativeness were blocking faults. |
| artifacts/reviews/jsc329_round1_adversarial_document_reviewer.md | next_command needed a deterministic selection ladder, contract_schemas needed consumer-usable validity, and representativeness had to be binding. |
| artifacts/reviews/jsc329_round1_architecture_strategist.md | Required fields needed semantic content, public check names needed mapping discipline, and the second skill needed a distinct representativeness axis. |
| .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md | Live Linear issue JSC-329 is the execution handle. |
| .harness/quality/steering-uptake.md | RF-0 closeout gate and repeated-feedback uptake evidence. |
| ~/dev/codex commits e7bffc5a2, f0166cadb, 4c8977231, a28024802, and 326e31ab6 | Upstream Python SDK lessons: normalize convenient inputs into typed contracts, return public domain result objects, expose attempt-local setup/login handles, split helper logic away from the facade, and test public exports/signatures. |
| openai/openai-python temporary design-reference clone | Reference architecture for Python SDK ergonomics, generated type stewardship, hosted skill resource vocabulary, version/content surfaces, cursor pagination, raw/streaming escape hatches, error taxonomy, and docs discipline; dependency use requires a concrete OpenAI API boundary and is not part of this doctor fixture slice. |

## Scope and Boundaries

In scope:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/test_ask_skills_package.py only if package comparison assertions need helper reuse
- Infrastructure/tests/fixtures/** only for stable doctor/package fixture evidence
- .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md or equivalent implementation evidence artifact
- .harness/plan and .harness/review artifacts for this planning/review chain
- Documentation updates that bind the doctor contract to upstream Codex Python SDK API-shape lessons and the openai-python reference/dependency decision

Out of scope:

- Runtime projection edits under .agents/**, .skillsets/**, skills-codex/**, or Plugins/cache/**
- Broad skill metadata migration
- Big-bang repository restructure or generic app-layer directory migration
- Package publication, sharing, install, or marketplace implementation
- coding-harness consumer changes
- Remote execution or auth-backed executor work
- Global environment or shell mutation
- Adding openai-python as a dependency without a concrete OpenAI API transport or generated-type implementation boundary

Do not proceed if implementation pressure requires an out-of-scope surface. Return to he-spec or he-reframe with the exact blocker.

## Current State / Evidence

| Evidence | Current Observation | Planning Impact |
| --- | --- | --- |
| Infrastructure/tests/test_ask_skills_doctor.py | Existing focused tests already cover pass, runtime blocked, repo-relative source, taxonomy, lifecycle event, and outcome warning behavior. | Extend this file first unless implementation discovers a cleaner fixture module. |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | skills_doctor assembles data.skill_doctor and already includes schema_version, status, target_summary, checks, blockers, warnings, contract_schemas, operation_context, check_summary, agent_summary, and next_command. | Implementation likely needs stronger fixture assertions more than broad behavior rewrite. |
| ./bin/ask skills doctor context7 --json --robot | Live probe exits 2 because readiness is blocked; the observed payload has data.skill_doctor.status=blocked, blocked_validation from structural audit, outcome_proof_missing warning, and a currently suspect next_command that points to proof before validation remediation. | Treat non-zero exit as valid blocked-readiness evidence, not contract-shape failure; PU-002 must correct or explicitly test the next_command blocker-first behavior. |
| ./bin/ask skills package context7 --json --robot | Live probe exits 0 with warning capability_contract_incomplete. | Use as comparison evidence to prove package readiness stays separate from outcome proof. |
| Infrastructure/tests/fixtures | Existing fixture root exists, but no doctor fixture directory is currently confirmed. | Add fixture files only if command-level fixture comparison is more maintainable than in-test dictionaries. |

## Decision Deepening

This pass resolves four plan-level questions that were previously too open for reliable agent execution.

| Decision Area | Decision | Rationale | Implementation Impact | Validation / Evidence |
| --- | --- | --- | --- | --- |
| Waiver authority | Waivers cannot be self-approved by the implementation agent. A valid waiver must come from Jamie, the Linear owner/assignee for JSC-329, or a named owner cited from a repo-owned authority source for Agent Skills Kit or the affected contract surface. | A waiver is a governance exception. If the same agent that failed a gate can waive it, representativeness and validation gates become decorative. | PU-005 and PU-006 must treat missing approver, missing verbatim authority source, missing follow-up, or open-ended waiver as blocked. | Closeout waiver record includes approver, authority source path/link, verbatim authority evidence, date, waived gate, reason, scope, expiry/revisit condition, and follow-up issue/artifact. |
| Concrete schema files | Do not create concrete schema files in RF-1 unless an existing canonical schema home is discovered or a focused test cannot honestly validate `contract_schemas` without file-backed truth, and a schema-file decision record proves the work cannot be deferred. | RF-1 is a doctor contract proof, not schema registry creation. Premature schema files create ownership and migration work outside the slice. | PU-001 asserts governed versioned identifiers or explicit `missing_schema_reason`; changed-file review flags new schema files unless justified by a decision record. | Closeout records either no schema files created, or a decision record with canonical schema home, why inline identifiers are insufficient, why RF-2 deferral is invalid, exact files, and future owner. |
| `sdk_layer` location | Known readiness classes must expose `sdk_layer` in production `data.skill_doctor` JSON. Fixture/evidence-only mapping is allowed only for unknown legacy classes with a documented reason. | Harness and agents cannot consume a professional SDK layer contract that exists only in tests. Production JSON must carry known ownership semantics. | PU-001 and PU-003 should add production-payload assertions, not only fixture normalizers. Known classes include source_resolution, runtime_reachability, structural_audit, package_readiness, profile_context, outcome_proof, and lifecycle_evidence. | Focused tests assert `sdk_layer` on known classes and reject generic public layers. Eval evidence preserves original class plus `sdk_layer`. |
| Imagegen fallback | Image generation is auxiliary to this review workflow and is not a JSC-329 implementation gate. Retry CLI fallback only if the user explicitly authorizes it and credentials are available. | Missing image tooling should not block the SDK doctor contract. Silent credential use or fallback would violate the imagegen skill contract. | PU-006 may record image status as generated, blocked, or skipped, but must not count it as plan/spec validation. | Current evidence: `skills-system/imagegen/scripts/image_gen.py` exists, imagegen resolves, and the default OpenAI imagegen credential was missing in this environment. |

## Confidence Review Corrections

The current plan is implementation-ready only as a bounded he-work handoff, not as a production-readiness claim. A fresh evidence pass found two live or test-level contradictions that PU-001 and PU-002 must resolve before the contract can be trusted:

| Evidence | Finding | Required Plan Adjustment |
| --- | --- | --- |
| Live `./bin/ask skills doctor context7 --json --robot` | The payload is parseable and `data.skill_doctor.status=blocked`, but the observed blocker is `blocked_validation` while `next_command` points to `./bin/ask skills proof context7 --json --robot`. | PU-002 must add a fixture for the current baseline class: structural validation blockers select the audit/validation remediation command before proof/outcome commands, or record why no blocker command is available. |
| `Infrastructure/tests/test_ask_skills_doctor.py` | The current pass test permits `checks.outcome_proof.status=available_not_run` with final `status=pass`. | PU-002 must update behavior/tests so available-not-run critical outcome proof maps to warning by default, or require explicit profile evidence that outcome proof is non-critical for that pass case. |
| Plan frontmatter and review appendix | Prior review labels say approved, but implementation has not run the new gates yet. | Closeout must report confidence as evidence-limited until focused tests, live probes, representativeness, and changed-file validation pass. |

## Implementation Strategy

Implement from the public robot contract inward.

1. Capture current doctor/package shape and decide whether to encode snapshots as fixture files or helper-generated dictionaries.
2. Add required-field shape, minimum-content, and negative-type assertions against data.skill_doctor.
3. Add SDK layer mapping assertions for known checks/blockers/warnings/evidence groups, preserving unknown or legacy classes without coercion.
4. Add status-precedence assertions that prove skipped, missing, unavailable, or not-run critical checks map to warning/blocked instead of pass.
5. Add next_command ladder assertions with mixed blocker/warning fixtures and explicit null evidence, including the live context7 class where `blocked_validation` must not route first to outcome proof.
6. Add separation assertions that prove runtime, package, and outcome-proof signals cannot satisfy each other.
7. Add or document dynamic-field normalization so volatile trace IDs and timestamps are not part of fixture truth.
8. Run a successful read-only representativeness probe against one verified additional skill class, or record a blocking waiver with owner/date/reason/follow-up issue.
9. Add apparatus-lens evidence that maps each readiness claim to its signing apparatus: typed field assertion, focused test, doctor/package command, structural audit, representativeness probe, eval artifact, changed-file validation, or rollback record.
10. Record an eval/closeout artifact that names command outcomes, SDK layer mapping, dynamic fields ignored, counterexample coverage, pattern sweep disposition, representativeness status, and validation results.

Prefer test-first work. Only change skills_impl.py when the focused tests expose real contract drift.

## Layered SDK Deepening

The layered SDK architecture is an implementation constraint for JSC-329, not a repository-moving instruction. The first executable proof is the doctor payload contract. Physical folder restructuring remains out of scope until validators can prove ownership boundaries.

Allowed public sdk_layer values:

| sdk_layer | Used For | Example Doctor Signal |
| --- | --- | --- |
| contracts | Public schemas, command payload contracts, status enums, failure taxonomy, compatibility contracts. | schema_version, contract_schemas, status enum validation. |
| catalog | Skill identity, discovery, handles, maturity, ownership, source paths, capability declarations. | source_resolution, target_summary, resolved handle metadata. |
| authoring | SKILL.md hot path, references, examples, eval declarations, source/projection ownership rules. | structural_audit findings about source shape or author-owned files. |
| validation | Doctor/lint/schema/representativeness/projection-drift/release-gate checks. | status precedence, next_command selection, skipped/not-run mapping. |
| packaging | Package metadata, install/share/upgrade/provenance/compatibility readiness. | package_readiness and package comparison warnings. |
| runtime_adapters | Codex projection, plugin cache, MCP/tool adapters, local shell, worktree and future CI/remote adapters. | runtime_reachability and adapter/tool availability blockers. |
| evidence | Review artifacts, eval outputs, validation logs, lifecycle traces, command evidence, closeout records. | outcome_proof, lifecycle_evidence, command evidence buckets. |
| memory | Durable learned fixes, prior failure patterns, steering uptake, migration notes, freshness/confidence metadata. | RF-0 steering uptake and learned-fix evidence references. |

Implementation defaults:

- Known checks MUST carry sdk_layer according to the table above in production data.skill_doctor JSON.
- Legacy or ambiguous checks MUST preserve their original class and MAY use sdk_layer: unknown.
- Generic implementation labels such as utils, providers, service, UI, types, config, or repo MUST NOT become public sdk_layer values.
- A helper should validate layer values at the boundary where data.skill_doctor is assembled or normalized for tests.
- Negative fixtures should reject generic public layer values while allowing internal detail fields to keep implementation names.
- Layer mapping is advisory for unknown legacy classes but binding for the known classes exercised by the context7 fixture.

Deepened execution order:

1. Define the allowed sdk_layer value set in the test helper or production boundary, depending on where data.skill_doctor is assembled.
2. Add fixture assertions for known class-to-layer mappings before adding broad behavior changes.
3. Add one negative fixture for a generic public layer value, such as service or utils.
4. Preserve original class names in failure output so layer mapping cannot hide the reason a check failed.
5. Record layer mapping in the eval/closeout artifact alongside command outcomes.

## Apparatus Lens Execution Rules

Infrastructure/references/skills-sdk-apparatus-lens.md is a reusable reference lens for this plan. It does not expand JSC-329 into a new static-analysis platform. It constrains how the existing doctor contract is proven.

Implementation must preserve Jamie's mantra:

- Thin surface: data.skill_doctor is the public SDK result surface; tests and closeout must assert it directly.
- Strong guardrails: at least one negative field-shape, critical skipped/not-run, blocker-first next_command, or second-skill representativeness case must fail in a named class.
- Durable memory: steering uptake, closeout evidence, and pattern-sweep disposition must capture transferable feedback instead of applying only a local patch.
- Professional output: every readiness claim must cite command output, typed test assertion, structural audit, eval/proof evidence, representativeness, changed-file validation, or rollback/supersession evidence.

Source presence, package metadata, AI review, or a coherent SKILL.md can support investigation, but cannot by itself close a readiness claim. The apparatus must stay bounded to JSC-329; do not add broad external analyzers or repository-wide migrations unless a focused doctor fixture exposes a direct contract bug.

## Enforcement Contract

essential_decisions:

- PU-001 through PU-006 implement the JSC-329 doctor fixture contract only; they do not migrate the whole Skill SDK, publish packages, edit runtime projections, or add coding-harness consumers.
- `data.skill_doctor` remains the public SDK result surface and must be asserted directly, including required field shapes, semantic content, status precedence, `contract_schemas`, `sdk_layer`, warnings, blockers, and `next_command`.
- Known readiness classes must carry production `sdk_layer` values from the domain SDK vocabulary; generic implementation buckets may appear only as internal detail or explicit mapping metadata.
- Critical skipped, missing, unavailable, or not-run readiness checks cannot produce pass unless a selected profile explicitly classifies the check as non-critical and records evidence.
- Waiver authority, schema-file creation, and representativeness gaps are governance decisions, not local implementation conveniences.

fillable_gaps:

- The worker may add test helpers, fixture files, or small production helpers inside the allowed paths when focused tests prove the need.
- The worker may select the second read-only skill probe during implementation, provided it differs from context7 by class or readiness axis and the result is recorded.
- The worker may leave concrete schema files deferred when `contract_schemas` includes governed identifiers or explicit `missing_schema_reason` metadata.

guardrails:

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q`
- `python3 -m pytest Infrastructure/tests/test_ask_skills_package.py -q` if package comparison behavior or shared helper code changes.
- `./bin/ask skills doctor context7 --json --robot`
- `./bin/ask skills package context7 --json --robot`
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`
- `python3 Infrastructure/scripts/testing/test_validate_steering_uptake.py -q`
- `./bin/ask repo validate --changed-files <changed-files> --json --robot`
- `python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-plan.md --kind plan --json`

refusal_triggers:

- Stop if a unit requires broad SDK metadata migration, runtime projection edits, package publication, coding-harness consumer implementation, remote execution, auth-backed executor work, or global shell/environment mutation.
- Stop if `next_command` cannot be made blocker-first without changing the public command contract outside the approved doctor scope.
- Stop if known readiness classes cannot expose `sdk_layer` in production JSON without coercing or hiding the original readiness class.
- Stop if a waiver is required and the approver, authority evidence, date, scope, expiry, and follow-up artifact are missing.

durable_memory:

- Record steering uptake and transferable review feedback in `.harness/quality/steering-uptake.md`, implementation closeout, and the nearest durable repo guidance surface selected by the feedback radius.
- Preserve dynamic-field normalization, representativeness, waiver, and rollback evidence so future agents can rerun the doctor contract without reconstructing intent from prose.

professional_output:

- Every PU closeout must report files changed, exact commands run, pass/fail state, blocker classes, warning classes, representativeness result, waiver status, rollback path, remaining risks, and next action.
- The final JSC-329 closeout must distinguish blocked-readiness command exits from command transport failures and must not claim SDK readiness from AI review, package presence, source presence, or coherent artifacts alone.

## Work Units

### PU-001: Establish Baseline Fixture And JSON Path Assertions

Objective: Prove that required doctor fields are asserted at data.skill_doctor with required JSON shapes, minimum semantic content, and contract_schemas validity while the outer ask robot envelope remains intact.

Source trace: FR-001, FR-012, FR-013, FR-014, SA-001, SA-011, SA-015, technical review Finding 1, Round 1 adversarial field-shape findings.

Allowed paths or areas:

- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/fixtures/skill-doctor/** if fixture files are chosen

Forbidden paths or areas:

- Runtime projections
- Coding-harness
- Skill source metadata migration

Steps:

- Inspect current test helper patterns in Infrastructure/tests/test_ask_skills_doctor.py.
- Add a focused test that calls skills_doctor through existing helper style and asserts result.data["skill_doctor"] contains schema_version, status, target_summary, checks, blockers, warnings, operation_context, contract_schemas, agent_summary, and next_command with the spec-defined shapes.
- Add negative fixtures or helper cases that reject wrong field types, empty semantic objects, empty agent_summary, opaque contract_schemas placeholders, and absent required check status values.
- Add a negative guard in the test name or assertion message that these are data.skill_doctor fields, not outer-envelope fields.
- Assert known checks, blockers, warnings, and evidence groups include or map to the spec's SDK layer values where safe: contracts, catalog, authoring, validation, packaging, runtime_adapters, evidence, and memory.
- Assert known checks, blockers, warnings, and evidence groups expose `sdk_layer` in production `data.skill_doctor` JSON. Do not satisfy this requirement solely with fixture-side normalization.
- Assert generic implementation labels such as utils, providers, service, UI, types, config, or repo do not become public readiness layers unless carried as internal detail or explicit mapping metadata.
- Preserve unknown or legacy classes as original class plus sdk_layer unknown instead of forcing misleading layer classification.
- If fixture files are used, add a normalizer helper in the test layer rather than production code unless production output needs repair.
- Assert contract_schemas is consumer-usable by requiring a governed stable name/version/owner/stability/path or an explicit missing_schema_reason. Do not create concrete schema files unless an existing canonical schema home is discovered or file-backed schemas are required for honest validation.
- Assert the doctor payload behaves like a public SDK result object: named status, named blocker/warning classes, target identity, operation context, contract schema metadata, evidence-bearing checks, and next action are available without parsing terminal prose.
- Add an apparatus-lens assertion or helper comment in the test that names the signing surface for field-contract readiness: data.skill_doctor typed fields plus negative shape coverage, not terminal prose or AI review.

Validation:

- required: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q
- required: fixture or helper assertion proves SDK layer values are present/mapped for observable readiness classes or explicitly unknown.
- required: at least one malformed or semantically empty field fixture fails with a named contract violation.

Stop condition:

- Stop if the contract requires flattening data.skill_doctor into the outer ask envelope.
- Stop if SDK layer mapping requires a repository-wide folder migration or broad metadata migration rather than a bounded doctor payload contract.

Rollback:

- Remove the new test/fixture and any production change made solely for this unit.

Handoff state:

- Continue to PU-002 after the focused doctor test passes.

Deepened layer-specific acceptance:

- Known context7 doctor checks either expose sdk_layer directly or are normalized in fixture evidence with a documented class-to-layer mapping.
- Known context7 doctor checks expose sdk_layer directly in production data.skill_doctor JSON; fixture-only mapping is allowed only for unknown legacy classes and must include a documented reason.
- The test suite rejects a public sdk_layer outside the allowed value set.
- Unknown legacy checks preserve original class and use sdk_layer unknown only when no safe mapping exists.
- The test treats data.skill_doctor as the stable SDK result surface, matching the Codex Python SDK pattern of returning a collected domain result instead of raw transport payloads.

### PU-002: Encode Status Precedence And next_command Semantics

Objective: Prove blocked outranks warning, warning outranks pass, pass requires no blockers or warnings, critical skipped/not-run states cannot pass, and next_command follows the blocker-first decision ladder for every status.

Source trace: FR-002, FR-006, FR-011, SA-002, SA-004, SA-012, SA-013.

Allowed paths or areas:

- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py only if tests expose a real behavior bug

Forbidden paths or areas:

- Generic repo doctor next-command refactors
- Broad golden-path rewrites

Steps:

- Extend existing mocked doctor tests or add helper cases for blocked, warning-only, pass, skipped critical check, not-run critical check, and mixed blocker/warning states.
- Assert status precedence through observable payloads rather than duplicating implementation logic.
- Assert next_command key presence for all observed statuses and prove its value follows this order: actionable blocker, warning-only remediation, pass proof/inspection command, explicit null with evidence that no safe command exists.
- Add a mixed blocker/warning fixture proving next_command cannot point at a warning while an actionable blocker exists.
- Add a structural-validation blocker fixture based on the current context7 class: when `blocked_validation` includes or can derive an audit/validation command, next_command must select that blocker command before `skills proof <handle>`.
- Update the existing pass fixture that currently accepts `outcome_proof.available_not_run`: final pass is invalid unless the fixture declares a profile where outcome proof is explicitly non-critical and records that classification in operation_context. The default expected status for available-not-run outcome proof is warning.
- Preserve existing non-zero error behavior when blockers are present.
- Treat skipped, missing, unavailable, and not-run critical checks as apparatus failures or warnings that must remain visible. They must not be hidden behind a coherent agent_summary.

Validation:

- required: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q

Stop condition:

- Stop if next_command semantics require changing unrelated repo doctor or golden_path behavior.

Rollback:

- Revert the focused test and any skills_doctor status/next-command change.

Handoff state:

- Continue to PU-003 only after blocked, warning, pass, critical skipped/not-run, and next_command ladder assertions pass; unresolved core contract coverage requires an owner-approved blocking waiver with date, reason, and follow-up issue.

### PU-003: Preserve Signal Separation For Runtime, Package, And Outcome Proof

Objective: Prove package readiness cannot satisfy outcome proof, runtime blockers do not hide package/outcome warnings, and each signal is classified against the correct SDK layer where known.

Source trace: FR-003, FR-004, FR-005, SA-003, SA-006, Round 1 architecture check-class mapping finding.

Allowed paths or areas:

- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/test_ask_skills_package.py only for comparison helper reuse
- Infrastructure/scripts/lib/ask/commands/skills_impl.py only if tests expose a real behavior bug

Forbidden paths or areas:

- Implementing package metadata migration
- Creating package publish/share workflows

Steps:

- Add doctor assertions that runtime_reachability, public package_readiness, and outcome_proof remain distinct checks.
- Assert runtime_reachability maps to runtime_adapters, package_readiness maps to packaging, outcome_proof maps to evidence or validation according to implementation detail, and source/catalog checks do not get collapsed into package or runtime layers.
- If implementation retains an internal capability_metadata name, assert it maps to the public package_readiness class in exported contract evidence or is documented as a non-public internal detail.
- Add comparison evidence that skills package context7 produces capability_contract_incomplete without satisfying outcome_proof.
- Confirm blockers and warnings both remain visible when runtime is blocked and outcome proof is missing.
- If production output currently lacks a required separation field, add the smallest field-preserving change and update tests.
- Record which apparatus signs off each claim: package command for distribution readiness, doctor runtime check for adapter reachability, prove/eval/outcome evidence for outcome proof.

Validation:

- required: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py Infrastructure/tests/test_ask_skills_package.py -q
- conditional: ./bin/ask skills doctor context7 --json --robot
- conditional: ./bin/ask skills package context7 --json --robot

Stop condition:

- Stop if proving separation requires changing package readiness semantics beyond doctor consumption.

Rollback:

- Revert separation assertions and any production mapping change introduced by this unit.

Handoff state:

- Continue to PU-004 after signal separation is covered.

Deepened layer-specific acceptance:

- runtime_reachability evidence maps to runtime_adapters.
- package_readiness evidence maps to packaging.
- outcome_proof evidence maps to evidence or validation with a short reason for the selected layer.
- source_resolution and target_summary evidence do not get collapsed into packaging or runtime_adapters.
- Any internal capability_metadata naming is either mapped to public package_readiness/packaging or retained only as non-public detail.

### PU-004: Normalize Dynamic Fields And Capture Evidence Artifact

Objective: Make fixture proof stable without hiding real contract drift.

Source trace: FR-007, FR-008, SA-005, SA-006, Round 1 exit-semantics finding.

Allowed paths or areas:

- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/fixtures/skill-doctor/**
- .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md

Forbidden paths or areas:

- Production code normalizers unless required by a reusable public API
- Machine-specific absolute path assertions

Steps:

- Define the dynamic fields ignored by fixture comparison: trace IDs, timestamps, event occurred_at values, durations, volatile event IDs, and machine-local temp paths.
- Assert the normalizer cannot remove schema_version, status, blocker class, warning class, command, target_summary, checks, contract_schemas, operation_context, or next_command.
- Record baseline doctor and package command outcomes in the eval artifact or equivalent closeout evidence.
- Classify ./bin/ask skills doctor context7 exit 2 with parseable robot payload and data.skill_doctor.status=blocked as blocked-readiness evidence, not command failure.
- Add an explicit command_failure or transport_failure fixture/path for cases where process failure prevents parsing a robot payload, so readiness failure and command execution failure stay separate.
- Record that baseline command evidence is apparatus input, not release-readiness output, until status precedence, signal separation, representativeness, and changed-file validation pass.

Validation:

- required: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q
- required: ./bin/ask skills doctor context7 --json --robot
- required: ./bin/ask skills package context7 --json --robot

Stop condition:

- Stop if dynamic-field normalization hides status or readiness class drift.

Rollback:

- Remove fixture/normalizer/eval additions and restore prior tests.

Handoff state:

- Continue to PU-005 after evidence is stable.

### PU-005: Run Representativeness And Pattern-Sweep Checks

Objective: Prove context7 is not the only skill that can satisfy the contract through a successful additional-skill contract parse, and prove transferable review feedback was handled as a pattern.

Source trace: FR-009, FR-010, SA-007, SA-009, SA-014.

Allowed paths or areas:

- .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md
- Infrastructure/tests/test_ask_skills_doctor.py if an additional fixture case is needed

Forbidden paths or areas:

- Broad repository-wide API refactors without a new plan
- Unbounded grep-and-edit loops

Steps:

- Verify an additional skill handle exists before using it. Candidate classes: a Harness Engineering skill such as he-plan, or a factory skill, selected by live resolve/doctor evidence.
- Select a handle that differs from context7 by at least one declared representativeness axis: plugin family, ownership boundary, lifecycle profile, or mutation policy.
- Run a read-only doctor probe for the selected handle and record whether data.skill_doctor preserves required fields with the same shape/minimum-content contract.
- Treat a missing required field in the additional skill as a blocking coverage gap unless explicitly waived with owner, date, reason, and a follow-up issue.
- Treat a missing required field in the additional skill as a blocking coverage gap unless explicitly waived by Jamie, the Linear owner/assignee for JSC-329, or a named owner cited from a repo-owned authority source for Agent Skills Kit or the affected contract surface. The implementation agent cannot self-approve the waiver.
- Perform a bounded pattern sweep for this implementation: search touched tests and skills_impl.py for similar doctor/package JSON-path assertions, status precedence assertions, and next_command assumptions.
- Perform a bounded upstream-pattern sweep: confirm the implementation did not add OpenAI transport dependencies for local validation, did not add concrete schema files without a canonical schema-home justification, and record whether any public Skill SDK result or handle naming should be deferred to a later API-shape slice.
- Record openai-python design-reference disposition: which lessons were adopted now, which are deferred to package/share/version work, and why hosted OpenAI skill resources remain distinct from local Agent Skills Kit canonical source and runtime projection.
- Classify similar cases as fixed_now, left_different_semantics, deferred_public_api, deferred_risk, or not_applicable.
- Record apparatus-lens disposition: which readiness claims are proven by command/test/eval/audit evidence now, which claims remain advisory, and which claims are deferred to RF-2 or later.

Validation:

- required: ./bin/ask skills resolve <selected-handle> --json --robot
- required: ./bin/ask skills doctor <selected-handle> --json --robot
- required: rg -n "skill_doctor|next_command|blocked_runtime|outcome_proof_missing|capability_contract_incomplete" Infrastructure/tests Infrastructure/scripts/lib/ask/commands/skills_impl.py
- required: rg -n "openai|OpenAI|TurnResult|RunInput|handle|wait\(|cancel\(" pyproject.toml Infrastructure .harness/strategy .harness/specs .harness/plan
- required: if a waiver is used, rg -n "approver|authority source|verbatim authority|expiry|revisit|follow-up|waived gate" <waiver-artifact>

Stop condition:

- Stop if the representativeness probe reveals immediate schema incompatibility outside context7 and no owner-approved waiver exists; route the incompatibility to RF-2 unless it is a direct JSC-329 bug.

Rollback:

- Remove only the representativeness evidence additions; do not revert unrelated discovered issues.

Handoff state:

- Continue to PU-006 after coverage gap or pass is recorded.

### PU-006: Closeout Validation And Review Handoff

Objective: Prove implementation is ready for human review and Linear closeout evidence.

Source trace: SA-008, SA-010, NFR-003, NFR-004.

Allowed paths or areas:

- .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md
- .harness/review/** implementation review artifact if requested
- Changed files from PU-001 through PU-005

Forbidden paths or areas:

- Staging, committing, or tracker closure unless explicitly requested
- Runtime projection edits

Steps:

- Run RF-0 steering uptake validator and regression test.
- Run focused pytest for touched tests.
- Run doctor/package probes and the successful representativeness probe, or record a waiver with owner, date, reason, and follow-up issue.
- If a waiver is used, verify it includes approver, authority source path/link, verbatim authority evidence, date, waived gate, reason, scope, expiry/revisit condition, and follow-up issue/artifact. Missing fields keep closeout blocked.
- Record the imagegen review-artifact status separately as generated, blocked, or skipped. Do not treat imagegen as a JSC-329 validation gate.
- Run changed-file repo validation.
- Record exact pass/fail/blocked outcomes and ownership classification for any blocked gate.
- If plain python3 or another canonical interpreter hangs or cannot start, classify it as environment/tooling failure before substituting an interpreter for artifact validation; implementation closeout should prefer repo wrappers or explicitly record the substitution and blocker.
- If technical or adversarial review feedback arrives, run the pattern-sweep disposition before claiming complete and update the plan/spec when the feedback is a transferable policy rule rather than a one-line issue.
- In the closeout evidence, include a short apparatus signoff table mapping field contract, status semantics, signal separation, representativeness, and changed-file validation to the exact command or artifact that signs each claim.

Validation:

- required: python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
- required: python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q
- required: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q
- conditional: python3 -m pytest Infrastructure/tests/test_ask_skills_package.py -q
- required: ./bin/ask repo validate --changed-files <changed-files> --json --robot

Stop condition:

- Stop if changed-file validation reports required failures introduced by this implementation.

Rollback:

- Revert JSC-329 implementation files and remove the new evidence artifact; then rerun the focused tests that existed before the change.

Handoff state:

- Ready for he-code-review or PR work, depending on Jamie's requested delivery path.

## Dependencies and Sequencing

| Unit | Depends On | Reason |
| --- | --- | --- |
| PU-001 | approved spec and layered SDK architecture decision | Establishes correct JSON path and SDK layer contract before any behavior work. |
| PU-002 | PU-001 | Status and next-command tests must assert the right contract object. |
| PU-003 | PU-002 | Signal separation depends on status and warning/blocker semantics. |
| PU-004 | PU-003 | Evidence snapshots should reflect the final separation behavior. |
| PU-005 | PU-004 | Representativeness and pattern sweep need stable contract/evidence. |
| PU-006 | PU-001 through PU-005 | Closeout validates all implementation evidence. |

## Validation Gates

| Gate | Phase | Required | Command | Expected Outcome |
| --- | --- | --- | --- | --- |
| Source spec exists | pre-implementation | yes | test -f .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md | exit 0 |
| Source spec has acceptance/validation/rollback/scope | pre-implementation | yes | `rg -n 'AC-\|acceptance\|validation\|rollback\|scope' .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md` | finds source contract terms |
| Required shape negative fixtures | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | rejects wrong field types, empty semantic fields, and opaque contract_schemas placeholders |
| SDK layer mapping fixtures | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | known checks/blockers/warnings/evidence groups map to approved SDK layer values or preserve original class with sdk_layer unknown |
| Production sdk_layer fields | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | known readiness classes expose sdk_layer in data.skill_doctor JSON, not only fixture mapping |
| Generic layer rejection fixture | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | public sdk_layer values such as service, utils, providers, UI, types, config, or repo are rejected unless held only as internal detail |
| Apparatus signoff mapping | implementation | yes | inspect focused fixture/eval/closeout artifact | each readiness claim cites a signing command, typed assertion, structural audit, probe, eval, validation gate, or rollback record |
| Counterexample-style fixture | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | malformed fields, critical skipped/not-run state, or blocker-first next_command case fails in a named class instead of passing |
| Schema-file scope check | closeout | yes | git diff --name-only -- '*.schema.json' 'schemas/**' | no new schema files unless closeout includes a schema-file decision record with canonical schema home, why inline identifiers are insufficient, why RF-2 deferral is invalid, exact files, and future owner |
| Focused doctor tests | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | exits 0 |
| Critical skipped/not-run mapping | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | skipped, missing, unavailable, or not-run critical checks map to warning/blocked, never pass |
| next_command ladder fixtures | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | mixed blocker/warning fixtures select the actionable blocker first |
| blocked_validation remediation fixture | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | structural validation blockers select audit/validation remediation before outcome-proof commands, or record why no blocker command exists |
| available-not-run outcome proof mapping | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | available_not_run critical outcome proof maps to warning unless operation_context explicitly marks it non-critical for the selected profile |
| Exit/payload semantics | implementation | yes | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | blocked readiness with parseable payload is distinct from command_failure or transport_failure |
| Package comparison tests | implementation | conditional | python3 -m pytest Infrastructure/tests/test_ask_skills_package.py -q | exits 0 when package test/helper touched |
| RF-0 steering validator | closeout | yes | python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json | exits 0 |
| RF-0 steering tests | closeout | yes | python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q | exits 0 |
| Context7 doctor probe | closeout | yes | ./bin/ask skills doctor context7 --json --robot | output captured; exit 2 may be valid blocked-readiness evidence |
| Context7 package probe | closeout | yes | ./bin/ask skills package context7 --json --robot | output captured; warning stays separate from outcome proof |
| Representativeness probe | closeout | yes | ./bin/ask skills doctor <selected-handle> --json --robot | required fields present with valid shapes, or blocking waiver includes owner/date/reason/follow-up issue |
| Waiver authority check | closeout | conditional | inspect waiver artifact | any waiver includes approver, authority source path/link, verbatim authority evidence, date, waived gate, reason, scope, expiry/revisit, and follow-up; otherwise gate remains blocked |
| Imagegen artifact status | closeout | informational | ./bin/ask skills resolve imagegen --json; check credentials for configured imagegen backend if fallback is requested | image status recorded separately as generated, blocked, or skipped; missing credentials do not fail JSC-329 |
| Changed-file repo validation | closeout | yes | ./bin/ask repo validate --changed-files <changed-files> --json --robot | required_failures=0 |

## Review Plan

Technical review should check:

- Tests assert data.skill_doctor, not the outer envelope.
- Required fields have JSON shape and minimum-content assertions, not presence-only checks.
- Readiness signals use the layered SDK vocabulary: contracts, catalog, authoring, validation, packaging, runtime_adapters, evidence, and memory.
- Generic app-layer labels are not exposed as public SDK readiness layers without explicit mapping metadata.
- contract_schemas is consumer-usable or carries an explicit missing_schema_reason.
- next_command behavior is selected by the deterministic blocker-first ladder and intentionally nullable only with evidence.
- Status precedence is tested without duplicating implementation internals.
- Critical skipped, missing, unavailable, or not-run checks cannot produce pass.
- Runtime, package, and outcome-proof evidence remain separate.
- Internal package/capability metadata names are mapped to the public package_readiness class.
- Dynamic-field normalizer cannot hide required contract drift.
- Exit/payload semantics distinguish readiness failure from command or transport failure.
- The representativeness probe is real, read-only, successful, and selected from a distinct skill axis unless a blocking waiver is recorded.
- Any waiver has external authority, cites a recognized authority source, and is not self-approved by the implementation agent.
- Known readiness classes expose sdk_layer in production JSON.
- Concrete schema files are not created unless justified by discovered schema-home evidence or focused-test necessity.
- Imagegen status is reported separately from JSC-329 validation.
- The pattern sweep disposition covers similar JSON-path, status, and next-command assumptions in touched areas.
- Apparatus signoff is explicit: every readiness claim in closeout points to command output, typed test assertion, structural audit, eval/proof evidence, representativeness, changed-file validation, or rollback/supersession evidence.
- AI review, source presence, package presence, or polished summaries are not used as standalone readiness proof.

Use api-contract and testing review lenses if a review swarm is requested.

## Rollback Plan

Rollback is file-scoped:

- Remove new doctor contract tests and fixture files.
- Revert any skills_impl.py behavior change introduced by JSC-329.
- Remove or supersede the JSC-329 eval evidence artifact if it only describes the reverted behavior.
- Rerun python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q.
- Rerun ./bin/ask skills doctor context7 --json --robot and classify its result against the pre-change baseline.

Do not rollback unrelated dirty worktree files.

## Risk Register

| Risk | Consequence | Mitigation |
| --- | --- | --- |
| Wrong JSON path asserted | Tests push implementation toward a broken robot envelope. | PU-001 asserts data.skill_doctor explicitly. |
| Overfitted context7 fixture | RF-1 looks green while other skill classes fail immediately. | PU-005 representativeness probe. |
| Package readiness confused with proof | Professional SDK reports false readiness. | PU-003 package/outcome separation assertions. |
| Generic layer naming leaks into public SDK contract | Agents route feedback to broad implementation buckets instead of the correct domain ownership layer. | PU-001 and PU-003 SDK layer mapping assertions. |
| Presence-only required fields | Wrong-typed or empty contract payloads pass while consumers fail. | PU-001 shape/minimum-content negative fixtures. |
| Skipped critical checks smoothed into pass | Professional output hides missing validation and overstates readiness. | PU-002 critical skipped/not-run mapping tests. |
| next_command points at the wrong fix | Operators chase warnings while actionable blockers remain. | PU-002 deterministic blocker-first ladder tests. |
| blocked_validation routes to outcome proof | Operators run proof/eval commands while structural validation is still blocking trust. | PU-002 structural-validation blocker fixture selects audit/validation remediation first. |
| available-not-run outcome proof passes by default | Doctor reports success without behavioral proof or explicit profile rationale. | PU-002 maps available-not-run critical outcome proof to warning unless operation_context marks it non-critical. |
| Internal check names leak as public contract | Consumers bind to unstable implementation terms. | PU-003 public package_readiness mapping assertion. |
| Non-zero blocked readiness treated as command failure | Valid blocked evidence is discarded. | PU-004 records exit behavior separately from contract shape. |
| Broad SDK migration creep | JSC-329 becomes slow and unsafe. | Scope boundaries and SA-010 changed-file review. |
| Layer mapping hides original failure class | Operators see an architecture bucket but lose the actionable blocker. | Preserve original class and add sdk_layer as supplemental metadata. |
| sdk_layer exists only in tests | Harness consumers cannot consume layer ownership from production doctor JSON. | Require production data.skill_doctor sdk_layer fields for known readiness classes. |
| Self-approved waiver bypasses evidence | Agents can convert blocked representativeness into apparent success without owner accountability. | Waivers require external approver, verbatim recognized authority source, expiry/revisit, and follow-up. |
| Premature schema files expand scope | RF-1 turns into schema registry design before doctor contract is stable. | Defer concrete schema files unless a canonical schema home is discovered or tests require file-backed truth, and require a schema-file decision record before closeout. |
| Imagegen fallback silently uses credentials | Auxiliary infographic work creates hidden external dependency or blocks core JSC-329. | Imagegen is informational only; CLI fallback requires explicit user authorization and credentials. |
| Layer architecture turns into premature folder migration | Planning churn replaces the doctor contract proof. | Keep physical restructuring out of scope; prove command contract first. |
| Feedback applied only locally | Same API-contract issue recurs elsewhere. | PU-005 pattern sweep and disposition. |
| Canonical Python interpreter hangs or is unavailable | Validation evidence becomes ambiguous or silently uses a different runtime. | PU-006 requires environment/tooling failure classification before interpreter substitution. |
| Artifact mistaken for apparatus | A coherent skill file, package summary, or AI review is treated as SDK readiness. | Apparatus signoff mapping requires concrete command, test, audit, eval, probe, validation, or rollback evidence for each readiness claim. |
| Verification theater expands scope | JSC-329 becomes a broad analyzer/platform effort instead of a doctor contract proof. | Apply the smallest credible apparatus for this claim and defer broader matrices to RF-2 or later. |

## Observability and Evidence

Implementation closeout must record:

- exact tests run and outcomes;
- interpreter/runtime used for validation, plus blocker classification if it differs from the canonical command;
- doctor/package command exit codes and readiness classifications;
- SDK layer values or unknown/mapping metadata for checks, blockers, warnings, and evidence groups;
- ignored dynamic fields and why they are non-semantic;
- selected representativeness handle, declared distinct axis, and result;
- any representativeness waiver owner/date/reason/follow-up issue;
- waiver approver authority source path/link, verbatim authority evidence, expiry/revisit condition, and follow-up artifact when a waiver is used;
- whether sdk_layer values were emitted in production JSON or only unknown legacy classes required fixture/evidence mapping;
- schema-file decision and justification if any schema files were created;
- imagegen artifact status and blocker if image generation was requested;
- pattern sweep scope, matches, and disposition;
- changed-file validation result;
- apparatus signoff table for field contract, status semantics, signal separation, representativeness, and changed-file validation;
- rollback notes if any behavior was reverted.

## Visual References / Diagrams

| Visual Element | Clarifies |
| --- | --- |
| Execution sequence | The ordered path from fixture path assertion to validation closeout. |
| Layered SDK boundary | How contracts, catalog, authoring, validation, packaging, runtime adapters, evidence, and memory constrain doctor classification. |

~~~mermaid
flowchart TD
  A["PU-001 data.skill_doctor required fields + SDK layers"] --> B["PU-002 status and next_command"]
  B --> C["PU-003 runtime/package/outcome separation"]
  C --> D["PU-004 dynamic-field normalization and evidence"]
  D --> E["PU-005 representativeness and pattern sweep"]
  E --> F["PU-006 closeout validation"]
~~~

## Accessibility and Operator Ergonomics

The implementation should improve machine readability without making human output more obscure. If production code changes are needed, agent_summary should remain compact, blockers and warnings should remain scanable, and validation output should distinguish blocked, warning, pass, skipped, and not-run states.

Layer names should help operators orient, not replace actionable evidence. Human summaries should mention the failed class and next command first, with sdk_layer as supporting context.

## Open Questions

| ID | Question | Default |
| --- | --- | --- |
| OQ-001 | Should fixtures be file-backed under Infrastructure/tests/fixtures/skill-doctor or helper-backed inside test_ask_skills_doctor.py? | Start helper-backed; move to fixture files only if snapshots become bulky. |
| OQ-002 | Which additional skill handle should represent the second skill class? | Verify he-plan first because it has a different Harness Engineering ownership boundary/profile from context7; if live resolution disproves that axis, choose a factory skill. |
| OQ-003 | Does RF-1 need concrete schema files for contract_schemas? | No, unless implementation discovers an existing schema home; RF-1 asserts governed stable identifiers or explicit missing_schema_reason. |
| OQ-004 | Should this slice restructure repository folders around the layered SDK model? | No. Command contracts and validation semantics move first; physical restructuring follows only after validators prove ownership boundaries. |
| OQ-005 | Who can approve representativeness, schema, or validation waivers? | Jamie, the Linear owner/assignee for JSC-329, or a named owner cited from a repo-owned authority source for Agent Skills Kit or the affected contract surface; implementation agents cannot self-approve. |
| OQ-006 | Should sdk_layer be production JSON or fixture/evidence mapping? | Production JSON for known readiness classes; fixture/evidence mapping only for unknown legacy classes with a documented reason. |
| OQ-007 | Should image generation be retried through CLI fallback if credentials are provided? | Only if the user explicitly authorizes fallback and credentials are available; it remains auxiliary and not a JSC-329 validation gate. |
| OQ-008 | Is this lens a reference or a persona? | Reference lens. It encodes reusable verification questions without turning an essay into a reviewer persona that could outrank command evidence. |

## Final Decision

Proceed to he-work with PU-001 as the first unit. Keep the implementation bounded to doctor contract tests/evidence and only touch production code if the focused tests expose a real contract gap.

## Appendix A. Harness Metadata / Traceability

| Field | Value |
| --- | --- |
| Selected stage | he-plan |
| Mode | standard-plan plus deepen pass |
| Source spec | .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md |
| Source technical review | .harness/review/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec-technical-review.md |
| Layered SDK plan technical review | .harness/review/2026-05-17-agent-skills-jsc-329-layered-sdk-plan-technical-review.md |
| Linear issue | JSC-329 |
| Handoff target | he-work |
| First unit | PU-001 |
| Apparatus lens | Infrastructure/references/skills-sdk-apparatus-lens.md |

## Appendix B. Linear / Tracker Handoff

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | JSC-329 |
| URL | https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7 |
| Team | JSC |
| Workspace | Jscraik |
| Status | Triage |
| Priority | High |
| Plan result | Ready for he-work after technical review |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| JSC-329 | SA-001, SA-011 | PU-001 | data.skill_doctor required-field shape and minimum-content assertions | PR evidence pending implementation. |
| JSC-329 | SA-015 | PU-001, PU-003 | layered SDK readiness classification for checks, blockers, warnings, and evidence groups | PR evidence pending implementation. |
| JSC-329 | SA-002, SA-004, SA-012, SA-013 | PU-002 | status precedence, critical skipped/not-run mapping, and next_command ladder assertions | PR evidence pending implementation. |
| JSC-329 | SA-003, SA-006 | PU-003 | runtime/package/outcome separation and public package_readiness mapping assertions | PR evidence pending implementation. |
| JSC-329 | SA-005 | PU-004 | dynamic-field normalization, baseline evidence, and exit/payload semantics | PR evidence pending implementation. |
| JSC-329 | SA-007, SA-009, SA-014 | PU-005 | successful representativeness probe and pattern-sweep disposition | PR evidence pending implementation. |
| JSC-329 | SA-008, SA-010 | PU-006 | RF-0 steering validation and changed-file validation | PR evidence pending implementation. |
| JSC-329 | SA-020, SA-021 | PU-001 through PU-006 | apparatus signoff mapping and counterexample-style fixture/probe coverage | PR evidence pending implementation. |

## Appendix C. Review Outcomes

### Deepen Pass Result

| Check | Result |
| --- | --- |
| Every PU maps to source SA/FR IDs. | passed |
| Every PU has allowed paths, forbidden paths, validation, stop condition, and rollback. | passed |
| Plan distinguishes implementation validation from closeout validation. | passed |
| Plan carries data.skill_doctor correction from the spec technical review. | passed |
| Plan includes pattern-sweep disposition for transferable feedback. | passed |
| Round 1 adversarial findings on field shapes, next_command, skipped critical checks, check-class mapping, exit semantics, contract_schemas, and representativeness are encoded in work units and validation gates. | passed |
| Round 2 adversarial findings on representativeness gate semantics and PU-002 continuation are resolved. | passed |
| Round 3 adversarial reviewer and architecture strategist approved the spec and plan with no blocking findings. | passed |
| Round 3B replacement document reviewer blocker on readiness metadata drift is resolved in frontmatter and appendix status. | passed |
| Layered SDK architecture is deepened into implementation defaults, fixture gates, source traceability, risk handling, and operator ergonomics. | passed |
| Layered SDK plan technical review approved the deepened plan with no blocking findings. | passed |
| Apparatus lens is integrated as a reference lens with bounded implementation gates and no broad verifier-platform expansion. | passed |

Technical review status: layered_sdk_technical_review_approved.
