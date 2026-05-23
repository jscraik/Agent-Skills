# Skills SDK Oagen Architecture Analysis

Date: 2026-05-22

Primary external repositories inspected:

- workos/oagen
- workos/oagen-emitters
- workos/openapi-spec

Primary article inspected:

- WorkOS, Handwritten SDKs Are Dead, 2026-05-08

Local Skills SDK planning surfaces inspected:

- .harness/linear/2026-05-11-agent-skills-he-product-front-door-runtime-contract-linear-plan.md
- .harness/linear/2026-05-17-agent-skills-skill-sdk-doctor-contract-linear-plan.md
- .harness/implementation-notes/2026-05-21-agent-skills-jsc-329-goal-kickoff.html
- Docs/goals/jsc-329-skill-sdk-doctor-contract
- Docs/goals/jsc-329-skill-sdk-doctor-contract/notes/2026-05-22-gap-analysis.md

## Executive Summary

No. We have not yet extracted and operationalized every high-leverage pattern needed for a full, sustainable Skills SDK implementation.

The current JSC-329 gap analysis correctly added the need for a normalized Skills SDK IR and emitters. That is the right direction, but the WorkOS Oagen architecture shows that IR plus emitters is only the center of a larger apparatus. A sustainable generator needs versioned IR, pure emitter boundaries, operation or command resolution, generated artifact manifests, public-surface compatibility snapshots, smoke verification, staleness checks, ownership boundaries between generated and human-maintained files, dependency-layer enforcement, and AI workflows constrained by deterministic evidence.

The Skills SDK is ready for a bounded prototype around the doctor contract and one or two representative skills. It is not ready for broad autonomous generation across skills, docs, runtime cards, deep modules, command metadata, and compatibility surfaces until the P0 systems in this document exist.

Highest-risk blind spots:

- The current plan names IR and emitters, but does not yet define a versioned SkillSdkIR contract with exhaustive handling rules.
- The current plan does not yet require a generated artifact manifest with input hashes, emitter versions, generated file ownership, and prune semantics.
- The current plan does not yet define a compatibility snapshot and diff system for the public Skills SDK surface: CLI JSON, schemas, command metadata, runtime cards, deep module paths, docs anchors, lifecycle events, and skill handles.
- The current plan does not yet separate parser, normalizer, IR, emitter, writer, verifier, and AI-assisted repair into enforced dependency layers.
- The current plan does not yet define AI-safe generation boundaries. AI can assist emitter scaffolding, migration notes, classification, and repair proposals, but deterministic validators must own truth, compatibility, and release decisions.
- The current plan does not yet include live-surface adoption policy for generated versus hand-maintained Skills SDK artifacts.
- The current plan does not yet include a coverage matrix equivalent to Oagen's SDK validation matrix, so missing deep modules, docs, package surfaces, and command contracts can be mislabeled as complete.

Strongest reusable patterns from WorkOS:

- A stable intermediate representation as the only contract between source parsing and language or artifact-specific emitters.
- Pure emitters that return generated files and avoid filesystem side effects.
- Runtime policy modeled in IR instead of being hardcoded into templates.
- Operation resolution before rendering, so naming and mounting are deterministic and shared.
- Consumer-owned interpretation config for hints, overrides, compatibility approvals, and spec-specific policy.
- Manifest-backed provenance and pruning.
- Baseline versus candidate compatibility snapshots.
- Smoke tests for behavioral correctness, separate from public-surface compatibility checks.
- External emitter plugin packages that register emitters, extractors, and smoke runners.
- AI workflows that consume deterministic diffs and compatibility signals rather than replacing them.

The WorkOS article reinforces the repo evidence: the source fixes the API surface, the IR is the language-independent state, emitters are translators, and AI is bounded by the spec plus persistent skills and conventions. The article is especially relevant to Skills SDK because it frames high-quality SDKs as agent-usable systems: method signatures, parameter descriptions, return types, and docstrings all trace back to the same source, so humans and AI agents share one coherent conceptual model.

Immediate next steps:

1. Define SkillSdkIR as a versioned schema and typed module.
2. Build a parser and normalizer that produce SkillSdkIR from canonical skills, command metadata, schemas, goal notes, and runtime contracts.
3. Implement pure emitters for doctor JSON/schema, docs/runtime cards, command metadata, and deep module skeletons.
4. Add a generated manifest with input hashes, emitter versions, file ownership, and prune policy.
5. Add public-surface compatibility extraction and diffing.
6. Add representative smoke checks for skills doctor, package/readiness, Context7, and at least one non-Context7 skill.
7. Add dependency-layer tests that prevent parser/emitter/writer/runtime coupling.
8. Add an AI-assisted generation workflow that is advisory unless deterministic validators pass.

## Core Architectural Patterns

### Pattern: Source To IR To Pure Emitters

Description: A canonical source is parsed and normalized into a stable intermediate representation. Emitters consume only the IR and produce generated files.

Why it exists: OpenAPI specs contain references, naming ambiguity, schema composition, vendor extensions, and operation grouping concerns. Skills contain similar ambiguity across SKILL.md, command metadata, schemas, runtime cards, plugin manifests, generated projections, goal boards, and docs.

