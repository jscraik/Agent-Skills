---
schema_version: 1
artifact_id: agent-skills-jsc-329-skill-sdk-doctor-contract-spec
artifact_type: he-spec
canonical_slug: jsc-329-skill-sdk-doctor-contract
title: Agent Skills Kit Skill SDK Doctor Contract Spec
harness_stage: he-spec
status: ready_for_he_plan
date: 2026-05-17
origin: .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
source_reframe: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
source_strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
risk: medium-high
depth: full-contract
spec_depth: full
ui: false
traceability_required: true
linear_mutation_status: created
linear_issue: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
linear_team: JSC
linear_workspace: Jscraik
linear_status: Triage
linear_priority: 2
linear_labels: [agent-skills, Governance, Reliability, Developer Experience, Roadmap: Next, Feature]
review_status: approved_for_he_plan
deepen_status: completed
confidence_review_status: updated_after_adversarial_plan_review
decision_deepening_status: updated_for_waiver_schema_layer_imagegen_decisions
apparatus_lens_status: integrated
apparatus_lens: Infrastructure/references/skills-sdk-apparatus-lens.md
---

# Agent Skills Kit Skill SDK Doctor Contract Spec

## Command Summary

BLUF: This spec defines the RF-1 behavior contract for making ./bin/ask skills doctor context7 --json --robot the first fixture-backed readiness spine for the Agent Skills Kit professional Skill SDK. It matters because Jamie, Codex, and future harness consumers need one command contract that distinguishes SDK layers, runtime blockers, package warnings, outcome-proof gaps, status precedence, and safe next action without reading skill internals. The decision is to keep JSC-329 narrow: prove the doctor contract for context7, preserve RF-0 steering-uptake validation, encode the layered SDK boundary model, apply the Skills SDK apparatus lens, and defer broader SDK metadata migration until this command-level trust contract passes focused validation.

Decision Needed: Treat this spec as the acceptance contract for JSC-329 and hand it to he-plan only after technical review accepts the contract.

Top Risks: The implementation can accidentally turn a fixture slice into a broad SDK rewrite; generic app-layer names can obscure skill SDK ownership; package readiness can be mistaken for outcome proof; runtime blockers can hide warnings that still matter; review feedback can be applied as a one-line patch instead of a bounded design-rule sweep; polished artifacts or AI review can be mistaken for the verification apparatus that must sign off readiness.

Next Action: Run technical review against this spec, then plan JSC-329 implementation with tests and snapshots that prove the required doctor JSON contract.

## Purpose

JSC-329 exists to prove the smallest professional SDK readiness behavior before wider Agent Skills Kit packaging, marketplace, profile, event, or harness-consumer work begins.

The purpose of this spec is to make that proof testable. It defines the doctor JSON fields, status semantics, signal separation, validation evidence, and closeout conditions required for context7 to act as the first contract fixture.

## Layered SDK Architecture

Agent Skills Kit SHOULD be framed as a layered domain SDK, not a generic app stack and not a folder of prompts. The architecture model for JSC-329 is:

~~~text
Canonical skill source
  -> SDK contract
    -> validation/proof
      -> projection/runtime/package surfaces
        -> evidence/memory
~~~

The domain layers are:

| Layer | Owns | Boundary Rule |
| --- | --- | --- |
| Contracts | Public SDK schemas, command payloads, status enums, lifecycle events, failure taxonomy, and compatibility contracts. | JSON contracts and schema-versioned payloads belong here; consumers must not infer contract truth from prose. |
| Catalog | Skill identity, discovery, category, role compatibility, maturity, ownership, source paths, and capability declarations. | Catalog answers what the skill is and where source truth lives; it does not prove runtime or outcome readiness. |
| Authoring | SKILL.md hot path, references, examples, eval definitions, author guidance, and hot-path budgets. | Authoring remains source-owned; generated projections and runtime cache files are not edited as canonical authoring source. |
| Validation | doctor, lint, schema validation, representativeness, projection drift, package readiness checks, and release gates. | Validation classifies readiness; it does not hide skipped checks, runtime blockers, or evidence gaps behind polished summaries. |
| Packaging | package metadata, install/share/upgrade rules, provenance, compatibility, and marketplace-like readiness. | Package readiness is distribution readiness, not outcome proof or runtime reachability. |
| Runtime Adapters | Codex projection, plugin cache, MCP/tool adapters, local shell, worktree runners, and future CI/remote execution adapters. | Runtime adapters may discover or execute, but they do not own canonical skill source or public SDK contracts. |
| Evidence | review artifacts, eval outputs, validation logs, lifecycle traces, command evidence, and closeout records. | Evidence must preserve pass, warning, blocked, skipped, and not-run distinctions with exact command provenance. |
| Memory | durable learned fixes, prior failure patterns, steering uptake, examples, migration notes, freshness/confidence metadata. | Memory informs orientation but cannot override live validation or schema-versioned contracts without a recheck. |

JSC-329 does not restructure the repository. It requires the doctor contract to classify readiness using these layer names so future restructuring has a stable target. Folder names such as utils, providers, service, runtime, UI, types, config, and repo are implementation aids only; the public SDK vocabulary SHOULD use Contracts, Catalog, Authoring, Validation, Packaging, Runtime Adapters, Evidence, and Memory.

## Apparatus, Not Artifact Lens

JSC-329 applies Infrastructure/references/skills-sdk-apparatus-lens.md as a reference lens, not a broad implementation mandate.

The rule for this slice is Jamie's mantra: Thin surface. Strong guardrails. Durable memory. Professional output.

For skills doctor, the thin surface is data.skill_doctor. The strong guardrails are typed field assertions, status precedence, structural audit, package comparison, outcome-proof classification, representativeness, and changed-file validation. Durable memory is the steering uptake and closeout evidence that prevents repeated local-only corrections. Professional output is explicit pass/warning/blocked status with blocker classes, warnings, next command, and rollback evidence.

The lens changes JSC-329 in four concrete ways:

- readiness claims MUST name the apparatus that proves them, such as schema field assertions, status precedence fixtures, package comparison probes, representativeness checks, and changed-file validation;
- AI review, prose summaries, package presence, and source existence are advisory unless tied to command or artifact evidence;
- skipped, missing, available-not-run, blocked, or unavailable checks MUST remain visible as readiness states instead of being absorbed by a polished report;
- the implementation MUST include counterexample-style checks, such as negative field shapes, blocked/warning/pass precedence, and a second skill-class probe, before one fixture becomes SDK confidence.

