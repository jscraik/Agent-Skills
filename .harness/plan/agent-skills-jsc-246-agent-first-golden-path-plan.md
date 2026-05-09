---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-plan
artifact_type: he-plan
type: he-plan
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Plan
harness_stage: he-plan
status: active
date: 2026-05-09
origin: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
risk: medium-high
depth: bounded-execution-slice
traceability_required: true
linear_status: existing
linear_refresh_status: resolved_live_fetch_done
linear_delta_status: pass_via_spec_and_live_issue_fetch
spec_live_baseline_status: runtime_budget_pass_with_unrelated_sync_required
linear_issue: JSC-246
linear_issue_url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_project_id: 791c2f12-5ffb-4644-8421-f4216ac6d805
linear_parent_initiative: Dev Portfolio
linear_milestone: Command surface and ask reliability
he_slice: Agent First Golden Path
linear_parent_issue_title: "Build repo surface contract and agent capability control-plane golden paths"
linear_labels: "Roadmap: Next, Agent, Infra, Improvement"
linear_label_status: resolved_with_existing_labels
linear_priority: 2
selected_refactor: .harness/refactors/agent-first-golden-path.md
source_spec: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
eval_artifact: .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
technical_review: .harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md
plan_technical_review: .harness/review/agent-skills-jsc-246-agent-first-golden-path-plan-technical-review.md
---

# Agent Skills JSC-246 Agent First Golden Path Plan

## Mode Decision

This is the durable `he-plan` artifact for the approved current slice only.

Selected slice:

- Linear issue: `JSC-246`
- Linear project: `agent-skills`
- Linear project ID: `791c2f12-5ffb-4644-8421-f4216ac6d805`
- Linear milestone: `Command surface and ask reliability`
- HE slice: `Agent First Golden Path`
- Source spec:
  `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
- Technical review:
  `.harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md`
- Selected refactor: `.harness/refactors/agent-first-golden-path.md`
- Eval artifact:
  `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`

This plan is not a broad command-surface cleanup plan. It implements the
smallest bounded path that makes this loop deterministic, compression-tested,
and closeout-ready:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo surface --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle-or-goal> --json --robot
./bin/ask repo closeout --changed --json --robot
```

`repo surface` remains a doctor-selected diagnostic lane, not a competing first
command.

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-246` |
| URL | https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Project ID | `791c2f12-5ffb-4644-8421-f4216ac6d805` |
| Milestone | `Command surface and ask reliability` |
| HE slice | `Agent First Golden Path` |
| Parent initiative | `Dev Portfolio` |
| Priority | `2` |
| Status at plan time | `Todo` |
| Labels | `Roadmap: Next`, `Agent`, `Infra`, `Improvement` |
| Execution route | Agent-assisted; human review required for public command output contracts |
| Blocked by | None known |
| Blocks | Later commandable skill-tree work, proof promotion enforcement, and broader docs cleanup should wait for this control-plane path |

## Linear Delta Capture

Captured: `2026-05-09`

Refreshed: `2026-05-09`

Live Linear fetch for `JSC-246` was performed during this planning pass. The
Linear research tool was unavailable, but direct issue fetch succeeded. No
Linear objects were created or updated.

| Object | Live state | Classification | Plan handling |
| --- | --- | --- | --- |
| `JSC-246` | Existing issue, `Todo`, priority `High`, project `agent-skills`, milestone `Command surface and ask reliability`, labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement` | `approved_current_slice` | Use as the only implementation parent for this plan. |
| `JSC-230` | Mentioned by source artifacts as neighboring commandable skill-tree work | `not_admitted` | Do not implement in this slice. |
| `JSC-167` | Mentioned by source artifacts as neighboring work | `not_admitted` | Do not implement in this slice. |
| `JSC-169` | Mentioned by source artifacts as neighboring work | `not_admitted` | Do not implement in this slice. |

No new Linear initiative, project, milestone, label, parent issue, or child
issue is required before implementation. If execution needs child issues, create
at most the phase-level children listed under "Linear Execution Shape"; do not
explode acceptance criteria into individual tickets.

## Source Evidence

Hard evidence:

- `./bin/ask skills resolve he-plan --json` resolved to
  `Plugins/harness-engineering/skills/he-plan/SKILL.md` with source revision
  `9105a11e1` and source SHA
  `22e715da20cfd56d7ccfa29029143b130f69580f6953eb3c9ef1cb957af8e9f1`.
- Direct Linear fetch for `JSC-246` confirmed the live issue, project,
  milestone, priority, labels, assignee, branch name, updated timestamp, and
  Todo status. Linear research remained unavailable with `Tool research not
  found`, so child/blocker graph refresh beyond the issue payload is not part
  of this plan artifact.
- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
  defines acceptance IDs `SA1` through `SA20`.
- `.harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md`
  approves handoff to `he-plan` with residual risks.
