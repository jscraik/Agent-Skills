---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-plan-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Plan Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-08
origin: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
reviewed_artifact: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
traceability_required: true
linear_status: existing
linear_issue: JSC-246
linear_issue_url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Build repo surface contract and agent capability control-plane golden paths"
review_result: approved_with_residual_risks
---

# Agent Skills JSC-246 Agent First Golden Path Plan Technical Review

## Findings

No open blocking findings remain after the plan-deepening pass.

### Remediated Finding 1: `skills improve` State Change Could Break Consumers

Severity: High  
Status: Fixed in plan

The original plan said unresolved ambiguity should change
`improvement.status` from `blocked` to `blocked_ambiguity`. That would satisfy
the spec vocabulary, but it could break existing consumers that treat
`status: blocked` as the stable failure class.

Fix applied:

- Added "Design Decision: Skills Improve Route State Compatibility".
- Preserved existing `status: resolved`, `status: resolved_with_fallback`, and
  `status: blocked`.
- Added additive `route_state` and `route_state_reason` fields for
  `resolved`, `resolved_with_fallback`, `blocked_ambiguity`,
  `blocked_reachability`, and `blocked_dependency`.
- Updated `PLAN-JSC246-003` and anti-regression constraints to require
  compatibility for current consumers.

Why it matters:

This prevents a plan that improves agent semantics by silently destabilizing
the current JSON contract.

### Remediated Finding 2: Doctor Additive Fields Needed Envelope Placement

Severity: Medium-high  
Status: Fixed in plan

The plan proposed `next_command_kind` and `next_command_blocks_task`, but did
not say where those fields must appear or how they interact with the existing
duplicated `repo_doctor` payload.

Fix applied:

- Added compatibility requirements under the diagnostic continuation design.
- Required new fields under `data.doctor`.
- Required top-level `data.<field>` mirrors to stay consistent with the
  existing `result.data.update(payload)` behavior.
- Required `metadata.next_steps` and `data.doctor.next_command` not to
  contradict each other.

Why it matters:

The repo already exposes the doctor payload in both nested and top-level forms.
Changing only one shape would create brittle behavior for agents and tests.

### Remediated Finding 3: `skills proof` And `skills prove` Were Easy To Conflate

Severity: Medium  
Status: Fixed in plan

The plan used the golden-path `skills prove` command but did not explicitly
protect the existing `skills proof` reachability command. The implementation
surface exposes both, and `skills explain` currently emits proof-style
reachability commands.

Fix applied:

- Added "Proof Command Boundary".
- Defined `skills proof` as the command-handle reachability check.
- Defined `skills prove` as the agent-facing proof scorecard.
- Required both to remain distinct in this slice.
- Added `./bin/ask skills proof he-spec --json --robot` to the relevant
  validation commands.

Why it matters:

The slice must not accidentally rename, collapse, or reinterpret proof
commands while claiming to avoid proof-system migration.

### Remediated Finding 4: Fresh-Agent Eval Could Pass With Prose Only

Severity: Medium  
Status: Fixed in plan

The original plan required a fresh-agent transcript or deterministic script,
but did not explicitly require command output evidence. That left a loophole
where a narrative transcript could satisfy closure without proving real command
behavior.

Fix applied:

- `PLAN-JSC246-007` now requires command output excerpts or JSON field
  summaries from actual command runs.
- Blocked commands must include exact stderr, exit code, or tool blocker
  evidence.

Why it matters:

The product goal is executable command truth. A manually written transcript is
not enough proof.

### Remediated Finding 5: Wrapper Validation Could Be Bypassed

Severity: Medium-high  
Status: Fixed in plan

The plan used focused `pytest` commands, which are useful for fixture-level
proof, but the repo instructions make `./bin/ask` the operational control-plane
entrypoint. Without an explicit wrapper gate, implementation could satisfy the
plan while bypassing the repo-native validation lane.

Fix applied:

- Added "Design Decision: Validation Routing".
- Kept focused pytest commands as local behavior evidence.
- Required `./bin/ask repo validate --changed-files <paths> --json --robot`,
  `./bin/ask repo doctor --json --robot`, and
  `./bin/ask repo closeout --changed --json --robot` before closure.
- Required exact blocker evidence if wrapper validation is blocked by unrelated
  dirty worktree state.

Why it matters:

This keeps the plan aligned with the repo's own command contract instead of
letting implementation pass through ad hoc test selection alone.

### Remediated Finding 6: Doctor Continuation Had Two Ambiguous Edges

Severity: Medium  
Status: Fixed in plan

The plan treated any `metadata.next_steps` disagreement with
`data.doctor.next_command` as blocking, but existing commands may legitimately
leave `metadata.next_steps` empty while `data.doctor.next_command` carries the
robot continuation. The plan also did not say what happens if the selected
blocker or warning has no recovery command.

Fix applied:

- Clarified that only populated command-bearing `metadata.next_steps` can
  contradict `data.doctor.next_command`.
- Added `next_command_kind: no_safe_command`.
- Required tests for selected blockers or actionable warnings with no recovery
  command.

Why it matters:

This prevents both false release blockers and silent null guidance in the
agent-facing first-contact path.

### Remediated Finding 7: Fresh-Agent Evidence Needed Isolation

Severity: Medium  
Status: Fixed in plan

The plan required command evidence, but did not prevent the same planning
thread from being treated as the "fresh agent" proof. That would overstate
discoverability because the current thread already has the spec, plan, review,
and repo context loaded.

Fix applied:

- Required fresh-agent proof to come from a new agent session, deterministic
  script, or explicitly clean transcript.
- Classified same-thread output as coordination evidence, not fresh-agent
  proof.

Why it matters:

The slice is supposed to prove first-contact navigation. A context-warmed
planning thread is not a valid first-contact user.

## Review Verdict

Approved for `he-work`.

The plan now has a safe execution shape:

- it starts with baseline snapshots and fixture coverage;
- it changes command JSON fields additively;
- it preserves existing command consumers;
- it keeps proof-schema and lifecycle-promotion work out of scope;
- it delays docs compression until command behavior is stable;
- it requires generated eval evidence before Linear closure.
- it uses repo-wrapper validation as the final closure authority.

## Linear Work Item Contract

`linear_status: existing`

This review covers the existing Linear work item:

- Linear issue: `JSC-246`
- Linear team: `JSC`
- Linear workspace: `Jscraik`
- Linear project: `agent-skills`
- Linear milestone: `Command surface and ask reliability`
- Parent issue title: `Build repo surface contract and agent capability
  control-plane golden paths`

The review does not create or approve additional Linear objects. It verifies
that the current plan can safely drive `he-work`.

## Residual Risks

### Residual Risk 1: Live Dirty Worktree Still Blocks Clean Closeout Evidence

The plan correctly treats current live `repo closeout --changed` as a blocked
dirty-worktree case. Implementation must still avoid pulling unrelated
projection churn into this slice.

Required response:

- Use helper-level fixtures or an isolated branch for clean closeout proof.
- Record live closeout as blocked evidence only when unrelated changes remain.

### Residual Risk 2: Route Fixtures May Need Route-Family Assertions

The plan requires exact handle resolution before exact-handle assertions, but
some representative goals may remain better asserted by route family if current
ownership metadata is not stable enough.

Required response:

- Prefer route-state and route-family assertions.
- Assert exact handles only after live `skills resolve` confirms ownership.

### Residual Risk 3: Full CLI Test Selection May Be Noisy

The plan includes focused `pytest -k` commands. If the repo's current
environment has unrelated CLI test failures, implementation must not hide them,
but it may use narrower helper tests plus live command evidence to isolate
`JSC-246` behavior.

Required response:

- Record exact pass/fail/blocked outcomes.
- Keep unrelated failures classified instead of editing around them.

### Residual Risk 4: Fresh-Agent Proof Requires Real Isolation

