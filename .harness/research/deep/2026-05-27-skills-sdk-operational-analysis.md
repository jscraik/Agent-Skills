# Skills SDK Operational Analysis

Date: 2026-05-27

Target repository: /Users/jamiecraik/dev/agent-skills

Output purpose: determine how Agent Skills Kit / Skills SDK behaves as an operational runtime layer today, where it still behaves like a collection of prompts, and what should become deterministic runtime infrastructure so it aligns more naturally with Codex.

Review stance: this is not a skill catalogue, prompt-style review, or changelog. It treats skills, manifests, schemas, validators, ASK commands, generated projections, runtime evidence, and prior steering uptake as one operating system.

Primary evidence:

- AGENTS.md, CODESTYLE.md, ARCHITECTURE.md, README.md, UBIQUITOUS_LANGUAGE.md.
- Docs/agents/04-validation.md, Docs/agents/14-path-ownership-boundaries.md, Docs/agents/19-high-signal-steering-feedback.md.
- Infrastructure/config/skills-sdk.json.
- Infrastructure/config/schemas/runtime-card.v1.schema.json, evidence-receipt.v1.schema.json, artifact-record.v1.schema.json, recovery-plan-summary.v1.schema.json, runtime-session-summary.v1.schema.json, skill-doctor.v1.schema.json, skill-package.v1.schema.json, skill-package-readiness.v1.schema.json, skills-sdk.project.v1.schema.json.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py.
- Infrastructure/scripts/lib/ask/skills_sdk/contracts.py, runtime_adapters.py, package_contracts.py, conformance.py, package_verify.py.
- Infrastructure/scripts/lifecycle-and-sync/route_skillset.py, command_surface.py, selection_policy.py.
- Infrastructure/scripts/validation-and-linting and Infrastructure/tests.
- Selected skills: skill-factory root router, skill-factory-router, goal-governor, code-fixes-triage, verification-before-completion.
- Live ASK samples: repo status, skills help, skills doctor skill-factory-router, skills package skill-factory-router, skills proof skill-factory-router --runtime-target codex, skills events, skills handles --check --check-command-handles.
- Existing local research: .harness/research/audits/2026-05-26-skills-sdk-code-tree-gap-audit.md.
- Recent git history from 2026-05-20 through 2026-05-26.
- Memory registry context around runtime proof plane, steering uptake, projection hardening, code-fixes triage, and goal-governor hardening.

Important scope note:

- The repo is currently dirty with many pre-existing edits and artifacts. This analysis does not classify those edits as mine and does not repair them.
- Live command samples intentionally exposed current runtime/projection drift. That drift is evidence for the analysis, not a requested fix lane.
- The Codex repo instruction front door instructions/CODESTYLE.md was absent in /Users/jamiecraik/dev/codex for this session; target repo AGENTS.md and CODESTYLE.md were read before writing this artifact.

## Executive Summary

Skills SDK is no longer just a skills repository. It has become a partially executable operating layer for agent work. The strongest signal is the explicit three-plane architecture in ARCHITECTURE.md:

- Ground state: canonical sources, policy, docs, specs, plans, and tests.
- Derived state: .agents, .skillsets, generated catalog/index content, plugin mirrors, and validation artifacts.
- Runtime truth: observed behavior from ASK, Codex skill loading, validation commands, PR checks, review threads, Linear state, and receipts.

That is the right foundation. It mirrors modern Codex operational patterns: runtime state outranks conversational state, generated projections are not source, and completion claims require evidence. The repo also has serious executable machinery: ASK robot JSON, trace IDs, skill doctor, skill package readiness, proof commands, runtime-card schemas, evidence receipts, projection checks, command handles, operation profiles, event vocabulary, steering-uptake validators, package and install security tests, eval lanes, and local review dashboards.

The weakness is not lack of ambition or lack of docs. The weakness is that the executable spine is still too wide, too internally named, and too partially wired. A new agent can see many plausible commands but no single public SDK authority for "initialize this repo", "diagnose this project", "what does this pass prove", "what should I do next", and "what runtime truth changed". The existing May 26 audit captured this well: there is no ./bin/ask skills sdk namespace, skills-sdk.json is a planning contract while also pointing at active interfaces, and lifecycle events exist as vocabulary more than as a mandatory per-run event stream.

The highest-leverage improvement is a small public SDK spine backed by existing internals:

- ./bin/ask skills sdk init
- ./bin/ask skills sdk doctor
- ./bin/ask skills sdk status
- ./bin/ask skills sdk eval
- ./bin/ask skills sdk sync

Those should not duplicate current logic. They should be thin facades over manifest, doctor, package, proof, eval, event, and projection checks, with one consistent agent_contract envelope: source authority, editable paths, generated paths, forbidden actions, what this proves, what this does not prove, freshness, next safe command, and blocker taxonomy.

The biggest stale-state risk is projection and runtime drift. Live evidence from this review showed:

- ./bin/ask repo status --json --robot passed and reported skills_synced: true.
- ./bin/ask skills handles --check --check-command-handles --json --robot returned error with command surface projection drift and command handle drift for skill-builder, skill-factory-router, skill-refactor, and skillify.
- ./bin/ask skills doctor skill-factory-router --json --robot returned blocked_runtime because generated_command_handle_check failed.
- ./bin/ask skills proof skill-factory-router --runtime-target codex --json --robot returned a runtime failure with recovery guidance to preview rooted sync before user/workspace runtime sync.

That is useful, not embarrassing. It proves the repo is building runtime truth systems that can catch drift. The missing next step is making those facts converge into a smaller, canonical, user-facing operational state so "repo status says synced" and "handles check says drift" cannot be interpreted as one green state by an agent trying to close out work.

The biggest orchestration problem is layered routing noise. There are root routers, generated command handles, .skillsets manifests, plugin routers, folded compatibility aliases, hidden bridge skills, skill-system bridge skills, package-owned skills, cache mirrors, and Codex session skills. That is powerful, but it creates ambiguity unless routing decisions are logged, replayable, and tied to selection policy identity. Today, route_skillset.py can return low confidence or be blocked by command policy, while the agent still needs a deterministic fallback. Routing should become an auditable selection event, not just a local helper invocation.

The best golden nugget is already present in the repo: repeated steering is treated as telemetry. Docs/agents/19-high-signal-steering-feedback.md is unusually strong. It says repeated Jamie corrections are operating evidence, not conversation, and must become validators, schema checks, trace events, runtime checks, workflow gates, skill-routing changes, retrieval improvements, recovery handlers, CI gates, or artifacts. That doctrine should move from repo behavior into the SDK product contract.

The final diagnosis:

- Skills SDK is operationally ahead of most skill repositories.
- It already contains the raw material for a Codex-native skills runtime.
- Its next phase should not be more prompts, more routers, or a larger catalogue.
- Its next phase should be contract convergence: one SDK spine, one runtime evidence packet, one durable event stream, one routing trace, one proof envelope, and one stale-state model.