- The refreshed spec's technical review focus requires runtime-budget blocker
  removal from active scope, diagnostic debt containment, sync-readiness
  isolation, no new command/proof expansion, docs compression, measured
  fresh-agent proof, and dirty-worktree evidence isolation.
- `.harness/refactors/agent-first-golden-path.md` identifies the golden path as
  the repo's agent capability control-plane spine.
- `Infrastructure/scripts/lib/ask/golden_path.py` already selects blocker,
  diagnostic, and normal next commands.
- `Infrastructure/tests/test_ask_repo_doctor.py` already has focused fixtures
  for doctor next-action ordering and closeout states.
- `Infrastructure/tests/test_ask_skills_goal.py` already tests resolved,
  fallback, unresolved, and catalog-blocked `skills improve` paths.
- `Infrastructure/tests/test_ask_cli.py` already checks JSON contracts for
  `repo doctor`, `repo closeout`, `skills improve`, and `skills prove`.
- `./bin/ask repo doctor --json --robot` currently passes with non-blocking
  repo-surface diagnostic debt and selects
  `./bin/ask repo surface --json --robot` as a diagnostic advisory.
- `./bin/ask runtime budget --json --robot` currently passes with no unresolved
  scope collisions; `agents-sdk`, `build-chatgpt-app`, and
  `chatgpt-app-submission` are baselined.
- `./bin/ask repo closeout --changed --json --robot` currently reports
  `sync_required` because unrelated dirty harness-engineering skill files are
  present in the worktree. Runtime budget still passes, and repo-surface debt
  remains non-blocking diagnostic debt.

Interpretation:

- The safest implementation path is fixture/test-first hardening around
  existing code, not a new command family.
- `repo doctor` already has most of the signal composition this slice needs,
  but the output needs clearer agent-facing continuation semantics when
  diagnostic debt is non-blocking.
- `skills improve` already distinguishes fallback in some cases, but the
  status vocabulary must become explicit enough for agents to act safely.
- Documentation changes should be last, after command behavior is stable.

Assumptions:

- Existing tests can be extended without large harness rewrites.
- Additive JSON fields are acceptable when existing fields remain stable.
- Current live closeout output is valid blocker evidence for the whole dirty
  worktree, not clean JSC-246 readiness evidence. Implementation must isolate
  clean closeout fixtures from unrelated generated/projection churn.

## Scope Boundary

### In Scope

- `Infrastructure/scripts/lib/ask/golden_path.py`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lib/ask/command_metadata.py`, only where help or
  examples affect first-contact command visibility
- `Infrastructure/tests/test_ask_golden_path.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `Infrastructure/tests/test_ask_skills_goal.py`
- `Infrastructure/tests/test_ask_cli.py`
- `Infrastructure/tests/test_ask_repo_surface.py`, only if surface output needs
  diagnostic continuation assertions
- `README.md`
- `AGENTS.md`
- `Docs/agents/16-agent-operating-contract.md`
- `Docs/agents/5-minute-success-path.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`

### Out Of Scope

- New proof schema, promotion gate, trusted/default-visible lifecycle state, or
  command-handle proof artifact.
- `JSC-230`, `JSC-167`, and `JSC-169` unless a later Linear Delta Capture Gate
  admits them.
- New `repo onboard`, `repo next`, or other top-level first-contact command
  unless ablation proves the existing command loop cannot carry the workflow.
- Cleanup of `artifacts/**`, `Infrastructure/artifacts/**`, `.skillsets/**`,
  `.harness/*.db`, `skills-system/**`, or `Plugins/cache/**`.
- Manual edits to generated/runtime projections except through canonical sync
  lanes if implementation changes require regeneration.
- Unrelated skill content rewrites.

## Design Decision: Diagnostic Continuation Representation

Use the smallest additive JSON contract:

```yaml
next_command: <existing command string>
next_command_kind: blocking_repair | diagnostic_advisory | normal_inspection | no_safe_command
next_command_blocks_task: true | false
```

Rules:

- `blocking_repair`: selected from a blocker; `next_command_blocks_task: true`.
- `diagnostic_advisory`: selected from non-blocking diagnostic debt;
  `next_command_blocks_task: false`.
- `normal_inspection`: selected when the repo is usable and has no actionable
  warning; `next_command_blocks_task: false`.
- `no_safe_command`: selected only when the winning blocker or actionable
  warning lacks a safe recovery command; this is itself a blocking contract
  failure unless the eval records why no safe command exists.

Tie-breaker rules:

- If multiple signals exist inside the same priority class, choose one primary
  `next_command` by stable signal id order.
- Preserve non-selected same-class signals in `blockers`, `diagnostic_debt`,
  `signals`, or an equivalent secondary array.
- Blocking signals outrank advisory signals even when an advisory has a larger
  count.
- Repo-surface `blocking_findings` is a repo-surface classification count, not a
  global closeout blocker unless `repo doctor` reports `blocking: true` or
  closeout includes a matching id in `commit_readiness.blockers`.

