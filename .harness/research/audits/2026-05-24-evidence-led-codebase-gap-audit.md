# Evidence-Led Codebase Gap Audit

Date: 2026-05-24

Project root: /Users/jamiecraik/dev/agent-skills

Output target: .harness/research/audits/2026-05-24-evidence-led-codebase-gap-audit.md

Primary skills used:
- improve-codebase-architecture
- testing

Researcher coverage:
- agent-native-reviewer: agent/user parity, command reachability, closeout parity
- api-contract-reviewer: CLI/API JSON contract and wrapper enforcement
- adversarial-reviewer: false-success paths, stale-state risk, partial parity failure modes

Selected architecture lenses:
- Deep Module Examiner
- Architectural Pattern Cartographer
- Pattern Catalog Skeptic
- Pragmatic Delivery Partner

Primary evidence documents:
- .harness/research/deep/2026-05-24-jamie-craik-evidence.md
- /Users/jamiecraik/dev/codex
- /Users/jamiecraik/dev/codex/.harness/research/deep/2026-05-24-codex-ecosystem-operational-review.md

Runtime evidence sampled:

| Command | Outcome | Audit Signal |
|---|---:|---|
| ./bin/ask repo status --json --robot | pass | Public wrapper is usable and emits a trace_id. |
| ./bin/ask repo doctor --json --robot | fail, exit 2 | Current repo health is blocked by generated command-handle drift: 3 violations. |
| ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot | fail, exit 2 | Command surface projection passes, generated command handles fail. |
| ./bin/ask skills proof testing --runtime-target codex --json --robot | fail, exit 2 | Codex user runtime is not ready for the testing command handle; Agents runtime is ready. |
| ./bin/ask skills package testing --json --robot | pass with warning | Package readiness exists, but the testing skill is a legacy capability missing share metadata. |
| ./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance-audit --json --robot | pass | Conformance writes JSONL/snapshots, but partial preview limitations can still pass. |
| wc -l key ask modules | pass | skills_impl.py is 6238 lines; repo_impl.py is 1634 lines; codex_preview.py is 856 lines; conformance.py is 408 lines. |

Important current-state caveat:

This is an audit artifact, not a repair patch. The repo may still be non-clean in this audit lane due to newly added evidence artifacts and unresolved runtime blockers. The audit did not attempt to repair command-handle drift, sync runtime projections, or mutate user runtime links.

## 1. Executive Summary

Overall maturity grade: B-

Trust-boundary grade: C+

Codex-runtime autonomy grade: C

The codebase is no longer mostly aspirational. Compared with the earlier state described in older research, it now has a real control plane: public ./bin/ask entrypoints, schema-backed skill doctor/package contracts, replayable conformance evidence, command-handle generation checks, runtime target proofs, capability lifecycle events, repo doctor decision packets, memory provider readiness, package verification safeguards, and CI/governance workflows.

The central problem is now stricter and more operational: several high-value surfaces can still say "pass" without proving the exact thing the evidence says must be trusted. The live repo doctor is blocked today by generated command-handle drift. Codex-targeted proof for the named testing skill fails because ~/.codex/skills is not pointing at this workspace runtime. The codex-parity conformance suite passes while embedding partial modeled-preview limitations. The public wrapper ./bin/ask is the documented entrypoint, but contract fixtures and many tests still execute Infrastructure/bin/ask directly.

Top 5 gaps:

1. Generated command-handle drift is live and repo-doctor-blocking.
2. Codex preview parity is modeled-only in key dimensions and can still pass conformance with blocked preview limitations.
3. Public ./bin/ask wrapper parity is not contract-tested for high-value JSON ABI surfaces.
4. Codex preview payloads declare codex-skill-runtime-preview.v1 but no corresponding schema file enforces that ABI.
5. Repo surface ownership debt is huge and mostly diagnostic: 17037 warning-class findings, dominated by tracked historical artifacts.

Top 5 risks:

1. False success: a conformance suite can pass even when the preview evidence says live ConfigLayerStack or plugin roots were not actually read.
2. Runtime mismatch: default "any" runtime proof can be satisfied by Agents runtime while Codex runtime is not ready.
3. Wrapper drift: users and agents call ./bin/ask, while implementation tests exercise Infrastructure/bin/ask.
4. Stale parity source: Codex preview source identity can report identified without validating every modeled Codex source file still exists.
5. Ownership noise: a large repo-surface diagnostic backlog can hide new unknown/generated surface drift.

Strongest existing foundations:

- ./bin/ask is a stable public wrapper and Infrastructure/bin/ask registers a broad command surface for repo, skills, runtime, reviewers, plugins, and validation.
- repo doctor produces a blocker-first decision packet with next_command, selected_next_command, signal classification, trace_id, and diagnostic debt.
- command-handle parity is now part of repo doctor, and the current failure is correctly blocking instead of being hidden.
- skills conformance writes replayable evidence files: skills-conformance-evidence.jsonl, skills-conformance-commands.jsonl, snapshots, and summary JSON.
- skills package verify has strong mutation-prevention tests for archive traversal, symlink escape, digest mismatch, untrusted provenance, and missing rollback journals.

Highest-leverage next fixes:

1. Repair current generated command-handle drift and add a small regression fixture for the exact code-fixes-triage and llm-wiki failure class.
2. Make codex-parity conformance fail or downgrade when preview.status is partial or blocked_checks are present in cases that claim parity.
3. Add codex-skill-runtime-preview.v1.schema.json and schema validation tests for load-preview, render-preview, config explain, inject-preview, and implicit-preview.
4. Extend wrapper contract fixtures to execute ./bin/ask, not only Infrastructure/bin/ask, for repo status, skills doctor, skills package, skills proof, and conformance.
5. Add a strict Codex-runtime closeout mode or changed-skill gate that requires ./bin/ask skills proof <handle> --runtime-target codex for touched command-visible skills.

## 2. Overall Gradecard

