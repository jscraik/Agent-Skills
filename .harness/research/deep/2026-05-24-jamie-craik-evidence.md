# Jamie Craik Evidence Extraction

Date: 2026-05-24

Source material inspected:

- .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html
- .harness/implementation-notes/2026-05-19-deep-module-plan.html
- .harness/research/deep/2026-05-22-skills-sdk-oagen-analysis.md
- .harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md

Source type: local implementation ledger, architecture plan, deep research artifact, and evidence-led gap audit.

This document is not a summary of the source material. It extracts reusable engineering intelligence from the observed operating model, validation behavior, failure handling, tooling decisions, and governance patterns.

Confidence labels:

- High confidence: directly evidenced in the inspected source material.
- Medium confidence: strongly inferred from repeated operating patterns and surrounding evidence.
- Low confidence: plausible extrapolation that should be tested before adoption.

## Executive Summary

The strongest engineering signal is a deliberate shift from narrative agent output to evidence-owned runtime truth. The operating model treats Codex-native behavior as the actual ABI, not as documentation prose or projection existence. Every important claim is forced through a command, schema, snapshot, review artifact, goal-board receipt, Linear update, or classified blocker.

The reusable pattern is not merely "use agents for coding." It is: create a narrow control plane, make each agent-visible claim machine-readable, bind each implementation slice to validation evidence, classify failures by ownership, and keep generated surfaces behind repo-owned sync commands. The loop is orientation, bounded slice, deterministic proof, review stack, remediation, live-state refresh, and closeout receipt.

The most important architectural insight is that skills, package metadata, runtime projection, generated command handles, Codex loader/render/injection parity, and evidence ledgers must be separate surfaces with explicit contracts. Collapsing those surfaces creates false success: a skill can appear ready because .agents is reachable, a projection exists, or a command produces polished JSON, while Codex-native invocation remains unproved.

The most reusable harness engineering concepts are runtime-targeted proof gates, doctor commands that expose next-command decision evidence, compatibility snapshots for public JSON surfaces, generated projection repair through repo-owned commands only, review swarms with artifact-first outputs, local evidence services, and deferred research governance.

The biggest risks are overclaiming parity, letting generated files become manual edit targets, treating blocked validation as failure or success instead of classified state, confusing review-system stale state with live current-head truth, and broadening a slice without an explicit scope expansion record.

## Core Engineering Patterns

### Pattern: Runtime Truth Over Surface Reachability

**Description:**

A skill or command is not considered ready merely because a projection exists, a handle resolves, or a non-Codex runtime can reach it. Runtime truth is target-specific. If the requested runtime is Codex, the proof must require Codex-specific readiness.

**Evidence:**

High confidence:

- The governed execution notes identify a false-success boundary where .agents readiness can be mistaken for Codex ABI conformance.
- The implementation introduced <code>runtime_target=any|codex|agents</code>, with <code>runtime_target=codex</code> requiring <code>codex_user_runtime_ready</code>.
- Codex-targeted proof intentionally exits with structured validation failure when only .agents is ready.
- The audit names runtime proof passing without Codex readiness as a top gap.

**Why It Matters:**

Without target-specific runtime gates, a harness can certify the wrong thing. This is especially dangerous for agent systems because agents will propagate the status as truth and may proceed to publish, sync, or recommend follow-up work based on a false ready signal.

**Implementation Opportunities:**

- Add runtime-target parameters to every proof command that can span multiple execution surfaces.
- Make the default compatibility mode explicit rather than implicit.
- Add schema fields such as runtime target, available runtimes, required gate, runtime satisfied by, and blocked checks.
- Require Codex parity mode in closeout checks that claim Codex-native availability.

**Risks / Tradeoffs:**

- Strict target modes can block workflows that were previously good enough.
- Compatibility defaults must be preserved carefully so older callers do not break.
- Target-specific gates increase schema complexity and test matrix size.

### Pattern: Doctor As Decision Packet, Not Status Summary

**Description:**

The doctor command should emit a structured decision packet: checks, blockers, warnings, runtime failure payloads, next-command precedence, and recovery guidance. It should not merely say pass, warning, or fail.

**Evidence:**

High confidence:

- The JSC-351 notes add runtime failure fields with schema version, error code, failed check id, JSON path, recovery guidance, and validation command guidance.
- Doctor output preserves runtime failure context inside runtime reachability checks.
- <code>next_command_decision</code> exposes blocker/warning/default precedence.

**Why It Matters:**

Agents need a next action, not just a diagnosis. A structured doctor packet lets agents route to repair, stop safely, or report a classified blocker without reinterpreting prose. It also makes regression tests possible for routing behavior.

**Implementation Opportunities:**

- Standardize <code>next_command_decision</code> across repo, skill, package, runtime, and projection doctors.
- Include precedence reasons and the exact failing check id.
- Add tests for invalid argument paths that must reach structured command implementation logic rather than being swallowed by parser-level errors.
- Snapshot doctor public output.

