---
schema_version: 1
artifact_id: 2026-05-24-agent-skills-codex-runtime-proof-plane
artifact_type: he-spec-standard
canonical_slug: agent-skills-codex-runtime-proof-plane
title: Agent Skills Codex Runtime Proof Plane Spec
harness_stage: he-spec
status: ready_for_plan
date: 2026-05-24
origin: "he-spec from evidence-led audit and Codex Skills SDK native integration analysis"
source_artifacts: "<REPO_ROOT>/.harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md; <CODEX_SOURCE_ROOT>/.harness/research/deep/2026-05-24-codex-skills-sdk-native-integration-analysis.md; <REPO_ROOT>/.harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md"
risk: high
depth: full
ui: false
traceability_required: true
linear_issue: JSC-364
linear_parent_issue: JSC-351
linear_status: Todo
linear_mutation_status: completed
linear_action_required: "JSC-364 was created as a child/follow-up under completed parent JSC-351 for the Runtime Proof Plane implementation slice."
blackboard_delta: "Promote the next Agent Skills slice from package/catalog parity to a Codex Runtime Proof Plane that can bind claims to live runtime evidence."
---

# Agent Skills Codex Runtime Proof Plane Spec

## Command Summary

BLUF: This spec defines the next Agent Skills implementation slice for Jamie and future agents: a Codex Runtime Proof Plane that turns package, conformance, and proof claims into live evidence-backed runtime records. The audit shows the current repo already has useful wrappers, package checks, and conformance fixtures, but it can still report success while command handles drift, Codex preview parity is partial, or live Codex runtime proof is blocked. The decision is to fix the immediate trust-boundary drift first, then add a typed runtime card and evidence receipt path so operators can see exactly which thread, turn, command, artifact, verifier, permission profile, and blocker made a claim true.

Decision Needed: Implement JSC-364 as the child/follow-up of completed JSC-351, using this spec as the source contract for the Runtime Proof Plane slice.

Top Risks: The current repo-doctor blocker can keep the control plane red; codex-parity conformance can pass while live parity remains partial; a runtime adapter can overreach into Codex internals before the repo has stable schemas and validator gates.

Next Action: Build the smallest P0 slice: repair generated command-handle drift, split modeled conformance from live parity status, define the runtime card and evidence receipt schemas, and add one runtime proof command that emits a durable proof artifact or an explicit blocked_runtime result.

## Purpose

The purpose of this spec is to convert the evidence-led audit and Codex Skills SDK integration analysis into a shippable implementation contract for Agent Skills.

It does not ask the repo to become a full Codex runtime clone. It asks the repo to stop treating package metadata, generated projections, and conformance fixtures as sufficient proof when the operator question is about live Codex behavior.

The selected slice is:

- Fix current trust-boundary blockers that already make repo doctor fail.
- Establish a typed Runtime Proof Plane for Codex-targeted skill claims.
- Preserve the existing ask wrappers, package checks, and conformance suite as the execution path.
- Add schemas and validators before adding broad orchestration.
- Leave rich workflow automation, subagent handoff, replay UX, and marketplace packaging for later phases.

## Problem Statement

Agent Skills is already a strong repository control plane for authoring, validating, discovering, and packaging skills. The audit found that it is not yet a reliable Codex runtime proof plane.

Current false-success and stale-state risks:

- Generated command-handle drift is live and blocks <code>repo doctor</code>, proving the repo can drift at the projected command boundary.
- The codex-parity conformance suite can pass while reporting limitations such as partial preview behavior, which makes a green result ambiguous.
- Codex runtime proof for at least one skill target is currently blocked because the Codex user runtime is not ready while the Agents runtime is ready.
- The public <code>./bin/ask</code> wrapper is core operator surface but is weaker than internal-module tests.
- Codex preview behavior is implemented before a named schema and stale-source/truncation policy are fully enforced.
- The Codex integration analysis says the next native step should be a runtime adapter plus evidence bridge, not another README refresh or catalog expansion.

The operator problem is that Jamie cannot safely delegate broader Codex autonomy to this repo until a claim like "this skill is Codex-ready" resolves to runtime evidence instead of a stack of plausible local checks.

## User / Operator Scenarios

### User Stories

As a Jamie-style operator, I want <code>./bin/ask repo doctor --json --robot</code> to fail on real command-handle drift, so that generated projections cannot silently diverge from canonical skill sources.

As a skill maintainer, I want Codex conformance results to distinguish model-contract validity from live-runtime parity, so that a passing fixture suite does not overstate Codex runtime readiness.

As a reviewing agent, I want a runtime card with thread, turn, command, artifact, verifier, and blocker evidence, so that I can audit a claim without trusting final-message prose.

As an implementation worker, I want blocked Codex runtime proof to emit a schema-backed <code>blocked_runtime</code> receipt, so that the failure is visible, retryable, and not confused with a skill defect.