## Skills Architecture Findings

### Finding 1: The Three-Plane Model Is The Core Architecture

WHAT: The repo clearly separates ground state, derived state, and runtime truth.

WHY: This is the architectural invariant that lets skills become operational systems instead of editable prompts. It prevents generated .agents or .skillsets output from masquerading as source and prevents docs from outranking executable evidence.

Operational implication: every SDK workflow needs to declare which plane it reads, which plane it writes, and which plane proves completion.

Risk/tradeoff: if the planes remain mostly documented instead of enforced in all command payloads, agents will still hand-edit projections, cite old docs as proof, or treat repo status as runtime parity.

Recommended implementation: add a plane_contract object to SDK command payloads:

- source_plane: canonical_source, plugin_source, owner_project_source.
- generated_plane: runtime_projection, command_surface, plugin_cache.
- runtime_truth_plane: command_result, runtime_card, event_stream, external_state_snapshot.
- writes_allowed: list of path classes.
- writes_forbidden: list of path classes.
- proof_required: list of evidence classes.

Priority: P0.

Validation: schema tests for sdk doctor, skills doctor, package, prove, sync, and external-review payloads must assert the plane_contract exists and is consistent with command mode.

### Finding 2: ASK Is Already The Runtime Kernel, But The Public SDK Spine Is Missing

WHAT: ./bin/ask exposes the control plane: repo status, skills list, handles, resolve, proof, prove, explain, doctor, package, conformance, profiles, events, memory, route, goal, improve, sync, audit, external-review, install, fold, and init.

WHY: This is the executable substrate that can make skills deterministic. It already emits JSON, trace_id, metadata.command, data, telemetry.latency_ms, and errors.

Operational implication: Skills SDK can become a Codex-native operational layer by narrowing this into a small public facade rather than asking agents to learn the whole command surface.

Risk/tradeoff: a wide CLI creates "choose your own adventure" behavior. Agents may run package when doctor is needed, audit when proof is needed, or treat one successful command as global readiness.

Recommended implementation: create a skills sdk namespace as a stable facade:

- sdk init: declare project roots, evidence path, eval path, trust policy, precedence policy.
- sdk doctor: aggregate repo status, project manifest, source/projection ownership, command handle drift, runtime proof, package readiness, event stream health, and next safe command.
- sdk status: current SDK state only, no broad validation.
- sdk eval: facade over eval/prove/package/conformance for one handle.
- sdk sync: projection sync with dry-run default and ownership proof.

Priority: P0.

Validation: ./bin/ask skills sdk --help must exist; sdk doctor must emit a schema-valid payload with agent_contract, plane_contract, freshness, next_command, and what_this_does_not_prove.

### Finding 3: Runtime Cards And Evidence Receipts Exist, But Need Codex Identity

WHAT: runtime-card.v1, evidence-receipt.v1, artifact-record.v1, runtime-session-summary.v1, and recovery-plan-summary.v1 are already present.

WHY: These are the right objects for runtime truth. They can turn skill use into inspectable evidence instead of transcript-only claims.

Operational implication: the SDK can emit a durable proof object for a skill run, blocked runtime check, artifact output, or verifier result.

Risk/tradeoff: v1 is permissive in key areas. thread_runs, turn_events, verifier_results, limitations, and permission_profile allow arbitrary objects. That is flexible, but it postpones the hard part: joining proof to Codex thread_id, turn_id, trace_id, tool_call_id, hook_event_id, plugin_id, environment_id, permission profile, and rollout path.

Recommended implementation: keep v1 for compatibility, but define runtime-card.v2 as a Codex-aligned profile:

- codex_thread_id
- codex_turn_id
- codex_trace_id
- codex_tool_call_ids
- hook_event_ids
- plugin_id
- environment_id
- permission_profile_id
- rollout_path or session_path
- generation_token
- freshness_observed_at
- stale_after
- claim_authority
- replay_pointer

Priority: P0 for design, P1 for implementation.

Validation: fixture tests should reject runtime cards that claim Codex target status without at least one Codex identity or explicit blocked_runtime reason.

### Finding 4: Doctor Is The Strongest Current Operational Primitive

WHAT: skills doctor aggregates resolution, runtime reachability, canonical source, projection ownership, structural audit, capability metadata, package readiness, outcome proof, lifecycle event, taxonomy, operation profiles, and next command.

WHY: It is the closest thing to a deterministic "what can I safely claim?" engine.

Operational implication: doctor should become the model for every SDK workflow: classify target, run bounded checks, emit schema-backed status, name blockers/warnings, and give the next safe command.

Risk/tradeoff: doctor currently lives as one command among many. Its output is powerful but too rich for quick operator routing unless summarized by an SDK facade.

Recommended implementation: sdk doctor should call skill doctor for handles, repo/project doctor for workspace health, and package/proof/event checks for runtime evidence, then reduce the result into one readiness state:

- usable
- usable_with_warnings
- blocked_source
- blocked_projection
- blocked_runtime
- blocked_validation
- blocked_auth
- blocked_environment
- stale_evidence

Priority: P0.

Validation: tests should cover contradictory states such as repo status skills_synced true while command handle check fails.

### Finding 5: Routing Is Useful, But It Is Not Yet A Replayable Decision

WHAT: route_skillset.py scores manifest rows by token/phrase overlap, returns top candidates, and treats low confidence below 0.18 as a clarify-before-loading state. Command handles and selection policy also define visibility, aliases, folded compatibility, default flat surface, plugin collision policy, and hidden bridge skills.

WHY: This keeps context small and preserves progressive disclosure.

Operational implication: routing is the execution front door for many tasks. When it is wrong, the whole workflow starts in the wrong mental model.

Risk/tradeoff: token overlap is transparent but shallow. It can produce low-confidence results for architecture/audit tasks that still clearly belong to a root skill. It can also be blocked by command policy, as happened during this review when the Python router invocation was rejected.

Recommended implementation: introduce route_decision.v1 as a replayable artifact:

- input_hash
- selected_skill_set
- candidates
- scores
- policy_identity
- route_mode: exact, phrase, token, manual, fallback
- confidence
- abstain_reason
- loaded_source_path
- fallback_used
- validation_command

Priority: P1.

Validation: deterministic route fixtures for ambiguous requests, exact skill mentions, root-router requests, and command-policy-blocked fallback.

### Finding 6: Command Handles Are A Native Abstraction, But Drift Is The Main Runtime Risk

WHAT: command_surface.py builds command-visible skill handles with command_visibility, runtime_visibility, source_path, command_handle_path, owner, invoke_via, level, aliases, deprecation state, and provenance. Live handles check reports 111 handles, 105 generated handles, and current drift in generated command handle YAML for four skill-factory handles.