**Risks / Tradeoffs:**

- Too many fields can create contract drift unless snapshots and schemas are mandatory.
- Additive compatibility can leave permissive schema behavior in early versions; this should be a conscious compatibility tradeoff, not an accident.

### Pattern: Classified Blocked State

**Description:**

A blocked validation command can be successful evidence if it proves the intended guardrail and classifies the remaining blocker. The operating model distinguishes expected fail-closed behavior, pre-existing blockers, introduced failures, stale projection drift, environment failures, and review-system stale state.

**Evidence:**

High confidence:

- PU-002 was recorded as <code>pass_with_classified_runtime_blockers</code> rather than a green global repo state.
- Skills handles and repo doctor reported <code>blocked_pre_existing</code> while proving generated command handles passed.
- Codex-targeted proof exiting 2 was recorded as pass because it proved fail-closed behavior.
- Browser navigation to a local file report was classified as Browser policy blocker, not missing artifact.

**Why It Matters:**

Binary pass/fail thinking causes two opposite errors: claiming success when the wrong thing passed, or stopping useful work because an unrelated system is red. Classified blocked state lets work continue only when the remaining risk is understood and owned.

**Implementation Opportunities:**

- Require every gate result to include outcome, classification, owner, and next action.
- Treat expected negative tests as pass only when the exact structured failure payload is verified.
- Persist blocker classifications in receipts or validation JSONL.
- Add a validator that fails if closeout text says pass while the evidence contains unclassified exit 2 commands.

**Risks / Tradeoffs:**

- Misclassification can hide real regressions.
- Requires discipline to avoid turning pre-existing into an excuse; pre-existing blockers still need a later owner.

### Pattern: Bounded Slice Governance

**Description:**

Each implementation slice has an explicit objective, allowed file set, exclusions, validation commands, review stack, and closeout receipt. Scope expansion is allowed only when runtime discovery proves it necessary and the governor records the expansion before edits.

**Evidence:**

High confidence:

- JSC-351 proceeds by bounded PU slices.
- T011 expanded allowed files before editing command-surface code and tests.
- PU-003 explicitly avoided package schemas, preview commands, and service extraction.
- PU-004 explicitly excluded preview commands, publishing workflows, global installs, plugin cache mutation, package registry integration, and runtime config writes.

**Why It Matters:**

Agent workflows drift easily. Bounded slices prevent "fix the found thing" from becoming uncontrolled architecture change. They also make review and rollback cheaper because each slice has a small intended behavior delta.

**Implementation Opportunities:**

- Add a slice manifest with objective, allowed files, excluded surfaces, tests, reviewers, and closeout criteria.
- Have validators compare changed files against allowed scope.
- Require a recorded scope expansion event before modifying out-of-scope files.
- Attach receipts to goal board state.

**Risks / Tradeoffs:**

- Overly rigid boundaries can slow necessary cross-cutting fixes.
- Scope manifests can become paperwork unless enforced by tooling.

### Pattern: Generated Surfaces Are Repaired By Generators

**Description:**

Generated projections, command surfaces, skillset manifests, runtime summaries, and root indexes must be refreshed through repo-owned commands, not hand-edited.

**Evidence:**

High confidence:

- T010 states command-surface drift is a generated projection reconciliation task to be performed through repo-owned commands, not hand edits.
- Generated-surface handling later refreshes .skillsets and SKILL.md through repo-owned sync.
- The deep module plan has a "Files Not To Hand-Edit" section.

**Why It Matters:**

Generated files carry derived state and provenance. Hand edits can produce a superficially correct diff that is overwritten later or masks a bug in the generator. Repo-owned sync commands preserve source identity and make the repair reproducible.

**Implementation Opportunities:**

- Put generated file ownership in a manifest.
- Add headers or metadata that identify generator, source hash, config hash, and ownership class.
- Make pre-commit fail when generated files change without a matching generator/source change or sync receipt.
- Provide dry-run and actual sync commands with machine-readable deltas.

**Risks / Tradeoffs:**

- Generator bugs can block urgent fixes.
- Sync commands can touch many files, so review tooling must separate expected generated churn from human implementation.

### Pattern: Compatibility Snapshot Before Broad Autonomy

**Description:**

Public JSON, CLI payloads, schemas, command metadata, runtime cards, generated handles, and package readiness output should be protected with baseline-vs-candidate compatibility snapshots before broad autonomous generation is allowed.

**Evidence:**

High confidence:

- The Oagen analysis requires generated artifact manifests, public-surface compatibility snapshots, smoke verification, and deterministic AI boundaries.
- PU-004 adds package schema files and a skill-package-readiness public-output fixture.
- The gap audit says the project is not ready for broad autonomous Skills SDK generation until loader/render/injection/config parity, package schemas, compatibility snapshots, and conformance evidence are executable and enforced.

