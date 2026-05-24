---
schema_version: 1
artifact_id: he-plan-2026-05-22-jsc-351-agent-skills-codex-abi-conformance
artifact_type: he-plan
canonical_slug: jsc-351-agent-skills-codex-abi-conformance
title: JSC-351 Agent Skills Codex ABI Conformance Plan
harness_stage: he-plan
status: ready_for_he_work
date: 2026-05-22
origin: .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
source_spec: .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
risk: high
depth: deep
ui: false
traceability_required: true
linear_mutation_status: already_linked
linear_status: In Progress
linear_issue: JSC-351
linear_issue_url: https://linear.app/jscraik/issue/JSC-351/agent-skills-make-skills-sdk-prove-codex-abi-conformance
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

# JSC-351 Agent Skills Codex ABI Conformance Plan

## Command Summary

BLUF: This plan gives the implementing agent, developer, and reviewer a sequenced path for making agent-skills prove Codex ABI conformance before broader Skills SDK work expands. It matters because a false pass from .agents readiness would let the SDK claim runtime parity while Codex itself could still fail to load, render, invoke, or validate the same skill package. The immediate risk is trust-boundary drift, so the first work is runtime-targeted proof, doctor Codex parity, generated command-handle enforcement, and deterministic schema-backed failures.

Decision Needed: Confirm the intended live Linear project for JSC-351 through JSC-356. The PU-008 refresh found live cycle assignment on the parent and child issues, so closeout must report cycle truth separately from unresolved project ownership.

Top Risks: .agents readiness can mask absent Codex readiness; generated command handles can drift without blocking closeout; preview commands can overclaim parity without Codex source or fixture identity.

Next Action: Complete PU-008 by refreshing Linear, PR, review-thread, and validation evidence, then report any remaining owner decisions without claiming unsupported final completion.

## Objective

Turn the canonical JSC-351 specification into an ordered implementation plan that can be executed safely across the live Linear child issues.

The first implementation slice is JSC-352. It must close the false-success boundary where agent-skills runtime checks can pass because .agents is ready while Codex-native proof remains absent. Later slices add the package, parity preview, service boundary, conformance, and governance layers needed for the Skills SDK to act as a Codex ABI conformance layer.

## Source Contract

| Source | Status | Use In This Plan |
|---|---:|---|
| .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md | canonical | Requirements, acceptance IDs, Linear tree, validation gates, rollback expectations |
| .harness/research/audits/2026-05-22-evidence-led-codebase-gap-audit.md | supporting evidence | Prioritized gap framing and Codex ABI risk basis |
| .harness/linear/2026-05-22-agent-skills-codex-abi-conformance-linear-plan.md | supporting evidence | Child issue decomposition and tracker handoff context |
| Infrastructure/bin/ask | runtime source | CLI parser and command dispatch truth |
| Infrastructure/scripts/lib/ask/commands/skills_impl.py | runtime source | Skills proof, doctor, package, handles, and current readiness aggregation |
| Infrastructure/scripts/lib/ask/commands/repo_impl.py | runtime source | Repo doctor gate surface |
| Infrastructure/tests/test_ask_skills_doctor.py | validation source | Current doctor contract test and schema-validation weakness |

## Review Hardening Delta

| Review Finding | Classification | Plan Change | Spec Change |
|---|---|---|---|
| Doctor next-command precedence existed only as a spec handoff sentence, not as a formal work item or acceptance gate. | fixable now | PU-001 and PU-003 now include next-command precedence implementation and fixture coverage. | FR-014, SA-011, and the doctor next-command contract were added to the spec. |
| The plan named implementers and reviewers in prose but did not assign decision and release ownership in a dedicated section. | fixable now | Added an Ownership section with decision, implementation, review, release, and tracker ownership. | Existing spec authority table already covers this; no further spec change needed. |
| Artifact validators alone could be mistaken for implementation validation. | fixable now | Added a Definition of Done that separates artifact validation, implementation tests, command smoke checks, tracker evidence, and blocked evidence. | Existing validation plan already distinguishes pre-implementation blockers; no further spec change needed. |

## Evidence Classification

| Claim | Classification | Evidence | Risk If Wrong | Required Action |
|---|---|---|---|---|
| The plan and associated spec are canonical local artifacts for JSC-351. | verified | Frontmatter paths and matching JSC-351 metadata in this plan and spec. | Low | Keep artifact identity and traceability validators green. |
| Current ask parser lacks --runtime-target, --codex-parity, load-preview, render-preview, config explain, and conformance run. | verified from source inspection before plan creation | Infrastructure/bin/ask parser evidence captured in the spec. | Medium | Recheck source before implementing each command because parser state can drift. |
| Doctor schema validation currently returns early when jsonschema is unavailable. | verified from source inspection before plan creation | Infrastructure/tests/test_ask_skills_doctor.py evidence captured in the spec. | High | PU-003 must make schema validation deterministic or explicitly blocked. |
| Live Linear issues exist; current refresh shows JSC-351 through JSC-356 in the JSC team with cycleId `4a0b5dca-7936-482b-a46c-c55c33069f9d`; active project assignment remains unproven by this artifact. | verified live on 2026-05-24, drift-prone | Linear MCP get_issue for JSC-351 through JSC-356. | Medium | Report cycle assignment as runtime truth, keep project assignment unresolved, and avoid further tracker mutation without owner confirmation. |
| Codex parity behavior can be modeled from source or fixtures. | assumption requiring implementation proof | Source and fixture identity are required but not yet selected. | High | PU-005 must choose and report the parity reference before claiming parity. |

