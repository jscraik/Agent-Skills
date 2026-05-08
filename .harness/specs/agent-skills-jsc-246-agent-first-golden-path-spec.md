---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-spec
artifact_type: he-spec
type: he-spec
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Spec
harness_stage: he-spec
status: draft
date: 2026-05-08
origin: .harness/linear/agent-skills-linear-plan.md
risk: medium-high
depth: bounded-execution-slice
ui: false
traceability_required: true
linear_status: existing
linear_issue: JSC-246
linear_issue_url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_parent_initiative: Dev Portfolio
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Build repo surface contract and agent capability control-plane golden paths"
linear_labels: "Roadmap: Next, Agent, Infra, Improvement"
linear_label_status: resolved_with_existing_labels
linear_priority: 2
selected_refactor: .harness/refactors/agent-first-golden-path.md
source_spec: Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md
---

# Agent Skills JSC-246 Agent First Golden Path Spec

## Mode Decision

This is a bounded HE spec for the approved next slice in
`.harness/linear/agent-skills-linear-plan.md`.

Selected slice:

- Linear issue: `JSC-246`
- Linear milestone: `Command surface and ask reliability`
- HE slice name: `Agent First Golden Path`
- Selected refactor: `.harness/refactors/agent-first-golden-path.md`
- Legacy source spec:
  `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`

This spec does not re-open all command-surface, cleanup, or skill-tree work. It
selects the next plan-ready behavioral contract: make the existing agent-first
loop dominant, compression-tested, and traceable enough for `he-plan`.

`JSC-230`, `JSC-167`, and `JSC-169` remain outside this slice unless explicitly
re-approved by a later Linear Delta Capture Gate.

## Linear Work Item Contract

`linear_status: existing`

Live Linear state captured during the delta gate:

```yaml
workspace: Jscraik
team: JSC
project: agent-skills
project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
milestone: Command surface and ask reliability
issue:
  key: JSC-246
  title: Build repo surface contract and agent capability control-plane golden paths
  status: Todo
  priority: 2
  labels:
    - Roadmap: Next
    - Agent
    - Infra
    - Improvement
  url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
  branch: jscraik/jsc-246-build-repo-surface-contract-and-agent-capability-control
relations:
  blocks: []
  blocked_by: []
delta_gate:
  prior_slice: JSC-284
  prior_slice_status: complete
  admitted_next_slice: JSC-246
  not_admitted:
    - JSC-230
    - JSC-167
    - JSC-169
```

The previous approved slice is complete in Linear:

| Issue | Status | Role |
| --- | --- | --- |
| `JSC-284` | Done | Prior parent issue |
| `JSC-285` | Done | Prior boundary-map child |
| `JSC-286` | Done | Prior extraction child |
| `JSC-287` | Done | Prior proof taxonomy ADR child |

## Problem Statement

Agent Skills Kit already has the important pieces of an agent capability control
plane:

- canonical skill source;
- generated command handles;
- runtime projection;
- `./bin/ask` command routing;
- repo health diagnostics;
- repo surface diagnostics;
- skill explain, improve, and prove commands;
- closeout reporting;
- proof vocabulary from the accepted proof taxonomy ADR.

The problem is not absence of commands. The problem is that the loop is not yet
binding enough as a product and agent operating contract.

A future agent should not need to infer the safe path by reading several docs,
scanning command metadata, and deciding whether repo surface, doctor, skill
routing, proof, or closeout should come first. The repository must make the next
safe action obvious from live command output.

