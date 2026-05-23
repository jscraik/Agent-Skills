# Evidence-Led Codebase Gap Audit

Date: 2026-05-22

Project root: `/Users/jamiecraik/dev/agent-skills`

Primary evidence:
- `.harness/research/deep/2026-05-22-skills-sdk-oagen-analysis.md`
- User-supplied Codex runtime ABI plan in the audit request
- Live code inspection of `Infrastructure/bin/ask`, `Infrastructure/scripts/lib/ask/**`, validators, tests, schemas, CI workflows, and projection scripts
- Reviewer inputs from `agent-native-reviewer`, `api-contract-reviewer`, and `adversarial-reviewer`

Skill used: `improve-codebase-architecture`

Selected architecture lenses:
- Deep Module Examiner
- Architectural Pattern Cartographer
- Pattern Catalog Skeptic
- Pragmatic Delivery Partner

Request-user-input status: not applicable for this audit artifact. User approval is required before executing the selected structural patch sequence.

Live checks run:

| Command | Outcome | Important signal |
|---|---:|---|
| `git status --short --branch` | pass | Worktree was already dirty; this audit adds only the requested research artifact. |
| `fd . Infrastructure/config/schemas -t f` | pass | Only `skill-doctor.v1.schema.json` and `selection-gate-severity.v1.schema.json` exist. |
| `./bin/ask runtime budget --json --robot` | pass | Runtime budget passes with 27 default-visible skills, but uses repo policy, not Codex renderer parity. |
| `./bin/ask runtime surface --json --robot` | pass | Same budget-backed path as runtime budget; `runtime.py` can downgrade validation errors for surface mode. |
| `./bin/ask skills handles --check --check-command-handles --no-handles --json --robot` | fail | Exit 2; command surface projection drift and generated command-handle check failures are live. |
| `./bin/ask skills proof context7 --json --robot` | pass | Passes through `.agents`; `codex_user_runtime_ready=false`. Global command-handle check remains fail. |
| `./bin/ask skills doctor context7 --json --robot` | warning | Doctor succeeds with warnings for package contract and outcome proof. |
| `./bin/ask skills package context7 --json --robot` | warning | Package readiness exists but `context7` lacks version, compatible roles, runtime needs, provenance, and share readiness. |

## 1. Executive Summary

Overall maturity grade: **C-**

Codex ABI readiness grade: **D+**

The codebase has a strong control-plane foundation: a real `ask` CLI, skill doctor payload, package readiness payload, runtime budget validator, command-handle projection checks, trace IDs, lifecycle events, and governance validators. The gap is not absence of effort. The gap is that the strongest SDK ideas remain spread across command glue, planning contracts, projection validators, and docs rather than being unified as a Codex-native conformance SDK.

The evidence document says Skills SDK needs a source-to-IR-to-emitter pipeline, generated manifests, compatibility snapshots, deterministic smoke checks, and validator-owned AI boundaries. The user plan narrows that into a runtime-ABI requirement: Codex itself is the ABI, and `ask` must prove Codex loader, renderer, config, package, and injection behavior. The current implementation does not yet meet that bar.

Top 5 gaps:

1. **No Codex loader parity oracle.** `ask` can prove workspace and user runtime files, but it cannot say which skills Codex would load from actual Codex roots, in actual order, with disabled rules applied.
2. **No Codex-native SkillPackage v1 schema.** `skills package` emits useful readiness JSON, but the only concrete schema artifact is the doctor schema.
3. **Runtime proof can pass without Codex readiness.** `skills proof context7` passed because `.agents` was ready even though `.codex` was not ready.
4. **Generated command-handle parity is available but not enforced in the main doctor lane.** A live command found command-handle failures, while `repo doctor` calls `skills_handles(... check=True)` without generated handle checking.
5. **SDK layers are named but not module boundaries.** The doctor and package behavior live in a large `skills_impl.py` command module instead of enforceable contracts/catalog/validation/packaging/runtime-adapter modules.

Top 5 risks:

1. **False success:** A skill can look reachable or usable while Codex-native invocation is still unproved.
2. **Contract drift:** JSON payloads can change without schema or compatibility snapshot detection.
3. **Stale projection:** Existing files can satisfy reachability checks while content/provenance differs from canonical source.
4. **Runtime mismatch:** Repo budget and projection policies can pass while Codex renderer, loader, or config rules behave differently.
5. **Agent loop misrouting:** Doctor `next_command` can steer agents toward strict audit while the active gap is package metadata or outcome proof.

Strongest existing foundations:

- `skills doctor` has a typed public payload and concrete schema at `Infrastructure/config/schemas/skill-doctor.v1.schema.json`.
- `skills package` already models package readiness, lifecycle events, promotion gates, and next commands.
- `skills proof` already checks resolver, generated command handle, workspace file, and user runtime links.
- `command_surface.py` already has projection and generated command-handle check/write primitives.
- `validate_all_impl.sh` already schedules required budget, context, projection, steering, and catalog validators.
- High-signal steering uptake is now represented by docs plus a validator.

Highest-leverage next fixes:

1. Add `ask skills load-preview --codex-parity --json`.
2. Add `skill-package.v1.schema.json` and mandatory schema validation for doctor/package contract snapshots.
3. Add `--require-codex-runtime` to `skills proof` and wire it into `skills doctor --codex-parity`.
4. Make generated command-handle check a hard repo doctor signal.
5. Extract the first deep module slice: `ask.services.skills.contracts`, `catalog`, `runtime_adapters.codex`, and `validation.schemas`.

## 2. Overall Gradecard

| Area | Grade | Confidence | Current Status | Main Gap | Recommended Fix |
|---|---:|---:|---|---|---|
| Repository as Control Plane | B | High | Strong docs, AGENTS, schemas, validators, workflows, and steering uptake surfaces. | SDK contract file is `planning_contract`; some docs describe intended SDK behavior without executable gates. | Add a validator that classifies each SDK contract section as `implemented_enforced`, `implemented_not_enforced`, or `documented_only`. |
| Runtime Truth and Decision Packets | C | High | `ask` envelopes include trace IDs, status, errors, next commands, lifecycle events. | No Codex loader/render/injection preview; current proof accepts `.agents` in place of Codex. | Add Codex parity previews and require them in doctor parity mode. |
| Claim-vs-Evidence Verification | C | High | Package/doctor/proof commands provide evidence fields and validation commands. | Claims are not backed by compatibility snapshots; `jsonschema` validation can be skipped in tests. | Add committed snapshots and mandatory JSON Schema validation. |
| Mechanical Architecture Enforcement | C | Medium | Many validators exist in `validate_all_impl.sh`; command surface checks exist. | No dependency-layer tests for Skills SDK parser/IR/emitter/runtime boundaries because those layers are not modules yet. | Extract one bounded module slice and add import/layer tests. |
| Harness Runtime Loop | C | Medium | Error codes, blockers, warnings, lifecycle events, and `repo doctor` signals exist. | Retry budgets, stale-state prevention, and Codex-specific stop reasons are not unified. | Add runtime card + attempt ledger for skill conformance checks. |
| Trace and Session Evidence | C | Medium | `CallResult.trace_id`, telemetry latency, lifecycle events, and eval artifacts exist. | No JSONL command/session evidence stream for conformance runs. | Add `ask skills conformance run --evidence-dir` with JSONL events. |
| Context Engineering | B- | High | Runtime budget, context-budget checks, rooted projection, and command handles exist. | Budget algorithm does not mirror Codex `render.rs`; command handles are not proven through Codex injection. | Add `render-preview --codex-parity` and `inject-preview`. |
| Skills and Workflow Density | B- | High | Rooted skills, latent handles, workouts, and validation family gates exist. | Workouts are not SDK conformance tests for loader/render/config/injection/package rollback. | Add conformance workout suite. |
| Recovery and Failure Handling | C | Medium | Classified blockers exist; steering uptake validator exists. | No deterministic recovery handlers for stale handles, Codex link drift, config-rule mismatch, or package snapshot drift. | Add recovery handlers with bounded retry and proof commands. |
| Governance and Safety | B- | Medium | Secret redaction, PR gates, security workflows, path boundaries, and install-readiness ideas exist. | Package supply-chain verification is partial; no `package verify` with digest lock/quarantine/rollback journal. | Add `ask skills package verify` and schema-backed provenance manifest. |

