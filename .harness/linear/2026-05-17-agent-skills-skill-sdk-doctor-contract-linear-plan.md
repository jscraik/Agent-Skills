---
schema_version: 1
selected_stage: he-linear-plan
source_reframe: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
source_strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
source_strategy_status: present
repo: agent-skills
slice: RF-1 doctor contract fixture for one skill
doctor_schema: Infrastructure/config/schemas/skill-doctor.v1.schema.json
live_cli_contract_status: blocked_missing_skills_doctor_action
live_cli_contract_checked_at: 2026-05-20
linear_mutation_status: created
live_linear_setup_status: partial
live_linear_checked_at: 2026-05-18
live_linear_current_status: Triage
live_linear_current_project: null
live_linear_current_assignee: null
linear_issue_id: JSC-329
linear_issue_url: https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7
label_status: partial
template_status: confirmation_required
decision_artifact_status: present
core_artifact_status: present
apparatus_lens_status: present
apparatus_lens: Infrastructure/references/skills-sdk-apparatus-lens.md
apparatus_lens_file_status: present
subagent_policy: not_used
roles_used: []
roles_recommended: [planning-specialist-agent, api-contract-reviewer, testing-reviewer]
roles_missing: []
---

# Agent Skills Kit Skill SDK Doctor Contract Linear Plan

## Command Summary

BLUF: This document's job is to convert RF-1 from the approved Skill SDK doctor-trust reframe into one live execution issue for Agent Skills Kit. It gives Jamie and future agents the Linear routing, scope, acceptance criteria, validation gates, rollback conditions, and evidence map for registering and hardening ./bin/ask skills doctor context7 --json --robot as the first professional SDK readiness contract. The plan matters because the live CLI does not expose skills doctor yet, so RF-1 must first replace the parser-level invalid-choice failure with a structured data.skill_doctor payload before fixture-backed proof through the Skills SDK apparatus lens can mean anything.

Decision Needed: Use the created Linear issue as the RF-1 execution handle, then plan RF-2 only after RF-1 closes with evidence.

Top Risks: Over-scoping RF-1 can turn a doctor registration and fixture slice into a broad SDK rewrite; treating planned package/profile/event seams as live commands would weaken the contract this issue is meant to prove; treating a polished skill artifact or AI review as readiness would bypass the verification apparatus; creating follow-on issues before RF-1 evidence would recreate backlog ceremony.

Next Action: Implement RF-1 against the live Linear issue after confirming the created issue routing is acceptable.

## Executive Linear Routing Summary

Classification: repo-specific implementation slice.

Selected slice: RF-1 from the SDK doctor-trust reframe.

Recommended action: use one live issue for RF-1. Do not create RF-2 through RF-6 yet.

Mutation status: created as JSC-329.

Live reconciliation, 2026-05-18: JSC-329 exists in Linear and remains in
Triage with no project assignment and no assignee. This matches the original
partial setup note. Treat JSC-329 as the active Skill SDK RF-1 execution handle,
but do not claim the local plan is fully routed until project assignment is
either intentionally left blank or updated in Linear.

## Target Linear Destination

- Team: Jscraik / JSC.
- Repo/location label: agent-skills was requested conceptually; exact label application depends on live label availability.
- Project: omitted unless Jamie confirms the exact healthy repo-control project.
- Cycle: empty.
- Initiative: empty.

live_linear_setup_status: partial.

live_linear_blocker: the issue was created without project assignment because exact repo-control project health and issue template IDs were not fully verified in this turn.

Live issue: JSC-329, https://linear.app/jscraik/issue/JSC-329/harden-skills-doctor-contract-fixture-for-context7.

## Existing Project Match

- Project name: agent-skills repo control project.
- Live evidence source: not fully verified in this run.
- Status: partial.
- Duplicate or canceled alternatives: unknown.
- Mutation safety: one repo-scoped issue created without project assignment to avoid attaching to an unverified destination.

existing_project_match: partial.

## ADR / Decision Artifact Readiness

decision_artifact_status: present.

Evidence:

- Source strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
- Source reframe: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- Apparatus lens: Infrastructure/references/skills-sdk-apparatus-lens.md
- Doctor schema: Infrastructure/config/schemas/skill-doctor.v1.schema.json
- RF-1 is selected as the smallest reversible implementation slice.

