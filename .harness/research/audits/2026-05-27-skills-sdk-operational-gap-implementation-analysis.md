# Skills SDK Operational Gap And Implementation Analysis

Date: 2026-05-27

Target evidence: `.harness/research/deep/2026-05-27-skills-sdk-operational-analysis.md`

Target codebase: `/Users/jamiecraik/dev/agent-skills`

Methods used:

- `$improve-codebase-architecture`: code-tree-first architecture comparison, runtime boundary classification, evidence-backed gaps.
- `$simplify`: reduce the recommended implementation to a smaller public SDK spine rather than another broad control-plane layer.
- `$testing`: record exact commands, outcomes, and verification gates for each recommended patch.
- Three read-only review lanes:
  - `sdk_spine_audit`: command spine, public SDK namespace, contract envelope.
  - `package_contract_audit`: skill package schema, scaffold, validation, eval/Tessl boundaries.
  - `runtime_truth_audit`: runtime cards, proof evidence, events, replay, staleness, route decisions.

---

## 1. Executive Summary

Overall maturity: **B- as an internal agent-skills control plane; C+ as a portable public Skills SDK.**

The codebase already contains serious Skills SDK foundations: a centralized `./bin/ask` command wrapper, mature `ask skills doctor/package/proof/prove/handles/conformance` commands, strict archive package verification, generated command-handle validation, runtime proof cards, package readiness schemas, nested `agent_contract` fields, Tessl-aware eval staging, and local observability provider discovery under `~/.agents`.

The main gap is not raw capability. The gap is **SDK product shape and enforcement convergence**. The operational analysis asks for a smaller public SDK spine with explicit contracts, runtime truth reduction, durable evidence, package behavior classification, and replayable route decisions. The code currently implements much of that as separate skill-management commands, nested payloads, permissive schemas, and snapshot artifacts.

Top five gaps:

| Rank | Gap | Current Status | Risk |
|---:|---|---|---|
| 1 | No public `ask skills sdk ...` or `ask sdk ...` namespace | Missing | Agents must infer the SDK spine from a wide `skills` command set. |
| 2 | No first-class `plane_contract` / top-level `agent_contract` envelope | Partial | Claim boundaries are inconsistent across commands. |
| 3 | Runtime proof artifacts are overwritten snapshots, not an append-only evidence ledger | Partial | Runtime proof cannot be replayed across attempts. |
| 4 | Package contract lacks normalized `behavior_type` and `enforcement_level` | Missing | Skills cannot declare whether they are advisory, mandatory, guardrail, review, or runtime-enforced. |
| 5 | Repo status can say `skills_synced: true` while command-handle drift fails elsewhere | Contradicted | False-success risk for cleanup, closeout, and agent autonomy. |

Strongest existing foundations:

- `Infrastructure/bin/ask` is a stable centralized command spine.
- `skills doctor`, `skills package`, `skills proof`, `skills prove`, and `skills handles` already cover much of the SDK lifecycle.
- `skill-package.v1` and `skill-package-readiness.v1` schemas exist.
- `package_verify.py` strongly enforces archive safety boundaries.
- Runtime proof emits structured probe, receipt, artifact record, and runtime card files.
- `~/.agents/otel-collector`, `~/.agents/session-collector`, and `~/.agents/observability-stack` are detected as enrichment providers.

Highest-leverage next fixes:

1. Add a thin public `ask skills sdk` facade that delegates to existing mature commands.
2. Promote `agent_contract` and introduce `plane_contract` as consistent SDK command envelope fields.
3. Add `command_surface_state` to `repo status` / SDK doctor so handle drift cannot hide behind `skills_synced: true`.
4. Add `behavior_type` and `enforcement_level` to the package contract, template, validators, and tests.
5. Add append-only runtime/event JSONL evidence and a semantic runtime-truth reducer.

Agent-safe boundary classification: **partially safe, not yet broadly autonomous.** Package operations are increasingly safe because they expose source/generated path boundaries, proof limits, and nested agent contracts. Broad Skills SDK autonomy remains risky until the SDK facade, command-surface state reducer, durable event ledger, and package behavior/enforcement fields are implemented.

---

## 2. Overall Gradecard