## 3. Evidence-to-Code Mapping

| Evidence Pattern | Source File | Code Location | Runtime Status | Grade | Confidence |
|---|---|---|---|---:|---:|
| Codex-native SkillPackage v1 | User plan P0.1; Oagen analysis lines 58-63 | `Infrastructure/config/schemas/` only has doctor and selection schemas; package JSON built in `skills_impl.py:2631-2721` | partial | D | High |
| Codex loader parity oracle | User plan P0.2; Codex loader source cited in plan | No `load-preview` command in `Infrastructure/bin/ask:113-145` or dispatch `500-555`; projection policy in `projection_engine.py:63-113` | missing | F | High |
| Codex renderer budget parity | User plan P0.3; Codex renderer source cited in plan | `skills_budget` shells to `verify_runtime_budget.py`; word/token estimate at `verify_runtime_budget.py:100-105` | partial | D | High |
| Codex-native command handles | User plan P0.4 | `check_command_handles` at `command_surface.py:926-977`; proof at `skills_impl.py:1110-1237`; live check fails | implemented_not_enforced | C | High |
| Explicit and implicit invocation preview | User plan P0.5 | `skills parse` exists at parser lines `133-134`; no `inject-preview` or `implicit-preview` command | partial | D | High |
| Doctor as SDK conformance command | User plan P1.7 | `skills_doctor` exists at `skills_impl.py:3126-3235`; no `--codex-parity` flag at `Infrastructure/bin/ask:138-140` | partial | C | High |
| Config-rule parity | User plan P1.8 | No `skills config explain`; no command metadata action for config parity | missing | F | High |
| Package/install safety | User plan P1.9; Oagen manifest/provenance lines 135-143 | `skills package` exists; sync copy rejects symlink sources; no package verify command or digest lock schema | partial | C- | High |
| Plugin skills first-class Codex skills | User plan P1.10 | Plugin-owned hiding/router policy exists in `runtime_surface_policy.py:76-86`; no Codex `plugin:skill` namespace proof | partial | C- | Medium |
| Workouts as conformance tests | User plan P2.11 | Workouts/evals exist; no conformance suite for malformed Codex package, config disable, renderer truncation, or injection | scaffolded | D | Medium |
| Generated artifact manifest | Oagen analysis lines 34, 61, 135-143 | `.skillsets/command-surface.json` exists; no `.skills-sdk-manifest.json` equivalent | partial | D | High |
| Compatibility snapshots and diffs | Oagen analysis lines 35, 62, 151-159 | Existing tests assert fields; no baseline/candidate public-surface diff command | missing | F | High |
| Pure emitter boundaries | Oagen analysis lines 43-45, 69-81 | CLI and payload assembly live in `skills_impl.py`; no parser/IR/emitter/writer split | missing | D | High |
| AI-safe deterministic boundaries | Oagen analysis lines 37, 52, 58-65 | Validators exist; no generation governance pipeline consuming deterministic diffs | partial | C- | Medium |

## 4. Gap Register

### GAP-001: Codex Loader Parity Oracle Is Missing

**Category:** runtime

**Current State:**  
`ask` can sync projections and inspect runtime budget. It cannot preview Codex’s actual skill loader result: roots, precedence, disabled paths, plugin namespace, parse failures, dedupe, and bundled/system skill behavior. `Infrastructure/bin/ask:113-145` registers existing skills actions, and `Infrastructure/bin/ask:500-555` dispatches them; neither includes `load-preview` or `--codex-parity`.

**Expected State:**  
`ask skills load-preview --codex-parity --json` returns the exact skill set Codex would load, including root source, scope, plugin id, path, disabled reason, parse errors, and final order.

**Evidence Basis:**  
User plan P0.2 and Oagen patterns for deterministic source normalization and compatibility surfaces.

**Code Evidence:**  
- `Infrastructure/bin/ask:113-145`: skills parser has budget, handles, resolve, parse, proof, prove, explain, doctor, package, profiles, events, memory.
- `Infrastructure/bin/ask:500-555`: dispatch has no parity preview.
- `Infrastructure/scripts/lifecycle-and-sync/projection_engine.py:63-113`: projection mode precedence is CLI/env/default, not Codex loader semantics.

**Risk:**  
The repo can claim projection success while Codex would load a different set of skills or disable a skill.

**Severity:** Critical

**Fix Grade:** P0

**Recommended Fix:**  
Create `ask.services.skills.runtime_adapters.codex_loader` that mirrors Codex loader rules from the checked Codex source. Add `ask skills load-preview --codex-parity --json` and include it in `skills doctor --codex-parity`.

**Suggested Software / Method:**  
Python dataclasses or Pydantic-style typed dicts, JSON Schema for output, fixture workspaces, golden JSON snapshots.

**Files Likely To Change:**  
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py` initially, then extracted service module
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/codex_loader.py`
- `Infrastructure/config/schemas/skill-load-preview.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_load_preview.py`

**Validation Command:**  
`./bin/ask skills load-preview --codex-parity --json --robot`

**Acceptance Criteria:**  
- Reports Codex roots and selected skills in deterministic order.
- Reports disabled-by-name and disabled-by-path rules.
- Reports plugin namespace and plugin id.
- Fixture tests cover duplicate names, disabled rules, symlinks, invalid frontmatter, plugin roots, and bundled/system toggles.
- `skills doctor --codex-parity` blocks if loader parity fails.

### GAP-002: SkillPackage v1 Contract Is Not a Concrete Codex ABI Schema

**Category:** validation

**Current State:**  
`skills package` emits `skill-package-readiness.v1`, but there is no schema file for it. `fd . Infrastructure/config/schemas -t f` found only `selection-gate-severity.v1.schema.json` and `skill-doctor.v1.schema.json`.

**Expected State:**  
A versioned `skill-package.v1.schema.json` and `skill-package-readiness.v1.schema.json` define Codex-native fields for `SKILL.md` frontmatter and optional `agents/openai.yaml`: `name`, `description`, `short_description`, `interface`, `dependencies`, `policy`, `scope`, `plugin_id`, and `allow_implicit_invocation`.