As a future orchestration agent, I want ToolContract, HookContract, ArtifactRecord, and EvidenceReceipt entities to exist before workflow automation expands, so that orchestration can attach to durable contracts instead of prompt-only instructions.

## Goals

- FR-001: Provide a runtime proof plane that binds Codex-targeted skill readiness claims to durable, machine-readable evidence.
- FR-002: Repair the current generated command-handle drift that blocks repo doctor before expanding Codex autonomy.
- FR-003: Split modeled Codex contract conformance from live Codex parity in command outputs, JSON schemas, and acceptance criteria.
- FR-004: Define the P0 canonical schemas for RuntimeCard, EvidenceReceipt, ArtifactRecord, RuntimeSessionSummary, and RecoveryPlanSummary.
- FR-005: Add a reachable runtime proof command that emits either implemented_enforced proof or explicit blocked_runtime evidence.
- FR-006: Strengthen public <code>./bin/ask</code> wrapper contract tests for the Codex-facing commands.
- FR-007: Make Codex preview source identity, truncation, and partial-depth behavior explicit and validated.
- FR-008: Keep the first implementation small enough to validate locally without requiring broad workflow orchestration.
- FR-021: Define P1 extension schemas for ThreadRun, TurnEvent, SkillPackage, ToolContract, HookContract, and SteeringEvent without making them P0 blockers unless a P0 command emits those objects.
- FR-022: Provide a machine-readable capability discovery surface so agents can discover supported proof/conformance commands, runtime targets, readiness, blockers, and next actions before invocation.
- FR-023: Require shared-workspace observability fields so users and agents can verify that proof artifacts land in the same approved workspace roots.
- FR-024: Require blocked_runtime receipts to include a machine-verifiable runtime probe, not just narrative blocker text.
- FR-025: Require an agent-operable closeout path that proves discover, invoke, observe, and handoff steps through artifacts.

## Non-Goals

- This spec does not require a full Codex app-server implementation inside Agent Skills.
- This spec does not require automated Linear mutation until Jamie confirms the live issue mapping.
- This spec does not require a marketplace, skill registry publishing flow, or plugin installation UX.
- This spec does not require subagent handoff orchestration beyond recording runtime evidence fields needed by future orchestration.
- This spec does not require rewriting the large ask implementation modules before trust-boundary validators are green.
- This spec does not remove existing package, proof, and conformance commands; it tightens their claims and evidence output.

## Current State / Evidence

### Evidence Snapshot

| Evidence item | Source | Runtime status | Implication |
|---|---|---|---|
| Generated command-handle drift blocks repo doctor | 2026-05-24 evidence-led audit GAP-001 | implemented_enforced failure | Trust-boundary repair is P0 and must precede broader autonomy. |
| codex-parity conformance can pass with partial preview limitations | Audit GAP-002 | partial | A green conformance status is too coarse for live Codex readiness. |
| Codex runtime proof for testing skill is blocked | Audit runtime evidence | blocked_runtime | The repo needs explicit blocked receipts rather than narrative status. |
| Codex preview ABI schema is missing | Audit GAP-003 | partial | Preview output needs a named data contract and validator. |
| Public wrapper parity is weak | Audit GAP-004 | partial | Operator entrypoints need first-class fixtures. |
| No native Codex runtime adapter exists | Codex integration analysis Gap 1 | missing | The next layer should speak in runtime sessions, threads, turns, and receipts. |
| No canonical runtime card schema exists | Codex integration analysis Gap 2 | missing | Claims need a single durable packet operators can inspect. |
| Hooks, tools, artifacts, permissions, and memory are runtime entities in Codex | Codex integration analysis | inferred high confidence | Skill contracts should model those entities directly. |

### Existing Foundation

The repo already has useful foundation pieces:

- <code>./bin/ask</code> as the operator-facing command wrapper.
- Package, proof, and conformance subcommands under the ask surface.
- Existing wrapper contract fixture validation.
- Existing generated command-handle checks.
- Existing Codex preview and conformance modules.
- Existing HE artifact linting and traceability tooling.
- Existing JSC-351 spec line for Codex ABI conformance.

The gap is not absence of scaffolding. The gap is that proof claims are not yet routed through a single live-runtime evidence contract.

## Proposed Behavior

### User-Facing Solution

Operators should be able to run the repo's normal ask commands and receive evidence that separates three different truths:

- The package/model contract is valid.
- The generated projections are current and command handles are aligned.
- Live Codex runtime behavior has been proven or is explicitly blocked.

The new runtime proof plane introduces a durable runtime card emitted by proof and conformance paths. The card records the skill, package, command, runtime target, runtime session, thread or turn evidence when available, artifact records, verifier receipts, permission requirements, stop reason, and recovery classification.

The P0 behavior is intentionally narrow:

1. <code>repo doctor</code> and command-handle checks must be green before Codex runtime proof is considered valid.
2. <code>skills conformance run --suite codex-parity</code> must emit separate <code>model_contract_status</code> and <code>live_parity_status</code> fields.
3. <code>skills proof HANDLE --runtime-target codex</code> must emit a RuntimeCard artifact and EvidenceReceipt records, or fail with <code>blocked_runtime</code> plus a concrete blocker.
4. Codex preview outputs must be schema-validated and include source identity, truncation status, and partial-depth warnings.
5. <code>./bin/ask</code> must be tested as the public entrypoint for these paths, not only internal Python modules.

### Runtime Status Semantics

The implementation must use explicit runtime statuses instead of overloaded pass/fail wording:

| Status | Meaning | Allowed claim |
|---|---|---|
| implemented_enforced | Runtime path exists, validation is wired, and tests execute through the public command path. | Claim may be used for closeout. |
| implemented_not_enforced | Code exists but no reachable validation rejects drift. | Claim may be described as present, not proven. |
| scaffolded | Contract, placeholder, or fixture exists but no runtime path is implemented yet. | Claim may only be used as design readiness. |
| modeled_only | Static or fixture contract is valid, but no live runtime evidence was collected. | Claim cannot be called Codex-ready. |
| partial | Some expected behavior works, but limitations affect the claim. | Claim must name the limitation. |
| blocked_runtime | Runtime proof could not run because runtime, auth, server, permission, or environment is unavailable. | Claim must report blocker and recovery path. |
| stale_or_drifted | Source/projection/schema/handle evidence disagrees. | Claim must fail until repaired. |

The same status enum is canonical for RuntimeCard, conformance output, failure tables, and validators. Producers must not emit undeclared status tokens. If implementation needs a more specific cause, it must use <code>failure_class</code>, <code>blocker_class</code>, or <code>limitation_class</code> fields rather than inventing a new runtime status.

## Requirements

### Functional Requirements

- FR-009: The command-handle generator and checker MUST agree on every skill command handle written to generated agent or package surfaces.
- FR-010: <code>repo doctor</code> MUST surface command-handle drift as a blocking result with file-level evidence and remediation guidance.
- FR-011: Codex conformance output MUST include <code>model_contract_status</code>, <code>live_parity_status</code>, <code>limitations</code>, <code>runtime_cards</code>, and <code>evidence_receipts</code>.
- FR-012: A conformance run MUST NOT report an unqualified pass when <code>live_parity_status</code> is <code>partial</code>, <code>modeled_only</code>, <code>blocked_runtime</code>, or <code>stale_or_drifted</code>.
- FR-013: Codex preview output MUST be schema-validated and include source path, source hash or mtime, generated artifact path, command handle, token/depth budget, truncation status, and warnings.
- FR-014: Runtime proof MUST create a RuntimeCard artifact under a deterministic evidence directory.
- FR-015: Runtime proof MUST create one or more EvidenceReceipt entries for each verifier claim it makes.
- FR-016: Runtime proof MUST classify runtime failure as <code>blocked_runtime</code> with exact blocker text, attempted fallback, and next recovery command.
- FR-017: Runtime proof MUST execute through <code>./bin/ask</code> in at least one contract fixture.
- FR-018: The initial runtime adapter MUST be additive and must not mutate user Codex config, sessions, or plugin state.
- FR-019: The implementation MUST preserve existing package/proof/conformance commands and evolve their JSON contracts compatibly with schema_version increments.
- FR-020: Future HookContract and ToolContract fields MUST be accepted as optional extension objects so P1 work can attach without breaking P0 consumers.
- FR-026: Capability discovery output MUST list each Codex-facing command with runtime target support, readiness status, blocker class, evidence schema version, and next executable action.
- FR-027: RuntimeCard and ArtifactRecord outputs MUST include shared workspace identity fields: <code>workspace_root</code>, <code>actor_type</code>, <code>mutation_scope</code>, and <code>visibility_status</code>.
- FR-028: <code>visibility_status</code> MUST be <code>user_observable</code> for committed or closeout-eligible evidence; agent-only evidence is allowed only for intermediate local diagnostics and cannot satisfy acceptance for this lane.
- FR-029: Every blocked_runtime EvidenceReceipt MUST include <code>probe_command</code>, <code>probe_exit_code</code>, <code>probe_artifact_path</code>, and a typed <code>blocker_class</code>.
- FR-030: RecoveryPlanSummary MUST express <code>next_commands[]</code> as executable command descriptors with preconditions, permission profile, and expected outcome.
- FR-031: Closeout evidence MUST include an agent-operable path receipt proving discover -> invoke -> observe -> handoff for at least one Codex-facing command.

### Non-Functional Requirements

- NFR-001: Runtime proof output must be deterministic enough for CI fixtures when live Codex runtime is unavailable.
- NFR-002: Evidence files must be small, JSON-parseable, and reviewable in pull requests.
- NFR-003: Validators must fail before generated artifacts are accepted as current.
- NFR-004: Runtime unavailable must be classified as blocked, not silently skipped or treated as success.
- NFR-005: The P0 implementation must keep direct Codex runtime coupling behind an adapter boundary.
- NFR-006: The command output must remain useful to a human operator reading terminal JSON.