WHY: Command handles are how skills feel native to Codex: small, mentionable, discoverable, and routeable.

Operational implication: handle health is runtime truth. A skill source being correct does not matter if its handle projection is stale or unreachable.

Risk/tradeoff: command handles create another generated plane. Without strong stale-state semantics, agents can claim "skills synced" from repo status while a deeper handle check reports drift.

Recommended implementation: define a single command_surface_state object consumed by repo status, sdk doctor, skills doctor, proof, and closeout:

- projection_status
- generated_handle_status
- handle_count
- drift_count
- drift_paths
- policy_identity
- source_revision
- last_checked_at
- next_repair_command

Priority: P0.

Validation: repo status should downgrade or qualify skills_synced when handle check fails, or expose separate fields so agents cannot collapse them.

### Finding 7: Skill Sprawl Is Managed, But Not Yet Continuously Scored

WHAT: the repo has 107 source SKILL.md files in primary source roots sampled by this review and 115 projected .agents skills. README reports 26 default catalog skills and 111 generated handles, with 77 first-party handles across 7 clusters.

WHY: The repo has intentionally moved from a flat skill bag to routers, latent modules, visibility modes, command handles, aliases, and root skill sets.

Operational implication: sprawl is acceptable only if selection, visibility, ownership, and overlap are continuously validated.

Risk/tradeoff: repeated overlapping words such as review, fix, validate, triage, improve, proof, doctor, runtime, and skill can create routing noise. Compatibility aliases keep old handles alive, but also increase ambiguity.

Recommended implementation: add a semantic routing-noise report:

- near-duplicate descriptions
- high-overlap trigger sets
- handles with same noun/verb pair
- root-router versus target ambiguity
- aliases used in recent sessions
- handles never selected
- skills with validation commands but no eval fixtures

Priority: P1.

Validation: report should be deterministic and reviewed as advisory first; P2 can enforce thresholds for newly added handles.

### Finding 8: Package Readiness Is Strong Internally, But Portability Is Partial

WHAT: skill-package.v1 validates Codex metadata compatibility. skill-package-readiness.v1 adds readiness, gates, lifecycle event, agent summary, and next command. package_contracts.py also defines SDK_PACKAGE_CONTRACT_FIELDS such as purpose, inputs, outputs, commands, permission_profile, portability_profile, evals, task_profile, and evidence_policy.

WHY: This is the bridge from local skill to shareable SDK package.

Operational implication: Skills SDK can tell whether a skill is merely loadable by Codex or genuinely ready for reuse across repos/runtimes.

Risk/tradeoff: current compatibility can pass narrower metadata while the richer SDK contract remains incomplete. The live package sample for skill-factory-router returned warning.

Recommended implementation: split readiness into explicit layers:

- codex_metadata_abi
- package_shape
- portability_contract
- permission_contract
- eval_contract
- evidence_contract
- runtime_contract
- governance_contract

Priority: P0.

Validation: package readiness output must expose layer-by-layer status and prohibit promotion claims when portability/evidence contracts are warning or blocked.

### Finding 9: Steering Uptake Is A Product Primitive, Not Just Repo Policy

WHAT: Docs/agents/19-high-signal-steering-feedback.md defines repeated steering as operating evidence and requires durable guardrails plus validation. It has a taxonomy of failure categories and durable improvement types, plus validate_steering_uptake.py.

WHY: This is the strongest steering-reduction system in the repo.

Operational implication: Skills SDK can generalize this into a product feature: convert repeated human corrections into validators, checks, routing rules, eval fixtures, runtime-card fields, or governance policies.

Risk/tradeoff: if uptake remains a repo-local ledger, external adopters will keep repeating the same corrections in every project.

Recommended implementation: make steering uptake an SDK event and artifact:

- steering_signal_detected
- failure_category
- improvement_type
- guardrail_path
- validation_command
- recurrence_count
- status
- evidence_receipt_id

Priority: P1.

Validation: sdk doctor should report open steering uptake items that touch changed skill/router/runtime surfaces.

### Finding 10: Skills Still Mix Operational Systems With Prompt-Only Instructions

WHAT: several skills now contain real scripts, contracts, evals, and validators. Others primarily contain workflow prose and a validation command. Some operationally sensitive skills tell agents to refresh live truth, write artifacts, or classify blockers, but the enforcement is not always in the skill package itself.

WHY: Prompt-only behavior is acceptable for judgement-heavy work, but not for source-of-truth claims, runtime readiness, projection repair, review convergence, or closeout.

Operational implication: the SDK needs a classification for skill behavior type:

- prompt_guidance
- artifact_writer
- validator_backed
- runtime_adapter
- external_state_reader
- orchestrator
- mutator
- reviewer
- governance_gate

Risk/tradeoff: over-mechanizing every skill would make the system brittle. But under-mechanizing operational skills keeps repeated steering alive.

Recommended implementation: add behavior_type and enforcement_level to package readiness:

- advisory_only
- schema_backed
- validator_backed
- artifact_backed
- runtime_backed
- external_state_backed

Priority: P1.

Validation: no skill with mutating, closeout, runtime, review, or governance claims should remain advisory_only.

## Workflow Findings

### Workflow Finding 1: The Golden Path Is Real But Too Wide

Workflow pattern: README suggests repo doctor, skills improve, explain, doctor, package, profiles, memory search, prove, repo closeout.

Runtime implications: this correctly separates repo health, selection, explanation, per-skill readiness, package metadata, runtime mode, durable memory, proof, and closeout.

Governance implications: it prevents "I read the skill" from becoming a readiness claim.

Stale-state implications: the path can still become stale because no single command remembers which earlier steps are fresh for the current head and runtime projection.

Replay/debugging implications: each command emits trace_id, but there is no shared workflow_run_id tying the golden path together.

Implementation advice: introduce sdk workflow run IDs. Every command in a golden path should accept --workflow-run-id or emit a resumable one. sdk doctor should summarize latest evidence by workflow_run_id and head/policy identity.

### Workflow Finding 2: Eval Lanes Are Carefully Separated, But Need Claim Boundaries Everywhere

Workflow pattern: README separates ask evals run, Plugin Eval, Tessl local review, Tessl live private lanes, and external-review. The Tessl staging policy is unusually strong: stable /tmp paths, no npx, no publish, no registry upload, archive prior temp contents.

Runtime implications: this prevents eval tools from becoming accidental mutation or publication lanes.

Governance implications: acceptance thresholds are explicit: Plugin Eval B+ or better with zero failures and Tessl score 95 or better.

Stale-state implications: eval artifacts can remain stable, but a previous eval does not prove current source unless tied to source hash and runtime profile.

