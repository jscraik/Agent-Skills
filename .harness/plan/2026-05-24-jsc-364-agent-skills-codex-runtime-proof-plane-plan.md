---
schema_version: 1
artifact_id: he-plan-2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane
artifact_type: he-plan-standard
canonical_slug: jsc-364-agent-skills-codex-runtime-proof-plane
title: JSC-364 Agent Skills Codex Runtime Proof Plane Plan
harness_stage: he-plan
status: ready_for_he_work
date: 2026-05-24
origin: .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md
source_spec: .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md
risk: high
depth: deep
ui: false
traceability_required: true
linear_mutation_status: already_linked
linear_action_required: none
linear_status: Todo
linear_issue: JSC-364
linear_issue_url: https://linear.app/jscraik/issue/JSC-364/agent-skills-add-codex-runtime-proof-plane
linear_parent_issue: JSC-351
linear_team: JSC
linear_workspace: Jscraik
linear_priority: 2
linear_labels:
  - agent-skills
  - Governance
  - Agent-Native
  - Reliability
  - Developer Experience
  - Roadmap: Now
  - Feature
---

# JSC-364 Agent Skills Codex Runtime Proof Plane Plan

## Command Summary

BLUF: This plan gives the implementing agent, developer, and reviewer a safe sequence for turning the JSC-364 runtime proof plane spec into reachable agent-skills code without letting modeled Codex parity masquerade as live proof. The reason to do this first is operational trust: repo doctor and closeout need machine-readable evidence that survives runtime absence, stale branches, and partial artifact visibility. The highest risk is false success, so the immediate action is command-handle drift repair, schema-backed runtime cards and evidence receipts, then a Codex-targeted proof command that emits either durable proof or blocked_runtime evidence.

Decision Needed: No product decision is needed before the first implementation slice. If implementation discovers that the Codex source fixture must be vendored or that Linear project or cycle ownership must change, stop and request owner approval before mutating those surfaces.

Top Risks: Generated command handles can drift while repo doctor still looks green; schema artifacts can be created without being wired into proof commands; Codex preview can report modeled parity without source identity; runtime absence can collapse into vague failure prose instead of blocked_runtime evidence.

Next Action: Start PU-001, repair command-handle drift, and capture a before and after repo doctor delta before adding the broader runtime proof schema layer.

## Objective

Turn the JSC-364 specification into an execution plan for adding a Codex Runtime Proof Plane to agent-skills.

The plan prioritizes trust-boundary repair before feature expansion. The first proof that matters is not a new concept document; it is an executable path where ./bin/ask can say which runtime target was checked, which evidence was produced, which artifacts were visible to Codex, and why the run is blocked when live runtime proof cannot complete.

## Source Contract

| Source | Status | Use In This Plan |
|---|---:|---|
| .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md | canonical | Requirements, acceptance IDs, runtime status enum, validation gates, Linear mapping |
| JSC-364 Linear issue | live tracker source | Tracker status, parent link to JSC-351, priority, labels, and work item identity |
| .harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md | supporting evidence | Gap framing around runtime proof, claim verification, traces, recovery, governance |
| .harness/research/deep/2026-05-24-jamie-craik-evidence.md | supporting evidence | Harness engineering patterns for proof surfaces, runtime truth, and agent-operable closeout |
| /Users/jamiecraik/dev/codex | read-only source context | Codex runtime source identity and preview behavior reference; not an implementation target for this plan |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | runtime source | Skills command implementation path for handles, conformance, capability discovery, proof |
| Infrastructure/scripts/lib/ask/commands/repo_impl.py | runtime source | Repo doctor command-handle gate and next-command behavior |
| Infrastructure/scripts/lib/ask/services/codex_preview.py | runtime source | Existing Codex preview source identity, truncation, and partial-depth behavior |
| Infrastructure/scripts/lib/ask/skills_sdk/conformance.py | runtime source | Existing conformance suite path that must split modeled conformance from live parity |
| Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py | runtime source | Existing runtime adapter and blocked_runtime behavior surface |
| Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py | validation source | Public wrapper fixture lane that must cover runtime proof and capability discovery |
| Infrastructure/tests/test_ask_skills_doctor.py | validation source | Doctor/runtime proof regression surface including blocked_runtime behavior |
| Infrastructure/tests/test_ask_skills_codex_preview.py | validation source | Existing Codex preview source identity and truncation regression surface |

## Scope and Boundaries

### In Scope

- Command-handle drift repair for skills command handles and repo doctor enforcement.
- RuntimeCard, EvidenceReceipt, ArtifactRecord, RuntimeSessionSummary, and RecoveryPlanSummary schemas needed for the P0 proof plane.
- CapabilityDiscovery and shared-workspace visibility fields when they are needed to make proof agent-operable.
- Codex parity conformance status separation: modeled_conformance, live_runtime_parity, blocked_runtime.
- Codex preview source identity, truncation, and partial-depth reporting.
- ./bin/ask skills proof HANDLE --runtime-target codex --json --robot as a reachable proof path.
- Validation scripts and focused tests that prove runtime cards, evidence receipts, and wrapper contracts.
- Evidence output under repo-owned .harness/evidence or temporary test paths when commands require artifacts.