Problem solved: Emitters do not need to rediscover domain semantics. They render from an already-normalized contract.

WorkOS implementation: Oagen describes its core as parsing an OpenAPI spec into a typed ApiSpec IR, then letting emitters turn that IR into files. Evidence: workos/oagen README.md lines 7-9. Its architecture guide defines IR as the contract between parser and emitters. Evidence: workos/oagen docs/architecture/ir-types.md line 5.

Skills SDK adaptation: Define SkillSdkIR with skill identity, canonical source path, runtime card, command surface, schemas, validation checks, lifecycle events, package metadata, deep module ownership, emitted docs, compatibility surface, generated artifact ownership, and provenance.

Risks and tradeoffs: A weak IR becomes another lossy summary layer. A too-large IR becomes a second application model. Keep it stable, versioned, discriminated, and traceable to source evidence.

Implementation priority: P0.

### Pattern: Runtime Behavior As IR Policy

Description: Runtime behavior belongs in a language-agnostic policy object that emitters interpret.

Why it exists: SDK behavior such as retry, errors, pagination, telemetry, idempotency, and request guards must remain coherent across languages.

Problem solved: Emitters do not invent runtime policy independently.

WorkOS implementation: SdkBehavior captures retry, errors, telemetry, pagination, idempotency, logging, User-Agent, request guards, and timeout defaults. Evidence: workos/oagen src/ir/sdk-behavior.ts lines 153-183. The README says emitters should read ctx.spec.sdk instead of hardcoding behavior. Evidence: workos/oagen README.md lines 145-155.

Skills SDK adaptation: Add SkillSdkBehavior for readiness status precedence, tolerated environmental differences, next-command semantics, projection policy, package provenance policy, eval promotion rules, lifecycle event semantics, and generated artifact ownership.

Risks and tradeoffs: Policy in templates creates drift. Policy in IR requires careful schema evolution.

Implementation priority: P0.

### Pattern: Operation Resolution Before Rendering

Description: Method names, mount points, resource grouping, and collision handling are derived before emitters render files.

Why it exists: Naming is compatibility-sensitive. Each emitter computing names independently creates drift.

Problem solved: Generated surfaces stay coherent across languages and artifacts.

WorkOS implementation: Oagen exposes resolved operations in emitter context. Evidence: workos/oagen README.md lines 179-181. Oagen emitters fail fast on resolved-operation naming collisions. Evidence: workos/oagen-emitters src/shared/resolved-ops.ts lines 4-31.

Skills SDK adaptation: Add command and artifact resolution before emitting: skill handles, command names, schema names, docs anchors, runtime-card IDs, deep-module package names, lifecycle event names, and generated file paths.

Risks and tradeoffs: Resolution rules become compatibility contracts. They need tests and explicit override policy.

Implementation priority: P0.

### Pattern: Consumer-Owned Interpretation Config

Description: The source-owning repository owns interpretation policy, hints, approvals, and compatibility exceptions.

Why it exists: Source semantics often require domain knowledge that generic generators cannot infer safely.

Problem solved: Generator core stays reusable while domain-specific meaning remains local.

WorkOS implementation: openapi-spec owns oagen.config.ts, operation hints, and WorkOS-specific interpretation policy. Evidence: workos/openapi-spec README.md lines 23-26 and oagen.config.ts lines 1-20.

Skills SDK adaptation: Add skills-sdk config or equivalent with handle overrides, command grouping, generated ownership policy, compatibility approvals, representative fixture selection, and migration overlays. Policy must live outside generated manifests.

Risks and tradeoffs: Config can become a landfill. It needs schema validation and concept-first approvals.

Implementation priority: P0.

### Pattern: Manifest-Backed Provenance And Pruning

Description: Generated outputs are accompanied by a manifest recording inputs, generator versions, generated files, and ownership data.

Why it exists: Regeneration must be replayable, reviewable, and safe to prune.

Problem solved: Prevents stale generated files, hidden hand edits, and untraceable output.

WorkOS implementation: .oagen-manifest.json records generated files, input hashes, emitter hashes, config hash, and compatibility schema version. Evidence: workos/oagen docs/core/manifest-schema.md lines 3-43. The manifest explicitly must not contain approvals or policy overrides. Evidence: workos/oagen docs/core/manifest-schema.md lines 69-76.

Skills SDK adaptation: Emit .skills-sdk-manifest.json or a repo-native equivalent for generated docs, schemas, command metadata, runtime cards, fixtures, and deep module skeletons. Include source hashes, IR schema version, emitter versions, config hash, generated file list, ownership class, and prune policy.

Risks and tradeoffs: Manifest pruning can delete user work if ownership is ambiguous. Start with report-only pruning until generated ownership is proven.

Implementation priority: P0.

### Pattern: Baseline Versus Candidate Compatibility

Description: Public API compatibility is enforced by comparing a committed baseline snapshot against a candidate snapshot generated from the current change.

Why it exists: Generated code can silently break users even when tests pass.

Problem solved: Compatibility becomes a deterministic artifact, not a reviewer feeling.