The target loop is:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle-or-goal> --json --robot
./bin/ask repo closeout --changed --json --robot
```

`repo surface` is the diagnostic-debt lane selected by `repo doctor` when repo
surface findings are the current highest-signal next action.

This slice should turn that loop into the dominant control-plane path. It should
not add another broad cockpit, command catalog, or documentation layer unless
the spec proves that hiding, merging, or deriving the behavior from the existing
loop makes task completion worse.

## Goals

- Make `repo doctor` the live first-truth command for repo state and next action.
- Make `repo doctor` next-action output deterministic enough for agents to
  follow without repo archaeology.
- Preserve `repo surface` as the classification-first diagnostic lane for repo
  surface debt.
- Make `skills improve` the task-to-capability routing entrypoint.
- Make `skills explain` the capability comprehension entrypoint.
- Make `skills prove` the proof interpretation entrypoint, aligned with the
  proof taxonomy ADR.
- Make `repo closeout --changed` the completion-readiness entrypoint.
- Keep all machine-facing golden-path commands available through stable
  `--json --robot` output where supported.
- Reduce first-contact ambiguity by demoting or documenting adjacent commands as
  advanced, plumbing, compatibility, or follow-on work.
- Define compression gates so implementation cannot satisfy the spec by merely
  adding more docs or more commands.

## Non-Goals

- Do not implement broad artifact cleanup in this slice.
- Do not delete historical evidence or generated files in this slice.
- Do not absorb the `JSC-230` commandable skill-tree work.
- Do not implement `JSC-167` or `JSC-169` unless a later delta gate admits one
  of them.
- Do not create a new top-level command family unless ablation proof shows the
  existing namespace-first commands cannot carry the workflow.
- Do not add a new cockpit, dashboard, or status matrix as a substitute for the
  existing command loop.
- Do not rename public `ask` commands without a compatibility and rollback plan.
- Do not treat structural audit, command existence, or routing metadata as
  outcome proof.

## Source Evidence

### Hard Evidence

| Evidence | Result | Why It Matters |
| --- | --- | --- |
| `./bin/ask skills resolve he-spec --json` | Resolved `he-spec` to `Plugins/harness-engineering/skills/he-spec/SKILL.md` with source revision `cec4b3a59`. | Confirms this spec used the canonical HE Spec workflow. |
| Live Linear issue `JSC-246` | Status `Todo`, priority `High`, labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement`, project `agent-skills`. | Confirms the selected issue exists and is not already complete. |
| `.harness/linear/agent-skills-linear-plan.md` | Approved current slice is `JSC-246` / Agent First Golden Path. | Establishes this spec's allowed scope. |
| `.harness/refactors/agent-first-golden-path.md` | Defines the product spine as `repo doctor`, `skills improve`, `skills explain`, `skills prove`, `repo closeout`. | Establishes the intended architecture and migration pressure. |
| `./bin/ask repo doctor --json --robot` | Succeeded; reported non-blocking diagnostic debt and next command `./bin/ask repo surface --json --robot`. | Shows `repo doctor` already behaves as a live health and next-action surface. |
| `./bin/ask repo status --json --robot` | Succeeded; repo root readable and `skills_synced: true`. | Confirms baseline repo state is readable through `ask`. |
| `./bin/ask skills explain he-spec --json --robot` | Succeeded; reports canonical source, generated handle, runtime visibility, validation command, and reachability proof command. | Shows `skills explain` already has the right shape for the golden path. |
| `Infrastructure/bin/ask` command registration | Registers `repo doctor`, `repo closeout`, `repo surface`, `skills improve`, `skills explain`, and `skills prove`; no `repo onboard` or `repo next` action was found. | Prevents the spec from hallucinating currently implemented commands. |
| `.harness/decisions/agent-skills-proof-taxonomy-and-lifecycle-adr.md` | Accepted ADR defines proof levels: `reachability`, `structural`, `quality`, `outcome`. | Gives `skills prove` semantics for acceptance. |
| `./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot` | Succeeded with `status: resolved_with_fallback`, recommended `$autofix`, and also reported nested `goal_decision_status: intent_unresolved`. | Shows the command is useful but not yet cleanly deterministic enough to treat fallback routing as proof-quality routing. |
| `./bin/ask skills prove he-spec --json --robot` | Succeeded with `proof_status: reachable_without_outcome_proof`, structural audit pass, outcome workout available but not run. | Confirms proof semantics are already honest and should be preserved, then strengthened with proof-level assertions. |
| `./bin/ask repo closeout --changed --json --robot` | Failed with `sync_required` because unrelated canonical skill and generated projection files were already changed; emitted next command `./bin/ask skills sync --scope workspace --projection rooted --json --robot`. | Shows closeout already catches sync readiness, but also that eval fixtures must isolate spec-slice changes from unrelated worktree churn. |

### Interpretation

- The golden path should sharpen existing commands before adding new command
  families.
- `repo surface` is not a competing first command when `repo doctor` selects it
  as the next action.
- `repo onboard` and `repo next` remain candidate command shapes from the
  legacy source spec, not admitted implementation requirements for this slice.

### Assumptions

- The existing command registration can be improved without major CLI
  restructuring.
- Existing JSON envelopes are intended to remain stable enough for agents.
- README and agent docs can be compressed around command output without
  weakening human usability.

## Current-State Baseline

Captured on `2026-05-08` from live commands.

`repo doctor` baseline:

```yaml
command: ./bin/ask repo doctor --json --robot
status: success
blocking: false
agent_summary: "Usable with diagnostic debt: Repo surface has 4537 diagnostic finding(s)."
next_command: ./bin/ask repo surface --json --robot
signals:
  repo_status: pass
  projection_sync: pass
  catalog_parity: pass
  runtime_budget: pass
  command_handles: pass
  repo_surface: warn
```

Repo surface diagnostic debt from doctor:

```yaml
total_paths: 7779
blocking_findings: 4537
counts_by_code:
  tracked_historical_artifact: 4223
  indexed_reference_surface: 1076
  tracked_generated_work_area: 267
  ownership_decision_required: 39
  duplicated_infrastructure_path: 6
  unknown_surface: 2
```

Runtime and handle baseline:

```yaml
runtime_budget:
  status: pass
  default_visible_count: 10
  estimated_description_tokens: 3172
  violation_count: 0
command_handles:
  status: pass
  handle_count: 95
  violation_count: 0
```

`repo status` baseline:

```yaml
command: ./bin/ask repo status --json --robot
status: success
repo_root_resolved: /Users/jamiecraik/dev/agent-skills
is_git: true
skills_synced: true
```