Replay/debugging implications: staged inputs are inspectable, but the SDK still needs a portable eval_run manifest linking source hash, scenario files, command, stdout/stderr artifact, external tool version, and outcome.

Implementation advice: require eval_run.v1 for all eval lanes. Include what_this_proves and what_this_does_not_prove in robot payloads.

### Workflow Finding 3: Review/Closeout Skills Know The Right Doctrine, But Need Shared State

Workflow pattern: code-fixes-triage, verification-before-completion, goal-governor, pr-green-sweep-style flows all keep Slack, CodeRabbit, CI, GitHub, Linear, local validation, and merge readiness separate.

Runtime implications: this matches Codex-native operational truth: external notification surfaces are signals, not proof.

Governance implications: review convergence should not depend on remembering which skill said what; it needs a review-state packet.

Stale-state implications: old PR comments, old checks, old branch heads, stale Slack messages, and stale local test output are major failure modes.

Replay/debugging implications: without review_state.v1, reruns must reconstruct context from chat and tool logs.

Implementation advice: build review_state.v1 and merge_readiness_snapshot.v1 as SDK primitives. Skills should write or consume those packets rather than summarize review status conversationally.

### Workflow Finding 4: Runtime Proof Has The Right Artifact Set But Needs Event Continuity

Workflow pattern: skills proof can emit runtime-card, evidence-receipt, artifact-record, and probe artifacts under .harness/evidence/runtime-proof.

Runtime implications: proof is becoming artifact-backed.

Governance implications: blocked_runtime can be a first-class status instead of a failed task.

Stale-state implications: proof must expire. A pass against yesterday's projection is not a pass against today's command surface.

Replay/debugging implications: proof artifacts need source revision, projection policy identity, command surface hash, Codex session pointer, and event stream pointer.

Implementation advice: every proof run should append events.jsonl with proof_started, projection_checked, runtime_target_checked, artifact_written, proof_completed or proof_blocked.

### Workflow Finding 5: Project-Local Adoption Is Planned Better Than It Is Executed

Workflow pattern: skills-sdk.json defines project-local manifest, owner repo evidence path, create/install/update lifecycle, save policy, eval suite, and lifecycle events.

Runtime implications: the repo understands external adoption, but it lacks the public init/doctor path that would make it obvious.

Governance implications: without sdk init, agents may guess roots and edit .agents or .codex paths unsafely.

Stale-state implications: owner project skill roots can drift from runtime projections unless declared and checked.

Replay/debugging implications: project-local runs need owner-repo evidence directories and event streams.

Implementation advice: implement sdk init before deeper platform work. It should create skills-sdk.json or validate an existing one, never infer write authority from path conventions alone.

### Workflow Finding 6: Recovery Is Described Well But Not Unified

Workflow pattern: doctor, proof, goal-governor, Tessl, steering uptake, and code-fixes triage all have recovery guidance, but each names its own format.

Runtime implications: failures are classified, but recovery state is not shared.

Governance implications: one blocked lane can be mistakenly bypassed by another workflow if the recovery state is not reusable.

Stale-state implications: after a recovery command runs, previous blocked evidence must be superseded, not silently ignored.

Replay/debugging implications: recovery requires before/after evidence and supersession links.

Implementation advice: define recovery_case.v1:

- blocker_class
- failed_command
- failed_at
- recovery_command
- recovery_policy
- allowed_mutations
- supersedes_receipt_ids
- outcome
- next_command

## Codex-Native Alignment Findings

### Strong Alignment

- Runtime truth outranks docs. This matches Codex's movement toward typed events, runtime state, app-server APIs, goals, hooks, and rollouts.
- Generated projections are separate from source. This matches Codex skill/plugin loading where runtime handles are not the authoring source.
- Command handles are small, mentionable runtime affordances. This matches Codex's need for small picker and instruction surfaces.
- Robot JSON with trace_id is agent-native. Codex can consume this more safely than prose.
- Doctor/proof/package commands use blockers, warnings, next_command, and schema references. This is exactly the right shape for autonomous continuation.
- Runtime cards and evidence receipts are first-class enough to become Codex runtime truth surfaces.
- Steering uptake taxonomy turns repeated human correction into durable engineering work.
- Code-fixes-triage and verification-before-completion preserve live source-of-truth boundaries.

### Friction

- No skills sdk namespace. Codex agents need a narrow public path, not the full internal ASK command graph.
- Lifecycle events are mostly declared contracts, not guaranteed durable event streams.
- Route selection is not a durable runtime event.
- Runtime cards do not yet require Codex thread/turn/trace identity.
- Repo status can be green while deeper command handle checks are red unless the agent inspects the right surface.
- skill-factory routing can require a command path that may be blocked by policy; fallback is human/agent judgement instead of an SDK-level fallback contract.
- Some docs and config still mix planned surfaces with active surfaces.
- skills_impl.py remains a large orchestration module, even though extraction into ask.skills_sdk has started.

### Runtime Assumptions That Conflict

- Codex treats runtime capabilities as session-scoped and evented; Skills SDK still often treats skills as repo objects plus generated files.
- Codex permissions and environments are active runtime constraints; Skills SDK package metadata has runtime_needs but does not yet resolve them against active Codex permission profiles and environments.
- Codex steering can arrive mid-thread and needs queue semantics; Skills SDK mostly models workflows as command sequences.
- Codex artifact review is runtime-linked; Skills SDK artifact receipts exist but do not yet represent annotations, side-panel review, or reviewer decisions as operational events.
- Codex replay relies on thread/session/rollout truth; Skills SDK evidence can be replayable only when it records the runtime identity and source hash that produced it.

### Where Workflows Should Converge

- SDK runtime proof should consume Codex thread and turn identity when available.
- SDK event streams should be mappable into Codex runtime cards and OTEL spans.
- SDK doctor should distinguish local repo readiness, generated projection readiness, user runtime readiness, Codex runtime readiness, and external review readiness.
- SDK closeout helpers should produce claim-vs-evidence packets that Codex can inspect before final responses.
- SDK routing should emit route_decision.v1 so Codex can replay why a skill was selected.

### Where Skills SDK Should Remain Independent

- Do not recreate Codex thread storage, turn queueing, app-server, hook execution, or permission approval UI.
- Do not make Skills SDK own all goal state. It should adapt to Codex goals and project goal boards, not replace both.
- Do not treat telemetry as proof authority. Preserve the repo's doctrine: artifacts decide, telemetry explains.
- Do not require every skill to be executable code. Some judgement and writing skills should remain advisory, but their proof claims must be bounded.

## Runtime Truth & Verification Findings

### Runtime Finding 1: Runtime Truth Exists, But Is Fragmented

Weak surface: repo status, handles check, doctor, package, proof, events, evals, steering uptake, and runtime cards each expose part of the truth.

Severity: High.

Implementation priority: P0.