## Problem Statement

Agent Skills Kit already has SDK-shaped surfaces: canonical skill source, generated runtime projection, ./bin/ask command handles, package readiness, profiles, lifecycle events, and proof workflows. The weakness is not lack of vocabulary. The weakness is that future agents and harness code can still infer readiness from whichever surface they read first.

For example, a skill can be structurally present, package-incomplete, runtime-blocked, outcome-proof-missing, and still produce a polished report. That is not a professional SDK contract. A professional SDK contract must make the true state machine easy to consume and hard to flatten.

JSC-329 fixes one slice: skills doctor MUST expose stable readiness evidence for context7, MUST identify which SDK layer each readiness signal belongs to when that layer is known, and MUST keep distinct failure classes visible even when the final status is blocked.

## User / Operator Scenarios

### Scenario 1: Jamie Checks Whether A Skill Is Safe To Rely On

Jamie runs ./bin/ask skills doctor context7 --json --robot before asking Codex to use the skill in a real workflow.

Expected result: the JSON tells Jamie whether the skill is usable, warning-only, or blocked; which evidence is missing; what command should be run next; and which warnings remain visible even under a blocked final status.

### Scenario 2: Codex Routes Around A Blocked Skill

Codex resolves context7, runs doctor, and sees blocked_runtime.

Expected result: Codex does not claim the skill is ready, does not confuse package metadata with runtime reachability, and reports the safe next command or null when no safe command exists.

### Scenario 3: Harness Consumes Readiness Without Parsing Internals

coding-harness or a future control pane consumes doctor JSON for readiness gates.

Expected result: the consumer reads declared schema fields and status classes, preserves raw evidence, and does not parse SKILL.md, package prose, or human summaries to infer state.

### Scenario 4: Review Feedback Names A Local Symptom But Means A General Rule

A technical reviewer says a boolean success/failure return should become a named sentinel error in a function.

Expected result: the JSC-329 implementation does not blindly patch only that named function when the feedback expresses an API design rule. It performs a bounded pattern sweep in the same implementation boundary, classifies similar cases, and records disposition.

## Goals

- Define the required doctor JSON contract for the context7 fixture.
- Encode the layered Skill SDK architecture vocabulary as the readiness-classification model.
- Keep runtime reachability, package readiness, outcome proof, and structural checks separate.
- Make final status deterministic through explicit precedence.
- Require next_command semantics for pass, warning, and blocked outcomes.
- Normalize or ignore dynamic fields so fixture tests are stable.
- Keep RF-0 high-signal steering uptake as a required closeout gate.
- Produce a spec that can be handed to he-plan without reinterpreting intent.

## Non-Goals

- Do not migrate every skill to a complete SDK manifest.
- Do not implement package publication, marketplace install, sharing, or remote execution.
- Do not hand-edit runtime projections as source.
- Do not teach coding-harness to consume the contract in this slice.
- Do not make package readiness count as outcome proof.
- Do not broaden context7 fixture work into a general skill-authoring rewrite.
- Do not perform a big-bang repository restructure in this slice.
- Do not use generic app-layer names as the public SDK contract vocabulary when domain layer names are available.

## Current State / Evidence

| Evidence | Meaning |
| --- | --- |
| .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md | Selects doctor-driven trust as the first proof point for the professional Skill SDK direction. |
| .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md | Defines RF-0 steering uptake and RF-1 doctor contract fixture for context7. |
| .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md | Converts RF-1 into live Linear issue JSC-329. |
| .harness/quality/steering-uptake.md | Records high-signal steering as durable operating evidence. |
| Infrastructure/references/skills-sdk-apparatus-lens.md | Captures the apparatus trust model and Jamie's mantra: Thin surface. Strong guardrails. Durable memory. Professional output. |
| ~/dev/codex commits e7bffc5a2, f0166cadb, 4c8977231, a28024802, and 326e31ab6 | Provide May 2026 Python SDK precedent for thin public inputs, typed result objects, first-class setup/login handles, focused internal helpers, public API signature tests, and docs/examples parity. |
| openai/openai-python temporary design-reference clone | Should be treated as a reference architecture for Python SDK ergonomics, generated type stewardship, error taxonomy, streaming/retry conventions, raw/streaming escape hatches, pagination, hosted skill resource vocabulary, and docs discipline; it is not automatically a runtime dependency for local skill validation. |
| ./bin/ask skills doctor context7 --json --robot | Baseline command currently reports runtime blocking and outcome-proof warning behavior. |
| ./bin/ask skills package context7 --json --robot | Baseline package comparison reports package metadata incompleteness separately from runtime reachability. |

## Verified Baseline Gaps

The current implementation evidence used by this spec is not a readiness claim. It reveals gaps that JSC-329 must close:

- Live `./bin/ask skills doctor context7 --json --robot` currently returns a parseable robot payload with `data.skill_doctor.status=blocked` and a `blocked_validation` blocker from structural audit. That supports the exit/payload distinction, but it also means context7 is not a healthy-skill fixture.
- The same live payload currently recommends `./bin/ask skills proof context7 --json --robot` as `next_command` even though the actionable blocker is `blocked_validation`. JSC-329 MUST correct or explicitly test against this class of misrouting so blocker remediation outranks outcome proof.
- Existing focused tests include a pass case where `checks.outcome_proof.status=available_not_run` and final `status=pass`. That conflicts with this spec's critical-check mapping unless a selected profile explicitly treats outcome proof as non-critical. JSC-329 MUST either update the behavior/test to produce warning or add a profile-specific non-critical classification with explicit evidence.

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | JSC-329 |
| URL | https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7 |
| Status | Triage |
| Priority | High |
| Team | JSC |
| Mutation status | created |
| Required tracker behavior | Keep this spec and the live issue aligned before implementation closeout. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Linkage |
| --- | --- | --- |
| JSC-329 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010 | RF-1 doctor contract fixture acceptance. |
| JSC-329 | SA-010 | Scope control excludes broad SDK metadata migration, package publication, runtime projection edits, and coding-harness consumer implementation. |
| JSC-329 | SA-001, SA-003, SA-006, SA-008 | Closeout should cite focused fixture tests, baseline doctor/package probes, representativeness check, RF-0 steering validation, and changed-file repo validation. |
| JSC-329 | SA-005 | Rollback should remove fixture/tests, revert introduced doctor behavior changes, and compare post-rollback doctor output against pre-change snapshot with dynamic fields normalized. |

## Proposed Behavior