### Out of Scope

- Mutating /Users/jamiecraik/dev/codex or treating it as the delivery repo.
- Editing global Codex config, user home runtime state, plugin caches, or runtime projections to force a proof pass.
- Publishing packages, installing global tools, or using network writes as part of proof.
- Building a broad new orchestration framework before the P0 proof plane is enforced.
- Treating documentation-only schemas or tests without command reachability as completion.
- Changing Linear project, cycle, or ownership metadata without explicit owner approval.

## Current State / Evidence

| Finding | Evidence | Plan Impact |
|---|---|---|
| JSC-364 is live and linked as a child of JSC-351. | Linear MCP get_issue returned JSC-364 with status Todo, priority High, parent JSC-351, and the runtime proof plane description. | Tracker traceability can be attached to this plan, but implementation should not mutate project or cycle metadata. |
| Repo doctor already references generated command-handle checking. | Infrastructure/scripts/lib/ask/commands/repo_impl.py defines COMMAND_HANDLES_COMMAND as ./bin/ask skills handles --check --no-handles --check-command-handles --json --robot. | PU-001 should verify this is reachable, blocking, and delta-reported rather than rebuilding the concept. |
| Runtime proof has some blocked_runtime behavior already. | Infrastructure/tests/test_ask_skills_doctor.py includes blocked_runtime expectations around runtime reachability and Codex-targeted proof. | PU-006 should extend and schema-bind existing behavior instead of replacing it. |
| Codex preview already reports source identity and truncation cases in tests. | Infrastructure/tests/test_ask_skills_codex_preview.py covers SOURCE_IDENTITY, sibling Codex repo absence, git revision failure, and budget truncation warnings. | PU-005 can harden the preview ABI around the existing service and test surface. |
| Conformance has an existing codex-parity command path. | Infrastructure/scripts/lib/ask/skills_sdk/conformance.py references ./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir PATH. | PU-003 should split status semantics and evidence contracts in place. |
| Wrapper fixtures do not yet prove runtime proof plane commands. | Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py currently validates baseline repo status, skills list, and plugin doctor/status fixtures. | PU-004 should add wrapper-level proof and capability fixtures so public ./bin/ask use is covered. |
| The spec now distinguishes modeled conformance from live runtime parity. | FR-003, FR-011, FR-012, and the runtime status enum define separate statuses. | Work must preserve that boundary across conformance, proof, doctor, and closeout output. |
| P1 schema ideas are intentionally not P0 blockers. | FR-021 moves CommandAttempt, FailureClassification, ValidatorResult, ContextPacket, and DependencySource to later extension scope. | PU-002 must avoid overbuilding the schema layer while leaving extension points stable. |

## Implementation Strategy

1. Repair the false-success boundary first by proving command handles and repo doctor drift are enforced.
2. Add the smallest P0 schema set that can validate runtime cards and evidence receipts without dragging P1 telemetry into the first slice.
3. Split modeled conformance from live runtime parity in command output, test expectations, and evidence files.
4. Extend public wrapper fixtures and capability discovery so agents can discover, invoke, and validate the proof plane without private implementation knowledge.
5. Harden Codex preview source identity and truncation behavior before any command claims parity from preview data.
6. Wire ./bin/ask skills proof HANDLE --runtime-target codex into RuntimeCard and EvidenceReceipt output, including blocked_runtime probes.
7. Add shared-workspace visibility and agent-operable closeout evidence only after the proof command can produce durable evidence.
8. Close with full validation, review, and tracker evidence, separating local proof from live Linear and PR state.

## Enforcement Contract

### essential_decisions

- JSC-364 is a runtime proof plane, not another prose-only governance layer.
- Command-handle drift is the first trust boundary because repo doctor cannot be trusted while command recommendation handles are stale or non-blocking.
- The P0 schema set is limited to RuntimeCard, EvidenceReceipt, ArtifactRecord, RuntimeSessionSummary, and RecoveryPlanSummary.
- modeled_conformance, live_runtime_parity, and blocked_runtime are separate statuses and must stay separate in CLI output, tests, and evidence.
- The proof command must emit durable proof or durable blocked_runtime evidence; an unstructured error is not acceptable proof.

### fillable_gaps