| Area | Grade | Confidence | Current Status | Main Gap | Recommended Fix |
|---|---:|---:|---|---|---|
| Repository as Control Plane | B | High | ask CLI, root AGENTS, UBIQUITOUS_LANGUAGE, .harness surfaces, schemas, workflows, and repo doctor exist. | Repo surface ownership debt is large and mostly diagnostic; source-of-truth discipline is present but noisy. | Classify or clean tracked_historical_artifact, tracked_generated_work_area, and unknown_surface categories; add thresholds for new debt. |
| Runtime Truth and Decision Packets | B- | High | repo doctor emits blocker-first packets, selected next command, trace_id, signal states, and package/memory/capability readiness. | Codex-targeted runtime truth is optional and currently fails for testing. | Add Codex-runtime proof requirements for changed command-visible skills and strict closeout lanes. |
| Claim-vs-Evidence Verification | C+ | High | tests, package verification, command-handle checks, conformance evidence, and validation commands exist. | Some "pass" claims include partial modeled evidence; wrapper/runtime entrypoint parity is under-tested. | Fail or annotate conformance parity when live-only dimensions are blocked; expand wrapper fixtures. |
| Mechanical Architecture Enforcement | C+ | Medium | Many validators and schemas exist; command-surface and repo doctor tests enforce key contracts. | ask command implementation remains concentrated in large command modules; no import-boundary gate for runtime adapter/service split. | Add import/layer tests for ask.commands, ask.services, ask.skills_sdk, and lifecycle scripts. |
| Harness Runtime Loop | B- | High | blocker classes, runtime failure payloads, next commands, lifecycle events, and conformance evidence dirs exist. | Attempt ledgers and recovery handlers are not unified across stale handles, Codex link drift, and preview limitations. | Add runtime-card/recovery-event payloads with attempt count, owner, retryability, and proof command. |
| Trace and Session Evidence | B- | Medium | trace_id appears in ask envelopes; conformance writes JSONL; historical artifacts include Codex event logs. | Ordinary doctor/proof/package runs do not emit a shared runtime evidence packet joining trace, artifact, git, PR, CI, and claim receipts. | Add a runtime evidence packet schema and optional --evidence-dir for high-value commands. |
| Context Engineering | B | High | load-preview, render-preview, config explain, inject-preview, implicit-preview, budget, and memory search exist. | Preview status is modeled and partial; traversal depth truncation is silent. | Add schema-backed preview status, depth-truncation warnings, and live-source-file existence checks. |
| Skills and Workflow Density | B | High | Runtime budget passes with 10 default-visible skills; load-preview modeled 122 skills; handles expose target/latent routing. | High skill count and generated handle drift still create routing/maintenance pressure. | Keep visible surface small; require generated-handle parity and package metadata only for promoted/sharable skills. |
| Recovery and Failure Handling | C+ | Medium | Runtime failure payloads include failed_check_id and recovery guidance; repo doctor gives blocking repair command. | Recovery remains command recommendation, not deterministic repair handler with bounded retry and post-proof. | Add repair subcommands or documented repair modes for generated handles and Codex runtime links. |
| Governance and Safety | B | Medium | Security workflows, package verification, provenance, rollback, path-boundary docs, and PR gates exist. | Human approval/permission tiers and no-secret-in-prompt enforcement are mainly policy/workflow surfaces, not an ask-enforced gate. | Add secret/redaction and permission-profile assertions to runtime evidence packets and governance checks. |

## 3. Evidence-to-Code Mapping

| Evidence Pattern | Source File | Code Location | Runtime Status | Grade | Confidence |
|---|---|---|---|---:|---:|
| Runtime evidence packet as trust primitive | Codex operational review lines 95-129, 182-214 | repo doctor emits partial packet in Infrastructure/scripts/lib/ask/commands/repo_impl.py; conformance emits JSONL in skills_sdk/conformance.py | partial | B- | High |
| Doctor as decision packet | Jamie evidence lines 36-61, 180-201 | ./bin/ask repo doctor; command output includes selected_next_command and blockers | implemented_enforced | B+ | High |
| Generated command handles as runtime ABI | Jamie evidence lines 109, 406; prior JSC-351 memory | Infrastructure/bin/ask lines 134-140; command_surface checks; repo doctor signal | implemented_enforced, currently failing | B | High |
| Codex runtime proof must be target-specific | Jamie evidence lines 999-1027; Codex operational review lines 120-124 | runtime_adapters.py lines 119-183; skills proof --runtime-target codex | implemented_not_enforced | C+ | High |
| Codex preview/source modeling | Codex operational review lines 320-358 | codex_preview.py lines 203-252 and 496-518 | partial | C | High |
| Claim-vs-evidence verifier | Codex operational review lines 120-123, 220-222 | repo doctor/closeout and conformance have fragments; no shared claim verifier for final answers/PR ready | partial | C | Medium |
| Replayable conformance evidence | Jamie evidence lines 605, 1027 | conformance.py lines 359-407; live command writes JSONL and snapshots | implemented_enforced | B | High |
| Schema-backed public ABI | Jamie evidence lines 1013-1025 | skill-doctor/package schemas exist; preview schema missing | partial | B- | High |
| Package/install safety with rollback | Codex operational review lines 113, 246-248 | tests in test_ask_skills_conformance.py lines 62-287; package verify command | implemented_enforced | A- | High |
| Public wrapper is the entrypoint | AGENTS common commands; api reviewer | bin/ask lines 9-12; wrapper fixtures use Infrastructure/bin/ask lines 136-140 | implemented_not_enforced | C | High |
| Artifact-first reviewer contract | Codex operational review lines 336-342 | review swarm requested for this audit; repo has reviewer guidance, but not a general artifact gate in ask closeout | partial | C+ | Medium |
| Repo surface ownership | Root guidance and repo doctor output | repo doctor reports 20993 paths and 17037 warning findings | implemented_not_enforced | C | High |
| Context hot/cold separation | Jamie evidence and UBIQUITOUS_LANGUAGE | render/load previews and memory provider exist | partial | B- | Medium |

