---
schema_version: 1
artifact_id: he-plan-2026-06-04-skills-sdk-v1-0-product-implementation
artifact_type: he-plan
canonical_slug: skills-sdk-v1-0-product-implementation
harness_stage: he-plan
title: Skills SDK V1.0 Product Implementation Plan
status: draft_ready_for_review
date: 2026-06-04
source_spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
source_scaffold_plan: .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md
origin: user_accepted_v1_spec_handoff
source_artifacts:
  - .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
  - .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md
  - Infrastructure/references/skills-sdk-apparatus-lens.md
scaffold_gate_status: complete
scaffold_gate_pr: 221
scaffold_gate_merge_commit: c3ff670f3
linear_issue: JSC-390
linear_status: Todo
linear_scope_note: JSC-390 owns docs and explorer; V1.0 implementation still needs a parent tracker before execution unless waived.
linear_mutation_status: confirmation_required
risk: high
traceability_required: true
---

# Skills SDK V1.0 Product Implementation Plan

## Command Summary

BLUF: This plan gives Jamie, implementation agents, and future reviewers a bounded Skills SDK V1.0 execution contract that builds the first executable product layer without drifting into marketplace, full registry, or broad governance work. It uses the merged JSC-391 scaffold gate as the foundation, preserves ./bin/ask as the repo control plane, introduces skills-sdk as the extracted product CLI name, and sequences schema, receipt, risk, install-preview, and artifact-test work so every readiness claim has command-backed proof. The main risk is that platform ambition pulls implementation past the smallest proof-producing seam; the stop condition is any attempt to mark refs, evals, signing, docs explorer, or security adapters as implemented without schema-valid not_run, skipped_optional, or blocked receipts. The next handoff is to create or promote a V1.0 parent tracker, then execute PU-001 through PU-007 one slice at a time with validation and rollback evidence recorded after each unit.

Decision Needed: Create or promote a V1.0 parent Linear issue before implementation starts. JSC-390 remains docs/explorer scope, and JSC-391 is complete scaffold evidence, not the parent implementation tracker.

Top Risks: command-surface drift between ./bin/ask and skills-sdk; schema/receipt fields becoming prose-only; generated runtime projections being edited as source; install preview implying real install writes; scanner, refs, eval, signing, or explorer placeholders being mislabeled as pass.

Next Action: Use he-work or a governed implementation goal to execute PU-001 after refreshing repo status, tracker scope, and the current validation baseline.

## Objective

Implement the first V1.0 Skills SDK product slice from .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md. The slice must produce executable schema and command proof for skills-sdk check, core receipts, risk classification, install preview stubs, and honest placeholder lifecycle states while preserving the JSC-391 scaffold boundaries that are now merged into main.

## Source Contract

| Source | Role in this plan | Current state |
| --- | --- | --- |
| .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md | Canonical V1 product contract, acceptance IDs SA-001 through SA-029, validation IDs VP-001 through VP-024. | Updated for JSC-391 completion and skills-sdk CLI decision. |
| .harness/plan/2026-06-03-jsc-391-agent-first-skills-sdk-scaffold-refactor-plan.md | Historical scaffold implementation plan. | Complete through PR #221. |
| .harness/evidence/jsc-391-agent-first-skills-sdk-scaffold-refactor/module-ownership-map.json | Deep module ownership map for V1 landing zones. | Merged source evidence. |
| Docs/reference/skills-sdk/modules.md | Human-readable module ownership reference. | Merged source evidence. |
| Infrastructure/references/skills-sdk-apparatus-lens.md | Enforcement lens: schema, command output, fixtures, evals, and validation evidence outrank prose. | Required for every unit. |
| Infrastructure/tests/test_skills_sdk_scaffold.py | Existing scaffold boundary tests and fixture precedent. | Baseline to preserve. |

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Current linked issue | JSC-390 |
| Current linked issue role | Docs and static Skill Explorer scope only. It is not the V1.0 implementation parent. |
| Required parent action | Create or promote a V1.0 parent issue before implementation starts, or record an explicit user waiver. |
| JSC-391 role | Completed scaffold gate and structural prerequisite through PR #221. |
| Mutation status | confirmation_required |
| Implementation dependency | V1.0 parent tracker must own PU-001 through PU-007, with JSC-390 remaining related docs/explorer context. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Plan handling |
| --- | --- | --- |
| V1.0 parent needed | SA-015, SA-023 | PU-001 creates/promotes or records waiver before implementation. |
| JSC-391 | SA-024, SA-025, SA-026, SA-027, SA-028, SA-029 | Complete scaffold evidence; inherited by every unit. |
| JSC-376 | SA-002, SA-005, SA-013 | PU-003 command facade and exit-code behavior. |
| JSC-378 | SA-003, SA-004 | PU-002 manifest and receipt schemas. |
| JSC-386 | SA-006, SA-014, SA-020, SA-021 | PU-005 install preview, lockfile model, data-disposition boundaries. |
| JSC-384, JSC-388 | SA-007, SA-010, SA-017, SA-018 | PU-004 risk and PU-006 sandbox/security placeholders. |
| JSC-381 | SA-008, SA-014, SA-019 | PU-006 refs placeholder and trust boundary. |
| JSC-379, JSC-383 | SA-009, SA-022 | PU-006 eval placeholder and confidence contract. |
| JSC-390 | SA-001, SA-011, SA-016 | Deferred docs/explorer placeholder only in V1.0. |