**Evidence Basis:**  
User plan P0.1; Codex `SkillMetadata` and `SkillPolicy` source cited by plan; Oagen analysis lines 58-63.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2631-2721`: package readiness is derived from local frontmatter fields such as `version`, `compatible_roles`, `runtime_needs`, `maturity`, `provenance`, `share_readiness`.
- `Infrastructure/tests/test_ask_skills_package.py:24-41`: tests payload shape, but not against a schema.

**Risk:**  
SDK users can produce packages that satisfy Agent Skills Kit readiness but do not match Codex’s native loader contract.

**Severity:** Critical

**Fix Grade:** P0

**Recommended Fix:**  
Add `skill-package.v1.schema.json` for physical package metadata and `skill-package-readiness.v1.schema.json` for readiness output. Teach `skills package` and `skills doctor --codex-parity` to validate both.

**Suggested Software / Method:**  
JSON Schema Draft 7, fixture packages, required-vs-optional field matrices, schema validation in runtime and tests.

**Files Likely To Change:**  
- `Infrastructure/config/schemas/skill-package.v1.schema.json`
- `Infrastructure/config/schemas/skill-package-readiness.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_package.py`
- `Infrastructure/tests/test_ask_skills_package_contract.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`

**Validation Command:**  
`UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 --with pytest --with jsonschema python -m pytest Infrastructure/tests/test_ask_skills_package_contract.py -q`

**Acceptance Criteria:**  
- Missing Codex-required metadata is classified explicitly.
- Existing readiness fields remain stable or version-migrated.
- Schema validation is mandatory in tests.
- `skills package <target> --strict` fails for schema-invalid package metadata.

### GAP-003: Runtime Proof Can Pass Without Codex Runtime Readiness

**Category:** runtime

**Current State:**  
`skills_proof` accepts either `.codex` or `.agents` readiness. Live `./bin/ask skills proof context7 --json --robot` passed with `codex_user_runtime_ready=false`, `agents_user_runtime_ready=true`, and `runtime_satisfied_by=agents_user_runtime`.

**Expected State:**  
Codex ABI proof must require Codex runtime readiness in Codex-targeted lanes. Cross-client readiness can remain a separate compatibility mode.

**Evidence Basis:**  
User plan says Codex itself is the runtime ABI.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1158-1164`: computes Codex and agents readiness, then `user_runtime_ready = codex_runtime_ready or agents_runtime_ready`.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1176-1183`: required gate is `user_runtime_ready`, explicitly accepting either runtime.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1193-1199`: reports which runtime satisfied proof.

**Risk:**  
A Codex-specific implementation plan can be marked reachable while Codex will not load or inject the skill.

**Severity:** Critical

**Fix Grade:** P0

**Recommended Fix:**  
Add `--runtime-target codex|agents|any` to `skills proof`; default `doctor --codex-parity` to `codex`. Preserve `any` only for cross-client inventory.

**Suggested Software / Method:**  
CLI flags, unit tests for each runtime target, live fixture symlink tests.

**Files Likely To Change:**  
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/tests/test_ask_skills_doctor.py`
- `Infrastructure/tests/test_ask_skills_proof.py`

**Validation Command:**  
`./bin/ask skills proof context7 --runtime-target codex --json --robot`

**Acceptance Criteria:**  
- Codex-targeted proof fails when `.codex/skills` is not ready.
- Any-runtime proof can still pass for cross-client compatibility.
- Doctor parity mode reports Codex readiness separately from agents readiness.

### GAP-004: Generated Command-Handle Check Is Opt-In, and It Currently Fails

**Category:** validation

**Current State:**  
Generated command-handle checking exists but is not part of `repo doctor`’s command handle signal. Live `./bin/ask skills handles --check --check-command-handles --no-handles --json --robot` exited 2 with projection drift and generated command-handle check failure.

**Expected State:**  
`repo doctor` and SDK conformance must include generated command-handle parity, because command handles are the runtime ABI for mentionability and progressive disclosure.

**Evidence Basis:**  
User plan P0.4; agent-native reviewer live evidence.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/repo_impl.py:870-873`: `repo doctor` calls `skills_handles(repo_root, check=True, include_handles=False)` without `check_command_handle_files=True`.
- `scripts/lifecycle-and-sync/command_surface.py:926-977`: generated command-handle check exists.
- Live command reported `command_surface_projection_check.status=fail` and `command_handle_check.status=fail`.

**Risk:**  
Repo-level health can be green while runtime command handles are missing or stale.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:**  
Wire `check_command_handle_files=True` into `repo doctor` command-handle signal. If that is too noisy for all repo doctors, make it a separate blocking `generated_command_handles` signal and require it in Skills SDK closeout.

**Suggested Software / Method:**  
Existing `check_command_handles`, repo doctor signal test, generated projection snapshot update.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/commands/repo_impl.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `.skillsets/command-surface.json` if projection is refreshed intentionally
- `.agents/skills/**` generated handles if sync is intentionally run

**Validation Command:**  
`./bin/ask skills handles --check --check-command-handles --no-handles --json --robot`

**Acceptance Criteria:**  
- Repo doctor fails or blocks when generated command handles drift.
- Live generated handle check passes after an intentional projection refresh.
- Drift output lists exact missing or stale handle files.

### GAP-005: Codex Renderer Budget Parity Is Absent

**Category:** context

**Current State:**  
`ask runtime budget` delegates to `verify_runtime_budget.py`, which counts default-visible skills and estimates description tokens from word counts. It does not mirror Codex’s renderer algorithm, root aliasing, shrink-then-omit behavior, or warning semantics.

**Expected State:**  
`ask skills render-preview --codex-parity --json` should reproduce Codex’s available-skill rendering budget and warnings.

**Evidence Basis:**  
User plan P0.3; Oagen’s runtime behavior policy pattern.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:895-904`: `skills_budget` shells to `verify_runtime_budget.py`.
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:100-105`: estimates token count from word count.
- `Infrastructure/scripts/lifecycle-and-sync/runtime_surface_policy.py:76-86`: visibility is repo policy, not Codex renderer.

**Risk:**  
A skill tree can pass repo budget while rendering poorly or being omitted by Codex.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:**  
Add a Codex renderer adapter that accepts the loader-preview output and emits rendered metadata, character budget, shrink events, omissions, and warnings.

**Suggested Software / Method:**  
Golden fixtures copied from Codex renderer behavior, snapshot tests, JSON output schema.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/codex_render.py`
- `Infrastructure/bin/ask`
- `Infrastructure/config/schemas/skill-render-preview.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_render_preview.py`

**Validation Command:**  
`./bin/ask skills render-preview --codex-parity --json --robot`

**Acceptance Criteria:**  
- Preview reports total rendered bytes/chars.
- Preview reports skills with shortened descriptions.
- Preview reports omitted skills and reasons.
- Tests include over-budget and duplicate-name fixtures.

### GAP-006: Invocation Preview Is Only a Parse/Resolve Approximation

**Category:** runtime

**Current State:**  
`skills parse` resolves `$` and `@` handles from prompt text. There is no command that answers “would Codex inject this skill body?” or “would Codex attribute this shell command or `SKILL.md` read as implicit invocation?”

**Expected State:**  
`ask skills inject-preview` and `ask skills implicit-preview` should mirror Codex explicit and implicit invocation semantics.

**Evidence Basis:**  
User plan P0.5.

**Code Evidence:**  
- `Infrastructure/bin/ask:131-135`: `resolve`, `parse`, and `proof` exist.
- `Infrastructure/bin/ask:500-555`: no injection preview dispatch.

**Risk:**  
SDK users can know a handle exists without knowing whether Codex will actually inject or attribute it.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:**  
Add `inject-preview` for user text and selection inputs; add `implicit-preview` for shell command JSON and file-read events. Use loader-preview and config-rule-preview as inputs.

**Suggested Software / Method:**  
JSON Schema, table-driven fixtures, Codex source parity tests.

**Files Likely To Change:**  
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/codex_invocation.py`
- `Infrastructure/tests/test_ask_skills_inject_preview.py`