`skills explain he-spec` baseline:

```yaml
command: ./bin/ask skills explain he-spec --json --robot
status: success
canonical_source: Plugins/harness-engineering/skills/he-spec/SKILL.md
generated_handle: .agents/skills/he-spec/SKILL.md
runtime_projection: rooted
runtime_visibility: latent
validation:
  - ./bin/ask skills audit Plugins/harness-engineering/skills/he-spec --level strict --json --robot
next_command: ./bin/ask skills proof he-spec --json --robot
```

Command registration baseline:

```yaml
present:
  - repo doctor
  - repo closeout --changed
  - repo surface
  - skills improve
  - skills explain
  - skills prove
not_found_as_registered_repo_actions:
  - repo onboard
  - repo next
```

`skills improve` baseline:

```yaml
command: ./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot
status: success
improvement.status: resolved_with_fallback
recommended_capability:
  handle: autofix
  confidence: 0.65
why:
  - fallback command-handle description match
  - matched terms=pr,review
goal_decision_status: intent_unresolved
goal_decision.failure_class: INTENT_UNRESOLVED
next_command: ./bin/ask skills proof autofix --json --robot
```

This is useful behavior, but not enough proof for deterministic routing. The
next plan must separate "fallback gave a usable route" from "goal routing
resolved cleanly." A fresh-agent path may rely on fallback only when the output
states that fallback was used, exposes confidence, and preserves a concrete
next command.

`skills prove he-spec` baseline:

```yaml
command: ./bin/ask skills prove he-spec --json --robot
status: success
proof_status: reachable_without_outcome_proof
reachability.status: pass
structural_quality.status: pass
outcome_proof.status: available_not_run
outcome_proof.workout_candidates:
  - harness-engineering/he-spec
next_command: ./bin/ask workouts run harness-engineering/he-spec --json --robot
```

`repo closeout --changed` baseline:

```yaml
command: ./bin/ask repo closeout --changed --json --robot
status: error
agent_summary: "Blocked: closeout has 1 blocker(s)."
commit_readiness.ready: false
commit_readiness.blockers:
  - sync_required
next_command: ./bin/ask skills sync --scope workspace --projection rooted --json --robot
changed_file_count: 57
note: output included unrelated pre-existing he-brainstorm and he-eval-report changes plus generated .skillsets projections
```

Closeout is already doing the right kind of pressure work. The next plan must
avoid treating the current dirty worktree as a clean golden-path fixture. Use an
isolated fixture, temporary branch, or explicitly scoped changed-file set when
proving `repo closeout --changed`.

## Baseline Gap Analysis

| Area | Current Strength | Gap To Close | Plan Implication |
| --- | --- | --- | --- |
| `repo doctor` | Composes repo status, sync, catalog parity, runtime budget, handles, repo surface, diagnostic debt, and one `next_command`. | Next-action priority ordering is implicit in implementation, not yet asserted as a contract with fixtures. | Plan must characterize and test next-action ordering before changing output. |
| `repo surface` | Already reachable and selected by doctor for current diagnostic debt. | Surface debt count is high and can dominate the loop; spec must keep it diagnostic rather than letting it become cleanup scope. | Plan may use surface output as evidence but must not delete or archive paths. |
| `skills improve` | Can recommend a useful capability and prove reachability. | Fallback can coexist with `intent_unresolved`; that is valuable but ambiguous for agents. | Plan must define clean resolved vs fallback-resolved vs blocked routing states. |
| `skills explain` | Already reports canonical source, generated handle, runtime projection, visibility, validation, and next proof command. | Needs representative coverage beyond `he-spec` and stable assertions for required fields. | Plan must add fixtures for at least one generated handle and one non-HE handle. |
| `skills prove` | Already separates reachability/structural validity from missing outcome proof. | Needs explicit proof-level fields aligned with the ADR, not only prose-like `proof_status` strings. | Plan must assert proof taxonomy mapping without overbuilding promotion gates. |
| `repo closeout --changed` | Detects sync-required blocker, focused validation, runtime budget, surface policy, and next command. | Live dirty worktree makes proof noisy; unrelated user work can pollute closeout evidence. | Plan must prove closeout in an isolated fixture or tightly scoped branch. |
| Docs/front door | README already shows the five-command loop. | Some docs still expose adjacent commands and older command names before proving first-contact compression. | Plan must budget docs deletion/demotion, not just add new copy. |

## Deterministic Next-Action Contract

`repo doctor` must emit at most one primary `next_command`. If multiple issues
exist, selection must follow a documented priority order.

Required priority order for this slice:

1. Repository unreadable or not a git repo.
2. Workspace skill runtime projection out of sync.
3. Catalog parity unresolved.
4. Runtime budget violation.
5. Command-handle validation failure.
6. Repo surface diagnostic debt.
7. Healthy repo status command.

Diagnostic debt continuation rule:

- Blocking failures may stop the agent until repaired.
- Non-blocking diagnostic debt may direct the agent to one diagnostic command,
  but it must not trap the agent in repeated diagnosis when a user task is
  active and all blocking health gates are green.
- The plan must decide whether this is represented as `next_command_kind`,
  diagnostic-debt freshness, a separate `diagnostic_debt[].next_command`, or an
  equivalent field already supported by the current output envelope.
- A fresh-agent eval must prove that after acknowledging or capturing repo
  surface debt, the agent can continue to `skills improve`, `skills explain`,
  `skills prove`, or `repo closeout` without needing to read docs.

For every priority level above, the plan must define:

- fixture or simulation strategy;
- expected `blocking` value;
- expected `agent_summary` class;
- expected `next_command`;
- whether diagnostic debt is blocking, warning, or informational.

The spec does not require every simulation to be implemented in the first code
slice if the repo lacks fixtures. It does require the plan to state which cases
are executable now, which are blocked by missing fixtures, and which must be
covered by focused unit tests around signal composition.

## Skill Routing Resolution Contract

`skills improve` must distinguish these states:

| State | Meaning | Agent Behavior |
| --- | --- | --- |
| `resolved` | Goal decision selected one primary capability without fallback. | Follow `recommended_capability` and `next_command`. |
| `resolved_with_fallback` | A useful fallback route was found after formal goal resolution failed or was ambiguous. | Follow only if confidence and rationale are present; preserve fallback note in evidence. |
| `blocked_ambiguity` | More than one plausible route exists and fallback is not safe. | Ask for narrowing or run the emitted diagnostic command. |
| `blocked_reachability` | A route was selected but command-handle proof failed. | Do not use the capability; follow the proof repair command. |

Acceptance must fail if `skills improve` hides an unresolved goal decision behind
a success summary without exposing fallback status, confidence, rationale, and
next command.

Representative routing fixtures should include:

| Goal | Expected Class | Notes |
| --- | --- | --- |
| `make agents better at fixing PR review comments` | `resolved` or explicit `resolved_with_fallback` to `$autofix` | Current live baseline is fallback-resolved; plan may tighten this. |
| `write a Linear-backed HE spec` | `resolved` to `$he-spec` or harness-engineering route | Exercises exact HE route. |
| `monitor a long-running HE work phase` | `resolved` to `$he-heartbeat` or harness-engineering route | Exercises operational routing. |
| `review this implementation against the spec` | `resolved` to `$he-code-review` or review route | Exercises review routing. |
| `fix validation blockers after review` | `resolved` to `$he-fix-bugs` or agent-ops/harness route | Exercises fix routing. |

The exact expected handles may be refined during `he-plan` after reading current
selection policy. The fixture set must not assert routes that current ownership
metadata cannot support.

Fixture stability rule:

- At plan time, resolve every expected handle through
  `./bin/ask skills resolve <handle> --json --robot` or an equivalent
  command-surface registry snapshot.
- Acceptance should assert route family and route class first, exact handle
  second, unless the handle is explicitly resolved and owned in the current
  projection.
- A fixture failure caused only by handle rename/projection drift should be
  classified separately from a routing-quality failure.

## Proof-Level Contract

`skills prove` must map output to the accepted proof taxonomy:

| Proof Taxonomy Level | Required Output Signal |
| --- | --- |
| `reachability` | Command handle resolves and required reachability gates pass. |
| `structural` | Audit target exists and structural audit passes. |
| `quality` | Quality evidence exists, such as review artifact, benchmark, workout design, or strict audit evidence when policy allows. |
| `outcome` | Workout, eval, transcript, or task evidence proves useful behavior in a representative scenario. |

`reachable_without_outcome_proof` is acceptable only when:

- reachability is explicit;
- structural status is explicit;
- outcome proof is missing or available-not-run;
- the next command points at the smallest outcome-proof action.

The plan must not introduce `trusted`, `default-visible`, or promotion status in
this slice. Those belong to later proof-driven promotion enforcement.

Boundary clause:

- `JSC-246` may map existing `skills prove` fields to proof taxonomy semantics
  in tests, evals, docs, or review assertions.
- `JSC-246` must not introduce a new proof schema, promotion gate,
  command-handle proof artifact, or trusted/default-visible lifecycle state
  unless a later Linear Delta Capture Gate explicitly admits the neighboring
  proof/handle work.
- If current output cannot support taxonomy assertions without schema changes,
  `he-plan` must record the gap and route schema work back to the proper
  proof/handle issue instead of expanding this slice.

## Closeout Isolation Contract

`repo closeout --changed` must be proven against a controlled changed-file set.

The live worktree currently includes unrelated canonical skill and generated
projection changes. That is useful evidence that closeout blocks on sync, but it
is not a clean fixture for `JSC-246`.

The next plan must choose one of:

- a temporary branch with only `JSC-246` fixture changes;
- a unit-level fixture for changed-file classification;
- an explicit test harness that passes controlled paths into closeout helpers;
- a documented blocked state if no safe isolation exists yet.

Closure must show both:

- a blocked closeout case with a concrete next command;
- a ready or validation-ready case where no unrelated sync blocker is present.

## Documentation Compression Contract

The README already exposes the five-command golden path. The next plan should
not simply add more prose.

Required compression behavior:

- Identify every first-contact doc section touched.
- Mark each touched section as `keep`, `collapse`, `demote`, `generate`, or
  `delete`.
- Ensure the diff does not increase the number of first-contact paths.
- Prefer command examples that match live `./bin/ask` behavior.
- Treat broad command catalogs as advanced/reference material unless the user
  explicitly asks for catalog browsing.

Docs subtraction is not sufficient by itself. The plan must pair any line-count
or section-count reduction with at least one behavior metric from the fresh-agent
eval, such as:

- number of commands required to reach ready-or-blocked;
- number of docs opened for basic navigation;
- misroute or ambiguity count from `skills improve` fixtures;
- whether the agent followed command-emitted `next_command` without manual repo
  browsing.

Minimum docs to inspect during planning:

- `README.md`
- `AGENTS.md`
- `Docs/agents/16-agent-operating-contract.md`
- `Docs/agents/5-minute-success-path.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`

Do not edit all of these by default. Inspect them to decide the smallest
compression-safe docs change.

## Plan Constraints

The next `he-plan` must sequence work in this order:

1. Characterize current command behavior with snapshots and fixtures.
2. Define next-action ordering and route-state vocabulary.
3. Add focused tests or fixture assertions for behavior that already exists.
4. Tighten command behavior only where tests show a gap.
5. Apply documentation compression after behavior is stable.
6. Run fresh-agent and ablation proof.
7. Write eval evidence before parent closure.

Do not start by rewriting docs. Do not start by adding aliases. Do not start by
cleaning artifacts. Those paths create apparent progress while avoiding the
actual control-plane contract.

## System Boundary

### In Scope

- `./bin/ask` public command behavior for the admitted golden path.
- `Infrastructure/bin/ask` command registration and alias correction behavior
  only where necessary to preserve the selected loop.
- `Infrastructure/scripts/lib/ask/commands/repo.py` for `repo doctor`,
  `repo surface`, and `repo closeout` behavior.
- `Infrastructure/scripts/lib/ask/commands/skills.py` for `skills improve`,
  `skills explain`, and `skills prove` behavior.
- `Infrastructure/scripts/lib/ask/golden_path.py` where it composes doctor and
  next-action semantics.
- `Infrastructure/scripts/lib/ask/command_metadata.py` where help/examples
  influence discoverability.
- README and high-traffic agent docs that define first-contact workflow.
- Focused tests, fixtures, snapshots, or eval artifacts required to prove the
  golden path.

### Out of Scope

- `JSC-230` commandable skill tree implementation and child issues.
- Mass cleanup of `artifacts/**`, `Infrastructure/artifacts/**`, `.skillsets/**`,
  `.harness/*.db`, `skills-system/**`, or `Plugins/cache/**`.
- Broad command modularization beyond what the completed `JSC-284` slice already
  unlocked.
- New plugin marketplace behavior.
- New Linear issues, milestones, or labels unless the later plan explicitly
  routes them.
- Unrelated skill content rewrites.

## Domain Model

| Term | Meaning In This Spec |
| --- | --- |
| Agent Capability Control Plane | The `./bin/ask`-centered system that routes, explains, proves, validates, and closes out agent capabilities. |
| Golden Path | The smallest remembered command loop that takes an agent from repo state to capability selection, proof, and closeout. |
| First Truth Command | The command a future agent should run before reading broad docs or scanning repo history: `./bin/ask repo doctor --json --robot`. |
| Next Action | A deterministic command or file action emitted by the current truth surface. |
| Diagnostic Debt | Non-blocking but real repository issues that should be surfaced without claiming the repo is broken. |
| Capability Route | The selected skill, plugin, or workflow returned by `skills improve` for a task goal. |
| Capability Explanation | The canonical source, generated handle, runtime projection, limitations, and validation for a capability. |
| Proof Level | One of `reachability`, `structural`, `quality`, or `outcome`, as defined by the proof taxonomy ADR. |
| Completion Readiness | The state reported by `repo closeout --changed`, grounded in actual changed files and validation needs. |
| Advanced Surface | Useful commands or docs that should not compete with the golden path for first-contact attention. |

## Lifecycle

### 1. Start From Repo Truth

The agent runs:

```bash
./bin/ask repo doctor --json --robot
```

The command must answer:

- is the repo usable;
- are there blocking failures;
- what diagnostic debt exists;
- what exact command should run next.

If repo surface debt is the most important next action, `repo doctor` may direct
the agent to:

```bash
./bin/ask repo surface --json --robot
```

That keeps `repo surface` subordinate to the first truth command instead of
turning it into another first-contact entrypoint.

### 2. Translate Goal To Capability

The agent runs:

```bash
./bin/ask skills improve "<goal>" --json --robot
```

The command must return one primary route when the evidence supports one.
Ambiguity is allowed only when the goal genuinely maps to multiple plausible
capabilities.

