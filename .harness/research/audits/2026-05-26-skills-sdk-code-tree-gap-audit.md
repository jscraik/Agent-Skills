# Skills SDK Code-Tree Gap Audit

Date: 2026-05-26

Target codebase: /Users/jamiecraik/dev/agent-skills

Audit basis:
- Live code tree inspection
- CLI help output from ./bin/ask skills ...
- Findings supplied by Jamie on the Skills SDK direction
- Current repo guidance in AGENTS.md, UBIQUITOUS_LANGUAGE.md, and CODESTYLE.md

## 1. Executive Summary

Overall maturity:

- Internal agent capability control plane: B
- Portable public Skills SDK: C+
- Agent-native command/evidence ergonomics: B-

The supplied findings are broadly correct, but the live tree has moved beyond several of the concerns. This is not just a planning deck anymore. The repo already contains skill-doctor.v1, skill-package.v1, skill-package-readiness.v1, skills-sdk.project.v1, runtime evidence schemas, package readiness command implementation, doctor command implementation, runtime adapter/evidence receipt machinery, conformance support, and boundary tests around extracted SDK modules.

The remaining issue is sharper: the project has strong internal mechanics, but the portable public SDK spine is still not the central executable path. The codebase can answer many expert questions, but it does not yet make the simple external-user questions mechanically obvious:

1. Where do project skills live?
2. What exact package shape must a skill satisfy?
3. How do I initialize another repo?
4. Which one command tells an agent the next safe action?
5. What does a pass prove and not prove?
6. Where is the lifecycle event stream?
7. Is this an active SDK contract or a planned surface?

Top 5 gaps:

1. No ./bin/ask skills sdk namespace exists, even though the findings identify sdk init and sdk doctor as the clean external adoption spine.
2. Infrastructure/config/skills-sdk.json is explicitly marked planning_contract while also pointing at active command and schema surfaces.
3. skill-package.v1 enforces Codex metadata compatibility, not the full portable SDK contract proposed in the findings.
4. Robot payloads do not expose a uniform agent_contract envelope with source authority, generated-path boundaries, claim permissions, and proves/does-not-prove fields.
5. Lifecycle events exist as vocabulary and payload fields, but not yet as a minimal required SDK event stream across the main lanes.

Top 5 risks:

1. Agents may treat planned lifecycle commands as implemented SDK capabilities.
2. External adopters may not find the safe path because the public CLI surface is wide.
3. Package readiness can pass narrower metadata checks while leaving permission, portability, eval, and evidence policy under-specified.
4. Evals, proof, readiness, package, external-review, and closeout lanes can still be conflated in summaries if the payload does not mechanically say what a command proves.
5. Telemetry/evidence providers remain optional enrichment without a minimal default lifecycle event contract.

Strongest foundations:

- Source/projection ownership is explicit and evidence-backed in skills-sdk.json.
- ./bin/ask skills doctor already aggregates resolver, runtime reachability, canonical source, projection ownership, structural audit, metadata, package readiness, and outcome proof checks.
- Package readiness now has a first-class schema and tests.
- Project-local manifest schema exists with root classifications and trust/precedence policies.
- Extracted ask.skills_sdk modules have boundary tests preventing command-layer coupling.

Highest-leverage next fixes:

1. Add ./bin/ask skills sdk init and ./bin/ask skills sdk doctor as thin facades over existing manifest, doctor, package, eval, and evidence checks.
2. Split active runtime SDK contract from planning contract, or add explicit active/planned section separation to skills-sdk.json.
3. Extend package schema with a portable SDK readiness layer for command contracts, permissions, portability, evals, and evidence policy.
4. Add a required agent_contract object to robot payloads for doctor, package, prove, eval, and SDK doctor.
5. Emit a small events.jsonl lifecycle stream for SDK lanes before integrating richer OTEL/session collectors.

Rename/productization position:

The eventual rename from agent-skills to Skills SDK is directionally correct, but it should be treated as an earned product milestone rather than a cosmetic repository rename. The current name still fits the present implementation: a strong, repo-local agent capability control plane. The Skills SDK name becomes fully accurate when another repository or agent can initialize, diagnose, validate, evaluate, inspect evidence, and receive a next safe command through a small public SDK spine without already understanding this repo's internal vocabulary.

Recommended rename gate:

- Use "Skills SDK" now as product direction and documentation language.
- Keep the repository name agent-skills until the public SDK spine exists.
- Rename the repository only after sdk init, sdk doctor, agent_contract, active/planned contract separation, and package portability checks are executable and validated.

## 2. Overall Gradecard