Do not remove or rename existing `next_command`, `blocking`, `blockers`,
`diagnostic_debt`, or `signals` fields. This keeps robot consumers compatible
while giving future agents enough information to avoid looping on advisory
surface debt.

Compatibility requirements:

- Add fields to the existing golden-path payload returned under
  `data.doctor`.
- Preserve the current top-level duplication created by
  `result.data.update(payload)` in `repo_doctor`; if `data.doctor` receives a
  new field, the top-level `data.<field>` mirror must remain consistent.
- Do not change `metadata.command`, `metadata.next_steps`, `status`, or error
  envelope semantics except to prevent contradiction with the selected
  `next_command`.
- If `metadata.next_steps` is populated with a command-bearing next step and it
  disagrees with `data.doctor.next_command`, that is a release blocker. Empty
  `metadata.next_steps` is allowed when `data.doctor.next_command` is the
  authoritative robot continuation.
- A selected blocker or actionable warning must not silently yield a null
  recovery path. It must either expose a concrete `next_command` or be
  classified as `next_command_kind: no_safe_command` with
  `next_command_blocks_task: true`.
- Human output may stay compact, but it must not imply advisory diagnostic debt
  is blocking when `next_command_blocks_task` is false.

## Design Decision: Validation Routing

Repo wrappers are the canonical closeout authority. Direct `pytest` commands are
allowed as focused fixture evidence because the existing tests are Python unit
tests, but they are not sufficient for final closure.

Rules:

- Use direct focused tests to prove local helper behavior.
- Use `./bin/ask repo validate --changed-files <paths> --json --robot` as the
  repo-native changed-file validation gate when implementation files are known.
- Use `./bin/ask repo doctor --json --robot` and
  `./bin/ask repo closeout --changed --json --robot` as the final readiness
  gates.
- If wrapper validation is blocked by unrelated worktree state, record exact
  blocker evidence and keep `JSC-246` open unless focused tests plus live
  command evidence prove the slice and the blocker is explicitly out of scope.
- Any eval artifact with `traceability_required: true` must pass both artifact
  identity lint and Linear traceability lint before closure.

## Design Decision: Skills Improve Route State Compatibility

`skills improve` must expose the spec's route-state vocabulary without breaking
existing consumers that read `improvement.status`.

Use additive fields:

```yaml
status: resolved | resolved_with_fallback | blocked
route_state: resolved | resolved_with_fallback | blocked_ambiguity | blocked_reachability | blocked_dependency
route_state_reason: <short stable reason>
```

Rules:

- Preserve existing `status: resolved` for clean recommendations.
- Preserve existing `status: resolved_with_fallback` for fallback
  recommendations.
- Preserve existing `status: blocked` for unresolved or dependency-blocked
  cases.
- Use `route_state` to distinguish blocked ambiguity, blocked reachability, and
  dependency blockers.
- Do not let fallback run when the underlying route decision is blocked by
  catalog parity, projection sync, runtime budget, command-handle failure, or
  other dependency failure.
- If a future implementation wants to replace `status` with richer values, that
  is a separate compatibility migration and is not admitted into `JSC-246`.

## Proof Command Boundary

The golden path uses:

```bash
./bin/ask skills prove <handle-or-goal> --json --robot
```

Current output still exposes the lower-level command-handle reachability check
as `./bin/ask skills proof <handle> --json --robot` in `skills explain` and
`skills improve` next-command fields. Existing tests assert that behavior. This
slice may improve the scorecard path, but it must not silently break the
compatibility contract.

Rules:

- `skills explain <handle>` may keep `next_command:
  ./bin/ask skills proof <handle> --json --robot` until an explicit
  compatibility migration updates tests and consumers.
- Reachability detail may retain `proof_command: ./bin/ask skills proof ...`
  as a low-level check.
- `skills prove <handle-or-goal>` remains the golden-path proof scorecard
  command and must be used for proof taxonomy validation.
- Do not collapse `skills proof` and `skills prove`, rename either command, or
  add a new proof schema in this slice.
- If future work wants `skills explain` to emit `skills prove` as the primary
  `next_command`, route that as a compatibility migration with focused tests
  rather than sneaking it into this slice.

## Implementation Units

### PLAN-JSC246-001: Baseline Snapshot And Fixture Map

Objective:

Capture current command output and identify which acceptance cases already have
focused tests before changing behavior.

Acceptance IDs:

- SA1, SA2, SA3, SA5, SA8, SA11, SA16, SA19, SA20

Affected systems:

- `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`
- Existing focused test inventory

Implementation notes:

- Snapshot current output for:
  - `./bin/ask repo doctor --json --robot`
  - `./bin/ask repo surface --json --robot`
  - `./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot`
  - `./bin/ask skills explain he-spec --json --robot`
  - `./bin/ask skills prove he-spec --json --robot`
  - `./bin/ask repo closeout --changed --json --robot`
- For every snapshot, record:
  - top-level `status`;
  - `metadata.command`;
  - `metadata.next_steps`;
  - primary `next_command` field when present;
  - whether the command is a blocker, advisory diagnostic, or normal
    continuation.