## Interfaces

### Command Interfaces

| Command | Required behavior |
|---|---|
| <code>./bin/ask skills handles --check --check-command-handles --no-handles --json --robot</code> | Blocks drift and returns exact skill/source/generated locations. |
| <code>./bin/ask repo doctor --json --robot</code> | Includes command-handle status and blocks stale generated projections. |
| <code>./bin/ask skills conformance run --suite codex-parity --evidence-dir PATH --json --robot</code> | Emits split model/live statuses and references runtime cards when produced. |
| <code>./bin/ask skills proof HANDLE --runtime-target codex --json --robot</code> | Emits a RuntimeCard path and EvidenceReceipt list or a blocked_runtime receipt. |
| <code>./bin/ask skills package HANDLE --json --robot</code> | Records package contract status and links to preview/schema evidence where relevant. |

### Runtime Adapter Interface

The runtime adapter boundary should expose these logical operations without assuming one Codex transport forever:

- discover_runtime_capabilities
- create_or_attach_runtime_session
- start_or_resume_thread_run
- capture_turn_event
- record_tool_or_hook_event
- write_artifact_record
- write_evidence_receipt
- classify_stop_reason
- classify_recovery_plan

For P0, live app-server access may be absent. In that case the adapter returns <code>blocked_runtime</code> or <code>modeled_only</code> depending on the command, and the evidence packet records why live proof was unavailable.

### JSON Consumer Behavior

Unknown fields are allowed for forward compatibility. Missing required fields in the current schema are blocking. Consumers must treat <code>model_contract_status</code> and <code>live_parity_status</code> independently.

## Data / Domain Contract

### RuntimeCard Required Fields

| Field | Type | Required | Notes |
|---|---:|---:|---|
| schema_version | integer | yes | Starts at 1. |
| card_id | string | yes | Stable artifact identifier. |
| created_at | ISO timestamp | yes | UTC or timezone-explicit. |
| runtime_target | enum | yes | codex, agents, local_model, fixture. |
| runtime_status | enum | yes | Must use the canonical runtime status enum: implemented_enforced, implemented_not_enforced, scaffolded, modeled_only, partial, blocked_runtime, stale_or_drifted. |
| skill_handle | string | yes | Canonical skill handle. |
| command_handle | string | conditional | Required when projected command surface exists. |
| package_id | string | conditional | Required when package/projection was evaluated. |
| runtime_session | object | yes | RuntimeSession summary or unavailable reason. |
| thread_runs | array | yes | ThreadRun summaries or empty with blocker. |
| turn_events | array | yes | TurnEvent summaries when live execution occurs. |
| artifacts | array | yes | ArtifactRecord objects. |
| evidence_receipts | array | yes | EvidenceReceipt objects. |
| verifier_results | array | yes | Test/check/verifier claims. |
| permission_profile | object | yes | Runtime needs and granted/blocked state. |
| workspace_root | string | yes | Shared workspace root observed by user and agent. |
| actor_type | enum | yes | user, agent, system. |
| mutation_scope | enum | yes | read_only, evidence_write, repo_write, tracker_mutation. |
| visibility_status | enum | yes | user_observable for closeout-eligible evidence; agent_only is allowed only for intermediate local diagnostics. |
| limitations | array | yes | Must be empty only when no limitation is known. |
| recovery_plan | object | yes | RecoveryPlan for non-success statuses. |

### EvidenceReceipt Required Fields

| Field | Required | Notes |
|---|---:|---|
| receipt_id | yes | Stable within evidence directory. |
| claim | yes | Human-readable claim being supported. |
| claim_status | yes | pass, fail, blocked, partial. |
| evidence_type | yes | test, command, runtime_event, artifact, schema_validation, ci, review_state. |
| command | conditional | Required for command evidence. |
| exit_code | conditional | Required for command evidence. |
| probe_command | conditional | Required for blocked_runtime evidence. |
| probe_exit_code | conditional | Required for blocked_runtime evidence. |
| probe_artifact_path | conditional | Required for blocked_runtime evidence. |
| blocker_class | conditional | Required for blocked_runtime evidence. |
| artifact_path | conditional | Required for artifact evidence. |
| source_paths | yes | Files or projections used. |
| verifier | yes | Validator or command name. |
| observed_at | yes | Timestamp. |
| blocker | conditional | Required for blocked or partial claims. |

### ArtifactRecord Required Fields

| Field | Required | Notes |
|---|---:|---|
| artifact_id | yes | Stable artifact identifier. |
| artifact_type | yes | runtime_card, preview, package, schema_report, trace, verifier_output. |
| path | yes | Repo-relative or evidence-dir path. |
| source_identity | yes | Source paths plus hash or mtime. |
| workspace_root | yes | Shared workspace root that contains or owns the artifact. |
| actor_type | yes | user, agent, or system writer. |
| mutation_scope | yes | Whether the artifact was read-only evidence, evidence write, repo write, or tracker mutation. |
| visibility_status | yes | user_observable is required for closeout-eligible evidence; agent_only may appear only on non-acceptance diagnostics. |
| generated_by | yes | Command or module. |
| validation_status | yes | pass, fail, blocked, partial. |
| consumer_contract | yes | Which command or reviewer consumes it. |