| Area | Grade | Confidence | Current Status | Main Gap | Recommended Fix |
|---|---:|---|---|---|---|
| Product frame as agent capability control plane | B+ | High | README frames the repo as governed skills plus runtime projection and evidence. | Product frame is broader than the portable SDK spine. | Add a minimal "Skills SDK in 7 nouns" public contract page and map advanced terms to it. |
| Source/projection ownership | A- | High | skills-sdk.json classifies .agents/skills as generated projection and Skills/** as canonical source. | Enforcement is strong internally but external adoption depends on manifest declaration. | Make sdk doctor fail closed when project roots are undeclared or ambiguous. |
| Agent-facing CLI and robot JSON | B | High | doctor, package, prove, events, profiles, memory, and sync surfaces exist. | Too many plausible next commands; no skills sdk facade. | Introduce ask skills sdk doctor as the what-next authority. |
| Minimal public SDK spine | D | High | Findings recommend sdk init, doctor, eval, project, sync; live CLI has no skills sdk action. | Missing namespace and setup path. | Add SDK action group with init/doctor/status/eval aliases. |
| Active vs planning contract separation | C- | High | skills-sdk.json has active command references but status is planning_contract. | Agents can confuse planned lifecycle commands with available commands. | Split skills-sdk.plan.json and skills-sdk.runtime.json, or add active/planned section schema. |
| Skill package contract | C+ | High | skill-package.v1 exists and validates Codex metadata/source files. | Does not enforce purpose/input/output/commands/permission profile/portability/evals/evidence policy. | Add skill-package-portability.v1 or extend skill-package.v1 with required SDK fields. |
| Project-local adoption | C | High | skills-sdk.project.v1 schema exists with roots, eval suite, evidence, trust, precedence. | No obvious init command creates the manifest and directories. | Add ask skills sdk init --project-root ... --json --robot. |
| Event and observability model | C | Medium | Lifecycle event names exist and evidence schemas exist. Runtime adapters read optional collector paths. | No minimal required events.jsonl stream emitted by every SDK lane. | Define 8 event types and write per-run JSONL receipts under owner evidence path. |
| Evidence/proof/readiness claim boundaries | B- | High | README separates eval, Plugin Eval, Tessl, and Snyk proof lanes; evidence receipt status vocabulary exists. | Payloads do not uniformly include proves, does_not_prove, and readiness_claim_allowed. | Add claim-boundary fields to quality-command schemas and payloads. |
| Architecture boundary enforcement | B | High | Tests ensure ask.skills_sdk modules do not import ask.commands and command facade does not own extracted helpers. | Boundary coverage is focused on module imports, not whole SDK contract. | Add schema tests for public SDK payloads and project-init fixtures. |

## 3. Evidence-to-Code Mapping

| Evidence Pattern | Source Basis | Code Location | Runtime Status | Grade | Confidence |
|---|---|---|---|---:|---|
| Skills as governed lifecycle artifacts | Findings BLUF, README product frame | README.md:1-40 | implemented_not_enforced | B | High |
| Small agent runtime surface | Findings 1.2, README context-small claim | README.md:22-25, README.md:65-83 | partial | B- | High |
| Source/projection ownership | Findings 1.3 | Infrastructure/config/skills-sdk.json:30-60 | implemented_enforced internally, partial externally | A- | High |
| Agent-facing doctor facade | Findings 1.4, 3.3 | skills_impl.py:3447-3785, skill-doctor.v1.schema.json | implemented_enforced | B+ | High |
| Package shape enforcement | Findings 3.4 | skill-package.v1.schema.json:1-225, test_ask_skills_package_contract.py | partial | C+ | High |
| Project-local manifest | Findings 3.7 | skills-sdk.project.v1.schema.json:1-111, skills-sdk.json:96-129 | scaffolded/partial | C | High |
| Public SDK namespace | Findings Move 1 | ./bin/ask skills sdk --help returns unknown action | missing | F | High |
| Minimal event model | Findings 3.5, Move 3 | skills_impl.py:1458-1510, skills-sdk.json:130-138 | scaffolded | C | Medium |
| Optional telemetry providers | Findings 3.5 | runtime_adapters.py, skills-sdk.json optional evidence providers | partial | C | Medium |
| Claim-vs-evidence separation | Findings 1.5, 3.6 | README.md:176-188, evidence-receipt.v1.schema.json:1-150 | partial | B- | High |
| Architecture extraction | Supplied architecture concern | test_skills_sdk_boundaries.py:36-74 | implemented_enforced | B | High |

Runtime status legend:

- implemented_enforced: executable, wired, and tested.
- implemented_not_enforced: executable or documented but not mechanically central.
- documented_only: stated in docs/config only.
- scaffolded: schema or placeholder exists but not enough executable path.
- partial: some working pieces exist, but contract is incomplete.
- missing: no executable surface found.
- overbuilt: many paths exist where one public path should be authoritative.

## 4. Gap Register

### GAP-001: Missing Public skills sdk Namespace

Category: runtime / agent-native UX

Current State:

./bin/ask skills exposes many actions, including doctor, package, prove, events, sync, install, init, and more. ./bin/ask skills sdk --help returns an unknown action.

Expected State:

The findings recommend a tiny public SDK spine:

    ./bin/ask skills sdk init --project-root . --json --robot
    ./bin/ask skills sdk doctor --json --robot
    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask evals run --json --robot
    ./bin/ask skills sync --json --robot

Important correction from review: do not document or plan around
`./bin/ask skills eval <handle>` unless that action is actually added. The
current executable eval lane is not a `skills` subcommand, so any public SDK
spine must either expose a real `skills sdk eval` facade or route explicitly to
the existing eval/prove/package/conformance commands.

Evidence Basis:

The supplied findings say the repo needs a smaller public SDK spine and an external adoption path. Live CLI evidence confirms no skills sdk action exists.

Code Evidence:

- README.md:65-83 lists a long AI-agent golden path.
- skills_impl.py:149-188 exposes many skill commands.
- CLI output: ./bin/ask skills sdk --help -> unknown action.

Risk:

Agents and external adopters have too many plausible paths and no single SDK bootstrap/doctor authority. Worse, if the SDK roadmap names commands that do not exist, the adoption path fails on the first terminal interaction.

Severity: High

Fix Grade: P0

Recommended Fix:

Add skills sdk dispatch with:

- sdk init: creates/validates project manifest and evidence directories.
- sdk doctor: summarizes project SDK readiness, declared roots, eval path, evidence path, skill roots, and next safe command.
- sdk eval: alias/facade over eval/prove package checks for a handle.
- sdk sync: facade over projection sync with source/projection guardrails.

Initial implementation can delegate to existing functions; do not duplicate logic.

Suggested Software / Method:

- Existing ./bin/ask dispatch layer
- JSON Schema for skills-sdk-doctor.v1
- Fixture snapshots in Infrastructure/tests/fixtures

Files Likely To Change:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/scripts/lib/ask/commands/skills.py or dispatch equivalent
- Infrastructure/config/schemas/skills-sdk-doctor.v1.schema.json
- Infrastructure/tests/test_ask_skills_sdk.py
- README.md

Validation Command:

    ./bin/ask skills sdk --help
    ./bin/ask skills sdk doctor --json --robot
    python3 -m unittest Infrastructure.tests.test_ask_skills_sdk

Acceptance Criteria:

- ./bin/ask skills sdk --help is a valid action.
- sdk doctor emits schema-valid JSON.
- sdk doctor marks undeclared external project roots blocked until manifest declaration.
- Payload includes a next safe command.

### GAP-002: Planning Contract Mixed With Active Runtime Contract

Category: governance / runtime

Current State:

Infrastructure/config/skills-sdk.json declares status planning_contract while also defining the active public interface, payload schema, root ownership policy, runtime targets, and project-local manifest requirements.

Expected State:

Agents should be able to distinguish active executable SDK contract, planned/reserved future surfaces, and non-goals.

Evidence Basis:

The findings explicitly warn that skills-sdk.json is still mostly planning-contract and can be mistaken for live capability.

Code Evidence:

- Infrastructure/config/skills-sdk.json:1-12 status is planning_contract, but current_slice.public_interface points to active ./bin/ask skills doctor.
- Infrastructure/config/skills-sdk.json:130-174 lists planned create/install/update interfaces.

Risk:

An agent may claim or invoke planned lifecycle commands as if implemented, especially create/update/project lifecycle commands.

Severity: High

Fix Grade: P0

Recommended Fix:

Either split the file into Infrastructure/config/skills-sdk.runtime.json and Infrastructure/config/skills-sdk.plan.json, or add explicit fields:

- contract_status: active
- active_sections: [...]
- planned_sections: [...]
- reserved_interfaces: [...]

Then validate that planned interfaces cannot appear in active_sections until executable tests exist.

Suggested Software / Method:

- JSON Schema
- jq
- Python schema/contract validator

Files Likely To Change:

- Infrastructure/config/skills-sdk.json
- Infrastructure/config/schemas/skills-sdk.extraction.v1.schema.json or new schemas
- Infrastructure/scripts/validation-and-linting/validate_skills_sdk_contract.py
- Infrastructure/tests/test_skills_sdk_contract.py

Validation Command:

    python3 Infrastructure/scripts/validation-and-linting/validate_skills_sdk_contract.py --json

Acceptance Criteria:

- Active interfaces are executable commands.
- Planned interfaces are explicitly marked unavailable or planned.
- Validator fails if a planned interface is listed as active without a test fixture.

### GAP-003: Package Schema Does Not Yet Define Full Portable SDK Shape

Category: validation / SDK contract

Current State:

skill-package.v1 exists and requires metadata, required_fields, and compatibility_status. For compatible packages it requires metadata.name, metadata.description, source_files.skill_md, and source_files.agents_openai_yaml.

Expected State:

The findings recommend a stronger package contract requiring name, description, purpose, input, output, commands, permission_profile, portability_profile, evals.path, and evidence_policy.

Evidence Basis:

The supplied findings say package shape is still too conventional/variable and should become a hard SDK schema.

Code Evidence:

- skill-package.v1.schema.json:7-49 requires only high-level compatibility fields and metadata.
- skill-package.v1.schema.json:183-224 compatible packages require metadata and source files, not command/eval/permission/evidence fields.
- test_ask_skills_package_contract.py:171-225 snapshots the narrower package contract.

Risk:

Skills can look package-compatible while lacking the operational details another repo or agent needs to safely expose and evaluate them.

Severity: High

Fix Grade: P1

Recommended Fix:

Add skill-package-portability.v1.schema.json or evolve skill-package.v1 with an sdk_contract object:

- purpose
- inputs
- outputs
- commands
- permission_profile
- portability_profile
- evals.path
- evidence_policy

Keep SKILL.md-first compatibility separate from SDK portability readiness. A canonical skill can be valid but not yet portable.

Suggested Software / Method:

- JSON Schema
- Existing package readiness command
- Snapshot tests

Files Likely To Change:

- Infrastructure/config/schemas/skill-package.v1.schema.json
- Infrastructure/config/schemas/skill-package-readiness.v1.schema.json
- Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py
- Infrastructure/tests/test_ask_skills_package_contract.py

Validation Command:

    ./bin/ask skills package <handle> --json --robot --strict
    python3 -m unittest Infrastructure.tests.test_ask_skills_package_contract

Acceptance Criteria:

- Package output distinguishes format_valid, sdk_portable, and promotion_ready.
- Missing command/eval/permission/evidence fields produce warnings or blockers according to strictness.
- Tests include at least one valid portable skill fixture and one non-portable-but-format-valid fixture.

### GAP-004: Missing Uniform agent_contract Envelope

Category: agent-native UX / governance

Current State:

Doctor and package payloads include agent_summary, next_command, operation context, lifecycle events, check summaries, blockers, and warnings. They do not expose one uniform agent_contract object across quality commands.

Expected State:

Every robot payload should tell an agent:

- source of truth
- editable paths
- generated paths
- forbidden actions
- next safe command
- readiness claim allowed
- what this proves
- what this does not prove

Evidence Basis:

The findings specifically recommend adding this object to every robot JSON payload.

Code Evidence:

- skill-doctor.v1.schema.json:7-26 required fields do not include agent_contract.
- skill-doctor.v1.schema.json:293-327 has agent_summary, next_command, and next_command_decision, but not source/proof/claim policy.
- skills_impl.py:3238-3299 package payload has summaries and next command, but not a uniform agent contract.

Risk:

Agents infer authority from prose and may overclaim readiness, edit generated paths, or confuse diagnostic output with promotion approval.

Severity: High

Fix Grade: P1

Recommended Fix:

Add a shared schema definition:

- source_of_truth
- editable_paths
- generated_paths
- forbidden_actions
- next_safe_command
- readiness_claim_allowed
- what_this_proves
- what_this_does_not_prove

Generate it in a shared helper used by doctor, package, proof, external-review, and future SDK doctor.

Suggested Software / Method:

- JSON Schema shared definition
- Snapshot tests
- jq smoke assertions

Files Likely To Change:

- Infrastructure/config/schemas/skill-doctor.v1.schema.json
- Infrastructure/config/schemas/skill-package-readiness.v1.schema.json
- Infrastructure/scripts/lib/ask/skills_sdk/contracts.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_ask_skills_doctor.py
- Infrastructure/tests/test_ask_skills_package_contract.py

Validation Command:

    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills package <handle> --json --robot

Acceptance Criteria:

- Every quality command emits agent_contract.
- readiness_claim_allowed is false unless promotion gates pass.
- Generated paths are listed explicitly.
- what_this_does_not_prove is non-empty.

### GAP-005: Lifecycle Event Model Is Present But Not Yet Minimal and Required

Category: traceability / observability

Current State:

The code defines lifecycle event types such as skill_loaded, skill_doctor_completed, package_readiness_checked, eval_started, eval_blocked, eval_completed, projection_synced, and manifest_changed. skills-sdk.json also plans owner-repo evidence paths and events.jsonl.

Expected State:

The findings recommend a tiny default lifecycle vocabulary:

- skill.doctor.started
- skill.source.resolved
- skill.projection.checked
- skill.package.checked
- skill.eval.started
- skill.eval.completed
- skill.lifecycle.decision
- skill.doctor.completed

Each event should include run ID, trace ID optional, skill handle, source path, projection path optional, status, evidence path, and timestamp.

Evidence Basis:

The findings say agent-native requires an event model, not just JSON commands.

Code Evidence:

- skills_impl.py:1458-1510 defines event vocabulary and producer/observer commands.
- skills-sdk.json:130-138 plans events.jsonl under owner repo evidence.
- evidence-receipt.v1.schema.json:35-38 supports runtime_event evidence type.

Risk:

Telemetry remains nice-later context rather than the replayable lifecycle record agents and humans can audit.

Severity: Medium

Fix Grade: P1

Recommended Fix:

Define a versioned skill-lifecycle-event.v1.schema.json and require doctor/package/prove/eval/sdk doctor to write or return events in that shape. Start local-first with JSONL before attempting OTEL integration.

Suggested Software / Method:

- JSONL event log
- Existing evidence receipt schema
- Optional OTEL/session collector enrichment

Files Likely To Change:

- Infrastructure/config/schemas/skill-lifecycle-event.v1.schema.json
- Infrastructure/scripts/lib/ask/skills_sdk/events.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_ask_skills_events.py

Validation Command:

    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills events --json --robot

Acceptance Criteria:

- A doctor run produces started/source/projection/package/proof/completed event records.
- Events are schema-valid.
- Events point to evidence artifacts when artifacts exist.
- Event writing is local-first and does not require OTEL.

### GAP-006: Quality Lanes Are Documented Separately But Not Mechanically Claim-Separated Everywhere

Category: validation / governance

Current State:

The README carefully separates evals, Plugin Eval, Tessl lint, Tessl review, and Snyk. Evidence receipt schemas also define claim statuses and runtime statuses.

However, command payloads do not uniformly emit proves, does_not_prove, and readiness_claim_allowed.

Expected State:

Every quality command should tell agents what claim it authorizes and what it does not authorize.

Evidence Basis:

The findings warn that eval/proof/readiness lanes risk fragmentation and that agents may say "eval passed, therefore skill is ready."

Code Evidence:

- README.md:176-188 explains lane separation in prose.
- evidence-receipt.v1.schema.json:7-16 requires claim and claim status.
- skill-doctor.v1.schema.json:7-26 does not require proves or does_not_prove.

Risk:

Closeout or readiness summaries may collapse distinct evidence lanes into false success.

Severity: High

Fix Grade: P1

Recommended Fix:

Add claim-boundary fields to the shared agent_contract and evidence receipt helpers. For each command:

- doctor proves current diagnostic state only.
- package proves package metadata/readiness gates only.
- prove proves runtime proof lane for the selected runtime target.
- external-review proves local review aggregation only.
- sdk doctor proves project SDK readiness only.

Suggested Software / Method:

- Shared claim policy table
- JSON Schema
- Snapshot tests

Files Likely To Change:

- Infrastructure/scripts/lib/ask/skills_sdk/contracts.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/config/schemas/*.schema.json
- Infrastructure/tests/test_ask_skills_doctor.py

Validation Command:

    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills package <handle> --json --robot
    ./bin/ask skills prove <handle> --json --robot

Acceptance Criteria:

- Each command emits non-empty what_this_proves.
- Each command emits non-empty what_this_does_not_prove.
- Readiness claims are blocked unless all required lanes pass.

### GAP-007: External Project Adoption Is Schema-Backed But Not Turnkey

Category: SDK adoption / workflow

Current State:

skills-sdk.project.v1.schema.json defines a project manifest with project_id, skill_roots, eval_suite.path, evidence.output_path, trust_policy, and precedence_policy.

Expected State:

External repo adoption should have a dead-simple init/doctor path.

Evidence Basis:

The findings recommend:

    ./bin/ask skills sdk init --project-root . --json --robot
    ./bin/ask skills sdk doctor --json --robot

Code Evidence:

- skills-sdk.project.v1.schema.json:7-15 requires project manifest essentials.
- skills-sdk.project.v1.schema.json:69-108 defines skill root classification and defaults.
- skills-sdk.json:96-129 describes owner repo manifest behavior.

Risk:

Only repo experts can operate the SDK. External users must reverse-engineer manifest shape and evidence paths.

Severity: Medium

Fix Grade: P1

Recommended Fix:

Implement sdk init to write a minimal manifest and create:

- declared skill source root
- .harness/evals/skills/
- .harness/session-evidence/skills/
- optional .agents/skills/.gitkeep only when declared as a projection or source root

Suggested Software / Method:

- Manifest generator
- Dry-run mode
- JSON Schema validation

Files Likely To Change:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/scripts/lib/ask/skills_sdk/project_manifest.py
- Infrastructure/config/schemas/skills-sdk.project.v1.schema.json
- Infrastructure/tests/test_ask_skills_sdk_init.py

Validation Command:

    ./bin/ask skills sdk init --project-root /tmp/ask-sdk-smoke --json --robot
    ./bin/ask skills sdk doctor --project-root /tmp/ask-sdk-smoke --json --robot

Acceptance Criteria:

- Init is idempotent.
- It refuses ambiguous roots unless explicitly declared.
- Generated manifest validates against skills-sdk.project.v1.
- Doctor reports source/projection/evidence/eval readiness.

### GAP-008: Public Vocabulary Is Still Dense

Category: documentation / agent UX

Current State:

The repo uses precise but dense vocabulary: canonical source, runtime projection, generated handles, visible runtime surface, package review, plugin-share, eval profile, lifecycle events, evidence receipts, conformance, proof, external-review, and more.

Expected State:

The findings recommend a smaller public vocabulary:

1. Source
2. Manifest
3. Doctor
4. Eval
5. Evidence
6. Projection
7. Decision

Evidence Basis:

The supplied findings call cognitive load the biggest issue for external adoption.

Code Evidence:

- README.md:17-37 presents many valuable product concepts.
- README.md:65-83 golden path includes nine commands before done.
- README.md:132-188 quality/readiness section introduces several lanes.

Risk:

A new agent or user can read the docs and still not know the shortest safe path.

Severity: Medium

Fix Grade: P2

Recommended Fix:

Add Docs/sdk/minimal-contract.md:

- Skills SDK in 7 nouns
- public command spine
- what each noun maps to in code
- what each command proves and does not prove
- one external project adoption example

Suggested Software / Method:

- Docs-only first, then validators later
- Link from README quick start

Files Likely To Change:

- README.md
- Docs/sdk/minimal-contract.md
- Docs/agents/README.md

Validation Command:

    ./bin/ask repo closeout --changed --json --robot

Acceptance Criteria:

- README quick start points to the minimal SDK contract.
- The contract uses the 7 nouns and avoids advanced internal terms until later.
- Each noun maps to a file, command, or schema.

### GAP-009: Observability Providers Are Optional But Not Yet a Default SDK Feedback Loop

Category: observability / traceability

Current State:

The architecture references optional telemetry/evidence providers such as ~/.agents/otel-collector and session evidence. Runtime adapters include evidence receipt and runtime status support.

Expected State:

The SDK should have a minimal event/evidence model that works without OTEL, then allow OTEL/session collectors to enrich it.

Evidence Basis:

The findings say telemetry must not become only nice-later context.

Code Evidence:

- evidence-receipt.v1.schema.json:35-38 includes runtime_event.
- evidence-receipt.v1.schema.json:138-148 includes runtime statuses including implemented_enforced, partial, blocked_runtime, and stale_or_drifted.
- skills-sdk.json:130-138 plans lifecycle event output paths.

Risk:

Runtime diagnosis depends on human memory or optional external collectors instead of built-in SDK evidence.

Severity: Medium

Fix Grade: P2

Recommended Fix:

Create a local evidence provider abstraction:

- default provider: JSONL events and evidence receipts in repo-local .harness/session-evidence/skills/
- optional provider: OTEL/session collector enrichment
- confidence fields: telemetry_confidence, freshness_status, provider_status

Suggested Software / Method:

- JSONL first
- Provider interface
- OTEL enrichment later

Files Likely To Change:

- Infrastructure/scripts/lib/ask/skills_sdk/evidence_provider.py
- Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py
- Infrastructure/config/schemas/evidence-provider.v1.schema.json
- Infrastructure/tests/test_skills_sdk_evidence_provider.py

Validation Command:

    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills events --json --robot

Acceptance Criteria:

- SDK doctor returns schema-valid output even when collectors are absent.
- Payload says whether telemetry is absent, stale, fresh, or enriched.
- Local evidence remains authoritative over telemetry commentary.

## 5. Contradictions

### CONTRADICTION-001: Planning Status vs Active Command References

Claim: skills-sdk.json is a planning contract.

Actual implementation: The same file points to active command and schema surfaces such as ./bin/ask skills doctor <handle> --json --robot.

Evidence: Infrastructure/config/skills-sdk.json:1-12

Severity: High

Operational impact: Agents can confuse reserved future surfaces with implemented SDK behavior.

Recommended fix: Split planning and runtime contracts or add active/planned section enforcement.

### CONTRADICTION-002: Minimal SDK Spine Recommended, But CLI Surface Is Broad and No SDK Namespace Exists

Claim: The SDK should have a small public spine.

Actual implementation: The README and CLI expose many quality and workflow paths. skills sdk is not a valid action.

Evidence:

- README.md:65-83
- README.md:132-188
- CLI output from ./bin/ask skills sdk --help

Severity: High

Operational impact: New agents have to infer which quality lane is authoritative.

Recommended fix: Add skills sdk namespace and make docs present it as the public front door.

### CONTRADICTION-003: Proof Lanes Are Separated in Prose, But Payloads Do Not Uniformly State Claim Boundaries

Claim: Evals, Plugin Eval, Tessl, and Snyk prove different things.

Actual implementation: The prose is strong, and evidence receipts have claim fields, but doctor/package payloads do not uniformly include proves, does_not_prove, and readiness_claim_allowed.

Evidence:

- README.md:176-188
- skill-doctor.v1.schema.json:7-26
- skill-doctor.v1.schema.json:293-327

Severity: High

Operational impact: Closeout summaries may still overstate what a green command means.

Recommended fix: Add shared claim-boundary fields to all robot payload schemas.

### CONTRADICTION-004: Package Schema Exists, But Does Not Yet Encode Full Portable Package Readiness

Claim: The repo is moving toward a Skills SDK package contract.

Actual implementation: skill-package.v1 validates core metadata/source compatibility, but not the full command/eval/permission/evidence package contract proposed by the findings.

Evidence:

- skill-package.v1.schema.json:7-49
- skill-package.v1.schema.json:183-224

Severity: Medium

Operational impact: A package can satisfy current compatibility while still being hard to adopt safely in another repo.

Recommended fix: Add a portability/readiness schema layer and expose its status separately from core format compatibility.

## 6. Missing Features

Runtime state:

- Missing skills sdk doctor as project-level runtime state facade.
- Missing default per-run SDK event stream.
- Partial runtime evidence receipts exist for proof, but not as a universal SDK lifecycle record.

Command selection:

- Missing one authoritative SDK front door.
- Current path relies on README sequence and next_command, but there are many plausible next commands.

Verification:

- Strong local verification primitives exist.
- Missing uniform claim-boundary fields across quality commands.

Validation:

- Existing JSON schemas are good foundations.
- Missing validator that fails if planned SDK interfaces are advertised as active.
- Missing package portability contract validation.

Architecture enforcement:

- Module boundary tests exist.
- Missing higher-level public SDK contract tests for sdk init, sdk doctor, and claim-boundary payloads.

Traces:

- Lifecycle event vocabulary exists.
- Missing required JSONL lifecycle stream for all SDK lanes.

Context:

- Source/projection separation is strong.
- Public conceptual vocabulary remains dense for new adopters.

Skills:

- Skill package shape is partially enforced.
- Missing portable eval and evidence-policy requirements in package schema.

Recovery:

- Existing doctor/prove/package next-command logic helps recovery.
- Missing project-level SDK recovery classification for undeclared roots, stale projection, missing eval suite, or missing evidence path.

Governance:

- Good docs and evidence receipts.
- Missing shared robot agent_contract object.

CI/CD:

- Tests cover schema snapshots and SDK module boundaries.
- Missing CI-visible gate for SDK active/planned contract separation and package portability schema.

Observability:

- Optional telemetry/evidence provider thinking exists.
- Missing default provider abstraction and freshness/confidence surface across SDK commands.

## 7. Fix Roadmap

### Phase 1 - Critical Trust Boundary Fixes

Objective: Reduce false-success, stale-state, unsafe-command, and planned-vs-active confusion.

Fixes included:

- GAP-001: Add ask skills sdk doctor facade.
- GAP-002: Separate active and planned SDK contract.
- GAP-004: Add agent_contract envelope.
- GAP-006: Add mechanical claim-boundary fields.

Files likely affected:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/scripts/lib/ask/skills_sdk/contracts.py
- Infrastructure/config/skills-sdk.json
- Infrastructure/config/schemas/skill-doctor.v1.schema.json
- Infrastructure/config/schemas/skill-package-readiness.v1.schema.json
- Infrastructure/tests/test_ask_skills_doctor.py

Validation gates:

    ./bin/ask skills sdk doctor --json --robot
    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills package <handle> --json --robot
    python3 -m unittest Infrastructure.tests.test_ask_skills_doctor
    python3 -m unittest Infrastructure.tests.test_ask_skills_package_contract

Expected risk reduction:

Agents stop confusing planned commands with active commands, and payloads directly prevent overclaiming readiness.

### Phase 2 - Mechanical Enforcement

Objective: Turn portable SDK package shape and project adoption into schemas and validators.

Fixes included:

- GAP-003: Add package portability contract.
- GAP-007: Add sdk init.
- Add active/planned contract validator.

Files likely affected:

- Infrastructure/config/schemas/skill-package-portability.v1.schema.json
- Infrastructure/config/schemas/skills-sdk.project.v1.schema.json
- Infrastructure/scripts/lib/ask/skills_sdk/package_contracts.py
- Infrastructure/scripts/lib/ask/skills_sdk/project_manifest.py
- Infrastructure/tests/test_ask_skills_sdk_init.py

Validation gates:

    ./bin/ask skills sdk init --project-root /tmp/ask-sdk-smoke --json --robot
    ./bin/ask skills sdk doctor --project-root /tmp/ask-sdk-smoke --json --robot
    ./bin/ask skills package <handle> --json --robot --strict

Expected risk reduction:

External projects can adopt the SDK without expert repo knowledge, and package readiness stops depending on convention alone.

### Phase 3 - Runtime Harness Maturity

Objective: Make lifecycle evidence replayable and provider-agnostic.

Fixes included:

- GAP-005: Minimal lifecycle event schema and JSONL output.
- GAP-009: Default evidence provider abstraction with optional telemetry enrichment.

Files likely affected:

- Infrastructure/config/schemas/skill-lifecycle-event.v1.schema.json
- Infrastructure/config/schemas/evidence-provider.v1.schema.json
- Infrastructure/scripts/lib/ask/skills_sdk/events.py
- Infrastructure/scripts/lib/ask/skills_sdk/evidence_provider.py
- Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py

Validation gates:

    ./bin/ask skills doctor <handle> --json --robot
    ./bin/ask skills events --json --robot

Expected risk reduction:

Post-run diagnosis no longer depends on optional telemetry or chat summaries.

### Phase 4 - Context and Skill Compression

Objective: Make the public contract simple enough for new agents and external users.

Fixes included:

- GAP-008: Add minimal SDK contract doc.
- README quick-start simplification around SDK nouns.

Files likely affected:

- README.md
- Docs/sdk/minimal-contract.md
- Docs/agents/README.md

Validation gates:

    ./bin/ask repo closeout --changed --json --robot

Expected risk reduction:

Lower cognitive load and fewer wrong-path command choices.

### Phase 5 - Governance and Scaling

Objective: Make readiness decisions scalable across skills, repos, and providers.

Fixes included:

- SDK-level readiness scorecard.
- Provider freshness/confidence policy.
- CI gate for SDK contract drift.
- Promotion decision artifact.

Files likely affected:

- Infrastructure/config/schemas/skills-sdk-readiness.v1.schema.json
- .github/workflows/**
- .harness/ci-required-checks.json
- harness.contract.json

Validation gates:

    ./bin/ask skills sdk doctor --json --robot
    ./bin/ask repo validate --ephemeral

Expected risk reduction:

The SDK can scale beyond Jamie-operated local workflows without losing source-of-truth discipline.

## 8. Highest-Leverage Fixes

| Rank | Fix | Impact | Difficulty | Risk Reduced | Why First |
|---:|---|---|---|---|---|
| 1 | Add ask skills sdk doctor | Very high | Medium | Wrong command path, weak adoption | Creates one front door without rewriting internals. |
| 2 | Add agent_contract envelope | Very high | Medium | False readiness claims, generated-path edits | Makes robot payloads self-governing. |
| 3 | Separate active/planned SDK contract | High | Low-Medium | Planned capability overclaiming | Small config/schema change with high clarity. |
| 4 | Add claim-boundary fields | High | Medium | Eval/proof/readiness conflation | Encodes the README's strongest doctrine mechanically. |
| 5 | Add package portability schema | High | Medium | Variable skill package shape | Converts SDK readiness from convention to contract. |
| 6 | Add sdk init | High | Medium | External adoption friction | Makes the SDK usable outside this repo. |
| 7 | Add lifecycle event schema + JSONL | Medium-High | Medium | Missing replayable evidence | Creates default observability without OTEL dependency. |
| 8 | Add minimal SDK contract doc | Medium | Low | Vocabulary overload | Gives humans and agents a small mental model. |
| 9 | Add active/planned contract validator | Medium | Low-Medium | Config drift | Prevents regression after the split. |
| 10 | Add provider freshness/confidence fields | Medium | Medium | Telemetry ambiguity | Keeps telemetry explanatory, not authoritative. |
| 11 | Stage the repo rename behind executable SDK gates | Medium-High | Medium | Product overclaiming, broken links, stale docs | Lets Skills SDK become a defended product name rather than a label change. |

## 9. Implementation Advice

Build first:

Build ask skills sdk doctor as a facade, not a rewrite. It should assemble project manifest status, root ownership status, existing doctor/package/proof summary, evidence path status, next safe command, and claim boundaries. This is the safest first patch because it clarifies the SDK without destabilizing existing lanes.

Do not build yet:

Do not build a large observability stack first. The repo already has enough complexity. Start with JSONL lifecycle events and make OTEL/session collectors optional enrichers.

Remove or simplify:

Do not remove existing expert commands. Instead, make the public SDK path prominent and classify the others as advanced/provider lanes.

Should become a validator:

- Active vs planned SDK contract separation
- Package portability requirements
- agent_contract presence in robot payloads
- Lifecycle event schema validity

Should become a schema:

- skills-sdk-doctor.v1
- skill-package-portability.v1
- skill-lifecycle-event.v1
- agent-contract.v1

Should become a skill:

External adoption and project-local SDK setup could become a skill once sdk init exists, but not before. The command should be the source of truth; the skill should route and explain it.

Should become documentation:

The 7-noun public model belongs in a short doc linked from README. Keep advanced terms in deeper architecture docs.

Should become CI:

Once agent_contract and active/planned validation exist, add them to the repo's standard validation lane.

Should remain manual:

Promotion decisions can remain human-reviewed initially, but the machine payload should clearly state whether promotion is allowed, blocked, or pending human approval.

### Rename and Productization Guidance

Use Skills SDK as the product direction now, but do not rename the repository yet.

The clean staging model is:

1. Product language now:
   - Keep the repo name agent-skills.
   - Introduce "Skills SDK" as the product name in README and SDK docs.
   - Say clearly that Agent Skills Kit is becoming Skills SDK.

2. SDK spine before rename:
   - Add ./bin/ask skills sdk init.
   - Add ./bin/ask skills sdk doctor.
   - Add ./bin/ask skills sdk status or equivalent if needed.
   - Keep these as facades over existing command/evidence lanes rather than a parallel implementation.

3. Contract freeze before rename:
   - skills-sdk.project.v1 must be active and validated.
   - skill-package-portability.v1 or equivalent must exist.
   - agent-contract.v1 must be emitted by robot payloads.
   - skill-lifecycle-event.v1 must define the local event stream.
   - skills-sdk-doctor.v1 must be snapshot-tested.

4. Rename only after adoption smoke:
   - Run sdk init and sdk doctor against a temp external project.
   - Confirm the generated manifest, evidence paths, source/projection classification, package readiness, and next safe command all work without repo-private knowledge.
   - Then rename the repository to skills-sdk or agent-skills-sdk.

Preferred final repo name:

- skills-sdk if the project is intended to be a broader, runtime-agnostic SDK.
- agent-skills-sdk if preserving the agent-native lineage is more important than broad public product clarity.

The cleaner product model is:

- Skills SDK = public product and repository identity.
- ask = command/control-plane CLI.
- skill = portable capability package.
- doctor/eval/proof/evidence = trust rails.
- Agent Skills Kit = lineage/current internal framing, eventually deprecated or kept as a historical term.

Rename risks to manage:

- Broken internal docs/scripts that hard-code agent-skills.
- GitHub redirects hiding stale generated artifact paths.
- Ambiguous product claims before sdk init/doctor are executable.
- Existing .agents and runtime projection references that should describe source/projection ownership, not the old repository name.
- PR/release notes accidentally claiming public SDK readiness before the gates above pass.

### Reviewer Addendum: Additional Gaps Found

Three independent reviews were run after the audit was updated:

- artifacts/reviews/2026-05-26-skills-sdk-gap-audit-architecture-strategist.md
- artifacts/reviews/2026-05-26-skills-sdk-gap-audit-agent-native-reviewer.md
- artifacts/reviews/2026-05-26-skills-sdk-gap-audit-adversarial-reviewer.md

The reviewers agreed with the main direction but found several sharper gaps that should be treated as first-class audit findings.

#### ADD-GAP-001: Owner Manifest Runtime Validation Bypass

Category: validation / architecture / agent-native UX

Current State:

_load_project_skills_sdk_manifest reads <repo_root>/skills-sdk.json with json.loads, checks only schema_version, detects duplicate normalized root paths, and then returns a manifest that can influence ownership decisions. Invalid JSON, wrong schema version, and duplicate-root cases are collapsed into absent/None-style behavior rather than becoming a structured blocker.

Expected State:

Every runtime path that consumes an owner project manifest should validate it against skills-sdk.project.v1 and return a typed manifest state: absent, valid, or invalid. Invalid manifests should fail closed with a blocker such as blocked_manifest_invalid and include the parse/schema/cardinality failure reason.

Code Evidence:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2513 loads the manifest directly.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2527 performs only duplicate normalized-root checks.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2541 uses the partially validated manifest for ownership classification.
- Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:73 defines lifecycle default flags but does not enforce unique defaults.

Risk:

A malformed owner manifest can silently degrade to undeclared behavior, or a root manifest can change doctor/source ownership semantics without a clear agent-readable blocker. This weakens the source/projection trust boundary exactly where the SDK needs deterministic external adoption diagnostics.

Recommended Fix:

Add a canonical project-manifest validator used by ownership, doctor, init, sync, and future lifecycle commands. Enforce required schema fields, declared root resolution, trust/precedence policy validity, and exactly one default root per create/install/update operation unless the operation is explicitly unsupported.

Validation Command:

    python3 -m unittest Infrastructure.tests.test_ask_skills_doctor Infrastructure.tests.test_skills_sdk_boundaries

Acceptance Criteria:

- Invalid JSON manifest reports blocked_manifest_invalid.
- Wrong schema version reports blocked_manifest_invalid.
- Multiple defaults for create/install/update report a deterministic validation error.
- Absent manifest remains distinct from invalid manifest.
- Doctor payload includes owner manifest path, schema reference, exact failure class, and next safe command.

#### ADD-GAP-002: Rename Identity Migration Is a Protocol Migration, Not a Cosmetic Rename

Category: governance / runtime / packaging / productization

Current State:

The project can use Skills SDK as a product direction, but multiple machine contracts still carry the current agent-skills identity. Schema IDs, doctor constants, package provenance trust, plugin cache selectors, and plugin state normalization all embed current names.

Expected State:

Before any repository rename, introduce an explicit compatibility strategy: neutral canonical IDs, legacy aliases, dual-read/dual-write migration where needed, and validation that old packages/state still verify while new Skills SDK identities are accepted.

Code Evidence:

- Infrastructure/config/schemas/skill-doctor.v1.schema.json:3 uses https://agent-skills.local.
- Infrastructure/config/schemas/skill-package.v1.schema.json:3 uses https://agent-skills.local.
- Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:3 uses https://agent-skills.local.
- Infrastructure/config/schemas/skill-doctor.v1.schema.json:387 still consts Agent Skills Kit.
- Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py:20 trusts current provenance source names.
- Infrastructure/scripts/lib/ask/services/plugin_cache.py:232 and Infrastructure/scripts/lib/ask/plugin_state.py:172 encode agent-skills-local identity assumptions.

Risk:

A rename can break package verification, plugin/runtime cache lookup, schema consumers, and human/operator expectations while appearing harmless through GitHub redirects.

Recommended Fix:

Create a rename-readiness validator that inventories schema IDs, provenance source names, plugin identities, docs, generated runtime projections, and package fixtures. Add explicit alias maps before replacing public names.

Validation Command:

    python3 Infrastructure/scripts/validation-and-linting/validate_skills_sdk_identity_migration.py --json

Acceptance Criteria:

- Both legacy agent-skills and new skills-sdk package provenance are accepted during migration.
- Schema ID aliases are documented and tested.
- Plugin/runtime selectors preserve existing agent-skills-local state or provide a deterministic migration.
- README/product docs state which names are current, legacy, and machine-contract identifiers.

#### ADD-GAP-003: Command Contract Drift Is Already Present in the Audit Layer

Category: runtime / documentation / CI/CD

Current State:

The live CLI has no skills sdk action and no skills eval action. The audit correctly treats skills sdk as missing/future work, but earlier wording also named a skills eval command that does not exist. Reviewers flagged this as a guaranteed adoption dead-end if copied into docs or implementation plans.

Expected State:

Any command string presented as executable in README, audits, specs, config, implementation notes, or generated docs should be checked against the live command parser or explicitly marked as proposed/future.

Code Evidence:

- Infrastructure/bin/ask:119 defines argparse command surfaces.
- Infrastructure/scripts/lib/ask/command_metadata.py:7 and :10 define a second metadata registry.
- ./bin/ask skills --help does not list sdk or eval as skills actions.

Risk:

Agents and external adopters follow a non-existent command, hit unknown action, and lose the safe next-command path that the SDK is supposed to provide.

Recommended Fix:

Add a command-contract lint that extracts ./bin/ask references from core docs, audits, specs, config, and robot guidance. It should classify each command as implemented, proposed, or invalid, and fail CI on invalid executable claims.

Validation Command:

    python3 Infrastructure/scripts/validation-and-linting/validate_skills_command_contracts.py --json

Acceptance Criteria:

- Existing references to future skills sdk commands are allowed only when labeled planned/proposed.
- References to unsupported commands such as skills eval fail unless the command is implemented or explicitly marked future.
- Parser and command metadata registries are checked for drift.

#### ADD-GAP-004: Init Semantics Are Ambiguous Between Skill Scaffold and SDK Project Bootstrap

Category: agent-native UX / project adoption

Current State:

ask skills init initializes a new skill scaffold and uses repo-specific defaults such as Skills/<category> and Agent Skills Kit ownership. The proposed SDK project bootstrap would naturally be named ask skills sdk init, but without careful UX the two init paths are easy to confuse.

Expected State:

Project-level SDK bootstrap should be separate from skill scaffolding, manifest-driven, and explicit about owner project roots, evidence paths, and non-editable projections.

Code Evidence:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py:4158 and :4184 scaffold skill package defaults.
- Infrastructure/config/skills-sdk.json:96-129 describes owner-repo manifest behavior as project-local SDK setup.

Risk:

A new external user runs the wrong init command, creates a skill package, and still lacks the SDK manifest and evidence directories required for doctor/adoption readiness.

Recommended Fix:

Make skills sdk init emit an explicit project manifest and directories only. Make skills init warn when the user appears to want project bootstrap. Both commands should emit agent_contract.next_safe_command.

Validation Command:

    ./bin/ask skills init --help
    ./bin/ask skills sdk init --help

Acceptance Criteria:

- Skill scaffold init and SDK project init are not interchangeable.
- Help output explains the distinction in agent-readable terms.
- SDK init never writes generated projection surfaces as canonical sources.

#### ADD-GAP-005: Root Manifest Filename Collision Can Make Diagnostics Stateful

Category: governance / runtime truth

Current State:

The owner project manifest path is <repo_root>/skills-sdk.json, while this repository also has an SDK planning/control file at Infrastructure/config/skills-sdk.json. A root-level manifest created during smoke testing can become an implicit authority for local doctor runs.

Expected State:

The repo should clearly distinguish the internal SDK control-plane contract from owner-project manifests. If the root manifest location remains, doctor must explicitly report which manifest was loaded and why.

Code Evidence:

- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2493-2538 auto-loads <repo_root>/skills-sdk.json.
- Infrastructure/config/skills-sdk.json:1-3 is a separate planning/control contract with a similar name.

Risk:

Local smoke tests or generated fixtures can unexpectedly change ownership classification and doctor results in the maintainer repo.

Recommended Fix:

Prefer .skills-sdk/project.json for owner manifests, or require doctor to report and validate the exact manifest source. Add a diagnostic determinism test proving doctor output changes only when a declared valid manifest is present.

Validation Command:

    python3 -m unittest Infrastructure.tests.test_skills_sdk_project_manifest_determinism

Acceptance Criteria:

- Internal control-plane config and owner project manifest are named or reported distinctly.
- Invalid root-level manifests never silently mutate doctor output.
- External fixture tests create manifests outside this repo or clean them up deterministically.

## 10. Final Recommendation

Immediate next action:

Implement ./bin/ask skills sdk doctor --json --robot as the public SDK readiness facade.

Safest first patch:

Add the command as a read-only aggregator over existing doctor/package/project/evidence checks. Do not change package readiness semantics in the same patch.

Highest-risk missing system:

The missing agent_contract envelope. Without it, agents still need to infer source authority, forbidden actions, and claim permissions from scattered fields and prose.

Best validation command to add first:

    ./bin/ask skills sdk doctor --json --robot

Whether the project is ready for broader Codex autonomy:

Partially. It is ready for repo-local Codex autonomy under the existing ask and evidence culture. It is not yet ready to be treated as a broadly portable Skills SDK without the public sdk facade, active/planned contract split, package portability contract, and uniform claim-boundary payloads.

Rename recommendation:

Use "Skills SDK" as the north-star product name immediately, but keep the repository named agent-skills until the SDK spine and claim-boundary contracts are implemented. Rename after the code can defend the name. The first rename-readiness validation command should be:

    ./bin/ask skills sdk doctor --json --robot

The rename is ready only when that command can explain source roots, projection status, package portability, eval/evidence status, claim boundaries, and next safe command for this repo and for a minimal external project fixture.

The steering line remains:

> A skill is SDK-ready only when an agent can discover it, understand its contract, validate its package, run its evals, inspect its evidence, know its projection status, and receive a safe next command without reading the whole repository.