Suggested architecture: sdk doctor as the truth reducer. It should not replace underlying commands; it should join their freshness and produce a single operational state.

Validation strategy: fixtures where one surface is green and another is red. The reducer must preserve separate statuses and choose the conservative next command.

### Runtime Finding 2: Event Contracts Need Durable Emission

Weak surface: ./bin/ask skills events reports 8 event types and their producer/observer commands, but this is a registry, not a per-run event log.

Severity: High.

Implementation priority: P0.

Suggested architecture: every SDK lane writes events.jsonl under the configured evidence path. Minimal events:

- sdk_run_started
- route_decision_recorded
- source_checked
- projection_checked
- runtime_checked
- package_checked
- eval_started
- eval_completed
- eval_blocked
- artifact_recorded
- evidence_receipt_recorded
- sdk_run_completed

Validation strategy: command tests assert events are written for doctor/proof/package/eval dry-run fixtures. Schema tests reject missing workflow_run_id or event_id.

### Runtime Finding 3: Runtime Cards Need Stronger Staleness Semantics

Weak surface: runtime-card.v1 has created_at and runtime_status, but no required stale_after, source_revision, projection_identity, command_surface_hash, or external_state_snapshot identity.

Severity: High.

Implementation priority: P0.

Suggested architecture: add freshness:

- observed_at
- stale_after
- source_revision
- source_sha256
- policy_identity
- generated_projection_sha256
- runtime_target_identity
- command_surface_status
- validity_scope

Validation strategy: runtime-card validation should reject pass cards without freshness and allow blocked cards with exact blocker and probe artifact.

### Runtime Finding 4: Package Proof Does Not Uniformly Say What It Proves

Weak surface: package readiness schema has agent_summary and next_command, but live summary extraction showed agent_contract was not uniformly exposed at the top-level location queried. The richer agent_contract appears in deeper doctor/package structures, not consistently across surfaces.

Severity: Medium-high.

Implementation priority: P1.

Suggested architecture: standardize agent_contract across all robot payloads:

- what_this_proves
- what_this_does_not_prove
- claim_allowed
- source_of_truth
- editable_paths
- generated_paths
- forbidden_actions
- next_safe_command

Validation strategy: schema snapshots for doctor, package, prove, eval, external-review, and sdk doctor assert this envelope exists.

### Runtime Finding 5: Selection Truth Is Not First-Class

Weak surface: selection_policy.py is detailed and policy_identity-backed, but a specific routing decision is not preserved by default as an artifact.

Severity: Medium-high.

Implementation priority: P1.

Suggested architecture: route_decision.v1 event and artifact.

Validation strategy: route command fixtures assert stable candidates, policy identity, abstain behavior, and fallback classification.

### Runtime Finding 6: Telemetry Is Present But Not Canonical

Weak surface: ASK payloads include trace_id and telemetry latency. Runtime adapters can read optional OTEL/session collector paths. There is no canonical SDK OTEL event set for skill invocation, doctor, proof, package, eval, route, sync, or closeout.

Severity: Medium.

Implementation priority: P2.

Suggested architecture: telemetry remains explanatory and points to artifact IDs. Emit spans/events for:

- skill.route
- skill.doctor
- skill.package
- skill.proof
- skill.eval
- skill.sync
- skill.external_review
- skill.steering_uptake
- skill.runtime_card_written

Validation strategy: local test exporter fixtures assert span attributes without requiring a live collector.

## Hidden Golden Nuggets

### Golden Nugget 1: Repeated Steering As Telemetry

This is the most valuable operational idea in the repo. It reframes user frustration as a missing system, not a chat failure. The SDK should export this pattern as a general mechanism: repeated correction becomes a guardrail candidate with taxonomy, owner, artifact, validation, and status.

Implementation opportunity: steering_uptake.v1 schema plus sdk doctor integration.

Operational value: large steering reduction.

Risk/tradeoff: over-recording every preference could create process noise. Require recurrence or high-signal classification.

### Golden Nugget 2: Blocked Runtime Is A Valid Outcome

The proof/doctor system treats runtime absence, command-handle drift, auth, missing tools, missing artifacts, environment blockers, and validation blockers as first-class outcomes.

Implementation opportunity: require blocked_runtime receipts across proof, eval, sync, and doctor.

Operational value: prevents false success.

Risk/tradeoff: agents may overuse blocked instead of recovering. Pair with next_safe_command and recovery_case.

### Golden Nugget 3: Stable Temp Staging As Evidence

The Tessl workflow's stable /tmp staging and archive-on-rerun policy is a strong replay/debugging pattern.

Implementation opportunity: generalize to stable evidence staging for external tools: staged_input, tool_command, output_artifact, archive_path, source_hash.

Operational value: reproducible external evals without mutating live source.

Risk/tradeoff: storage growth. Add retention policy and redaction checks.

### Golden Nugget 4: Projection Ownership As Governance

Projection ownership is not just file hygiene. It is a runtime safety boundary.

Implementation opportunity: sdk init and sdk doctor should fail closed on undeclared roots, generated projections edited as source, and unknown project roots.

Operational value: prevents the most common "fix the generated thing" failure.

Risk/tradeoff: external projects may need a gentler migration mode. Use warning mode before enforcement unless mutation is requested.

### Golden Nugget 5: Command Handles Are The UX Layer

Handles let Codex use skills without loading the whole corpus. They are the native-feeling interaction layer.

Implementation opportunity: handle health should become the default visible readiness metric for skills.

Operational value: reduces picker noise and context pressure.

Risk/tradeoff: handles can drift from source. Treat drift as runtime truth.

### Golden Nugget 6: Operation Profiles Are A Lightweight Permission Model

Profiles such as authoring, package-review, eval, plugin-share, and live-mutation already define intent, write policy, and evidence needs.

Implementation opportunity: promote profiles into SDK runtime contracts and map them to Codex permission profiles.

Operational value: safer autonomous execution.

Risk/tradeoff: do not duplicate Codex's approval system. Skills SDK should declare needs; Codex grants or denies.

### Golden Nugget 7: What This Does Not Prove Is As Important As What This Proves

The repo already names proof boundaries in package agent contracts and docs. This should become mandatory.

Implementation opportunity: every robot command payload that could be cited in final output must include what_this_does_not_prove.

Operational value: prevents overclaiming and false readiness.

Risk/tradeoff: verbose payloads. Keep human summaries short while preserving machine fields.

### Golden Nugget 8: Compatibility Aliases Need Expiry Semantics

Folded compatibility handles preserve usability during refactors.

Implementation opportunity: alias telemetry and deprecation state should drive cleanup.

Operational value: reduces routing noise over time.

Risk/tradeoff: removing aliases too early breaks muscle memory. Use observed usage and release windows.

### Golden Nugget 9: Runtime Proof Should Be A Skill Capability, Not A Repo Specialty