## 4. Gap Register

### GAP-001: Live Generated Command-Handle Drift Blocks Repo Doctor

**Category:** validation / runtime

**Current State:**
repo doctor exits 2 and reports "Blocked: Generated command-handle check found 3 violation(s)." The direct handles check shows COMMAND_HANDLE_MISSING for code-fixes-triage SKILL.md and agents/openai.yaml, plus COMMAND_HANDLE_DRIFT for llm-wiki agents/openai.yaml. Command-surface projection itself passes.

**Expected State:**
Generated command handles should match rooted manifest metadata at all times, or the repo should present a deterministic repair command that writes only the generated handles and re-runs the proof.

**Evidence Basis:**
Jamie evidence treats generated surfaces as outputs repaired through generators, not by hand. The prior JSC-351 direction made command handles the runtime ABI for mentionability and progressive disclosure.

**Code Evidence:**
- Infrastructure/bin/ask lines 134-140 exposes --write-command-handles and --check-command-handles.
- repo doctor live output selected next_command: ./bin/ask skills handles --check --no-handles --check-command-handles --json --robot.
- Live handles output reports command_handle_check.status fail, checked_count 208, violation_count 3.

**Risk:**
Agents can route to stale or missing thin handles; generated runtime projections stop matching canonical skill metadata; repo doctor cannot be used as a green closeout signal.

**Severity:** Critical

**Fix Grade:** P0

**Recommended Fix:**
Run the generated handle write path for the affected handles, inspect the diff, and add a focused regression test that simulates missing handle plus metadata drift. Keep the source of truth in rooted manifests and generated handle writers.

**Suggested Software / Method:**
Repo-native ./bin/ask handles writer, fixture-driven unit test, generated-file diff review.

**Files Likely To Change:**
- .agents/skills/code-fixes-triage/SKILL.md
- .agents/skills/code-fixes-triage/agents/openai.yaml
- .agents/skills/llm-wiki/agents/openai.yaml
- Infrastructure/tests/test_command_surface_handles.py

**Validation Command:**
./bin/ask skills handles --check --check-command-handles --no-handles --json --robot

**Acceptance Criteria:**
- command_handle_check.status is pass.
- repo doctor exits 0 or no longer has command_handles blocker.
- New regression covers missing generated handle and drifted generated openai.yaml.

### GAP-002: Codex-Parity Conformance Can Pass with Partial Preview Limitations

**Category:** validation / runtime

**Current State:**
The conformance suite passes 12 fixture cases and writes replayable evidence, but disabled_config and context_truncation pass even when their evidence contains status: partial and blocked_checks for live ConfigLayerStack or plugin runtime roots.

**Expected State:**
A conformance case claiming Codex parity should fail, block, or explicitly downgrade status when required live dimensions are unavailable. "Modeled preview behaved as designed" is useful, but it is not equivalent to "Codex parity proven."

**Evidence Basis:**
Codex operational review calls out false success from stale or partial truth as the largest operational risk. Jamie evidence separates smoke verification from compatibility and runtime truth.

**Code Evidence:**
- Infrastructure/scripts/lib/ask/skills_sdk/conformance.py lines 128-140 passes disabled_config when selector_policy exists while recording preview limitations as metadata.
- conformance.py lines 187-205 passes context_truncation when any included/omitted count exists while recording blocked_checks as metadata.
- conformance.py lines 390-397 sets suite status blocked only when case.status is not pass.
- Live conformance output reports suite status pass while disabled_config and context_truncation evidence contain status: partial.

**Risk:**
Operators can treat codex-parity conformance as stronger evidence than it is and ship runtime assumptions that were never tested against live Codex state.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:**
Split each modeled-preview case into two statuses: model_contract_status and live_parity_status. Keep model_contract_status passing when the modeled command reports limitations correctly, but make live_parity_status blocked when preview.status is partial or blocked_checks is non-empty for required parity cases. Suite status should expose both.

**Suggested Software / Method:**
JSON Schema enum fields, fixture snapshots, negative tests for preview.status partial, evidence-dir JSONL.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/skills_sdk/conformance.py
- Infrastructure/tests/test_ask_skills_conformance.py
- Infrastructure/config/schemas/skills-conformance-evidence.v1.schema.json if added

**Validation Command:**
./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance-audit --json --robot

**Acceptance Criteria:**
- Suite output distinguishes model pass from live parity blocked.
- Cases with preview.status partial cannot produce an unqualified codex-parity pass.
- JSONL snapshots include both statuses and blocked_check IDs.

### GAP-003: Codex Preview ABI Declares a Schema Version Without a Schema

**Category:** validation / context

**Current State:**
codex_preview.py declares codex-skill-runtime-preview.v1 and emits preview payloads, but Infrastructure/config/schemas does not include codex-skill-runtime-preview.v1.schema.json.

**Expected State:**
Every public JSON ABI with schema_version should have a schema file and tests validating representative outputs.

**Evidence Basis:**
Evidence documents emphasize schema-backed runtime cards, proof packets, compatibility snapshots, and deterministic validators over prose claims.

**Code Evidence:**
- codex_preview.py declares CODEX_PREVIEW_SCHEMA_VERSION.
- build_codex_load_preview returns roots, root_summary, skills, skill_count, errors, disabled_paths, validation_commands, agent_summary.
- Infrastructure/config/schemas currently contains skill-package-readiness, selection-gate-severity, skill-doctor, and skill-package schemas, but no preview schema.

**Risk:**
Preview output can drift without a mechanical ABI break, weakening downstream conformance and future Codex integration.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**
Add codex-skill-runtime-preview.v1.schema.json covering shared fields and command-specific payload sections. Add tests for load-preview, render-preview, config explain, inject-preview, and implicit-preview against the schema.