WorkOS implementation: The compat engine compares baseline live SDK snapshots with candidate generated output and classifies breaking, soft-risk, and additive changes. Evidence: workos/oagen docs/core/compatibility.md lines 3-60.

Skills SDK adaptation: Extract snapshots for CLI commands, JSON payloads, schemas, command metadata, docs anchors, skill handles, runtime cards, deep module APIs, lifecycle events, and package provenance fields.

Risks and tradeoffs: Snapshot schemas require versioning. Human-authored and generated surfaces must be classified differently.

Implementation priority: P0.

### Pattern: Smoke Verification Separate From Compatibility

Description: Structural public-surface compatibility and behavioral runtime smoke checks are separate gates.

Why it exists: A compatible API shape can still behave incorrectly, and a behaviorally correct runtime can still break public contracts.

Problem solved: The validation system can name the exact failure mode.

WorkOS implementation: Compatibility checks structural public API, while smoke tests verify HTTP behavior. Evidence: workos/oagen docs/core/compatibility.md lines 34-38 and src/verify/run-smoke-check.ts lines 26-81.

Skills SDK adaptation: Keep schema and compat diffs separate from runtime doctor, proof, package, and eval smoke checks. A skills doctor payload validating against schema is necessary but insufficient; runtime proof must still confirm the selected skill can actually satisfy the readiness claim.

Risks and tradeoffs: More gates create more evidence to maintain. The payoff is clearer blocker classification.

Implementation priority: P0.

### Pattern: External Emitter Plugin Bundle

Description: Emitters, extractors, and smoke runners live in a package separate from the generator core and are registered by plugin.

Why it exists: Core generator contracts should be stable while output-specific implementations evolve independently.

Problem solved: Language or artifact-specific complexity does not leak into the generator core.

WorkOS implementation: oagen-emitters registers emitters, compatibility extractors, and smoke runner paths through workosEmittersPlugin. Evidence: workos/oagen-emitters README.md lines 7-22 and src/plugin.ts lines 1-51.

Skills SDK adaptation: Split Skills SDK core from emitters for doctor schema, docs, command metadata, package metadata, deep modules, eval fixtures, and runtime cards. The repo can start monorepo-local, but the dependency boundary should be enforced from the beginning.

Risks and tradeoffs: Plugin boundaries add ceremony. They also prevent irreversible coupling.

Implementation priority: P1.

### Pattern: Generated Versus Hand-Maintained Live Surface

Description: The generator inspects the target SDK and decides which files or declarations are managed, adopted, protected, or human-owned.

Why it exists: Mature SDKs contain a mix of generated and hand-written code.

Problem solved: Regeneration does not overwrite protected human work, and generated code does not leave obsolete artifacts behind unnoticed.

WorkOS implementation: The Node emitter uses a live-surface snapshot and policies for protected files, autogen headers, hand-written files, brand-new paths, managed directories, adopted files, and owned directories. Evidence: workos/oagen-emitters src/node/index.ts lines 96-120 and src/node/live-surface.ts lines 5-113.

Skills SDK adaptation: Classify Skills SDK files as canonical hand-authored sources, generated projections, adopted generated artifacts, protected docs, runtime-owned outputs, and external plugin mirrors. Enforce this in the writer and manifest.

Risks and tradeoffs: File ownership rules can become path-glob fragile. Prefer explicit headers and manifest evidence.

Implementation priority: P1.

### Pattern: Dependency Layers Enforced By Tests

Description: Repository architecture is represented as an allowed import matrix and checked by tests.

Why it exists: Generator maintainability depends on one-way dependencies.

Problem solved: Parser, IR, engine, diff, compat, CLI, and emitters cannot quietly entangle.

WorkOS implementation: Oagen documents one-way dependency layers and enforces them with an architecture test. Evidence: workos/oagen docs/architecture/dependency-layers.md lines 3-71.

Skills SDK adaptation: Enforce one-way layers: source discovery to parser to normalizer to IR to planner to emitter to writer to manifest to compatibility to smoke to CLI. Emitters must not call parser or perform filesystem writes.

Risks and tradeoffs: Layer tests require clear module paths. Add them early while the package is still small.

Implementation priority: P0.

### Pattern: AI As Bounded Accelerator, Not Source Of Truth

Description: AI gets structured deterministic context and returns constrained outputs, while compatibility and release decisions remain validator-owned.

Why it exists: AI is useful for classification, synthesis, migration notes, and emitter scaffolding, but unsafe as the arbiter of public API truth.

Problem solved: AI can help scale generation without weakening governance.

WorkOS implementation: generate-prs.yml feeds AI deterministic Oagen spec diffs, compatibility-breaking flags, truncated SDK diff context, and a tool schema; deterministic fallbacks and safety nets override or repair AI output when needed. Evidence: workos/openapi-spec .github/workflows/generate-prs.yml lines 198-224, 325-351, and 422-439.

Skills SDK adaptation: Use AI for emitter design proposals, migration notes, compatibility repair suggestions, review summaries, and change classification. Block AI from inventing IR contracts, declaring compatibility, bypassing smoke checks, or writing runtime projections without manifest and validator proof.

