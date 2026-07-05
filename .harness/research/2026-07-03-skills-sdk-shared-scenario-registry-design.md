# Skills SDK Shared Scenario Registry Design

Date: 2026-07-03

Status: design-only recommendation

Source thread: `019f0314-ba59-7a00-ab78-9bd3174d1d03`

## Executive Recommendation

Create a governed Skills SDK scenario registry, but do not make it a directly
loadable scenario database.

The registry should be a source library of reusable scenario seeds with
provenance, score history, domain tags, adaptation rules, and lifecycle state.
Skills should consume those seeds only through authenticated and authorized
Skills SDK pipeline stages that produce local adapted scenarios, validation
receipts, and package-owned criteria.

This is valuable because the current repo has broad scenario coverage spread
across many skill packages, but reuse is mostly implicit. A shared registry can
reduce repeated scenario design work, help new or external skills start with
stronger eval coverage, and turn successful cases into reusable assets.

The same idea becomes unsafe if it is implemented as a loose shared bucket. A
global scenario must never become runtime authority, replace skill-specific
criteria, or let a raw skill folder claim coverage by pointing at central data.

## Evidence Reviewed

- `Infrastructure/scripts/lib/ask/skills_sdk/scenario_quality.py` already blocks unsupported acceptance shapes and coordinates release scenario, generated fixture, parity, and rubric checks.
- `Infrastructure/scripts/lib/ask/skills_sdk/scenario_quality_contracts.py` already uses strict Pydantic contracts for scenario-quality receipts.
- `Infrastructure/scripts/lib/ask/skills_sdk/scenario_set_parity.py` already compares canonical skill evals, reviewed fixture notes, staged Tessl scenarios, and Tessl score receipts.
- `Skills/agent-ops/sdk-scenario-generator/SKILL.md` already requires scenario failures to be classified before edits and routes repeated downstream failures into earlier SDK quality gates.
- `Skills/agent-ops/evals-router/SKILL.md` already separates scorer, criteria, task, runtime, and pipeline guardrail ownership.
- Repo inventory found 163 `evals.yaml` files under Skills and Infrastructure, 83 skill-local `references/evals.yaml` files, 23,836 `expected_signal` mentions, 34 `release_scenario_sets` mentions, and only 1 existing shared-registry-like mention.

## Core Invariant

Shared scenarios are seed/source assets, not runtime authority.

The authoritative scenario universe for a skill remains its local package
surface after SDK-mediated adaptation:

- `<skill>/references/evals.yaml` for canonical skill eval cases.
- `<skill>/references/evals/*.md` for reviewed generated fixture notes when used.
- SDK receipts for scenario-quality, scorer-quality, scorer-calibration,
  oss-local, oss-cloud, Tessl dry-run, and Tessl score proof.

The registry may suggest, seed, or adapt scenarios. It must not be directly
loaded by a skill at runtime, by Tessl staging, or by ad hoc scenario runners.

## SDK-Only Consumption

### Enforcement Model

Enforce SDK-only consumption with three layers:

1. No direct references:
   - Block `registry://`, `shared_scenario_ref`, `canonical_scenario_id`, or registry paths in `SKILL.md` and `references/evals.yaml` unless an SDK adaptation receipt exists for the target case.
   - Treat direct registry references from raw skill folders, external installs, generated files, or ad hoc loaders as blockers.

2. Local adaptation required:
   - The SDK must materialize an adapted local scenario into the target skill package.
   - The local scenario must have its own task text, local acceptance criteria, domain fit check, and fixture references.
   - The registry source id may appear only as provenance metadata, not as the executable criteria authority.

3. Receipt-backed coverage:
   - A registry-derived scenario counts as coverage only after the SDK writes a scenario adaptation receipt and scenario-quality validates the adapted local package.
   - Scorer-quality and scorer-calibration remain required when the adapted scenario changes scorer behavior.
   - OSS or Tessl evidence can promote confidence, but it cannot replace the local adaptation receipt.

### Direct Answers

1. How do we enforce SDK-only consumption?

   Use a validator in the Skills SDK quality path that rejects direct registry
   references unless a current adaptation receipt proves the scenario was
   imported through an authorized SDK stage. Raw skill package loading, external
   install copying, Tessl staging, and ad hoc runners must read only local
   package scenarios.

2. What receipt/schema proves authorized adaptation?

   Add `skills-sdk.scenario-adaptation-receipt.v0`. It should record the
   registry source, target package, SDK command, authorized stage, local case id,
   transformed task and criteria ownership, fixture asset handling, validation
   commands, and receipt refs.

3. What validator blocks unauthenticated or direct scenario use?

   Add `validate_no_direct_registry_scenario_use.py` and call it from
   scenario-quality and package verify. It blocks registry references in
   `SKILL.md`, `references/evals.yaml`, Tessl staged payloads, and generated
   fixture notes when the target case lacks a matching adaptation receipt.