**Why It Matters:**

Agents can generate plausible public outputs quickly. Compatibility snapshots catch silent API drift that ordinary tests and manual review often miss.

**Implementation Opportunities:**

- Create snapshot extractors for doctor, package, proof, handles, runtime preview, command metadata, and runtime cards.
- Compare baseline and candidate snapshots in CI.
- Classify changes as breaking, soft-risk, additive, or internal.
- Require explicit approval records for breaking changes.

**Risks / Tradeoffs:**

- Snapshot systems can become noisy if schemas are unstable.
- Early snapshots should focus on public surface, not incidental ordering or timestamps.

### Pattern: Smoke Verification Separate From Compatibility

**Description:**

Compatibility checks protect public shape; smoke checks prove behavior. Neither replaces the other.

**Evidence:**

High confidence:

- The Oagen analysis has a dedicated pattern, "Smoke Verification Separate From Compatibility."
- PU-004 uses schema and snapshot identity plus live package command smoke.
- PU-005 validates preview commands with both tests and live CLI smoke.

**Why It Matters:**

A command can preserve public JSON shape while executing the wrong runtime behavior. Conversely, behavior can work while breaking consumers. Separate gates produce better failure labels.

**Implementation Opportunities:**

- For every public command, maintain both schema/snapshot tests and live representative smoke commands.
- Store smoke evidence in JSONL with command, exit code, expected outcome, payload path checks, and runtime environment.
- Use smoke checks to validate next-command guidance after failure.

**Risks / Tradeoffs:**

- More gates require maintenance.
- Smoke tests can become flaky unless they avoid external dependencies or classify environment blockers.

### Pattern: Review Stack As Controlled Failure Injection

**Description:**

Reviews are used to find likely regressions before closeout, and re-reviews verify remediation. The review stack is not a vague quality ritual; it is a targeted adversarial system with artifact outputs.

**Evidence:**

High confidence:

- PU-001, PU-002, T011, T012, and PU-004 all record review findings, fixes, re-review artifacts, and residual tradeoffs.
- T011 caught a simplification attempt that disabled folded compatibility handles, then restored compatibility-preserving policy.
- Review artifacts are referenced as required closeout evidence.

**Why It Matters:**

Agent implementation can overfit the immediate failing test. Review stack catches second-order regressions such as compatibility breaks, insufficient assertions, weak schemas, and misleading docs.

**Implementation Opportunities:**

- Require reviewer artifacts to include severity, file/line evidence, remediation suggestion, and final status.
- Add a coordinator verification step that checks every expected artifact exists and is non-empty.
- Classify review findings by introduced/current/pre-existing/environment.
- Use targeted re-review after remediation rather than treating first review as final truth.

**Risks / Tradeoffs:**

- Review swarms can become slow or expensive.
- Without artifact verification, mailbox summaries can be mistaken for completed reviews.

### Pattern: Local Evidence Feedback Loop

**Description:**

Logs, metrics, traces, lifecycle events, validation outcomes, and session summaries become queryable evidence. Codex uses that evidence to find failing boundaries, patch owner modules, rerun workloads, and decide promotion or rollback.

**Evidence:**

High confidence:

- The deep module plan describes local evidence services: logs, metrics, traces, query/correlate, patch/rerun, promote/rollback.
- It names session-collector and otel-collector as evidence services.
- It frames eval findings as classified deltas, affected paths, rerun commands, and evidence.

**Why It Matters:**

Agent improvement without replayable evidence devolves into anecdotal prompt tweaking. A local evidence loop makes skill repair and harness repair observable and repeatable.

**Implementation Opportunities:**

- Emit JSONL events for command lifecycle, validation lifecycle, projection lifecycle, package lifecycle, and subagent lifecycle.
- Build evidence-provider interfaces over local logs, stats, traces, and session summaries.
- Store before/after evidence for each repair.
- Add promotion records that cite rerun proof and rollback criteria.

**Risks / Tradeoffs:**

- Local telemetry can create privacy and retention concerns.
- Evidence volume must be indexed and summarized; raw logs alone are not an operating system.

## Tooling & Ecosystem

### Repository CLI And Control Plane

#### ./bin/ask

Purpose: Repo-native command surface for skill operations, doctor checks, package readiness, runtime previews, sync, proof, and repo health.

Workflow role: Primary automation interface for agents and humans. It encodes repo contracts and returns machine-readable JSON in robot mode.

Integration opportunities:

- Use as the only supported entrypoint for repo operations.
- Add conformance commands that emit evidence directories.
- Wrap doctor/package/proof outputs with schemas and compatibility snapshots.

Implied best practices:

- Prefer repo-owned commands over ad hoc shell sequences.
- Include exact next commands in failure payloads.
- Use structured errors and stable schema versions.

Strengths:

- Centralizes behavior.
- Supports deterministic validation and agent-readable routing.
- Makes policy enforceable through tests.