Risks and tradeoffs: AI workflows can look authoritative because they produce polished text. Every AI conclusion must cite deterministic evidence.

Implementation priority: P0.

## IR Architecture Analysis

Oagen's IR is not a convenience structure. It is the stability boundary that allows many emitters and compatibility systems to operate without reinterpreting the source spec. Its ApiSpec includes services, operations, models, enums, auth, servers, and SDK behavior. Evidence: workos/oagen docs/architecture/ir-types.md lines 15-48. Its type system is a discriminated union over primitives, arrays, models, enums, unions, nullable values, literals, and maps. Evidence: workos/oagen docs/architecture/ir-types.md lines 55-67. Schema composition is represented explicitly with union metadata and composition kind. Evidence: workos/oagen docs/architecture/ir-types.md lines 107-118. The implementation uses assertNever to force compile-time handling of new IR variants. Evidence: workos/oagen src/ir/types.ts lines 232-253.

The equivalent Skills SDK IR must be a long-term contract, not a generated report. It should include:

- irVersion: version of the Skills SDK IR schema.
- sourceSet: canonical files and hashes used to build the IR.
- skillIdentity: handle, display name, root, owner, plugin source, package source, runtime projection source.
- runtimeCard: command hints, tool expectations, compatibility posture, activation guidance, and context dependencies.
- commandSurface: public ask commands, JSON mode, robot mode, help text, parser metadata, guided errors, and next-command semantics.
- doctorSurface: status precedence, checks, schema references, tolerated environmental differences, runtime blocker classes, and proof linkage.
- packageSurface: package provenance, install source, DotSlash or wrapper entrypoints, bundled resources, and eval metadata.
- deepModules: doctor, package doctor, profiles, events, routing, compatibility checks, and lifecycle services.
- schemas: public JSON schemas and internal validation schemas.
- docsSurface: generated docs, anchors, examples, runtime cards, implementation notes, and readme snippets.
- validationSurface: focused tests, smoke checks, snapshot tests, eval gates, and closeout validators.
- compatibilitySurface: public names, output fields, schema paths, lifecycle events, docs anchors, and migration approvals.
- generationOwnership: generated, adopted, protected, hand-authored, runtime projection, and external mirror classifications.
- provenance: source hash, config hash, emitter version, generated artifact manifest ID, and validation receipt IDs.

Normalization must resolve:

- Skill handles and aliases into canonical identities.
- Repo-owned canonical sources versus generated projections.
- Runtime-card claims versus live command and schema evidence.
- Command parser, help, metadata, and guided-error parity.
- Doctor status precedence and next-command behavior.
- Deep module names, owners, and package paths.
- Public schema references and schema version ownership.
- Compatibility-sensitive names before emitters run.

The IR is stable enough only if new variants fail loudly. Skills SDK should copy Oagen's exhaustive handling posture: adding a new surface, status type, artifact ownership class, or schema-reference type must fail emitter tests until every affected emitter handles it.

AI-generation implication: the IR narrows the search space. AI should never be asked to infer whether a skill is package-ready from raw docs and scattered tests. It should receive a validated IR and propose bounded changes against it.

## Generator Pipeline Analysis

The full Skills SDK pipeline should be:

canonical skills, command metadata, schemas, goals, docs, runtime evidence
-> parse
-> normalize
-> validate SkillSdkIR
-> resolve commands, names, paths, docs anchors, lifecycle events
-> run compatibility preflight against baseline when available
-> emit generated files through pure emitters
-> write files through ownership-aware writer
-> update generation manifest
-> extract candidate public surface
-> run compatibility diff
-> run smoke/runtime checks
-> produce diagnostics and implementation notes

Mandatory stages:

- Parse canonical sources.
- Normalize into SkillSdkIR.
- Validate IR schema and invariants.
- Resolve compatibility-sensitive names.
- Emit with pure emitters.
- Write through generated ownership policy.
- Record manifest provenance.
- Extract candidate compatibility surface.
- Run compatibility diff and focused smoke checks.

Optional stages:

- AI-assisted emitter scaffolding.
- AI-assisted migration notes.
- AI-assisted compatibility repair suggestions.
- Overlay retry loops for preserving existing names.
- PR comment generation and release-note classification.

Governance-critical stages:

- IR validation.
- Compatibility baseline extraction.
- Manifest creation.
- Ownership-aware writing and pruning.
- Smoke checks.
- Staleness detection.
- Layer enforcement.

Oagen's parser pipeline bundles refs, transforms specs, extracts schemas and operations, normalizes inline models, collects enums, validates references, and defaults SDK behavior. Evidence: workos/oagen src/parser/parse.ts lines 45-120. Its architecture docs separate parser, emitter orchestration, writer, and diff engine. Evidence: workos/oagen docs/architecture/pipeline.md lines 29-110. The orchestrator carries prior manifests, target paths, API surface, hints, overlays, and emitter options into context. Evidence: workos/oagen src/engine/orchestrator.ts lines 11-48. Generation then builds files, operations maps, reachability filters, and headers before writing. Evidence: workos/oagen src/engine/generate-files.ts lines 129-178.