- Exact module names for schema helpers, evidence writers, and runtime card validators can be chosen during implementation if they remain under Infrastructure-owned paths.
- Evidence output path conventions can use a temporary directory for tests and .harness/evidence for durable local proof, provided commands report the path.
- CapabilityDiscovery may be implemented as a skills subcommand or a proof-plane subcommand if ./bin/ask exposes the same machine-readable fields.
- The Codex source reference can be live /Users/jamiecraik/dev/codex source or checked fixtures, but every preview result must report which basis was used.

### guardrails

- Do not claim live Codex parity from source inspection, modeled conformance, or .agents readiness.
- Do not create schemas that are not validated by a reachable command or test.
- Do not silently downgrade runtime absence into success.
- Do not mutate /Users/jamiecraik/dev/codex, global Codex config, plugin caches, or generated runtime projections as part of this implementation.
- Do not make P1 telemetry schemas required for P0 acceptance.

### refusal_triggers

- A fix requires editing /Users/jamiecraik/dev/codex rather than reading it as source context.
- The proof command cannot produce either RuntimeCard proof or blocked_runtime evidence.
- Repo doctor reports green while command-handle drift remains detectable.
- Evidence receipts omit command, exit code, runtime target, source identity, or blocker fields needed by the spec.
- Tracker or external service mutation is required without explicit owner approval.

### durable_memory

- If command-handle drift appears again, record the failure class and durable validator in .harness/quality/steering-uptake.md and validate steering uptake.
- If blocked_runtime handling changes, preserve a fixture that proves the probe command, blocker class, artifact path, and operator next action.
- If Codex preview source identity changes, update the source identity tests and keep the plan/spec traceability row current.

### professional_output

- CLI human output should name the runtime target, evidence path, and next command without dumping raw schema internals.
- JSON output should preserve stable field names, enums, and unknown-field compatibility expectations.
- Closeout output should separate command proof, schema proof, live tracker truth, PR state, and remaining blockers.

## Work Units

### PU-001: Command-Handle Drift Repair And Repo Doctor Baseline

Source IDs: FR-002, FR-009, FR-010, SA-001, SA-002, VAL-001, VAL-002, VAL-014.

Objective: Make command-handle drift mechanically visible and blocking before runtime proof features expand.

Allowed path: Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/scripts/lib/ask/commands/repo_impl.py, Infrastructure/tests/test_ask_skills_doctor.py, Infrastructure/tests/test_ask_cli_impl.py, generated command-handle fixtures owned by existing generators.

Forbidden path: /Users/jamiecraik/dev/codex, .agents runtime projections, Plugins/cache, global Codex config, unrelated skill bodies.

Implementation steps:

1. Reproduce current command-handle and repo doctor behavior.
2. Verify ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot is reachable from the public wrapper.
3. Ensure repo doctor treats command-handle drift as a distinct check with a clear next command and before/after delta.
4. Add regression coverage for stale command recommendations and the repaired path.

Validation: ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot; ./bin/ask repo doctor --json --robot; focused pytest for doctor and handles.

Stop condition: Stop if generator ownership for command handles is unclear or if repo doctor cannot report the drift check without unrelated failures masking it.

Rollback: Revert command-handle generator/check changes and doctor wiring for this unit only, preserving test fixtures for investigation.

Handoff: Continue to PU-002 only when command-handle drift is either green or explicitly reported as the first blocker with a reproducible next command.

### PU-002: P0 Runtime Evidence Schemas And Validator

Source IDs: FR-001, FR-004, FR-014, FR-015, FR-024, FR-029, FR-030, SA-005, SA-006, SA-016, SA-017, VAL-007, VAL-013.

Objective: Create the smallest schema and validation layer that can prove runtime evidence without overbuilding P1 telemetry.

Allowed path: Infrastructure/config/schemas, Infrastructure/scripts/validation-and-linting, Infrastructure/tests, Infrastructure/scripts/lib/ask/skills_sdk, .harness/evidence test fixtures.

Forbidden path: global runtime caches, plugin package cache, published package metadata, user home Codex state, unrelated docs.

Implementation steps:

1. Add schemas for RuntimeCard, EvidenceReceipt, ArtifactRecord, RuntimeSessionSummary, and RecoveryPlanSummary.
2. Encode required fields, runtime status enum, artifact visibility fields, blocked_runtime probe fields, and recovery command fields.
3. Add a validator command or script that can validate runtime card files and evidence receipt files.
4. Add positive and negative fixtures for missing command, missing runtime target, missing blocker class, and missing shared workspace visibility.

Validation: python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <fixture-or-evidence-path> --json; focused pytest for valid and invalid schema fixtures.

Stop condition: Stop if schema dependencies require network install or if P1 schema concepts become necessary to satisfy P0 acceptance.

Rollback: Remove the schema files, validator entrypoint, and fixtures added in this unit.

Handoff: Continue to PU-003 and PU-006 only after the validator can reject malformed runtime evidence deterministically.

### PU-003: Codex Parity Conformance Status Split