## Scope and Boundaries

In scope:

- skills-sdk check product command facade routed through the repo control plane.
- Manifest/source-shape schema for the V1.0 check path.
- Core check receipt schema with status, failure taxonomy, work mode, proof metadata, sensor metadata, actor role, command version, schema URI, and placeholder states.
- Risk-tier classifier sufficient to choose local check gates for docs-only, referenced, scripted, external, and placeholder package states.
- Install-preview stub that emits target paths, scope, digest, permission summary, trust state, conflicts, lockfile delta preview, rollback note, and receipt without writing install state.
- skills.lock.json schema/model placeholder for install-preview deltas only.
- Placeholder contracts for refs, evals, signing, sandbox, and docs/explorer that emit honest not_run, skipped_optional, or blocked states.
- Artifact tests and fixtures for positive and negative command, schema, risk, receipt, and preview cases.

Out of scope:

- Public marketplace, registry protocol, publisher accounts, ranking, moderation, payments, or public submissions.
- Required Tessl confirmation.
- Global install writes or real projection mutations.
- Hosted docs/explorer publishing.
- Full refs ingestion, full eval runner, package signing, sandbox execution, or third-party scanner orchestration.
- Linear mutation until the user authorizes the V1.0 parent issue action.

## Authority and Scope Boundary

| Field | Contract |
| --- | --- |
| requested_depth | standard implementation plan for V1.0 only |
| approved_execution_boundary | Plan only. Implementation is authorized only after parent tracker scope is created/promoted or explicitly waived. |
| downscope_authority | User approval required to remove skills-sdk check, manifest schema, receipt schema, risk tier, install preview, or artifact tests from V1.0. |
| external_mutation_boundary | No GitHub, Linear, hosted docs, registry, global install, secret, or runtime projection mutation from this plan. |
| freshness_required | Before implementation, refresh git status --short --branch, git log -1 --oneline, tracker state, and baseline validation commands. |
| human_acceptance_boundary | Required for V1.0 parent tracker, mandatory scanner stack, first representative fixture skill if not chosen from existing fixtures, and any real install writes. |

## Current State / Evidence