Skills SDK replayability requirements:

- Input hashes for skill sources, schemas, docs, goal notes, command metadata, and config.
- IR schema version.
- Emitter versions.
- Config hash.
- Generated file list.
- Prior manifest path.
- Baseline compatibility snapshot path.
- Candidate compatibility snapshot path.
- Smoke command evidence.
- Validation command evidence.

Stale-state risks:

- Generated docs can claim a command exists after the parser changes.
- Runtime-card hints can drift from command metadata.
- Doctor schema references can advertise contracts that have no schema.
- Deep modules can be described in plans but absent from code.
- Compatibility-sensitive names can be renamed by cleanup work.
- Existing generated projections can persist after source removal.

Skills SDK needs staleness checks equivalent to Oagen's non-additive change detection. Oagen already notes that additive-only writing leaves stale dead code behind and therefore needs a staleness check. Evidence: workos/oagen docs/architecture/non-additive-changes.md lines 3-10. Skills SDK has the same risk across docs, runtime projections, and command metadata.

## Emitter Architecture Analysis

Oagen's emitter contract is deliberately narrow. Emitters receive ApiSpec plus context and return GeneratedFile arrays. Evidence: workos/oagen docs/architecture/emitter-contract.md lines 11-24. Generated files carry path, content, skip behavior, header placement, and integration target metadata. Evidence: workos/oagen docs/architecture/emitter-contract.md lines 30-36. Emitter context includes namespace, spec, output directory, API surface, overlays, resolved operations, model hints, target directory, emitter options, and prior manifest paths. Evidence: workos/oagen src/engine/types.ts lines 16-43.

The most important emitter rules are reusable:

- Emitters are pure functions.
- Empty input should produce empty output.
- Namespace and naming must be threaded through context.
- Inapplicable emitter methods return empty arrays.
- Generators should be composable.
- New IR variants must be handled explicitly.

For Skills SDK, emitters should be split by artifact family:

- doctor-schema-emitter: emits skill-doctor schema and doctor payload schema fixtures.
- doctor-runtime-emitter: emits doctor contract fixtures, status precedence tests, and next-command expectations.
- command-surface-emitter: emits parser metadata, help metadata, guided-error fixtures, and command docs.
- runtime-card-emitter: emits skill runtime cards and agent-facing usage hints from IR.
- deep-module-emitter: emits service module skeletons for doctor, package doctor, profiles, events, routing, compatibility, and lifecycle commands.
- docs-emitter: emits generated docs, anchors, examples, and implementation-note snippets.
- package-metadata-emitter: emits package provenance contracts, install context, bundled resources metadata, and eval metadata.
- compat-snapshot-emitter: emits or updates baseline and candidate snapshot schemas.

Shared emitter primitives:

- Skill handle resolver.
- Command name resolver.
- Docs anchor resolver.
- Schema name resolver.
- Runtime status planner.
- Next-command planner.
- Ownership classifier.
- Generated header utility.
- Manifest builder.
- Snapshot extractor helpers.
- Markdown rendering helpers.
- JSON schema rendering helpers.

Emitter isolation rules:

- Emitters must not parse source files.
- Emitters must not inspect git state.
- Emitters must not write to disk.
- Emitters must not call live ask commands.
- Emitters must not fetch network resources.
- Emitters must not decide compatibility policy.
- Emitters may render from IR, context, resolved names, overlays, and validated config.

Anti-slop generation strategies:

- Require a short design note for each emitter before implementation.
- Add fixtures for every emitted artifact family.
- Snapshot emitted files in stable, normalized form.
- Add exact generated header and manifest references.
- Add line-of-ownership tests that reject unmanifested generated files.
- Add command metadata parity tests for parser, help, related commands, and guided errors.
- Add one second representative skill fixture beyond Context7 to prevent single-example overfitting.

AI-safe boundaries:

- Safe: propose emitter structure, sketch templates from existing idioms, suggest tests, classify diff summaries, write migration explanations.
- Unsafe: decide IR shape without review, infer runtime readiness from prose, mutate generated projections directly, approve breaking changes, skip fixture updates, or rewrite compatibility baselines without explicit approval.

## Compatibility & Migration Analysis

Oagen separates public API compatibility from smoke behavior. Baseline snapshots represent the live SDK surface. Candidate snapshots represent generated output. Diffs classify breaking, soft-risk, and additive changes. Evidence: workos/oagen docs/core/compatibility.md lines 13-60. Oagen's compatibility runner extracts candidate API, filters baseline to spec-derived names, applies language policy, and passes only if no breaking severity remains. Evidence: workos/oagen src/verify/run-compat-check.ts lines 18-55.

Skills SDK needs the same model for non-code and runtime surfaces.

Required Skills SDK compatibility snapshots:

- CLI command names, aliases, parser choices, help text, related commands, and guided error suggestions.
- JSON output shapes for skills doctor, skills prove, skills proof, skills explain, package/readiness commands, and lifecycle commands.
- Public schema file paths and schema versions.
- Doctor status values, check IDs, blocker classes, status precedence, and next-command semantics.
- Runtime card fields consumed by agents.
- Skill handles and aliases.
- Generated docs anchors that agents or users may link to.
- Deep module import paths and service entrypoints.
- Package metadata fields and eval artifact paths.
- Lifecycle event names and payload fields.