**Suggested Software / Method:**
JSON Schema Draft 7, in-test lightweight schema validator or jsonschema if allowed, snapshot fixtures.

**Files Likely To Change:**
- Infrastructure/config/schemas/codex-skill-runtime-preview.v1.schema.json
- Infrastructure/tests/test_ask_skills_codex_preview.py
- Infrastructure/scripts/lib/ask/services/codex_preview.py

**Validation Command:**
python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q

**Acceptance Criteria:**
- All preview commands emit schema-valid payloads.
- blocked_checks are typed and mandatory when status is partial.
- Source identity fields are typed and validated.

### GAP-004: Public ./bin/ask Wrapper Is Not Contract-Tested for High-Value JSON Surfaces

**Category:** API contract / validation

**Current State:**
The public wrapper bin/ask delegates with os.execv to Infrastructure/bin/ask. Wrapper contract fixtures and CLI tests execute Infrastructure/bin/ask directly for most checks.

**Expected State:**
The documented public entrypoint ./bin/ask should be tested for envelope parity and argument passthrough on high-value JSON ABI surfaces.

**Evidence Basis:**
Repository-as-control-plane evidence makes the command surface the operational interface. If agents and humans call ./bin/ask, the public wrapper is part of the contract.

**Code Evidence:**
- bin/ask lines 9-12 resolves repo_root and execs Infrastructure/bin/ask.
- verify_wrapper_contract_fixtures.py lines 136-140 checks Infrastructure/bin/ask repo status, skills list, plugins doctor.
- test_ask_cli_impl.py line 53 invokes Infrastructure/bin/ask --json.
- validate_all_impl.sh line 685 schedules runtime-separation-wrapper-fixtures, which currently checks the internal binary.

**Risk:**
Wrapper-specific failures in argv passthrough, env/path behavior, executable bit, or output envelope can reach users while CI stays green.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**
Expand wrapper fixtures to execute ./bin/ask and compare required envelope fields against Infrastructure/bin/ask for repo status, skills doctor, skills package, skills proof --runtime-target codex, and conformance help/argument errors.

**Suggested Software / Method:**
Python subprocess fixtures, JSON envelope parity assertions, timeout-bounded command matrix.

**Files Likely To Change:**
- Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py
- Infrastructure/tests/test_ask_cli_impl.py

**Validation Command:**
python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation --repo-root .

**Acceptance Criteria:**
- Fixture invokes ./bin/ask directly for at least five public command shapes.
- Required top-level fields status, trace_id, metadata, data, telemetry, errors are asserted.
- Internal binary tests remain, but no longer stand in for public wrapper proof.

### GAP-005: Codex Runtime Target Is Optional and Currently Failing for testing

**Category:** runtime / recovery

**Current State:**
skills proof testing --runtime-target codex fails because ~/.codex/skills exists but points to /Users/jamiecraik/dev/configs/.codex/skills, not this workspace runtime, and the testing handle does not exist there. Agents runtime is ready, so runtime_target=any would be satisfied by agents_user_runtime.

**Expected State:**
For Codex-facing work, Codex runtime readiness should be a first-class gate with a clear recovery path and post-repair validation.

**Evidence Basis:**
The evidence documents distinguish runtime truth from surface reachability and emphasize current-state packets, stale-state detection, and safe-to-run checks.

**Code Evidence:**
- runtime_adapters.py lines 119-133 computes codex_runtime_ready, agents_runtime_ready, and user_runtime_ready.
- runtime_adapters.py lines 129-183 makes runtime_target any accept user_runtime_ready, meaning either runtime.
- Live proof output for testing reports codex_user_runtime_ready false, agents_user_runtime_ready true, user_runtime_ready true, status fail because runtime_target codex was requested.

**Risk:**
Default or broad proof modes can mask Codex-specific runtime gaps; operators may assume Codex invocation is ready when only Agents runtime is ready.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**
Add a changed-skill Codex-runtime proof gate for command-visible skills and a deterministic repair classifier for when ~/.codex/skills is intentionally external vs accidentally stale.

**Suggested Software / Method:**
Runtime target policy file, proof gate in repo closeout strict mode, symlink classifier, no-mutation by default.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py
- Infrastructure/scripts/lib/ask/commands/repo_impl.py
- Infrastructure/tests/test_command_surface_handles.py
- Infrastructure/tests/test_ask_repo_closeout.py

**Validation Command:**
./bin/ask skills proof testing --runtime-target codex --json --robot

**Acceptance Criteria:**
- Codex-targeted workflows do not accept Agents runtime as substitute.
- Failure payload states whether the Codex symlink is intentionally external or should be repaired.
- Closeout strict mode can require Codex proof for changed command-visible skills.

### GAP-006: Codex Preview Source Identity Can Miss Stale Source Files

**Category:** context / validation

**Current State:**
codex_preview._codex_runtime_source_identity checks that the sibling /Users/jamiecraik/dev/codex repo exists and git rev-parse succeeds. It does not verify every file listed in CODEX_PREVIEW_SOURCE_FILES exists. If git status fails for those paths, dirty_lines becomes empty and status can still become identified.

**Expected State:**
Source identity should fail or warn when any modeled Codex source file is missing, renamed, or unreadable.

**Evidence Basis:**
Codex operational review says runtime proof needs source freshness snapshots and stale-state detection with current_ref, observed_at, and stale_reason.

**Code Evidence:**
- codex_preview.py lines 203-236 checks repo existence and git revision.
- codex_preview.py lines 238-249 treats git status failure as empty dirty_lines and sets identity.status to identified.

**Risk:**
The preview layer can imply it is grounded in current Codex source when upstream paths have drifted.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:**
Validate CODEX_PREVIEW_SOURCE_FILES before setting status identified. Emit missing_source_files and blocked_missing_source_files when any path is absent. Add a unit test that monkeypatches the file list with a nonexistent path.