Limitations:

- Large command modules can become architectural bottlenecks unless services are extracted.
- Public output becomes an API and requires compatibility discipline.

#### Python test runners and uv dependency runtime

Purpose: Focused and wider regression testing.

Workflow role: Proves changed behavior, provides fallback when default Python lacks dependencies such as PyYAML, and enables narrow selectors around package, doctor, preview, invocation, render, and command-surface behavior.

Integration opportunities:

- Use focused tests for slices, then selector-based wider tests before closeout.
- Encode environment cache paths for sandboxed dependency runs.

Implied best practices:

- Treat missing local dependencies as an environment classification, not a code failure.
- Use ephemeral dependency-supplied runtimes when the repo permits them.

Strengths:

- Fast focused proof.
- Good fit for schema and command-payload tests.

Limitations:

- Default interpreter drift can cause collection blockers.
- Tests must be paired with live CLI smoke to prove command wiring.

### Runtime And Projection Tooling

#### Rooted Projection Sync

Purpose: Generate and reconcile runtime projection files, command handles, manifests, and indexes from canonical source.

Workflow role: Repairs stale generated surfaces and prevents manual generated-file edits.

Integration opportunities:

- Emit source identity, generator identity, and file ownership manifest.
- Provide dry-run deltas for review.
- Fail when stale bridge aliases or unauthorized generated handles appear.

Implied best practices:

- Keep plugin cache refresh explicit and skippable.
- Use dry-run before actual sync.
- Test both symlink and real-directory stale aliases.

Strengths:

- Makes generated drift repair reproducible.
- Protects canonical/generated boundaries.

Limitations:

- Requires careful sandbox permissions for symlink mutation.
- Large generated diffs can obscure human intent.

#### Command Surface Generator

Purpose: Maintain skill command metadata and generated command handles.

Workflow role: Bridges skills into agent-invokable command handles while enforcing hidden/system bridge policy.

Integration opportunities:

- Validate command-handle parity in repo doctor.
- Snapshot command-surface public output.
- Add compatibility tests for folded aliases and bridge suppression.

Implied best practices:

- Separate command-surface projection drift from generated handle drift.
- Preserve compatibility aliases unless a targeted policy removes them.

Strengths:

- Converts skill availability into explicit runtime command handles.

Limitations:

- Compatibility behavior is fragile when simplification touches alias policy.

### Evidence And Review Tooling

#### Linear

Purpose: Issue tracking, task traceability, slice status, and durable comments.

Workflow role: External tracker truth for JSC issues, continuation blockers, implementation status, and closeout evidence.

Integration opportunities:

- Link goal-board receipts to Linear comments.
- Validate issue state and parent/child relationships before closeout.
- Include Linear mutation status in delivery audit.

Implied best practices:

- Keep project assignment intentionally omitted until destination health is known.
- Comment with classified runtime truth instead of greenwashed summaries.

Strengths:

- Provides durable external coordination state.

Limitations:

- Tracker state can lag repo truth and must be rechecked live.

#### GitHub and CodeRabbit

Purpose: PR review, inline comments, review status, and current-head feedback.

Workflow role: Review truth source, but only after distinguishing active current-head feedback from stale comments on old commits.

Integration opportunities:

- Build exact-head review-thread validators.
- Classify stale comments as review-system residuals.
- Verify addressed comments against commit SHAs and line availability.

Implied best practices:

- Do not treat old inline comments with null lines as active current-head blockers.
- Do not treat external review state as code failure without current-head verification.

Strengths:

- Provides high-signal adversarial review.

Limitations:

- Review state can be stale, commit-scoped, or externally blocked.

#### session-collector and otel-collector

Purpose: Local evidence capture for sessions, logs, metrics, traces, health, stats, freshness, and telemetry confidence.

Workflow role: Feed evidence loops that turn failures into repairable deltas and rerun proof.

Integration opportunities:

- Query validation failures by command, path, slice, and owner.
- Feed skill improvement candidates.
- Generate telemetry confidence and freshness reports.

Implied best practices:

- Keep evidence local and privacy-aware.
- Correlate events before patching.

Strengths:

- Enables forensic diagnosis and replayable learning.

Limitations:

- Needs indexing, redaction, and retention policy.

### Architecture References

#### WorkOS Oagen and Oagen Emitters

Purpose: Reference architecture for source-to-IR-to-emitter generation, compatibility snapshots, manifests, smoke checks, and deterministic AI-assisted workflows.

Workflow role: External model for Skills SDK design.

Integration opportunities:

- Adapt versioned IR, pure emitters, generated manifests, baseline/candidate compatibility snapshots, and plugin emitters to skills, package metadata, docs, runtime cards, and command surfaces.

Implied best practices:

- Keep AI advisory around deterministic evidence.
- Put domain policy in config, not generated manifests.
- Separate public-surface compatibility from behavior smoke.