Migration workflows needed:

1. Extract current hand-authored public surface.
2. Generate candidate surface from SkillSdkIR.
3. Diff baseline versus candidate.
4. Preserve names through overlays where public compatibility matters.
5. Classify changes as breaking, soft-risk, additive, or internal.
6. Require explicit approval for breaking or soft-risk changes.
7. Commit manifest and compatibility snapshot changes together.
8. Run smoke checks against representative skills.

Overlay repair loop:

Oagen has a bounded overlay retry loop with patchable changes, max retries, stall detection, cleanup of generated files, and regeneration. Evidence: workos/oagen src/verify/run-overlay-retry-loop.ts lines 61-148. Skills SDK should adapt this for compatibility-preserving renames and docs-anchor preservation, but only after baseline extraction exists. Overlay repair cannot be the first line of defense.

Staleness:

Skills SDK needs checks for stale docs and generated artifacts. Examples:

- A doc claims skills package is part of the current contract but no command or schema exists.
- A runtime card mentions a deep module that has no service module.
- A schema reference appears in doctor output with no concrete schema and no tracked deferral.
- A generated command fixture persists after the command is removed.
- A goal note labels required full implementation as a later slice without scope authority.

Compatibility policy location:

- Policy belongs in Skills SDK config and reviewed approvals.
- Provenance belongs in the generated manifest.
- Evidence belongs in validation receipts and implementation notes.
- Generated artifacts should not carry policy exceptions.

## AI-Assisted Generation Analysis

The WorkOS pattern is not "AI generates everything." It is "deterministic systems make generation safe enough for AI to assist around the edges."

Where AI adds leverage:

- Extracting architecture patterns from existing emitters.
- Scaffolding a new emitter from a design note and IR examples.
- Suggesting compatibility overlays when names drift.
- Summarizing generated diffs for reviewers.
- Classifying behavior-change notes from deterministic diff summaries.
- Writing migration guides from verified compatibility reports.
- Explaining smoke or compatibility failures.

Where AI introduces risk:

- Inferring source truth from prose rather than IR.
- Smoothing over absent runtime behavior.
- Treating a generated document as proof of an implemented command.
- Accepting a compatibility break because the generated code looks cleaner.
- Creating broad abstractions before a representative fixture proves the seam.
- Rewriting baselines to match candidate output.

Deterministic systems required before AI-assisted generation is safe:

- Versioned SkillSdkIR.
- Schema validation for IR and public outputs.
- Pure emitter contract.
- Generated manifest.
- Compatibility snapshots and diff classifications.
- Smoke checks.
- Layer enforcement tests.
- Coverage matrix.
- Explicit ownership policy.
- Validation receipts tied to generated artifacts.

How WorkOS constrains hallucination risk:

- AI receives structured spec diff and compatibility-breaking signals.
- AI output is constrained by a tool schema.
- Diffs are truncated to fit context, but authoritative machine summaries remain present.
- Deterministic safety nets promote breaking changes when compat says they are breaking.
- Deterministic fallback creates a usable classification if AI fails.

Skills SDK should follow the same posture. AI can propose, classify, explain, and scaffold. Validators must decide.

The WorkOS article makes this boundary explicit in plain terms: Claude is not the SDK source of truth and does not invent API behavior. The source fixes what exists, the IR makes that source clean and typed, emitters encode target conventions, and skills preserve institutional knowledge about naming, errors, pagination, docstrings, and tests. For Skills SDK, the equivalent is: canonical skill sources and runtime evidence fix what exists; SkillSdkIR makes it coherent; emitters encode docs, schemas, command metadata, package metadata, and deep module idioms; and Codex skills can assist only inside those constraints.

The agent-facing quality point is also important. WorkOS argues that generated SDKs with comprehensive, accurate docstrings are more useful to AI coding agents than inconsistent hand-maintained SDKs, because signatures, parameter descriptions, and return types trace to the same source. Skills SDK should treat agent usability as a first-class compatibility target: generated runtime cards, command schemas, doctor payload fields, and docs must all describe the same model.

## Missing Systems In Skills-SDK

### Missing System: Versioned Skills SDK IR

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Add SkillSdkIR as a typed contract plus JSON schema. Include skill identity, runtime card, command surface, doctor surface, package surface, deep modules, docs, schemas, validation, compatibility, ownership, and provenance.

Suggested tooling: Add an extraction command or internal parser module that can emit the IR for one skill and for the repository.

Suggested validation strategy: Schema validation, discriminated union exhaustive tests, representative fixtures for Context7 and a second skill, and a golden normalized IR snapshot.

### Missing System: Parser And Normalizer Layer

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Separate discovery, parsing, normalization, and validation. Discovery finds canonical sources. Parsing reads files and command metadata. Normalization resolves handles, paths, commands, status semantics, schema references, and ownership into IR.