## Core / Invariant Artifact Readiness

core_artifact_status: present.

Relevant invariants:

- Agent Skills Kit owns SDK contract shape and canonical skill source.
- Coding-harness consumes stable JSON contracts and must not parse skill internals.
- `skills doctor` is an additive facade over current `skills prove`,
  `skills proof`, `skills explain`, audit, and future package signals. RF-1
  must not move or deprecate existing prove/proof semantics.
- skills doctor is the planned readiness aggregator. As of 2026-05-20 it is not
  registered in the live `ask skills` parser, so RF-1 must create the CLI seam
  before claiming a doctor baseline.
- skills doctor composes readiness signals; it does not replace package, eval, audit, or lifecycle events.
- The SDK is agent-native first: schemas, JSON output, fixtures, eval artifacts, lifecycle events, and harness consumer tests are authoritative. Human-facing docs are thin summaries and decision records only.
- Skills improve over time through eval feedback loops: every material pass, fail, warning, blocked, or not_run result can produce a classified improvement delta, bounded canonical update, rerun proof, and promotion or rollback evidence.
- The terminology flywheel is part of the SDK contract: repeated patterns from use and evals become controlled vocabulary in command JSON, schemas, fixtures, eval labels, package metadata, and harness reports.
- Jamie's mantra is the operating shape: Thin surface. Strong guardrails. Durable memory. Professional output.
- Skill readiness is trusted only to the degree that the verification apparatus signs off the exact claim: typed contract assertions, doctor/package/prove/eval commands, structural audits, representativeness probes, closeout validation, and rollback evidence.
- High-signal steering uptake is RF-0 and must remain a preflight gate.

## Proposed Milestones

No new milestone is required for RF-1.

## Proposed Parent Issues

Do not create a parent issue unless the full RF-1 to RF-6 program is promoted.

## Proposed Sub-Issues

### Issue 1: Register and harden skills doctor contract fixture for context7

template: Feature

issue_type: feature

priority: 2

repo_location_label: agent-skills

project_assignment_reason: bounded repo-specific implementation slice from an approved reframe.

cycle_assignment_reason: empty.

Objective: Register and harden the skills doctor JSON contract around context7 so Agent Skills Kit has a fixture-backed first proof point for professional Skill SDK readiness.

Source Artifacts:

- .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
- .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
- .harness/quality/steering-uptake.md
- Infrastructure/config/skills-sdk.json
- Infrastructure/references/skills-sdk-apparatus-lens.md
- Infrastructure/config/schemas/skill-doctor.v1.schema.json

Why This Matters: Agent Skills Kit is becoming a professional SDK of Codex skills. RF-1 proves the smallest readiness spine: doctor must first exist as a public `skills` action, then expose stable fields, status precedence, and safe next action without confusing runtime blockers, package warnings, or outcome-proof gaps.

Scope:

- Register `./bin/ask skills doctor <handle>` as a namespace-first public command.
- Keep `skills doctor` additive over `skills prove`, `skills proof`,
  `skills explain`, audit, and future package signals; do not deprecate or
  reinterpret existing `prove`/`proof` output in RF-1.
- Validate `data.skill_doctor` against
  `Infrastructure/config/schemas/skill-doctor.v1.schema.json`.
- Add a focused doctor JSON contract fixture or snapshot for context7.
- Add tests asserting required fields: schema_version, status, target_summary, checks, blockers, warnings, operation_context, contract_schemas, agent_summary, and next_command.
- Assert status precedence: blocked outranks warning, warning outranks pass, and pass requires no blockers or warnings.
- Assert next_command is present for blocked, warning, and pass states, and is null only when no safe next command exists.
- Preserve separate reporting for runtime reachability, package readiness, and outcome proof; package readiness may be reported as unavailable until a real package seam exists.
- Capture before and after doctor output and document tolerated environmental differences such as trace IDs and timestamps.
- Map readiness claims to the apparatus that signs them off: typed field assertions, focused tests, doctor/package probes, structural audit, representativeness, changed-file validation, and rollback evidence.
- Avoid adding human-facing docs unless they link to or reconcile the executable contract; prefer schema, fixture, eval, or machine-readable closeout artifacts.
- Include at least one counterexample-style assertion so malformed fields, skipped/not-run critical evidence, or blocker-first next_command drift cannot produce pass.
- Add an assertion-backed fixture for one additional non-`context7` skill class
  selected during implementation.