**Suggested Software / Method:**
Path existence validation, source identity schema, fixture with missing source file.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/services/codex_preview.py
- Infrastructure/tests/test_ask_skills_codex_preview.py

**Validation Command:**
./bin/ask skills load-preview --json --robot

**Acceptance Criteria:**
- Missing modeled Codex source file prevents unqualified identified status.
- Preview payload lists missing source files and their expected repo-relative paths.

### GAP-007: Repo Surface Ownership Debt Is Too Large to Remain Only Background Noise

**Category:** governance / architecture

**Current State:**
repo doctor reports 20993 tracked paths and 17037 ownership diagnostic findings: 16731 tracked_historical_artifact, 267 tracked_generated_work_area, and 39 unknown_surface.

**Expected State:**
Repo surface diagnostics should distinguish accepted historical archive from new unknown/generated drift, and strict gates should block newly introduced unclassified surfaces.

**Evidence Basis:**
Evidence-led workflow requires source-of-truth boundaries, stale-state detection, and validators that prevent drift rather than making humans read enormous inventories.

**Code Evidence:**
- Live repo doctor repo_surface signal includes diagnostic_class repo_surface_ownership_debt and next_action classify_allowlist_or_cleanup_tracked_surface.
- repo surface is a warning in repo doctor, not the current blocker.

**Risk:**
Large known debt creates alert fatigue and can hide new generated artifacts or unknown source surfaces.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:**
Create a baseline snapshot for accepted historical artifacts and enforce delta-only strictness on new tracked_generated_work_area and unknown_surface findings. Keep full inventory available, but make the daily signal about new debt.

**Suggested Software / Method:**
JSON baseline, repo surface delta validator, jq summary, CI required check for new unknown/generated paths.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/commands/repo_impl.py
- Infrastructure/tests/test_ask_repo_surface.py
- GOVERNANCE or .harness surface baseline file

**Validation Command:**
./bin/ask repo surface --strict --json --robot

**Acceptance Criteria:**
- Existing accepted historical artifact baseline does not block.
- New unknown_surface or tracked_generated_work_area paths block strict validation.
- repo doctor reports top deltas, not only absolute total debt.

### GAP-008: Silent Depth Truncation in Modeled Skill Discovery

**Category:** context / skills

**Current State:**
_scan_preview_skills stops traversal at depth > 8 without recording a warning or blocked check.

**Expected State:**
Discovery truncation should be observable so preview consumers know whether skill_count is complete.

**Evidence Basis:**
Evidence requires stale/partial state to be explicit and not hidden behind normal-looking outputs.

**Code Evidence:**
- codex_preview.py lines 446-458 uses a queue and continues when depth > 8.
- build_codex_load_preview lines 496-518 reports skill_count and errors but no truncation count.

**Risk:**
Deep projected or plugin skill paths can be omitted while preview output appears normal.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:**
Track truncated paths and emit discovery_truncation warnings or blocked_checks. Add a fixture with SKILL.md at depth 9.

**Suggested Software / Method:**
Preview schema extension, fixture directory tree, unit test.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/services/codex_preview.py
- Infrastructure/tests/test_ask_skills_codex_preview.py

**Validation Command:**
./bin/ask skills load-preview --json --robot

**Acceptance Criteria:**
- Depth-truncated directories appear in preview output.
- Truncation changes status to partial or adds a warning.

### GAP-009: Review-State Packet Is Missing from Closeout Contract

**Category:** traceability / governance

**Current State:**
repo closeout centers on local readiness, changed files, sync, validation, and surface diagnostics. It does not surface unresolved PR threads, CodeRabbit/GitHub comments, reviewer artifact presence, review coverage gaps, or stale PR head state as a first-class packet.

**Expected State:**
Closeout should have a review-state packet when the repo or branch has PR context, including PR URL, head SHA, unresolved threads, reviewer artifacts expected/written, validation ownership, and coverage gaps.

**Evidence Basis:**
Codex operational review lines 228-232 explicitly defines a review-state model joining comments, artifacts, checks, diffs, and resolution evidence.

**Code Evidence:**
- agent-native reviewer found closeout contract lacks this remote review-state surface.
- Existing PR template and workflows enforce review artifacts at PR body level, not ask closeout runtime truth.

**Risk:**
Local closeout can look ready while remote review state is stale, unresolved, or missing required independent review evidence.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:**
Add optional review_state to repo closeout when PR metadata is discoverable, with explicit unknown/unavailable states when network or auth is absent. Do not block offline local closeout unless strict/live mode is requested.

**Suggested Software / Method:**
gh CLI/API adapter, JSON snapshot, freshness TTL, unavailable classification.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/commands/repo_impl.py
- Infrastructure/tests/test_ask_repo_closeout.py
- Infrastructure/config/schemas/review-state-packet.v1.schema.json

**Validation Command:**
./bin/ask repo closeout --changed --strict --json --robot

**Acceptance Criteria:**
- closeout payload includes review_state with observed_at, source, status, and freshness.
- Missing auth/network is classified, not silently ignored.

### GAP-010: ask Command Implementation Remains Over-Concentrated

**Category:** architecture

**Current State:**
skills_impl.py is 6238 lines, repo_impl.py is 1634 lines, codex_preview.py is 856 lines, and conformance.py is 408 lines. Some service extraction exists, but public command logic, payload assembly, validation, and routing still concentrate in large modules.

**Expected State:**
Command modules should mostly parse/dispatch and call smaller service modules with enforceable boundaries: contracts, runtime adapters, preview, packaging, conformance, recovery, and evidence emission.

**Evidence Basis:**
Architecture skill lenses favor deep module boundaries, low-complexity interfaces, and contracts that make drift mechanically detectable.

**Code Evidence:**
- wc output confirms 9136 total lines across four key ask modules.
- Infrastructure/bin/ask dispatch is broad but mostly direct.

**Risk:**
High-change command modules make false coupling easier, reduce test locality, and make it harder to enforce prompt/harness separation.