Strengths:

- Strong separation of source parsing, IR, emitters, writer, and verifier.

Limitations:

- OpenAPI/SDK semantics should not be copied wholesale into skills; the domain model must be skill/runtime/eval specific.

## Harness Engineering Insights

### Orchestration

- Use bounded slices as the unit of agent execution.
- Maintain a single active task in the goal board.
- Record scope expansion before edits when runtime discovery changes the required file set.
- Use review swarms only when the risk surface needs multiple lenses.
- Verify artifact existence and non-empty content before synthesis.

Implementation pattern:

1. Orient against repo state, tracker state, and source evidence.
2. Open a bounded slice with allowed files and excluded surfaces.
3. Implement only the slice.
4. Run focused validation.
5. Run review stack.
6. Remediate findings.
7. Rerun validation and review as needed.
8. Close with receipt, tracker comment, and exact remaining blockers.

### Validation

- Validation is a chain, not a single command.
- Expected negative outcomes can be pass conditions if the structured failure is verified.
- Repo doctor must distinguish advisory diagnostics from blockers.
- Generated projection checks must run before downstream gates that depend on generated state.
- Schema validation and live command smoke are separate.

Implementation pattern:

- For each command contract, maintain schema test, public snapshot, focused unit test, and live smoke.
- Emit classification for every non-zero command.
- Persist exact command text and result.

### Context

- Keep heavy details in deep modules and source artifacts.
- Expose root-level command handles and summaries only when needed.
- Use runtime budget checks to prevent context flooding.
- Model Codex render behavior explicitly before claiming parity.

Implementation pattern:

- Build a render-preview command that reports included/omitted skills, budget behavior, source identity, and blocked live-runtime checks.
- Keep root skill bodies short and move implementation detail to references.

### Routing

- Route by explicit runtime target, not generic availability.
- Route generated-handle failures separately from projection-drift failures.
- Route package readiness separately from doctor readiness.
- Route research artifacts as deferred design inputs until adopted by a plan/spec/issue.

Implementation pattern:

- Use stable failure codes for projection drift, generated handle failure, blocked runtime, and blocked validation.
- Make next-command choice explainable with precedence reason.

### Memory

- Treat durable memory as a retrieval layer, not source of current truth.
- Recheck live repo and tracker state before closeout.
- Use implementation ledgers and receipts for durable project memory.
- Store failure patterns as validators or docs when they recur.

Implementation pattern:

- Add memory-derived suggestions to orientation, then verify them with current commands.
- Convert repeated failure patterns into a repo artifact plus validation.

### Evals

- Evals should produce classified deltas, affected paths, rerun commands, and evidence.
- Workouts should become conformance tests, not just examples.
- Judge/calibration outputs must be bounded by deterministic acceptance checks.

Implementation pattern:

- Add <code>ask skills conformance run --evidence-dir</code>.
- Store JSONL events, final summary, fixture snapshots, and command transcript redaction.
- Promote skill changes only with before/after evidence.

### Governance

- Merge authority and implementation authority remain separate unless explicitly delegated.
- Generated output authority belongs to generators.
- Runtime truth belongs to live commands and validated payloads.
- Research authority is deferred until adopted.

Implementation pattern:

- Maintain authority fields in plan/spec/goal-board artifacts.
- Add validators for authority and scope boundary sections.
- Reject closeout claims that lack live state evidence.

### Scaling

- Broad autonomy waits until loader/render/config/injection parity, schemas, snapshots, and conformance evidence exist.
- External emitter/plugin patterns can scale output families without coupling the core.
- Local evidence services scale learning loops by turning failures into queryable repair candidates.

Implementation pattern:

- Start with one or two representative skills and public commands.
- Add emitter boundaries after the first public contract is stable.
- Scale only after compatibility snapshots stabilize.

### Recovery

- Classify before repairing.
- Use the smallest owner module change.
- Rerun the failing command, not just nearby tests.
- Preserve rollback criteria when promotion is uncertain.

Implementation pattern:

- Add recovery handlers for stale handles, Codex link drift, config-rule mismatch, package snapshot drift, and projection drift.
- Require before failure, repair command, after proof, and residual risk.

## Implied Best Practices