Source IDs: FR-003, FR-011, FR-012, SA-003, SA-004, VAL-003.

Objective: Make conformance output distinguish source-modeled compatibility from live Codex runtime proof.

Allowed path: Infrastructure/scripts/lib/ask/skills_sdk/conformance.py, Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/tests/test_pr196_jsc351_governed_closeout.py, new focused conformance tests if needed.

Forbidden path: /Users/jamiecraik/dev/codex mutation, broad SDK rewrites, generated runtime projections, unrelated package code.

Implementation steps:

1. Inspect existing codex-parity suite output and evidence file shape.
2. Add explicit modeled_conformance, live_runtime_parity, and blocked_runtime status fields.
3. Ensure blocked live runtime does not fail the modeled conformance result unless the schema or command contract says it should.
4. Add tests for each status split and for evidence output consumed by later runtime card validation.

Validation: ./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/jsc-364-codex-parity --json --robot; focused pytest for conformance status behavior.

Stop condition: Stop if conformance results cannot report modeled and live status independently without changing the public suite semantics.

Rollback: Revert conformance status additions and tests while preserving any failing fixture as evidence for a later design decision.

Handoff: Continue to PU-006 after conformance can feed proof-plane evidence without overclaiming live parity.

### PU-004: Capability Discovery And Public Wrapper Fixtures

Source IDs: FR-006, FR-022, FR-026, SA-008, SA-014, VAL-004, VAL-012.

Objective: Let an agent discover the runtime proof plane through public ./bin/ask commands and prove wrapper reachability.

Allowed path: Infrastructure/bin/ask, Infrastructure/scripts/lib/ask/commands/skills.py, Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py, Infrastructure/tests.

Forbidden path: private local aliases, shell-only helper scripts with no wrapper path, package manager roots unrelated to ask, plugin cache.

Implementation steps:

1. Add or extend a capability discovery command that reports runtime_target_support, evidence_modes, supported_commands, required_artifacts, and known_limitations.
2. Add wrapper fixtures for proof-plane discovery, conformance, and a blocked_runtime-safe proof command.
3. Ensure fixture output is stable JSON and usable by agents without reading Python internals.
4. Add tests that fail when public wrapper commands drift from implementation.

Validation: ./bin/ask skills capabilities --runtime-target codex --json --robot or the selected equivalent; python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation.

Stop condition: Stop if discovery requires a new command family that conflicts with existing ask command taxonomy.

Rollback: Remove discovery command additions and wrapper fixture rows from this unit.

Handoff: Continue to PU-005 and PU-006 after agents can discover the proof plane from public commands.

### PU-005: Codex Preview Source Identity And Truncation Hardening

Source IDs: FR-007, FR-013, SA-009, VAL-005.

Objective: Ensure Codex preview evidence reports source identity, partial-depth status, and truncation state before it is used in proof.

Allowed path: Infrastructure/scripts/lib/ask/services/codex_preview.py, Infrastructure/tests/test_ask_skills_codex_preview.py, preview fixtures under Infrastructure/tests.

Forbidden path: /Users/jamiecraik/dev/codex writes, vendored Codex source copies without approval, unrelated preview UI, global Codex config.

Implementation steps:

1. Recheck existing SOURCE_IDENTITY, sibling Codex absence, git revision failure, and budget truncation tests.
2. Add missing fields required by the spec for source identity, truncation policy, partial-depth status, and unavailable reason.
3. Ensure preview output can be embedded in RuntimeCard or ArtifactRecord without losing provenance.
4. Add negative tests where Codex source is missing or stale.

Validation: python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q.

Stop condition: Stop if source identity cannot be proven without mutating /Users/jamiecraik/dev/codex or adding unapproved vendored fixtures.

Rollback: Revert preview service and test changes from this unit.

Handoff: Continue to PU-006 once preview evidence is trustworthy enough to attach to runtime proof artifacts.

### PU-006: Codex Runtime Proof Command And Blocked Runtime Evidence

Source IDs: FR-005, FR-014, FR-015, FR-016, FR-017, FR-018, FR-024, FR-029, FR-030, FR-031, SA-007, SA-016, SA-017, SA-018, VAL-006, VAL-013.

Objective: Implement the core proof command that emits a RuntimeCard, EvidenceReceipt, ArtifactRecord data, and a RecoveryPlanSummary.

Allowed path: Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/scripts/lib/ask/commands/skills.py, Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py, Infrastructure/scripts/lib/ask/skills_sdk/contracts.py, Infrastructure/config/schemas, Infrastructure/tests.

Forbidden path: /Users/jamiecraik/dev/codex mutation, global runtime caches, plugin cache, secret stores, publishing paths.

Implementation steps:

1. Add or harden ./bin/ask skills proof HANDLE --runtime-target codex --json --robot.
2. Emit RuntimeCard fields: runtime_session, artifacts, evidence_receipts, verifier_results, workspace_root, actor_type, mutation_scope, visibility_status, limitations, and recovery_plan.
3. Emit EvidenceReceipt fields for command, exit_code, probe_command, probe_exit_code, probe_artifact_path, blocker_class, and suggested next action.
4. Treat runtime absence as blocked_runtime with probe evidence rather than generic failure.
5. Validate emitted artifacts with the PU-002 schema validator inside tests.

Validation: ./bin/ask skills proof testing --runtime-target codex --json --robot; python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <proof-artifact-path> --require-shared-workspace --json; focused pytest for proof and blocked_runtime behavior.

Stop condition: Stop if the command cannot produce schema-valid proof or blocked_runtime evidence for a known fixture handle.

Rollback: Revert proof command changes and schema wiring from this unit while preserving generated evidence for diagnosis.

Handoff: Continue to PU-007 only after proof artifacts are machine-valid and agent-discoverable.

### PU-007: Shared Workspace Evidence And Agent-Operable Closeout

Source IDs: FR-023, FR-027, FR-028, FR-031, SA-010, SA-015, SA-018.

Objective: Make proof artifacts usable by another agent without private session context.

Allowed path: Infrastructure/scripts/lib/ask/skills_sdk, Infrastructure/scripts/lib/ask/commands, Infrastructure/tests, .harness/evidence, .harness/research implementation notes if created by the implementation lane.

Forbidden path: user-private prompt logs, secrets, unredacted local home paths beyond necessary workspace_root, plugin runtime cache.

Implementation steps:

1. Add shared workspace visibility fields to runtime cards and artifact records.
2. Ensure artifact paths are repo-relative or explicitly marked as local-only with limitations.
3. Add closeout output that points to proof artifacts, validation commands, and blocked_runtime recovery steps.
4. Add agent-operable tests or fixtures that discover, invoke, observe, and hand off proof evidence.

Validation: focused pytest for agent-operable closeout fixture; validate_runtime_cards.py with shared workspace requirements; ./bin/ask repo doctor --json --robot after proof evidence exists.

Stop condition: Stop if proof artifacts depend on ephemeral session-only state or private prompt content.

Rollback: Revert shared-workspace evidence and closeout-output changes for this unit.

Handoff: Continue to PU-008 after another agent can follow command output to the proof artifacts and next action.

### PU-008: Final Integration, Review, And Tracker Evidence

Source IDs: SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-012, SA-013, SA-014, SA-015, SA-016, SA-017, SA-018, VAL-001, VAL-002, VAL-003, VAL-004, VAL-005, VAL-006, VAL-007, VAL-008, VAL-009, VAL-010, VAL-011, VAL-012, VAL-013, VAL-014, VAL-015.

Objective: Prove the complete implementation through local validation, review, and live tracker evidence without conflating those proof sources.

Allowed path: implementation-owned files from PU-001 through PU-007, .harness/evidence, .harness/research/implementation-notes if needed for delivery notes, artifacts/reviews for requested review swarm outputs.

Forbidden path: unrelated feature code, broad repo formatting, unapproved Linear mutation, PR or GitHub mutation unless explicitly delegated by the implementation lane.

Implementation steps:

1. Run all unit validation gates and capture exact command outcomes.
2. Run the repository's canonical closeout or doctor wrapper if available and applicable.
3. Request architecture, agent-native, and adversarial review for runtime proof, command contracts, and false-success risks.
4. Refresh JSC-364 live issue state and report local validation separately from tracker state.
5. Prepare a final implementation note with files changed, validation results, residual blockers, and rollback path.

Validation: all commands listed in Validation Gates; live Linear MCP get_issue for JSC-364; reviewer artifacts verified non-empty if a swarm is requested.

Stop condition: Stop if a critical validator fails, if review identifies a false-success path, or if live tracker state contradicts claimed delivery.

Rollback: Revert implementation units in dependency order, starting with proof command wiring and schema registration, then command-handle and doctor enforcement if needed.

Handoff: Handoff state is explicit_stop for this planning artifact; implementation should begin only after the owner authorizes the execution lane.

## Dependencies and Sequencing

| Order | Unit | Depends On | Parallelism | Reason |
|---:|---|---|---|---|
| 1 | PU-001 | none | no | Command-handle and repo doctor truth must be trustworthy before later commands add more claims. |
| 2 | PU-002 | PU-001 | no | Schema validation is the foundation for proof output and blocked_runtime evidence. |
| 3 | PU-003 | PU-002 | partial with PU-004 | Conformance can split status after schemas define evidence boundaries. |
| 4 | PU-004 | PU-002 | partial with PU-003 and PU-005 | Discovery and wrapper fixtures can progress once schema names and proof fields are stable. |
| 5 | PU-005 | PU-002 | partial with PU-003 and PU-004 | Preview hardening can run alongside command wrapper work if source identity remains read-only. |
| 6 | PU-006 | PU-003, PU-004, PU-005 | no | The proof command consumes conformance status, discovery contracts, preview identity, and schemas. |
| 7 | PU-007 | PU-006 | no | Shared-workspace closeout requires real proof artifacts. |
| 8 | PU-008 | PU-001 through PU-007 | no | Integration and review require the complete proof plane. |