The runtime-proof plane can generalize beyond this repo to any skill package.

Implementation opportunity: make proof artifacts part of the public SDK contract.

Operational value: external projects can know if a skill loads and behaves under Codex.

Risk/tradeoff: initial implementation should support Codex/local first, then additional runtimes.

## Missing Systems In Skills SDK

### Missing System 1: Public SDK Namespace

Severity: Critical.

Implementation priority: P0.

Suggested architecture: ./bin/ask skills sdk with init, doctor, status, eval, sync.

Suggested validation method: help test, JSON schema test, fixture with undeclared project root, fixture with generated projection drift, fixture with no eval path.

### Missing System 2: Durable Event Stream

Severity: Critical.

Implementation priority: P0.

Suggested architecture: events.jsonl per workflow run, schema capability-lifecycle-event.v1 promoted from inline contract to concrete file.

Suggested validation method: doctor/proof/package command tests assert event writing in temp evidence root.

### Missing System 3: Runtime Truth Reducer

Severity: Critical.

Implementation priority: P0.

Suggested architecture: reducer consumes repo status, handles check, doctor, package, proof, event stream, runtime card, and optional external state snapshots.

Suggested validation method: contradictory-state fixtures.

### Missing System 4: Staleness Model

Severity: High.

Implementation priority: P0.

Suggested architecture: freshness_snapshot.v1 with source revision, generated projection identity, external state source, observed_at, stale_after, and invalidation triggers.

Suggested validation method: tests that stale evidence downgrades readiness even when status was pass.

### Missing System 5: Route Decision Record

Severity: High.

Implementation priority: P1.

Suggested architecture: route_decision.v1 artifact/event emitted by route, improve, goal, and sdk doctor when a skill is selected or abstained.

Suggested validation method: route replay fixtures.

### Missing System 6: Review-State Awareness

Severity: High.

Implementation priority: P1.

Suggested architecture: review_state.v1 and merge_readiness_snapshot.v1 consumed by code-fixes-triage, verification-before-completion, goal-governor, and pr-green-sweep.

Suggested validation method: fixtures for stale comments, latest-head mismatch, unresolved thread, addressed thread, missing reviewer artifact, and external blocker.

### Missing System 7: Artifact Registry

Severity: High.

Implementation priority: P1.

Suggested architecture: artifact-index.jsonl per workflow with artifact_id, path, type, producer, source command, verifier, checksum, created_at, visibility, retention, redaction.

Suggested validation method: artifact-producing skills must either record artifacts or declare none.

### Missing System 8: Telemetry Event Pack

Severity: Medium.

Implementation priority: P2.

Suggested architecture: local OTEL-compatible event names and attributes, with artifact IDs as links.

Suggested validation method: test exporter snapshots.

### Missing System 9: Skill Behavior Type And Enforcement Level

Severity: Medium-high.

Implementation priority: P1.

Suggested architecture: package readiness fields behavior_type and enforcement_level.

Suggested validation method: mutating/governance/review/runtime skills cannot be advisory_only.

### Missing System 10: SDK Replay Harness

Severity: Medium-high.

Implementation priority: P2.

Suggested architecture: replay a workflow_run from events.jsonl, artifact index, runtime cards, source hash, command outputs, and route decisions.

Suggested validation method: replay fixtures for pass, warning, blocked_runtime, stale_evidence, and projection_drift.

## What Should Become Deterministic

### Stop Being Prompt-Only

- Runtime proof claims.
- Projection sync and projection ownership.
- Skill route selection.
- Review readiness and merge readiness.
- Completion claims.
- Stale external state checks.
- Artifact existence claims.
- Eval/pass claims.
- Skill package promotion.
- Project-local root authority.
- Repeated steering uptake.

### Become Validators

- skills-sdk project manifest presence and root classification.
- generated projection drift.
- command handle parity.
- skill behavior type versus enforcement level.
- runtime-card freshness.
- evidence receipt claim boundaries.
- package portability fields.
- event stream presence for SDK lanes.
- route_decision shape.
- artifact index completeness.
- stale review and CI snapshots.

### Become Runtime Checks

- active Codex runtime handle reachability.
- Codex target readiness by runtime_target.
- user runtime link health.
- permission profile compatibility.
- environment/tool availability.
- current source revision versus proof source revision.
- command surface hash versus proof hash.

### Become Governance Rules

- generated projections are never source unless manifest declares that project root as canonical.
- no final readiness claim without what_this_does_not_prove.
- no live mutation without operation profile and allowed write roots.
- no eval/publish/tool upload from skill eval lanes unless explicitly authorized.
- repeated steering requires durable guardrail or blocked ledger status.

### Become Orchestration Primitives

- workflow_run_id.
- route_decision.
- runtime_card.
- evidence_receipt.
- artifact_record.
- freshness_snapshot.
- recovery_case.
- review_state.
- merge_readiness_snapshot.
- steering_uptake_record.

### Become Replay/Debugging Systems

- stable evidence directories with source hashes.
- events.jsonl per SDK workflow.
- artifact-index.jsonl per workflow.
- replay command that reconstructs state from local artifacts.
- blocked-runtime probe artifacts with exact command and failed gate.

### Remain Human-Controlled

- approving scope changes.
- accepting review tradeoffs that waive findings.
- merging/publishing/deploying.
- granting secrets or credentials.
- approving live project mutation when roots are undeclared.
- deciding whether a judgement-heavy skill output is good enough for public publication.

## What NOT To Build

### Do Not Build A Separate Codex Runtime

Skills SDK should not recreate threads, turns, queues, approvals, hooks, app-server, or permission UI. It should adapt to Codex and emit evidence.

### Do Not Build A Giant Workflow DSL

The repo already has enough routing and orchestration vocabulary. A broad DSL would become another thing agents must learn. Use small schemas and command facades first.

### Do Not Make Every Skill Executable

Some skills are judgement guides. The right rule is not "all prompts become code"; it is "all operational claims become evidence-bound".

### Do Not Treat Telemetry As Proof

Keep the doctrine: artifacts decide, telemetry explains. OTEL spans should link to receipts, not replace them.

### Do Not Hide Planned Surfaces In Active Config

Planning contracts are useful, but they must be separated from executable SDK contracts. Agents should not have to infer whether a command exists.

### Do Not Over-Promote Compatibility Aliases

Aliases help transition, but they increase routing noise. Give them deprecation state, usage telemetry, and cleanup rules.

### Do Not Centralize Domain Skill Logic In ASK

ASK should own contracts, validators, routers, and proof plumbing. Domain-specific procedures should remain in skills/plugins with local validators.

### Do Not Let Repo Status Become A Blanket Green Light

Repo status is one health surface. It must not obscure handle drift, runtime proof failure, package warnings, stale evidence, or external-state gaps.