Deep Module Conformance:

- Public interface: `./bin/ask skills doctor <handle> --json --robot` plus the
  `skill-doctor.v1` JSON payload.
- Owner layer: `ask.commands.skills` owns the facade; the doctor service owns
  readiness aggregation, status precedence, and safe-next-command selection.
- Hidden implementation: source resolution, runtime projection checks,
  structural audit, package-readiness availability, outcome proof, and eval
  feedback classification are implementation details behind the doctor seam.
- Caller rule: coding-harness, Linear closeout, and future agents consume the
  doctor payload. They must not reconstruct readiness by reading skill internals
  or by chaining `prove`, audit, package, projection, and eval commands.
- Seam tests: parser/help/metadata/guided-error parity, schema snapshot tests,
  status-precedence assertions, and the second-skill fixture are required before
  the boundary may be called agent-safe.
- Current classification: `risky` until `skills doctor` is registered and the
  Phase A/B gates pass; target classification after RF-1 acceptance is `safe`.

Layered Project Module Map:

- Types: `Infrastructure/config/schemas/**`, command metadata, status
  vocabulary, and compatibility policy.
- Config: validation policy, permission profiles, runtime profiles, and repo
  execution defaults.
- Repo: canonical `Skills/**`, `Plugins/**`, `.harness/**`, and source
  artifacts.
- Providers: source, projection, package, audit, and eval readers that adapt
  repo state into typed inputs.
- Service: deep SDK modules such as doctor, package-doctor, profiles, events,
  routing, and compatibility checks.
- Runtime: `./bin/ask`, generated projections, plugin mirrors, and future
  app-server/CI contexts.
- UI: thin human-facing docs, visual maps, and summaries over the
  machine-readable contract.
- Utils: shared parsing, filesystem, JSON/schema, command, and formatting
  helpers that do not own product rules.

Observability Feedback Loop:

- Capture command, package, projection, eval, hook, and subagent lifecycle
  events as structured evidence.
- Keep RF-1 limited to doctor output plus eval/closeout evidence; do not invent
  the full event stack inside JSC-329.
- RF-2+ should let Codex query and correlate logs, metrics, traces, and eval
  results, then apply a bounded source change, rerun the workload, and record
  promotion or rollback evidence.
- Skills improve over time only when eval findings become classified deltas
  with affected paths, rerun commands, before/after evidence, and a final
  decision.
- Existing local adapters are available for this loop:
  `/Users/jamiecraik/.agents/otel-collector` for OTLP logs, traces, metrics,
  health, stats, freshness, and telemetry confidence; and
  `/Users/jamiecraik/.agents/session-collector` for privacy-safe session
  summaries, skill invocation analytics, skill proof candidates, and Harness
  Engineering evidence.
- Treat those collectors as optional evidence providers behind the SDK seam,
  not as mandatory RF-1 runtime dependencies.
- `Infrastructure/config/skills-sdk.json` is the machine-readable extraction
  contract for these sources. It defines which fields RF-1 and later slices
  should collect from doctor output, command surfaces, eval artifacts, Linear,
  and optional collector evidence.

Out of Scope:

- Broad SDK metadata migration.
- Publishing, sharing, or installing skills.
- Editing runtime projections by hand.
- Coding-harness consumer implementation.
- RF-2 negative-path matrix beyond the minimum needed to prove RF-1.

Execution Notes:

- Start with the current baseline: `./bin/ask skills doctor context7 --json --robot` exits 2 with parser error `invalid choice: 'doctor'`.
- Treat `./bin/ask skills package context7 --json --robot` as unavailable in the current CLI; it exits 2 with parser error `invalid choice: 'package'`.
- Treat `./bin/ask skills --help` and parser choices as the live command source
  of truth. Current unknown-action guidance mentions `external-review` even
  though help/parser output does not list that action, so RF-1 should reconcile
  guided-error text or avoid relying on it as contract evidence.
- Use `./bin/ask skills prove context7 --json --robot` as the current readiness-adjacent comparison evidence until doctor/package seams exist.
- Keep RF-0 steering uptake validator passing before closeout.
- Do not treat package metadata gaps as runtime blockers.
- Do not claim outcome proof from package readiness.
- Do not claim readiness from source presence, package presence, AI review, or coherent prose unless the apparatus evidence is named.

