---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-plan
artifact_type: he-plan
type: he-plan
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Plan
harness_stage: he-plan
status: local_proof_complete_pending_linear_review
date: 2026-05-09
origin: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
risk: medium-high
depth: bounded-execution-slice
traceability_required: true
linear_status: existing
linear_refresh_status: resolved_live_fetch_done
linear_delta_status: pass_via_spec_live_refresh_2026_05_09
spec_live_baseline_status: runtime_budget_pass_with_unrelated_sync_required
spec_deepening_status: linear_delta_live_evidence_drift_and_scope_guards_added
plan_deepening_status: refreshed_against_live_evidence_drift_and_scope_guards
live_evidence_status: diagnostic_counts_are_snapshots_not_acceptance_thresholds
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

## HE Gate Profile

```yaml
gate_profile:
  risk_class: architecture_sensitive
  proven_risks:
    - public command output can route agents incorrectly if next-action
      priority is implicit or contradictory.
    - diagnostic debt can become a loop if advisory findings are treated as
      blockers.
    - proof terminology can expand into neighboring proof-schema or promotion
      work if tests require fields outside the admitted slice.
    - docs compression can become cosmetic if not paired with fresh-agent
      behavior metrics.
    - live closeout can be noisy when unrelated dirty generated/projection work
      exists in the same worktree.
  required_contracts:
    - Plugins/harness-engineering/references/gate-selection-contract.md
    - Plugins/harness-engineering/references/first-principles-contract.md
    - Plugins/harness-engineering/references/agent-native-compression-contract.md
    - Plugins/harness-engineering/references/execution-slice-contract.md
    - Plugins/harness-engineering/references/artifact-routing-contract.md
    - Plugins/harness-engineering/skills/he-plan/references/post-plan-handoff.md
  skipped_contracts:
    - contract: Plugins/harness-engineering/references/plugin-hook-capability-contract.md
      reason: The plan does not add, alter, or depend on bundled plugin hooks.
    - contract: Plugins/harness-engineering/references/domain-model-production-contract.md
      reason: The slice changes command routing and proof semantics, not domain language.
    - contract: codex-security security scan
      reason: The plan admits no permissions, auth, secrets, sandboxing, dependency trust, or external side effects.
  minimum_proof_required:
    continue_to_next_stage: Plan artifact identity, Linear traceability, phase sequencing, negative proof cases, validation commands, rollback rules, and post-plan handoff.
    safe_to_close: Eval artifact with fresh-agent transcript or deterministic script, focused tests, live command evidence, docs compression metric, closeout proof, and no open technical review findings.
    block_next_stage: Missing controlled closeout fixture, unclassified Linear delta, docs-first implementation sequence, proof-schema expansion, or new public command without ablation proof.
  evidence_basis: repo+linear+harness
  downstream_route: he-work
```

This plan inherits the spec's architecture-sensitive risk class. It must not
promote the slice to broad `mixed` governance unless implementation evidence
proves a new risk class that was not present at planning time.

## First-Principles Planning Check

```yaml
first_principles_check:
  verified_failure: Agents can see many useful `ask` surfaces but still need
    repo archaeology to know the first safe command, next command, and closure
    readiness.
  fundamental_constraint: The control plane must be executable through live
    command output and robot JSON, not maintained as duplicated prose.
  assumption_being_challenged: More docs, broader command catalogs, aliases, or
    a cockpit-style command would automatically make the repo more agent-native.
  smallest_effective_mechanism: Characterize current command behavior, add
    focused fixtures, make only additive output changes where tests prove
    ambiguity, then compress docs around verified behavior.
  analogy_or_template_rejected: Do not copy cockpit/dashboard patterns from
    adjacent systems unless ablation proves the existing `ask` namespace cannot
    carry the workflow.
  proof_required: Focused tests, command snapshots, negative proof cases,
    controlled closeout fixtures, docs-opened metric, and eval artifact before
    Linear closure.
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 1
  outcome: proceed
```

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

Live Linear fetch for `JSC-246` was performed during the spec/planning pass.
The refreshed spec then re-ran the Linear Delta Capture Gate and classified
neighboring work. No Linear objects were created or updated.

