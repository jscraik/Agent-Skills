# JSC-329 Gap Analysis: Missing SDK, Deep-Module, and Documentation Work

Date: 2026-05-22
Status: audit-ready implementation backlog
Scope: JSC-329 Skill SDK Doctor Contract, deep-module plan, HE product front-door/runtime-contract plan, and current executable repo behavior.

## Executive Summary

The current repo contains a real `./bin/ask skills doctor <target> --json --robot` implementation, but it does not yet satisfy the broader original SDK/deep-module implementation shape.

The gap is not absence of all work. The gap is that the delivered work is an RF-1 slice: a live doctor command and schema-backed payload surface. The broader apparatus remains either planning-only, explicitly deferred, or only partially evidenced. Some implementation notes still describe stale runtime blockers and should no longer be used as current truth.

Current live evidence gathered on 2026-05-22:

| Command | Current result | Interpretation |
| --- | --- | --- |
| `ctx7 whoami` | pass, authenticated user redacted | Context7 CLI/runtime is available and should be part of Context7-related audits. |
| `ctx7 skills list --universal` | pass | Universal skill root is visible to Context7 CLI. |
| `./bin/ask skills doctor context7 --json --robot` | exit 0; `data.skill_doctor.status=warning` | Doctor command works; active gaps are package/share metadata and outcome proof. |
| `./bin/ask skills proof context7 --json --robot` | exit 0; `data.proof.status=pass` | The old context7 runtime blocker is stale. |
| `./bin/ask skills handles --check --no-handles --json --robot` | exit 2; `COMMAND_SURFACE_PROJECTION_DRIFT` | Command-surface projection drift still exists and must be separately classified. |
| `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json` | pass | Context7 audit omission was recorded as high-signal steering uptake. |

The priority queue below is ordered by what should be implemented first to convert the current RF-1 slice into reliable agent-facing SDK behavior.

## External SDK Generation Lens: WorkOS Article Review

Source reviewed: https://workos.com/blog/handwritten-sdks-are-dead

The WorkOS article argues that high-quality SDKs should not be hand-maintained wrappers. Their approach is:

- one first-class source specification
- a normalized, fully-resolved intermediate representation
- language- or surface-specific emitters
- AI constrained by repo-owned conventions, not allowed to invent behavior
- generated SDKs that stay in parity because changes flow from the source spec through the same pipeline
- docstrings, types, error handling, pagination, retries, and auth behavior treated as SDK quality, not optional polish
- SDK output designed for both humans and coding agents to consume consistently

Mapped to Agent Skills Kit, this means the Skills SDK should not be only a collection of command handlers and documentation. It needs a repo-owned generation pipeline:

| WorkOS SDK principle | Current gap coverage | What it means for Agent Skills Kit |
| --- | --- | --- |
| Single source of truth | Partly covered by Priority 3 | `skills-sdk.json` must become the source contract or be replaced by one; runtime payloads and docs cannot drift independently. |
| Normalized IR | Newly added as Priority 2A | Add a resolved Skills SDK IR that command handlers, docs, projections, and lifecycle commands consume. |
| Emitters over hand-maintained surfaces | Newly added as Priority 2A | Generate command metadata, schema docs, fixtures, and projection contracts from the IR rather than editing each surface separately. |
| AI constrained by skills/instructions | Partly covered by Priority 8 and Priority 9 | Agent guidance must be generated or validated from the same contract so future agents cannot follow stale docs. |
| Agent-usable SDKs | Covered by Priority 1, Priority 5, and Priority 6 | Stable snapshots, precise next actions, and target/global proof separation make the SDK reliable for agents. |
| Consistency across SDK outputs | Partly covered by Priority 4 and Priority 10 | Lifecycle commands, schemas, package readiness, events, and docs must advance together through one pipeline. |

The added implementation implication is Priority 2A: define the Skills SDK IR and generator/emitter boundary before broad lifecycle expansion. Without that, project-local lifecycle commands risk becoming more handwritten CLI surface area instead of a real SDK apparatus.

## Priority 0: Correct Scope Authority and Current-State Records