- Make false success the first design enemy. The best slices target places where a command can pass for the wrong reason.
- Separate compatibility defaults from strict parity modes so adoption can be incremental without losing rigor.
- Prefer additive schemas and explicit versioning for early contracts, then tighten unknown-key handling once fixtures stabilize.
- Keep blocked as a first-class status with ownership, not an embarrassment to hide.
- Use repo-owned wrappers for operations because they encode policy, caches, sandbox expectations, and output shape.
- Treat generated-file diffs as evidence of source/generator state, not as manual implementation territory.
- Make every review finding end in one of: fixed, accepted residual, pre-existing, environment, stale review state, or out-of-scope.
- Validate the validator when it becomes part of the contract; test fallback schema harnesses and unsupported-key behavior.
- Use exact source identity when modeling external runtime behavior; avoid machine-local paths in public payloads.
- Keep plugin cache mutation, home config writes, package publishing, and runtime config writes out of read-only preview slices.
- Prefer dry-run before actual sync when projection state is involved.
- Use source-to-IR-to-emitter only after the source contract is understood; do not introduce an IR as a substitute for domain clarity.
- Do not let AI-written prose become authority. AI can suggest, summarize, or classify, but deterministic evidence owns truth.
- Maintain public artifacts for human coordination, but anchor them to machine-verifiable receipts.
- Keep project assignment and delivery routing intentionally unset until destination health is confirmed.

## Failure Modes & Mitigations

### Failure: False Runtime Readiness

Description: A skill appears ready because .agents runtime is available while Codex runtime is not.

Evidence: The audit names runtime proof passing without Codex readiness as a top gap; PU-001 implements runtime-targeted proof to fail closed.

Probable root cause: Runtime availability was modeled as generic reachability instead of target-specific conformance.

Severity: Critical.

Mitigation strategy: Require runtime-targeted proof for every conformance claim and wire strict targets into doctor parity mode.

Recommended guardrails:

- Runtime-target schema field.
- Codex parity doctor mode.
- Negative smoke proving fail-closed behavior.
- CI check that parity claims cite Codex-targeted proof.

### Failure: Generated Projection Drift Becomes Manual Work

Description: Stale .skillsets, command surfaces, root indexes, or runtime projections tempt agents to hand-edit generated files.

Evidence: T010 classifies command-surface drift as projection reconciliation through repo-owned commands; generated-surface handling explicitly says no generated projection was hand-edited.

Probable root cause: Generated outputs are visible in the repo and can look like ordinary implementation files.

Severity: High.

Mitigation strategy: Add generated artifact manifest, ownership headers, sync receipts, and pre-commit checks that detect unsupported manual generated edits.

Recommended guardrails:

- Generated by, source hash, generator version, and ownership class.
- Dry-run sync in review.
- Pre-commit generated drift validator.
- Files-not-to-hand-edit documentation with validator enforcement.

### Failure: Blocked Validation Is Misreported

Description: A command exits non-zero, but the workflow either calls the slice failed or claims success without classifying the blocker.

Evidence: PU-002 records classified runtime blockers; multiple commands are marked pre-existing blockers or expected validation failures.

Probable root cause: Validation systems often collapse outcomes to pass/fail and omit ownership.

Severity: High.

Mitigation strategy: Require outcome, classification, owner, and next action for every non-zero result in closeout.

Recommended guardrails:

- Closeout linter for unclassified failures.
- Structured validation ledger.
- Required owner labels: current patch, pre-existing, unrelated dirty worktree, environment/tooling, expected negative test.

### Failure: Review System Stale State Blocks Delivery

Description: Old inline comments or review artifacts are mistaken for active current-head feedback.

Evidence: The notes identify one remaining inline comment on an old commit with null line as stale GitHub review-comment state, not current-head feedback.

Probable root cause: Review tools retain commit-scoped comments after code moves or is addressed.

Severity: Medium.

Mitigation strategy: Verify review feedback against current head SHA, line existence, and addressed markers before classifying as active.

Recommended guardrails:

- Exact-head review-thread audit.
- Stale-comment classifier.
- Delivery-state auditor that separates active blockers from historical review state.

### Failure: Simplification Breaks Compatibility

Description: A cleanup intended to reduce duplication removes compatibility behavior.

Evidence: T011's first simplification attempt disabled folded compatibility handles; architecture re-review caught it and the governor restored compatibility-preserving policy.

Probable root cause: Compatibility behavior was encoded in duplicated or subtle policy paths without enough targeted tests.

Severity: High.

Mitigation strategy: Add compatibility tests before simplification and require architecture re-review for public-surface policy changes.

Recommended guardrails:

- Compatibility snapshots for aliases and generated handles.
- Tests for folded aliases, hidden bridge skills, wrong-target symlinks, and stale real directories.
- Review checklist item: does simplification remove a compatibility path?

### Failure: Schema Fallback Gives False Confidence

Description: A fallback schema validator silently accepts unsupported constructs or skips validation when dependencies are unavailable.

Evidence: PU-001 and PU-004 remediate fallback/schema harness gaps, including unsupported validation keywords, minItems, local references, conditional constructs, and unknown metadata keys.

Probable root cause: Optional dependency behavior made validation environment-sensitive.

Severity: High.

Mitigation strategy: Make fallback validators fail on unsupported keywords and test every declared construct.

Recommended guardrails:

- Schema harness self-tests.
- Disallow silent skip when jsonschema is unavailable.
- Use dependency-supplied test runtime when repo policy allows.
- Public snapshot fixtures for schemas.