## Highest-Leverage Implementations

### 1. Build The Public Skills SDK Namespace

WHAT: add ./bin/ask skills sdk init, doctor, status, eval, sync.

WHY: it gives Codex and external projects a small native path instead of a wide internal command graph.

HOW: implement thin facades over existing manifest, doctor, package, proof, eval, handles, and events functions. Do not duplicate logic.

PRIORITY: P0.

VALIDATION METHOD: help output test, JSON schema fixtures, undeclared root fixture, projection drift fixture, blocked runtime fixture.

RISK: facade could become another layer of indirection if it does not reduce decisions. Keep it small and authoritative.

### 2. Add The Agent Contract Envelope Everywhere

WHAT: standardized agent_contract in robot payloads.

WHY: agents need to know what a command proves, does not prove, can mutate, and should do next.

HOW: shared helper in ask.skills_sdk.contracts used by doctor, package, proof, eval, external-review, sync, and sdk doctor.

PRIORITY: P0.

VALIDATION METHOD: schema snapshot tests assert fields across command outputs.

RISK: payload verbosity. Solve with concise agent_summary plus full machine contract.

### 3. Add Durable SDK Events

WHAT: events.jsonl per workflow run.

WHY: lifecycle events are declared but need durable emission for replay and continuity.

HOW: small event writer service with event_id, workflow_run_id, trace_id, event_type, subject, source revision, observed_at, outcome, artifact IDs.

PRIORITY: P0.

VALIDATION METHOD: command tests with temp evidence root.

RISK: event spam. Start with SDK facade commands and proof/package/eval lanes only.

### 4. Make Runtime Card Freshness Enforced

WHAT: require freshness and source/projection identity for pass or warning runtime cards.

WHY: stale proof is the central false-success risk.

HOW: update validate_runtime_cards.py and schema/profile fixtures.

PRIORITY: P0.

VALIDATION METHOD: invalid fixture where runtime_status is implemented_enforced but source_revision/freshness/generation token is absent.

RISK: older cards may fail. Support v1 legacy and v2 strict mode.

### 5. Add Route Decision Replay

WHAT: route_decision.v1 event/artifact.

WHY: routing is an execution decision, not a hidden helper.

HOW: emit from route, improve, goal, sdk doctor, and skill-factory routing wrappers.

PRIORITY: P1.

VALIDATION METHOD: deterministic route tests and low-confidence abstain fixtures.

RISK: token-overlap scoring remains shallow. The event at least exposes the failure.

### 6. Unify Runtime Truth Reduction

WHAT: one reducer for repo, projection, handle, package, proof, event, and freshness states.

WHY: live evidence showed repo status can be green while handle/proof state is red.

HOW: new ask.skills_sdk.truth module with state vocabulary and precedence rules.

PRIORITY: P0.

VALIDATION METHOD: contradictory-state fixtures.

RISK: reducer can become policy-heavy. Keep it as state reduction, not repair logic.

### 7. Add Project-Local SDK Init

WHAT: create or validate skills-sdk.json in owner repos.

WHY: external adoption depends on declared roots and evidence paths.

HOW: sdk init writes minimal manifest only when authorized; otherwise emits proposed manifest and blocked mutation state.

PRIORITY: P1.

VALIDATION METHOD: temp owner repo fixtures with .agents/skills, .codex/skills, custom roots, and unknown roots.

RISK: unsafe root inference. Fail closed until declared.

### 8. Add Review-State And Merge-Readiness Packets

WHAT: structured review/merge truth consumed by review-oriented skills.

WHY: review churn and stale PR state are repeated failure classes.

HOW: schema plus artifact writer, initially local/read-only with manual input or gh-backed adapter.

PRIORITY: P1.

VALIDATION METHOD: fixtures for stale head, unresolved comments, missing checks, addressed old comments, external blocker.

RISK: GitHub/CodeRabbit API churn. Keep adapter separate from schema.

### 9. Add Behavior Type And Enforcement Level To Package Readiness

WHAT: classify skills by operational role and proof strength.

WHY: prompt-only behavior is fine for advisory skills, unsafe for mutating/governance/runtime claims.

HOW: infer from metadata and require explicit override for mutating/review/runtime skills.

PRIORITY: P1.

VALIDATION METHOD: newly added operational skill without validator/eval/artifact contract fails package readiness.

RISK: false positives. Start warning, then enforce on high-risk classes.

### 10. Add SDK Replay Harness

WHAT: replay workflow_run evidence into the same truth reducer.

WHY: debugging operational failures should not require reading the chat transcript.

HOW: sdk replay reads events.jsonl, artifact index, runtime cards, route decisions, and evidence receipts.

PRIORITY: P2.

VALIDATION METHOD: replay fixtures for pass, blocked, stale, and projection drift.

RISK: too much up-front generality. Implement after events and artifact index exist.

## Final Operational Roadmap

### Phase 1 - Runtime Truth & Validation

Objectives:

- Collapse fragmented truth into one SDK readiness reducer.
- Make pass/warning/blocked states freshness-aware.
- Make command payloads clear about what they prove.

Systems affected:

- ASK skills sdk facade.
- skill-doctor, package readiness, proof, handles check.
- runtime-card and evidence-receipt schemas.
- validate_runtime_cards.py and command-handle validators.

Implementation priorities:

- Add skills sdk doctor and status.
- Standardize agent_contract and plane_contract.
- Add command_surface_state to repo status and sdk doctor.
- Enforce runtime-card freshness in strict mode.
- Add contradictory-state fixtures.

Risks:

- Too much work inside one facade.
- Breaking existing consumers of current payloads.
- Treating warning states as pass.

Validators:

- sdk doctor schema validation.
- command surface drift fixture.
- runtime-card stale fixture.
- doctor/proof/package snapshot tests.

Success criteria:

- A Codex agent can run one command and know whether the SDK state is usable, warning, blocked, stale, or unsafe to mutate.
- The payload says exactly what the command proves and does not prove.

### Phase 2 - Workflow & Orchestration Hardening

Objectives:

- Make routing, evals, sync, package review, and recovery workflows deterministic.
- Reduce prompt-only behavior in operational skills.

Systems affected:

- route_skillset.py.
- command_surface.py.
- selection_policy.py.
- eval wrappers and Tessl staging.
- steering uptake ledger.

Implementation priorities:

- Add route_decision.v1.
- Add workflow_run_id.
- Add recovery_case.v1.
- Add behavior_type and enforcement_level.
- Add public sdk init.

Risks:

- Routing artifacts could become noisy.
- The SDK namespace could hide useful expert commands.

Validators:

- route replay fixtures.
- project-local init fixtures.
- eval_run manifest fixtures.
- steering uptake validator.

Success criteria:

- Skill selection and recovery can be replayed from artifacts.
- Project-local adoption does not depend on guessing roots.