- Resolve exact handles before using them as route fixtures:
  - `./bin/ask skills resolve autofix --json --robot`
  - `./bin/ask skills resolve he-spec --json --robot`
  - `./bin/ask skills resolve he-heartbeat --json --robot`
  - `./bin/ask skills resolve he-code-review --json --robot`
  - `./bin/ask skills resolve he-fix-bugs --json --robot`
- Record current closeout dirty-worktree behavior as a live blocked case owned
  by unrelated skill/projection work.
- Do not treat current worktree state as a clean JSC-246 closeout fixture.
- Record current runtime-budget pass as resolved/baselined evidence, not an
  active implementation blocker.
- Confirm the technical-review focus checklist from the spec is represented in
  this plan before handing to `he-work`.

Expected risk:

- Low.

Can run in parallel:

- Yes, with docs inspection only.

Validation requirements:

- Snapshot commands above produce JSON or an explicitly recorded blocker.
- Eval artifact exists and separates baseline facts from implementation
  conclusions.

Rollback conditions:

- None for code; revert only the eval artifact if it records incorrect command
  output.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Capture agent-first golden path baseline`

Agent-safe:

- Yes.

Human review required:

- No, unless baseline contradicts the spec.

### PLAN-JSC246-002: Doctor Next-Action Contract

Objective:

Make `repo doctor` next-action output explicit enough for agents to distinguish
blocking repair from non-blocking diagnostic advice.

Acceptance IDs:

- SA3, SA4, SA5, SA6

Affected systems:

- `Infrastructure/scripts/lib/ask/golden_path.py`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/tests/test_ask_golden_path.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`

Implementation notes:

- Add additive `next_command_kind` and `next_command_blocks_task` fields to the
  golden-path payload.
- Preserve the existing `next_command` field exactly.
- Preserve the duplicate payload contract for `data.doctor` and top-level
  `data` mirrors.
- Add tests that fail if `metadata.next_steps` contradicts
  `data.doctor.next_command` when both contain command-bearing guidance.
- Add tests that fail if a selected blocker or actionable warning produces no
  concrete recovery command without explicit `no_safe_command` classification.
- Extend golden-path unit tests for:
  - blocker wins over warning;
  - same-priority conflicts choose the same primary command by stable signal id
    order across repeated runs;
  - non-selected same-priority signals remain visible in a secondary structured
    field;
  - diagnostic warning selects `diagnostic_advisory`;
  - all-pass state selects `normal_inspection`;
  - missing blocker recovery is classified instead of silently producing
    ambiguous output;
  - advisory diagnostic debt does not mark `blocking` true;
  - repo-surface `blocking_findings` does not become a global closeout blocker
    unless doctor/closeout emits a real blocker id.
- Extend repo doctor tests for the existing priority order:
  - repo unreadable / not git;
  - projection sync;
  - catalog parity;
  - runtime budget;
  - command handles;
  - repo surface diagnostic debt;
  - healthy repo.
- Keep `repo surface` non-destructive and doctor-selected.

Expected risk:

- Medium. This touches agent-facing JSON output, but only additively.

Can run in parallel:

- No. This should land before docs compression and fresh-agent eval.

Validation requirements:

- `python3 -m pytest Infrastructure/tests/test_ask_golden_path.py Infrastructure/tests/test_ask_repo_doctor.py`
- `./bin/ask repo doctor --json --robot`
- `./bin/ask repo surface --json --robot`
- Re-run `./bin/ask runtime budget --json --robot` only as a regression check;
  this phase must not re-open resolved runtime-budget collision work unless the
  command fails live.

Rollback conditions:

- Roll back additive fields if existing `next_command` behavior changes for
  current passing tests or robot JSON consumers break.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Add doctor diagnostic continuation contract`

Agent-safe:

- Agent-assisted.

Human review required:

- Yes, because this changes public robot output.

### PLAN-JSC246-003: Skills Improve Route-State Contract

Objective:

Make `skills improve` expose safe route states instead of hiding ambiguity or
fallback routing behind a generic success/block result.

Acceptance IDs:

- SA7, SA8

Affected systems:

- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/tests/test_ask_skills_goal.py`
- `Infrastructure/tests/test_ask_cli.py`

Implementation notes:

- Preserve existing `resolved` and `resolved_with_fallback` behavior.
- Preserve existing `status: blocked` for unresolved ambiguity and add
  `route_state: blocked_ambiguity` when the route failure class is ambiguity
  or intent unresolved.
- Add `route_state: blocked_reachability` when a route exists but proof fails.
- Add `route_state: blocked_dependency` for catalog parity, projection sync,
  runtime budget, command-handle, or other dependency blockers.
- Preserve catalog parity / infrastructure blockers as blocking repair states;
  do not let fallback bypass catalog parity.
- Ensure fallback output always includes:
  - `status: resolved_with_fallback`
  - `route_state: resolved_with_fallback`
  - `goal_decision_status`
  - confidence
  - rationale
  - reachable proof summary
  - concrete `next_command`