**Validation Command:**  
`./bin/ask skills inject-preview 'use $context7 for docs' --codex-parity --json --robot`

**Acceptance Criteria:**  
- Explicit mention, picker selection, path mention, script execution, and `SKILL.md` read cases are covered.
- Disabled skills are not injected.
- `allow_implicit_invocation=false` is honored.

### GAP-007: Doctor Is Strong but Not Yet the SDK Conformance Command

**Category:** validation

**Current State:**  
`skills doctor` resolves, proofs, audits, checks metadata, reports package readiness, and emits lifecycle events. It does not expose `--codex-parity`, and its schema references for events, lifecycle, profiles, package, and memory are inline contract references rather than concrete schema files.

**Expected State:**  
`ask skills doctor <target> --codex-parity --json` should run package schema checks, loader preview, render preview, config-rule preview, injection preview, command-handle proof, and install provenance.

**Evidence Basis:**  
User plan P1.7; Oagen compatibility + smoke separation.

**Code Evidence:**  
- `Infrastructure/bin/ask:138-140`: doctor parser only has `--strict`.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:3126-3235`: doctor implementation calls proof/audit/metadata checks but no Codex loader/render/config/injection preview.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1516-1534`: only doctor schema has a concrete path; other contract refs carry missing schema rationale.

**Risk:**  
Doctor can become a generic health check rather than the conformance answer for Codex-native skill packages.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Add `--codex-parity` to doctor and fail closed on missing parity subchecks. Keep non-parity doctor as a compatibility diagnostic.

**Suggested Software / Method:**  
Nested checker orchestration, stable check IDs, JSON Schema, snapshot tests.

**Files Likely To Change:**  
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_doctor_contract.py`

**Validation Command:**  
`./bin/ask skills doctor context7 --codex-parity --json --robot`

**Acceptance Criteria:**  
- Parity mode blocks on loader, render, config, injection, package schema, or Codex runtime proof failure.
- Non-parity mode remains available for exploratory diagnostics.
- Snapshot tests lock parity check IDs and status precedence.

### GAP-008: SDK Layers Are Named but Not Enforced as Deep Modules

**Category:** architecture

**Current State:**  
The doctor schema enumerates SDK layers, and `skills-sdk.json` names a planning contract. Most behavior still lives in `Infrastructure/scripts/lib/ask/commands/skills_impl.py`.

**Expected State:**  
Contracts, Catalog, Authoring, Validation, Packaging, Runtime Adapters, Evidence, and Memory should be real modules with import boundaries and tests.

**Evidence Basis:**  
User plan P1.6; improve-codebase-architecture Deep Module Examiner; Oagen parser/IR/emitter separation.

**Code Evidence:**  
- `Infrastructure/config/schemas/skill-doctor.v1.schema.json:108-123`: SDK layer enum exists.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:3126-3235`: doctor orchestration lives in command glue.
- `Infrastructure/config/skills-sdk.json:3`: status is `planning_contract`.

**Risk:**  
Future changes accumulate in command glue, making ABI behavior hard to test or reuse.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Extract the first bounded slice: `contracts.schemas`, `catalog.resolve`, `runtime_adapters.proof`, and `validation.doctor`. Keep CLI output unchanged.

**Suggested Software / Method:**  
Small Python service modules, import-linter or custom AST import test, snapshot-preserving refactor.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/contracts.py`
- `Infrastructure/scripts/lib/ask/services/skills/catalog.py`
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters.py`
- `Infrastructure/scripts/lib/ask/services/skills/doctor.py`
- `Infrastructure/tests/test_ask_skills_doctor.py`
- `Infrastructure/tests/test_skills_sdk_layer_boundaries.py`

**Validation Command:**  
`python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py Infrastructure/tests/test_skills_sdk_layer_boundaries.py -q`

**Acceptance Criteria:**  
- CLI remains a facade.
- Service modules can be imported without CLI parser side effects.
- Layer test rejects command module imports from service modules.
- Doctor JSON snapshots are unchanged unless intentionally versioned.

### GAP-009: Config-Rule Parity Is Missing

**Category:** governance

**Current State:**  
No `ask skills config explain` command exists. Repo policy handles visible/hidden skills, but Codex config rules such as bundled enablement, include instructions, and per-skill enable/disable selectors are not modeled.

**Expected State:**  
`ask skills config explain --json` should show selected config layers, rules, final enable/disable decision, and disabled path reporting.

**Evidence Basis:**  
User plan P1.8.

**Code Evidence:**  
- `Infrastructure/bin/ask:113-145`: no config subparser under skills.
- `Infrastructure/scripts/lifecycle-and-sync/runtime_surface_policy.py:76-86`: repo selection policy only.

**Risk:**  
`ask sync` or `doctor` can report skill availability while Codex config disables it.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Implement config-rule parser/preview using Codex config rule semantics and fixtures for name selectors, path selectors, duplicate names, and later-rule overrides.

**Suggested Software / Method:**  
JSON fixture tests, selector normalization, explicit source-layer ordering.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/codex_config.py`
- `Infrastructure/bin/ask`
- `Infrastructure/tests/test_ask_skills_config_explain.py`

**Validation Command:**  
`./bin/ask skills config explain --json --robot`

**Acceptance Criteria:**  
- Explains every rule that affected a skill.
- Reports disabled paths and selectors.
- Feeds loader-preview and doctor parity checks.

### GAP-010: Package Verification and Supply-Chain Safety Are Partial

**Category:** governance

**Current State:**  
`skills package` checks metadata readiness and optional checkout evidence. Sync copy code rejects symlink source trees. There is no `ask skills package verify` with pinned refs, trusted source allowlist, provenance manifest, zip traversal rejection, quarantine staging, rollback journal, and digest lock.

**Expected State:**  
Package verification should be a first-class command and schema-backed supply-chain gate.

**Evidence Basis:**  
User plan P1.9; Oagen generated manifest pattern.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2631-2721`: package metadata readiness fields.
- `Infrastructure/bin/ask:141-144`: `skills package` supports target, `--strict`, `--checkout-test`; no verify action.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:5567-5602`: sync copy skips unsafe source symlinks.

**Risk:**  
The SDK can say a package is ready without proving source integrity, install safety, or rollback.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Add `ask skills package verify <target|archive|repo-ref>` with a manifest and staged verification. Reuse existing installer hardening where possible.

**Suggested Software / Method:**  
Digest lock JSON, quarantine temp directory, zip traversal checks, symlink escape tests, rollback journal.

**Files Likely To Change:**  
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/services/skills/packaging.py`
- `Infrastructure/config/schemas/skill-package-verification.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_package_verify.py`

**Validation Command:**  
`./bin/ask skills package verify Skills/agent-ops/context7 --json --robot`

**Acceptance Criteria:**  
- Rejects path traversal and symlink escape fixtures.
- Emits digest lock and rollback journal path.
- Blocks untrusted or unpinned remote sources unless explicitly allowed by policy.

### GAP-011: Compatibility Snapshots and Diffs Are Missing

**Category:** validation

**Current State:**  
Tests assert selected fields, and doctor has a schema. There is no baseline/candidate compatibility extraction and diff for public Skills SDK surfaces.