### 3. Explain Before Use

The agent runs:

```bash
./bin/ask skills explain <handle> --json --robot
```

The command must distinguish:

- generated command handle;
- canonical source;
- runtime projection;
- runtime visibility;
- validation command;
- limitations and ambiguity.

### 4. Prove Before Trust

The agent runs:

```bash
./bin/ask skills prove <handle-or-goal> --json --robot
```

The command must not imply `trusted` or `default-visible` status from
reachability alone. Proof output must map to the proof taxonomy ADR.

### 5. Close Out Against Changed Files

The agent runs:

```bash
./bin/ask repo closeout --changed --json --robot
```

The command must report focused validation, sync needs, blockers, diagnostic
debt, and whether commit/PR work is ready, blocked, or requires human review.

## Interfaces

### Required Public Commands

These commands are in scope for the next plan:

| Command | Role | Contract |
| --- | --- | --- |
| `./bin/ask repo doctor --json --robot` | First truth | Emits repo health, blockers, diagnostic debt, and one next command. |
| `./bin/ask repo surface --json --robot` | Diagnostic debt lane | Classifies repo surface findings when selected by doctor or closeout. |
| `./bin/ask skills improve "<goal>" --json --robot` | Goal routing | Recommends one primary capability route when possible. |
| `./bin/ask skills explain <handle> --json --robot` | Capability explanation | Shows canonical source, generated handle, runtime projection, limits, validation, and next command. |
| `./bin/ask skills prove <handle-or-goal> --json --robot` | Capability proof | Reports proof state using proof taxonomy semantics. |
| `./bin/ask repo closeout --changed --json --robot` | Completion readiness | Reports changed-file validation, generated sync needs, blockers, diagnostic debt, and readiness. |

### Candidate Commands Not Admitted

The legacy source spec mentions `repo onboard` and `repo next`. They are not
current acceptance requirements for this slice because command registration did
not show them as repo actions.

They may only enter a later plan if one of these is proven:

- the existing golden path cannot support first-contact onboarding without them;
- they replace more first-contact docs than they add;
- they are implemented as thin aliases or summaries over existing command
  outputs rather than a competing control plane.

### JSON Envelope Expectations

Machine-facing command output should preserve:

- top-level `status`;
- `trace_id`;
- `metadata.command`;
- `metadata.next_steps` when relevant;
- structured `data`;
- explicit `errors`.

Commands that emit `next_command` must not contradict `metadata.next_steps`.

## Agent-Native Compression Gates

Implementation must pass these gates before this issue can be considered ready
for `he-work`.

| Gate | Requirement | Blocking |
| --- | --- | --- |
| First-contact budget | README, AGENTS, and primary agent docs must point to one short command loop before advanced catalogs. | Yes |
| Agent catalog budget | Agent-facing command discovery must prioritize the golden path over broad command listings. | Yes |
| Standalone command admission | Any new public command or alias must prove it cannot be a subcommand, derived section, readiness packet, or advanced command. | Yes |
| Docs deletion budget | The plan must remove, collapse, or demote at least as much first-contact prose as it adds. | Yes |
| Fresh-agent eval | A new-session path must start from `repo doctor`, follow recommendations, and reach ready-or-blocked without opening docs for basic navigation. | Yes |
| Ablation proof | Each visible command family touched must answer whether hiding it from first-contact help would make task completion worse. | Yes |
| Evidence-backed metric | Closure must use generated command/eval evidence, not a manually maintained status matrix. | Yes |

## Invariants And Safety Requirements

- `./bin/ask` remains the public control-plane contract.
- `repo doctor` remains the first repo-health truth surface.
- `repo surface` remains classification-first and non-destructive.
- Generated command handles remain shallow pointers.
- Runtime projections remain generated outputs, not canonical source.
- `--json --robot` output remains the agent-facing contract where supported.
- Proof output must distinguish reachability, structural, quality, and outcome
  evidence.
- Closeout claims must be grounded in changed files and validation evidence.
- A new first-contact command is forbidden unless it reduces total first-contact
  ambiguity.
- Docs must point to live command truth rather than duplicate stale behavior.
- Diagnostic debt may be non-blocking, but it must not disappear from the
  command loop.

## Failure Model And Recovery

| Failure | Impact | Recovery |
| --- | --- | --- |
| `repo doctor` emits multiple equally ranked next actions | Agents must choose by inference. | Define deterministic priority ordering and expose ambiguity explicitly. |
| `repo surface` becomes a competing first command | First-contact ambiguity grows. | Keep surface as a doctor-selected diagnostic lane and advanced command. |
| `skills improve` returns an unranked buffet | Agents browse instead of route. | Require one primary recommendation unless ambiguity is real. |
| `skills prove` treats reachability as trust | Weakens proof-driven lifecycle semantics. | Map output to proof taxonomy and label missing proof honestly. |
| `repo closeout --changed` misses generated sync needs | Agents commit incomplete work. | Keep changed-file mapping and sync/reporting checks in closeout acceptance. |
| Docs add golden-path prose without removing old first-contact paths | The repo becomes more confusing despite better docs. | Apply docs deletion budget before closure. |
| New aliases duplicate namespace commands | Public command surface grows without leverage. | Require standalone command admission and ablation proof. |