### Phase 3 - Replayability & Operational Memory

Objectives:

- Make operational runs replayable without chat transcript reconstruction.
- Turn repeated failures into searchable, structured memory.

Systems affected:

- SDK event writer.
- artifact index.
- runtime cards.
- memory providers.
- session/OTEL adapters.

Implementation priorities:

- Write events.jsonl for SDK lanes.
- Write artifact-index.jsonl for produced artifacts.
- Add sdk replay command.
- Link steering uptake records to evidence receipts.
- Add optional OTEL span export.

Risks:

- Large evidence directories.
- Privacy/redaction mistakes.
- Treating memory as current truth.

Validators:

- replay fixtures.
- redaction checks.
- artifact checksum tests.
- stale-memory downgrade tests.

Success criteria:

- A failed skill run can be reconstructed from local evidence.
- Memory helps route investigation but never outranks current runtime proof.

### Phase 4 - Governance & Review Convergence

Objectives:

- Make review readiness and closeout claims deterministic.
- Prevent stale review, CI, PR, or tracker state from being collapsed into optimism.

Systems affected:

- code-fixes-triage.
- verification-before-completion.
- goal-governor.
- pr-green-sweep and review-oriented skills.
- external review dashboards.

Implementation priorities:

- Add review_state.v1.
- Add merge_readiness_snapshot.v1.
- Add claim_vs_evidence.v1.
- Require artifact-first reviewer outputs for reviewer workflows.
- Add stale external state checks.

Risks:

- External APIs are flaky and rate-limited.
- Over-blocking on stale but irrelevant signals.

Validators:

- stale head fixture.
- unresolved review fixture.
- addressed old-head comment fixture.
- missing artifact fixture.
- external blocker fixture.

Success criteria:

- No skill can claim PR/merge/review readiness from Slack, old CI, old comments, or memory alone.

### Phase 5 - Fully Codex-Native Skills Ecosystem

Objectives:

- Make Skills SDK feel built into Codex workflows.
- Preserve independent package governance while using Codex runtime identity and evidence.

Systems affected:

- Codex runtime adapter.
- runtime-card v2.
- permission/environment resolver.
- app-server/session/rollout adapters.
- skill package portability.

Implementation priorities:

- Map SDK operation profiles to Codex permission profiles.
- Bind runtime cards to Codex thread, turn, trace, tool call, hook, plugin, environment, and rollout identifiers.
- Add Codex session/rollout importer for proof and replay.
- Add OTEL span pack with artifact links.
- Add package portability gates for hosted/local/Codex runtimes.

Risks:

- Recreating Codex runtime behavior in the SDK.
- Binding too tightly to unstable Codex internals.
- Overgeneralizing before the SDK spine is stable.

Validators:

- Codex runtime adapter fixtures.
- permission profile compatibility tests.
- runtime-card v2 schema tests.
- rollout/session replay fixtures.
- package portability matrix.

Success criteria:

- Codex can observe, verify, resume, and explain skill execution through SDK artifacts and events.
- Skills remain portable packages, but their operational truth feels native to Codex.

## Final Recommendation

The single highest-leverage improvement is a public Skills SDK spine with a runtime truth reducer:

- ./bin/ask skills sdk doctor
- a uniform agent_contract envelope
- a durable event stream
- freshness-aware runtime cards
- route decisions and proof artifacts tied to source/projection identity

What currently blocks native-feeling integration is not missing prose. It is fragmented truth. The repo can already produce many useful facts, but an agent still has to know which facts dominate when repo status, handle checks, doctor, package, proof, and event contracts disagree.

The mandatory runtime primitives are:

- workflow_run_id
- route_decision
- command_surface_state
- plane_contract
- agent_contract
- runtime_card
- evidence_receipt
- artifact_record
- freshness_snapshot
- recovery_case
- review_state
- steering_uptake_record

Prototype first:

1. sdk doctor facade.
2. truth reducer with contradictory-state fixtures.
3. events.jsonl for sdk doctor/proof/package.
4. runtime-card strict freshness validation.

Canonicalize after that:

- route_decision.v1.
- eval_run.v1.
- review_state.v1.
- merge_readiness_snapshot.v1.
- runtime-card.v2 Codex identity profile.

How close is Skills SDK to a true Codex-native operational layer?

It is close in architecture and vocabulary, halfway in executable proof, and not yet close enough in public ergonomics. The bones are strong. The next leap is not a bigger skill library. It is a smaller, stricter, more replayable runtime contract that makes the correct next action obvious and makes false success mechanically harder.

## Validation Outcomes

- Command: test -f /Users/jamiecraik/dev/codex/instructions/CODESTYLE.md -> blocked (the Codex front-door file requested by session instruction does not exist in this checkout).
- Command: sed -n '1,220p' AGENTS.md -> pass (target repo instructions read).
- Command: sed -n '1,220p' CODESTYLE.md -> pass (target repo style and validation guidance read).
- Command: sed -n '1,220p' /Users/jamiecraik/dev/agent-skills/.agents/skills/skill-factory/SKILL.md -> pass (skill-factory root skill guidance read).
- Command: python3 Infrastructure/scripts/lifecycle-and-sync/route_skillset.py --skill-set skill-factory ... -> blocked (command rejected by command policy; root skill-factory guidance was applied without loading a child module).
- Command: git status --short --branch -> pass (target repo is on main with many pre-existing local modifications and untracked artifacts).
- Command: ./bin/ask repo status --json --robot -> pass (repo status succeeded and reported skills_synced true).
- Command: ./bin/ask skills --help -> pass (wide skill command surface inspected; no skills sdk namespace present).
- Command: find Skills Plugins/skill-factory/skills Plugins/plugin-factory/skills Plugins/harness-engineering/skills skills-system -name SKILL.md -print | wc -l -> pass (107 source skill entrypoints in sampled primary source roots).
- Command: find .agents/skills -maxdepth 2 -name SKILL.md -print | wc -l -> pass (115 projected runtime skill entrypoints).
- Command: ./bin/ask skills doctor skill-factory-router --json --robot -> fail as evidence (blocked_runtime from generated_command_handle_check).
- Command: ./bin/ask skills proof skill-factory-router --runtime-target codex --json --robot -> fail as evidence (runtime failure from generated_command_handle_check).
- Command: ./bin/ask skills handles --check --check-command-handles --json --robot -> fail as evidence (command surface projection drift plus command handle drift for skill-builder, skill-factory-router, skill-refactor, and skillify).
- Command: ./bin/ask skills events --json --robot -> pass (8 lifecycle event types declared; used to classify event registry versus durable event stream gap).
- Command: rg for required section headings in this artifact -> pass after writing.
- Command: wc -l .harness/research/deep/2026-05-27-skills-sdk-operational-analysis.md -> pass after writing.