- Add or extend route fixtures for these goals:
  - `make agents better at fixing PR review comments`
  - `write a Linear-backed HE spec`
  - `monitor a long-running HE work phase`
  - `review this implementation against the spec`
  - `fix validation blockers after review`
- For exact handle assertions, first prove the handle exists with
  `./bin/ask skills resolve <handle> --json --robot`.
- Assert route family and status class before exact handle where ownership
  metadata is not stable enough.

Expected risk:

- Medium-high. Route wording and status changes affect agents directly.

Can run in parallel:

- No, because route-state vocabulary is a central behavioral contract.

Validation requirements:

- `python3 -m pytest Infrastructure/tests/test_ask_skills_goal.py`
- `python3 -m pytest Infrastructure/tests/test_ask_cli.py -k "skills_improve or skills_goal"`
- Live representative `./bin/ask skills improve ... --json --robot` commands
  recorded in the eval artifact.

Rollback conditions:

- Roll back if exact-route success decreases, fallback confidence disappears,
  or catalog parity blockers can be bypassed through fallback routing.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Make skills improve route states deterministic`

Agent-safe:

- Agent-assisted.

Human review required:

- Yes for route-ranking and ambiguity behavior.

### PLAN-JSC246-004: Explain And Prove Taxonomy Assertions

Objective:

Align `skills explain` and `skills prove` with the golden path using existing
output semantics, without adding proof schemas or promotion states.

Acceptance IDs:

- SA9, SA10, SA16

Affected systems:

- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/tests/test_ask_cli.py`
- Optional focused tests under `Infrastructure/tests/test_ask_skills_goal.py`
  if proof routing helper coverage is needed

Implementation notes:

- Add tests that `skills explain` exposes:
  - generated command handle;
  - canonical source;
  - runtime projection / runtime visibility;
  - limitations or ambiguity where available;
  - validation command;
  - current compatibility next command, which may remain
    `./bin/ask skills proof <handle> --json --robot` unless this phase
    explicitly updates tests and consumers.
- Test at least `he-spec` and one non-HE or plugin-backed representative
  handle if live resolution supports it.
- Add assertions mapping existing `skills prove` output to:
  - reachability;
  - structural;
  - quality;
  - outcome.
- Preserve `skills proof` as the existing reachability command in current
  explain/improve output unless an explicit compatibility migration is accepted.
- Use `skills prove` for the golden-path scorecard eval.
- Do not introduce:
  - new proof schema;
  - trusted/default-visible lifecycle state;
  - promotion gate;
  - command-handle proof artifact.
- If current output cannot support a taxonomy assertion without schema changes,
  record that gap in the eval artifact and leave the schema change for a later
  Linear slice.

Expected risk:

- Medium. Tests may reveal gaps that should not be fixed in this slice.

Can run in parallel:

- Yes, after PLAN-JSC246-003 route-state vocabulary is stable.

Validation requirements:

- `python3 -m pytest Infrastructure/tests/test_ask_cli.py -k "skills_prove or explain"`
- `./bin/ask skills explain he-spec --json --robot`
- `./bin/ask skills prove he-spec --json --robot`
- Optional compatibility evidence:
  `./bin/ask skills proof he-spec --json --robot` may be recorded only to
  demonstrate low-level reachability, not as the golden-path next action.

Rollback conditions:

- Stop and route back to Linear if implementation requires a new proof schema
  or lifecycle promotion model.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Assert explain and prove golden path semantics`

Agent-safe:

- Agent-assisted.

Human review required:

- Yes for proof semantics.

### PLAN-JSC246-005: Closeout Isolation Fixtures

Objective:

Prove `repo closeout --changed` as the completion-readiness gate without using
the current dirty worktree as the clean fixture.

Acceptance IDs:

- SA11, SA18

Affected systems:

- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`
- `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`

Implementation notes:

- Use helper-level fixtures or mocked changed-file sets for:
  - skill source change requiring sync;
  - non-skill implementation change requiring scoped validation;
  - no changed files / ready state;
  - strict diagnostic debt case.
- Keep live `./bin/ask repo closeout --changed --json --robot` evidence as
  current-state evidence only: blocked when it reports blockers, ready when it
  reports readiness.
- Use helper-level fixtures, an isolated branch, or an explicitly controlled
  changed-file scenario for clean/validation-ready and blocked `sync_required`
  cases.
- Ensure closeout output includes:
  - changed files;
  - sync needs;
  - focused validation;
  - surface policy;
  - commit readiness;
  - blocker state;
  - next command.

Expected risk:

- Medium.

Can run in parallel:

- Yes, after PLAN-JSC246-002 defines advisory diagnostic semantics.

Validation requirements:

- `python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py`
- `./bin/ask repo closeout --changed --json --robot` recorded as live evidence
  with blocker classification if unrelated changes remain.

Rollback conditions:

- Roll back if closeout produces false readiness, hides sync requirements, or
  blocks unrelated non-skill edits incorrectly.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Prove closeout changed-file readiness fixtures`

Agent-safe:

- Agent-assisted.

Human review required:

- Yes for commit-readiness semantics.

### PLAN-JSC246-006: First-Contact Compression

Objective:

Move first-contact docs and command metadata toward the golden path only after
the command behavior is stable.

Acceptance IDs:

- SA12, SA13, SA14, SA17

Affected systems:

- `README.md`
- `AGENTS.md`
- `Docs/agents/16-agent-operating-contract.md`
- `Docs/agents/5-minute-success-path.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `Infrastructure/scripts/lib/ask/command_metadata.py`

Implementation notes:

- Inspect the docs listed above and classify touched first-contact sections as:
  `keep`, `collapse`, `demote`, `generate`, or `delete`.
- Do not edit every inspected doc by default.
- Prefer the smallest docs diff that makes the first action obvious:
  `./bin/ask repo doctor --json --robot`.
- Demote broad catalogs and non-admitted command names (`repo onboard`,
  `repo next`) unless an ablation note proves they are necessary.
- Do not add more first-contact prose than is removed, collapsed, or demoted.
- Keep public framing executable: "agent capability control plane" is allowed
  only when adjacent text points at live command behavior.
- The docs compression proof must carry the fresh-agent metric thresholds from
  the spec: zero docs opened before the first command, first command is
  `repo doctor`, zero admitted-family misroutes, and ready/validation-ready/
  explicitly-blocked state within five command decisions after `repo doctor`.

Expected risk:

- Low-medium.

Can run in parallel:

- No. Run after command behavior changes are stable.

Validation requirements:

- `git diff --check -- README.md AGENTS.md Docs/agents/16-agent-operating-contract.md Docs/agents/5-minute-success-path.md Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md Infrastructure/scripts/lib/ask/command_metadata.py`
- Focused grep or review evidence showing default first-contact sections point
  to the golden path before advanced catalogs.
- Eval artifact records line/section additions versus deletions/demotions and
  behavior metrics from PLAN-JSC246-007.

Rollback conditions:

- Roll back docs if they become longer without reducing first-contact
  ambiguity, or if they mention command behavior not supported by live output.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Compress first-contact docs around repo doctor`

Agent-safe:

- Yes, with review.

Human review required:

- Yes if public product framing changes materially.

### PLAN-JSC246-007: Fresh-Agent Eval And Closure Gate

Objective:

Prove the implemented golden path with generated evidence before closing the
parent issue.

Acceptance IDs:

- SA6, SA13, SA15, SA18

Affected systems:

- `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`
- Command snapshots from all in-scope commands
- Final closeout evidence

Implementation notes:

- Write the eval artifact with:
  - baseline command snapshots;
  - after-change command snapshots;
  - route fixture outcomes;
  - closeout fixture outcomes;
  - docs compression evidence;
  - fresh-agent transcript or deterministic script.
- Fresh-agent path must start with:
  `./bin/ask repo doctor --json --robot`.
- The path must show that when doctor emits non-blocking diagnostic debt:
  - the agent can run or acknowledge `repo surface`;
  - the debt is recorded as advisory;
  - the agent continues to `skills improve`, `skills explain`, `skills prove`,
    or `repo closeout` without opening docs for basic navigation.
- The eval must contain command output excerpts or JSON field summaries from
  actual command runs. A prose-only transcript is not sufficient.
- Fresh-agent proof must be isolated from the planning thread. Use a new agent
  session, a deterministic script, or an explicitly clean transcript that starts
  with no prior access to this spec/plan. Evidence produced in the same
  planning thread is coordination evidence, not fresh-agent proof.
- If a command cannot run, the eval must mark it `blocked` with exact stderr,
  exit code, or tool blocker evidence.
- Record metrics:
  - commands to ready-or-blocked;
  - docs opened for basic navigation;
  - route ambiguity count;
  - whether `next_command` was followed without manual repo browsing.
- Required thresholds:
  - docs opened before first command: `0`;
  - first command: `./bin/ask repo doctor --json --robot`;
  - misroute count for admitted golden-path command family: `0`;
  - command decisions after `repo doctor` before ready, validation-ready, or
    explicitly-blocked state: `<= 5`;
  - each threshold miss is an eval failure unless exact repo-state blocker
    evidence explains why the metric could not be satisfied.

Expected risk:

- Medium.

Can run in parallel:

- No. This is the closure gate.

Validation requirements:

- Eval artifact identity lint.
- Eval artifact Linear traceability lint if `traceability_required: true`.
- All focused tests from prior phases.
- `./bin/ask repo doctor --json --robot`
- `./bin/ask repo surface --json --robot`
- Representative `./bin/ask skills improve ... --json --robot`
- `./bin/ask skills explain he-spec --json --robot`
- `./bin/ask skills prove he-spec --json --robot`
- `./bin/ask repo closeout --changed --json --robot`
- `./bin/ask repo validate --changed-files <changed files> --json --robot`
  where closeout recommends scoped validation.

Rollback conditions:

- Do not close `JSC-246` if the eval artifact is missing, command output
  contradicts the plan, or fresh-agent evidence still requires docs archaeology
  for basic navigation.

Linear mapping:

- Parent issue: `JSC-246`
- Suggested child title: `[agent-skills] Record fresh-agent golden path eval`

Agent-safe:

- Agent-assisted.

Human review required:

- Yes before closing Linear.

## Linear Execution Shape

Recommended active set: one parent plus at most three active phase children at
any time.

Create child issues only if implementation will span multiple sessions. If the
work stays in one continuous HE work run, track phases in this plan and the eval
artifact instead of creating Linear noise.

Suggested child issues:

| Title | Phase coverage | Priority | Labels | Execution route |
| --- | --- | --- | --- | --- |
| `[agent-skills] Add doctor diagnostic continuation contract` | PLAN-JSC246-001, PLAN-JSC246-002 | 2 | `Agent`, `Infra`, `Improvement` | Agent-assisted, human review |
| `[agent-skills] Make skills improve route states deterministic` | PLAN-JSC246-003 | 2 | `Agent`, `Infra`, `Improvement` | Agent-assisted, human review |
| `[agent-skills] Prove explain, closeout, and fresh-agent golden path` | PLAN-JSC246-004 through PLAN-JSC246-007 | 2 | `Agent`, `Infra`, `Improvement` | Agent-assisted, human review |

Do not create separate issues for every acceptance ID.

## Dependency Order

```text
PLAN-JSC246-001
  -> PLAN-JSC246-002
      -> PLAN-JSC246-003
          -> PLAN-JSC246-004
          -> PLAN-JSC246-005
              -> PLAN-JSC246-006
                  -> PLAN-JSC246-007