## Validation Gates

| Gate | Type | Source Requirement / Acceptance ID | Command | Expected Outcome |
|---|---|---|---|---|
| VAL-001 | pre and post | FR-009, SA-001 | ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot | Observable behavior: command-handle drift is detected before repair and green or explicitly classified after repair. |
| VAL-002 | post | FR-010, SA-002 | ./bin/ask repo doctor --json --robot | Expected outcome: command_handles appears as an enforced repo doctor check with a specific next command. |
| VAL-003 | post | FR-011, FR-012, SA-003, SA-004 | ./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/jsc-364-codex-parity --json --robot | Proof: modeled_conformance and live_runtime_parity are separate, and blocked_runtime is not hidden. |
| VAL-004 | post | FR-006, SA-008 | python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation | Observable behavior: public wrapper fixtures include runtime proof plane commands. |
| VAL-005 | post | FR-007, FR-013, SA-009 | python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q | Expected outcome: source identity, truncation, partial-depth, and unavailable-source cases are covered. |
| VAL-006 | post | FR-005, FR-017, SA-007 | ./bin/ask skills proof testing --runtime-target codex --json --robot | Proof: command emits schema-valid runtime proof or blocked_runtime evidence. |
| VAL-007 | post | FR-014, FR-015, FR-024, SA-005, SA-006, SA-016, SA-017 | python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py <proof-artifact-path> --json | Expected outcome: RuntimeCard and EvidenceReceipt fixtures pass and malformed evidence fails. |
| VAL-008 | post | SA-012 | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | Observable behavior: doctor regressions and blocked_runtime paths stay enforced. |
| VAL-009 | post | SA-012 | python3 -m pytest Infrastructure/tests/test_ask_cli_impl.py -q | Expected outcome: public CLI parser and wrapper behavior remain reachable. |
| VAL-010 | post | SA-012, SA-013 | ./bin/ask repo closeout --changed --json --robot or documented repo closeout equivalent | Proof: changed files, validation evidence, and blockers are reported through the repo closeout surface. |
| VAL-011 | review | SA-013 | reviewer artifacts under artifacts/reviews | Expected outcome: architecture, agent-native, and adversarial reviewers find no blocking false-success or reachability gaps. |
| VAL-012 | post | FR-022, FR-026, SA-014 | ./bin/ask skills capabilities --runtime-target codex --json --robot or selected equivalent | Observable behavior: capability discovery reports runtime target support and limitations. |
| VAL-013 | post | FR-023, FR-027, FR-028, SA-010, SA-015 | validate_runtime_cards.py <proof-artifact-path> --require-shared-workspace --json | Proof: runtime card artifacts are usable from the shared workspace and limitations are explicit. |
| VAL-014 | pre and post | FR-010, SA-002 | ./bin/ask repo doctor --json --robot with before and after evidence | Expected outcome: unrelated failures are separated from command_handles and proof-plane checks. |
| VAL-015 | closeout | JSC-364 tracker contract | Linear MCP get_issue JSC-364 | Expected outcome: live tracker state is refreshed and not confused with local validation. |

## Review Plan

| Reviewer | Trigger | Focus | Required Output |
|---|---|---|---|
| architecture-strategist | After PU-006 or before broad service extraction | Proof-plane boundaries, schema placement, runtime adapter seams, overbuild risk | Severity-ranked findings with file:line evidence and remediation |
| agent-native-reviewer | After PU-004 and PU-007 | Agent discoverability, wrapper reachability, shared-workspace evidence, closeout handoff | Severity-ranked findings with exact command and artifact evidence |
| adversarial-reviewer | Before PU-008 closeout | False-success paths, stale-state handling, blocked_runtime quality, unsafe external assumptions | Severity-ranked findings and explicit no-further-blockers status |
| api-contract-reviewer | Conditional if JSON schemas or public command output change materially | CLI JSON compatibility, enum stability, unknown-field behavior, schema versioning | Contract-risk findings and compatibility notes |

Reviewer artifacts should be written under artifacts/reviews/jsc-364-runtime-proof-plane/ when a swarm is requested. The coordinator must verify artifacts exist and are non-empty before treating review as complete.

## Rollback Plan