### CapabilityDiscovery Required Fields

| Field | Required | Notes |
|---|---:|---|
| schema_version | yes | Starts at 1. |
| command | yes | Public command string or structured command descriptor. |
| runtime_targets | yes | Supported targets and target-specific status. |
| readiness_status | yes | Uses the canonical runtime status enum. |
| blocker_class | conditional | Required when readiness is blocked_runtime, partial, stale_or_drifted, or scaffolded. |
| evidence_schema_version | yes | RuntimeCard/EvidenceReceipt schema versions expected by the command. |
| next_action | yes | Executable command descriptor or human approval action. |

### RecoveryPlanSummary Required Fields

| Field | Required | Notes |
|---|---:|---|
| recovery_status | yes | Uses the canonical runtime status enum where applicable. |
| reason | yes | Short human-readable explanation. |
| next_commands | yes | Array of executable command descriptors. Empty only when human approval is required. |
| preconditions | yes | Preconditions for each next command. |
| permission_profile | yes | Required permissions for the next command or approval. |
| expected_outcome | yes | What the command should prove or unblock. |
| freshness_expires_at | conditional | Required for tracker/runtime state evidence. |

### Conformance Rules

- Required fields missing from RuntimeCard, EvidenceReceipt, or ArtifactRecord are schema failures.
- Unknown fields are accepted but must not shadow required field names.
- Enum values must be documented in the schema and tests.
- RuntimeCard, conformance output, failure tables, and validators must use the same canonical runtime status enum: implemented_enforced, implemented_not_enforced, scaffolded, modeled_only, partial, blocked_runtime, stale_or_drifted.
- <code>live_parity_status</code> cannot default to pass.
- A fixture-only run may set <code>live_parity_status</code> to modeled_only, not pass.
- A partial run must include at least one limitation and one EvidenceReceipt explaining the partial condition.
- A blocked run must include a RecoveryPlan with next command or human action.
- A blocked_runtime run must include probe command, exit code, probe artifact path, and blocker class.
- A live Linear mapping acceptance claim must include a fresh tracker EvidenceReceipt whose <code>freshness_expires_at</code> has not passed.
- A repo-doctor failure accepted as pre-existing must include a before/after doctor delta artifact and ownership classification: introduced, pre-existing, dirty-worktree, or environment.
- agent_only visibility is not valid for acceptance or closeout evidence; any accepted RuntimeCard or ArtifactRecord must be user_observable.

## Enforcement Contract

This work must use the Skills SDK apparatus lens as an enforcement layer, not as prose guidance.

| Apparatus field | Enforcement rule |
|---|---|
| essential_decisions | Treat split model/live status, RuntimeCard schema, EvidenceReceipt schema, command-handle drift repair, and public wrapper fixtures as non-optional P0 decisions. |
| fillable_gaps | Allow adapter transport details, exact evidence directory naming, and future hook/tool extension fields to be filled during implementation if schemas and validators stay stable. |
| guardrails | Reject unqualified Codex-ready claims without live parity evidence or an explicit blocked_runtime receipt; reject generated projections when command handles drift. |
| refusal_triggers | Stop implementation if a command claims pass while runtime_status is partial or blocked, if source/projection identity disagrees, or if a validation command is unreachable through <code>./bin/ask</code>. |
| durable_memory | Record recurring drift, runtime blockers, and final validator outcomes in the repo's learned-fixes surface when the same failure repeats. |
| professional_output | Emit compact JSON and Markdown evidence that a reviewer can inspect without reconstructing hidden agent reasoning. |

Additional enforcement:

- Schema validators must run in CI or the repo's aggregate validation path before the runtime proof plane is considered implemented_enforced.
- The first patch must repair current command-handle drift or explicitly split the repair into an earlier blocking patch.
- No command may downgrade blocked runtime proof to a warning when the user asked for Codex runtime readiness.

## Security, Privacy, and Safety

- Runtime cards must not include secrets, raw auth tokens, private prompt bodies, or unredacted environment dumps.
- Permission profiles may record permission class, source, and grant/deny state, but must not record sensitive credential values.
- Runtime adapter code must avoid mutating Codex config, sessions, plugin state, or workspace automation state in P0.
- Evidence directories must be suitable for repository review or must clearly mark non-committable local evidence.
- Destructive actions are out of scope for runtime proof and must remain behind existing approval boundaries.
- Hook and tool event capture must avoid logging full user messages unless an explicit evidence policy permits it.

## Failure and Recovery