| Area | Grade | Confidence | Current Status | Main Gap | Recommended Fix |
|---|---|---:|---|---|---|
| Public SDK spine | C | High | SDK internals exist under `ask skills ...`. No `ask skills sdk` action. | Public product shape is hidden inside broad skill-management commands. | Add thin `ask skills sdk doctor/eval/project/sync/status` facade over existing commands. |
| Agent contract envelope | C | High | `agent_contract` exists nested inside package SDK contract. | Not first-class across doctor/proof/prove/package. No `plane_contract`. | Shared envelope builder used by SDK facade and existing commands. |
| Package contract | B- | High | Schema, readiness, package verifier, metadata merge, strict mode exist. | Missing behavior/enforcement fields; creator validation is scaffold-level. | Add `behavior_type`, `enforcement_level`, and a creator strict gate. |
| Runtime proof plane | C+ | High | Runtime cards and receipts emitted. Blocked runtime is represented. | Snapshot artifacts overwrite prior runs; staleness is absence-tolerant. | Append-only ledger plus semantic reducer and v2 runtime card freshness fields. |
| Command surface drift | B- | High | `skills handles --check` catches drift. | `repo status` does not include command-surface state. | Make command-surface state part of SDK doctor/repo status. |
| Route decisions | C | Medium | Deterministic routing policy and decision payloads exist. | No persisted route-decision artifact or replay bundle. | Emit `route_decision.v1` with input hash, policy hash, manifest hash, candidates, selected. |
| Evals and Tessl | B | High | `ask evals run` stages controlled payloads and runs local Tessl unless skipped. | Claim boundaries are mostly docs/template plus wrapper behavior. | Emit `proves`, `does_not_prove`, `readiness_claim_allowed` in eval outputs. |
| Observability | C+ | Medium | Provider discovery exists and reports telemetry confidence. | No minimal required event model tied to SDK commands. | Add SDK event pack and provider freshness fields, enriched by `~/.agents`. |
| External adoption | C | Medium | Project-local lifecycle and config concepts exist. | No small `sdk init` / external repo doctor path. | Add project-local `ask skills sdk init/doctor` after core contract settles. |
| Simplicity | C+ | High | Existing pieces are reusable. | Command lanes and vocabulary remain too wide for new agents. | Make `sdk doctor` the reducer; avoid new parallel lanes. |

---

## 3. Evidence-To-Code Mapping

| Evidence Pattern | Source Evidence | Code Location | Runtime Status | Grade | Confidence |
|---|---|---|---|---|---:|
| Smaller public SDK spine | Operational analysis: public SDK spine should answer discover/validate/eval/evidence/projection/next command | `Infrastructure/bin/ask` exposes `skills`, not `sdk`; `./bin/ask skills sdk --help` fails | missing | C | High |
| SDK doctor as reducer | Operational analysis: doctor should reduce status/package/proof/events | `skills doctor` composes resolver, audit, package readiness, proof availability; `repo doctor` composes broader checks | partial | B- | High |
| Plane contract on command payloads | Operational analysis: explicit plane contract and claim limits | No `plane_contract` hits in `Infrastructure/config`, `Infrastructure/scripts`, `Docs` | missing | D | High |
| Agent-native command payloads | Operational analysis: commands should expose next safe command, proof limits, editable/generated paths | `package_contracts.py` emits nested `agent_contract` | implemented_not_enforced | C+ | High |
| Runtime-card v2 identity/freshness | Operational analysis: runtime card should carry Codex identity and freshness | `runtime-card.v1.schema.json` is permissive and lacks Codex identity/freshness fields | partial | C | High |
| Durable events | Operational analysis: runtime/eval/doctor events should be replayable | `skills events` returns event contract/readiness metadata; proof writes fixed files | documented_only/partial | C | High |
| Route decision replay | Operational analysis: routing should be inspectable and replayable | `route_skillset.py` emits in-memory decision with policy identity, candidates, operator action | partial | C | Medium |
| Package behavior/enforcement levels | Operational analysis: package readiness needs behavior and enforcement classification | No `behavior_type` or `enforcement_level` in schemas or validators | missing | D | High |
| Skill scaffold quality | Operational analysis: strengthen template/validation/evals | `init_skill.py`, `quick_validate.py`, `audit_skill_descriptions.py`, OpenAI lint, eval templates | partial | B- | High |
| Tessl/eval claim boundary | Operational analysis: eval artifacts explain but do not overclaim | `ask evals run` stages temp payloads and runs Tessl; docs say scores are evidence, not proof | implemented_not_universal | B | High |
| Telemetry as enrichment | Operational analysis: `~/.agents` observability should aid but not replace artifacts | `local_evidence_provider_status()` reports enrichment-only providers | implemented | B | Medium |
| False-success prevention | Operational analysis: runtime truth should prevent green claims over stale/drifted state | `repo status` reports `skills_synced: true` while `skills handles --check` can fail | contradicted | C | High |

---

## 4. Current Runtime Evidence From This Audit

Commands run:

| Command | Outcome | Evidence |
|---|---|---|
| `./bin/ask skills --help` | pass | Shows broad `skills` action set including `doctor`, `package`, `prove`, `proof`, `events`, `route`, `audit`, `init`; no compact SDK facade. |
| `./bin/ask skills sdk --help` | fail | `unknown action 'sdk'`; confirms public SDK namespace is missing. |
| `./bin/ask repo status --json --robot` | pass | Returned `skills_synced: true`, but no `command_surface` or `next_command`. |
| `./bin/ask skills package skill-factory-router --json --robot` | warning | Package contract compatible, but install/promotion blocked; missing `commands`, `permission_profile`, `portability_profile`. |
| `./bin/ask skills events --json --robot` | pass | Reports `skill-events.v1` contract ready with 8 event types; this is a contract catalogue, not a durable event log. |
| `./bin/ask skills route skill-factory "create a new skill package with evals" --json --robot` | diagnostic error | Returned `selection-decision.v1` with `unresolved_ambiguity`; useful decision payload but no persisted replay artifact. |
| `./bin/ask skills handles --check --check-command-handles --json --robot` | fail | Current worktree reports command-handle drift for authoring-family projections; proves handle drift exists outside `repo status`. |

The worktree is dirty with pre-existing edits. This report treats current command outputs as live evidence, not as proof that the dirty changes are ready.