## Scope and Boundaries

### In Scope

- Infrastructure/bin/ask command parsing and dispatch for Skills SDK conformance commands.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py while extracting only when a unit requires it.
- Infrastructure/scripts/lib/ask/commands/repo_impl.py for repo doctor enforcement of generated command-handle checks.
- Infrastructure/config/schemas/** for public JSON schemas and package/readiness contracts.
- Infrastructure/tests/** fixtures and focused command tests for proof, doctor, handles, package, preview, and conformance evidence.
- .harness/evidence/** or .harness/research/** evidence artifacts created by conformance commands when a unit explicitly defines them.

### Out of Scope

- Editing .agents/** generated or runtime projection paths as a way to satisfy Codex runtime parity.
- Editing Plugins/cache/**, global Codex config, user home config, or plugin runtime caches.
- Assigning or changing Linear project/cycle metadata while project destination and cycle authority remain unconfirmed.
- Building broad IR/emitter generation infrastructure before the Codex ABI command contracts and validators exist.
- Treating documentation-only proof as implementation completion.

## Authority and Scope Boundary

| Field | Contract |
|---|---|
| requested_depth | Deep implementation with governed slices, runtime truth, and deterministic validation. |
| approved_execution_boundary | Implement the JSC-351 plan/spec in dependency order, starting with PU-001 / JSC-352, using only declared allowed paths per active slice. |
| downscope_authority | The governor may narrow a slice to preserve safety, but may not recategorize required correctness as later scope without spec-owner approval. |
| external_mutation_boundary | Linear, GitHub, CircleCI, CodeRabbit, package registries, user config, and runtime caches require explicit lane evidence and must not be used as speculative side effects. Live tracker state may be read for closeout truth, but project/cycle mutations remain blocked without owner confirmation. |
| freshness_required | Repo state, plan/spec validator state, Linear state, parser/runtime behavior, PR state, and CI state must be refreshed before claims that depend on them. |
| human_acceptance_boundary | Jamie or the delegated maintainer retains authority for project/cycle ambiguity, merge approval, public contract scope changes, and broad SDK architecture decisions. |

## Current State / Evidence

| Finding | Evidence | Plan Impact |
|---|---|---|
| ask skills proof exists, but it does not expose --runtime-target codex, agents, or any. | Infrastructure/bin/ask dispatches proof with only handle=args.handle. | PU-001 must add a target-aware proof contract before later SDK claims can be trusted. |
| Current readiness logic aggregates Codex and .agents readiness into user_runtime_ready. | skills_impl.py computes user_runtime_ready from Codex or .agents readiness. | PU-001 must prove Codex readiness independently and fail closed for Codex-targeted checks. |
| ask skills doctor exists, but --codex-parity is absent. | Infrastructure/bin/ask doctor parser has target and strict only. | PU-001 must add the flag and gate it through Codex-targeted proof. |
| Repo doctor calls skills_handles with check=True without generated command-handle checking. | repo_impl.py uses the base handle check. | PU-002 must wire generated command-handle checks into repo doctor or an equivalent blocking gate. |
| Doctor schema tests can return early when jsonschema is unavailable. | test_ask_skills_doctor.py skips schema validation through an import guard. | PU-003 must make schema validation deterministic in the test lane. |
| Loader, renderer, config, and invocation parity preview commands are absent from the current parser. | Parser has list, budget, handles, resolve, parse, proof, prove, explain, doctor, package, profiles, events, and memory. | PU-005 adds explicit preview commands after the trust boundary and package contracts are in place. |

## Implementation Strategy

1. Fix the trust boundary first: runtime target selection, Codex-targeted proof, and doctor parity entrypoint.
2. Make false success mechanically harder: generated command-handle checks must run in repo doctor or an equivalent blocking gate.
3. Stabilize machine contracts: doctor/runtime JSON failures and schema validation must be deterministic.
4. Add package and compatibility contracts after the runtime and doctor gates can fail correctly.
5. Add Codex preview commands with source or fixture identity, so parity claims are traceable.
6. Extract service boundaries only after the public API and tests expose the real seams.
7. Add conformance workouts, evidence JSONL, and package verification as regression protection.
8. Close with Linear/spec/plan/PR traceability and explicit project/cycle blocking evidence.

## Runtime Persistence and State

| Field | Plan Contract |
|---|---|
| runtime_state | Runtime truth is read from executable commands, source code, focused tests, live tracker/PR/CI state, and validated goal-board receipts. |
| resumption_key | Resume from Docs/goals/jsc-351-agent-skills-codex-abi-conformance/state.yaml, the active task ID, and the latest receipt in receipts.jsonl. |
| runtime_invocation_receipt | Every implemented slice records exact commands, outcomes, changed files, and blocker state in the goal receipt and implementation notes. |
| artifact_chain_key | The canonical chain is spec to plan to goal board to slice receipt to validation evidence to review disposition to delivery state. |
| persistent_artifacts | Persistent artifacts include the canonical spec, canonical plan, goal board, implementation notes, schemas, fixtures, tests, and conformance evidence files created by slices. |
| live_state_refresh | Before Worker implementation and before closeout, refresh git status, plan/spec validators, relevant ask command behavior, Linear, PR, CI, and review state. |
| session_evidence_status | Session-only summaries are not proof; any claim needed for closeout must be backed by repo artifacts, command output, live tracker state, or an explicit blocked receipt. |
| proof_boundary | Artifact validators prove artifact shape only; implementation proof requires focused tests and runtime command behavior for the slice being claimed. |

## Ownership

| Area | Owner | Responsibility | Escalation |
|---|---|---|---|
| Product/spec decisions | Jamie / spec owner | Approve broad SDK architecture, project routing, and unresolved IR/emitter decisions. | Stop and ask when the decision changes scope or long-lived contract. |
| Implementation | Assigned coding agent for each child issue | Implement only the unit scope, preserve source boundaries, and record validation evidence. | Stop when a forbidden path or unsupported runtime assumption is needed. |
| Review | Reviewer selected by risk surface | Check runtime trust boundary, JSON compatibility, service boundaries, security, and agent-native reachability. | Require reviewer follow-up before closeout if the change touches public command contracts. |
| Release/merge | Maintainer or delegated release owner | Confirm local validation, tracker state, PR evidence, and remaining blockers are separated. | Do not merge on artifact validators alone. |
| Tracker | Jamie or tracker owner | Confirm project/cycle destination and issue hierarchy. | Keep project/cycle assignment blocked until confirmed. |

## Enforcement Contract

### essential_decisions

- Codex runtime parity is the ABI target. .agents readiness can support agent-skills workflows, but it cannot satisfy Codex-targeted proof.
- The first slice is JSC-352 because it reduces false-success risk before expanding SDK surface area.
- Public command JSON is part of the SDK contract and must be versioned, schema-backed, and tested.
- Generated command handles are runtime artifacts and must be validated by repo doctor or an equivalent mandatory closeout gate.
- Service extraction follows proven command contracts; it must not precede the trust-boundary fixes.

### fillable_gaps

- Exact internal service module names can be chosen during PU-006 after parser, command output, and tests reveal stable boundaries.
- Compatibility snapshot storage paths can be chosen during PU-004 if they remain repo-owned, reviewable, and covered by tests.
- Codex source fixture strategy can use either checked-in fixtures or direct source identity, but each preview command must report which basis it used.

### guardrails

- Do not claim Codex ABI conformance from .agents runtime readiness.
- Do not add broad SDK abstractions without a failing fixture, command path, schema path, and rollback path.
- Do not flatten machine-readable validation failures into generic prose.
- Do not assign Linear project or cycle metadata until live evidence confirms the target is active and correct.
- Keep generated projections, plugin caches, and user/global Codex config out of implementation scope.

### refusal_triggers

- A proposed fix requires editing .agents/** or Plugins/cache/** to pass Codex-targeted proof.
- A command is added without parser coverage, implementation coverage, JSON contract, and at least one failing fixture.
- A parity preview cannot identify the Codex source or fixture version used for comparison.
- A package verification path needs network writes, publishing, or global install mutation.
- A tracker mutation would assign a project or cycle despite the current blocked evidence.

### durable_memory

- Record any repeated steering, false-success regression, or parity model mismatch in .harness/quality/steering-uptake.md and validate it with python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json.
- If a command output shape changes, update the corresponding schema, fixtures, and acceptance evidence in the same unit.
- If a runtime mismatch is discovered during implementation, preserve the concrete command, fixture, and source identity in the unit evidence.

### professional_output

- Human output stays concise and names the exact gate, command, or blocker.
- JSON output stays complete, stable, and schema-testable.
- Closeout reports separate local validation, tracker state, PR evidence, and remaining blockers.

## Coding and Testing Lenses

| Lens | Contract |
|---|---|
| coding_lens | Prefer the existing ask command architecture, keep parser and implementation changes additive, isolate service extraction until command contracts prove the seam, and avoid touching generated projections or plugin caches. |
| testing_lens | Add focused regression tests that prove observable behavior, including negative cases where .agents readiness cannot satisfy Codex-targeted proof and schema validation cannot silently skip. |

## Work Units

### PU-001: JSC-352 Runtime-Targeted Proof And Doctor Codex Parity Entry

Source IDs: FR-001, FR-002, FR-014, NFR-001, NFR-003, SA-002, SA-011.

Objective: Add the first executable Codex ABI trust boundary: ask skills proof --runtime-target codex|agents|any and ask skills doctor --codex-parity.

Allowed path: Infrastructure/bin/ask, Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/tests/test_ask_skills_doctor.py, focused fixtures under Infrastructure/tests/fixtures/**.

Forbidden path: .agents/**, Plugins/cache/**, global Codex config, generated runtime projections, broad service extraction files outside the current command path.

Implementation steps:

1. Add a parser argument for ask skills proof --runtime-target with choices codex, agents, and any; default to any only for backward compatibility.
2. Extend skills_proof to accept the target and compute Codex readiness independently from .agents readiness.
3. For --runtime-target codex, fail closed when Codex runtime evidence is absent even if .agents evidence is present.
4. Add ask skills doctor --codex-parity and make the first parity check call the Codex-targeted proof path.
5. Ensure doctor next-command selection prefers the blocking Codex parity corrective command before generic explain, improve, or informational commands.
6. Add tests proving .agents readiness cannot satisfy Codex-targeted proof.
7. Preserve current human-readable output while adding machine-readable target, next-command precedence, and evidence fields to JSON output.

Validation: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q; a focused proof command with ./bin/ask skills proof --runtime-target codex --json --robot once the parser is wired; a focused doctor fixture proving blocker-specific next-command precedence.

Stop condition: Stop if Codex runtime evidence cannot be modeled without guessing; capture the blocked source identity and add a fixture-based contract before continuing.

Rollback: Revert the parser argument, skills_proof signature change, doctor flag, and focused tests.

Handoff: PU-002 can start once Codex-targeted proof can fail independently and doctor can surface that failure.

### PU-002: JSC-352 Generated Command-Handle Gate In Repo Doctor

Source IDs: FR-003, SA-003.

Objective: Make stale generated command handles a required repo doctor failure instead of an optional maintenance check.

Allowed path: Infrastructure/scripts/lib/ask/commands/repo_impl.py, Infrastructure/scripts/lib/ask/commands/skills_impl.py, Infrastructure/tests/test_ask_repo_doctor.py, focused handle fixtures under Infrastructure/tests/fixtures/**.

Forbidden path: Generated handle projection output, .agents/**, plugin cache paths, runtime projection caches.

Implementation steps:

1. Inspect the existing skills handles --check --check-command-handles --no-handles behavior and fixture coverage.
2. Wire generated command-handle checking into ask repo doctor --json --robot or a repo doctor subcheck with equivalent closeout status.
3. Emit a distinct machine-readable failure code for stale, missing, or mismatched generated command handles.
4. Add a stale generated handle fixture that fails before the fix and passes after regeneration or corrected source.
5. Document the gate in the command output, not just in prose.

Validation: python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py -q; ./bin/ask repo doctor --json --robot on the local repo after implementation.

Stop condition: Stop if command-handle checking mutates generated outputs during doctor; doctor must validate and report, not silently rewrite.

Rollback: Remove the repo doctor subcheck and associated stale-handle fixtures.

Handoff: PU-003 can start once stale handles are a blocking validation signal.

### PU-003: JSC-352 Deterministic Doctor Schema And Runtime Failure Surface

Source IDs: FR-004, FR-005, FR-014, NFR-002, SA-004, SA-011.

Objective: Ensure doctor contract validation and runtime command failures remain machine-readable and deterministic.

Allowed path: Infrastructure/tests/test_ask_skills_doctor.py, Infrastructure/scripts/lib/ask/commands/skills_impl.py, runtime command modules discovered through imports, Infrastructure/config/schemas/**.

Forbidden path: Test-only shortcuts that bypass the actual parser or command output path.

Implementation steps:

1. Replace the early-return schema test behavior with deterministic validation or an explicit blocked result in the repo-owned test contract.
2. Add tests that fail if missing jsonschema silently skips public schema validation.
3. Identify runtime command failure serialization paths that flatten structured failures.
4. Preserve validation error code, failed check ID, path, and recovery guidance in JSON output.
5. Preserve the precedence reason for the selected next command when multiple commands are available.
6. Add fixtures for at least one schema failure, one runtime surface failure, and one blocker-specific next-command decision.

Validation: python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q; focused schema validation command if the repo exposes one; focused next-command precedence fixture.

Stop condition: Stop if dependency management is required to make schema validation deterministic; classify the dependency decision and request the smallest repo-owned validation path.

Rollback: Revert schema-test changes, runtime failure serialization changes, and fixtures.

Handoff: PU-004 can start once doctor/runtime JSON failure contracts are reliable enough to support package schemas.

### PU-004: JSC-353 SkillPackage v1 Schemas And Compatibility Snapshots

Source IDs: FR-006, FR-007, FR-012, SA-005.

Objective: Define the first Codex-native package contract and snapshot drift checks.

Allowed path: Infrastructure/config/schemas/skill-package.v1.schema.json, Infrastructure/config/schemas/skill-package-readiness.v1.schema.json, related schema tests, package fixtures, Infrastructure/scripts/lib/ask/commands/skills_impl.py package verification paths.

Forbidden path: Publishing workflows, global installs, plugin cache mutation, package registry integration.

Implementation steps:

1. Add SkillPackage v1 schema for SKILL.md frontmatter and optional agents/openai.yaml metadata fields named in the spec.
2. Add readiness schema fields for loadability, provenance, policy, dependencies, and compatibility status.
3. Add golden compatibility snapshots for valid and invalid packages.
4. Add drift tests that fail when schemas or public package output change without snapshot updates.
5. Update package command JSON to report schema version and compatibility snapshot identity.

Validation: python3 -m pytest Infrastructure/tests -q -k 'skill_package or package or doctor'; schema validation command once present.

Stop condition: Stop if schema fields diverge from Codex loader metadata without source evidence; capture the unresolved field and defer it rather than inventing a contract.

Rollback: Remove package schemas, snapshot fixtures, and package JSON output changes.

Handoff: PU-005 can start once package metadata and snapshots give preview commands stable input contracts.

### PU-005: JSC-354 Codex Loader, Renderer, Config, And Invocation Previews

Source IDs: FR-008, FR-013, SA-006.

Objective: Add runtime preview commands that model Codex skill loading, rendering, config rules, and invocation attribution with source identity.

Allowed path: Infrastructure/bin/ask, Infrastructure/scripts/lib/ask/commands/skills_impl.py, new focused runtime adapter modules if extracted under Infrastructure/scripts/lib/ask/**, preview fixtures, preview tests.

Forbidden path: Direct writes to Codex runtime config, home config, plugin cache state, or generated projection directories.

Implementation steps:

1. Add parser and implementation paths for ask skills load-preview, ask skills render-preview, ask skills config explain, ask skills inject-preview, and ask skills implicit-preview.
2. Include Codex source file, commit/ref or fixture identity, and modeled rule version in every preview JSON result.
3. Model root precedence, disabled rules, render budget semantics, and explicit/implicit invocation only to the fidelity supported by source evidence.
4. Add fixtures for duplicate names, disabled rules, truncation/omission warnings, explicit mention, path mention, and script invocation attribution.
5. Mark unsupported parity dimensions as structured blocked checks instead of prose warnings.

Validation: python3 -m pytest Infrastructure/tests -q -k 'preview or codex_parity or invocation or render'; focused ./bin/ask skills load-preview --json --robot and sibling preview commands after implementation.

Stop condition: Stop if the Codex source version cannot be identified; preview commands must not report parity without source identity.

Rollback: Remove preview parser branches, preview implementations, and fixtures.

Handoff: PU-006 can start once preview code reveals stable loader, renderer, config, and invocation boundaries.

### PU-006: JSC-355 Skills SDK Service Boundary Extraction

Source IDs: FR-009, SA-007.

Objective: Split the CLI-heavy implementation into testable SDK service layers without changing public command behavior.

Allowed path: Infrastructure/scripts/lib/ask/commands/skills_impl.py, new modules under Infrastructure/scripts/lib/ask/skills_sdk/** or the closest existing package boundary, import boundary tests, command regression tests.

Forbidden path: Broad rewrites of unrelated ask commands, public JSON shape changes without schema and snapshot updates, moving tests without preserving coverage.

Implementation steps:

1. Map functions touched by PU-001 through PU-005 into service responsibilities: contracts, catalog, validation, packaging, runtime adapters, evidence, and memory.
2. Extract the smallest modules that remove command-file concentration while preserving parser and JSON behavior.
3. Add import-boundary tests that prevent runtime adapters from depending on command presentation code.
4. Keep CLI command functions as thin facades over service modules.
5. Run all previously added command tests to prove behavior did not drift.

Validation: python3 -m pytest Infrastructure/tests -q -k 'skills or repo_doctor or package or preview'; import-boundary test command added in this unit.

Stop condition: Stop if extraction changes public JSON output or command names; fix contract drift before continuing.

Rollback: Inline extracted modules back into the previous implementation and preserve tests.

Handoff: PU-007 can start once service layers make conformance evidence and package verification reusable.

### PU-007: JSC-356 Conformance Workouts, Evidence, And Package Verification

Source IDs: FR-010, SA-008.

Objective: Add repeatable conformance workouts and package verification that produce durable evidence for Codex ABI compatibility.

Allowed path: Infrastructure/bin/ask, Infrastructure/scripts/lib/ask/**, Infrastructure/tests/**, .harness/evidence/** for generated local evidence, package verification fixtures.

Forbidden path: Network publishing, external package upload, direct CODEX_HOME mutation, plugin cache mutation.

Implementation steps:

1. Add ask skills conformance run --json --robot --evidence-dir <path> or an equivalent command named in the spec.
2. Add conformance cases for malformed frontmatter, invalid-but-fail-open agents/openai.yaml, duplicate names, plugin namespace, disabled config, symlinked roots, thin handles, context truncation, and installer rollback.
3. Add ask skills package verify checks for unsafe archives, symlink escapes, digest mismatches, untrusted provenance, and rollback journal evidence.
4. Emit JSONL or equivalent append-only evidence with run ID, fixture identity, command result, validation result, and recovery guidance.
5. Add tests proving unsafe packages fail before any install mutation.

Validation: python3 -m pytest Infrastructure/tests -q -k 'conformance or package_verify or package'; focused conformance command with a temp evidence directory.

Stop condition: Stop if package verification requires a real install or external write; redesign verification to operate on fixtures and staged archives first.

Rollback: Remove conformance command, package verify command, evidence fixtures, and associated tests.

Handoff: PU-008 can close the plan only after evidence paths are deterministic and reviewable.

### PU-008: JSC-351 Traceability, Validation, And Closeout Control

Source IDs: FR-011, NFR-004, NFR-005, NFR-007, SA-001, SA-009, SA-010.

Objective: Keep Linear, spec, plan, PR, and validation truth aligned without inventing tracker readiness.

Allowed path: .harness/plan/**, .harness/specs/**, .harness/research/**, .harness/quality/steering-uptake.md, .harness/implementation-notes/2026-05-23-agent-skills-jsc-351-codex-abi-governed-execution-notes.html, Docs/goals/jsc-351-agent-skills-codex-abi-conformance/**, artifacts/reviews/jsc-351-pu008-closeout/**, PR description artifacts.

Forbidden path: Live Linear project or cycle mutation without owner confirmation, unrelated implementation code, external writes outside declared delivery lanes, generated projection edits.

Implementation steps:

1. Verify the JSC-351 parent and child issue tree before claiming tracker readiness.
2. Report project and cycle state from live Linear separately: project assignment remains unresolved, while cycleId `4a0b5dca-7936-482b-a46c-c55c33069f9d` is already present and must not be mutated without owner confirmation.
3. Run artifact validators for plan/spec identities and traceability before closeout.
4. Record PR evidence by child issue and acceptance ID.
5. Report local validation, tracker state, PR state, and remaining blockers as separate truths.

Validation: python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md; python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md; python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md --json; python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md --kind plan --json; python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md --kind spec --json; python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-351-agent-skills-codex-abi-conformance; git diff --check HEAD; bash scripts/validate-codestyle.sh; ./bin/ask repo validate --json --robot.

Stop condition: Stop if live Linear state contradicts the JSC-351 through JSC-356 tracker tree, if project/cycle mutation would be required without owner confirmation, if PR/review/check truth is stale, or if acceptance traceability cannot connect requirement to validation evidence.

Rollback: Revert traceability artifact edits and restore the previous plan artifact.

Handoff: This unit hands the goal to final Judge or PM closeout only after validators, live PR truth, review-thread truth, and tracker-state reporting pass without unresolved blockers.

## Dependencies and Sequencing

| Sequence | Unit | Depends On | Why |
|---:|---|---|---|
| 1 | PU-001 | Spec approval and local source evidence | Establishes runtime trust boundary. |
| 2 | PU-002 | PU-001 | Prevents stale generated handles from bypassing repo doctor. |
| 3 | PU-003 | PU-001 | Makes doctor/runtime JSON reliable enough for package contracts. |
| 4 | PU-004 | PU-001, PU-003 | Package schemas need stable proof and failure semantics. |
| 5 | PU-005 | PU-001, PU-004 | Parity previews need package metadata and source identity. |
| 6 | PU-006 | PU-001 through PU-005 | Extraction should follow stable command behavior. |
| 7 | PU-007 | PU-004 through PU-006 | Conformance workouts reuse schemas, previews, and services. |
| 8 | PU-008 | All units as each lands | Traceability and closeout run continuously, then finish last. |

## Validation Gates

| Gate | Command | Required Result | Applies To |
|---|---|---:|---|
| Plan identity | python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md | pass | This plan |
| Linear traceability | python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md | pass | This plan |
| BLUF structure | python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md --json | pass | This plan |
| Artifact shape | python3 Plugins/harness-engineering/scripts/check_generated_artifact_shape.py .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md --kind plan --json | pass | This plan |
| JSC-352 proof | python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q | pass | PU-001, PU-003 |
| Doctor next-command precedence | focused doctor fixture proving blocker-specific corrective command precedence | pass | PU-001, PU-003 |
| Repo doctor handle gate | python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py -q | pass | PU-002 |
| Package contract | python3 -m pytest Infrastructure/tests -q -k 'skill_package or package or doctor' | pass | PU-004 |
| Preview contract | python3 -m pytest Infrastructure/tests -q -k 'preview or codex_parity or invocation or render' | pass | PU-005 |
| Service boundary | python3 -m pytest Infrastructure/tests -q -k 'skills or repo_doctor or package or preview' | pass | PU-006 |
| Conformance | python3 -m pytest Infrastructure/tests -q -k 'conformance or package_verify or package' | pass | PU-007 |

## Review Plan

| Review Surface | Reviewer Focus | Trigger |
|---|---|---|
| Runtime trust boundary | Confirm Codex-targeted proof cannot be satisfied by .agents readiness. | After PU-001 |
| API and JSON contracts | Confirm public command output is versioned, schema-backed, and compatible. | After PU-003 and PU-004 |
| Architecture | Confirm service extraction follows proven command seams and avoids premature abstractions. | After PU-006 |
| Security and supply chain | Confirm package verification rejects traversal, symlink escape, digest mismatch, and untrusted provenance before mutation. | After PU-007 |
| Agent-native parity | Confirm commands are reachable by agents through ask and produce machine-readable failures. | After each unit touching command output |

## Rollback Plan

| Failure Mode | Rollback Action | Evidence To Preserve |
|---|---|---|
| Runtime-targeted proof causes false negatives for existing users. | Keep any default behavior, revert only Codex-targeted enforcement, and preserve failing fixture. | Command JSON, fixture path, failing test output |
| Repo doctor generated-handle gate blocks unrelated work. | Revert repo doctor subcheck while keeping standalone handle check and stale fixture. | Doctor output and stale-handle diff |
| Schema validation introduces dependency blocker. | Revert dependency-sensitive test path and add explicit blocked classification until dependency contract is decided. | Import error, validator output, dependency proposal |
| Preview command models Codex behavior incorrectly. | Disable the affected preview check as structured blocked, keep source identity and test fixture. | Codex source reference, mismatched fixture |
| Package verification blocks safe packages. | Revert the specific verifier rule and add a minimal regression fixture before reintroducing. | Package fixture, verifier output |

## Risk Register

| Risk | Severity | Likelihood | Mitigation |
|---|---:|---:|---|
| .agents readiness continues to mask absent Codex readiness. | Critical | High | PU-001 target-aware proof with failing fixture. |
| Generated command handles drift without blocking closeout. | High | Medium | PU-002 repo doctor gate and stale-handle fixture. |
| Public JSON contracts change without schema evidence. | High | Medium | PU-003 and PU-004 schema validation and snapshots. |
| Preview commands overclaim parity against Codex. | High | Medium | PU-005 source or fixture identity in every result. |
| Service extraction becomes a broad rewrite. | Medium | Medium | PU-006 after command stabilization only, with import boundary tests. |
| Package verification mutates runtime state during validation. | High | Low | PU-007 staged fixture verification before install mutation. |
| Linear project/cycle state is assigned or changed from stale evidence. | Medium | Medium | PU-008 reads live tracker state, reports project and cycle truth separately, and keeps further mutation blocked until owner confirmation. |

## Observability and Evidence

- Every new command must emit a run ID or stable check ID where practical.
- Every parity result must include runtime target, source or fixture identity, status, failed check ID, evidence path, and next command.
- Doctor output must include the selected next command, precedence reason, and lower-priority alternatives when a blocker has more than one possible follow-up.
- Every package verification result must include archive identity, provenance identity, rule ID, mutation status, and rollback hint.
- Every conformance run must emit reviewable evidence under a caller-provided evidence directory.
- Closeout must separate local validation, tracker state, PR evidence, and remaining blockers.

## Definition of Done

| Completion Layer | Required Evidence | Cannot Be Substituted By |
|---|---|---|
| Artifact readiness | Plan and spec HE validators pass. | Implementation tests or command smoke checks. |
| Unit implementation | The unit's focused tests pass and at least one failing fixture proves the false-success class is blocked. | Prose summary or passing artifact validators. |
| Command contract | Parser path, implementation path, JSON output, schema or snapshot, and robot-mode evidence exist. | Direct function tests alone. |
| Runtime parity | Codex source or fixture identity is reported by the command output. | .agents readiness, projection success, or remembered Codex behavior. |
| Tracker closeout | Live Linear state is rechecked, project assignment is reported separately from cycle assignment, and owner-decision blockers remain explicit. | Local plan/spec metadata alone. |
| Blocked evidence | Blocked checks include blocker class, exact missing dependency or authority, next safe command, and owner. | Generic warning or skipped test. |

## Visual References / Diagrams

| Node | Meaning |
|---|---|
| JSC-351 Spec | Canonical source contract and acceptance IDs |
| PU-001 | Runtime-targeted proof and doctor Codex parity |
| PU-002 | Generated command-handle repo doctor gate |
| PU-003 | Deterministic doctor schema and runtime failure JSON |
| PU-004 through PU-007 | Package, preview, service boundary, and conformance layers |
| PU-008 | Continuous traceability and closeout control |

Mermaid flow:

flowchart TD
  Spec[JSC-351 Spec] --> Plan[HE Plan]
  Plan --> PU001[PU-001 Runtime-Targeted Proof]
  PU001 --> PU002[PU-002 Command-Handle Gate]
  PU001 --> PU003[PU-003 Deterministic Doctor JSON]
  PU003 --> PU004[PU-004 Package Schemas And Snapshots]
  PU004 --> PU005[PU-005 Codex Parity Previews]
  PU005 --> PU006[PU-006 SDK Service Boundaries]
  PU006 --> PU007[PU-007 Conformance Evidence]
  PU001 --> PU008[PU-008 Traceability]
  PU007 --> PU008

## Accessibility and Operator Ergonomics

- Human command output must identify the failing check in plain language and avoid color-only status signaling.
- JSON output must preserve structured error details so agents do not need to scrape prose.
- New commands must support --json --robot where the surrounding command family supports it.
- Validation instructions must be copy-pasteable and include exact paths.
- Failure messages must include a next command or explicit blocked reason.

## Open Questions

| Question | Owner | Impact | Handling |
|---|---|---:|---|
| Which live Linear project should own JSC-351 after the trashed-project signal is resolved, and is the current cycleId `4a0b5dca-7936-482b-a46c-c55c33069f9d` intentional? | Jamie or tracker owner | Medium | Report current cycle truth and keep further project/cycle mutation blocked until confirmed. |
| Should Codex parity preview fixtures pin to a Codex commit, bundled source snapshot, or local checkout source path? | Implementer with reviewer confirmation | High | PU-005 must choose one source identity model and report it in JSON. |
| Should jsonschema become a required repo validation dependency or should schema validation use a repo-owned fallback? | Implementer with repo maintainer | Medium | PU-003 must classify and encode the chosen dependency contract. |

## Final Decision

Proceed with JSC-352 PU-001 first. Do not start package schemas, parity previews, or service extraction until runtime-targeted proof and doctor Codex parity can fail independently from .agents readiness. Keep Linear project/cycle assignment blocked until live tracker evidence confirms the active destination.

## Linear Work Item Contract

| Field | Value |
|---|---|
| Parent issue | JSC-351 |
| First child issue | JSC-352 |
| Later child issues | JSC-353, JSC-354, JSC-355, JSC-356 |
| Current Linear status | Triage |
| Project/cycle assignment | Blocked by current evidence |
| Required tracker behavior | Preserve parent/child traceability and avoid project/cycle assignment until confirmed |

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
|---|---|---|---|---|
| JSC-351 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011 | PU-001, PU-002, PU-003, PU-004, PU-005, PU-006, PU-007, PU-008 | SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011 | Pending implementation PRs |
| JSC-352 | SA-002, SA-003, SA-004, SA-011 | PU-001, PU-002, PU-003 | SA-002, SA-003, SA-004, SA-011 | Pending implementation PR |
| JSC-353 | SA-005 | PU-004 | SA-005 | Pending implementation PR |
| JSC-354 | SA-006 | PU-005 | SA-006 | Pending implementation PR |
| JSC-355 | SA-007 | PU-006 | SA-007 | Pending implementation PR |
| JSC-356 | SA-008 | PU-007 | SA-008 | Pending implementation PR |
| JSC-351 | SA-001, SA-009, SA-010 | PU-008 | SA-001, SA-009, SA-010 | Pending closeout evidence |

## Appendix A. Harness Metadata / Traceability

interactive_status: execution_selected
route: he-plan
stage: he-plan
artifact_id: he-plan-2026-05-22-jsc-351-agent-skills-codex-abi-conformance
plan_path: .harness/plan/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-plan.md
source_spec: .harness/specs/2026-05-22-jsc-351-agent-skills-codex-abi-conformance-spec.md
linear_issue: JSC-351
first_child_issue: JSC-352
acceptance_ids: SA-001, SA-002, SA-003, SA-004, SA-005, SA-006, SA-007, SA-008, SA-009, SA-010, SA-011
safe_to_continue_jsc_352_runtime_proof: true
safe_to_continue_project_cycle_assignment: false
blocked_reason_project_cycle_assignment: live tracker evidence must confirm active project and cycle before assignment
linear_action_required: project and cycle confirmation only
linear_mutation_status: already_linked
post_plan_handoff_state: explicit_stop
post_plan_handoff_selected_next_stage: none
post_plan_handoff_evidence: plan artifact generated for JSC-351 and ready for validation
post_plan_handoff_next_action: start JSC-352 with PU-001 after plan validators pass
blackboard_delta_focus: Codex ABI conformance before broader SDK implementation
blackboard_delta_first_slice: runtime-targeted proof and doctor parity
git_staging_status: unstaged
staged_paths: []
confidence: strong candidate with implementation validation still required

## Appendix B. Linear / Tracker Handoff

- JSC-351 is the parent execution umbrella.
- JSC-352 is the first implementation issue and owns PU-001 through PU-003.
- JSC-353 owns PU-004.
- JSC-354 owns PU-005.
- JSC-355 owns PU-006.
- JSC-356 owns PU-007.
- PU-008 remains active across all issues for traceability and closeout.
- Project and cycle assignment remain blocked until active Linear metadata is confirmed.

## Appendix C. Review Outcomes

No independent code review has been run for this plan. Required review starts after PU-001 changes exist and must focus on whether Codex-targeted proof can still be satisfied by .agents readiness.