**Severity:** Medium

**Fix Grade:** P3

**Recommended Fix:**
Do not rewrite. Extract only the next touched seam: codex preview schema validation and conformance status policy are the best first service boundary. Add import-boundary tests after extraction.

**Suggested Software / Method:**
import-linter style custom pytest, dependency-cruiser equivalent for Python via grimp if available, or simple AST import checks.

**Files Likely To Change:**
- Infrastructure/scripts/lib/ask/services/codex_preview.py
- Infrastructure/scripts/lib/ask/skills_sdk/conformance.py
- Infrastructure/tests/test_ask_architecture_boundaries.py

**Validation Command:**
python3 -m pytest Infrastructure/tests/test_ask_architecture_boundaries.py -q

**Acceptance Criteria:**
- ask.commands imports services; services do not import command modules.
- Schema validation and status policy live outside CLI dispatch.

### GAP-011: Package Readiness Exists, but Many Local Skills Remain Legacy Capabilities

**Category:** skills / governance

**Current State:**
skills package testing exits success with status warning. testing lacks version, compatible_roles, runtime_needs, maturity, provenance, and share_readiness. skill-builder is ready, but not all command-visible skills meet package promotion metadata.

**Expected State:**
Only intentionally shareable/promoted skills need full metadata, but the package command should make this distinction explicit so "warning" does not become normalized noise.

**Evidence Basis:**
Evidence favors few, high-density, validated workflows and clear promotion gates rather than every skill pretending to be distribution-ready.

**Code Evidence:**
- Live package testing output: readiness_level legacy_capability; install_ready false; promotion_status blocked_validation; missing_field_count 6.
- repo doctor package_readiness uses skill-builder as the canonical ready target.

**Risk:**
Warnings become expected and ignored; operators may not know whether a skill is intentionally local-only or accidentally incomplete.

**Severity:** Low

**Fix Grade:** P3

**Recommended Fix:**
Add explicit package_intent values: local_only, internal_runtime, share_candidate, share_ready. Only share_candidate/share_ready require full promotion metadata.

**Suggested Software / Method:**
Schema enum, package metadata docs, package command warning classification.

**Files Likely To Change:**
- Infrastructure/config/schemas/skill-package.v1.schema.json
- Skills/*/*/SKILL.md only when intentionally promoted
- Infrastructure/scripts/lib/ask/commands/skills_impl.py

**Validation Command:**
./bin/ask skills package testing --json --robot

**Acceptance Criteria:**
- local_only skills do not produce ambiguous promotion warnings.
- share candidates still block when metadata is incomplete.

## 5. Contradictions

### CONTRADICTION-001: Workspace runtime appears synced, but generated command handles are drifted

**Claim:** repo doctor projection_sync says "Workspace skill runtime appears synced."

**Actual Implementation:** The same repo doctor run blocks on command_handles because generated command-handle check found 3 violations.

**Evidence:** Live repo doctor: projection_sync state pass; command_handles state block; handles check lists code-fixes-triage missing files and llm-wiki drift.

**Severity:** High

**Operational Impact:** A coarse sync signal can mislead readers unless they inspect downstream command-handle ABI checks.

**Recommended Fix:** Rename or narrow projection_sync to workspace_projection_sync and explicitly state that generated command handles are checked separately.

### CONTRADICTION-002: codex-parity conformance passes while evidence says live Codex dimensions are blocked

**Claim:** skills conformance run reports "Conformance suite codex-parity passed with 12 fixture cases."

**Actual Implementation:** disabled_config and context_truncation evidence include status partial and blocked_checks for live skills config layers, live ConfigLayerStack, and runtime plugin skill roots.

**Evidence:** Live conformance output and conformance.py lines 128-205.

**Severity:** High

**Operational Impact:** The suite name overstates the proven runtime truth.

**Recommended Fix:** Split model conformance from live parity or make blocked preview limitations produce blocked live_parity_status.

### CONTRADICTION-003: Public command examples use ./bin/ask, but wrapper fixture tests use Infrastructure/bin/ask

**Claim:** Root guidance and examples make ./bin/ask the repo command interface.

**Actual Implementation:** verify_wrapper_contract_fixtures.py hardcodes Infrastructure/bin/ask for repo status, skills list, and plugins doctor.

**Evidence:** bin/ask lines 9-12; verify_wrapper_contract_fixtures.py lines 136-140; test_ask_cli_impl.py line 53.

**Severity:** High

**Operational Impact:** CI can miss public wrapper regressions.

**Recommended Fix:** Add public wrapper fixtures and compare against internal command where useful.

### CONTRADICTION-004: Preview source identity can say identified without source file existence proof

**Claim:** preview payloads identify the local Codex source revision used by the model.

**Actual Implementation:** source identity only proves the repo has a git HEAD and does not verify every modeled source file exists before setting identified.

**Evidence:** codex_preview.py lines 203-252.

**Severity:** Medium

**Operational Impact:** Source-grounded preview claims can survive upstream Codex path moves.

**Recommended Fix:** Validate all CODEX_PREVIEW_SOURCE_FILES exist and emit missing_source_files.

### CONTRADICTION-005: Repo surface debt is called diagnostic, but counts are operationally large

**Claim:** repo surface is diagnostic warning debt.

**Actual Implementation:** repo doctor reports 17037 blocking_findings by code in the repo_surface signal, though not as the selected blocker.

**Evidence:** Live repo doctor repo_surface details.

**Severity:** Medium

**Operational Impact:** Absolute counts are too high to guide daily work and may hide new risky files.

**Recommended Fix:** Baseline accepted historical debt and block deltas.

## 6. Missing Features

### Runtime State

- Shared runtime evidence packet joining ask trace_id, git state, user runtime links, validation receipts, artifacts, external state, and claims.
- Codex app-server/live runtime adapter for skill loader/config state.
- Strict Codex-runtime closeout proof for changed command-visible skills.