## Observability

The spec requires observable proof, not just implementation presence.

Minimum evidence:

- `repo doctor` JSON snapshot before and after any behavior change.
- `repo doctor` next-command decision for at least:
  - clean usable repo;
  - repo surface diagnostic debt;
  - blocking catalog/runtime/sync failure if fixtures exist or can be simulated.
- `skills improve` examples for at least five representative goals.
- `skills explain` output for at least one generated handle and one canonical or
  plugin skill if supported.
- `skills prove` output showing proof level and limitations.
- `repo closeout --changed` output with representative changed canonical files.
- Docs/front-door diff showing first-contact prose was reduced, collapsed, or
  demoted.
- Fresh-agent eval transcript or deterministic script starting from
  `repo doctor`.

## Acceptance Matrix

| ID | Acceptance Criteria | Verification |
| --- | --- | --- |
| SA1 | The HE spec artifact exists under `.harness/specs/**`, carries artifact identity frontmatter, and links `JSC-246` to the approved Linear plan and selected refactor. | `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` |
| SA2 | Linear traceability is complete for issue, project, milestone, priority, labels, route, and delta-gate scope. | `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` |
| SA3 | `repo doctor` remains the first truth command and emits blocking status, diagnostic debt, and one deterministic next command in `--json --robot` mode. | `./bin/ask repo doctor --json --robot` plus focused tests for next-command priority. |
| SA4 | `repo doctor` next-action ordering is documented and tested for repo unreadable, projection sync, catalog parity, runtime budget, command-handle, repo surface, and healthy states where fixtures or helper tests are available. | Focused golden-path signal tests or documented blocked fixture gaps. |
| SA5 | `repo surface` remains reachable as a non-destructive classification-first diagnostic lane and is selected by `repo doctor` when repo surface debt is the highest-signal next action. | `./bin/ask repo surface --json --robot`; doctor fixture or live output showing surface next command. |
| SA6 | Non-blocking diagnostic debt does not create an endless diagnostic loop; a fresh agent can continue from surfaced debt into route, explain, prove, or closeout. | Fresh-agent eval showing repo surface acknowledgement/capture followed by task continuation without doc archaeology. |
| SA7 | `skills improve` distinguishes `resolved`, `resolved_with_fallback`, `blocked_ambiguity`, and `blocked_reachability` states without hiding unresolved goal decisions behind success prose. | Goal fixture set with at least five representative goals; assert primary route, fallback metadata, or explicit ambiguity. |
| SA8 | Routing fixtures are grounded in a live capability registry snapshot and separate route-family expectations from exact-handle expectations. | `./bin/ask skills resolve <handle> --json --robot` for every exact expected handle, or documented route-family-only assertion. |
| SA9 | `skills explain` distinguishes generated command handle, canonical source, runtime projection, runtime visibility, limitations, validation command, and next proof command. | `./bin/ask skills explain he-spec --json --robot` and at least one additional representative handle if available. |
| SA10 | `skills prove` maps existing output to the accepted proof taxonomy without introducing new proof schema, promotion gates, or trusted/default-visible lifecycle state in this slice. | `./bin/ask skills prove <handle> --json --robot`; proof-level assertions against the ADR; plan scope check for no proof schema expansion. |
| SA11 | `repo closeout --changed` reports changed-file readiness, generated sync needs, focused validation, blocker state, diagnostic debt, and commit readiness in both blocked and clean/validation-ready scenarios. | Controlled changed-file fixture, temporary branch, or helper-level test plus live `./bin/ask repo closeout --changed --json --robot` evidence. |
| SA12 | Primary first-contact docs expose the golden path before broad catalogs and do not present multiple competing first commands. | README/AGENTS/docs lint or focused grep plus human review of first-contact sections. |
| SA13 | The implementation removes, collapses, or demotes at least as much first-contact prose as it adds and proves improved behavior through a fresh-agent metric. | Docs diff review plus fresh-agent metric such as commands-to-ready, docs-opened count, or misroute count. |
| SA14 | Any new public command or alias passes standalone command admission and ablation proof. | Plan/review artifact documents why an existing subcommand or derived output is insufficient. |
| SA15 | A fresh-agent eval starts from `repo doctor`, follows command output, and reaches ready-or-blocked without reading docs for basic navigation. | `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` includes transcript or deterministic command script. |
| SA16 | Neighboring Linear issues `JSC-230`, `JSC-167`, and `JSC-169` are not implemented in this slice unless a later delta gate admits them. | Plan scope check and final diff review. |
| SA17 | Product language frames Agent Skills Kit as an agent capability control plane, but does not add branding prose without executable command support. | README/docs diff plus command-evidence references. |
| SA18 | Closure evidence records exact pass/fail/blocked commands and does not close the parent issue without the eval artifact. | `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` exists and references exact commands. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Scope |
| --- | --- | --- |
| `JSC-246` | SA1, SA2 | Spec artifact identity and Linear traceability. |
| `JSC-246` | SA3, SA4, SA5, SA6 | Repo truth, deterministic next-action ordering, repo surface diagnostic lane, and continuation after diagnostic debt. |
| `JSC-246` | SA7, SA8, SA9, SA10 | Capability route, fixture grounding, explanation, and proof loop. |
| `JSC-246` | SA11 | Closeout as completion-readiness gate. |
| `JSC-246` | SA12, SA13, SA14, SA15 | Agent-native compression and fresh-agent proof. |
| `JSC-246` | SA16, SA17, SA18 | Scope control, product framing, and eval-backed closure. |