Validation Gates:

Phase A, registration and command-surface parity:

- python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json
- python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q
- ./bin/ask skills --help
- ./bin/ask skills prove context7 --json --robot
- python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py::test_skills_action_metadata_matches_parser -q
  proves parser actions, help output, command metadata, and unknown-action
  guidance expose the same `ask skills` action set

Phase B, post-registration contract proof:

- ./bin/ask skills doctor context7 --json --robot
- write snapshots to `artifacts/skill-doctor/context7.before.json`,
  `artifacts/skill-doctor/context7.after.json`, and
  `artifacts/skill-doctor/<second-skill>.after.json`
- python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py::test_skill_doctor_snapshots_validate_schema -q
  validates `data.skill_doctor` snapshots against
  `Infrastructure/config/schemas/skill-doctor.v1.schema.json`
- Focused pytest for the new doctor contract fixture
- Focused pytest for one additional non-`context7` skill-class fixture
- Apparatus signoff table in the eval or closeout artifact
- ./bin/ask repo validate --changed-files <changed-files> --json --robot

Rollback Conditions:

- Before RF-1 acceptance, a full revert may restore the parser-level
  invalid-choice snapshot.
- After RF-1 acceptance, ordinary rollback must preserve the `skills doctor`
  command and return degraded/blocking output that still validates against the
  schema.
- Removing the command after acceptance requires an explicit emergency waiver
  and reopens JSC-329/RF-1.

Acceptance criteria:

- `skills doctor` is listed by `./bin/ask skills --help` and dispatches through `Infrastructure/bin/ask`.
- Parser actions, help output, command metadata, and guided-error suggestions
  expose the same `ask skills` action set.
- `data.skill_doctor` validates against
  `Infrastructure/config/schemas/skill-doctor.v1.schema.json`.
- Doctor fixture asserts all required SDK readiness fields for context7.
- A second non-`context7` skill-class fixture asserts the same schema and status
  semantics.
- Status precedence is covered by tests or helper-level assertions.
- Runtime reachability, package readiness, and outcome proof remain separate in JSON output and agent summary, including a schema-valid `not_run` package-readiness check with unavailable command-surface evidence if no package command exists yet.
- next_command contract is asserted for the observed blocked baseline and any warning/pass fixture used.
- Readiness claims cite command/test/audit/eval/probe/validation evidence rather than source presence, package presence, AI review, or prose alone.
- Counterexample-style coverage exists for malformed fields, critical skipped/not-run state, blocker-first next_command behavior, or second-skill representativeness.
- Before and after snapshots record tolerated dynamic fields.
- RF-0 steering uptake checks still pass.

## Now / Next / Later / Do Not Create

Now: implement RF-1 using the live Linear issue as the execution handle.

Next: RF-2 negative-path readiness matrix after RF-1 closes with evidence.

Next SDK contract import, 2026-05-19: upstream Codex now has strong package,
lifecycle, namespace, permission, enablement, provenance, and environment
contract signals. Do not add those to JSC-329. Capture them as RF-2+ design
inputs and make the first post-RF-1 vertical slice skills package-doctor
<skill>.

Later: RF-3 profile/freshness determinism; RF-4 coding-harness schema consumer boundary; RF-5 review feedback intent radius; RF-6 migration of high-value HE/factory skills.

Do Not Create: one issue per SDK field; a broad package metadata migration issue before RF-1 proves doctor contract value; a coding-harness implementation issue before Agent Skills Kit owns a stable fixture.

## Dependency Map

- RF-0 steering uptake environment gate must stay green before RF-1 closeout.
- RF-1 blocks RF-2, RF-4, and RF-6.
- RF-3 can start after RF-1 only if fixture ownership is clear.
- RF-4 must not start until Agent Skills Kit exposes stable doctor/package/profile/event schemas.

## Eval Gate Map