4. How does this integrate with skill-factory, skill-installer, skill-builder,
   skillify, sdk-scenario-generator, and evals-router?

   Each surface may request registry suggestions or adaptations, but none may
   copy or execute registry scenarios directly. They must call SDK adaptation
   commands and carry the resulting receipt into the next gate.

5. What migration rule applies to existing skill-local scenarios?

   Existing skill-local scenarios remain canonical local scenarios. They should
   not be replaced by registry references. Successful existing scenarios can be
   proposed for registry promotion with provenance and evidence, but local
   packages keep owning their criteria.

## Registry Entry Shape

Each registry scenario seed should have a strict schema such as
`skills-sdk.scenario-registry-entry.v0` with these fields:

- `canonical_scenario_id`: stable global id.
- `version`: semver or monotonic registry version.
- `title`: human-readable scenario purpose.
- `domain_tags`: domain, artifact type, skill family, and target user.
- `capability_tags`: routing, safety, proof, docs, refactor, release, install, or other capability labels.
- `source_skill`: original skill package path or external source package id.
- `source_case_id`: original local case id.
- `source_commit`: commit or immutable source digest.
- `scenario_contract_type`: routing_smoke, release_behavior, negative_boundary, pressure_case, generated_fixture, scorer_calibration, or regression.
- `required_fixture_assets`: fixture paths, generated notes, staged files, or none.
- `adaptation_rules`: what must be localized before use.
- `nonportable_assumptions`: assumptions that must be removed or rewritten.
- `acceptance_schema`: allowed acceptance types and required fields.
- `scorer_rubric_mapping`: scorer dimensions and calibration labels.
- `proven_gates`: latest known pass, fail, or blocked gates with receipt refs.
- `score_history`: oss-local, oss-cloud, Tessl, and internal trend refs.
- `provenance`: owner, creation source, source evidence, and review evidence.
- `promotion_status`: candidate, promoted_seed, deprecated, quarantined, or retired.
- `demotion_reason`: required when status is deprecated, quarantined, or retired.

## Adaptation Receipt Shape

Add `skills-sdk.scenario-adaptation-receipt.v0` with strict fields:

- `schema_version`.
- `operation`: scenario_registry_adapt.
- `authorized_stage`: skill_creation, skill_install, skill_update, skill_refactor, skill_builder_audit, scenario_generation, eval_routing, or repair_loop.
- `operator_context`: SDK command, user-approved source, and workspace identity without secrets.
- `registry_source`: scenario id, version, digest, and registry path.
- `target_skill`: skill path, package id, and source head.
- `target_case_id`: local case id written to `references/evals.yaml`.
- `localization_summary`: what changed for the target domain.
- `criteria_ownership`: proof that local criteria are now authoritative.
- `fixture_asset_plan`: copied, generated, staged, omitted, or blocked.
- `acceptance_mapping`: registry acceptance fields to local accepted SDK types.
- `domain_fit`: why this scenario is valid for the target skill.
- `nonportable_assumptions_removed`.
- `validation`: command refs and outcomes for package verify, scenario-quality, and any scorer gates.
- `mutation_manifest`: exact files changed.
- `blockers`: empty only when adaptation can count as coverage.

## Validators And Ratchets

Recommended deterministic controls:

1. `validate_scenario_registry.py`
   - Validates registry entry schema, provenance, unique ids, lifecycle state,
     score history refs, and fixture asset declarations.

2. `validate_no_direct_registry_scenario_use.py`
   - Blocks raw registry references in skill packages unless backed by a
     matching adaptation receipt.

3. `validate_scenario_adaptation_receipts.py`
   - Validates receipt schema and checks receipt target case, target package,
     source digest, and file mutation manifest.

4. Scenario-quality integration
   - Add checks:
     - `registry_source_requires_adaptation_receipt`
     - `registry_case_not_runtime_authority`
     - `registry_adaptation_local_criteria_present`
     - `registry_domain_tags_match_skill_family`
     - `registry_generic_coverage_not_domain_specific`
     - `registry_fixture_assets_staged`
     - `registry_receipt_head_current`

5. Scenario-set parity integration
   - Extend parity so adapted registry cases must appear in local canonical
     evals and staged Tessl sources by local case id, not by registry id.

6. Scorer-quality integration
   - Reject boilerplate expected signals imported from registry seeds without
     local domain evidence.

7. Release ratchet integration
   - Do not count registry-derived cases toward release coverage until the
     local adaptation receipt and scenario-quality receipt both pass.

## Consumption By SDK Surface

### skill-factory

Skill Factory can request registry suggestions during creation or update, but
must write adapted local cases through the SDK command path. It must not vendor
registry cases directly into a package.

### skill-installer

External installs can use the registry only after intake identifies the target
skill family and runs SDK adaptation. Direct registry dependencies in an
external package should be stripped, rewritten, or blocked.

### skill-builder

Skill Builder should audit for direct registry use, missing adaptation receipts,
weak local criteria, generic coverage, and stale source digests. It can propose
registry seeds for coverage gaps, but package verification should fail if those
seeds are not adapted locally.