Suggested tooling: Internal module with one public entrypoint and a CLI wrapper.

Suggested validation strategy: Unit tests for source discovery, path ownership, command parity, and schema-reference normalization.

### Missing System: Pure Emitter Contract

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Define SkillSdkEmitter with methods for artifact families and a context object carrying resolved names, config, compatibility overlays, and prior manifest data. Emitters return generated files.

Suggested tooling: Emitter test harness with snapshots and generated header checks.

Suggested validation strategy: Test that emitters do not perform I/O, do not call live commands, and handle empty inputs predictably.

### Missing System: Generated Manifest And Ownership Policy

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Add a manifest recording source hashes, IR version, config hash, emitter versions, generated files, ownership class, and prior generated paths.

Suggested tooling: Writer module with report-only prune mode, strict mode, and manifest validation.

Suggested validation strategy: Reject generated files missing manifest entries, reject manifest policy exceptions, and detect hand edits to generated artifacts.

### Missing System: Public-Surface Compatibility Snapshots

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Baseline and candidate snapshots for CLI, JSON, schema, docs, runtime-card, lifecycle, deep-module, and package metadata surfaces.

Suggested tooling: skills sdk compat extract, skills sdk compat diff, and skills sdk compat summary.

Suggested validation strategy: Breaking changes fail unless explicitly approved in config. Soft-risk changes require evidence. Additive changes pass with report output.

### Missing System: Smoke Runtime Checks

Severity: Critical.

Implementation priority: P0.

Suggested architecture: Smoke runners for representative skill flows: doctor, proof, explain, package/readiness, and generated docs/runtime-card checks.

Suggested tooling: skills sdk verify --smoke plus matrix support for selected fixtures.

Suggested validation strategy: Distinguish schema pass, compatibility pass, runtime pass, environment blocker, and projection blocker.

### Missing System: Dependency-Layer Enforcement

Severity: High.

Implementation priority: P0.

Suggested architecture: Define allowed import layers for discovery, parser, normalizer, IR, planner, emitters, writer, compat, smoke, CLI, and AI helpers.

Suggested tooling: Architecture test that scans imports or module boundaries.

Suggested validation strategy: Fails when emitters import parser, writer, CLI, live runtime probes, or network helpers.

### Missing System: Coverage Matrix

Severity: High.

Implementation priority: P1.

Suggested architecture: A matrix mapping planned Skills SDK surfaces to live code, emitted artifacts, schemas, tests, smoke checks, and compatibility snapshots.

Suggested tooling: Machine-readable coverage file plus generated markdown report.

Suggested validation strategy: Fail closeout when a required surface is claimed complete but has no implementation and validation evidence.

### Missing System: Live-Surface Adoption Policy

Severity: High.

Implementation priority: P1.

Suggested architecture: Classify files and declarations as canonical source, generated, adopted generated, protected hand-authored, runtime projection, or external mirror.

Suggested tooling: Ownership classifier and writer integration.

Suggested validation strategy: Generated writer refuses to overwrite protected files and flags stale generated files.

### Missing System: Staleness Detection

Severity: High.

Implementation priority: P1.

Suggested architecture: Compare prior manifest, current IR, docs claims, command metadata, and schema references.

Suggested tooling: skills sdk verify --staleness.

Suggested validation strategy: Report stale claims, stale generated files, stale schema references, and missing deep modules as closeout blockers when they affect claimed completion.

### Missing System: AI Governance Workflow

Severity: High.

Implementation priority: P1.

Suggested architecture: AI helpers receive IR, compat reports, smoke reports, and bounded task schemas. AI outputs become proposals until validators pass.

Suggested tooling: skills sdk ai classify-change, skills sdk ai propose-overlay, and skills sdk ai scaffold-emitter behind validation gates.

Suggested validation strategy: AI output cannot update baselines, approve breaking changes, or write generated artifacts without deterministic reruns.

### Missing System: Migration Playbook

Severity: Medium.

Implementation priority: P2.

Suggested architecture: A documented path for moving hand-authored Skills SDK surfaces into generated ownership: extract baseline, generate candidate, diff, overlay names, smoke, commit manifest.

Suggested tooling: Migration command or checklist that produces receipts.

Suggested validation strategy: Requires baseline and candidate artifacts in review notes.

## High-Leverage Adaptations

1. Versioned SkillSdkIR
   - Impact: Very high.
   - Difficulty: Medium.
   - Operational value: Makes scattered skill/runtime/docs evidence machine-checkable.
   - Maintainability value: Prevents emitter-specific reinterpretation.
   - AI-generation safety value: Narrows ambiguity before AI touches artifacts.

2. Pure emitter and writer separation
   - Impact: Very high.
   - Difficulty: Medium.
   - Operational value: Makes generated output replayable and reviewable.
   - Maintainability value: Prevents parser/runtime/write coupling.
   - AI-generation safety value: AI can scaffold emitters without receiving filesystem authority.

3. Manifest-backed provenance
   - Impact: Very high.
   - Difficulty: Medium.
   - Operational value: Names exactly what was generated from which sources.
   - Maintainability value: Enables safe pruning and review.
   - AI-generation safety value: Prevents AI or agents from laundering generated artifacts as hand-authored truth.