./bin/ask skills doctor context7 --json --robot MUST produce an SDK-grade readiness report with a stable field contract and deterministic status semantics.

Doctor is an aggregator. It MUST compose readiness signals from source resolution, runtime reachability, package readiness, outcome proof, profile context, lifecycle evidence, and next action. It MUST NOT replace package, prove, eval, or audit behavior.

The first fixture MAY use the current blocked baseline for context7, but the contract MUST be written so pass, warning, and blocked states have consistent field semantics.

## Requirements

### Functional Requirements

| ID | Requirement |
| --- | --- |
| FR-001 | Doctor output MUST expose schema_version, status, target_summary, checks, blockers, warnings, operation_context, contract_schemas, agent_summary, and next_command in the robot envelope at data.skill_doctor, with the type and minimum-content constraints defined in the Data / Domain Contract. |
| FR-002 | status MUST be deterministic: blocked outranks warning, warning outranks pass, and pass requires empty blockers and empty warnings. |
| FR-003 | Runtime reachability, package readiness, outcome proof, source resolution, structural audit, profile context, and lifecycle evidence MUST be reported as distinct check classes or evidence groups. |
| FR-004 | A runtime blocker MUST NOT suppress package warnings, outcome-proof warnings, or other non-runtime checks that can still be evaluated. |
| FR-005 | Package readiness MUST NOT be treated as outcome proof. A package pass, warning, or block only describes package/share/install readiness. |
| FR-006 | next_command MUST be present for every doctor status and MUST be chosen by the deterministic decision ladder in the Data / Domain Contract. It MAY be null only when no safe command exists after the ladder is evaluated, and that absence MUST be intentional rather than omitted. |
| FR-007 | Fixture assertions MUST normalize or ignore dynamic fields such as trace IDs, timestamps, volatile event IDs, elapsed durations, and absolute temp paths. |
| FR-008 | The implementation MUST record before and after doctor snapshots or equivalent fixture evidence with tolerated dynamic-field differences named explicitly. |
| FR-009 | The implementation MUST run one successful read-only representativeness check against an additional skill class selected during implementation; a missing required field in the additional skill's data.skill_doctor contract is blocking for JSC-329 unless waived with owner, date, reason, and follow-up issue. |
| FR-010 | Any reviewer feedback that expresses a transferable API, schema, validation, naming, or architecture rule MUST trigger a bounded pattern sweep and disposition, not a one-line correction only. |
| FR-011 | Critical skipped or not-run readiness checks MUST map to warning or blocked before final status is computed; a doctor payload MUST NOT report pass when any critical readiness check was skipped, not run, missing, or unavailable. |
| FR-012 | contract_schemas MUST be consumer-usable: each entry must either identify a governed schema by stable name/version/owner/stability or include an explicit missing_schema_reason that prevents release-readiness claims. |
| FR-013 | Doctor checks, blockers, warnings, and evidence groups SHOULD include or map to the relevant SDK layer when known: contracts, catalog, authoring, validation, packaging, runtime_adapters, evidence, or memory. Unknown or legacy classes MUST remain visible rather than being coerced into a misleading layer. |
| FR-014 | The public SDK vocabulary for readiness classification MUST prefer domain layer names over generic application buckets such as utils, providers, service, UI, types, config, and repo. Generic implementation names MAY appear only as internal detail or explicit mapping metadata. |
| FR-015 | Public Skill SDK surfaces SHOULD follow the May 2026 Codex Python SDK precedent: convenience inputs normalize into typed contracts at the boundary, public methods return domain result objects rather than raw transport payloads, setup workflows expose attempt-local handles, internal helper modules keep the facade thin, and public signatures are covered by tests. |
| FR-016 | The implementation MUST distinguish reference use of openai/openai-python from dependency use. It MAY cite openai-python as a design reference for Python SDK ergonomics, generated types, error taxonomy, streaming/retry behavior, and docs discipline; it MUST NOT add openai-python as a runtime dependency unless a concrete OpenAI API transport or generated-type boundary requires it. |
| FR-017 | Package/share/publish planning SHOULD account for the hosted skill resource shape observed in openai-python: create from files or zip bundle, retrieve typed skill metadata, update default version, list with cursor pagination, delete with explicit deleted result, download binary content, and manage versions as first-class resources. These hosted-resource verbs inform vocabulary and readiness gates but do not replace local canonical source, runtime projection, doctor, or eval contracts. |
| FR-018 | Skill SDK error and evidence outputs SHOULD preserve operation context and original cause, following the openai-python error model's distinction between status errors, validation errors, connection/timeouts, auth/permission classes, response body, code, param, type, and request ID where available. Local skill failures MUST continue to classify auth, sandbox, runtime, validation, user-input, timeout, and transport blockers separately. |
| FR-019 | When `blocked_validation` or another actionable blocker is present, `next_command` MUST target the blocker remediation or blocker inspection path before any outcome-proof, package-warning, or exploratory command. For the current context7 baseline, a structural audit blocker MUST NOT select `skills proof context7` unless the payload also records why no structural-audit remediation command is available and why proof is the safest next action. |
| FR-020 | `available_not_run`, `skipped`, `missing`, and `not_run` critical checks MUST be profile-classified before status computation. The default for outcome proof is warning, not pass. A pass outcome with `outcome_proof.available_not_run` is allowed only when `operation_context` declares a profile where outcome proof is explicitly non-critical and the payload records that classification. |
| FR-021 | Waivers for representativeness, schema, or validation gaps MUST NOT be self-approved by the implementation agent. A waiver is valid only when it names an approver with authority for Agent Skills Kit or the target issue, cites the authority source verbatim from a recognized owner source, records date, reason, scope, expiry or revisit condition, and a follow-up issue or artifact. Missing waiver authority keeps the gate blocked. |
| FR-022 | RF-1 MUST NOT create concrete schema files unless an existing canonical schema home is discovered during implementation. In RF-1, `contract_schemas` may use governed versioned identifiers or explicit `missing_schema_reason`; creating file-backed schemas is a separate follow-up unless required to make current tests truthful and a short schema-file decision record proves inline identifiers are insufficient, identifies the canonical schema home, and explains why the work cannot be deferred to RF-2. |
| FR-023 | Known doctor readiness signals MUST expose `sdk_layer` in production `data.skill_doctor` JSON, not only through test-side normalization. Fixture-only mapping MAY be used only to document legacy or unknown classes that cannot be safely classified during RF-1; it is not sufficient for known classes such as source_resolution, runtime_reachability, structural_audit, package_readiness, profile_context, outcome_proof, and lifecycle_evidence. |
| FR-024 | Image generation is not part of the JSC-329 implementation or closeout gate. If an external review workflow requests an infographic and a built-in image generation tool is unavailable, CLI fallback may be retried only when credentials are present and the user explicitly authorizes the fallback. Missing credentials or tool access is reported as a blocked auxiliary artifact, not as a JSC-329 plan/spec failure. |
| FR-025 | Release-readiness, skill-readiness, or SDK-readiness claims MUST cite the verification apparatus that signs off the claim. Valid apparatus evidence includes typed robot contract assertions, focused tests, doctor/package/prove/eval command output, structural audit evidence, representativeness probes, changed-file validation, lifecycle evidence, or rollback/supersession records. Prose summaries, package presence, source presence, or AI review alone are insufficient. |
| FR-026 | The JSC-329 fixture MUST include at least one counterexample-style assertion for the apparatus lens: malformed or semantically empty required fields, a critical skipped/not-run check, a blocker-first next_command case, or an overfit-prevention representativeness probe. The counterexample MUST fail in a named blocker or warning class rather than silently producing pass. |