**Expected State:**  
Public surfaces should be snapshotted and diffed: CLI commands, JSON payloads, schemas, command metadata, docs anchors, lifecycle events, package readiness fields, runtime cards, deep module public APIs, and skill handles.

**Evidence Basis:**  
Oagen compatibility snapshot pattern in the evidence document.

**Code Evidence:**  
- `Infrastructure/tests/test_ask_skills_doctor.py:21-29`: schema validation can skip if `jsonschema` is absent.
- `Infrastructure/tests/test_ask_skills_package.py:24-41`: field assertions, no schema-backed snapshot.
- `Infrastructure/scripts/lib/ask/command_metadata.py:7-47`: command surface is static data without compatibility diff gate.

**Risk:**  
Agents and integrations can break due to quiet JSON or CLI changes.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Add `ask skills compat snapshot` and `ask skills compat diff` or an internal validator invoked by CI. Start with doctor/package/handles/runtime budget.

**Suggested Software / Method:**  
JSON snapshots, semantic diff classification, allowlist approvals file, CI gate.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/compat.py`
- `Infrastructure/config/schemas/skills-sdk-compat-snapshot.v1.schema.json`
- `Infrastructure/tests/test_skills_sdk_compat.py`
- `.harness/compat/skills-sdk-baseline.json`

**Validation Command:**  
`./bin/ask skills compat diff --baseline .harness/compat/skills-sdk-baseline.json --json --robot`

**Acceptance Criteria:**  
- Breaking changes fail.
- Additive changes pass with record.
- Approved exceptions require a named owner and expiry.

### GAP-012: Doctor Contract Validation Is Optional in Tests

**Category:** validation

**Current State:**  
`test_ask_skills_doctor.py` validates against JSON Schema only when `jsonschema` is importable.

**Expected State:**  
Contract tests should fail clearly when the schema validator dependency is missing.

**Evidence Basis:**  
User requirement to prefer validators over reminders; Oagen compatibility governance.

**Code Evidence:**  
- `Infrastructure/tests/test_ask_skills_doctor.py:21-23`: returns early if `jsonschema` is absent.

**Risk:**  
CI or local validation can appear green while skipping the public contract proof.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:**  
Make `jsonschema` mandatory for contract tests. Use ephemeral uv dependencies in wrapper validation if the repo has no root package install.

**Suggested Software / Method:**  
`uv run --python 3.12 --with pytest --with jsonschema python -m pytest ...`

**Files Likely To Change:**  
- `Infrastructure/tests/test_ask_skills_doctor.py`
- `scripts/validate_all_impl.sh` if needed for dependency provisioning

**Validation Command:**  
`UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 --with pytest --with jsonschema python -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q`

**Acceptance Criteria:**  
- Missing validator dependency produces a clear test failure or wrapper installs it ephemerally.
- Contract schema validation always runs in the contract test lane.

### GAP-013: Runtime Surface Can Hide Validation Errors

**Category:** runtime

**Current State:**  
`runtime surface` calls the same budget check as `runtime budget`, stores `runtime_surface_status`, then changes result status to success and clears errors when the only errors are validation errors.

**Expected State:**  
Advisory surfaces can avoid a nonzero exit only if the machine-readable status still preserves blocking state and the command name makes advisory behavior explicit.

**Evidence Basis:**  
User requirement for runtime truth and false-success prevention.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/runtime.py:26-44`: `runtime surface` mutates error status to success.

**Risk:**  
Automation sees success while the embedded runtime surface says the underlying validation failed.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Preserve `status=error` for validation failures or add `--advisory` to opt into success-with-findings. Keep errors in the payload either way.

**Suggested Software / Method:**  
CLI behavior tests and envelope schema expectations.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/commands/runtime.py`
- `Infrastructure/tests/test_ask_runtime.py`

**Validation Command:**  
`./bin/ask runtime surface --json --robot`

**Acceptance Criteria:**  
- Validation failure remains visible in top-level status unless `--advisory` is supplied.
- Machine-readable payload never drops validation errors.

### GAP-014: Runtime Proof Checks Existence, Not Content Provenance

**Category:** traceability

**Current State:**  
`skills_proof` checks whether workspace and user command-handle files exist and whether symlinks point to expected runtime roots. It does not compare handle file content, source hash, generated provenance, or `agents/openai.yaml` content for the target.

**Expected State:**  
Proof should ensure the runtime handle injects the exact canonical source or generated handle content expected by the current command-surface projection.

**Evidence Basis:**  
User plan P0.4; Oagen manifest-backed provenance pattern.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1144-1152`: gates are booleans for resolver and file existence.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:1200-1220`: proof embeds command handle check and runtime file paths, not target content hash parity.

**Risk:**  
Stale or hand-edited runtime files can satisfy proof if the target handle’s violation list is empty or hidden by symlink behavior.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:**  
Add target-level content/provenance hash checks to `skills_proof`, using command-surface expected rows and canonical source hash.

**Suggested Software / Method:**  
SHA-256 source/content fields, generated manifest, stale-handle fixtures.

**Files Likely To Change:**  
- `scripts/lifecycle-and-sync/command_surface.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/tests/test_ask_skills_proof.py`

**Validation Command:**  
`./bin/ask skills proof context7 --json --robot`

**Acceptance Criteria:**  
- Proof reports source hash, expected handle hash, actual handle hash, and parity status.
- Stale runtime file fixture fails.
- Symlinked rooted handles are explicitly classified.

### GAP-015: Plugin Skill Namespace Parity Is Partial

**Category:** skills

**Current State:**  
Plugin-owned skill visibility is handled through repo policy, and duplicate plugin names are baselined in runtime budget. The code does not prove Codex `plugin:skill` namespace, display name, plugin id, or cache provenance parity.

**Expected State:**  
Plugin skills should be first-class Codex skills with namespace, plugin id, display name, root path, and provenance preserved in package, projection, doctor, and handle commands.

**Evidence Basis:**  
User plan P1.10.

**Code Evidence:**  
- `Infrastructure/scripts/lifecycle-and-sync/runtime_surface_policy.py:76-86`: plugin-owned visibility filtering.
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:46-80`: baselines known plugin name collisions.

**Risk:**  
Plugin skill ownership and runtime naming can drift, causing collisions or wrong invocation targets.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:**  
Extend load-preview and package schemas with `plugin_id`, `plugin_namespace`, `display_name`, `plugin_root`, and cache provenance. Add collision tests.

**Suggested Software / Method:**  
JSON Schema, fixture plugins, namespace normalization tests.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/codex_loader.py`
- `Infrastructure/scripts/lib/ask/services/skills/packaging.py`
- `Infrastructure/tests/test_ask_plugin_skill_parity.py`

**Validation Command:**  
`./bin/ask skills load-preview --codex-parity --include-plugins --json --robot`

**Acceptance Criteria:**  
- Plugin skills use Codex namespace rules.
- Duplicate bare names are explained and disambiguated.
- Package/doctor payloads preserve plugin id.

### GAP-016: Skills SDK IR and Emitter Pipeline Are Missing

**Category:** architecture

**Current State:**  
The repo has many command surfaces and planning docs. It lacks a versioned `SkillSdkIR`, parser, normalizer, pure emitters, writer, generated manifest, and compatibility verifier.

**Expected State:**  
Canonical skill sources, command metadata, schemas, docs, runtime cards, and package metadata should normalize into `SkillSdkIR`. Emitters should produce schemas, docs, command metadata, fixtures, and runtime cards from that IR.

**Evidence Basis:**  
Oagen analysis lines 27-37 and 58-65.

**Code Evidence:**  
- `Infrastructure/config/skills-sdk.json:3`: `planning_contract`.
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`: broad command implementation still assembles many surfaces directly.