| Rollback Slice | Action | Preserved Evidence |
|---|---|---|
| PU-001 | Revert command-handle generator/check and repo doctor wiring. | Failing handle fixture and before/after doctor output. |
| PU-002 | Remove P0 schemas, validator, and schema fixtures. | Invalid fixture cases and validator failure output. |
| PU-003 | Revert conformance status split. | Evidence file showing why modeled/live separation failed. |
| PU-004 | Remove capability discovery additions and wrapper fixture rows. | Wrapper validator output and command taxonomy decision. |
| PU-005 | Revert preview identity and truncation changes. | Missing-source or stale-source fixture output. |
| PU-006 | Revert proof command wiring and runtime card emission. | Blocked_runtime probe artifact and schema validator output. |
| PU-007 | Revert shared-workspace closeout additions. | Agent-operable fixture and limitation report. |
| PU-008 | Do not merge; report blocker with validation and reviewer evidence. | Full validation ledger and live JSC-364 receipt. |

Global rollback rule: do not revert unrelated untracked research, spec, or review artifacts already present in the worktree. Limit rollback to files changed by the active implementation slice.

## Risk Register

| Risk | Severity | Evidence | Mitigation |
|---|---:|---|---|
| Repo doctor reports success while command recommendations are stale. | Critical | JSC-364 objective and FR-002 identify command-handle drift as the first blocker. | PU-001 makes command-handle drift an enforced doctor check with a next command. |
| Schema files exist but are not wired into runtime behavior. | High | Spec requires RuntimeCard and EvidenceReceipt to be emitted by reachable commands. | PU-002 adds validator fixtures; PU-006 validates emitted proof artifacts. |
| Conformance output overclaims live Codex parity from source modeling. | High | FR-003, FR-011, and FR-012 split modeled and live statuses. | PU-003 enforces status separation and evidence file fields. |
| Codex source context is stale or unavailable. | Medium | Existing preview tests already cover sibling Codex repo absence and git revision errors. | PU-005 reports source identity, unavailable reason, partial-depth status, and truncation state. |
| Runtime absence produces vague failures. | High | FR-016 and FR-024 require blocked_runtime probe evidence. | PU-006 requires probe command, exit code, artifact path, blocker class, and recovery plan. |
| Agents cannot use proof artifacts after the session ends. | High | FR-023, FR-027, FR-028, and FR-031 require shared-workspace evidence. | PU-007 adds visibility fields, repo-relative paths, limitations, and agent-operable fixture coverage. |
| Implementation expands into broad SDK architecture before P0 proof. | Medium | FR-021 explicitly keeps P1 schemas out of P0 blockers. | Keep the schema set limited and defer broad telemetry fields to later work. |
| Tracker state is mistaken for local implementation proof. | Medium | JSC-364 is live Todo; local validation and tracker truth are distinct. | PU-008 refreshes Linear separately and reports tracker state separately from validation. |

## Observability and Evidence

| Evidence Surface | Required Contents | Consumer |
|---|---|---|
| RuntimeCard | runtime target, status enum, runtime session, artifacts, evidence receipts, verifier results, workspace root, actor type, mutation scope, visibility status, limitations, recovery plan | repo doctor, closeout, reviewers, future agents |
| EvidenceReceipt | command, exit code, runtime target, evidence path, source identity, probe command, probe exit code, blocker class, suggested next action | proof command, blocked_runtime analysis, retry logic |
| ArtifactRecord | path, source identity, workspace root, actor type, mutation scope, visibility status, limitations | shared workspace handoff and artifact replay |
| RuntimeSessionSummary | proof run metadata, command list, evidence artifacts, status, blockers | closeout and review |
| RecoveryPlanSummary | blocker class, operator action, executable next commands, retry boundaries | runtime recovery and safe next command selection |
| Linear receipt | JSC-364 id, status, parent, labels, timestamp of refresh | tracker handoff and delivery truth |

## Visual References / Diagrams

| Flow Step | Input | Command / Component | Output | Trust Boundary |
|---|---|---|---|---|
| 1 | Command handles | skills handles check and repo doctor | Drift result and next command | Prevent stale command recommendations |
| 2 | Runtime schemas | validate_runtime_cards.py | Accepted or rejected evidence | Prevent prose-only proof |
| 3 | Codex source context | codex_preview service | Source identity and truncation status | Prevent modeled parity overclaim |
| 4 | Conformance suite | skills conformance codex-parity | modeled_conformance, live_runtime_parity, blocked_runtime | Separate fuzzy and deterministic states |
| 5 | Runtime proof | skills proof --runtime-target codex | RuntimeCard and EvidenceReceipt | Convert runtime truth into durable artifact |
| 6 | Shared workspace | proof artifacts and closeout | Agent-operable handoff | Preserve evidence beyond the session |

## Accessibility and Operator Ergonomics

The proof plane should be operable from plain terminal commands and should not require a human to read Python internals. Human output must name the runtime target, status, evidence artifact path, and next action. JSON output must remain complete enough for agents and validators to consume. Error cases should be specific but not noisy: blocked_runtime is useful only when it includes the probe command, blocker class, and recovery plan.