### skillify

Skillify can promote successful local scenarios as registry candidates after
they pass provenance and evidence checks. Promotion does not remove the local
scenario from the source skill.

### skill-refactor

Skill Refactor can dedupe or align scenario families by using registry
provenance. It should replace copy-paste drift with local adapted descendants,
not shared runtime references.

### sdk-scenario-generator

SDK Scenario Generator owns the review and adaptation workflow. It should:

- Suggest registry candidates for named gaps.
- Generate local adapted cases.
- Write adaptation receipts.
- Rerun scenario-quality before the cases count as coverage.
- Treat Tessl rejection of adapted cases as evidence for earlier SDK guardrail
  repair.

### evals-router

Evals Router uses registry metadata for coverage audits, scorer calibration
ideas, and failure classification. It should not treat registry scores as
release evidence without local labels, local criteria, and receipts.

## Migration Rule

Existing skill-local scenarios are grandfathered as local canonical scenarios.
They do not need registry adaptation receipts unless they later claim registry
provenance or are rewritten from a registry seed.

For new or touched skills:

- No direct registry references in `SKILL.md`.
- No direct registry references in `references/evals.yaml` unless they are
  provenance-only and backed by an adaptation receipt.
- Registry scenarios must enter through SDK adaptation commands.
- Local criteria remain authoritative.
- Local package validation must pass before coverage is counted.

For existing high-performing scenarios:

- Promotion to registry is optional and evidence-based.
- Promotion requires provenance, current local receipts, domain tags, and review.
- Promotion records a source link but does not rewrite the local package into a
  registry dependency.

## MVP

1. Add schemas:
   - `Infrastructure/config/schemas/skills-sdk/scenario-registry-entry.v0.schema.json`
   - `Infrastructure/config/schemas/skills-sdk/scenario-adaptation-receipt.v0.schema.json`

2. Add registry root:
   - Current layout: `Infrastructure/config/skills-sdk/scenario-registry/`
   - Future layout after repo migration: `skills-sdk/artifacts/scenario-registry/`

3. Add validators:
   - `Infrastructure/scripts/validation-and-linting/validate_scenario_registry.py`
   - `Infrastructure/scripts/validation-and-linting/validate_no_direct_registry_scenario_use.py`
   - `Infrastructure/scripts/validation-and-linting/validate_scenario_adaptation_receipts.py`

4. Add SDK commands:
   - `./bin/ask sdk eval scenario-registry suggest <skill> --json --robot`
   - `./bin/ask sdk eval scenario-registry adapt <skill> --scenario <id> --preview --json --robot`
   - `./bin/ask sdk eval scenario-registry adapt <skill> --scenario <id> --apply --json --robot`

5. Wire scenario-quality:
   - Registry-derived coverage is blocked without a valid adaptation receipt.
   - Direct global references are blocked.
   - Generic registry seeds cannot satisfy domain-specific release coverage
     without local domain evidence.

6. Add tests:
   - Direct registry reference in `SKILL.md` blocks.
   - Direct registry reference in `references/evals.yaml` blocks.
   - Adapted local case with valid receipt passes the registry-use guard.
   - Stale source digest blocks.
   - Missing fixture asset blocks.
   - Generic seed cannot count as domain-specific coverage without domain tags
     and local criteria.

## Risks

- A shared registry can encourage generic scenarios that pass everywhere but
  prove little.
- Scenario score history can become stale and falsely trusted.
- Registry ids can become hidden authority if direct references are allowed.
- Copy-on-write adaptation can drift without receipt checks.
- External installed skills may smuggle registry dependencies unless intake
  blocks them.
- Tessl scores can be misread as local SDK proof unless the proof lanes remain
  separate.

## How This Prevents Repeated Steering

The registry design turns repeated eval repair lessons into a reusable but
governed asset. The important ratchet is not the registry itself. The ratchet is
that every reuse must leave:

- local adapted scenarios,
- local criteria,
- provenance,
- an adaptation receipt,
- scenario-quality proof,
- and owner-classified blockers when adaptation is invalid.

That makes repeated scenario drift visible before oss-local, oss-cloud, or
Tessl lanes spend time rediscovering the same quality defects.

## Open Decisions

- Should the first registry be JSONL for easy diffing, or one YAML file per
  scenario for review ergonomics?
- Should registry promotion require oss-local proof only, or oss-local plus
  scorer-calibration?
- Should registry demotion be automatic when downstream adapted cases regress,
  or advisory until multiple skills report the same failure?
- Should KnowledgeOS capsules be allowed as registry source evidence directly,
  or only through a skill-local scenario that already passed SDK gates?

## Non-Goals

- No direct runtime scenario loading.
- No central registry scenario counts as package coverage by itself.
- No Tessl upload from the registry root.
- No replacement of skill-local `references/evals.yaml` as the canonical
  package scenario surface.
- No implementation in this design slice.