### Command Selection

- Public wrapper fixture matrix for ./bin/ask.
- Typed command recommendation schema shared by repo doctor, skills doctor, package, proof, and conformance.
- Explicit recovery mode for generated-handle drift.

### Verification

- Preview ABI schema validation.
- Negative conformance tests for partial preview limitations.
- Claim-vs-evidence verifier for final closeout statements and PR readiness.

### Validation

- Delta-based repo surface strictness.
- Import/layer boundary tests for ask commands vs services.
- Cross-repo source-file existence proof for Codex preview modeling.

### Architecture Enforcement

- ask architecture boundary test preventing services from importing CLI command modules.
- Explicit schemas for conformance evidence and runtime preview payloads.
- More extraction from skills_impl.py only around touched, high-risk boundaries.

### Traces

- Optional --evidence-dir for repo doctor, skills proof, skills package, and closeout.
- Artifact receipt schema with path/hash/producer/validation result.
- Runtime evidence packet compatible with session collector/OTEL indexing.

### Context

- Discovery truncation warnings.
- Preview freshness TTL and source revision fields in a schema.
- Hot/cold context source promotion policy connected to validation, not only docs.

### Skills

- package_intent distinction for local-only vs share-candidate skills.
- Package metadata promotion checklist only for skills intended for sharing.
- Skill density validator that tracks default-visible budget and command-handle drift together.

### Recovery

- Bounded retry ledger for generated-handle repair.
- Codex symlink/runtime-link classifier with safe no-mutation default.
- Recovery event schema with retryability, owner, and proof command.

### Governance

- No-secret-in-prompt and permission-profile assertions in runtime evidence packets.
- Review-state packet in closeout.
- Human override points and revocation paths surfaced as machine-readable policy, not only prose.

### CI/CD

- Required check for public wrapper fixtures.
- Required check for preview schema validation.
- Delta-only repo surface strict check.
- Conformance check that cannot report unqualified codex-parity pass with partial live preview limitations.

### Observability

- Trace/event IDs preserved in package/proof/conformance evidence.
- Collector health and observability confidence fields in runtime evidence packet.
- Session evidence lookup linked from closeout artifacts.

## 7. Fix Roadmap

### Phase 1 - Critical Trust Boundary Fixes

**Objective:** Reduce false-success, stale-state, unsafe-command, and missing-evidence risk.

**Fixes included:**
- GAP-001 generated command-handle drift repair.
- GAP-002 split modeled conformance from live Codex parity.
- GAP-004 public ./bin/ask wrapper contract fixtures.
- GAP-005 strict Codex runtime proof policy for changed command-visible skills.

**Files likely affected:**
- .agents/skills/code-fixes-triage/SKILL.md
- .agents/skills/code-fixes-triage/agents/openai.yaml
- .agents/skills/llm-wiki/agents/openai.yaml
- Infrastructure/scripts/lib/ask/skills_sdk/conformance.py
- Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py
- Infrastructure/tests/test_ask_skills_conformance.py
- Infrastructure/tests/test_ask_cli_impl.py
- Infrastructure/tests/test_command_surface_handles.py

**Validation gates:**
- ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot
- ./bin/ask repo doctor --json --robot
- ./bin/ask skills conformance run --suite codex-parity --evidence-dir /tmp/ask-conformance-audit --json --robot
- python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation --repo-root .

**Expected risk reduction:** High. This phase directly removes current repo doctor red state and closes the easiest false-success path.

### Phase 2 - Mechanical Enforcement

**Objective:** Turn runtime-preview and conformance contracts into schemas/tests/CI.

**Fixes included:**
- GAP-003 preview ABI schema.
- GAP-006 source identity missing-file checks.
- GAP-008 discovery truncation warnings.
- Add conformance evidence schema if absent.

**Files likely affected:**
- Infrastructure/config/schemas/codex-skill-runtime-preview.v1.schema.json
- Infrastructure/config/schemas/skills-conformance-evidence.v1.schema.json
- Infrastructure/scripts/lib/ask/services/codex_preview.py
- Infrastructure/tests/test_ask_skills_codex_preview.py

**Validation gates:**
- python3 -m pytest Infrastructure/tests/test_ask_skills_codex_preview.py -q
- ./bin/ask skills load-preview --json --robot
- ./bin/ask skills render-preview --context-window 1024 --json --robot

**Expected risk reduction:** Medium-high. This makes preview drift mechanically visible.

### Phase 3 - Runtime Harness Maturity

**Objective:** Add first-class evidence packets and recovery event surfaces.

**Fixes included:**
- Runtime evidence packet schema.
- Optional --evidence-dir for doctor/proof/package/closeout.
- Recovery event payloads for generated handles, Codex symlink drift, and partial preview.
- Attempt ledger with retryability and owner.

**Files likely affected:**
- Infrastructure/scripts/lib/ask/commands/repo_impl.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py
- Infrastructure/config/schemas/runtime-evidence-packet.v1.schema.json
- Infrastructure/tests/test_runtime_evidence_packet.py

**Validation gates:**
- ./bin/ask repo doctor --evidence-dir /tmp/ask-doctor-evidence --json --robot
- ./bin/ask skills proof testing --runtime-target codex --evidence-dir /tmp/ask-proof-evidence --json --robot

**Expected risk reduction:** Medium. This makes claims replayable and connects local artifacts to runtime truth.

### Phase 4 - Context and Skill Compression

**Objective:** Keep skill surface dense, non-overlapping, and context-efficient without hiding important routing failures.

**Fixes included:**
- package_intent for local-only vs share-candidate skills.
- Skill density validator combining default-visible count, command-handle parity, and preview completeness.
- Hot/cold context promotion policy backed by preview schema.

**Files likely affected:**
- Infrastructure/config/schemas/skill-package.v1.schema.json
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Skills/*/*/SKILL.md only for intentionally promoted packages
- Infrastructure/tests/test_skill_package_intent.py