| Evidence | Observed state | Consequence |
| --- | --- | --- |
| Local main | c3ff670f3 feat(skills-sdk): add agent-first scaffold gate (#221) | Scaffold gate is complete. Do not restart JSC-391. |
| JSC-391 artifacts | ADR, module map, placeholder schemas, fixtures, tests, closeout, and review artifacts are merged. | V1.0 work can land in accepted scaffold paths. |
| Existing scaffold tests | Infrastructure/tests/test_skills_sdk_scaffold.py exists. | Preserve and extend this test family. |
| Spec open questions | CLI name resolved to skills-sdk; security precedence accepted as written; lockfile defaults to skills.lock.json; scanner stack and fixture still require implementation-time confirmation. | Plan can proceed with explicit decision debt. |
| Tracker scope | Spec says JSC-390 is docs/explorer only and V1 parent is needed. | Implementation should not hide V1.0 inside JSC-390. |

## Implementation Strategy

Build from the evidence backbone outward:

1. Preserve the JSC-391 landing zones and ownership map.
2. Define public schemas before command behavior claims.
3. Implement skills-sdk check as a thin facade around repo-owned logic, keeping ./bin/ask authoritative until extraction is proven.
4. Emit health cards and receipts from the same result model so human and agent outputs cannot drift.
5. Make risk classification cheap, deterministic, and fixture-backed.
6. Make install preview read-only by construction and prove it does not mutate lockfiles, projections, global skill roots, or trust stores.
7. Represent refs, evals, sandbox, signing, and explorer as placeholder receipt producers only until later V1 milestones implement them.

### Command Facade Contract

V1.0 must make the product command name concrete without bypassing the repo control plane:

- Add a repo-local skills-sdk command facade only if it delegates to the same implementation path used by ./bin/ask.
- Keep ./bin/ask as the authoritative parser/action registry during V1.0.
- PU-003 must document the selected invocation shape before implementation tests are accepted. The preferred shape is ./bin/skills-sdk check as a thin wrapper over ./bin/ask sdk check, with both commands using the same result model, schemas, exit-code mapping, and receipt writer.
- If implementation evidence shows ./bin/ask sdk check is the only safe first route, PU-003 must emit a blocked extraction note rather than inventing an independent skills-sdk binary.
- Help text, action metadata, JSON output, and receipts must prove the two surfaces cannot drift.

## Runtime Persistence and State

| Field | Contract |
| --- | --- |
| runtime_state | No runtime state is created by this plan. Implementation may create test artifacts under controlled .harness/evidence/** or artifacts/** paths only when the executing slice records them. |
| resumption_key | skills-sdk-v1-0-product-implementation |
| artifact_chain_key | skills-sdk-v1-product -> jsc-391-agent-first-skills-sdk-scaffold-refactor -> skills-sdk-v1-0-product-implementation |
| runtime_invocation_receipt | not_applicable: this is a plan artifact, not a live SDK command execution. Implementation receipts begin in PU-003. |
| persistent_artifacts | This plan, the source spec, schemas, fixtures, tests, receipts, closeout reports, and validation output. |
| live_state_refresh | Refresh git, tracker scope, and current validation before implementation and before closeout. |
| session_evidence_status | Current chat evidence is historical once this plan is handed off; commands must rerun in the implementation session. |
| proof_boundary | A passing plan validator proves artifact shape only. It does not prove SDK behavior until implementation tests and command receipts pass. |

## Enforcement Contract

This plan inherits Infrastructure/references/skills-sdk-apparatus-lens.md.

| Apparatus field | V1.0 enforcement |
| --- | --- |
| essential_decisions | skills-sdk is the product CLI name; ./bin/ask remains repo control plane; skills.lock.json is the default lockfile model; deny-first security precedence is accepted; JSC-391 scaffold is complete. |
| fillable_gaps | Scanner mandatory set, first representative fixture skill, and parent tracker issue remain explicit plan-time decisions. Refs/evals/signing/sandbox/explorer are placeholders only in V1.0. |
| guardrails | Schema validation, command contract tests, fixture tests, receipt validation, risk-tier tests, install-preview no-write tests, placeholder-state tests, and repo closeout gates. |
| refusal_triggers | Editing generated projections as source; claiming install writes work from preview-only code; marking placeholder lifecycle checks as pass; bypassing ./bin/ask; requiring Tessl; starting marketplace or registry work. |
| durable_memory | Record decisions in the spec, this plan, receipts, closeout report, and any required steering uptake if a repeated failure class appears. |
| professional_output | Closeout must list changed files, exact commands, pass/fail/blocked outcomes, accepted blockers, warnings, next action, and rollback path. |

## Coding and Testing Lenses

coding_lens:

- Preserve ./bin/ask authority, accepted SDK scaffold paths, generated artifact boundaries, structured schemas, deterministic errors, and thin command facade.
- Do not edit runtime projections, plugin caches, global skill roots, or generated mirrors as source.
- Keep skills-sdk thin. Route durable repo operations through ./bin/ask until extraction is proven.
- Prefer structured schemas, JSON/YAML parsers, and fixture-backed result models over ad hoc string parsing.
- Keep command output progressively disclosed: default health card has one next action; --json and receipts carry full detail.
- Failure states must classify blockers with deterministic reason codes rather than generic exceptions.

testing_lens:

- Observable behavior matters more than private helper shape.
- Positive tests must cover a minimal valid skill, a referenced skill, a scripted skill, and install-preview output.
- Negative tests must cover missing frontmatter, generated projection source rejection, unknown scope, placeholder lifecycle states, and mandatory adapter unavailable states.
- Receipt tests must validate schema URI, status enum, command version, work mode, proof type, evidence kind, sensor IDs, actor role, approval decision, placeholder state, and redaction posture.
- Install preview tests must prove no lockfile, trust store, projection, or global path writes occur.
- Validation must record exact commands and outcomes after every completed unit.

## Work Units

### PU-001: Baseline Refresh and Parent Tracker Gate

Objective: Reconfirm repo and tracker state before implementation starts, and create or promote the V1.0 parent issue if the user authorizes external tracker mutation.

Source trace: SA-015, SA-023, VP-019, spec Linear Work Item Contract.

Allowed paths or areas: .harness/evidence/**, .harness/reports/**, optional Linear if separately authorized.

Forbidden paths or areas: implementation code, runtime projections, global installs.

Steps:

- Refresh git status --short --branch and git log -1 --oneline.
- Check current Linear issue state for JSC-390, JSC-391, and SDK platformization parent candidates.
- If authorized, create/promote a V1.0 parent issue and record the URL in the plan or closeout.
- If not authorized, record linear_mutation_status: confirmation_required and proceed only with local plan/code slices when the user explicitly waives tracker mutation.

Validation command/evidence: git status, git log, and Linear state query when available.

Stop condition: Tracker scope is ambiguous and the user has not waived parent issue creation.

Rollback note: No code rollback. Remove or supersede any mistakenly created tracker issue only with explicit user approval.

Handoff state: blocked until tracker creation is approved, or ready if user waives tracker mutation for local implementation.

### PU-002: Schema Spine for Manifest, Receipt, Risk, and Preview

Objective: Add versioned schemas for V1.0 manifest/source shape, check receipt, risk classification, install preview, lockfile preview, and placeholder lifecycle states.

Source trace: FR-003, FR-006, FR-008, FR-009, FR-010, NFR-004, SA-003, SA-004, SA-005, SA-020, SA-021, VP-001, VP-002, VP-011, VP-021.

Allowed paths or areas: Infrastructure/config/schemas/skills-sdk/**, Infrastructure/tests/fixtures/skills_sdk/**, Docs/reference/skills-sdk/**.

Forbidden paths or areas: runtime projection roots, global config, plugin cache.

Steps:

- Inspect existing placeholder schemas from JSC-391 before adding new contracts.
- Define schema URIs and version names for V1.0.
- Encode receipt statuses: pass, warning, blocked, degraded, quarantined, not_run, skipped_optional.
- Encode failure taxonomy and exit-code mapping.
- Encode work mode, proof metadata, sensor metadata, actor role, approval decision, command version, and redaction posture.
- Add positive and negative fixtures for schema validation.

Validation command/evidence: targeted schema fixture tests and JSON schema validation through the repo-selected test route.

Stop condition: Any schema field cannot map back to an FR, SA, VP, or apparatus-lens status vocabulary.

Rollback note: Revert schema files and fixtures from this unit only; later units depend on these versions.

Handoff state: ready_for_pu_003 after schema tests pass.

### PU-003: skills-sdk check Command Facade

Objective: Implement the first product command facade so authors can run skills-sdk check while ./bin/ask remains the repo control plane.

Source trace: FR-001, FR-002, FR-009, FR-024, NFR-003, NFR-009, NFR-010, SA-002, SA-005, SA-012, VP-003, VP-011, VP-024.

Allowed paths or areas: repo command wrappers, Infrastructure/bin/**, parser/action metadata, command tests, docs for command contract.

Forbidden paths or areas: package manager install roots unless existing command pattern requires them; global shell profile changes.

Steps:

- Inspect current ./bin/ask command routing before adding facade behavior.
- Add or route a skills-sdk check command that can run locally and return deterministic exit codes.
- Prefer a repo-local ./bin/skills-sdk wrapper over an installed global command; the wrapper must delegate to the ./bin/ask SDK route or block with command_surface_gap.
- Add parser/action metadata parity coverage so ./bin/ask help, the skills-sdk facade, and robot JSON expose the same command contract.
- Emit a default health card with one next action.
- Emit --json output and receipt path/evidence fields from the same result model.
- Keep unknown or unsupported lifecycle commands unavailable with classified output, not silent pass.

Validation command/evidence: command help/metadata parity tests, CLI contract tests, and manual smoke commands for both ./bin/ask sdk check and ./bin/skills-sdk check when both surfaces exist. If the wrapper is deferred, record command_surface_gap with the single accepted route.

Stop condition: Command facade bypasses ./bin/ask authority or emits output that cannot validate against PU-002 schemas.

Rollback note: Remove facade route and command tests; preserve schemas if still valid for future route.

Handoff state: ready_for_pu_004 after command and output tests pass.

### PU-004: Risk Tier Classifier and Sensor Placement

Objective: Classify source shape and risk tier before gate selection, and record sensor placement for V1.0 gates.

Source trace: FR-003, FR-018, FR-019, NFR-001, NFR-002, SA-025, SA-026, SA-027, SA-028, VP-020, VP-022.

Allowed paths or areas: Infrastructure/** SDK modules, fixtures, schema docs, tests.

Forbidden paths or areas: live sandbox execution, external scanner invocation unless explicitly classified as optional adapter detection.

Steps:

- Model docs-only, referenced, scripted, external, and placeholder/package states.
- Classify probability, impact, detectability, cost, blocking behavior, and receipt requirement for each V1.0 sensor.
- Select cheap coding-session checks before integration or CI checks.
- Ensure high-cost scanners remain optional adapter states unless the selected risk tier makes them mandatory.

Validation command/evidence: risk classifier tests, sensor metadata receipt tests, and negative tests for ambiguous or external source shapes.

Stop condition: Risk tier changes activate heavy gates by blanket policy instead of risk evidence.

Rollback note: Revert classifier and sensor metadata changes; command can fall back to blocked risk_classifier_unavailable.

Handoff state: ready_for_pu_005.

### PU-005: Install Preview and Lockfile Model Stub

Objective: Implement a read-only install-preview path that explains planned writes without performing them.

Source trace: FR-004, FR-005, FR-006, FR-007, FR-010, FR-011, SA-006, SA-020, SA-021, VP-004, VP-005, VP-016.

Allowed paths or areas: SDK install module, schemas, fixtures, tests, docs/examples.

Forbidden paths or areas: real project/workspace/global skill install writes, trust-store writes, lockfile writes outside test temp dirs, runtime projections.

Steps:

- Model project, workspace, and global scopes.
- Default lockfile model to skills.lock.json.
- Emit target paths, digest, permissions, trust state, conflicts, lockfile delta preview, rollback path, and receipt.
- Prove preview does not write to lockfile, trust store, projection roots, or global skill roots.
- Emit blocked or policy_denied for ambiguous scope, denied target, or missing trust context.

Validation command/evidence: install preview fixture tests, no-write tests using temp directories and path assertions, and receipt schema validation.

Stop condition: Preview mutates live state or implies installation is complete.

Rollback note: Remove preview route and install tests; keep schema if still accurate.

Handoff state: ready_for_pu_006.

### PU-006: Honest Placeholder Lifecycle Receipts

Objective: Add placeholder receipt producers for refs ingestion, evals, package signing, sandbox/security adapters, and static docs/explorer contracts.

Source trace: FR-012 through FR-023, SEC-001 through SEC-011, SA-007 through SA-011, SA-017 through SA-019, SA-022, VP-006 through VP-010, VP-012 through VP-018.

Allowed paths or areas: schemas, fixtures, placeholder modules, docs/examples, tests.

Forbidden paths or areas: real scanner orchestration, real sandbox execution, hosted publishing, signing key access, Tessl requirement.

Steps:

- Add receipt states for lifecycle surfaces that are intentionally unavailable in V1.0.
- Ensure optional adapters can report available, missing, misconfigured, blocked, and optional without credentials.
- Ensure missing mandatory adapters fail closed for the selected risk tier.
- Emit not_run, skipped_optional, or blocked rather than pass for unimplemented lifecycle features.

Validation command/evidence: placeholder lifecycle tests, adapter detection state tests without live credentials, and conditional static explorer boundary tests only if explorer placeholders are user-visible.

Stop condition: Any placeholder output can be misread as implemented lifecycle capability.

Rollback note: Revert placeholder producers and tests; schemas may remain if they correctly reserve future fields.

Handoff state: ready_for_pu_007.

### PU-007: Evidence Packaging, Reviews, and Closeout

Objective: Package V1.0 evidence so local truth, PR state, CI state, review state, tracker state, and merge readiness remain separate.

Source trace: SA-012, SA-023, SA-029, VP-019, VP-023, apparatus professional output.

Allowed paths or areas: .harness/evidence/**, .harness/reports/**, review artifacts, PR body.

Forbidden paths or areas: merge, force-push, admin-merge, tracker closure without explicit approval.

Steps:

- Run the focused test suite for changed SDK files.
- Run repo closeout wrapper or classify blocker ownership.
- Record accepted blockers, especially external or quota-based checks, separately from local validation.
- Run requested review lanes only when explicitly requested; do not make agent swarm review a hidden blocker.
- Prepare PR summary with exact commands and outcomes.

Validation command/evidence: git diff --check, targeted pytest, repo closeout wrapper, and PR checks/review thread state after PR creation.

Stop condition: A done claim would collapse local code truth, PR/CI truth, review truth, tracker truth, or merge readiness into one status.

Rollback note: Ordinary rollback reverts V1.0 commits; emergency rollback disables skills-sdk facade while preserving schema receipts as degraded/blocking output.

Handoff state: explicit_stop after closeout unless user authorizes implementation continuation.

## Dependencies and Sequencing

PU-001 Baseline and parent tracker gate -> PU-002 Schema spine.

PU-002 Schema spine -> PU-003 skills-sdk check, PU-004 Risk and sensors, PU-006 Placeholder lifecycle receipts.

PU-003 skills-sdk check plus PU-004 Risk and sensors -> PU-005 Install preview.

PU-005 Install preview plus PU-006 Placeholder lifecycle receipts -> PU-007 Evidence and closeout.

PU-001 is the only tracker-dependent gate. PU-002 must precede behavior. PU-003 and PU-004 can proceed in parallel only after schemas exist. PU-005 requires both command output and risk metadata. PU-006 can be developed against schemas once command output can display placeholder states. PU-007 closes the local and PR lanes without treating one lane as proof for another.

## Validation Gates

| Gate | Status | Planned command or evidence | Owner |
| --- | --- | --- | --- |
| Artifact identity lint | required | python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md | Proves plan artifact identity fields are parseable before handoff. |
| Linear traceability lint | required | python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md | Proves JSC-linked traceability is explicit before implementation. |
| BLUF structure | required | python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md --json | Proves the plan has a reader-facing BLUF before handoff. |
| Generated artifact shape | required | python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md --kind plan --json | Proves required plan sections, work units, rollback, runtime fields, and validation structure exist. |
| Existing scaffold preservation | required | uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_scaffold.py -q, or the repo-selected Python wrapper discovered during PU-001 | Observable behavior: JSC-391 scaffold path rejection and fixture contracts still pass. Source: SA-024 through SA-029. |
| Schema and receipt fixtures | required after PU-002 | Targeted schema/fixture tests selected by changed files. | Observable behavior: valid manifests and receipts pass; invalid states fail. Source: FR-003, FR-008, VP-001, VP-002. |
| Command facade tests | required after PU-003 | Targeted command tests and skills-sdk check smoke route. | Observable behavior: health card, JSON output, receipt path, and exit codes match the contract. Source: FR-001, FR-002, VP-003, VP-011. |
| Risk and preview tests | required after PU-004 and PU-005 | Risk classifier, sensor metadata, install-preview no-write tests. | Observable behavior: risk gates are selected before execution, and preview writes no live state. Source: FR-003, FR-005, VP-020, VP-004. |
| Placeholder honesty tests | required after PU-006 | Placeholder lifecycle and adapter-state tests. | Observable behavior: unimplemented refs, evals, signing, sandbox, and explorer states emit not_run, skipped_optional, or blocked, never pass. Source: FR-012 through FR-023, VP-006 through VP-018. |
| Repo closeout | required after implementation | ./bin/ask repo closeout --changed --json --robot or blocked with ownership classification. | Proves local closeout lane without claiming PR, CI, tracker, or merge readiness. Source: SA-012, SA-029. |
| PR checks | required after PR | gh pr checks <number> --watch=false with accepted external blockers separated. | Proves current CI lane only; does not prove review or tracker state. |

## Review Plan

- After each implementation unit, run the local skill checks requested by the user for the governed execution style: simplify, improve-codebase-architecture, testing, and ubiquitous-language, or record the exact reason if a skill is unavailable.
- Do not run an agent swarm as an implicit blocker. The user separated swarm review from the implementation lane.
- Treat advisory reviews as findings until they are backed by computational proof, accepted deferral, or evidence-backed non-applicability.
- P1/P2 findings cannot close from summary text alone.

## Rollback Plan

- PU-002 rollback: remove schema and fixture files added for V1.0.
- PU-003 rollback: remove skills-sdk facade route and command tests; keep schemas if future-compatible.
- PU-004 rollback: remove risk classifier and sensor metadata; command emits blocked classifier-unavailable state.
- PU-005 rollback: remove install-preview route; ensure no test temp lockfiles are committed.
- PU-006 rollback: remove placeholder producers; leave reserved schema fields only if schema tests still pass.
- PU-007 rollback: correct evidence artifacts or PR body; do not rewrite commit history without explicit approval.

## Risk Register

| Risk | Probability | Impact | Detectability | Mitigation |
| --- | --- | --- | --- | --- |
| V1.0 expands into full V1 platform | medium | high | medium | Keep work units bound to schemas, check, risk, preview, and placeholders. |
| skills-sdk diverges from ./bin/ask | medium | high | high | Command metadata and parser/action parity tests. |
| Placeholder states look implemented | medium | high | high | Receipt schema and negative tests require not_run, skipped_optional, or blocked. |
| Install preview writes real state | low | high | high | No-write tests and forbidden path assertions. |
| Scanner stack decision stalls implementation | medium | medium | high | Keep scanners as adapter detection placeholders in V1.0 unless user accepts mandatory set. |
| Tracker parent remains missing | medium | medium | high | PU-001 blocks or records explicit waiver before implementation. |

## Observability and Evidence

Evidence must be written or linked by unit:

- Baseline: repo status, commit, tracker state.
- Schema: validation output and fixture matrix.
- Command: health card sample, JSON output, receipt sample, exit code matrix.
- Risk: classifier matrix and sensor placement receipt.
- Preview: target path preview, conflict example, no-write assertion.
- Placeholders: lifecycle state receipts and adapter-state examples.
- Closeout: command outcomes, PR/CI state, review state, tracker state, accepted blockers, rollback note.

## Visual References / Diagrams

The dependency sequence in Dependencies and Sequencing is the required visual reference. Generated bitmap media is not needed because this is an execution sequencing plan, not a UI or presentation artifact.

## Accessibility and Operator Ergonomics

- Default human output has one next action.
- Machine output remains available through --json and receipt paths.
- Status does not depend on color.
- Error messages explain what failed, why it matters, and how to recover.
- Evidence is progressively disclosed so agents can parse receipts without flooding the human path.

## Open Questions

| ID | Question | Plan handling |
| --- | --- | --- |
| OQ-001 | Docs and Skill Explorer domain/subdomain layout | Deferred; not in V1.0 implementation. |
| OQ-005 | Mandatory scanner stack versus optional adapter detection | Treat as optional adapter detection in V1.0 unless user accepts a mandatory set. |
| OQ-006 | Repo-local static output first or hosted site first | Deferred; V1.0 may reserve manifest fields only. |
| OQ-007 | First representative skill package fixture | Implementation should prefer existing Infrastructure/tests/fixtures/skills_sdk/valid_skill and draft_package unless repo inspection finds a better representative package. |

## Final Decision

Proceed to V1.0 planning handoff, not implementation closeout. The next executor must refresh live state, resolve or waive parent tracker mutation, then execute PU-001 through PU-007 with command-backed proof after every slice.

## Appendix A. Harness Metadata / Traceability

interactive_status: not_requested

selection_evidence:

- User confirmed this spec as the next artifact.
- User selected skills-sdk as the extracted CLI name.
- User accepted moving to the bounded V1.0 plan after JSC-391 completion.

route: he-plan

stage: plan

scope:

- In scope: V1.0 implementation plan from accepted Skills SDK V1 product spec.
- Out of scope: code implementation, marketplace, full registry, hosted docs, global install, Linear mutation without approval.

plan_path: .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md

traceability:

- Spec: .harness/specs/2026-06-03-skills-sdk-v1-product-spec.md
- Scaffold PR: #221
- Scaffold merge commit: c3ff670f3
- Acceptance IDs: SA-001 through SA-029, with V1.0 emphasis on SA-002 through SA-006, SA-012 through SA-015, SA-020, SA-021, SA-024 through SA-029.

validation:

- Plan validators required before handoff.
- Implementation validators are listed by work unit and must rerun after edits.

safe_to_continue: true

blocked_reason: not_applicable_for_plan

linear_action_required: true

linear_mutation_status: confirmation_required

post_plan_handoff:

- state: explicit_stop
- next_route: he-work after user authorizes implementation and parent tracker handling

authority_scope_boundary:

- Plan artifact only. No implementation or external tracker mutation performed by this artifact.

runtime_persistence:

- This plan persists as the V1.0 resumption key. Runtime, PR, CI, review, and tracker states must be refreshed in the implementation session.

coding_lens:

- Preserve ./bin/ask authority, accepted SDK scaffold paths, generated artifact boundaries, structured schemas, deterministic errors, and thin command facade.

testing_lens:

- Validate command behavior, schema shape, risk classification, install-preview no-write behavior, placeholder honesty, and closeout lane separation.

blackboard_delta:

- JSC-391 scaffold gate is now complete and should not be planned again.
- skills-sdk is the accepted product CLI name.
- skills.lock.json is the default lockfile model unless implementation evidence requires a narrower equivalent.

git_staging_status: unstaged

staged_paths: []

confidence:

- high: scaffold completion and source spec path are verified in repo.
- high: skills-sdk CLI naming decision was provided by the user.
- medium: scanner and representative fixture choices remain plan-time decisions.
- medium: Linear parent issue is required by the spec but not mutated by this plan.

stage_arc_boundary:

- left_arc: accepted V1 spec plus completed JSC-391 scaffold gate.
- active_arc: V1.0 implementation planning artifact only.
- right_arc: governed implementation via he-work or goal-governed slices after tracker handling.
- coding_lens: schema-first, command-proof-first, generated-boundary-preserving implementation.
- testing_lens: fixture-backed, receipt-backed, no-write, placeholder-honesty validation.

## Appendix B. Linear / Tracker Handoff

Suggested parent issue title:

Implement Skills SDK V1.0 schema, check, risk, and install-preview slice

Suggested scope:

- Build skills-sdk check facade through repo control plane.
- Add manifest/check receipt/risk/install-preview schemas.
- Add risk classifier and sensor metadata.
- Add read-only install preview with skills.lock.json delta model.
- Add honest placeholder receipts for refs, evals, signing, sandbox, and explorer.
- Add fixture-backed tests and closeout evidence.

Suggested blockers:

- Blocks follow-on refs ingestion, eval runner, signing, sandbox execution, docs/explorer, and real install/update work.
- Is blocked by parent tracker creation or explicit user waiver.

## Appendix C. Review Outcomes

Review status: coordinator adversarial fixes applied; plan validation passing; independent subagent artifact coverage blocked_runtime.

Coordinator adversarial review loop:

- Requested subagent reviewers: agent-native-reviewer, architecture-strategist, adversarial-reviewer, autoresearch-validator.
- Runtime result: reviewer threads did not produce artifact files after bounded retries and were treated as blocked_runtime for this planning pass.
- Coordinator fix-now findings applied: command facade ambiguity, fuzzy Python validation route, and stale pending-validation status.
- Loop status after fixes: no additional coordinator fix-now findings before implementation; independent subagent coverage remains a separate runtime gap, not evidence that the plan was independently approved.

Validation commands:

- python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
- python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md
- python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md --json
- python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md --kind plan --json