---

## 5. Gap Register

### GAP-001: Missing Public SDK Namespace

**Category:** interface / agent-native UX

**Current State:** `Infrastructure/bin/ask` exposes `skills` as the public topic. Mature SDK-like commands exist as `ask skills doctor/package/proof/prove/handles/conformance/events`. `./bin/ask skills sdk --help` fails with unknown action.

**Expected State:** A small public Skills SDK spine that lets another repo or agent answer: initialize, doctor, validate/eval, project/sync, inspect evidence, and get next safe command.

**Evidence Basis:** Operational analysis recommends a smaller public SDK spine and warns that the current surface is too wide for external adoption.

**Code Evidence:** `Infrastructure/bin/ask`; `Infrastructure/scripts/lib/ask/command_metadata.py`; `Infrastructure/scripts/lib/ask/commands/skills_impl.py`.

**Risk:** Agents choose the wrong command or over-trust a partial lane because the true SDK reducer is not obvious.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:** Add a thin `ask skills sdk` namespace first, not a broad rewrite. Delegate:

- `ask skills sdk doctor [handle]` -> reducer over existing `skills doctor`, `skills package`, `skills proof/prove`, `skills handles --check`, `skills events`.
- `ask skills sdk status` -> repo-level SDK readiness.
- `ask skills sdk eval <handle>` -> eval lane with claim-boundary fields.
- `ask skills sdk project <handle>` -> projection/sync readiness.

**Suggested Software / Method:** Existing `argparse` dispatch in `Infrastructure/bin/ask`; existing robot JSON wrapper.

**Files Likely To Change:**

- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/command_metadata.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/tests/test_ask_skills_sdk_*.py`

**Validation Command:**

```bash
./bin/ask skills sdk --help
./bin/ask skills sdk doctor skill-factory-router --json --robot
```

**Acceptance Criteria:**

- `skills sdk --help` exists.
- SDK doctor returns one compact payload with `status`, `agent_contract`, `plane_contract`, `command_surface_state`, `package_state`, `runtime_state`, `event_state`, `next_safe_command`.
- Existing commands still work.

---

### GAP-002: No First-Class Plane Contract

**Category:** governance / claim boundary

**Current State:** `agent_contract` exists nested in package readiness. No `plane_contract` object or schema exists.

**Expected State:** Every SDK-facing command should explicitly state the planes it touched and what that command proves or does not prove.

**Evidence Basis:** Operational analysis recommends P0 `plane_contract` command payloads.

**Code Evidence:** `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py` emits nested `agent_contract`; no `plane_contract` found in `Infrastructure/config`, `Infrastructure/scripts`, or docs.

**Risk:** A command result can be interpreted as broader proof than it actually provides.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:** Create shared envelope helpers:

```json
{
  "agent_contract": {
    "source_of_truth": "...",
    "editable_paths": [],
    "generated_paths": [],
    "forbidden_actions": [],
    "next_safe_command": "...",
    "what_this_proves": [],
    "what_this_does_not_prove": [],
    "readiness_claim_allowed": false
  },
  "plane_contract": {
    "source_plane": "checked|not_checked|not_applicable",
    "runtime_plane": "checked|blocked|not_checked|not_applicable",
    "package_plane": "checked|blocked|not_checked|not_applicable",
    "evidence_plane": "checked|blocked|not_checked|not_applicable",
    "claim_boundary": "..."
  }
}
```

**Suggested Software / Method:** JSON Schema plus shared Python helper.

**Files Likely To Change:**

- `Infrastructure/config/schemas/agent-contract.v1.schema.json`
- `Infrastructure/config/schemas/plane-contract.v1.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`

**Validation Command:**

```bash
./bin/ask skills package skill-factory-router --json --robot | jq '.data.skill_package.agent_contract, .data.skill_package.plane_contract'
```

**Acceptance Criteria:**

- SDK facade payloads expose both contracts at predictable locations.
- `readiness_claim_allowed` is false unless all required planes pass.

---

### GAP-003: Repo Status Can Mask Command-Handle Drift

**Category:** runtime / false-success prevention

**Current State:** `repo status` reports `skills_synced: true` but does not include command-handle state. In this audit, `skills handles --check --check-command-handles` failed with command-handle drift.

**Expected State:** Repo or SDK status should not allow a green-looking state when generated command handles are stale or inconsistent.

**Evidence Basis:** Operational analysis emphasizes runtime truth and command surface state consistency.

**Code Evidence:** `Infrastructure/scripts/lib/ask/commands/repo_impl.py`; `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`.

**Risk:** Agents or humans can claim the repo is ready while generated runtime projections are stale.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:** Add `command_surface_state` to `repo status` and SDK doctor. Compute it using existing `validate_skill_handles()` / handles check logic, but keep `repo status` lightweight by returning summary counts and next command.

**Suggested Software / Method:** Existing command-surface validator; JSON schema update.

**Files Likely To Change:**

- `Infrastructure/scripts/lib/ask/commands/repo_impl.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`

**Validation Command:**

```bash
./bin/ask repo status --json --robot | jq '.data.command_surface_state'
./bin/ask skills handles --check --check-command-handles --json --robot
```

**Acceptance Criteria:**

- If handle drift exists, `repo status` reports `command_surface_state.status: fail|warning`.
- Payload includes `next_safe_command`.

---

### GAP-004: Runtime Proof Is Snapshot-Based, Not Replayable

**Category:** traceability / runtime truth

**Current State:** Runtime proof writes fixed files under `.harness/evidence/runtime-proof/<handle>/<runtime_target>/`: `probe.json`, `evidence-receipt.json`, `artifact-record.json`, and `runtime-card.json`. Repeated runs overwrite the prior attempt.

**Expected State:** Runtime proof should emit append-only attempt records so stale, failed, repaired, and passing proofs can be replayed.

**Evidence Basis:** Operational analysis recommends durable events and runtime truth reducer.

**Code Evidence:** `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`; `Infrastructure/scripts/lib/ask/commands/skills_impl.py`.

**Risk:** Post-incident analysis cannot reconstruct how a runtime proof changed over time.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:** Keep current latest files for ergonomics, but also append to:

```text
.harness/evidence/runtime-proof/events.jsonl
.harness/evidence/runtime-proof/<handle>/<runtime_target>/attempts/<attempt_id>/...
```

Each event should include `attempt_id`, `run_id`, `timestamp`, `handle`, `runtime_target`, `proof_status`, `runtime_status`, `claim_status`, `evidence_paths`, and `failure_class`.

**Suggested Software / Method:** JSONL event log, deterministic attempt ID from timestamp + handle + target.

**Files Likely To Change:**

- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- `Infrastructure/config/schemas/skill-runtime-event.v1.schema.json`
- `Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py`

**Validation Command:**

```bash
./bin/ask skills proof skill-factory-router --runtime-target codex --json --robot
jq -c 'select(.event_type=="skill.runtime.proof.completed")' .harness/evidence/runtime-proof/events.jsonl | tail -1
```

**Acceptance Criteria:**

- Current latest files remain.
- Append-only JSONL grows on each proof run.
- Validator checks event schema and evidence path existence.

---

### GAP-005: Runtime Card v1 Lacks Strong Identity And Freshness

**Category:** runtime / context

**Current State:** `runtime-card.v1.schema.json` permits broad additional properties in several nested objects and lacks required Codex identity/freshness fields.

**Expected State:** Runtime card should distinguish current live runtime proof from stale or absent runtime observation.

**Evidence Basis:** Operational analysis recommends runtime-card v2 with Codex identity and freshness.

**Code Evidence:** `Infrastructure/config/schemas/runtime-card.v1.schema.json`; `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`.

**Risk:** A card can look structurally valid while remaining weak as runtime truth.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:** Add `runtime-card.v2` fields:

- `observed_at`
- `stale_after`
- `freshness_status`
- `codex_thread_id`
- `codex_turn_id`
- `tool_call_ids`
- `collector_sources`
- `absence_policy`

Absence of current runtime observation should degrade confidence, not silently pass.

**Suggested Software / Method:** JSON Schema v2 with transitional reader for v1.

**Files Likely To Change:**

- `Infrastructure/config/schemas/runtime-card.v2.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- `Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py`