The plan now requires fresh-agent isolation, but implementation must still make
that operationally real. A transcript from the current thread is not sufficient
unless it is explicitly treated as coordination evidence only.

Required response:

- Use a new agent session or deterministic script for the closure proof.
- Record the command outputs that drove navigation decisions.

## Validation Evidence

| Command | Result | Notes |
| --- | --- | --- |
| `./bin/ask skills resolve he-code-review --json` | pass | Confirmed canonical HE code review workflow at `Plugins/harness-engineering/skills/he-code-review/SKILL.md`. |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md` | pass | Plan artifact identity remains valid after deepening. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md` | pass | Plan Linear traceability remains valid after deepening. |
| `git diff --check -- .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md` | pass | No whitespace errors in the deepened plan. |
| `./bin/ask repo validate --help` | pass | Confirmed repo wrapper supports `--changed-files` and JSON/robot flags required by the closure gate. |
| `./bin/ask repo validate --changed-files .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md .harness/review/agent-skills-jsc-246-agent-first-golden-path-plan-technical-review.md --json --robot` | blocked | Plan/docs lint and lifecycle checks passed, but existing required failures remain: `SKILLSET_SOURCE_HASH_STALE` in `context-budget.log` and projection drift in cache mirrors. This validates the wrapper route and confirms closure still depends on resolving or explicitly classifying repo-surface projection debt. |
| `./bin/ask repo doctor --json --robot` | pass | Repo is usable with non-blocking diagnostic debt: `blocking: false`, next command `./bin/ask repo surface --json --robot`, 4537 repo-surface diagnostic findings. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Review coverage |
| --- | --- | --- |
| `JSC-246` | SA3, SA4, SA5, SA6 | Reviewed doctor next-action contract and diagnostic continuation compatibility. |
| `JSC-246` | SA7, SA8 | Reviewed additive route-state contract and handle-resolution fixture guard. |
| `JSC-246` | SA9, SA10, SA16 | Reviewed `skills proof` / `skills prove` boundary and proof-schema exclusion. |
| `JSC-246` | SA11, SA18 | Reviewed closeout isolation and eval-before-closure gate. |
| `JSC-246` | SA12, SA13, SA14, SA15, SA17 | Reviewed docs compression sequencing, ablation requirement, and fresh-agent proof gate. |

## Evidence & Traceability Matrix

| Conclusion | Evidence type | Files / commands | Confidence | Why it matters |
| --- | --- | --- | --- | --- |
| The plan is ready for `he-work`. | validation, review | `.harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md`; identity lint; Linear traceability lint | High | The plan is traceable, phase-bounded, and validates structurally. |
| `skills improve` compatibility is now protected. | plan review | "Design Decision: Skills Improve Route State Compatibility"; `PLAN-JSC246-003` | High | Prevents semantic improvement from breaking existing JSON consumers. |
| Doctor diagnostic continuation is now testable without breaking current fields. | source-code, plan review | `Infrastructure/scripts/lib/ask/golden_path.py`; plan diagnostic design section | High | Existing doctor output can be extended additively while preserving robot consumers. |
| Proof command scope is bounded. | source-code, plan review | `Infrastructure/bin/ask`; plan proof command boundary | High | Avoids accidental proof-system migration in `JSC-246`. |
| Fresh-agent proof cannot be prose-only. | plan review | `PLAN-JSC246-007`; eval requirements | Medium-high | Forces closure to use command output, not narrative confidence. |
| Wrapper validation is now required for closure. | command contract, plan review | `./bin/ask repo validate --help`; validation routing design | High | Prevents the plan from bypassing the repo-native control plane. |
| Doctor next-step semantics now avoid false contradictions and null recovery guidance. | plan review | diagnostic continuation design; `PLAN-JSC246-002` | High | Makes the first-contact continuation contract testable without over-constraining empty metadata. |
| Fresh-agent evidence must be isolated. | plan review | `PLAN-JSC246-007` | High | Prevents context-warmed planning evidence from masquerading as first-contact usability proof. |