**Validation gates:**
- ./bin/ask skills budget --json --robot
- ./bin/ask skills package testing --json --robot
- ./bin/ask skills load-preview --json --robot

**Expected risk reduction:** Medium. This prevents skill proliferation and warning normalization from eroding trust.

### Phase 5 - Governance and Scaling

**Objective:** Join local proof, remote review truth, and policy boundaries into closeout-ready evidence.

**Fixes included:**
- Review-state packet in repo closeout.
- Permission-profile and no-secret assertions in runtime evidence.
- Delta-only repo surface enforcement.
- Audit trail links from closeout to conformance/doctor evidence dirs.

**Files likely affected:**
- Infrastructure/scripts/lib/ask/commands/repo_impl.py
- Infrastructure/config/schemas/review-state-packet.v1.schema.json
- Infrastructure/tests/test_ask_repo_closeout.py
- .github/workflows/pr-pipeline.yml or validation scripts if promoted to CI

**Validation gates:**
- ./bin/ask repo closeout --changed --strict --json --robot
- ./bin/ask repo surface --strict --json --robot
- python3 -m pytest Infrastructure/tests/test_ask_repo_closeout.py -q

**Expected risk reduction:** Medium-high for delivery governance and remote-state false readiness.

## 8. Highest-Leverage Fixes

| Rank | Fix | Impact | Difficulty | Risk Reduced | Why First |
|---:|---|---:|---:|---|---|
| 1 | Repair generated command-handle drift | Very High | Low | Current repo doctor blocker | It is red now and blocks trust in the control plane. |
| 2 | Split conformance model pass from live parity pass | Very High | Medium | False-success codex-parity claims | It prevents a green suite from overstating live runtime proof. |
| 3 | Add public ./bin/ask wrapper fixture matrix | High | Low | Public API drift | Users and agents call ./bin/ask, so tests should too. |
| 4 | Add preview ABI schema | High | Medium | Contract drift | Preview commands are now public enough to need a schema. |
| 5 | Validate Codex preview source files exist | High | Low | Stale Codex source modeling | Cheap check with high epistemic value. |
| 6 | Add strict Codex proof gate for changed skills | High | Medium | Agents runtime masking Codex gaps | Keeps Codex-facing readiness honest. |
| 7 | Emit discovery truncation warnings | Medium | Low | Silent missing skills | Small patch, direct evidence improvement. |
| 8 | Add delta-only repo surface strictness | Medium | Medium | Ownership debt alert fatigue | Turns a huge backlog into actionable new-drift prevention. |
| 9 | Add review-state packet to closeout | Medium | Medium-high | Local/remote readiness split | Needed before broader PR autonomy. |
| 10 | Add ask architecture boundary tests | Medium | Medium | Over-concentrated command modules | Prevents future complexity creep without a rewrite. |

## 9. Implementation Advice

**What to build first**

Start with the current red path: generated command-handle drift. It is concrete, already detected by repo doctor, and has a narrow repair command. Then patch conformance status semantics so the suite cannot say unqualified codex-parity pass when its own evidence says partial.

**What not to build yet**

Do not start with a broad runtime evidence packet platform. The concept is correct, but the first patch should remove current false-success and drift risks. A big packet schema before fixing live blockers would create a nicer envelope around untrusted truth.

**What to remove**

Do not remove the existing modeled preview limitations. They are useful and honest. Instead, stop letting them coexist with unqualified parity pass.

**What to simplify**

Package readiness should stop warning local-only skills as though every skill is a share candidate. Add package_intent so the command can distinguish "not meant for promotion" from "promotion incomplete."

**What should become a validator**

- Public wrapper parity for ./bin/ask.
- Preview ABI schema validation.
- Codex source file existence for preview modeling.
- Delta-only repo surface strictness.
- Conformance no-unqualified-pass-when-partial rule.

**What should become a schema**

- codex-skill-runtime-preview.v1
- skills-conformance-evidence.v1 if it remains public/replayable
- runtime-evidence-packet.v1 later
- review-state-packet.v1 later

**What should become a skill**

Do not create a new skill for the first patch. The needed behavior belongs in validators and ask commands. A later skill could package the "Codex parity repair loop" once the underlying commands are deterministic.

**What should become documentation**

Document the distinction between model_contract_status and live_parity_status once implemented. Documentation should explain the statuses after code enforces them, not before.

**What should become CI**

Promote wrapper parity and preview schema tests into the existing validation path. Add repo surface delta strictness only after a baseline exists, otherwise it will create noisy CI failures.

**What should remain manual**

Changing ~/.codex/skills symlink targets should remain manual or explicitly approved. The repo can classify the mismatch and recommend a command, but it should not silently repoint user-level runtime state.

## 10. Final Recommendation

Immediate next action:

Repair the current generated command-handle drift, then re-run ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot and ./bin/ask repo doctor --json --robot.

Safest first patch:

Use the existing generated command-handle writer for only the missing/drifted handles, inspect the generated diff, and add one focused regression to test_command_surface_handles.py.

Highest-risk missing system:

The highest-risk missing system is not another doc or orchestration layer. It is the live-parity status boundary: conformance and preview need to mechanically distinguish "the model explains what it cannot prove" from "Codex runtime parity is proven."

Best validation command to add first:

python3 Infrastructure/scripts/validation-and-linting/verify_wrapper_contract_fixtures.py --runtime-separation --repo-root .

This should be expanded to execute ./bin/ask directly and probe schema-backed high-value surfaces.

Whether the project is ready for broader Codex autonomy:

Not yet for broad autonomy. It is ready for bounded autonomy inside repo-native commands because blockers, next commands, schemas, and package verification are real. It is not ready for wider Codex-runtime autonomy until generated command handles are green, codex-parity pass semantics are tightened, public wrapper ABI is tested, and Codex runtime proof is required where Codex invocation is the actual target.