| Failure | Severity | Required classification | Recovery |
|---|---|---|---|
| Generated command-handle drift | Critical | stale_or_drifted | Regenerate or repair projected handles, then rerun handles check and repo doctor. |
| Codex app-server unavailable | High | blocked_runtime | Emit blocked RuntimeCard with exact runtime discovery probe command, exit code, artifact path, blocker class, and next recovery command. |
| Codex preview truncates or omits source | High | partial or stale_or_drifted | Include truncation/source warning and fail live parity if the missing portion affects readiness. |
| Conformance fixture passes but live parity unavailable | High | modeled_only | Mark model_contract_status pass and live_parity_status modeled_only. |
| Public wrapper fixture missing | Medium | implemented_not_enforced | Add <code>./bin/ask</code> fixture before claiming enforced behavior. |
| Schema validator absent | High | scaffolded | Add JSON Schema or typed parser before runtime card output is accepted. |
| Evidence artifact missing after command success | High | fail | Treat command as failed and include artifact-missing receipt. |
| Adapter emits unknown stop reason | Medium | partial | Preserve raw reason, classify as unknown_stop_reason, and require follow-up taxonomy update. |

## Validation Plan

### P0 Validation Commands

| Validation ID | Command | Expected outcome |
|---|---|---|
| VAL-001 | <code>./bin/ask skills handles --check --check-command-handles --no-handles --json --robot</code> | pass; no COMMAND_HANDLE_MISSING or COMMAND_HANDLE_DRIFT results. |
| VAL-002 | <code>./bin/ask repo doctor --json --robot</code> | command_handles is non-blocking; any unrelated failure is accompanied by a before/after doctor delta artifact and ownership classification. |
| VAL-003 | <code>./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance-audit --json --robot</code> | emits model_contract_status and live_parity_status; cannot show unqualified pass when live parity is partial, modeled_only, or blocked. |
| VAL-004 | <code>python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation --repo-root .</code> | pass; includes public wrapper fixtures for Codex-facing commands. |
| VAL-005 | <code>python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q</code> | pass; covers preview schema, source identity, and truncation warnings. |
| VAL-006 | <code>./bin/ask skills proof testing --runtime-target codex --json --robot</code> | emits RuntimeCard and EvidenceReceipt artifacts or blocked_runtime evidence with recovery plan. |
| VAL-007 | <code>python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py --evidence-dir /tmp/ask-runtime-proof --json</code> | pass after validator exists; validates RuntimeCard and EvidenceReceipt schemas. |
| VAL-012 | <code>./bin/ask skills capabilities --runtime-target codex --json --robot</code> | emits CapabilityDiscovery records for proof and conformance commands, including readiness status and next actions. |
| VAL-013 | <code>python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py --require-shared-workspace --evidence-dir /tmp/ask-runtime-proof --json</code> | pass; RuntimeCard and ArtifactRecord include user-observable workspace identity fields. |
| VAL-014 | <code>./bin/ask repo doctor --json --robot --baseline-artifact /tmp/ask-doctor-before.json --delta-artifact /tmp/ask-doctor-delta.json</code> | pass or emits classified delta proving non-command-handle failures are pre-existing, dirty-worktree, or environment. |
| VAL-015 | Linear MCP <code>get_issue</code> / <code>save_issue</code> receipt for JSC-351 and JSC-364 | pass; records live parent status and chosen child/follow-up mapping with freshness timestamp. |

### Artifact Validation Commands

| Validation ID | Command | Expected outcome |
|---|---|---|
| VAL-008 | <code>python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md</code> | pass. |
| VAL-009 | <code>python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md</code> | pass for local JSC-351 traceability; live Linear mutation still confirmation_required. |
| VAL-010 | <code>python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md --json</code> | pass. |
| VAL-011 | <code>python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md --kind spec --json</code> | pass. |

## Acceptance Criteria

- SA-001: The current generated command-handle drift is repaired or explicitly isolated as a prerequisite patch, and VAL-001 passes.
- SA-002: <code>repo doctor</code> no longer fails on command_handles for the current checkout after command-handle repair.
- SA-003: Codex conformance output includes separate <code>model_contract_status</code> and <code>live_parity_status</code> fields.
- SA-004: A partial, modeled-only, or blocked Codex parity run cannot produce an unqualified top-level pass.
- SA-005: RuntimeCard schema exists, is documented, and is validated by a reachable command.
- SA-006: EvidenceReceipt schema exists, is documented, and is emitted for every proof/conformance claim.
- SA-007: <code>skills proof HANDLE --runtime-target codex</code> emits a RuntimeCard path or a blocked_runtime receipt with recovery plan.
- SA-008: Public wrapper fixtures execute through <code>./bin/ask</code> for Codex proof and conformance surfaces.
- SA-009: Codex preview output includes validated source identity, generated artifact identity, truncation state, and limitation warnings.
- SA-010: ArtifactRecord entries link runtime cards, previews, schema reports, and verifier outputs to their source identities.
- SA-011: P0 implementation does not mutate Codex config, session, plugin, or automation state.
- SA-012: The artifact validators VAL-008 through VAL-011 pass for this spec.
- SA-013: Live Linear mapping is confirmed before any tracker mutation is claimed.
- SA-014: CapabilityDiscovery output lets an agent discover Codex proof/conformance support, blockers, and next executable action without reading prose docs.
- SA-015: RuntimeCard and ArtifactRecord evidence is user_observable in the shared workspace and includes workspace_root, actor_type, and mutation_scope.
- SA-016: blocked_runtime receipts are rejected unless they include machine-verifiable probe command, exit code, probe artifact path, and blocker_class.
- SA-017: RecoveryPlanSummary next_commands are executable descriptors with preconditions, permission profile, and expected outcome.
- SA-018: At least one acceptance fixture proves an agent-operable discover -> invoke -> observe -> handoff path without hidden manual-only steps.