- RF-1 eval artifact target: .harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md
- Required evidence: pre-RF-1 parser-failure output for `skills doctor context7`; `skills --help` before/after evidence; `python3 -m pytest Infrastructure/tests/test_ask_skills_command_contract.py::test_skills_action_metadata_matches_parser -q`; current `skills prove context7` comparison output; post-registration doctor output for context7; `artifacts/skill-doctor/context7.after.json`; `artifacts/skill-doctor/<second-skill>.after.json`; `python3 -m pytest Infrastructure/tests/test_ask_skills_doctor_contract.py::test_skill_doctor_snapshots_validate_schema -q`; context7 and second-skill fixture test results; changed-file repo validation result; explicit blocked/warning/pass classification evidence or recorded coverage gap for unavailable classes.
- Future eval-improvement evidence: each material eval result should include outcome, learning_class, proposed_delta, affected_canonical_paths, rerun_commands, before_after_evidence, promotion_decision, and rollback_decision.
- Terminology-flywheel evidence: doctor and eval fixtures should include controlled_vocabulary_version plus readiness_state, outcome_state, blocker_class, learning_class, delta_type, and promotion_decision when those fields apply.

## Human vs Agent Execution Map

Agent-safe: draft tests and fixtures; run help/prove/doctor probes; run focused pytest and repo validation; update eval artifact and implementation notes. Package probes are RF-2+ until the command is registered.

Human review required: review any change that alters public doctor JSON semantics; decide whether RF-1 should be current-cycle work.

## Story / Value Basis

As Jamie, I need skills doctor to produce stable SDK-grade readiness evidence for one representative skill so future agents and harness workflows can trust the command before relying on broader skill readiness claims.

Feedback signal: the fixture either proves the current doctor contract is already close enough, or exposes exactly which fields and status rules need implementation hardening.

Risk reduction: avoids broad SDK ceremony before proving one command-backed readiness spine.

## Recommended Labels

Conceptual labels: agent-skills; Feature; Roadmap Next; Developer Experience; Governance; Reliability.

label_status: partial.

## Repo / Location Label

repo_location_label: agent-skills.

## Priority Mapping

Priority: 2 High.

Reason: RF-1 is a migration blocker for the professional Skill SDK direction and for reliable harness consumption of skill readiness.

## Project / Cycle Justification

project_assignment_reason: bounded deliverable from approved reframe; project omitted until exact healthy repo control project is confirmed.

cycle_assignment_reason: empty.

## Project Reactivation Recommendation

Do not reactivate or create projects from this plan. If the canonical agent-skills repo project is archived, canceled, duplicated, or trashed, block project assignment and ask Jamie to confirm the target.

## Portfolio Ops Items

No Portfolio Ops item is recommended for RF-1.

## Dev Portfolio Impact

This is repo-specific Agent Skills Kit execution work. It supports Dev Portfolio indirectly by improving skill readiness evidence, but it does not need an initiative-level mutation for RF-1.

## GitHub PR Tracking

github_tracking_rule: include the Linear issue identifier in the branch name, commit message context, or PR body.

## Delivery Evidence

delivery_evidence_rule: a merged PR is implementation evidence, not shipped evidence. Closure should cite the RF-1 eval artifact, passing fixture tests, and changed-file repo validation.

## Evidence & Traceability Matrix

| Claim | Evidence |
| --- | --- |
| RF-1 is selected | .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md |
| North star is doctor-driven trust | .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md |
| Apparatus lens is the reusable reference | Infrastructure/references/skills-sdk-apparatus-lens.md |
| Doctor schema is bound | Infrastructure/config/schemas/skill-doctor.v1.schema.json |
| Current doctor baseline is command absent | ./bin/ask skills doctor context7 --json --robot exits 2 with parser error `invalid choice: 'doctor'` as of 2026-05-20 |
| Current package baseline is command absent | ./bin/ask skills package context7 --json --robot exits 2 with parser error `invalid choice: 'package'` as of 2026-05-20 |
| Guided-error action list drifts from parser/help | Unknown-action guidance currently mentions `external-review`, but `./bin/ask skills --help` and parser choices do not list it. Parser/help remain authoritative until reconciled. |
| Steering uptake is a preflight gate | .harness/quality/steering-uptake.md and validate_steering_uptake.py |
| Live Linear issue exists | JSC-329 verified live on 2026-05-18: Triage, no project, no assignee |

## Visual References / Diagrams

RF-0 steering uptake gate -> RF-1 doctor contract fixture -> RF-2 negative-path matrix -> RF-4 harness consumer boundary.