### What Is Missing

The repo needs a current-state reconciliation that distinguishes:

- live runtime truth
- completed RF-1 implementation
- remaining SDK/deep-module gaps
- user-authorized scope versus agent-selected future-work slicing

The older T003 note says context7 doctor/proof remained blocked by runtime drift, but live commands now show proof passes and doctor warns on package/outcome evidence.

Evidence:

- `docs/goals/jsc-329-skill-sdk-doctor-contract/notes/T003-doctor-contract-live-reconciliation.yaml` records `live_doctor.outcome: blocked_expected` and `live_proof.outcome: blocked`.
- `.harness/implementation-notes/2026-05-21-agent-skills-jsc-329-goal-kickoff.html` says the live context7 doctor still reports `blocked_runtime`.
- Fresh live command evidence shows `skills proof context7` passes and `skills doctor context7` warns, not blocks.

### Why It Matters

If stale goal state remains the steering source, future agents will fix the wrong problem. They will chase runtime reachability that now passes instead of closing package metadata, outcome proof, contract snapshots, and SDK/deep-module boundaries.

This also preserves the original authority issue: if full implementation was requested, converting the rest into future work required explicit user approval. That authority boundary is not currently encoded as a hard stop in the goal artifacts.

### How To Implement

1. Add a new current-state receipt under `docs/goals/jsc-329-skill-sdk-doctor-contract/receipts.jsonl` or a new note under `docs/goals/jsc-329-skill-sdk-doctor-contract/notes/`.
2. Record the fresh live command outputs:
   - `ctx7 whoami` authenticated, redacted
   - `./bin/ask skills doctor context7 --json --robot`
   - `./bin/ask skills proof context7 --json --robot`
   - `./bin/ask skills handles --check --no-handles --json --robot`
3. Classify the active blocker as contract completeness, not runtime reachability.
4. Add an explicit scope-authority statement:
   - RF-1 is implemented only as a partial slice.
   - Full SDK/deep-module implementation remains incomplete.
   - Future-work labeling is not equivalent to user approval for deferral.
5. Update `state.yaml` only after the current-state note exists and validation evidence is attached.

### Verification

- `./bin/ask skills doctor context7 --json --robot`
- `./bin/ask skills proof context7 --json --robot`
- `./bin/ask skills handles --check --no-handles --json --robot`
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`

## Priority 1: Add Contract Snapshot Evidence for `skills doctor`

### What Is Missing

The plan requires persisted, assertion-backed doctor contract evidence. The current implementation has tests, but the planned snapshot artifacts and a dedicated contract test are missing.

Missing artifacts found during audit:

- no `artifacts/skill-doctor/context7.before.json`
- no `artifacts/skill-doctor/context7.after.json`
- no second non-context7 live doctor snapshot
- no `Infrastructure/tests/test_ask_skills_doctor_contract.py`

Evidence:

- `Infrastructure/config/skills-sdk.json` lists safe conditions including schema snapshots, context7 fixture, and second non-context7 fixture.
- `Infrastructure/tests/test_ask_skills_doctor.py` contains useful behavior coverage, but it is not the planned persisted snapshot contract.
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json` exists and is the concrete schema reference.

### Why It Matters

Without committed snapshots, downstream agents and harness consumers cannot tell whether the doctor payload is stable or merely happens to pass current unit tests. The contract remains easy to drift because no artifact locks the public JSON shape to real command output.

This is the highest-value implementation gap after state reconciliation because it turns the doctor command from "works locally" into "safe for agents to consume."

### How To Implement

1. Create `artifacts/skill-doctor/`.
2. Capture normalized JSON output for:
   - `context7`
   - one representative second skill that is not context7, such as `Skills/agent-ops/autofix` or another stable canonical skill.
3. Normalize volatile fields before committing snapshots:
   - timestamps
   - trace IDs
   - absolute temp paths
   - authenticated user identity