**Validation Command:**

```bash
python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py --json
```

**Acceptance Criteria:**

- Runtime cards contain freshness status.
- Missing observation is classified explicitly.

---

### GAP-006: Route Decisions Are Not Persisted Or Replay-Complete

**Category:** routing / traceability

**Current State:** `route_skillset.py` emits `selection-decision.v1` with status, policy identity, candidates, selected, and operator action. It does not persist route decisions with input hash, manifest row hashes, routing map identity, or replay context.

**Expected State:** Route decisions should be replayable artifacts so routing drift and semantic noise can be audited.

**Evidence Basis:** Operational analysis recommends `route_decision.v1` artifacts and semantic routing-noise report.

**Code Evidence:** `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py`; `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`.

**Risk:** Routing behavior can change without a durable explanation of what input, policy, and candidate set produced the decision.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:** Emit route decision artifacts to:

```text
.harness/evidence/routing/<date>/<decision_id>.json
```

Include `task_hash`, `task_excerpt`, `policy_identity`, `routing_map_hash`, `candidate_manifest_hashes`, `selected`, `rejected_candidates`, `ambiguity_reason`, `next_safe_command`.

**Suggested Software / Method:** JSON Schema, deterministic hashing, optional `--evidence-path`.

**Files Likely To Change:**

- `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py`
- `Infrastructure/config/schemas/route-decision.v1.schema.json`
- `Infrastructure/tests/test_route_skillset*.py`

**Validation Command:**

```bash
./bin/ask skills route skill-factory "create a new skill package with evals" --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_route_decisions.py --json
```

**Acceptance Criteria:**

- Every route command can write a replay artifact.
- Ambiguity is preserved as an auditable decision, not just an error.

---

### GAP-007: Package Contract Lacks Behavior Type And Enforcement Level

**Category:** package contract / governance

**Current State:** Package contract fields include metadata, references, purpose, inputs, outputs, commands, permission profile, portability profile, evals, task profile, evidence policy. There is no normalized `behavior_type` or `enforcement_level`.

**Expected State:** Every skill package should declare how it behaves and how strongly it is enforced.

**Evidence Basis:** Operational analysis recommends behavior/enforcement fields for package readiness.