RF-1 also enables RF-3 profile and freshness determinism, RF-5 review intent radius, and RF-6 high-value skill migration.

## 2026-05-19 SDK Runtime-Contract Addendum

Source: local research against /Users/jamiecraik/dev/codex upstream commits
including 7f4d7ae3a, d661ab70e, c69cde354, 5c43a64e2, 3c7608187,
05b8ce435, 545ede569, b3ae3de40, ae10708ae, d3d38159e, a66e0e9c4,
9e9a62dc2, 826b2182e, ba57aab13, 55f6bbc66, 9289b7cea, 10f7dc6eb,
80fdd4688, 3009e2364, and 4dbca61e2.

Do not expand JSC-329. The addendum is a post-RF-1 SDK plan input.

| Codex runtime-contract signal | Agent Skills SDK import |
| --- | --- |
| Codex package builder | Add deterministic skill package layout, metadata, target rules, archive inspection, and validation. |
| SubagentStart hook | Model delegated agent starts as lifecycle events with role, cwd, parent run, expected artifact, and timeout. |
| Tool lifecycle contributor | Add tool/package/eval lifecycle events as proof, not prose. |
| Optional local environment | Add execution context classification: local, optional-local, remote, CI, app-server, unknown. |
| Canonical deny permissions | Normalize SDK permission profiles and eval fixtures around deny. |
| Namespaced/deferred tools | Keep skill, plugin, harness, eval, review, and release surfaces namespaced and search-first. |
| App-server skill enablement | Separate installed, projected, enabled, valid, discoverable, routable, and smoke-tested states. |
| Additive plugin upgrades | Require additive skill package upgrades unless a migration note explicitly removes capability. |
| Plugin id in tool metadata | Preserve skill/package/plugin/source provenance in reports and eval artifacts. |
| Skill/plugin injection extraction | Keep skill routing, skill context injection, plugin context injection, and prompt content distinct. |
| Context baselines for forks | Ensure review/harness subagents inherit the right baseline context. |
| Goal DB and explicit pause | Model run states as active, paused, blocked, usage-limited, and complete with exact reasons. |
| Hook runtime plumbing | Treat hooks as schema-validated runtime events. |
| Auditable AGENTS.md reads | Record discovered instruction files as filesystem evidence. |
| body_after_prefix compaction | Keep SKILL.md front doors short; move bulk detail to references. |
| Permission picker metadata | Let future control panes present valid permission profiles instead of prose-only modes. |
| Empty unknown tool schemas | Classify missing/malformed schemas as testable metadata defects. |

Recommended post-RF-1 vertical slice:

    ./bin/ask skills package-doctor context7 --json --robot

Minimum output contract: package metadata, namespace, permission profile,
required roots, enablement states, execution context, lifecycle events,
provenance, additive upgrade policy, checks, blockers, warnings, agent summary,
and safe next command.

## 2026-05-20 Live Checkout Reconciliation

Source: current branch codex/harden-he-domain-interview in
/Users/jamiecraik/dev/agent-skills.

The current branch does not register ./bin/ask skills doctor ... or ./bin/ask
skills package .... Both commands currently fail at argument parsing as unknown
skills actions. The adjacent live SDK surfaces are:

- ./bin/ask skills prove <handle> --json --robot, which emits
  skill-proof-scorecard.v1.
- ./bin/ask skills proof <handle> --json --robot, which emits command-handle
  reachability proof.
- ./bin/ask skills explain <handle> --json --robot, which emits the
  explanation/source/projection surface.

Plan correction: JSC-329 must include a public-boundary decision before it can
lock fixtures. Either register skills doctor as the stable SDK readiness facade
over existing proof/explain signals, or retitle RF-1 around the existing skills
prove contract. The preferred path is to register the facade because it
preserves a small, professional SDK consumer contract and keeps lower-level
proof internals replaceable.

Implementation-order correction:

1. Register or consciously defer the skills doctor action.
2. Map existing skill-proof-scorecard.v1, command-handle proof, and
   explanation/projection fields into the first data.skill_doctor response.
3. Add fixture tests for unknown-action regression, blocked reachability,
   package metadata warnings, outcome-proof gaps, and safe next command.
4. Only after that, design skills package-doctor as a post-RF-1 package
   readiness vertical slice.