### Non-Functional Requirements

| ID | Requirement |
| --- | --- |
| NFR-001 | The fixture MUST be stable across normal local runtime variance. |
| NFR-002 | The contract MUST be readable by agents and harness consumers without requiring prose interpretation. |
| NFR-003 | The implementation MUST be reversible by removing the fixture/tests and reverting any doctor behavior change introduced by JSC-329. |
| NFR-004 | The spec, plan, and implementation evidence MUST preserve live tracker traceability to JSC-329. |
| NFR-005 | The layered SDK model MUST be usable without a repository-wide folder migration; command contracts and validation semantics move first, physical restructuring follows only after validators can prove ownership. |
| NFR-006 | The verification apparatus SHOULD be the smallest credible stack for the readiness claim. JSC-329 must not expand into broad static-analysis theater, external verifier adoption, or package-marketplace migration unless a focused doctor-contract gap requires it. |

## Interfaces

### CLI Interface

Primary command:

~~~bash
./bin/ask skills doctor context7 --json --robot
~~~

Comparison command:

~~~bash
./bin/ask skills package context7 --json --robot
~~~

Closeout command:

~~~bash
./bin/ask repo validate --changed-files <changed-files> --json --robot
~~~

### Robot JSON Interface

The robot JSON contract is the public surface for this slice. Consumers MUST read doctor readiness from data.skill_doctor inside the standard ask robot envelope, and MUST rely on named fields and status classes rather than terminal prose or markdown summaries.

### Test Fixture Interface

The fixture MUST encode required field presence, status precedence, distinct readiness signals, and dynamic-field normalization. The fixture MAY live in the existing ask CLI test layout, but the final plan decides exact file paths after inspecting current test conventions.

## Data / Domain Contract

### Required Top-Level Fields

Top-level in this section means top-level within data.skill_doctor, not the outer ask robot envelope.

| Field | Required | Semantics |
| --- | --- | --- |
| schema_version | yes | Non-empty string version for the doctor contract. |
| status | yes | String enum: pass, warning, or blocked. |
| target_summary | yes | Object with stable target identity. It MUST include query, target_kind, canonical_source_path or an explicit null, and handle when the target is a command handle. |
| checks | yes | Non-empty object keyed by readiness check or public check class. Each check MUST include a status string and SHOULD include command, evidence, reason, or class-specific detail when available. |
| blockers | yes | Array of blocker objects. Each blocker MUST include class and message; definition SHOULD be present when known. Use an empty array only when no blocker exists. |
| warnings | yes | Array of warning objects. Each warning MUST include class and message; definition SHOULD be present when known. Use an empty array only when no warning exists. |
| operation_context | yes | Non-empty object with profile and command context. It MUST include primary_profile or an equivalent selected profile field and at least one validation or follow-up command list when available. |
| contract_schemas | yes | Non-empty object. Each entry MUST identify a governed schema by stable name/version/owner/stability or declare missing_schema_reason; opaque placeholders and empty strings are invalid. |
| agent_summary | yes | Non-empty string that mirrors the structured status without replacing it. |
| next_command | yes | Safe next command string or explicit null. When non-null it MUST be a string and MUST be selected by the next_command decision ladder. |

### SDK Layer Values

Allowed public layer values for JSC-329 are:

- contracts
- catalog
- authoring
- validation
- packaging
- runtime_adapters
- evidence
- memory

Checks, blockers, warnings, and evidence groups SHOULD include sdk_layer when the layer is known. When the implementation cannot classify a legacy check safely, it MUST preserve the original class and MAY use sdk_layer: unknown. It MUST NOT force a generic implementation label into a public SDK layer without a documented mapping.

For RF-1, `sdk_layer` is a production contract field for known classes. Tests may normalize or assert mappings, but they must not be the only place where the mapping exists for known doctor signals. If a check remains internal or legacy, the payload must preserve the original class and either omit `sdk_layer` with a documented reason or set `sdk_layer: unknown`; it must not invent a misleading public layer.

### Critical Check State Mapping

Final status MUST be computed after check states are mapped into blockers and warnings.

| Check State | Default Mapping | Notes |
| --- | --- | --- |
| pass | no blocker or warning | The check completed successfully. |
| warning | warning | The check completed with non-blocking readiness concern. |
| fail | blocker | The check failed a required readiness gate. |
| blocked | blocker | The check could not complete because a prerequisite or environment boundary blocked it. |
| missing | warning or blocker | Warning for exploratory authoring profiles; blocker for promotion or release-readiness claims. |
| available_not_run | warning | The evidence exists but was not executed in this run. |
| skipped | warning or blocker | Warning only when the skip is explicitly non-critical for the selected profile; otherwise blocker. |
| not_run | warning or blocker | Warning only when the not-run check is intentionally deferred for the selected profile; otherwise blocker. |

Critical checks for JSC-329 are source resolution, runtime reachability, structural audit, package readiness visibility, outcome proof classification, operation context, and next_command selection. A payload MUST NOT report pass when any critical check maps to warning or blocker, or when any critical check is absent.

### Status Enum

Allowed values: pass, warning, blocked.

Unknown status values MUST fail the focused contract fixture. If a future schema version adds statuses, the schema version and fixture expectations MUST change together.

### Check Classification

At minimum, the implementation MUST preserve or map these classes when they are observable:

| Class | Meaning |
| --- | --- |
| source_resolution | Canonical source, generated handle, or path resolution. |
| runtime_reachability | Whether the skill can be loaded or executed by the current runtime. |
| structural_audit | Format, manifest, source/projection, or instruction integrity. |
| package_readiness | Package/share/install metadata and provenance readiness. |
| profile_context | Operation profile and promotion/readiness interpretation. |
| outcome_proof | Eval, proof, smoke, or artifact evidence that behavior works. |
| lifecycle_evidence | Events, traces, or run metadata that explain what happened. |

Internal names MAY appear only when they are explicitly mapped to public check classes. For JSC-329, capability_metadata or package-facing metadata MUST map to package_readiness in the exported data.skill_doctor contract or be documented as a non-public internal detail. An exported contract that contains only internal class names for package readiness is not sufficient.

### Python SDK Pattern Contract

JSC-329 is a doctor fixture slice, but it should not forget the SDK shape it is proving. The command contract should align with these public API rules:

- Convenience input is allowed only at the edge. A future `skill.run("...")` or `skills doctor context7` shortcut must normalize into the same typed payload used by tests, fixtures, and harness consumers.
- Result objects must carry domain truth. Doctor/package/eval/prove outputs should expose named statuses, errors, blockers, warnings, artifacts, timing, evidence, trace IDs, and next actions rather than raw subprocess or transport payloads.
- Blocking workflows should return attempt handles. Setup, login, install, projection sync, package, eval, and live mutation flows should have attempt-local identity and `wait`/`cancel` semantics when they can continue asynchronously or block on user/tool/auth state.
- Setup is part of the SDK, not external homework. A zero-setup agent path means the SDK can discover missing tools, roots, auth, packages, or projections, perform allowed setup steps, and classify forbidden or blocked setup with named blocker classes.
- Public signatures and JSON contracts are release gates. Tests should assert exported method names, result fields, status enums, and robot JSON paths so future agents do not infer behavior from prose.
- Hosted-resource vocabulary is useful but bounded. OpenAI's generated skills resource has create, retrieve, update default version, list, delete, content download, and version subresources; Agent Skills Kit should borrow the clarity of those verbs while preserving its own local source/projection/proof model.
- Raw and streaming evidence should be explicit. The default Skill SDK path should return parsed, typed JSON contracts; raw logs, raw command output, binary package content, and event streams should be opt-in evidence channels with provenance.

`openai-python` is a design source unless a specific implementation boundary requires it. Local skill doctor, package, projection, eval, and filesystem validators should remain lightweight and should not import OpenAI transport code just to look SDK-shaped.

### next_command Decision Ladder

next_command MUST be deterministic for the same normalized input.

1. If any actionable blocker has a safe repair or proof command, choose the highest-severity actionable blocker command.
2. If multiple blockers are actionable at the same severity, choose in this order: blocked_resolution, blocked_missing_source, blocked_runtime, blocked_validation, blocked_missing_tool, blocked_environment, blocked_auth, blocked_user_input, timeout_no_output, timeout_partial_output, blocked_missing_artifact.
3. If no blocker has a safe command and warnings exist, choose the highest-severity warning command that does not bypass blockers.
4. If no blocker or warning has a safe command and the payload is pass, choose the normal proof or inspection command for the target.
5. If no safe command exists, next_command MUST be explicit null and the payload MUST include evidence explaining why no safe command exists.

next_command MUST NOT prioritize a warning command while an actionable blocker command exists.

For `blocked_validation`, the preferred command is the validation or audit command that produced the blocker, when available. If that command is unavailable, `next_command` may select a diagnostic doctor command only if the payload records the missing blocker command. Outcome-proof commands are not valid `blocked_validation` remediation unless the validation blocker is already resolved or the payload proves the proof command is the only safe blocker-inspection path.

### Exit And Payload Semantics

The process exit code is a transport/execution signal; data.skill_doctor.status is the readiness signal. For JSC-329 tests, a non-zero command exit caused by blocked readiness is valid evidence only when the robot payload is parseable and data.skill_doctor.status is blocked with blocker detail. A process failure that prevents parsing the robot payload MUST be classified separately as command_failure, transport_failure, or environment/tooling failure and MUST NOT be reported as a skill readiness blocker.

### Dynamic Fields

Fixture comparison MUST normalize or ignore:

- trace IDs;
- timestamps;
- elapsed durations;
- volatile event IDs;
- machine-local temporary paths;
- ordering that is explicitly documented as non-semantic.

The normalizer MUST NOT hide status, blocker class, warning class, command, schema version, or required-field drift.

### Unknown Field Behavior

Unknown additive fields MAY be allowed in the fixture if required fields preserve meaning. Removing, renaming, or changing required-field semantics MUST fail the fixture until the schema version and consumer expectations are updated.

### contract_schemas Minimal Validity

For RF-1, concrete schema files are not required if no canonical schema home exists yet. However, each contract_schemas entry MUST be more than a placeholder string. The minimum acceptable form is either:

- a stable schema identifier string that includes a version, such as skill-doctor.v1, and is listed in the doctor taxonomy or operation context; or
- an object with name, version, owner, stability, and optional path; or
- an object with name, version, owner, stability, and missing_schema_reason when the schema is declared but not yet file-backed.

Empty strings, unknown unversioned names, and placeholder values are invalid.

Schema-file creation decision: RF-1 should prefer governed identifiers and explicit `missing_schema_reason` over creating new schema files. The implementation may create concrete schema files only if it discovers an existing canonical schema registry or if a focused test cannot honestly validate `contract_schemas` without a file-backed schema. Otherwise, file-backed schema creation is a follow-up issue after the doctor JSON contract is stable.

### Waiver Authority

Waivers are exceptional control-plane records, not implementation conveniences. Authority must be sourced from one of these recognized owner sources:

- the current Linear issue owner or assignee for JSC-329;
- a repo-owned CODEOWNERS, ownership, governance, or AGENTS/UBIQUITOUS_LANGUAGE authority file that names the owner for Agent Skills Kit or the affected contract surface;
- a direct Jamie decision in the current thread or a linked decision artifact.

A valid waiver must include:

- approver name or handle;
- verbatim authority source and path/link;
- date;
- waived gate;
- reason;
- scope;
- expiry or revisit condition;
- follow-up issue, artifact, or decision record.

The implementation agent may draft a waiver request but must not approve it. A missing approver, missing authority evidence, missing follow-up, or open-ended waiver keeps the gate blocked.

### Schema-File Decision Record

If implementation creates concrete schema files during RF-1, closeout MUST include a short decision record with:

- the discovered canonical schema home and evidence path;
- why governed inline identifiers or `missing_schema_reason` cannot satisfy RF-1;
- why schema-file creation cannot be deferred to RF-2;
- exact files created;
- owner for future schema stewardship.

Absent that record, new schema files are out of scope and must be reverted or moved to a follow-up issue.

## Enforcement Contract

essential_decisions:

- `data.skill_doctor` is the public SDK readiness surface for JSC-329; consumers must not infer readiness from terminal prose, package summaries, runtime projections, or AI review artifacts.
- Final doctor status uses deterministic precedence: blocked outranks warning, warning outranks pass, and pass requires no blockers, warnings, or critical skipped/not-run readiness checks.
- Known doctor readiness signals expose the domain SDK layer vocabulary in production JSON: contracts, catalog, authoring, validation, packaging, runtime_adapters, evidence, and memory.
- Package readiness, runtime reachability, structural audit, outcome proof, profile context, and lifecycle evidence remain separate readiness classes; one class cannot satisfy another.
- Waivers for schema, validation, or representativeness gaps require external authority and cannot be self-approved by the implementation agent.

fillable_gaps:

- The implementation agent may choose fixture-file or helper-generated assertions after inspecting existing ASK CLI test conventions.
- The exact additional skill for the representativeness probe may be selected during implementation, provided it exercises a different readiness axis than context7 and stays read-only.
- Concrete schema files may stay deferred if `contract_schemas` entries carry governed identifiers or explicit `missing_schema_reason` evidence.

guardrails:

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q`
- `python3 -m pytest Infrastructure/tests/test_ask_skills_package.py -q` when package comparison behavior or shared helpers change.
- `./bin/ask skills doctor context7 --json --robot`, captured as blocked-readiness evidence when the robot payload is parseable.
- `./bin/ask skills package context7 --json --robot`, captured as package-readiness comparison evidence.
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`
- `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md`
- `python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md --kind spec --json`

refusal_triggers:

- Stop if the fix requires hand-editing runtime projections, broad SDK metadata migration, package publication, coding-harness consumer changes, or repository-wide folder restructuring.
- Stop if `data.skill_doctor` would need to be flattened into the outer ask robot envelope.
- Stop if `sdk_layer` mapping cannot be added without hiding original blocker or warning classes.
- Stop if a waiver is needed but no owner, authority source, expiry, and follow-up artifact are available.

durable_memory:

- Record transferable steering or review feedback in `.harness/quality/steering-uptake.md`, the implementation closeout artifact, and any nearest owning repo guidance surface required by the feedback radius.
- Preserve before/after doctor and package evidence with dynamic-field normalization rules so future agents can distinguish readiness drift from volatile runtime data.

professional_output:

- Closeout must report files changed, exact validation commands, pass/fail state, blocked-readiness command exits, warning classes, waiver status, representativeness result, rollback path, remaining risks, and next action for JSC-329.
- Release-readiness, skill-readiness, or SDK-readiness claims must cite the verification apparatus that signed them: typed assertions, focused tests, doctor/package/prove/eval command output, structural audit, representativeness probe, changed-file validation, or rollback evidence.

## Security, Privacy, and Safety

Doctor output MUST NOT expose secrets, tokens, private credential material, or unredacted environment variables.

Path evidence SHOULD use repository-relative paths where possible. Absolute paths MAY appear when existing ask output requires them, but tests MUST avoid depending on machine-specific paths unless the path is intentionally part of the contract.

The fixture MUST avoid live external mutations. This slice is read-only except for repository test, fixture, and documentation edits.

## Accessibility and Operator Ergonomics

The contract must be useful to both humans and agents:

- humans get a compact agent_summary, blocker/warning buckets, and safe next action;
- agents get stable JSON fields, enums, and check classes;
- harness gets raw evidence that can be preserved without parsing prose.

Professional output means uncertainty is visible. Passed, warning, blocked, skipped, and not-run evidence MUST NOT be collapsed into a single success-looking report.

## Failure and Recovery

| Failure | Required Behavior | Recovery |
| --- | --- | --- |
| Missing required field | Focused fixture fails. | Restore field or intentionally version the schema. |
| Runtime blocked | Final status is blocked; package/outcome warnings remain visible if observable. | Report blocker and safe next command. |
| Package metadata incomplete | Package readiness is warning or blocked according to profile; runtime state remains separate. | Run package command or metadata repair flow. |
| Outcome proof missing | Outcome proof is warning or blocked according to profile; package readiness does not satisfy it. | Run prove or an approved eval/proof command. |
| Unknown dynamic-field drift | Fixture fails unless field is added to documented normalizer for non-semantic reasons. | Classify drift and update normalizer or fixture. |
| Review feedback implies broader pattern | Implementation cannot close with only named-line fix. | Run bounded pattern sweep and record disposition. |

Rollback rule: remove the new fixture/tests, revert any doctor behavior change introduced by JSC-329, and verify the post-rollback context7 doctor output matches the recorded pre-change snapshot except documented dynamic fields.

## Validation Plan

Required validation for JSC-329 implementation:

| Gate | Command | Pass Condition |
| --- | --- | --- |
| RF-0 steering uptake | python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json | exits 0 and reports ledger valid. |
| RF-0 regression test | python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q | exits 0. |
| Baseline doctor probe | ./bin/ask skills doctor context7 --json --robot | output is captured and classified, even if command exits non-zero for blocked readiness. |
| Package comparison | ./bin/ask skills package context7 --json --robot | output is captured and does not count as outcome proof. |
| Focused contract test | command selected by implementation, expected under existing ask CLI test conventions | asserts required fields, status precedence, next command, signal separation, SDK layer mapping, and dynamic-field normalization. |
| Representativeness check | read-only doctor command for one additional skill class | required fields and shapes satisfy the contract, or the gate is blocking with owner/date/reason/follow-up waiver metadata; an unwaived coverage gap is not a pass condition. |
| Changed-file repo validation | ./bin/ask repo validate --changed-files <changed-files> --json --robot | required failures are zero or blockers are classified with ownership. |

Spec validation for this artifact:

~~~bash
test -f .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
rg -n "AC-|acceptance|validation|rollback|observability" .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md --json
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md
python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-17-agent-skills-jsc-329-skill-sdk-doctor-contract-spec.md --kind spec --json
~~~

## Acceptance Criteria