4. Add `Infrastructure/tests/test_ask_skills_doctor_contract.py`.
5. Test that snapshots:
   - validate against `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
   - include required `target_summary`
   - include check taxonomy
   - include `next_command`
   - preserve pass/warning/blocked status precedence
   - preserve package/outcome-proof warning classes
6. Make schema validation mandatory in the contract test. If `jsonschema` is not available, the contract test should fail with a clear dependency/setup message rather than silently skipping the public contract proof.

### Verification

- `UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 --with pytest --with jsonschema python -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py -q`
- `./bin/ask skills doctor context7 --json --robot`
- `./bin/ask skills doctor Skills/agent-ops/autofix --json --robot`
- `python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills_impl.py Infrastructure/tests/test_ask_skills_doctor_contract.py`

## Priority 2: Extract the Doctor Deep Module Behind the CLI Facade

### What Is Missing

The current doctor behavior is implemented inside `Infrastructure/scripts/lib/ask/commands/skills_impl.py`. That command module owns target resolution, proof invocation, checks, warnings, status precedence, next-command policy, lifecycle event assembly, and schema refs.

The deep-module plan called for a shallow public command facade backed by deeper service modules. The current implementation is therefore a working patch, not the planned deep-module boundary.

Evidence:

- `skills_doctor` lives in `Infrastructure/scripts/lib/ask/commands/skills_impl.py`.
- `_skill_doctor_next_command` also lives in the command implementation module.
- No `Infrastructure/scripts/lib/ask/services/skills/doctor.py` or equivalent doctor service exists.
- `Infrastructure/scripts/lib/ask/services/` currently contains plugin services, not a skills SDK doctor service.

### Why It Matters

A command-module implementation makes it harder to reuse the doctor contract from other SDK surfaces, tests, package readiness, lifecycle events, or future project-local skill commands. It also makes future agents more likely to patch behavior in place instead of strengthening the domain boundary.

The deep module should make the unsafe or partial use harder to express: command handlers should call the service, not own the readiness model.

### How To Implement

1. Create a skills service package, for example:
   - `Infrastructure/scripts/lib/ask/services/skills/__init__.py`
   - `Infrastructure/scripts/lib/ask/services/skills/doctor.py`
   - optionally `Infrastructure/scripts/lib/ask/services/skills/contracts.py`
2. Move the following responsibilities into the service:
   - doctor target resolution
   - runtime proof adapter
   - canonical source check
   - structural audit adapter
   - metadata/package readiness check
   - outcome proof discovery
   - status precedence
   - warning/blocker taxonomy
   - next-action policy
   - lifecycle event construction
   - schema reference lookup
3. Keep `Infrastructure/bin/ask` and `skills_impl.py` as thin command facades.
4. Preserve the existing `data.skill_doctor` JSON shape exactly unless a schema migration is explicitly planned.
5. Add service-level tests for status precedence and next-action policy.
6. Keep the CLI contract tests from Priority 1 as regression protection.

### Verification

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py Infrastructure/tests/test_ask_skills_doctor_contract.py -q`
- `./bin/ask skills doctor context7 --json --robot`
- `./bin/ask skills doctor Skills/agent-ops/autofix --json --robot`
- `python3 -m py_compile Infrastructure/scripts/lib/ask/services/skills/doctor.py Infrastructure/scripts/lib/ask/commands/skills_impl.py`

## Priority 2A: Define the Skills SDK Intermediate Representation and Emitters

### What Is Missing

The gap analysis already calls out that `skills-sdk.json` is a planning contract and that doctor behavior is still command-module-heavy. The WorkOS SDK-generation lens adds a more specific missing layer: there is no normalized Skills SDK intermediate representation that every surface consumes.

Today, the repo has several related but separate surfaces:

- `Infrastructure/config/skills-sdk.json`
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/command_metadata.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- generated command-surface/projection files
- README and agent operating docs
- future lifecycle/event/package/profile contracts

Those surfaces can drift because they are not generated from one resolved model.

### Why It Matters

The WorkOS article's strongest SDK lesson is that the OpenAPI spec is the source, the IR is the stable language-independent state, and emitters translate that IR into target-language SDKs. For Agent Skills Kit, the equivalent is:

- source contract: the canonical skill/package/runtime/lifecycle specification
- IR: a resolved Skills SDK model with handles, roots, schemas, operations, status taxonomy, lifecycle events, evidence requirements, and projection ownership
- emitters: CLI parser/metadata, JSON schemas, docs, fixtures, projection contracts, and test snapshots

Without this layer, the repo will continue to hand-maintain SDK surfaces in parallel. That recreates the failure mode the WorkOS article warns about: one surface exposes a field another forgot, docs go stale, and agent-facing behavior drifts from the machine contract.

### How To Implement

1. Define a resolved Skills SDK IR schema, for example `Infrastructure/config/schemas/skills-sdk-ir.v1.schema.json`.
2. Add a builder that reads canonical sources:
   - `Infrastructure/config/skills-sdk.json`
   - skill frontmatter
   - command metadata
   - schema refs
   - projection ownership policy
   - lifecycle/eval evidence policy
3. The builder should resolve references and produce one normalized artifact, for example:
   - `Infrastructure/artifacts/skills-sdk/ir.json` for generated evidence, or
   - a deterministic test fixture under `Infrastructure/tests/fixtures/skills-sdk/ir.json`
4. Add emitters from the IR for:
   - command metadata expectations
   - doctor schema extraction fields
   - fixture snapshot normalization rules
   - README/operating-contract command tables
   - lifecycle event schema references
   - projection ownership checks
5. Constrain AI/agent guidance to the IR:
   - update agent docs to say generated SDK surfaces must be changed through the IR or emitter layer
   - add tests that fail when docs/metadata/schema fields diverge from the IR
6. Make the doctor service from Priority 2 consume the IR instead of re-deriving contract shape in command glue.

### Verification

- `python3 -m pytest Infrastructure/tests/test_skills_sdk_ir.py -q`
- `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py Infrastructure/tests/test_ask_skills_doctor_contract.py -q`
- `./bin/ask skills doctor context7 --json --robot`
- a new check such as `./bin/ask skills sdk-ir --check --json --robot`, if a public validation command is added

## Priority 3: Align `skills-sdk.json` With the Live Doctor Payload

### What Is Missing

`Infrastructure/config/skills-sdk.json` still describes a planning contract. Several extraction fields do not match the live doctor payload.

Examples:

| Contract field | Live payload reality |
| --- | --- |
| `target_summary.resolved` | live payload uses target kind, handle, canonical source, audit target |
| `target_summary.source_path` | live payload uses `canonical_source_path` |
| `target_summary.projection_path` | not present in current live summary |
| `checks[].id` | live payload uses an object keyed by check name, not an array |
| `checks[].summary` | not present as planned |
| `contract_schemas.skill_doctor` | live payload uses `contract_schemas.doctor` |

Evidence:

- `Infrastructure/config/skills-sdk.json` is still `planning_contract`.
- The extraction list under the doctor source does not line up with fresh `skills doctor context7` JSON.

### Why It Matters

The SDK contract should be the machine-readable agreement that consumers use. If it does not match the live payload, agents will either ignore it or implement against the wrong shape.

This is a contract drift problem: the docs look authoritative, but the runtime is the real source of truth.

### How To Implement

1. Decide whether the live payload is the intended shape or whether the contract file is the intended shape.
2. If the live payload is intended:
   - update `skills-sdk.json` extraction fields to match it
   - mark which fields are RF-1 stable and which are experimental
   - update status from `planning_contract` only when snapshots/tests prove it
3. If the contract file is intended:
   - migrate `skills_doctor` output to match it
   - update `skill-doctor.v1.schema.json`
   - update tests and snapshots together
4. Add a test that compares `skills-sdk.json` extraction declarations with live fixture keys.

### Verification

- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py -q`
- a new test such as `Infrastructure/tests/test_skills_sdk_contract.py::test_doctor_extraction_contract_matches_snapshot`
- `./bin/ask skills doctor context7 --json --robot`

## Priority 4: Implement or Explicitly De-Scope Project-Local SDK Lifecycle Commands

### What Is Missing

The broad SDK plan includes project-local skill lifecycle commands:

- `./bin/ask skills create <handle> --project <owner-repo> --root <declared-root> --eval-gate full --json --robot`
- `./bin/ask skills install <source> --project <owner-repo> --root <declared-root> --eval-gate install-smoke --json --robot`
- `./bin/ask skills update <handle> --project <owner-repo> --eval-gate regression --json --robot`

These have not been delivered as planned. Existing live surfaces are not equivalent:

- `skills install` is currently a GitHub URL installer with `--dest`, `--remediate`, and `--dry-run`.
- `skills init` scaffolds local skills under a category but does not implement the project-local SDK lifecycle gate.
- no `skills create` or `skills update` parser action exists.

### Why It Matters

This is the core "SDK format" gap. Without lifecycle commands, the repo has a doctor for readiness but no complete SDK lifecycle for creating, installing, updating, evaluating, and promoting project-local skills.

It also keeps ownership ambiguous: when another repo owns `.agents/skills` or `.codex/skills`, this SDK needs command support to avoid agents editing generated projections or the wrong canonical source.

### How To Implement

1. Add parser actions for `skills create`, `skills update`, and project-local mode for `skills install`.
2. Define an owner-repo resolution layer:
   - validates target repo
   - reads owner repo `skills-sdk.json`
   - determines canonical project skill root
   - rejects generated projection writes
3. Implement lifecycle gates:
   - create: scaffold skill + eval suite + first evidence path
   - install: copy/import source + provenance + namespace validation + install-smoke eval
   - update: change existing skill + regression eval + promotion/rollback decision
4. Emit lifecycle events into the owner repo `.harness/session-evidence/skills/<handle>/<eval-run-id>/events.jsonl`.
5. Add dry-run mode for each lifecycle command.
6. Add tests for:
   - project root resolution
   - generated projection rejection
   - eval gate required
   - lifecycle event write
   - blocked status when owner repo lacks `skills-sdk.json`

### Verification

- `./bin/ask skills create demo-skill --project <fixture-repo> --root .agents/skills --eval-gate full --json --robot --dry-run`
- `./bin/ask skills install <fixture-source> --project <fixture-repo> --root .agents/skills --eval-gate install-smoke --json --robot --dry-run`
- `./bin/ask skills update demo-skill --project <fixture-repo> --eval-gate regression --json --robot --dry-run`
- focused pytest for lifecycle commands
- `./bin/ask repo validate --changed-files <changed files> --json --robot`

## Priority 5: Fix Warning-State `next_command` Routing

### What Is Missing

When `skills doctor context7` reports package/share metadata and outcome proof warnings, the current `next_command` points to strict audit first. That does not directly address the missing evidence.

Current code path:

- package/metadata warning returns `skills audit ... --level strict`
- only afterward would capability contract warning point to `skills package`
- only afterward would outcome proof warning point to `skills prove`

### Why It Matters

Agents often follow `next_command` literally. If `next_command` points to structural audit when the actual missing work is package metadata or outcome proof, the workflow loops around the real gap.

This is a misuse-resistant interface problem: the contract exposes the right warnings but gives a less precise action.

### How To Implement

1. Replace single `next_command` selection with either:
   - a prioritized `next_actions[]` array, or
   - a more precise single `next_command` for warning-only states.
2. For `capability_contract_incomplete`, route to `skills package <handle>` or a specific package metadata repair command if one exists.
3. For `outcome_proof_missing`, route to `skills prove <handle>` or an outcome-workout creation command if one exists.
4. Keep strict audit available as a secondary action, not the primary action for package/outcome gaps.
5. Add table-driven tests for warning combinations.

### Verification

- pytest coverage for `_skill_doctor_next_command` or the extracted service equivalent
- `./bin/ask skills doctor context7 --json --robot | jq '.data.skill_doctor.next_command'`
- snapshot test update from Priority 1

## Priority 6: Resolve Proof Payload Ambiguity Around Global Command-Handle Drift

### What Is Missing

`./bin/ask skills proof context7 --json --robot` reports target proof pass, while the embedded `command_handle_check.status` can still be fail for unrelated command handles such as `he-brainstorm`.

That may be semantically valid if the target handle is satisfied through the user runtime, but the payload does not make the global-versus-target distinction clear enough.

### Why It Matters

A consumer can incorrectly read the proof as either:

- fully clean repo-wide command-surface health, or
- invalid target proof despite target runtime being ready

Both readings are plausible because the payload mixes target gates and global drift without clear ownership classification.

### How To Implement

1. Split target proof from global projection health in the payload:
   - `target_runtime.status`
   - `global_command_surface.status`
   - `global_command_surface.blocks_target: true|false`
2. If global drift does not block the target, classify it as `non_blocking_global_drift`.
3. If global drift blocks the target, identify exactly which target gate fails.
4. Update doctor runtime-reachability check to consume the target proof section, not a mixed interpretation.
5. Add tests where:
   - target passes and unrelated global drift exists
   - target fails due to missing handle
   - no global drift exists

### Verification

- `./bin/ask skills proof context7 --json --robot`
- `./bin/ask skills handles --check --no-handles --json --robot`
- focused proof/doctor tests

## Priority 7: Implement or Explicitly Track HE Product Front-Door Runtime Contract

### What Is Missing

The May 11 HE plan proposed HE setup/status front-door behavior and an HE runtime/source boundary, but no active executable `he-doctor` or HE setup/status route was found in `./bin/ask` surfaces.

### Why It Matters

This is adjacent to JSC-329 but not completed by it. Counting JSC-329 doctor work as satisfying the HE front-door/runtime-contract plan would collapse two separate plans into one and hide unimplemented product work.

### How To Implement

1. Decide whether HE front-door work belongs in the current implementation queue or remains a separate issue lane.
2. If implementing:
   - add an HE setup/status command under `./bin/ask`
   - report source/projection/runtime boundaries
   - include readiness checks for required HE skill surfaces
   - expose safe next commands
3. If not implementing now:
   - add a current-state note that explicitly says this is not covered by JSC-329
   - link the owning issue/plan
   - avoid claiming HE front-door closure from skills doctor completion

### Verification

- `./bin/ask he status --json --robot` or whatever final route is chosen
- focused HE status tests
- README/agent operating contract alignment

## Priority 8: Align Agent-Facing Documentation With the Real Doctor Contract

### What Is Missing

`README.md` includes `skills doctor` in common/golden-path commands, while `Docs/agents/16-agent-operating-contract.md` still describes a path that moves from explain to prove without doctor.

### Why It Matters

Different agents will follow different evidence paths depending on which front door they read. That weakens the public contract and makes stale-state regressions more likely.

### How To Implement

1. After Priority 1 and Priority 3, update `Docs/agents/16-agent-operating-contract.md`.
2. Make the standard readiness path explicit:
   - `skills resolve`
   - `skills doctor`
   - `skills prove`
   - `skills package` or `skills audit` only when the doctor says so
3. Include exact examples and expected status classes.
4. Keep README and operating contract in sync.
5. Add a doc-contract check if the repo already has one for command tables.

### Verification

- documentation review
- `./bin/ask skills --help`
- command metadata/parser parity test from Priority 9

## Priority 9: Add Parser, Help, Metadata, and Guided-Error Parity Tests

### What Is Missing

The plan calls for parser/help/metadata/guided-error parity. The parser registers `doctor` and `package`, and command metadata includes related entries, but no dedicated command-contract test file was found.

### Why It Matters

This is the guardrail that prevents future work from adding a command in one surface but not another. For agent-facing CLIs, inconsistent help/metadata/error suggestions are real runtime failures.

### How To Implement

1. Add `Infrastructure/tests/test_ask_skills_command_contract.py`.
2. Compare:
   - parser subcommands in `Infrastructure/bin/ask`
   - `VALID_ACTIONS["skills"]`
   - command metadata
   - help output
   - unknown-action suggestions
3. Include `doctor`, `package`, and any new lifecycle commands from Priority 4.
4. Fail if a command is parser-visible but missing metadata or guided-error support.

### Verification

- `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py -q`
- `./bin/ask skills --help`
- invalid command smoke such as `./bin/ask skills doctro context7 --json --robot`

## Priority 10: Decide Which Deferred Schemas Must Become Concrete

### What Is Missing

Only the doctor schema currently has a concrete schema file. Other contract schema references are advertised but explicitly defer concrete schemas until external consumers require them:

- events
- lifecycle event
- profiles
- package
- memory

Evidence:

- `_doctor_contract_schema_refs` returns `missing_schema_reason` for non-doctor schemas.
- Live doctor payload includes these deferred schema references.

### Why It Matters

This is acceptable only if the current claim is "doctor RF-1 is partially implemented." It is not acceptable if the claim is "the SDK contract apparatus is fully implemented."

### How To Implement

1. Decide which surfaces are required for the next SDK milestone.
2. For each required surface:
   - add a concrete schema file under `Infrastructure/config/schemas/`
   - add a fixture payload
   - add validation tests
3. For each intentionally deferred surface:
   - keep `missing_schema_reason`
   - link to a tracked issue or explicit milestone
   - do not count it as implemented

### Verification

- schema validation tests for every concrete schema
- doctor payload schema-reference tests
- SDK contract extraction tests

## Implementation Order Summary

| Priority | Implement first because | Deliverable |
| --- | --- | --- |
| P0 | Prevents future agents from working from stale or unauthorized scope state. | Current-state note/receipt and explicit scope-authority classification. |
| P1 | Turns live doctor behavior into a stable public contract. | Doctor snapshots and mandatory schema contract tests. |
| P2 | Converts patch-shaped implementation into planned deep-module architecture. | Doctor service module behind thin CLI facade. |
| P2A | Prevents handwritten SDK-surface drift by adding a normalized IR and emitters. | Skills SDK IR schema, builder, emitters, and drift tests. |
| P3 | Makes the machine-readable SDK contract match runtime truth. | Updated `skills-sdk.json` extraction contract plus tests, ideally emitted from the IR. |
| P4 | Delivers the actual SDK lifecycle surface. | Project-local `create/install/update` lifecycle commands and eval gates. |
| P5 | Makes remediation paths actionable. | Precise warning-state `next_command` or `next_actions[]`. |
| P6 | Removes ambiguity from target proof versus global drift. | Split proof payload semantics and tests. |
| P7 | Prevents JSC-329 from being mistaken for HE front-door completion. | HE status/setup route or explicit de-scope note. |
| P8 | Keeps agent docs aligned with the real contract. | README/operating-contract alignment. |
| P9 | Prevents command-surface drift. | Parser/help/metadata/guided-error parity tests. |
| P10 | Makes future SDK schemas honest. | Concrete schemas or tracked deferrals. |

## Definition of Done for the Full Missing Work

The missing implementation should not be considered complete until all of these are true:

1. Goal notes distinguish stale T003 evidence from current runtime truth.
2. `skills doctor context7` and one second fixture have committed normalized snapshots.
3. Contract tests validate snapshots against `skill-doctor.v1.schema.json`.
4. Doctor behavior is owned by a service/deep module, not primarily by command glue.
5. A normalized Skills SDK IR exists and at least doctor schema/docs/metadata expectations are emitted or validated from it.
6. `skills-sdk.json` extraction fields match live payloads or the live payloads are migrated to match the contract.
7. Project-local SDK lifecycle commands are implemented or explicitly tracked outside this completion claim.
8. Doctor warning states route to the evidence that is actually missing.
9. Proof payloads separate target runtime readiness from global command-surface drift.
10. HE product front-door work is implemented or clearly de-scoped from JSC-329.
11. Agent-facing docs and command metadata agree on the golden path.
12. Validation evidence is current and command outcomes are recorded without reusing stale blocker language.

## Authority Note

The repo evidence shows that deferral happened in plan and implementation artifacts. If the accepted user direction was full implementation, then this should be treated as a scope-authority failure: agents selected smaller slices and labeled remaining work as future/post-RF-1 without first making that a user-approved change in completion criteria.

Future implementation should therefore begin with P0 before writing feature code.