**Risk:**  
SDK surfaces will continue to drift because each command/document/test can evolve separately.

**Severity:** High

**Fix Grade:** P2

**Recommended Fix:**  
Prototype IR only for doctor/package/command-handle/runtime-card first. Do not attempt full repo generation until snapshots and parity commands exist.

**Suggested Software / Method:**  
JSON Schema + Python typed dataclasses; pure emitter functions returning `GeneratedFile` objects; writer with manifest.

**Files Likely To Change:**  
- `Infrastructure/config/schemas/skills-sdk-ir.v1.schema.json`
- `Infrastructure/scripts/lib/ask/services/skills/ir.py`
- `Infrastructure/scripts/lib/ask/services/skills/emitters/**`
- `Infrastructure/tests/test_skills_sdk_ir.py`

**Validation Command:**  
`python3 -m pytest Infrastructure/tests/test_skills_sdk_ir.py -q`

**Acceptance Criteria:**  
- IR records source evidence for every emitted field.
- Emitters do not write files directly.
- Generated manifest records input hashes and emitter versions.

### GAP-017: Workouts Are Not SDK Conformance Tests

**Category:** skills

**Current State:**  
Workouts and evals exist as quality machinery. They do not yet include conformance workouts for Codex loader, config disable, malformed package, renderer truncation, injected handle, implicit invocation, installer rollback, and plugin namespace.

**Expected State:**  
`ask skills conformance run` should execute deterministic fixture workouts and write evidence.

**Evidence Basis:**  
User plan P2.11; Oagen smoke verification pattern.

**Code Evidence:**  
- `skills_doctor` reports `outcome_proof_missing` for `context7` in the live doctor run.
- `Docs/reference/skill-authoring-validation-maturity-matrix.md` records live smoke machinery for skill-builder, but not Codex parity conformance.

**Risk:**  
Quality experiments exist, but SDK ABI regressions are not caught by a focused conformance suite.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:**  
Add `ask skills conformance run --suite codex-parity` with deterministic fixtures.