### Failure: Preview Commands Overclaim Runtime Parity

Description: Repo-side preview commands model Codex runtime behavior but cannot prove live Codex config stack, plugin-root injection, UI selection, or exact shell parser parity.

Evidence: PU-005 says preview commands must not claim full runtime parity and must emit structured blocked checks.

Probable root cause: Modeling external runtime source can be confused with executing that runtime.

Severity: High.

Mitigation strategy: Include source identity, modeled rule version, and blocked live-runtime checks in every preview output.

Recommended guardrails:

- Modeled rule version.
- Source files.
- Blocked checks.
- Separate live Codex integration gate when available.

### Failure: Research Becomes Unapproved Implementation Authority

Description: Deep research artifacts influence design but are treated as if they authorize implementation scope.

Evidence: Prior memory and current artifacts frame deep research as design input; implementation slices require separate plan/spec/goal authority.

Probable root cause: Research documents can be detailed enough to look like a spec.

Severity: Medium.

Mitigation strategy: Label research artifacts as deferred or advisory until adopted by an implementation authority surface.

Recommended guardrails:

- Research frontmatter with deferred research authority.
- Plan/spec adoption section citing which research recommendations are accepted.
- Validator that rejects implementation closeout based only on research artifact existence.

Confidence: Medium.

### Failure: Command Module Becomes A Monolith

Description: CLI behavior, payload assembly, validation, packaging, runtime adaptation, and evidence logic live in large command modules.

Evidence: The gap audit says SDK layers are named but not module boundaries and behavior remains concentrated in command modules.

Probable root cause: CLI-first growth accumulates behavior where commands are easiest to patch.

Severity: Medium.

Mitigation strategy: Extract services around contracts, catalog, validation, packaging, runtime adapters, evidence, and emitters with import-layer tests.

Recommended guardrails:

- Dependency layer tests.
- Pure service functions returning data, not writing files.
- Thin CLI adapters.
- Package-level architecture documentation.

### Failure: Context Budget Does Not Match Runtime Renderer

Description: Repo budget checks pass while actual Codex renderer inclusion, shortening, or omission behavior differs.

Evidence: The gap audit marks renderer parity as partial and recommends render preview; PU-005 adds modeled render preview with blocked live-runtime checks.

Probable root cause: Repo validators estimate context behavior instead of using Codex renderer rules.

Severity: Medium.

Mitigation strategy: Model renderer source with explicit source identity, then add live integration proof when possible.

Recommended guardrails:

- Render-preview snapshots.
- Tests for omission and shortened-description branches.
- Runtime source revision field.

## Reusable Techniques

### Technique: Evidence-First Slice Template

Use this template for each implementation slice:

1. Objective: one behavior change.
2. Authority: goal/spec/issue reference.
3. Allowed files: explicit list or glob.
4. Exclusions: surfaces that must not change.
5. Runtime discovery: current commands and expected failures.
6. Implementation delta: exact contract changes.
7. Focused tests: unit/fixture.
8. Live smoke: command-level proof.
9. Review stack: required reviewers/artifacts.
10. Remediation: findings and disposition.
11. Closeout: receipt, tracker comment, residual blockers.

### Technique: Structured Negative Test

For fail-closed behavior, require:

- Command exits with expected non-zero code.
- Top-level envelope is valid.
- Error code is stable.
- Data payload includes failed check id and JSON path.
- Recovery guidance contains exact next command.
- Test names the negative outcome as expected pass.

### Technique: Projection Repair Protocol

1. Run projection verifier.
2. If drift exists, identify generated owner.
3. Run repo-owned sync dry-run.
4. Run actual sync with plugin cache refresh setting explicit.
5. Rerun verifier.
6. Record generated files as sync output, not manual implementation.

### Technique: Compatibility Snapshot Rollout

1. Pick one public command.
2. Define schema.
3. Capture sanitized public-output fixture.
4. Add extractor that removes timestamps/local paths.
5. Compare baseline and candidate.
6. Classify changes.
7. Add approval mechanism for intentional breaking changes.

### Technique: Review Artifact Contract

Each reviewer writes scope reviewed, severity-ranked findings, exact file and line evidence, remediation suggestion, validation ownership classification, and status line. The coordinator verifies artifacts, retries once if missing, then records coverage gaps.

### Technique: Preview Without Overclaiming

For modeled runtime commands, include source repository, source revision, modeled source files, modeled rule version, and unsupported live dimensions in blocked checks. Avoid claiming parity unless live runtime execution proves parity.

### Technique: Evidence Service Loop

1. Collect logs, metrics, traces, validation outputs, and session summaries.
2. Query by failure code, command, path, and slice.
3. Correlate to owner module.
4. Patch smallest owner surface.
5. Rerun exact failing workload.
6. Promote if evidence improves; roll back otherwise.

## Strategic Insights

### Codex-Native ABI Is The Real Contract