**Code Evidence:** `Infrastructure/config/schemas/skill-package.v1.schema.json`; `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py`; `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`.

**Risk:** Agents cannot tell whether a skill is advisory guidance, a mandatory gate, a review workflow, a deterministic validator, or a runtime tool projection.

**Severity:** High

**Fix Grade:** P0

**Recommended Fix:** Add fields:

```yaml
behavior_type: guidance | workflow | validator | reviewer | generator | runtime_projection | governance_gate
enforcement_level: advisory | recommended | required_for_authoring | required_for_closeout | blocking
```

Wire them through:

- scaffold template
- `references/contract.yaml`
- package schema
- `ask skills package --strict`
- eval template claims
- tests and fixture snapshots

**Suggested Software / Method:** JSON Schema enum, YAML contract parser, strict-mode migration warnings.

**Files Likely To Change:**

- `Infrastructure/config/schemas/skill-package.v1.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `skills-system/skill-creator/scripts/init_skill.py`
- `skills-system/skill-creator/scripts/quick_validate.py`
- `Infrastructure/templates/evals.yaml`

**Validation Command:**

```bash
./bin/ask skills package skill-factory-router --strict --json --robot
python3 skills-system/skill-creator/scripts/quick_validate.py /tmp/generated-skill
```

**Acceptance Criteria:**

- Strict package readiness fails if behavior/enforcement fields are missing.
- Scaffolded skills include valid defaults.
- Existing skills have migration warnings before becoming hard blockers.

---

### GAP-008: Skill Creator Validation Is Scaffold-Level, Not SDK-Release-Level

**Category:** validation / skills

**Current State:** `quick_validate.py` checks `SKILL.md` existence, frontmatter parsing, allowlisted keys, and basic name/description. It does not validate `references/contract.yaml`, `references/evals.yaml`, `agents/openai.yaml`, package readiness metadata, or Tessl/eval evidence.

**Expected State:** Skill creator should have a strict release gate that combines scaffold, OpenAI lint, description audit, package strictness, eval contract, and claim boundaries.

**Evidence Basis:** Operational analysis and user steering emphasize package contract, template quality, OpenAI lint, Tessl, validation, testing, and evals.

**Code Evidence:** `skills-system/skill-creator/scripts/quick_validate.py`; `skills-system/skill-creator/scripts/audit_skill_descriptions.py`; `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format_impl.sh`; `Infrastructure/templates/evals.yaml`.

**Risk:** A skill can be locally scaffold-valid but not SDK-ready.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:** Add `validate_skill_package_contract.py` or `skill_creator_release_gate.py` that runs:

- quick validate
- OpenAI frontmatter lint
- description audit strict
- contract file schema
- evals.yaml schema
- package strict readiness
- optional local Tessl eval staging check

**Suggested Software / Method:** Python validator with machine-readable JSON output; call it from `ask skills init --validate` and CI.

**Files Likely To Change:**

- `skills-system/skill-creator/scripts/quick_validate.py`
- `skills-system/skill-creator/scripts/validate_skill_package_contract.py`
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh`
- `Infrastructure/tests/test_skill_creator_*.py`

**Validation Command:**

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh
```

**Acceptance Criteria:**

- One command proves a scaffold is SDK-package-ready.
- Report differentiates scaffold, lint, package, eval, and Tessl lanes.

---

### GAP-009: Frontmatter Policy Drift Between Creator And OpenAI Lint

**Category:** validation / docs

**Current State:** Creator prose says not to expand frontmatter beyond `name` and `description`. `init_skill.py` emits `metadata`. `quick_validate.py` allows `metadata` but not `compatibility` or `triggers`; OpenAI lint allows `compatibility` and `triggers`.

**Expected State:** One explicit frontmatter policy shared by creator, lint, package contract, and docs.

**Evidence Basis:** User specifically asked whether templates pass OpenAI lint and validation.

**Code Evidence:** `skills-system/skill-creator/SKILL.md`; `skills-system/skill-creator/scripts/init_skill.py`; `skills-system/skill-creator/scripts/quick_validate.py`; `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format_impl.sh`.

**Risk:** Template changes pass one validator and fail another, or agents avoid useful fields due to stale prose.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:** Create a shared allowlist source or generated constants for:

- `name`
- `description`
- `license`
- `compatibility`
- `allowed-tools`
- `metadata`
- `triggers`

Then update creator guidance to say minimal required fields are `name` and `description`, while optional allowed fields are governed by the shared policy.

**Suggested Software / Method:** Shared JSON schema or Python constant imported by creator validator and OpenAI lint equivalent.

**Files Likely To Change:**

- `Infrastructure/config/schemas/openai-skill-frontmatter.v1.schema.json`
- `skills-system/skill-creator/scripts/quick_validate.py`
- `Infrastructure/scripts/validation-and-linting/lint_openai_skill_format_impl.sh`
- `skills-system/skill-creator/SKILL.md`

**Validation Command:**

```bash
python3 skills-system/skill-creator/scripts/quick_validate.py <skill-dir>
bash Infrastructure/scripts/validation-and-linting/lint_openai_skill_format_impl.sh --strict
```

**Acceptance Criteria:**

- Scaffold template passes both validators.
- Allowed keys match in code and docs.

---

### GAP-010: Events Surface Is A Catalogue, Not Durable Evidence

**Category:** traceability / observability

**Current State:** `skills events` reports `skill-events.v1` readiness and 8 declared event types. It does not prove those events are emitted by doctor/package/proof/eval execution.

**Expected State:** SDK commands should emit durable event rows for started/completed/blocker/decision states.

**Evidence Basis:** Operational analysis recommends a minimal event contract.

**Code Evidence:** `Infrastructure/scripts/lib/ask/commands/skills_impl.py` `skills_events`.

**Risk:** Teams think the system is observable because an event contract exists, but there is no replayable event stream.

**Severity:** Medium

**Fix Grade:** P1

**Recommended Fix:** Start with these events:

- `skill.doctor.started`
- `skill.source.resolved`
- `skill.projection.checked`
- `skill.package.checked`
- `skill.eval.started`
- `skill.eval.completed`
- `skill.lifecycle.decision`
- `skill.doctor.completed`

Write to `.harness/evidence/skills-sdk/events.jsonl`.

**Suggested Software / Method:** Append-only JSONL with schema validator.

**Files Likely To Change:**

- `Infrastructure/scripts/lib/ask/skills_sdk/events.py`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/config/schemas/skill-events.v1.schema.json`