**Suggested Software / Method:**  
Pytest fixture workspaces, JSONL event log, evidence directory, schema validation.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/conformance.py`
- `Infrastructure/tests/fixtures/skills/codex-parity/**`
- `Infrastructure/tests/test_ask_skills_conformance.py`

**Validation Command:**  
`./bin/ask skills conformance run --suite codex-parity --json --robot`

**Acceptance Criteria:**  
- Suite covers all P0 parity primitives.
- Evidence directory includes JSONL events and final summary.
- CI can run a fast deterministic subset.

### GAP-018: `next_command` Can Route Around the Active Gap

**Category:** workflow

**Current State:**  
Live `skills doctor context7` reports warnings for package metadata and outcome proof. Existing gap analysis notes that next-command routing can favor strict audit even when package/evidence is the current gap.

**Expected State:**  
`next_command` should route to the command that directly addresses the highest-priority failing or warning check.

**Evidence Basis:**  
User request asks for “what, how, why and priority order”; claim-vs-evidence verification.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:3126-3235`: doctor builds warnings and checks.
- Existing gap analysis lines 367-394 identify next-command misrouting.

**Risk:**  
Agents follow an apparently authoritative next command and spend time proving a surface that already passes.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:**  
Update `_skill_doctor_next_command` precedence: blockers first, then package metadata repair, then outcome proof/conformance, then strict audit as secondary.

**Suggested Software / Method:**  
Table-driven status-to-command mapping tests.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/tests/test_ask_skills_doctor.py`

**Validation Command:**  
`./bin/ask skills doctor context7 --json --robot | jq '.data.skill_doctor.next_command'`

**Acceptance Criteria:**  
- Package metadata warnings route to package repair/proof.
- Outcome proof warnings route to `skills prove` or conformance run.
- Strict audit remains available but is not the default for unrelated warnings.

### GAP-019: Current Command-Handle Contract Changed Without Version Boundary

**Category:** api-contract

**Current State:**  
`command-handle-write.v1` and `command-handle-check.v1` now include rooted symlink skip semantics. The same schema versions represent changed status semantics, including pass-with-skipped rows.

**Expected State:**  
Behavioral contract changes should bump schema version or include a clear compatibility flag and migration note.

**Evidence Basis:**  
API contract reviewer finding.

**Code Evidence:**  
- `scripts/lifecycle-and-sync/command_surface.py:914-922`: write payload includes `schema_version=command-handle-write.v1`, `skipped`, and pass/fail status.
- `scripts/lifecycle-and-sync/command_surface.py:970-977`: check payload includes `schema_version=command-handle-check.v1`, `skipped`, and pass/fail status.
- `Infrastructure/tests/test_command_surface_handles.py:292-344`: write skips rooted symlink lane.
- `Infrastructure/tests/test_command_surface_handles.py:346-374`: check accepts rooted symlink lane and reports zero checked rows with skips.

**Risk:**  
Consumers that gate on previous violation semantics can silently accept a state they formerly rejected.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**  
Bump to `command-handle-write.v2` and `command-handle-check.v2`, or emit `compatibility_semantics=rooted_symlink_skipped_v1_1` and add a migration note plus tests.

**Suggested Software / Method:**  
Schema versioning, compatibility diff tests, migration notes.

**Files Likely To Change:**  
- `scripts/lifecycle-and-sync/command_surface.py`
- `Infrastructure/tests/test_command_surface_handles.py`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`

**Validation Command:**  
`python3 -m pytest Infrastructure/tests/test_command_surface_handles.py -q`

**Acceptance Criteria:**  
- Consumers can distinguish old violation semantics from new skip semantics.
- Snapshot tests prove the version boundary.

### GAP-020: Trace Evidence Is Present but Not Replayable for SDK Conformance

**Category:** traceability

**Current State:**  
`CallResult` includes trace IDs and telemetry fields. Lifecycle events exist in payloads. There is no conformance run evidence stream that records command inputs, subcheck outcomes, recovery events, and final status as replayable JSONL.

**Expected State:**  
Every conformance run should write an evidence directory with `events.jsonl`, `commands.jsonl`, `summary.json`, and relevant snapshots.

**Evidence Basis:**  
Audit categories for trace/session evidence; Oagen manifest and smoke verification.

**Code Evidence:**  
- `Infrastructure/scripts/lib/ask/envelope.py:68-84`: trace ID and telemetry exist.
- `skills package` and `skills doctor` live runs emit lifecycle events, but only inside command output.

**Risk:**  
Failures are hard to replay, and claims depend on transient terminal output.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:**  
Add `ask skills conformance run --evidence-dir` that writes structured evidence and references it from doctor parity mode.

**Suggested Software / Method:**  
JSONL events, summary schema, command transcript redaction, artifact manifest.

**Files Likely To Change:**  
- `Infrastructure/scripts/lib/ask/services/skills/evidence.py`
- `Infrastructure/config/schemas/skills-conformance-evidence.v1.schema.json`
- `Infrastructure/tests/test_ask_skills_conformance_evidence.py`

**Validation Command:**  
`./bin/ask skills conformance run --suite codex-parity --evidence-dir /private/tmp/skills-conformance --json --robot`

**Acceptance Criteria:**  
- Evidence path is returned in JSON.
- JSONL validates against schema.
- Final summary links to subcheck snapshots.

## 5. Contradictions

### CONTRADICTION-001: “Runtime proof passed” vs “Codex runtime was not ready”

**Claim:** `skills proof context7` can be treated as runtime reachability proof.

**Actual Implementation:** Proof accepts either `.codex` or `.agents`. Live proof passed with `codex_user_runtime_ready=false` and `agents_user_runtime_ready=true`.

**Evidence:** `skills_impl.py:1158-1164`, `skills_impl.py:1176-1183`, live `skills proof context7`.

**Severity:** Critical

**Operational Impact:** Codex ABI readiness can be overclaimed.

**Recommended Fix:** Add `--runtime-target codex` and wire it into parity doctor.

### CONTRADICTION-002: “Runtime surface” vs top-level success after validation errors

**Claim:** `ask runtime surface` reports runtime surface status.

**Actual Implementation:** `runtime.py` can convert validation-error status to success and clear errors for surface mode.

**Evidence:** `Infrastructure/scripts/lib/ask/commands/runtime.py:34-43`.

**Severity:** High

**Operational Impact:** Automation can treat a failing runtime surface as successful.

**Recommended Fix:** Preserve top-level failure or make advisory mode explicit.

### CONTRADICTION-003: “Contract schemas” vs missing schema artifacts

**Claim:** Doctor payload exposes consumer-usable contract schema references.

**Actual Implementation:** Only doctor has a concrete path; events, lifecycle_event, profiles, package, and memory are inline experimental contracts.

**Evidence:** `skills_impl.py:1516-1534`; live `skills doctor context7` output.

**Severity:** Medium

**Operational Impact:** Compatibility tooling cannot validate those referenced surfaces.

**Recommended Fix:** Add concrete schemas or mark those fields as `documented_only` until schemas exist.

### CONTRADICTION-004: “SDK contract” vs `planning_contract`

**Claim:** `skills-sdk.json` describes an SDK extraction contract.

**Actual Implementation:** The file status is `planning_contract`, and command surfaces do not enforce most extraction fields.

**Evidence:** `Infrastructure/config/skills-sdk.json:2-11`; `Infrastructure/bin/ask:113-145`.

**Severity:** High

**Operational Impact:** Future agents may treat a plan as live conformance.

**Recommended Fix:** Add a validator that classifies every section and blocks unlabelled plan-only claims.

### CONTRADICTION-005: “Command-handle contract v1” vs changed skip semantics

**Claim:** `command-handle-check.v1` and `command-handle-write.v1` identify stable payload contracts.

**Actual Implementation:** New rooted symlink skip semantics changed pass/fail behavior under the same version.

**Evidence:** `command_surface.py:914-922`, `command_surface.py:970-977`, `test_command_surface_handles.py:292-374`.

**Severity:** High

**Operational Impact:** Consumers may silently accept a state they previously treated as invalid.

**Recommended Fix:** Version the contract or add a compatibility flag and migration test.

## 6. Missing Features

### Runtime state

- Missing Codex loader-preview.
- Missing Codex renderer-preview.
- Missing Codex injection-preview.
- Missing Codex config-rule explanation.
- Missing Codex-targeted proof mode.

### Command selection

- Missing stable SDK primitive commands: `load-preview`, `render-preview`, `inject-preview`, `implicit-preview`, `package verify`, `config explain`, `conformance run`.
- Existing command metadata does not expose parity primitives.

### Verification

- Missing compatibility snapshots for doctor/package/handles/runtime surfaces.
- Missing live Codex smoke proof.
- Missing target-level runtime handle hash proof.

### Validation

- Missing package schema.
- Missing lifecycle/event/profile/memory schema artifacts.
- Optional schema validation in doctor tests.
- Generated handle parity not in main repo doctor lane.

### Architecture enforcement

- Missing SDK module boundaries.
- Missing parser/normalizer/IR/emitter/writer/verifier separation.
- Missing dependency-layer tests.

### Traces

- Missing conformance JSONL evidence.
- Missing replayable command transcripts for parity runs.
- Missing final conformance status artifact.

### Context

- Missing Codex renderer budget parity.
- Missing stale context detection for skill descriptions after projection.
- Missing root alias/render warnings parity.

### Skills

- Missing conformance workouts for P0 parity.
- Missing plugin namespace conformance fixtures.
- Missing package metadata repair primitive.

### Recovery

- Missing stale generated handle recovery handler.
- Missing Codex symlink repair handler.
- Missing config disable mismatch recovery.
- Missing package snapshot drift recovery.

### Governance

- Missing package verify with provenance lock.
- Missing compatibility exception approval file.
- Missing AI-assisted generation boundary workflow.

### CI/CD

- CI has strong skill quality and validation jobs, but does not currently gate Codex parity primitives because those primitives do not yet exist.

### Observability

- Trace IDs exist; conformance evidence storage and replay are absent.

## 7. Fix Roadmap

### Phase 1 — Critical Trust Boundary Fixes

**Objective:** Stop false-success and stale-runtime claims.

**Fixes included:**
- GAP-003: `skills proof --runtime-target codex`.
- GAP-004: generated command-handle check in repo doctor.
- GAP-012: mandatory doctor schema validation.
- GAP-013: preserve runtime-surface validation failures.
- GAP-018: fix doctor `next_command` precedence.

**Files likely affected:**
- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/commands/repo_impl.py`
- `Infrastructure/scripts/lib/ask/commands/runtime.py`
- `Infrastructure/tests/test_ask_skills_doctor.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `Infrastructure/tests/test_ask_runtime.py`

**Validation gates:**
- `./bin/ask skills handles --check --check-command-handles --no-handles --json --robot`
- `./bin/ask skills proof context7 --runtime-target codex --json --robot`
- `./bin/ask runtime surface --json --robot`
- `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py Infrastructure/tests/test_ask_repo_doctor.py -q`

**Expected risk reduction:**  
Eliminates the biggest false-success paths before broader SDK work.

### Phase 2 — Mechanical Enforcement

**Objective:** Turn contracts into schemas, snapshots, and enforced module boundaries.

**Fixes included:**
- GAP-002: SkillPackage schema.
- GAP-007: `doctor --codex-parity` scaffolding with check slots.
- GAP-008: deep module extraction for doctor/package/proof.
- GAP-011: compatibility snapshots/diffs.
- GAP-019: command-handle version boundary.

**Files likely affected:**
- `Infrastructure/config/schemas/**`
- `Infrastructure/scripts/lib/ask/services/skills/**`
- `Infrastructure/tests/test_ask_skills_package_contract.py`
- `Infrastructure/tests/test_skills_sdk_compat.py`
- `scripts/lifecycle-and-sync/command_surface.py`

**Validation gates:**
- `python3 -m pytest Infrastructure/tests/test_ask_skills_package_contract.py Infrastructure/tests/test_skills_sdk_compat.py Infrastructure/tests/test_command_surface_handles.py -q`
- `./bin/ask skills doctor context7 --codex-parity --json --robot`

**Expected risk reduction:**  
Prevents schema drift and makes SDK layers testable.

### Phase 3 — Runtime Harness Maturity

**Objective:** Make Codex runtime behavior executable and replayable.

**Fixes included:**
- GAP-001: loader parity oracle.
- GAP-005: renderer parity preview.
- GAP-006: invocation preview.
- GAP-009: config-rule explain.
- GAP-014: target-level provenance proof.
- GAP-020: conformance evidence stream.

**Files likely affected:**
- `Infrastructure/scripts/lib/ask/services/skills/runtime_adapters/**`
- `Infrastructure/scripts/lib/ask/services/skills/evidence.py`
- `Infrastructure/config/schemas/skill-load-preview.v1.schema.json`
- `Infrastructure/config/schemas/skill-render-preview.v1.schema.json`
- `Infrastructure/tests/fixtures/skills/codex-parity/**`

**Validation gates:**
- `./bin/ask skills load-preview --codex-parity --json --robot`
- `./bin/ask skills render-preview --codex-parity --json --robot`
- `./bin/ask skills inject-preview 'use $context7 for docs' --codex-parity --json --robot`
- `./bin/ask skills config explain --json --robot`

**Expected risk reduction:**  
Moves from projection truth to Codex runtime truth.

### Phase 4 — Context and Skill Compression

**Objective:** Preserve rooted/latent tree leverage while proving Codex render/injection outcomes.

**Fixes included:**
- Codex render warnings in budget gates.
- Command handle provenance manifest.
- Conformance workouts for root routers and latent handles.
- Plugin namespace fixtures.

**Files likely affected:**
- `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py`
- `Infrastructure/scripts/validation-and-linting/check_context_budget.py`
- `.skills-sdk-manifest.json` or repo-native manifest path
- `Infrastructure/tests/fixtures/skills/codex-parity/**`

**Validation gates:**
- `./bin/ask skills conformance run --suite codex-parity --json --robot`
- `./bin/ask runtime budget --codex-parity --json --robot`

**Expected risk reduction:**  
Prevents context pressure and mentionability regressions.

### Phase 5 — Governance and Scaling

**Objective:** Add package supply-chain verification, AI-safe generation, and long-term compatibility governance.

**Fixes included:**
- GAP-010: package verify.
- GAP-016: IR/emitter pipeline prototype.
- AI-assisted generation workflow consuming deterministic diffs.
- Compatibility exception approvals.

**Files likely affected:**
- `Infrastructure/scripts/lib/ask/services/skills/ir.py`
- `Infrastructure/scripts/lib/ask/services/skills/emitters/**`
- `Infrastructure/scripts/lib/ask/services/skills/packaging.py`
- `Infrastructure/config/schemas/skills-sdk-ir.v1.schema.json`
- `.harness/compat/**`

**Validation gates:**
- `./bin/ask skills package verify Skills/agent-ops/context7 --json --robot`
- `./bin/ask skills compat diff --json --robot`
- `python3 -m pytest Infrastructure/tests/test_skills_sdk_ir.py -q`

**Expected risk reduction:**  
Makes generation sustainable without granting AI authority over truth.

## 8. Highest-Leverage Fixes

| Rank | Fix | Impact | Difficulty | Risk Reduced | Why First |
|---:|---|---:|---:|---|---|
| 1 | Add `--runtime-target codex` to `skills proof` | Very high | Low | False Codex readiness | Small patch; closes current live contradiction. |
| 2 | Wire generated command-handle check into repo doctor | Very high | Low | Missing/stale handles | Existing checker already exists and currently finds real failures. |
| 3 | Make doctor schema validation mandatory | High | Low | Contract drift | Changes a skip into deterministic proof. |
| 4 | Fix `runtime surface` error masking | High | Low | False success | Tiny surface with high trust impact. |
| 5 | Add package readiness schema | High | Medium | ABI mismatch | Converts package readiness from code convention into SDK contract. |
| 6 | Add `doctor --codex-parity` with stubbed hard slots | High | Medium | Scope drift | Creates one authoritative conformance entrypoint. |
| 7 | Add loader-preview parity oracle | Very high | Medium | Runtime mismatch | Most important Codex ABI primitive. |
| 8 | Add compatibility snapshots for doctor/package/handles | High | Medium | JSON/API drift | Prevents silent consumer breakage. |
| 9 | Extract doctor/proof/package services | Medium | Medium | Command glue sprawl | Enables safe evolution and layer tests. |
| 10 | Add conformance run evidence JSONL | Medium | Medium | Non-replayable proof | Makes future audits and regressions evidence-led. |

## 9. Implementation Advice

Build first:

- `skills proof --runtime-target codex`
- generated command-handle check in `repo doctor`
- mandatory schema validation
- package schema
- loader-preview parity oracle

Do not build yet:

- Full Skills SDK IR and all emitters across docs, runtime cards, schemas, and deep modules. Prototype only doctor/package/handles first.
- Broad autonomous generation workflows before compatibility snapshots and deterministic validators exist.
- Plugin marketplace packaging before package verify and provenance manifest are schema-backed.

Remove or simplify:

- Avoid adding more behavior directly to `skills_impl.py` without extracting a service boundary.
- Avoid treating `skills-sdk.json` as live truth until a validator maps each section to execution.
- Avoid duplicate command metadata edits once IR/emitter proof exists.

Should become a validator:

- Codex loader parity.
- Codex renderer budget parity.
- Doctor/package schema validation.
- Generated command-handle parity in repo doctor.
- SDK contract section status classification.
- Compatibility diff for public JSON and CLI surfaces.

Should become a schema:

- `skill-package.v1`
- `skill-package-readiness.v1`
- `skill-load-preview.v1`
- `skill-render-preview.v1`
- `skill-inject-preview.v1`
- `skills-sdk-compat-snapshot.v1`
- `skills-conformance-evidence.v1`

Should become a skill:

- A compact `skills-sdk-conformance` skill that routes operators through doctor parity, package verify, compat diff, and conformance run. It should not contain the full implementation; it should be a high-density router to executable commands.

Should become documentation:

- A short “Codex ABI contract” ADR after `load-preview`, `render-preview`, and `inject-preview` exist.
- Migration notes for command-handle v1 to v2 skip semantics.

Should become CI:

- Fast parity fixture suite.
- Schema validation for doctor/package snapshots.
- Generated command-handle parity.
- Compatibility diff against baseline.

Should remain manual:

- Approval of compatibility exceptions.
- Decision to broaden autonomous generation beyond bounded fixtures.
- Human acceptance of package trust policies and source allowlists.

## 10. Final Recommendation

Immediate next action: **ship a P0 trust-boundary patch before broader SDK implementation.**

Safest first patch:

1. Add `--runtime-target codex|agents|any` to `skills proof`.
2. Make `skills doctor --codex-parity` call proof with `--runtime-target codex`.
3. Wire generated command-handle checking into `repo doctor` or an explicitly blocking repo doctor signal.
4. Make doctor schema validation mandatory in contract tests.
5. Preserve runtime-surface validation errors instead of clearing them.

Highest-risk missing system: **Codex loader parity oracle.** Without it, every projection, package, and doctor claim is still a model of Codex rather than Codex runtime truth.

Best validation command to add first:

```bash
./bin/ask skills load-preview --codex-parity --json --robot
```

Broader Codex autonomy readiness: **not ready yet.** The project is ready for a bounded implementation prototype around doctor/package/handles parity. It is not ready for broad autonomous Skills SDK generation until Codex loader/render/injection/config parity, package schemas, compatibility snapshots, and conformance evidence are executable and enforced.
