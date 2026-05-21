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
codex_runtime_alignment_checked_at: 2026-05-21
codex_runtime_alignment_origin_main: "20fedafff"
codex_runtime_alignment_sources: ["~/dev/codex", "codex-repo-mcp"]
runtime_evidence_contract_status: post_rf1_design_input
agents_observability_bridge_status: post_rf1_design_input
goal_board_status: prepared_not_started
goal_board_path: docs/goals/jsc-329-skill-sdk-doctor-contract/goal.md
goal_board_validated_at: 2026-05-21T10:58:43Z
goal_governor_guard_status: included_as_pre_slice
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

Next Action: Use the prepared \`/goal\` board only after Jamie says
\`proceed with governed implementation\`. Start with the
\`goal-governor-review-mode-guard\` pre-slice unless Jamie explicitly defers it,
then reconcile live \`skills doctor\` runtime state before choosing the smallest
remaining RF-1 contract proof.

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

Goal kickoff package, 2026-05-21:

- Board: docs/goals/jsc-329-skill-sdk-doctor-contract/goal.md
- State: docs/goals/jsc-329-skill-sdk-doctor-contract/state.yaml
- Receipts: docs/goals/jsc-329-skill-sdk-doctor-contract/receipts.jsonl
- Notes: docs/goals/jsc-329-skill-sdk-doctor-contract/notes/kickoff.md
- Implementation notes: .harness/implementation-notes/2026-05-21-agent-skills-jsc-329-goal-kickoff.html
- Validation: \`python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/jsc-329-skill-sdk-doctor-contract\` -> pass at 2026-05-21T10:58:43Z
- Status: prepared, paused, not started.

Included Goal Governor pre-slice:

- \`goal-governor-review-mode-guard\`
- Purpose: add review/dry-run mode so prompt review and \`not start yet\`
  requests cannot create or continue native goals.
- Run before the doctor RF-1 implementation slice unless Jamie explicitly
  defers it.

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
- Agent Skills standard compatibility means `SKILL.md` package shape and
  progressive disclosure. It does not make `.agents/skills/**` canonical
  source automatically.
- `.agents/skills/` is the interoperable cross-client root; `.codex/skills/`
  is a Codex-native root. Either may be project-local source only when the
  owner repo's `skills-sdk.json` declares it as
  `canonical_project_source`.
- Project-local skills are evaluated in place in their owner repo and write
  evidence back to that repo. Do not copy them into `agent-skills` or
  hand-edit generated projections to satisfy SDK checks.
- Project-local skills are created, installed, and updated through Skills SDK
  lifecycle commands, with evals as the promotion gate. The SDK saves skill
  source to `<owner-repo>/<declared-root>/<skill-handle>/`, portable evals to
  `<owner-repo>/<declared-root>/<skill-handle>/evals/evals.json`, SDK eval
  extensions to `<owner-repo>/.harness/evals/skills/<skill-handle>/`, and run
  evidence/events to
  `<owner-repo>/.harness/session-evidence/skills/<skill-handle>/<eval-run-id>/`.
- The planned lifecycle command surfaces are `skills create`,
  `skills install`, and `skills update`; each must return JSON evidence for
  the target root, eval gate, lifecycle events, and promote/rollback/blocked
  decision.
- Skills improve over time through eval feedback loops: every material pass, fail, warning, blocked, or not_run result can produce a classified improvement delta, bounded canonical update, rerun proof, and promotion or rollback evidence.
- The terminology flywheel is part of the SDK contract: repeated patterns from use and evals become controlled vocabulary in command JSON, schemas, fixtures, eval labels, package metadata, and harness reports.
- Post-RF-1 runtime evidence must distinguish declared capability, resolved
  runtime state, observed telemetry, portable eval proof, and harness
  enforcement. A polished readiness summary is not a substitute for those
  layers.
- Permission claims must separate declared profile, inherited profile, managed
  profile source, effective profile, runtime refresh, approval availability,
  fallback policy, runner enforcement, and observed effects. A single
  `repo-write` label is insufficient for an SDK-grade runtime contract.
- Goal-aware skills must distinguish active goal state, progress accounting,
  failed accounting flushes, goal-store availability, and final completion.
  Chat summaries and Linear issue state are linked context, not durable goal
  truth by themselves.
- Delegation evidence must cover both `SubagentStart` and `SubagentStop`
  or an equivalent terminal event. Artifact-written evidence alone does not
  prove delegated work closed cleanly.
- Extension and MCP-backed evidence must preserve `turn_id`,
  `truncation_policy`, `plugin_id`, marketplace/source attribution, and
  raw output references when those fields are available from the runtime.
- Package-backed skill or runtime claims must preserve archive checksum,
  platform package, DotSlash entrypoint, SDK launch source, bundled resource,
  and install-context provenance before they can support release-readiness
  claims.
- Networked skill evidence must distinguish disabled network, allowed network,
  MITM-inspected traffic, MITM hook enforcement, websearch-client use,
  external ingest, and redaction status.
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
- Preserve separate reporting for source ownership: canonical `Skills/**` and
  plugin-owned sources in this repo, manifest-declared project-local roots in
  owner repos, generated runtime projections, and unknown paths must not be
  collapsed into one source status.
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
  artifacts, plus manifest-declared project-local skill roots in owner repos.
- Providers: project-root, source, projection, package, audit, and eval readers
  that adapt repo state into typed inputs.
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
- Portable skill evals should remain compatible with the Agent Skills
  `evals/evals.json` pattern: realistic prompts, expected outputs, optional
  files, assertions, and with-skill versus without-skill or previous-skill
  comparisons. SDK fields such as trace IDs, lifecycle events, provenance,
  permission profile, namespace, telemetry confidence, and promotion decision
  are extensions over that baseline.
- Existing local adapters are available for this loop:
  `$HOME/.agents/otel-collector` for OTLP logs, traces, metrics,
  health, stats, freshness, and telemetry confidence; and
  `$HOME/.agents/session-collector` for privacy-safe session
  summaries, skill invocation analytics, skill proof candidates, and Harness
  Engineering evidence.
- Treat those collectors as optional evidence providers behind the SDK seam,
  not as mandatory RF-1 runtime dependencies.
- `Infrastructure/config/skills-sdk.json` is the machine-readable extraction
  contract for these sources. It defines which fields RF-1 and later slices
  should collect from doctor output, command surfaces, eval artifacts, Linear,
  and optional collector evidence.
- Post-RF-1, `.agents` should be treated as the local observed-evidence
  bridge: session collector and OTel collector evidence can prove permission
  profile refreshes, approval fallback rejections, goal accounting events,
  SubagentStart/SubagentStop pairs, extension tool-call turn binding, plugin
  attribution, MITM decisions, package runtime provenance, and websocket
  warmup versus logical request traces.
- The SDK must keep those collector fields optional until a slice explicitly
  wires them. The contract should say which fields are required, optional,
  unavailable, or not_applicable for each skill type rather than requiring all
  telemetry providers in RF-1.

Out of Scope:

- Broad SDK metadata migration.
- Registry publishing or hosted package upload in RF-1.
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

Next SDK contract import, 2026-05-21: upstream Codex now treats permissions,
goals, hooks, plugins, package runtimes, network policy, extension calls, and
thread settings as runtime-governed state. Do not add those to JSC-329/RF-1.
Capture them as RF-2+ Runtime Evidence Contract inputs and keep RF-1 focused
on registering the doctor seam and proving one stable JSON fixture.

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
| Latest Codex runtime-governance delta is design input only | Read-only local `~/dev/codex` check on 2026-05-21 showed `origin/main` at `20fedafff`; codex-repo MCP search confirmed matching code surfaces for permissions, hooks, plugins, packages, and extension evidence. |

## Visual References / Diagrams

RF-0 steering uptake gate -> RF-1 doctor contract fixture -> RF-2 negative-path matrix -> RF-4 harness consumer boundary.

RF-1 also enables RF-3 profile and freshness determinism, RF-5 review intent radius, and RF-6 high-value skill migration.

## 2026-05-19 SDK Runtime-Contract Addendum

Source: local research against the adjacent `codex` checkout's upstream commits
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

## 2026-05-20 Codex Runtime-Alignment Delta

Source: read-only check of adjacent `~/dev/codex` after origin/main reached
`59507b849` on 2026-05-20. The local Codex worktree was not modified.

This delta does not expand JSC-329/RF-1. It identifies Codex behaviors that
Agent Skills Kit should align to in RF-2+ package, lifecycle, profile, event,
and evidence contracts.

| New Codex signal | Commits | Agent Skills SDK alignment |
| --- | --- | --- |
| Turn-start metadata and async turn processing | `59507b849`, `1392a2a77` | Model skill runs as lifecycle events with run metadata, not prompt-in/prose-out transcripts. |
| Async approval contributors | `f64fce61b` | Add explicit approval states: not_required, requested, pending, approved, denied, expired, resumed, blocked. |
| Durable goal store wiring | `b555dd5d1`, plus `ba57aab13` baseline | Separate user objective, active goal, run contract, artifact contract, validation status, and closeout evidence. |
| Remote compaction timeout | `18cefba92` | Classify remote_compaction_timeout as runtime/infrastructure blocker, not task failure. |
| Remote/environment registration | `000bf5ce6`, `5c43a64e2`, `83af3abc6`, `954a9c857`, `1509ae6d8`, `c2141c7ce` | Require environment profiles: local, optional-local, remote, CI, app-server, unknown; default remote_ready false until proven. |
| Package layout detection and archives | `cfa16fcc2`, `57a68fb9e`, `343a74076`, `79f044ed3`, `59f262a2b`, `7f4d7ae3a` | Treat skills as packages with build, inspect, validate, install/project, warm, and smoke proof. |
| Skill/plugin startup warmup and enablement | `532b9c83a`, `ae10708ae`, `8335b56c3`, `dc255b0d8`, `d3d38159e` | Separate available, installable, installed, projected, enabled, warmed, runnable, validated, and release-ready. Keep upgrades additive unless a migration says otherwise. |
| Permission profile API and canonical deny | `c3faea0b0`, `3009e2364`, `3c7608187` | Add declared permission_profile metadata and drift checks; use `deny` as the canonical filesystem exclusion term. |
| Subagent lifecycle and namespace restraint | `d661ab70e`, `c53da029b`, `c58c84d6e`, `05b8ce435`, `b3ae3de40` | Record SubagentStart-style events with role, reason, expected artifact, service tier, timeout, closeout, and parent integration. Keep tools namespaced/search-first. |
| Raw/sensitive evidence handling | `5a4202ad9`, `34aad4368`, `e43a2e297`, `826b2182e`, `80fdd4688` | Evidence envelopes should distinguish raw_output_ref, parsed_result, summary, redaction_status, encrypted/sensitive output handling, and compacted context. |
| App-server/version/tool surface introspection | `149530234`, `05e171094`, `1dd9bf9a7`, `d269aa2af` | Prefer runtime introspection over inferred tool assumptions: app-server version, permission profiles, enabled skills/plugins, environment profile, and active goal state. |

Post-RF-1 contract fields to reserve:

```text
skill_package
permission_profile
environment_profile
runtime_capability
turn_start_metadata
async_approval_state
goal_ref
subagent_event
artifact_contract
evidence_envelope
raw_output_ref
redaction_status
validation_gate
drift_classification
```

Avoid using vague readiness terms in new contracts unless they map to fields:
`safe`, `done`, `handled`, `available`, `works`, `synced`,
`verified`, and `agent-ready`.

Recommended post-RF-1 vertical slice:

    ./bin/ask skills package-doctor context7 --json --robot

Minimum output contract: package metadata, namespace, permission profile,
required roots, enablement states, warmup state, runtime capability,
environment profile, async approval state, goal_ref compatibility, subagent
artifact policy, evidence envelope, lifecycle events, provenance, additive
upgrade policy, checks, blockers, warnings, agent summary, and safe next
command.

## 2026-05-20 Live Checkout Reconciliation

Source: current branch codex/harden-he-domain-interview in
`<repo-root>`.

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

## 2026-05-21 Codex Runtime-Governance Delta

Source: read-only local check of adjacent `~/dev/codex` plus codex-repo MCP
search after upstream `origin/main` moved from `59507b849` to
`20fedafff`. The local Codex worktree was not modified. Relevant local state
at the time of review: `~/dev/codex` remained on
`codex/update-codex-environment` with local edits and untracked harness/tmp
files, so this plan imports runtime ideas and contract shape only.

This delta does not expand JSC-329/RF-1. It upgrades the post-RF-1 design input
from package-oriented SDK readiness to runtime-governed agent operations:

```text
declared skill contract
-> resolved Codex runtime state
-> observed .agents telemetry/provenance
-> portable eval proof
-> coding-harness enforcement
```

| New Codex runtime-governance signal | Commits | Agent Skills SDK integration point |
| --- | --- | --- |
| Permission profiles are runtime policy, not static labels | `713a5b1b0`, `40ad7be2b`, `a27d3847b`, `63a72e6b7`, `729bdf3c8`, `896ee672c`, `e1ec0eee5`, `fe7c069fe`, `0edcc4b94`, `2b4898cc4` | Add permission resolution fields: declared, inherited, managed_source, effective, refreshed_at, approvals_enabled, fallback_policy, runner_enforcement, observed_effects. |
| Goals are default-on runtime state with accounting semantics | `0e9d22217`, `d4f842f3b`, `d84b824d5` | Model goal_absent, goal_active, goal_progress_accounted, goal_accounting_flush_failed, goal_store_unavailable, goal_cleared, and goal_complete. |
| Subagent lifecycle now has terminal stop evidence | `eee3e60db` | Require SubagentStart, ArtifactExpected, ArtifactWritten, SubagentStop, ParentIntegrated, ValidationRun, and ReviewerClosed before delegation is closed. |
| Extension tool calls carry turn identity and truncation policy | `c5bd13156` | Evidence envelopes should include turn_id, truncation_policy, evidence_complete, and raw_output_ref for extension-backed artifacts. |
| Plugin discovery and MCP tool items carry source identity | `0a4179bb1`, `60b45d92d`, `3075061bd`, `9265701b` | Preserve plugin_id, plugin marketplace, plugin source, and MCP attribution in skill reports and eval payloads. |
| Packages are installable, checksum-verifiable, platform-aware runtimes | `e9f59e30d`, `110b30d54`, `e389e01f8`, `cb05de672`, `f48be015d`, `80c4a978f`, `0b4f86095`, `0b5cf85b6`, `b0b383bea` | Extend package contracts with archive checksum, platform package, DotSlash entrypoint, SDK launch support, bundled resources, and install context. |
| Network policy can be enforced through MITM hooks and websearch clients | `3d94e24a3`, `f6970214d`, `3cae84009`, `ed6d73b3b` | Distinguish network_disabled, network_allowed, mitm_configured, mitm_enforced, websearch_client_used, external_ingest_allowed, and redaction status. |
| App-server thread settings are mutable runtime state | `771a4e74a`, `edc48e461`, `370b13afc` | Snapshot thread_settings_revision, resolved model/service tier, and permission profile at run start and closeout. |
| Compact SessionStart and websocket trace boundaries are observable | `af49d3837`, `20fedafff` | Separate compact startup/warmup evidence from logical user request evidence in collectors and harness reports. |
| Deferred tools are hidden from code-mode prompt | `a52c91d8b` | Skill docs and doctor guidance must not assume every capability is prompt-visible; prefer discover/request/probe semantics. |

Post-RF-1 agent-skills contract files to update after JSC-329 closes:

```text
Infrastructure/references/agent-native-skill-contract.md
Infrastructure/references/skill-validation-reporting-contract.md
Infrastructure/config/skills-sdk.json
Infrastructure/config/schemas/skill-doctor.v1.schema.json
```

Recommended split:

```text
skill-package-contract-v1:
  package layout, checksum, platform package, DotSlash entrypoint,
  SDK launch support, install context, bundled resources, projection targets

skill-runtime-contract-v1:
  permission resolution, goal accounting, hook lifecycle, turn binding,
  plugin attribution, network policy, thread settings, evidence envelope,
  runtime telemetry availability, harness enforcement classification
```

Runtime Evidence Contract v1 fields to reserve:

```yaml
runtime_evidence:
  codex_origin_main: 20fedafff
  thread_settings_revision: optional
  declared_permission_profile: required
  inherited_permission_profile: optional
  managed_permission_profile_source: optional
  effective_permission_profile: required
  permission_profile_refreshed_at: optional
  approvals_enabled: required
  fallback_policy: required
  fallback_rejected_reason: optional
  goal_accounting_status: optional
  goal_accounting_flush_status: optional
  extension_turn_id: optional
  truncation_policy: optional
  plugin_id: optional
  plugin_marketplace: optional
  subagent_start_seen: optional
  subagent_stop_seen: optional
  mitm_policy: optional
  websearch_client_used: optional
  package_checksum_ref: optional
  platform_package: optional
  dotslash_entrypoint: optional
  sdk_launch_source: optional
  warmup_trace: optional
  logical_websocket_request_id: optional
  raw_output_refs: required
```

Agent Skills Kit import rules:

- Keep JSC-329 focused on the public doctor seam and one stable fixture.
- Rename or extend the earlier package-only manifest concept so it does not
  underspecify runtime behavior. Preferred shape: skill package contract plus
  skill runtime contract.
- Add permission resolution tests after RF-1: a strict skill validation should
  fail when declared profile, inherited/effective profile, managed source, or
  fallback behavior is missing for operational skills.
- Add goal accounting language only to skills that claim to manage ongoing
  work. Skills that merely emit artifacts should explicitly mark goal progress
  accounting as not_applicable.
- Add plugin attribution fields for plugin-backed skills and MCP-backed tool
  evidence.
- Add compact warmup constraints: front-door `SKILL.md` content survives
  startup and compact startup; deep references remain lazy-loaded.
- Add discover/request language for deferred tools rather than assuming tools
  are visible in code-mode prompt.

Future eval cases to reserve in RF-2+:

```text
permission-profile-inheritance.case.json
managed-permission-profile-requirements.case.json
runtime-permission-refresh.case.json
approval-disabled-readonly-fallback.case.json
goal-accounting-flush-failure.case.json
subagent-stop-missing.case.json
thread-settings-drift.case.json
extension-tool-call-turn-id-missing.case.json
extension-tool-call-truncation-policy-missing.case.json
plugin-id-attribution-missing.case.json
plugin-marketplace-source-missing.case.json
mitm-network-policy-missing.case.json
package-checksum-missing.case.json
sdk-launch-provenance-missing.case.json
logical-websocket-warmup-noise.case.json
```

Future `.agents` bridge fields to reserve:

```text
permission_profile_resolution
permission_profile_runtime_refresh
managed_requirements_profile_source
approval_availability
approval_fallback_rejection
goal_accounting_event
goal_accounting_flush_failure
thread_settings_update
extension_turn_id
extension_truncation_policy
plugin_id
plugin_marketplace
marketplaces_considered
subagent_start
subagent_stop
compact_session_start
mitm_hook_decision
websearch_client_use
package_archive_checksum
platform_package
dotslash_entrypoint
sdk_runtime_launch_source
warmup_trace
logical_websocket_request_id
```

Do not edit `$HOME/.agents/otel-collector` or
`$HOME/.agents/session-collector` from this plan until their current dirty
work is intentionally adopted or stabilized. Treat them as optional evidence
providers for RF-2+ and as the likely owner of observed local telemetry,
provenance, and installed-state evidence.

Updated cross-repo ownership:

```text
agent-skills:
  owns declared skill package and runtime contracts

coding-harness:
  owns run-time enforcement and closeout governance

evals:
  owns portable positive and negative proof cases

.agents:
  owns observed local telemetry, provenance, installed-state, and runtime
  behavior evidence

codex:
  provides runtime primitives, app-server surfaces, hooks, package runtime,
  permissions, goals, extension calls, and plugin attribution
```

Updated risk list:

- Permission inheritance drift: declared skill profile differs from inherited,
  managed, or effective runtime profile.
- Runtime refresh drift: permissions change mid-run and risky phases continue
  under stale assumptions.
- Approval-disabled fallback: a write-required task silently continues in
  read-only mode when approvals are unavailable.
- Goal accounting loss: chat or Linear claims progress while durable goal
  accounting failed to flush.
- Subagent non-closure: a delegated agent writes an artifact but never emits a
  terminal stop event.
- Plugin attribution gap: MCP-backed evidence cannot identify the plugin or
  marketplace that supplied it.
- Network policy laundering: websearch or network ingest happens without MITM
  policy, enforcement, and redaction evidence.
- Package provenance gap: a packaged runtime launches without checksum,
  platform package, DotSlash entrypoint, or SDK launch-source evidence.
- Warmup trace confusion: warmup websocket traffic is misclassified as logical
  user work.

## 2026-05-21 Goal Kickoff Status

JSC-329 kickoff is now governed by
`docs/goals/jsc-329-skill-sdk-doctor-contract/goal.md`.

First slice completed:

- `T002 goal-governor-review-mode-guard` hardened Goal Governor so
  prompt-review and not-start-yet launch package requests route to
  `PROMPT_REVIEW_ONLY` unless the user explicitly says
  `proceed with governed implementation`.
- The slice added mode-specific contract metadata, review-mode eval metadata,
  and structure-aware regression coverage.
- Mandatory review stack findings were normalized in
  `.harness/reviews/2026-05-21-jsc-329-goal-governor/`.
- Accepted findings were fixed. Broader Goal Governor instruction dedupe and
  doctor-mode simplification are deferred to later bounded slices.

Validation evidence:

- `python3 -m pytest Skills/agent-ops/goal-governor/tests/test_check_goal_board.py`
  -> pass, 13 passed.
- `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/jsc-329-skill-sdk-doctor-contract`
  -> pass.
- `python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json`
  -> pass, 10 rooted skillset manifests written.
- `./bin/ask repo validate --changed-files <27 changed files> --json --robot`
  -> pass, required_failures 0, warn_only_issues 0, logs
  `Infrastructure/artifacts/validation/20260521T113707Z`.

Known deferral:

- Full rooted workspace sync remains blocked before mutation by pre-existing
  `COMMAND_HANDLE_PARENT_SYMLINK` violations under `.agents/skills`.

Next implementation slice:

- `T003 doctor-contract-live-reconciliation`: reconcile the smallest remaining
  RF-1 skills doctor public-contract proof without broadening into RF-2 runtime
  governance fields.