| ID | Behavior | Source Evidence | Validation | Risk | Observability | Rollback / Supersession |
| --- | --- | --- | --- | --- | --- | --- |
| SA-001 | Doctor exposes all required SDK readiness fields for context7. | JSC-329 Linear plan and RF-1 reframe. | Focused contract fixture asserts required field presence, shape, and minimum semantic content. | Harness or agents infer readiness from missing/prose-only fields. | Fixture diff names any missing or extra required fields. | Remove fixture/tests and revert doctor field changes. |
| SA-002 | Status precedence is deterministic: blocked outranks warning, warning outranks pass, pass requires no blockers or warnings. | North star SDK-AC2 and RF-1. | Unit or fixture test feeds mixed outcomes and asserts final status. | Mixed states produce misleading success. | Test failure shows expected and actual status. | Revert status helper/fixture changes. |
| SA-003 | Runtime reachability, package readiness, and outcome proof remain separate. | RF-1 scope and Linear acceptance criteria. | Doctor and package probes plus focused test assert distinct buckets/classes. | Package pass hides missing proof or runtime failure hides package warning. | JSON includes separate checks, blockers, and warnings. | Remove separation assertions only with explicit schema supersession. |
| SA-004 | next_command is always present and intentionally nullable. | Linear plan next-command scope. | Fixture asserts field exists for blocked/warning/pass fixture states and permits null only by explicit expectation. | Agents loop or guess unsafe follow-up commands. | Doctor report shows safe next command or explicit absence. | Revert next-command contract changes and fixture. |
| SA-005 | Dynamic fields do not make fixtures flaky and required fields cannot be normalized away. | RF-1 before/after snapshot requirement. | Normalized fixture comparison excludes only documented volatile fields. | Tests either flap or hide real contract drift. | Normalizer report lists ignored fields. | Remove normalizer or narrow ignored-field list. |
| SA-006 | context7 baseline is captured without claiming it is fully healthy. | Current doctor/package command evidence. | Baseline doctor probe and package comparison are stored or summarized in test/eval evidence. | A blocked baseline is misreported as release readiness. | Evidence records status, blocker classes, warning classes, and command exit behavior. | Delete baseline artifact if superseded by a new stable fixture. |
| SA-007 | One additional skill class is checked for representativeness. | RF-1 reframe validation requirement. | Read-only doctor command runs against selected additional skill and records successful contract parse or a blocking waiver with owner/date/reason/follow-up issue. | context7 hides assumptions that fail immediately elsewhere. | Closeout names selected skill class, difference axis, and result. | Defer only with owner-approved blocking waiver and follow-up issue. |
| SA-008 | RF-0 steering uptake remains a closeout gate. | Steering uptake docs, ledger, and validator. | Steering validator and test pass before implementation closeout. | High-signal feedback becomes prose again instead of environment change. | Closeout includes exact command outcomes. | Revert only if validator is proven too strict and replacement gate exists. |
| SA-009 | Review feedback that expresses a broader design principle triggers a bounded pattern sweep. | Jamie API design feedback and RF-5 preview. | Technical review closeout records scope searched, similar cases fixed/deferred/not applicable, and exclusions. | Model applies named-line correction only. | Review or closeout artifact includes disposition table. | Defer only with explicit public API/risk classification. |
| SA-010 | Runtime projections and package-wide SDK migration stay out of scope. | Path ownership docs and JSC-329 non-goals. | Changed-file review confirms no hand-edited runtime projections and no broad metadata migration. | Fixture slice becomes unbounded churn. | Changed-file validation and review artifact name touched ownership surfaces. | Revert out-of-scope projection or migration edits. |
| SA-011 | Required fields have enforceable JSON shapes and minimum content, not only key presence. | Round 1 adversarial reviews. | Negative fixture rejects wrong field types, empty semantic objects, and opaque contract_schemas placeholders. | Shape-only green payloads break SDK consumers. | Fixture failure names field path and expected shape. | Revert shape assertions only with explicit schema supersession. |
| SA-012 | Critical skipped, not-run, missing, or unavailable checks cannot produce pass. | Round 1 adversarial reviews and professional output requirement. | Fixture covers at least one critical skipped/not-run state and asserts warning or blocked final status. | Unevaluated readiness becomes false green. | Check summary records mapped warning/blocker. | Revert only with profile-specific waiver. |
| SA-013 | next_command selection is deterministic and blocker-first. | Round 1 adversarial document review. | Mixed blocker/warning fixture asserts selected command follows the decision ladder. | Agents loop on low-safety or non-remediating commands. | Payload records selected next_command and candidate basis. | Revert only with replacement command-selection contract. |
| SA-014 | Representativeness requires one successful additional-skill contract parse. | Round 1 adversarial and architecture reviews. | Additional read-only skill doctor output is parsed and asserted for required fields/shapes. Coverage gap is blocking unless waived with owner/date/follow-up issue. | context7-only assumptions ship as SDK confidence. | Eval artifact records selected skill, difference axis, and result class. | Defer only with owner-approved waiver and follow-up issue. |
| SA-015 | Doctor readiness evidence maps to the layered Skill SDK architecture. | Layered SDK Architecture section and Jamie architecture prompt. | Focused fixture or eval evidence asserts observable checks/blockers/warnings include sdk_layer or explicit unknown/mapping metadata where safe classification is unavailable. | Generic implementation buckets obscure ownership and let agents patch local symptoms instead of the right SDK layer. | Doctor/eval evidence records layer values or unknown classifications without hiding original classes. | Revert layer mapping only with a superseding SDK vocabulary decision. |
| SA-016 | Waivers require explicit external authority and cannot be self-approved by the implementation agent. | FR-021 and Jamie systems-thinking feedback. | Any waiver fixture or closeout record includes approver, authority evidence, date, gate, reason, scope, expiry/revisit, and follow-up; missing fields keep the gate blocked. | Agents can bypass representativeness or validation gates by writing their own waiver. | Closeout shows waiver metadata or states no waiver used. | Revoke invalid waiver and treat the gate as blocked. |
| SA-017 | RF-1 does not create concrete schema files unless a canonical schema home is discovered or tests require file-backed truth. | FR-022 and contract_schemas scope. | Changed-file review confirms no new schema files unless justified in closeout; contract_schemas entries remain versioned or carry missing_schema_reason. | Schema churn distracts from doctor contract proof or creates premature schema ownership. | Closeout records schema-file decision and evidence. | Remove premature schema files or route to follow-up schema stewardship issue. |
| SA-018 | Known readiness classes expose sdk_layer in production data.skill_doctor JSON. | FR-023 and layered SDK contract. | Focused test asserts sdk_layer appears in production payload for known checks/blockers/warnings/evidence groups; fixture-only mapping is allowed only for unknown legacy classes with a reason. | Harness consumers cannot use SDK layers because they exist only in tests. | Doctor JSON and eval evidence include sdk_layer values while preserving original classes. | Revert layer field only with a superseding SDK vocabulary decision. |
| SA-019 | Imagegen is treated as an auxiliary review artifact, not a JSC-329 implementation gate. | FR-024 and imagegen skill contract. | Closeout states generated, blocked, or skipped image status separately from plan/spec validation. CLI fallback is attempted only with credentials and explicit user authorization. | A missing image tool blocks unrelated SDK contract work or silently uses credentials. | Review artifact records imagegen status and blocker if any. | Remove image artifact from JSC-329 gate; rerun only when authorized. |
| SA-020 | Skill readiness claims cite the apparatus that signs them off. | Skills SDK apparatus lens and FR-025. | Focused fixture/eval/closeout evidence maps each readiness claim to a command, schema assertion, test, probe, audit, representativeness result, validation gate, or rollback record. | Agents trust polished artifacts, package presence, or AI review as if they were verification. | Closeout records the apparatus used for field contract, status semantics, signal separation, representativeness, and changed-file validation. | Narrow or remove any readiness claim that lacks apparatus evidence. |
| SA-021 | Counterexample-style checks prevent overfitted green readiness. | Skills SDK apparatus lens and FR-026. | Focused test or fixture includes malformed required fields, critical skipped/not-run state, blocker-first next_command, or second-skill representativeness evidence that fails in a named class when the contract is violated. | A single coherent context7 artifact becomes false SDK confidence. | Test failure names the violated field, state, blocker ladder, or representativeness axis. | Remove only the overfitted claim or route uncovered matrix work to RF-2. |