```

Parallelizable after PLAN-JSC246-003:

- PLAN-JSC246-004 and PLAN-JSC246-005 may proceed in parallel if the same agent
  coordinates output-contract changes.

Sequential gates:

- PLAN-JSC246-006 must wait for command behavior.
- PLAN-JSC246-007 must wait for all implementation and docs compression.

## Validation Plan

Focused tests:

```bash
python3 -m pytest Infrastructure/tests/test_ask_golden_path.py
python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py
python3 -m pytest Infrastructure/tests/test_ask_skills_goal.py
python3 -m pytest Infrastructure/tests/test_ask_cli.py -k "repo_doctor or repo_closeout or skills_improve or skills_prove or explain"
```

Focused tests prove local behavior only. They must be paired with the wrapper
and live command gates below before `JSC-246` can close.

Live command evidence:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo surface --json --robot
./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot
./bin/ask skills improve "write a Linear-backed HE spec" --json --robot
./bin/ask skills improve "monitor a long-running HE work phase" --json --robot
./bin/ask skills improve "review this implementation against the spec" --json --robot
./bin/ask skills improve "fix validation blockers after review" --json --robot
./bin/ask skills explain he-spec --json --robot
./bin/ask skills prove he-spec --json --robot
./bin/ask repo closeout --changed --json --robot
```

Optional compatibility evidence:

```bash
./bin/ask skills proof he-spec --json --robot
```

Use this only to prove low-level command-handle reachability. It is not the
golden-path proof command.

Wrapper validation gate:

```bash
./bin/ask repo validate --changed-files <changed files> --json --robot
./bin/ask repo doctor --json --robot
./bin/ask repo closeout --changed --json --robot
```

Artifact gates:

```bash
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
git diff --check -- .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
```

Closeout gate:

```bash
./bin/ask repo closeout --changed --json --robot
```

If closeout is blocked by unrelated pre-existing projection churn, record that
as a blocker in the eval and use focused tests/fixtures as the clean readiness
proof. Do not commit unrelated generated churn just to satisfy this slice.

## Rollback Plan

Rollback is phase-local:

- Revert `PLAN-JSC246-002` if additive doctor fields alter existing
  `next_command`, `blocking`, or `diagnostic_debt` behavior.
- Revert `PLAN-JSC246-003` if route quality worsens or ambiguity is hidden.
- Stop `PLAN-JSC246-004` if proof taxonomy assertions require new schema or
  lifecycle promotion.
- Revert `PLAN-JSC246-005` if closeout claims false readiness or loses sync
  blockers.
- Revert `PLAN-JSC246-006` if docs mention unsupported command behavior or add
  first-contact surface area.

If rollback is triggered:

- Keep `JSC-246` open.
- Record the failed phase and command evidence in the eval artifact.
- Do not proceed to docs compression or Linear status mutation.

## Anti-Regression Constraints

Must not regress:

- `./bin/ask` remains the public control-plane entrypoint.
- `repo doctor` remains the first repo-health truth command.
- Existing `next_command` stays stable for robot consumers.
- Existing `improvement.status` stays compatible for current consumers; richer
  route detail is additive.