The repo is moving from "skills exist as packages" to "skills are valid only when Codex can load, render, configure, inject, and invoke them as expected." This reframes skill development as runtime conformance engineering rather than content packaging.

Strategic implication: future skill systems need compatibility tests against the host agent runtime, not only their own package format.

Confidence: High.

### Harness Engineering Is Control-Plane Design

The durable work is the control plane around agent action: routing, validators, schemas, snapshots, ledgers, review artifacts, and recovery commands. The agent is useful because the harness constrains what success means.

Strategic implication: the highest-leverage investment is not more prompt text; it is better executable surfaces for agents to inspect and obey.

Confidence: High.

### AI Belongs Around Deterministic Evidence

The WorkOS-derived pattern and local governance agree: AI can classify, suggest, repair, and generate candidate changes, but deterministic systems own truth. This is a mature boundary for agentic engineering.

Strategic implication: organizations should invest in validators, compatibility snapshots, and evidence ledgers before scaling autonomous code generation.

Confidence: High.

### Generated And Human-Maintained Ownership Must Be Explicit

Agent workflows make generated/human boundaries more important, because agents can edit anything that looks like text. Ownership metadata, manifests, and sync commands are safety infrastructure.

Strategic implication: generated artifact governance should be part of every agent-friendly repo.

Confidence: High.

### Research Needs An Adoption Boundary

Deep research documents are powerful, but they should not silently become scope. The adoption boundary is a plan/spec/issue/validator that names which recommendations become binding.

Strategic implication: research-to-implementation pipelines need explicit promotion gates.

Confidence: Medium.

## Key Quotes & Evidence

Only material evidence is included here.

- "Execution will proceed by bounded slices." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:47.
- "The default remains runtime_target=any for compatibility, while runtime_target=codex requires codex_user_runtime_ready." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:92.
- "This is the expected fail-closed result." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:107.
- "The command-surface blocker is separate." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:206.
- "The governor expanded T011's allowed files... before editing them." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:223.
- "The preview commands must not claim full runtime parity." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:304.
- "No generated projection was hand-edited." Evidence: .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html:582.
- "AI workflows that consume deterministic diffs and compatibility signals rather than replacing them." Evidence: .harness/research/deep/2026-05-22-skills-sdk-oagen-analysis.md:52.
- "The WorkOS pattern is not 'AI generates everything.' It is 'deterministic systems make generation safe enough for AI to assist around the edges.'" Evidence: .harness/research/deep/2026-05-22-skills-sdk-oagen-analysis.md:472.
- "Runtime proof can pass without Codex readiness." Evidence: .harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md:50.
- "Broad autonomous generation workflows before compatibility snapshots and deterministic validators exist." Evidence: .harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md:1302.
- "Codex can then correlate failures, patch the owner module, rerun the workload, and improve the skill through eval feedback." Evidence: .harness/implementation-notes/2026-05-19-deep-module-plan.html:987-1016.

## Final Assessment

### Strongest Ideas

- Codex runtime as ABI, with target-specific proof.
- Doctor output as a structured decision packet.
- Classified blocked state.
- Generated projection repair through repo-owned commands.
- Compatibility snapshots before broad autonomy.
- Local evidence services for patch/rerun/promotion loops.

### Weakest Areas

- Some service boundaries still appear to have grown from CLI modules rather than dedicated architecture layers.
- Preview commands are currently modeled parity, not full live runtime parity.
- Research artifacts can become over-detailed enough to blur into implementation authority unless adoption is explicit.
- Review and tracker state require live verification to avoid stale conclusions.

### Most Reusable Concepts

- Runtime-target proof gates.
- Next-command decision with precedence reasons.
- Generated artifact ownership manifests.
- Public-output compatibility snapshots.
- Slice-scoped implementation governance.
- Review artifact verification.
- Local evidence query/correlate/patch/rerun loop.

### Highest-Leverage Opportunities

1. Make every public ask skills command schema-backed and snapshot-backed.
2. Add live or modeled Codex loader/render/config/injection parity commands with explicit blocked checks.
3. Extract skills SDK service boundaries from command implementation modules.
4. Add conformance evidence directories with JSONL event streams.
5. Add generated artifact manifests and pre-commit generated ownership checks.

### Most Important Risks

- False success from proving the wrong runtime.
- Manual edits to generated surfaces.
- Overclaiming preview parity.
- Compatibility regression from simplification.
- Unclassified blocked validation.
- Stale review/tracker state treated as current truth.

### Immediate Implementation Candidates

- Add a closeout linter that rejects unclassified non-zero validation outcomes.
- Add snapshot fixtures for skills proof, skills doctor, skills package, and skills handles.
- Add generated ownership metadata to projection sync output.
- Add an ask skills conformance run evidence-dir skeleton that records JSONL command evidence.
- Add a research adoption marker so deep research recommendations remain advisory until explicitly promoted.