| Object | Live state | Classification | Plan handling |
| --- | --- | --- | --- |
| `JSC-246` | Existing issue, `Todo`, priority `High`, project `agent-skills`, milestone `Command surface and ask reliability`, labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement` | `approved_current_slice` | Use as the only implementation parent for this plan. |
| `JSC-284` through `JSC-287` | Prior factory gate work marked done/covered in the refreshed spec | `covered_prior_work` | Do not reopen here unless a regression is discovered by JSC-246 validation. |
| `JSC-230` through `JSC-236` | Neighboring commandable skill-tree / child work | `not_admitted` | Do not implement in this slice. |
| `JSC-167`, `JSC-169`, `JSC-171`, `JSC-172`, `JSC-173`, `JSC-174`, `JSC-175` | Adjacent command, routing, and follow-on improvement candidates | `not_admitted` | Do not implement unless a later Linear Delta Capture Gate explicitly admits one. |
| `JSC-174` | `ask start` / first-contact command candidate | `explicitly_excluded` | Do not add or promote `ask start` in this slice; require ablation proof and a later gate. |

No new Linear initiative, project, milestone, label, parent issue, or child
issue is required before implementation. If execution needs child issues, create
at most the phase-level children listed under "Linear Execution Shape"; do not
explode acceptance criteria into individual tickets.

Fresh verification note, `2026-05-09`:

- The live `JSC-246` issue payload remains the authoritative source for the
  selected issue's project, milestone, labels, status, and priority. It confirmed
  `Todo` / `unstarted`, priority `High`, project `agent-skills` with project ID
  `791c2f12-5ffb-4644-8421-f4216ac6d805`, milestone `Command surface and ask
  reliability`, and labels `Roadmap: Next`, `Agent`, `Infra`, `Improvement`.
- `.harness/linear/agent-skills-linear-plan.md` remains the approved local Linear
  Delta Capture snapshot for slice admission. Its `Approved Current Slice`
  admits `JSC-246`; its next-slice queue language is historical context after
  this plan stage, not a competing scope selector.
- If project-name Linear lookups return stale or partial project metadata, such
  as `Ask Control Plane Decomposition` from a milestone listing, do not reroute
  this plan. The JSC-246 issue payload and approved local Linear snapshot outrank
  project-name aggregate lookup surfaces unless the issue payload itself changes.
- If project-label listings omit labels that are present on the JSC-246 issue
  payload, do not classify that as label drift. Label membership for this slice
  is verified from the issue payload, not from a project-label catalog query.

## Source Evidence

Hard evidence:

- `./bin/ask skills resolve he-plan --json --robot` resolved to
  `Plugins/harness-engineering/skills/he-plan/SKILL.md` with source revision
  `17b151a25` and source SHA
  `953d02f2a269df1584a946b2bb6eef45c1e973a563abb8a4d97f422d3d20cce6`.
- Direct Linear fetch for `JSC-246` confirmed the live issue, project,
  milestone, priority, labels, assignee, branch name, updated timestamp, and
  Todo status. Linear research remained unavailable with `Tool research not
  found`, so child/blocker graph refresh beyond the issue payload is not part
  of this plan artifact.
- Fresh live Linear cross-check on `2026-05-09` confirmed that issue-level
  metadata remains the reliable selector for `JSC-246`; project-name aggregate
  milestone and label listing surfaces can be stale or incomplete and must not
  override the issue payload.
- The refreshed spec added a Linear Delta Capture Refresh that keeps
  `JSC-174`, `JSC-230`, and their neighboring issue families outside this
  slice.
- The refreshed spec added a Live Evidence Drift section that treats live
  diagnostic counts as snapshots, not acceptance thresholds.
- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
  defines acceptance IDs `SA1` through `SA20` and now includes the HE Gate
  Profile, First-Principles Check, Negative Proof Requirements, and Agentic
  Search And Artifact Naming rule.
- `.harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md`
  approves handoff to `he-plan` with residual risks and records post-deepening
  artifact identity, frontmatter, and Linear traceability lints as passed.
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
- `./bin/ask repo doctor --json --robot` passed in the refreshed evidence loop
  with `blocking:false`, selected `./bin/ask repo surface --json --robot`, and
  reported repo-surface diagnostics as advisory.
- The refreshed evidence loop reported repo-surface counts of `7448` findings
  across `10817` paths. These counts are environment snapshots for triage, not
  plan acceptance thresholds.
- `./bin/ask runtime budget --json --robot` currently passes with no unresolved
  scope collisions; `agents-sdk`, `build-chatgpt-app`, and
  `chatgpt-app-submission` are baselined.
- `./bin/ask skills explain he-spec --json --robot` passed and confirmed
  canonical source, generated handle, rooted projection, latent runtime,
  validation command, and current proof reachability next command.
- `./bin/ask skills prove he-spec --json --robot` passed with
  `proof_status: reachable_without_outcome_proof`, reachability and structural
  proof, and outcome proof available but not run.
- `./bin/ask repo closeout --changed --json --robot` currently reports
  `sync_required` because unrelated dirty harness-engineering, plugin-factory,
  skill-factory, generated, and session-evidence files are present in the
  worktree. Runtime budget still passes, and repo-surface debt remains
  non-blocking diagnostic debt.

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
- Current live diagnostic counts are not stable enough for acceptance checks.
  Implementation should assert semantic classes, blocker flags, and
  `next_command` behavior instead of exact finding totals.

## Deepening Refresh Rules

These rules were added after the spec deepening pass and bind all implementation
units below:

- Do not implement `JSC-174`, `ask start`, `JSC-230` through `JSC-236`, or
  adjacent commandable skill-tree work in this plan.
- Do not treat live repo-surface finding totals as pass/fail thresholds.
  Validate semantic behavior: advisory versus blocking, selected
  `next_command`, blocker ids, and continuation safety.
- Do not treat the current dirty worktree as either clean JSC-246 readiness or
  as JSC-246 implementation scope. Prove closeout with controlled fixtures or
  an isolated changed-file scenario.
- Preserve the `skills proof` / `skills prove` compatibility boundary unless a
  later gate admits a compatibility migration and updates tests and consumers
  together.
- If live Linear, command output, or worktree evidence drifts again during
  `he-work`, refresh the eval artifact first and then decide whether this plan
  still applies.

## Ablation Admission Protocol

This slice repeatedly mentions ablation because the tempting failure mode is to
add a new command, alias, dashboard, or docs surface before proving the existing
golden path cannot carry the job. Ablation proof must be concrete, not a product
preference.

An additive public surface is admitted only if all of these are true:

- The implementation first tries the existing command loop:
  `repo doctor`, `repo surface`, `skills improve`, `skills explain`,
  `skills prove`, and `repo closeout --changed`.
- The eval records the exact point where that loop fails with command output,
  not just narrative friction.
- The failure is not fixable by changing `next_command`, route-state fields,
  docs ordering, command metadata, or eval instructions inside the existing
  loop.
- The proposed new surface has one owner, one acceptance ID mapping, one
  rollback path, and one focused test proving why it is necessary.
- A later Linear Delta Capture Gate explicitly admits the new surface or issue.

Without that proof, implementation must improve the existing loop rather than
add `ask start`, `repo onboard`, `repo next`, a cockpit/dashboard command, or a
new first-contact alias.

## Fresh-Agent Eval Isolation Protocol

The fresh-agent proof must not inherit this planning thread's context.
Acceptable evidence forms:

- a new Codex/agent session transcript whose first repo action is
  `./bin/ask repo doctor --json --robot`;
- a deterministic script that runs the golden-path commands from a clean process
  and stores command, exit code, selected JSON fields, and stderr/tool blockers;
- a tightly scoped subagent transcript where the instruction includes the repo
  goal but not the plan's answers, expected command sequence, or success
  criteria.

The eval must record:

- environment and cwd;
- exact first command;
- commands-to-ready-or-blocked count;
- docs opened before first command;
- whether each `next_command` was followed or intentionally skipped;
- the reason for every skipped command;
- raw output excerpts or JSON field summaries sufficient for another reviewer
  to reproduce the verdict.

Same-thread output can support coordination but cannot satisfy fresh-agent proof.
Screenshots, prose summaries, or copied expected outputs are not sufficient.

Closure requires one immutable fresh-agent evidence bundle. The eval must record
all of:

- bundle path under `.harness/session-evidence/` or `.harness/evals/evidence/`;
- transcript/session id or script name;
- timestamp;
- cwd;
- command list;
- exit codes;
- SHA-256 hash of the transcript or command log;
- whether the first command was exactly
  `./bin/ask repo doctor --json --robot`.

If the bundle path or hash is missing, the eval must recommend `Blocked` or
`Needs rework`, not `Complete` or `Complete with follow-up`.

## Live Evidence Freshness Gate

Any live command evidence used for closure must be refreshed inside the final
closure window.

Closure window:

- Default maximum age: same local day as the closure recommendation.
- If the implementation spans multiple days, re-run all live command gates
  before writing the final eval recommendation.
- If a command is too expensive or blocked, record it as `blocked` with exact
  stderr/tool error, blocker owner, and next recovery step.

Commands that must be fresh at closure:

```bash
./bin/ask repo doctor --json --robot
./bin/ask repo surface --json --robot
./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot
./bin/ask skills explain he-spec --json --robot
./bin/ask skills prove he-spec --json --robot
./bin/ask repo closeout --changed --json --robot
```

Diagnostic counts remain snapshots, but blocker/advisory classification,
selected `next_command`, route state, and closeout ownership must be current
when the eval recommends closure.

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
- `JSC-174`, `JSC-230` through `JSC-236`, `JSC-167`, `JSC-169`, `JSC-171`,
  `JSC-172`, `JSC-173`, and `JSC-175` unless a later Linear Delta Capture Gate
  admits them.
- New `repo onboard`, `repo next`, or other top-level first-contact command
  unless ablation proves the existing command loop cannot carry the workflow.
- Cleanup of `artifacts/**`, `Infrastructure/artifacts/**`, `.skillsets/**`,
  `.harness/*.db`, `skills-system/**`, or `Plugins/cache/**`.
- Manual edits to generated/runtime projections except through canonical sync
  lanes if implementation changes require regeneration.
- Unrelated skill content rewrites.

## Implementation Checkpoints

The implementation must advance through checkpoints, not broad file sweeps.
Each checkpoint needs evidence before the next one starts.

| Checkpoint | Required before moving on | Stop condition |
| --- | --- | --- |
| Baseline characterization | Current command JSON snapshots, handle-resolution snapshots, current test inventory, and closeout blocker classification are recorded in the eval artifact. | Any snapshot cannot run and the blocker is not recorded with exact command, exit status, and stderr/tool error. |
| Public JSON contract design | Additive field placement is confirmed for nested `data.doctor`, top-level mirrors, and `skills improve` result payloads before code edits. | Any plan requires renaming/removing existing fields or changing command names. |
| Fixture-first implementation | New/updated tests fail against the old behavior or explicitly document an already-covered behavior before production code changes are treated as complete. | Implementation changes are made with no corresponding fixture for the affected route or closeout state. |
| Live command verification | Focused tests pass and representative `./bin/ask ... --json --robot` commands are captured after behavior changes. | Live output contradicts the expected `next_command_kind`, `next_command_blocks_task`, `route_state`, or closeout blocker semantics. |
| Docs compression | Docs/metadata changes happen only after command behavior and live output are stable. | Docs introduce a command, alias, catalog, or product claim not proven by live command output. |
| Eval closure | Eval artifact includes before/after evidence, negative proof, fresh-agent proof, validation outcomes, and residual blockers. | Eval is prose-only, same-thread-only, missing a negative case, or treats unrelated dirty worktree state as clean readiness. |

The implementation should not batch all phases into one indistinguishable diff.
If a later agent continues the work after interruption, it should resume from
the first incomplete checkpoint instead of reinterpreting the whole plan.

## Fixture Inventory

Minimum fixture set before closure:

| Fixture ID | Command surface | State to prove | Primary files | Required evidence |
| --- | --- | --- | --- | --- |
| `doctor-blocker-over-advisory` | `repo doctor` | A blocking repair outranks repo-surface advisory debt. | `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py` | Failing-before/passing-after fixture or existing assertion plus live snapshot. |
| `doctor-advisory-continues` | `repo doctor` | Non-blocking diagnostic debt emits `diagnostic_advisory` and does not block task continuation. | `Infrastructure/tests/test_ask_golden_path.py`, `Infrastructure/tests/test_ask_repo_doctor.py` | JSON assertion for `next_command_kind` and `next_command_blocks_task`. |
| `doctor-no-safe-command` | `repo doctor` | Selected actionable warning/blocker with no recovery command is explicit, not silent. | `Infrastructure/tests/test_ask_golden_path.py` | `no_safe_command` classification with blocking state. |
| `skills-improve-fallback` | `skills improve` | Fallback route remains explicit and actionable. | `Infrastructure/tests/test_ask_skills_goal.py`, `Infrastructure/tests/test_ask_cli.py` | `status`, `route_state`, rationale, confidence, and `next_command`. |
| `skills-improve-ambiguity` | `skills improve` | Unsafe ambiguity blocks instead of silently choosing. | `Infrastructure/tests/test_ask_skills_goal.py` | `status: blocked` plus `route_state: blocked_ambiguity`. |
| `skills-improve-dependency-blocker` | `skills improve` | Catalog/projection/runtime dependency blockers cannot be bypassed by fallback. | `Infrastructure/tests/test_ask_skills_goal.py` | `route_state: blocked_dependency` or equivalent explicit dependency blocker. |
| `skills-explain-missing-handle` | `skills explain` | Missing handle returns structured recovery guidance. | `Infrastructure/tests/test_ask_cli.py` | Stable error/not-found payload without traceback. |
| `skills-prove-reachability-only` | `skills prove` | Reachability or structural evidence does not imply trust/outcome proof. | `Infrastructure/tests/test_ask_cli.py` | Proof taxonomy assertion preserving `reachable_without_outcome_proof` semantics. |
| `closeout-sync-required` | `repo closeout --changed` | Skill/runtime projection changes produce sync-required blocker. | `Infrastructure/tests/test_ask_repo_doctor.py` or lower-level closeout helper tests | Controlled changed-file fixture, not current dirty worktree only. |
| `closeout-ready-controlled` | `repo closeout --changed` | Clean or validation-ready changed-file scenario can be proven independently of unrelated churn. | `Infrastructure/tests/test_ask_repo_doctor.py` or lower-level closeout helper tests | Controlled fixture or isolated branch evidence. |
| `docs-only-not-complete` | Docs/metadata | Docs compression cannot satisfy implementation without command/eval proof. | `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` | Eval explicitly rejects docs-only closure. |

If a named fixture cannot be implemented without broad test-harness work, the
eval must classify it as `blocked_fixture_gap` and keep `JSC-246` open unless
human review explicitly narrows the acceptance scope.

## Changed-File Validation Ownership

`./bin/ask repo validate --changed-files <paths> --json --robot` must receive
only files touched for this slice. Before final validation, build a deterministic
JSC-246 changed-file ledger and record it in the eval before running validation.

Allowed sources:

- explicit path allowlist derived from the plan's in-scope files; and
- `git diff --name-only <merge-base>...HEAD` or `git diff --name-only` only
  when the eval also records why the current dirty tree is the selected scope.

The eval must include:

```yaml
changed_file_ledger:
  baseline_command: ""
  merge_base: ""
  included_paths: []
  excluded_paths: []
  exclusion_reason_by_path: {}
  validation_command: ""
```

Do not rely on an implicit shell expansion or manually curated command line
alone. The ledger is the source of truth for what belongs to JSC-246 validation.

Classify each file:

| Class | Examples | Validation handling |
| --- | --- | --- |
| JSC-246 implementation | `Infrastructure/scripts/lib/ask/**`, focused tests, JSC-246 docs, JSC-246 eval artifact | Include in changed-file validation. |
| JSC-246 harness artifacts | This plan, source spec, plan technical review, eval artifact | Include in artifact lints and traceability evidence. |
| Pre-existing unrelated work | HE plugin/factory changes, generated projection/cache/session-evidence files not part of JSC-246 | Exclude from JSC-246 readiness claims; record as unrelated closeout noise if live closeout sees it. |
| Generated projection refresh admitted by JSC-246 | Only if implementation requires canonical sync and the projection is generated by the approved sync command | Include the sync command and output; do not hand-edit projection files. |

If the working tree contains unrelated changes at closure time, the eval must
separate:

- focused JSC-246 validation result;
- live whole-worktree closeout result;
- whether the unrelated blocker prevents committing this branch;
- what must happen before Linear can close.

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

Validation evidence must be recorded with this minimum shape:

```yaml
validation_result:
  command: ""
  status: pass|fail|blocked|not_run
  evidence: ""
  affected_acceptance_ids: []
  blocks_closure: true|false
  blocker_owner: jsc246|unrelated_dirty_worktree|environment|unknown
  next_recovery_step: ""
```

Do not mark `not_run` as equivalent to `pass`. Do not treat a focused test pass
as final readiness if the wrapper gate is blocked for a JSC-246-owned reason.

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

## Eval Artifact Skeleton

`PLAN-JSC246-007` must produce or update:

```text
.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
```

Required sections:

1. Executive Eval Summary
2. Evaluated Slice
3. Linear Backlink Map
4. Baseline Command Snapshots
5. After-Change Command Snapshots
6. Fixture And Negative Proof Results
7. Live Command Validation Results
8. Changed-File Validation
9. Fresh-Agent Or Deterministic Script Evidence
10. Docs Compression Evidence
11. Drift Validation
12. Failures / Blockers
13. Linear Completion Recommendation
14. Evidence & Traceability Matrix

The eval must include these identifiers:

```yaml
Linear Project: agent-skills
Linear Milestone: Command surface and ask reliability
Linear Parent Issue: JSC-246
Linear Status Recommendation: Complete|Complete with follow-up|Blocked|Needs rework|Unsafe to close
Proof Artifact Links:
  - .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
  - .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
  - .harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md
```

`Complete` is allowed only when:

- every required fixture whose Negative Proof Implementation Matrix row has
  `Closure blocker: Yes` has `pass`;
- fresh-agent or deterministic script evidence is present;
- wrapper validation is either passed or blocked only by explicitly unrelated
  worktree state;
- no open technical review finding blocks closure;
- the eval artifact passes artifact identity, frontmatter, and Linear
  traceability lints.

Non-blocking exceptions are allowed only for fixtures that are not closure
blockers, and the eval must include:

```yaml
fixture_exception:
  fixture_id: ""
  allowed_reason: environment_only|human_scope_narrowed|duplicate_coverage
  owner: ""
  follow_up_issue_or_artifact: ""
  reviewer_approval: ""
```

No `blocked_fixture_gap` may be counted as `Complete` when its matrix row has
`Closure blocker: Yes`.

`Complete with follow-up` is allowed only when the golden path works for
JSC-246, all blocking acceptance IDs pass, and the follow-up is explicitly
outside the admitted slice. It is not allowed when:

- a required negative proof fixture is missing;
- fresh-agent evidence is same-thread-only;
- wrapper validation is blocked by a JSC-246-owned change;
- a new command or alias is needed but lacks ablation proof;
- the plan/review/eval artifact chain fails identity, frontmatter, or Linear
  traceability lint.

`Blocked`, `Needs rework`, or `Unsafe to close` must name the smallest recovery
step and the owning lane: JSC-246 implementation, unrelated worktree cleanup,
environment/tooling, Linear scope decision, or follow-up slice.

## Negative Proof Implementation Matrix

The implementation must prove what the command loop refuses, not only what it
does on a clean path.

| Negative case | Planned proof location | Expected implementation response | Closure blocker |
| --- | --- | --- | --- |
| `repo doctor` sees a blocking sync failure and repo-surface diagnostic debt. | PLAN-JSC246-002 doctor priority fixtures. | Blocking sync repair wins; surface debt remains visible as secondary/advisory evidence. | Yes |
| `repo doctor` sees only non-blocking repo-surface diagnostic debt. | PLAN-JSC246-002 doctor advisory fixture plus PLAN-JSC246-007 fresh-agent eval. | Emit `diagnostic_advisory`, `next_command_blocks_task: false`, and keep repo usable. | Yes |
| `skills improve` resolves only through fallback. | PLAN-JSC246-003 route fixtures. | Emit `resolved_with_fallback`, confidence, rationale, fallback note, and concrete proof command. | Yes |
| `skills improve` has unsafe ambiguity. | PLAN-JSC246-003 route fixtures. | Emit `blocked_ambiguity` or equivalent explicit blocked route state; do not silently pick. | Yes |
| `skills explain` receives a missing handle. | PLAN-JSC246-004 explain fixtures. | Return structured not-found/error output plus recovery guidance; no traceback. | Yes |
| `skills prove` has reachability/structural evidence only. | PLAN-JSC246-004 proof taxonomy assertions. | Preserve `reachable_without_outcome_proof`; do not imply trust, default visibility, promotion, or outcome proof. | Yes |
| `repo closeout --changed` sees unrelated generated/projection churn. | PLAN-JSC246-005 closeout fixtures and live evidence. | Report blocker and sync command; do not claim clean JSC-246 readiness. | Yes |
| First-contact docs change without command/eval proof. | PLAN-JSC246-006 docs compression review. | Reject readiness as docs-only completion. | Yes |
| A new public command or alias appears before ablation proof. | PLAN-JSC246-006 ablation notes and final review. | Reject or classify out of scope for JSC-246. | Yes |

Any negative case omitted from tests must be recorded as a blocked fixture gap in
the eval artifact with the smallest follow-up needed to make it executable.

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
- Re-run the post-deepening spec and review lints that were blocked by the
  approval/usage-limit failure before implementation claims readiness.
- Preserve the existing stable plan filename for this active slice. If a later
  dated Linear-style rename is approved, update frontmatter, spec/review/eval
  backlinks, and `canonical_slug` references in the same change.

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
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
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

## Compound Closeout State

`he-eval-report` now classifies the local `JSC-246` proof as complete for
`PLAN-JSC246-001` through `PLAN-JSC246-007`.

`he-compound` routing should no longer resume this plan at `he-work`. The
earliest remaining lifecycle step is human Linear closure/linkage review for
`JSC-246` only. Do not infer completion for unrelated command-surface milestone
work, `JSC-230` through `JSC-236`, `JSC-174`, or broad dirty-worktree cleanup.

Closure status:

- Local HE proof: complete.
- Linear mutation: not attempted from the heartbeat/eval pass.
- Next route: human Linear status/linkage review, using the eval artifact and
  pushed commit evidence.
- Residual risk: unrelated dirty worktree entries may still exist and must stay
  outside `JSC-246` closure claims.

## Blackboard Delta

```yaml
schema_version: he-blackboard-delta/v1
topic: agent-first-golden-path
linear_issue: JSC-246
selected_slice: Agent First Golden Path
plan_status: local_proof_complete_pending_linear_review
live_blockers:
  - id: unrelated_dirty_worktree
    command: git status --short --branch
    status: present
    owner: unrelated_dirty_harness_engineering_plugin_factory_skill_factory_session_evidence_and_generated_artifacts
    jsc246_scope_blocker: false
validation_follow_up:
  - id: post_deepening_lints
    status: pass
    required_before: complete
    commands:
      - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
      - python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
      - python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
      - python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/review/agent-skills-jsc-246-agent-first-golden-path-technical-review.md
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
    finding_count_snapshot: 7448
    finding_path_count_snapshot: 10817
    acceptance_threshold: semantic_advisory_not_exact_count
golden_path:
  first_truth: ./bin/ask repo doctor --json --robot
  diagnostic_lane: ./bin/ask repo surface --json --robot
  route: ./bin/ask skills improve "<goal>" --json --robot
  explain: ./bin/ask skills explain <handle> --json --robot
  prove: ./bin/ask skills prove <handle-or-goal> --json --robot
  closeout: ./bin/ask repo closeout --changed --json --robot
non_negotiables:
  - no_new_top_level_first_contact_command_without_ablation
  - no_ask_start_or_jsc174_work_without_later_delta_gate
  - no_jsc230_to_jsc236_commandable_skill_tree_work
  - no_proof_schema_or_lifecycle_promotion_in_this_slice
  - diagnostic_debt_must_not_block_task_continuation_when_non_blocking
  - diagnostic_finding_counts_are_snapshots_not_thresholds
  - fresh_agent_evidence_requires_bundle_path_and_sha256
  - closure_live_evidence_must_be_refreshed_same_day
  - changed_file_validation_requires_recorded_ledger
  - closure_blocker_fixtures_cannot_be_waived
  - docs_compression_after_behavior_stabilization
  - eval_artifact_required_before_linear_closure
post_plan_handoff:
  state: local_proof_complete_pending_linear_review
  selected_next_stage: human_linear_closure_linkage_review
  evidence: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
  eval_artifact: .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md
  next_action: link the eval and pushed commit evidence to JSC-246 through the normal human-reviewed Linear update path; do not resume he-work for PLAN-JSC246-001 through PLAN-JSC246-007
```

## Handoff To Linear Closure Review

Do not restart `PLAN-JSC246-001`. The eval artifact records fresh completion
evidence for all seven plan units.

Recommended closure evidence:

- `.harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md`
- pushed commit evidence for the JSC-246 implementation/proof refresh
- focused validation evidence recorded in the eval artifact
- explicit note that Linear mutation was intentionally not attempted during the
  heartbeat/eval pass