4. Compatibility snapshots and diffs
   - Impact: Very high.
   - Difficulty: Medium to high.
   - Operational value: Converts public-surface breaks into deterministic findings.
   - Maintainability value: Protects users and agents consuming stable contracts.
   - AI-generation safety value: Keeps AI classification subordinate to compatibility evidence.

5. Smoke verification matrix
   - Impact: High.
   - Difficulty: Medium.
   - Operational value: Separates runtime failure from schema or docs success.
   - Maintainability value: Prevents one-fixture overfitting.
   - AI-generation safety value: Blocks polished but non-executable generated surfaces.

6. Command and artifact resolution planner
   - Impact: High.
   - Difficulty: Medium.
   - Operational value: Centralizes names, paths, mounts, anchors, and next-command rules.
   - Maintainability value: Reduces repeated command/help/docs drift.
   - AI-generation safety value: Keeps naming deterministic.

7. Dependency-layer enforcement
   - Impact: High.
   - Difficulty: Low to medium.
   - Operational value: Stops architecture drift early.
   - Maintainability value: Keeps future contributors inside a coherent model.
   - AI-generation safety value: Prevents generated code from growing hidden side effects.

8. AI-bounded generation workflow
   - Impact: High.
   - Difficulty: Medium.
   - Operational value: Uses AI where it helps without making it the source of truth.
   - Maintainability value: Keeps workflows explainable and replayable.
   - AI-generation safety value: Makes hallucination risk explicit and validator-contained.

## What NOT To Copy

- Do not copy WorkOS's HTTP/API-specific domain model wholesale. Skills SDK needs skill/runtime/docs/package/eval semantics, not OpenAPI endpoint semantics.
- Do not start with WorkOS's full multi-language matrix. Start with artifact-family emitters for the doctor contract, command metadata, docs/runtime cards, and one deep module surface.
- Do not copy Node-specific live-surface heuristics directly. Skills SDK should prefer explicit generated headers and manifests before path-glob inference.
- Do not copy release automation before local replayability is stable. PR automation should follow IR, manifest, compat, and smoke gates.
- Do not let compatibility overlays become the primary design mechanism. First define stable naming and ownership rules.
- Do not copy AI changelog automation before deterministic compatibility reports exist.
- Do not accept deferred rename detection as acceptable for Skills SDK. Skills SDK must classify renames, preserve aliases, or require explicit compatibility approval.
- Do not use generated docs as proof of runtime behavior. Runtime evidence must come from commands, smoke checks, schemas, and compatibility extraction.
- Do not move policy into generated manifests. Keep policy in reviewed config and evidence in receipts.

## Final Readiness Assessment

What we understand well:

- Why a stable IR is essential.
- Why emitters must be pure and isolated.
- Why runtime behavior should be modeled as policy instead of template constants.
- Why compatibility snapshots are separate from smoke tests.
- Why generated artifacts need manifest provenance.
- Why AI should operate only inside deterministic boundaries.

What we only partially understand:

- The exact final SkillSdkIR field set and versioning policy.
- The complete public-surface taxonomy for Skills SDK compatibility.
- The ownership boundary between hand-authored skill docs, generated runtime cards, generated projections, and plugin mirrors.
- The right first set of representative fixtures beyond Context7.
- The migration plan for existing hand-authored surfaces into generated ownership.

What still requires research or prototype work:

- A minimal SkillSdkIR extraction prototype over Context7 and one second skill.
- A doctor-schema and docs/runtime-card emitter pair.
- A generated manifest and report-only stale artifact detector.
- A public-surface compatibility snapshot schema.
- A smoke matrix that distinguishes contract failure, runtime blocker, projection blocker, and environment blocker.
- Layer enforcement tests for the eventual Skills SDK package layout.

What should be prototyped first:

1. SkillSdkIR extraction for Context7 and one second representative skill.
2. Pure emitters for doctor schema fixture and runtime-card/docs output.
3. Manifest-backed write in report-only prune mode.
4. Compatibility extraction for skills doctor JSON shape, schema refs, command metadata, and docs anchors.
5. Smoke verification for skills doctor, skills proof, and generated runtime-card references.

Dangerous architectural decisions that remain open:

- Whether Skills SDK treats docs as source, generated output, or mixed ownership.
- Whether deep modules are generated skeletons, hand-authored services, or generated adapters over hand-authored services.
- How compatibility approvals are represented and reviewed.
- How aliases and renamed skill handles are preserved.
- How runtime projection drift is classified when the repo source is correct but user runtime is stale.
- How much AI scaffolding is allowed before a deterministic emitter harness exists.

Final verdict: Skills SDK is not ready for broad full implementation yet. It is ready for a strict implementation-readiness prototype that builds the missing P0 systems first: versioned IR, parser/normalizer, pure emitter contract, manifest/provenance, public-surface compatibility diffing, smoke verification, dependency-layer enforcement, and AI-governed generation boundaries. Broad autonomous Skills SDK generation becomes safe only after those systems exist and produce repeatable evidence.