## Visual References / Diagrams

| Visual Element | Clarifies |
| --- | --- |
| Doctor readiness flow | How source, projection, package, proof, profile, and lifecycle evidence feed deterministic status precedence. |
| Layered SDK architecture | How contracts, catalog, authoring, validation, packaging, runtime adapters, evidence, and memory separate ownership. |

~~~mermaid
flowchart TD
  A["Canonical skill source"] --> B["skills doctor"]
  C["Runtime projection"] --> B
  D["Package readiness"] --> B
  E["Outcome proof"] --> B
  F["Profiles and lifecycle events"] --> B
  B --> G{"Status precedence"}
  G -->|"blockers present"| H["blocked"]
  G -->|"warnings only"| I["warning"]
  G -->|"no blockers or warnings"| J["pass"]
  H --> K["required fields + next_command"]
  I --> K
  J --> K
  K --> L["Harness may consume JSON without parsing skill internals"]
~~~

The diagram is explanatory only. The normative requirements are the FR, NFR, and SA tables.

## Implementation Notes

The implementation plan should inspect existing ask CLI tests before choosing fixture paths. It should prefer small helper-level assertions if status precedence already lives in helper functions, and command-level fixture assertions where the public robot JSON contract is assembled.

The first additional skill class for representativeness should be selected from a skill with different runtime needs than context7, such as a Harness Engineering skill or a factory skill, but the plan must verify the chosen handle exists before using it.

If ./bin/ask skills doctor context7 --json --robot exits non-zero because readiness is blocked, the command can still be valid evidence. The validation record must classify command exit behavior separately from contract-shape failure.

## Open Questions

| ID | Question | Default Until Resolved |
| --- | --- | --- |
| OQ-001 | Which exact test file should own the focused contract fixture? | Use existing ask CLI test conventions discovered during he-plan. |
| OQ-002 | Which additional skill class should be used for representativeness? | Select one read-only skill after verifying handle availability. |
| OQ-003 | Should contract_schemas point to concrete schema files in RF-1 or declare current schema names inline? | RF-1 may assert field presence and defer schema-file creation unless implementation discovers an existing schema home. |
| OQ-004 | Who can approve representativeness or validation waivers? | Only Jamie or a named owner with authority over Agent Skills Kit, JSC-329, or the affected contract surface; implementation agents cannot self-approve. |
| OQ-005 | Should RF-1 expose sdk_layer in production JSON or only in fixture/evidence mapping? | Production JSON for known readiness classes; fixture/evidence mapping only for unknown legacy classes. |
| OQ-006 | Should image generation be retried through CLI fallback if credentials are provided? | Only as an auxiliary artifact when the user explicitly authorizes fallback and credentials are available; it is not a JSC-329 gate. |

## Decision

Proceed with JSC-329 as a focused doctor-contract fixture slice. Do not expand to broad SDK metadata migration, package publication, harness consumer integration, or runtime projection rewriting until RF-1 produces command-level evidence.

## Evidence and References

- .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
- .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
- .harness/quality/steering-uptake.md
- Docs/agents/14-path-ownership-boundaries.md
- Docs/agents/19-high-signal-steering-feedback.md
- Docs/agents/20-misuse-resistant-interface-design.md
- Docs/agents/23-ctf-workflow-evals.md
- Infrastructure/references/skills-sdk-apparatus-lens.md
- Linear issue: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7

## Appendix A. Harness Metadata / Traceability

| Field | Value |
| --- | --- |
| Selected stage | he-spec |
| Mode | standard-spec plus deepen pass |
| Source artifact | .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md |
| Source reframe | .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md |
| Linear issue | JSC-329 |
| Live tracker status | created |
| Traceability required | true |
| Handoff target | he-plan after technical review |

## Appendix B. Review Outcomes

### Deepen Pass Result

| Check | Result |
| --- | --- |
| Acceptance IDs include behavior, source, validation, risk, observability, and rollback. | passed |
| Data/domain contract defines required fields, enum behavior, unknown fields, and error handling. | passed |
| Failure recovery covers runtime, package, outcome proof, fixture drift, and review-transfer cases. | passed |
| High-signal steering uptake is encoded as a closeout gate. | passed |
| Scope boundaries exclude broad SDK migration and runtime projection edits. | passed |

Technical review status: approved_for_he_plan.

## Appendix C. he-plan Handoff

The next he-plan should produce an implementation plan for JSC-329 with:

- exact test files after inspecting current ask CLI test conventions;
- exact baseline snapshot location or fixture update strategy;
- dynamic-field normalization rules;
- selected additional skill class for representativeness;
- RF-0 steering uptake validation before closeout;
- changed-file validation command;
- explicit review-feedback pattern-sweep step for transferable feedback.