## Open Questions

| Question | Owner | Blocking? | Handling |
|---|---|---:|---|
| Should durable implementation evidence land in .harness/evidence or a more specific proof-plane subdirectory? | Implementer with maintainer review | No | Choose the smallest repo-owned path and report it in RuntimeCard. |
| Should CapabilityDiscovery be a new subcommand or folded into an existing skills status/capability surface? | Implementer with reviewer input | No | Preserve required fields and wrapper reachability either way. |
| Is live /Users/jamiecraik/dev/codex always expected in developer environments? | Jamie or repo maintainer | No | Treat absence as blocked_runtime or modeled_only with unavailable reason, not a hard implementation failure. |
| Should P1 schemas be created immediately after P0 lands? | Jamie or planner | No | Defer until P0 proof evidence exposes real telemetry needs. |

## Final Decision

Proceed with an execution-first P0 implementation of JSC-364 in the order defined by PU-001 through PU-008. The first patch should be PU-001 because it reduces false-success risk before the repo adds new proof-plane commands or schemas. This plan intentionally stops at explicit_stop after producing the plan artifact; implementation should begin only when the next stage is authorized.

## Appendix A. Harness Metadata / Traceability

| Field | Value |
|---|---|
| schema_version | 1 |
| interactive_status | explicit_stop |
| selection_evidence | User invoked he-plan for the JSC-364 runtime proof plane spec and supplied /Users/jamiecraik/dev/codex as source context. |
| route | he-plan |
| stage | he-plan |
| scope | Plan only; no code implementation, no commit, no Linear mutation. |
| source | .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md; JSC-364; /Users/jamiecraik/dev/codex read-only context |
| plan_path | .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md |
| traceability | JSC-364 mapped to FR, SA, VAL, and PU identifiers below. |
| validation | Plan artifact validators are listed in Appendix C after execution. |
| safe_to_continue | true for planning; implementation requires explicit next-stage authorization. |
| blocked_reason | none |
| linear_action_required | none |
| linear_mutation_status | already_linked |
| post_plan_handoff | explicit_stop |
| blackboard_delta | New durable he-plan artifact for JSC-364 runtime proof plane. |
| git_staging_status | not_staged |
| staged_paths | none |
| confidence | high |

## Linear Work Item Contract

| Field | Value |
|---|---|
| Linear issue | JSC-364 |
| Parent issue | JSC-351 |
| Title | [agent-skills] Add Codex Runtime Proof Plane |
| Status | Todo |
| Priority | High |
| Team | JSC |
| URL | https://linear.app/jscraik/issue/JSC-364/agent-skills-add-codex-runtime-proof-plane |
| Local plan | .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md |
| Source spec | .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
|---|---|---|---|---|
| JSC-364 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-012, SA-013, SA-014, SA-015, SA-016, SA-017, SA-018 | PU-001, PU-002, PU-003, PU-004, PU-005, PU-006, PU-007, PU-008 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-012, SA-013, SA-014, SA-015, SA-016, SA-017, SA-018 | Pending implementation PR |
| JSC-364 | SA-001, SA-002 | PU-001 | SA-001, SA-002 | Pending command-handle and repo doctor patch |
| JSC-364 | SA-005, SA-006, SA-016, SA-017 | PU-002, PU-006 | SA-005, SA-006, SA-016, SA-017 | Pending runtime card and evidence receipt patch |
| JSC-364 | SA-003, SA-004, SA-008, SA-014 | PU-003, PU-004 | SA-003, SA-004, SA-008, SA-014 | Pending conformance and capability discovery patch |
| JSC-364 | SA-009, SA-010, SA-015, SA-018 | PU-005, PU-007, PU-008 | SA-009, SA-010, SA-015, SA-018 | Pending preview, shared workspace, and closeout patch |

## Appendix B. Linear / Tracker Handoff

| Field | Value |
|---|---|
| linear_issue | JSC-364 |
| linear_status | Todo |
| linear_mutation_status | already_linked |
| linear_action_required | none for planning; implementation closeout should refresh issue state before delivery claims |
| tracker_handoff | Use this plan as the execution breakdown for JSC-364. Do not mutate project or cycle metadata without owner approval. |
| post_plan_handoff | explicit_stop |

## Appendix C. Review Outcomes

| Artifact / Review | Status | Evidence |
|---|---|---|
| Source spec review swarm | completed before this plan | artifacts/reviews/2026-05-24-runtime-proof-spec/ exists in the current worktree and the spec records no blocking gaps after review. |
| Plan identity lint | pass | python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md |
| Plan Linear traceability lint | pass | python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md |
| Plan BLUF lint | pass | python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md --json |
| Plan shape lint | pass | python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-plan.md --kind plan --json |