## Visual References / Diagrams

| Flow step | Input | Contract entity | Output | Blocking condition |
|---|---|---|---|---|
| Canonical skill source | Skill files and package metadata | SkillPackage | Package/projection status | Source/projection drift |
| Public command | <code>./bin/ask</code> invocation | ToolContract command surface | Command evidence | Wrapper fixture missing |
| Runtime adapter | Codex runtime capability discovery | RuntimeSession | Session status | Codex unavailable or unauthorized |
| Proof execution | Skill handle plus runtime target | ThreadRun and TurnEvent | Runtime evidence | Runtime blocked or partial |
| Artifact capture | Preview, logs, schema reports | ArtifactRecord | Evidence directory | Artifact missing or stale |
| Verification | Tests, validators, conformance | EvidenceReceipt | RuntimeCard | Claim unsupported |
| Operator decision | RuntimeCard | RecoveryPlan or pass receipt | Closeout-ready proof | Ambiguous status |

## Linear Work Item Contract

This spec now maps to JSC-364, created as a child/follow-up of completed parent JSC-351. JSC-351 remains the completed Codex ABI conformance lineage; JSC-364 owns the next Runtime Proof Plane implementation slice.

Live-tracker decision:

- Option A: Replace/deepen JSC-351 with this runtime-proof-plane scope.
- Option B: Keep JSC-351 focused on completed ABI conformance and create a child or follow-up issue for Runtime Proof Plane. Selected: JSC-364.
- Option C: Split P0 command-handle repair into a separate issue, then attach Runtime Proof Plane as a follow-up.

SA-013 is complete only when a fresh live Linear EvidenceReceipt records the chosen option, the target issue identifier, parent/child or related-link relationship, status, labels, priority, and freshness timestamp. Local HE traceability lint is not sufficient for SA-013.

Live Linear mutation receipt:

| Field | Value |
|---|---|
| Parent issue | JSC-351 |
| Parent status at mutation | Done |
| Child/follow-up issue | JSC-364 |
| Child status at mutation | Todo |
| Child priority | High |
| Child labels | agent-skills, Governance, Agent-Native, Reliability, Developer Experience, Roadmap: Now, Feature |
| Child URL | https://linear.app/jscraik/issue/JSC-364/agent-skills-add-codex-runtime-proof-plane |
| Mutation time | 2026-05-24T18:04:00.581Z |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs |
|---|---|
| JSC-364 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011, SA-012, SA-013, SA-014, SA-015, SA-016, SA-017, SA-018 |
| JSC-351 | Parent lineage only; completed ABI conformance line. |

## Evidence and References

Path placeholders: <REPO_ROOT> means this repository checkout. <CODEX_SOURCE_ROOT> means the read-only sibling Codex source checkout used as evidence context.

| Source | Evidence used |
|---|---|
| <REPO_ROOT>/.harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md | Current repo maturity, gap register, runtime command evidence, and fix roadmap. |
| <CODEX_SOURCE_ROOT>/.harness/research/deep/2026-05-24-codex-skills-sdk-native-integration-analysis.md | Codex runtime primitives, proof-plane architecture, adapter roadmap, and native integration gaps. |
| <REPO_ROOT>/.harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md | Existing JSC-351 local spec lineage and Codex ABI conformance context. |

## Implementation Notes

Recommended first patch order:

1. Repair generated command-handle drift and add a regression around the exact failure class.
2. Add schema files for RuntimeCard, EvidenceReceipt, and ArtifactRecord with fixture examples.
3. Add the canonical runtime status enum and compatibility tests that reject undeclared statuses.
4. Update codex-parity conformance output to split modeled and live statuses.
5. Add capability discovery output for Codex proof and conformance paths.
6. Add public wrapper fixtures for the Codex conformance/proof paths.
7. Add runtime proof command output that writes a card even when live runtime is blocked, including probe evidence for blocked_runtime.
8. Extend Codex preview tests to cover source identity and truncation warnings.
9. Add the agent-operable discover -> invoke -> observe -> handoff fixture.

Suggested software and methods:

- JSON Schema or typed Python dataclasses for RuntimeCard, EvidenceReceipt, and ArtifactRecord.
- Existing ask CLI robot JSON format for command output compatibility.
- Existing wrapper fixture validator for public entrypoint coverage.
- Existing codex-preview tests for ABI/schema hardening.
- Repo doctor as the operator-facing aggregate trust gate.
- Evidence directories under /tmp for local non-committable runtime proof only when each RuntimeCard also records retention policy, source identity, freshness timestamp, and copy-forward instructions for PR evidence. Closeout-eligible evidence must be user_observable in a shared workspace or explicitly attached to the tracker/PR.

## Open Questions

- Should live Codex runtime proof require Codex app-server v2, or should the first implementation use an adapter that supports local fixture mode and app-server mode?
- Should RuntimeCard artifacts live under <code>.harness/evidence/</code>, a command-specified <code>--evidence-dir</code>, or both?
- Should JSC-351 own the entire runtime proof plane, or should JSC-351 stay ABI-focused while a child issue owns RuntimeCard and EvidenceReceipt implementation?
- Which runtime-card fields are safe to commit by default, and which should remain local-only unless redacted?
- Should repeated blocked_runtime receipts automatically create learned-fix entries, or only after Jamie steering confirms recurrence?

## Decision

Decision: use JSC-364 as the live implementation issue for this spec, with JSC-351 preserved as completed parent lineage.

Decision rationale:

- The audit shows existing implemented checks but exposes live trust-boundary gaps.
- The Codex analysis shows the product direction is runtime-shaped and evidence-shaped, not catalog-shaped.
- A runtime proof plane is a small enough abstraction to start with schemas, validators, and command output before building orchestration.
- Fixing command-handle drift first prevents new runtime claims from sitting on top of a known red control plane.

## Appendix A: Gap to Requirement Mapping

| Audit / analysis gap | Requirement IDs | Acceptance IDs |
|---|---|---|
| GAP-001 generated command-handle drift | FR-002, FR-009, FR-010 | SA-001, SA-002 |
| GAP-002 conformance pass with partial preview limitations | FR-003, FR-011, FR-012 | SA-003, SA-004 |
| GAP-003 Codex preview schema missing | FR-007, FR-013 | SA-009 |
| GAP-004 public wrapper parity weak | FR-006, FR-017 | SA-008 |
| GAP-005 Codex runtime target optional/failing | FR-005, FR-014, FR-016 | SA-007 |
| Codex analysis Gap 1 native runtime adapter missing | FR-004, FR-018 | SA-005, SA-011 |
| Codex analysis Gap 2 runtime card schema missing | FR-004, FR-014 | SA-005 |
| Codex analysis Gap 6 artifact model file-centric | FR-004, FR-015 | SA-010 |
| Codex analysis Gap 7 verifier truth fragmented | FR-005, FR-015 | SA-006 |

## Appendix B: Phasing

### Phase 1 - Critical Trust Boundary Fixes

Objective: remove false-success and stale-state risk from the current command surface.

Included fixes: command-handle repair, repo doctor green path, split model/live status.

Validation gates: VAL-001, VAL-002, VAL-003.

### Phase 2 - Mechanical Enforcement

Objective: make the runtime proof plane schema-backed and validator-backed.

Included fixes: RuntimeCard schema, EvidenceReceipt schema, ArtifactRecord schema, wrapper fixtures.

Validation gates: VAL-004, VAL-007.

### Phase 3 - Runtime Harness Maturity

Objective: collect or block live Codex runtime evidence deterministically.

Included fixes: runtime adapter, blocked_runtime receipts, recovery plan taxonomy.

Validation gates: VAL-006, plus schema validation.

### Phase 4 - Context and Skill Compression

Objective: use runtime cards to control hot/cold context and future skill routing.

Included fixes: optional ToolContract and HookContract extension fields, source identity policy, limitation reporting.

Validation gates: preview schema tests and conformance contract tests.

### Phase 5 - Governance and Scaling

Objective: use the proof plane as the substrate for broader Codex autonomy.

Included fixes: review-state packet integration, learned-fix recurrence handling, future workflow orchestration, tracker mapping.

Validation gates: repo closeout, review-state validators, live tracker verification once authorized.

## Appendix C: Validation Status for This Spec

This section records artifact validation and review evidence run during spec generation.

| Command | Status | Notes |
|---|---|---|
| <code>python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md</code> | pass | HE identity metadata and filename contract passed. |
| <code>python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md</code> | pass | Local JSC-364 traceability table passed; JSC-364 is linked to parent JSC-351. |
| <code>python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md --json</code> | pass | Command Summary BLUF contract passed. |
| <code>python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-24-agent-skills-codex-runtime-proof-plane-spec.md --kind spec --json</code> | pass | Standard HE spec artifact shape passed. |
| <code>Linear MCP save_issue</code> | pass | Created JSC-364 as a child/follow-up under completed parent JSC-351. |