Legacy Linear issue acceptance from `JSC-246` maps as follows:

| Legacy Acceptance | Current Spec Handling |
| --- | --- |
| SA1-SA5 repo surface policy/inventory | Preserved through `repo surface` diagnostic lane; implementation may harden behavior only where needed to support golden-path evidence. |
| SA6-SA8 cleanup/deferred context | Deferred; cleanup is not admitted into this slice. |
| SA9 doctor | Admitted and blocking. |
| SA10 onboard | Not admitted as a new command; first-contact behavior must be proven through `repo doctor` unless ablation proves `onboard` is necessary. |
| SA11 improve | Admitted and blocking. |
| SA12 explain | Admitted and blocking. |
| SA13 closeout | Admitted and blocking. |
| SA14 runtime surface reporting | Admitted through doctor and closeout evidence. |
| SA15 control-plane framing | Admitted only where backed by executable command support. |

## Planning-Ready First Slice

The first `he-plan` unit should be:

```text
Make the existing agent-first command loop plan-ready and compression-tested:
repo doctor selects the next action, repo surface remains the diagnostic lane,
skills improve/explain/prove form the capability route, and repo closeout
proves completion readiness from changed files.
```

The first implementation plan should start with behavior characterization before
editing command logic:

1. Snapshot current `repo doctor`, `repo surface`, `skills improve`,
   `skills explain`, `skills prove`, and `repo closeout --changed` output.
2. Define the deterministic next-action ordering.
3. Add or tighten tests around the current loop.
4. Only then adjust command behavior or docs.
5. Apply docs deletion budget after command behavior is stable.
6. Prove a fresh-agent path from `repo doctor` to ready-or-blocked.

## Open Questions

- Does `repo doctor` need an explicit `--next` flag, or is the existing
  `next_command` field sufficient when backed by tests?
- Should `repo surface` diagnostic debt remain non-blocking by default for
  closeout, or should strict mode become required for release-sensitive work?
- Which five representative `skills improve` goals should become golden
  fixtures?
- What is the minimum `skills prove` proof-level schema that preserves the ADR
  without overbuilding the proof system?
- Should any first-contact README sections be generated from command metadata,
  or is validated prose sufficient for this slice?

## Definition Of Done

- Spec identity and Linear traceability lints pass.
- `he-plan` can derive a bounded implementation plan from this spec without
  reading the legacy source spec as the execution contract.
- The plan preserves one admitted parent issue: `JSC-246`.
- The plan does not implement `JSC-230`, `JSC-167`, or `JSC-169`.
- The plan includes compression gates before docs or command-surface expansion.
- The eventual eval artifact exists at:
  `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`.
- Closure evidence records exact commands, outcomes, and blockers.

## Handoff To he-plan

Use this artifact as the source contract for `$he-plan`.

Required planning constraints:

- Start with live behavior characterization.
- Keep `repo doctor` first.
- Preserve `repo surface` as diagnostic lane, not first-contact replacement.
- Treat `skills improve`, `skills explain`, `skills prove`, and
  `repo closeout --changed` as the loop.
- Sequence subtractive and compression work before additive docs or aliases.
- Require fresh-agent eval and ablation proof before closure.
- Keep the active set small: one parent issue, no speculative sub-issue
  explosion.

Suggested eval artifact:

```text
.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
```

## Blackboard Delta

```yaml
schema_version: he-blackboard-delta/v1
topic: agent-first-golden-path
finding:
  selected_linear_issue: JSC-246
  prior_slice: JSC-284
  prior_slice_status: complete
  next_stage: he-plan
  golden_path:
    - ./bin/ask repo doctor --json --robot
    - ./bin/ask skills improve "<goal>" --json --robot
    - ./bin/ask skills explain <handle> --json --robot
    - ./bin/ask skills prove <handle-or-goal> --json --robot
    - ./bin/ask repo closeout --changed --json --robot
  diagnostic_lane:
    - ./bin/ask repo surface --json --robot
  non_negotiable_rule: agents should only need the golden path and command-emitted next actions for basic operation
  required_gates:
    - first_contact_budget
    - agent_catalog_budget
    - standalone_command_admission
    - docs_deletion_budget
    - fresh_agent_eval
    - ablation_proof
    - evidence_backed_metric
```