**Validation Command:**

```bash
./bin/ask skills sdk doctor skill-factory-router --json --robot
tail -20 .harness/evidence/skills-sdk/events.jsonl | jq -c .
```

**Acceptance Criteria:**

- Each SDK command writes started/completed or blocked event rows.
- Event rows include `run_id`, `trace_id` optional, `skill_handle`, `source_path`, `status`, `evidence_path`, `timestamp`.

---

### GAP-011: Telemetry Providers Are Enrichment, But Not Yet A Minimal Event Pack

**Category:** observability / telemetry

**Current State:** `local_evidence_provider_status()` detects `~/.agents/otel-collector`, `~/.agents/session-collector`, and `~/.agents/observability-stack`, and reports `telemetry_confidence: enriched` when available. It correctly states artifacts decide and telemetry explains.

**Expected State:** The SDK should define a minimal telemetry/event pack that collectors can enrich without becoming mandatory for schema-valid output.

**Evidence Basis:** Operational analysis and user request to utilize observability/OTel at `~/.agents`.

**Code Evidence:** `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`.

**Risk:** Observability remains optional text rather than useful evidence joined to doctor/proof/eval decisions.

**Severity:** Medium

**Fix Grade:** P2

**Recommended Fix:** Add collector-enrichment fields to SDK event rows:

- `collector_status`
- `collector_freshness`
- `otel_trace_id`
- `session_trace_id`
- `telemetry_confidence`

Keep `required_for_readiness: false` unless a specific skill declares a stronger requirement.

**Suggested Software / Method:** Local file/HTTP health probes, schema-enforced optional fields.

**Files Likely To Change:**

- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/events.py`
- `Infrastructure/config/schemas/skill-events.v1.schema.json`

**Validation Command:**

```bash
./bin/ask skills package skill-factory-router --json --robot | jq '.data.skill_package.package_contract.evidence_providers'
```

**Acceptance Criteria:**

- SDK event rows include telemetry confidence when collectors are available.
- Artifact authority remains primary.

---

### GAP-012: Eval/Readiness Claim Boundaries Are Not Uniform Across Commands

**Category:** evals / governance

**Current State:** Package contract already says package proof does not prove runtime behavior, security posture, or human approval. Tessl docs say Tessl scores are evidence, not proof. Not every robot payload exposes `proves`, `does_not_prove`, and `readiness_claim_allowed`.

**Expected State:** Every quality command states what it proves, what it does not prove, and whether a readiness claim is allowed.

**Evidence Basis:** Operational analysis warns eval/proof/readiness lanes risk fragmentation.

 **Code Evidence:** `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`; `Infrastructure/scripts/lib/ask/commands/evals.py`; `Docs/agents/24-tessl-live-skill-eval-workflow.md`.

**Risk:** Agents collapse `eval passed` into `skill ready` or `package verified` into `runtime safe`.

**Severity:** High

**Fix Grade:** P1

**Recommended Fix:** Normalize claim boundary fields in `agent_contract` for:

- `skills package`
- `skills package verify`
- `skills proof`
- `skills prove`
- `evals run`
- `skills sdk doctor`

**Suggested Software / Method:** Shared helper and schema test snapshots.

**Files Likely To Change:**

- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `Infrastructure/scripts/lib/ask/commands/evals.py`
- `Infrastructure/tests/fixtures/*`

**Validation Command:**

```bash
./bin/ask evals run --help
./bin/ask skills package skill-factory-router --json --robot | jq '.. | objects | select(has("what_this_proves"))'
```

**Acceptance Criteria:**

- Robot JSON exposes claim boundaries in stable fields.
- Readiness claims require all relevant lanes.

---

## 6. Contradictions

### CONTRADICTION-001: `repo status` Says Synced While Handles Check Fails

**Claim:** `repo status` reported `skills_synced: true`.

**Actual Implementation:** `skills handles --check --check-command-handles` failed with `COMMAND_HANDLE_DRIFT` violations in current live tree.

**Evidence:** `repo status` only checks whether `.agents/skills` exists and appears synced; handles check performs deeper command-handle validation.

**Severity:** High

**Operational Impact:** Closeout and automation can see a green-ish repo state while generated runtime pointers are stale.

**Recommended Fix:** Make `command_surface_state` part of `repo status` / SDK doctor.

---

### CONTRADICTION-002: SDK Is Internally Real But Publicly Hidden

**Claim:** The project is becoming a Skills SDK.

**Actual Implementation:** SDK implementation is spread across `ask skills ...`; no public `ask skills sdk` or `ask sdk` entrypoint exists.

**Evidence:** `./bin/ask skills sdk --help` fails. `Infrastructure/scripts/lib/ask/skills_sdk/**` exists and is heavily used.

**Severity:** Medium

**Operational Impact:** External adopters and agents learn the internal topology instead of a compact SDK contract.

**Recommended Fix:** Add facade first, reuse existing internals.

---

### CONTRADICTION-003: Event Contract Exists But Runtime Events Are Not Durable

**Claim:** `skills events` reports `skill-events.v1` ready.

**Actual Implementation:** It exposes event contract metadata, not an append-only event stream produced by SDK command execution.

**Evidence:** Runtime proof writes fixed latest files; no durable SDK event JSONL is emitted by these command paths.

**Severity:** Medium

**Operational Impact:** Observability can be overestimated.

**Recommended Fix:** Implement append-only event writer and make events validator check real rows.

---

### CONTRADICTION-004: Creator Guidance And Validators Differ On Frontmatter

**Claim:** Creator guidance says keep frontmatter to `name` and `description`.

**Actual Implementation:** Scaffold emits `metadata`; quick validator allows `metadata`; OpenAI lint also allows `compatibility` and `triggers`.

**Severity:** Medium

**Operational Impact:** Template authors can satisfy one rule and violate another.

**Recommended Fix:** Single frontmatter schema shared by scaffold, docs, and validators.

---

## 7. Simplification Analysis

Do **not** build a second SDK control plane. The existing code already has most low-level mechanics. The smallest coherent product spine is:

```bash
./bin/ask skills sdk status --json --robot
./bin/ask skills sdk doctor <handle> --json --robot
./bin/ask skills sdk eval <handle> --json --robot
./bin/ask skills sdk project <handle> --json --robot
./bin/ask skills sdk sync --json --robot
```

Internally these should delegate to existing commands. The key work is to normalize outputs and evidence, not duplicate behavior.

What not to build yet:

- A new DSL for skills.
- A separate observability stack.
- A new package manager.
- A dashboard before durable events exist.
- A full external-repo init flow before the package contract and SDK doctor stabilize.
- A broad rename from `agent-skills` to `Skills SDK` before public command semantics are stable.

What to remove or simplify later:

- Merge overlapping `proof` / `prove` / `package` readiness interpretation behind SDK doctor.
- Convert docs-only claim-boundary warnings into shared command payload fields.
- Reduce frontmatter policy to one schema-backed source.

---

## 8. Implementation Roadmap

### Phase 1 — Critical Trust Boundary Fixes

**Objective:** Prevent false-success and give agents one safe SDK entrypoint.

**Fixes Included:**

- GAP-001 public `skills sdk` facade.
- GAP-002 shared `agent_contract` / `plane_contract`.
- GAP-003 command-surface state in repo/SDK status.
- GAP-012 uniform claim-boundary fields.

**Files Likely Affected:**

- `Infrastructure/bin/ask`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/scripts/lib/ask/commands/repo_impl.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `Infrastructure/config/schemas/*contract*.json`

**Validation Gates:**

```bash
./bin/ask skills sdk --help
./bin/ask skills sdk doctor skill-factory-router --json --robot
./bin/ask repo status --json --robot
./bin/ask skills handles --check --check-command-handles --json --robot
```

**Expected Risk Reduction:** High. Agents stop confusing partial status with SDK readiness.

---

### Phase 2 — Package Contract Hardening

**Objective:** Make skill package shape enforceable and agent-native.

**Fixes Included:**

- GAP-007 behavior/enforcement fields.
- GAP-008 creator release gate.
- GAP-009 frontmatter policy convergence.

**Files Likely Affected:**

- `Infrastructure/config/schemas/skill-package.v1.schema.json`
- `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py`
- `skills-system/skill-creator/scripts/init_skill.py`
- `skills-system/skill-creator/scripts/quick_validate.py`
- `skills-system/skill-creator/SKILL.md`
- `Infrastructure/templates/evals.yaml`

**Validation Gates:**

```bash
bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh
./bin/ask skills package skill-factory-router --strict --json --robot
```

**Expected Risk Reduction:** High. Scaffold-valid and SDK-ready become distinct, enforceable states.

---

### Phase 3 — Runtime Harness Maturity

**Objective:** Make runtime proof replayable and freshness-aware.

**Fixes Included:**

- GAP-004 append-only runtime proof ledger.
- GAP-005 runtime-card v2 identity/freshness.
- GAP-010 durable SDK event stream.
- GAP-011 telemetry event enrichment.

**Files Likely Affected:**

- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py`
- `Infrastructure/scripts/lib/ask/skills_sdk/events.py`
- `Infrastructure/config/schemas/runtime-card.v2.schema.json`
- `Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py`

**Validation Gates:**

```bash
./bin/ask skills proof skill-factory-router --runtime-target codex --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py --json
tail -20 .harness/evidence/skills-sdk/events.jsonl | jq -c .
```

**Expected Risk Reduction:** Medium-high. Proof becomes auditable across attempts.

---

### Phase 4 — Routing And Replay

**Objective:** Make skill selection explainable and regression-testable.

**Fixes Included:**

- GAP-006 persisted route decisions.
- Semantic routing-noise report.
- Route decision replay validator.

**Files Likely Affected:**

- `Infrastructure/scripts/lifecycle-and-sync/route_skillset.py`
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Infrastructure/config/schemas/route-decision.v1.schema.json`

**Validation Gates:**

```bash
./bin/ask skills route skill-factory "create a new skill package with evals" --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_route_decisions.py --json
```

**Expected Risk Reduction:** Medium. Routing changes become inspectable and replayable.

---

### Phase 5 — External Adoption

**Objective:** Make the repo usable as a portable Skills SDK.

**Fixes Included:**

- `ask skills sdk init --project-root .`
- Project-local SDK doctor.
- Example minimal project fixture.
- Docs rename path from Agent Skills Kit to Skills SDK.

**Validation Gates:**

```bash
tmpdir="$(mktemp -d)"
./bin/ask skills sdk init --project-root "$tmpdir" --json --robot
./bin/ask skills sdk doctor --project-root "$tmpdir" --json --robot
```

**Expected Risk Reduction:** Medium. External users get a stable adoption path without learning the whole internal repo.

---

## 9. Highest-Leverage Fixes

| Rank | Fix | Impact | Difficulty | Risk Reduced | Why First |
|---:|---|---|---|---|---|
| 1 | `ask skills sdk doctor` facade | Very high | Medium | False-success, UX ambiguity | Reuses existing mature commands and gives agents one reducer. |
| 2 | `command_surface_state` in status | High | Low-medium | Stale projections | Current live evidence shows drift can hide from `repo status`. |
| 3 | Top-level `agent_contract` / `plane_contract` | High | Medium | Overclaiming | Makes command authority explicit. |
| 4 | `behavior_type` / `enforcement_level` | High | Medium | Package ambiguity | Required for package contract strength and agent-native use. |
| 5 | Creator release gate | High | Medium | Scaffold-vs-ready confusion | Converts template quality into enforceable SDK readiness. |
| 6 | Durable SDK events JSONL | Medium-high | Medium | Auditability | Turns event contract into runtime evidence. |
| 7 | Runtime proof attempts ledger | Medium-high | Medium | Replay gaps | Preserves proof history without replacing latest files. |
| 8 | Runtime-card v2 freshness | Medium | Medium | Stale runtime truth | Prevents stale/absent runtime observation from looking current. |
| 9 | Route decision artifacts | Medium | Medium | Routing drift | Enables replay and routing-noise reports. |
| 10 | Shared frontmatter schema | Medium | Low | Validator drift | Keeps creator/OpenAI lint/template aligned. |

---

## 10. Testing And Validation Plan

Baseline commands for each patch family:

| Patch Family | Required Validation |
|---|---|
| SDK facade | `./bin/ask skills sdk --help`; `./bin/ask skills sdk doctor skill-factory-router --json --robot`; schema snapshot test. |
| Contract envelope | JSON schema validation for `agent_contract` and `plane_contract`; fixture snapshot update. |
| Command surface state | `./bin/ask repo status --json --robot`; `./bin/ask skills handles --check --check-command-handles --json --robot`. |
| Package behavior fields | `./bin/ask skills package <handle> --strict --json --robot`; package contract unit tests. |
| Creator validator | `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_impl.sh`; generated skill fixture tests. |
| Runtime events | Run proof twice and confirm JSONL has two attempts; validate schemas. |
| Runtime card v2 | `python3 Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py --json`. |
| Route decision replay | Route command emits artifact; replay validator passes on artifact. |
| Evals/Tessl boundary | `./bin/ask evals run --json --robot` in controlled lane; verify `proves` / `does_not_prove`. |

Testing rule: do not treat a passing eval as readiness unless the SDK doctor reducer says the relevant package, runtime, command surface, event, and claim planes pass.

---

## 11. Final Recommendation

Immediate next action: **build the smallest public SDK doctor facade**.

Safest first patch:

1. Add `ask skills sdk doctor <handle> --json --robot` as a delegating reducer.
2. Include `agent_contract`, `plane_contract`, `command_surface_state`, `package_state`, `runtime_state`, `event_state`, `readiness_claim_allowed`, and `next_safe_command`.
3. Add one fixture test and one live command validation.

Highest-risk missing system: **runtime truth reducer plus command-surface state.** The current code can produce strong evidence in separate lanes, but agents can still see a green repo status while command handles drift, and runtime proof history is not replayable.

Best validation command to add first:

```bash
./bin/ask skills sdk doctor skill-factory-router --json --robot
```

Broader Codex autonomy readiness: **not yet.** The project is agent-native in intent and partially agent-native in payloads. It becomes ready for broader autonomy when the SDK doctor reducer can answer, in one place, what is source, what is generated, what is stale, what is blocked, what proof exists, what evals prove, and what the next safe command is.