- `repo surface` remains non-destructive and classification-first.
- `skills improve` does not bypass catalog parity or reachability blockers.
- `skills proof` and `skills prove` keep their separate roles.
- `skills prove` does not imply trust from reachability alone.
- `repo closeout --changed` remains grounded in changed files and sync needs.
- Generated projections remain generated outputs, not canonical source edits.

Must not reappear:

- Multiple competing first-contact commands in docs.
- New top-level aliases without ablation proof.
- Broad catalogs before the golden path in first-contact surfaces.
- Proof schema work hidden inside this slice.
- Diagnostic debt loops where non-blocking surface warnings prevent task
  continuation.

## Review Gates

At the end of each implementation phase:

1. Run focused validation for that phase.
2. Record exact pass/fail/blocked evidence in the eval artifact.
3. Run simplification review for unnecessary additions.
4. Run bug-fix review for behavioral regressions.
5. Run code review for command-output contract risk.

Do not commit or close Linear before:

- all phase evidence is recorded;
- the eval artifact exists;
- focused tests pass or blockers are explicit;
- no review finding remains open against the phase diff.

## Linear / Spec / Plan / PR Traceability

| Linear issue | Source acceptance IDs | Plan units | Acceptance IDs | PR evidence |
| --- | --- | --- | --- | --- |
| `JSC-246` | SA1, SA2, SA19, SA20 | PLAN-JSC246-001 | SA1, SA2, SA19, SA20 | Plan identity lint; Linear traceability lint; baseline eval section; runtime-budget pass evidence; technical-review checklist. |
| `JSC-246` | SA3, SA4, SA5, SA6, SA19 | PLAN-JSC246-002 | SA3, SA4, SA5, SA6, SA19 | Golden-path and repo-doctor tests; live doctor, runtime-budget, and surface JSON snapshots. |
| `JSC-246` | SA7, SA8 | PLAN-JSC246-003 | SA7, SA8 | Skills improve route-state tests; live handle resolution snapshot; five-goal routing evidence. |
| `JSC-246` | SA9, SA10, SA16 | PLAN-JSC246-004 | SA9, SA10, SA16 | Explain/prove tests; proof taxonomy mapping evidence; final diff review showing no proof-schema expansion. |
| `JSC-246` | SA11, SA18 | PLAN-JSC246-005 | SA11, SA18 | Closeout fixture tests; live closeout blocker/ready evidence where available. |
| `JSC-246` | SA12, SA13, SA14, SA17 | PLAN-JSC246-006 | SA12, SA13, SA14, SA17 | Docs compression diff; ablation notes; command metadata review. |
| `JSC-246` | SA6, SA13, SA15, SA18, SA20 | PLAN-JSC246-007 | SA6, SA13, SA15, SA18, SA20 | `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`; fresh-agent transcript or deterministic script; final technical review gate evidence. |

## Blackboard Delta

```yaml
schema_version: he-blackboard-delta/v1
topic: agent-first-golden-path
linear_issue: JSC-246
selected_slice: Agent First Golden Path
plan_status: ready_for_he_work
live_blockers:
  - id: sync_required
    command: ./bin/ask repo closeout --changed --json --robot
    status: blocked
    sync_needed: true
    owner: unrelated_dirty_harness_engineering_skill_changes
    jsc246_scope_blocker: false
resolved_live_blockers:
  - id: runtime_budget
    command: ./bin/ask runtime budget --json --robot
    status: pass
    unresolved_scope_collisions: []
    baselined_scope_collisions:
      - agents-sdk
      - build-chatgpt-app
      - chatgpt-app-submission
diagnostic_debt:
  - id: repo_surface
    command: ./bin/ask repo surface --json --robot
    blocking: false
    finding_count: 4620
golden_path:
  first_truth: ./bin/ask repo doctor --json --robot
  diagnostic_lane: ./bin/ask repo surface --json --robot
  route: ./bin/ask skills improve "<goal>" --json --robot
  explain: ./bin/ask skills explain <handle> --json --robot
  prove: ./bin/ask skills prove <handle-or-goal> --json --robot
  closeout: ./bin/ask repo closeout --changed --json --robot
non_negotiables:
  - no_new_top_level_first_contact_command_without_ablation
  - no_proof_schema_or_lifecycle_promotion_in_this_slice
  - diagnostic_debt_must_not_block_task_continuation_when_non_blocking
  - docs_compression_after_behavior_stabilization
  - eval_artifact_required_before_linear_closure
post_plan_handoff:
  state: ready_for_he_work
  selected_next_stage: he-work
  evidence: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
  next_action: start PLAN-JSC246-001 baseline snapshots and fixture map
```

## Handoff To he-work

Start with `PLAN-JSC246-001`. Do not edit docs, add aliases, or change proof
schema before baseline snapshots and fixture coverage are recorded.

Recommended first command:

```bash
./bin/ask repo doctor --json --robot
```

Then run the handle-resolution and command snapshot commands from
PLAN-JSC246-001 and record results in:

```text
.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
```
