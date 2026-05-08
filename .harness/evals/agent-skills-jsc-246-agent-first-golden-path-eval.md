---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-eval
artifact_type: he-eval-report
type: he-eval-report
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Eval
harness_stage: he-eval-report
status: phase_002_in_review
date: 2026-05-08
traceability_required: true
origin: .harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md
linear_issue: JSC-246
linear_status: existing
linear_milestone: Command surface and ask reliability
---

# Agent Skills JSC-246 Agent First Golden Path Eval

## Status

`PLAN-JSC246-001` baseline evidence is captured.

`PLAN-JSC246-002` implementation is locally complete and pending phase-end
review gates before any local commit.

## Scope

- Plan:
  `.harness/plan/agent-skills-jsc-246-agent-first-golden-path-plan.md`
- Linear issue: `JSC-246`
- Current completed implementation unit: `PLAN-JSC246-002`
- Current phase gate status: review pending

## Linear Work Item Contract

| Field | Value |
| --- | --- |
| Linear issue | `JSC-246` |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Milestone | `Command surface and ask reliability` |
| Parent issue title | `Build repo surface contract and agent capability control-plane golden paths` |
| Priority | `2` |
| Status at plan time | `Todo` |
| Execution route | Agent-assisted; human review required for public command output contracts |

## Linear Delta Capture

Live Linear refresh is blocked in this session.

Command/tool attempted:
`mcp__codex_apps__linear._research`

Result:
blocked

Evidence:
Linear connector returned `INVALID_ARGUMENT` with MCP error
`Tool research not found`.

Plan handling:
continue from the approved local Linear snapshot in the plan because the current
user explicitly approved `he-work`, and do not mutate Linear from this phase.

## PLAN-JSC246-001 Baseline Evidence

Command:
`./bin/ask repo doctor --json --robot`

Result:
pass

Summary:
`status: success`; `blocking: false`; `metadata.next_steps: []`;
`next_command: ./bin/ask repo surface --json --robot`; diagnostic debt present.

Command:
`./bin/ask repo surface --json --robot`

Result:
pass with warning

Summary:
`status: success`; `repo_surface.status: warning`; `total_paths: 7835`;
`blocking_findings: 4585`.

Command:
`./bin/ask skills improve "make agents better at fixing PR review comments" --json --robot`

Result:
pass

Summary:
`status: success`; `improvement.status: resolved_with_fallback`;
recommended capability `$autofix`; `next_command:
./bin/ask skills proof autofix --json --robot`.

Command:
`./bin/ask skills explain he-spec --json --robot`

Result:
pass

Summary:
`explanation.status: resolved`; canonical source
`Plugins/harness-engineering/skills/he-spec/SKILL.md`; reachability proof
command `./bin/ask skills proof he-spec --json --robot`.

Command:
`./bin/ask skills prove he-spec --json --robot`

Result:
pass

Summary:
`skill_proof.proof_status: reachable_without_outcome_proof`;
`command_handle_proof.status: pass`; next command
`./bin/ask workouts run harness-engineering/he-spec --json --robot`.

Command:
`./bin/ask repo closeout --changed --json --robot`

Result:
blocked

Summary:
`status: error`; `commit_readiness.blockers: [sync_required]`;
`changed_file_count: 110`; next command
`./bin/ask skills sync --scope workspace --projection rooted --json --robot`.

Interpretation:
closeout is blocked by broader dirty/generated surfaces in the current worktree,
not by the `PLAN-JSC246-002` doctor continuation patch alone.

## Handle Resolution Baseline

| Handle | Result | Source |
| --- | --- | --- |
| `autofix` | pass | `Skills/agent-ops/autofix/SKILL.md` |
| `he-spec` | pass | `Plugins/harness-engineering/skills/he-spec/SKILL.md` |
| `he-heartbeat` | pass | `Plugins/harness-engineering/skills/he-heartbeat/SKILL.md` |
| `he-code-review` | pass | `Plugins/harness-engineering/skills/he-code-review/SKILL.md` |
| `he-fix-bugs` | pass | `Plugins/harness-engineering/skills/he-fix-bugs/SKILL.md` |

## PLAN-JSC246-002 Implementation Evidence

Changed files:

- `Infrastructure/scripts/lib/ask/golden_path.py`
- `Infrastructure/tests/test_ask_golden_path.py`
- `Infrastructure/tests/test_ask_repo_doctor.py`

Behavior added:

- `next_command_kind`
- `next_command_blocks_task`
- `no_safe_command` classification for missing recovery commands

Compatibility preserved:

- existing `next_command`
- existing `blocking`
- existing `blockers`
- existing `diagnostic_debt`
- existing `signals`
- `repo_doctor` nested `data.doctor` payload and top-level
  `result.data.update(payload)` mirrors

Live command:
`./bin/ask repo doctor --json --robot`

Result:
pass

After-change summary:
`status: success`; `blocking: false`; `next_command:
./bin/ask repo surface --json --robot`; `next_command_kind:
diagnostic_advisory`; `next_command_blocks_task: false`; top-level
`data.next_command_kind` mirrors `data.doctor.next_command_kind`.

## Validation

| Command | Result | Notes |
| --- | --- | --- |
| `python3 -m pytest Infrastructure/tests/test_ask_golden_path.py -q` | pass | `5 passed`; covers blocker sorting, normal inspection, diagnostic advisory, no-safe-command blocker, and summary rendering. |
| `python3 -m pytest Infrastructure/tests/test_ask_repo_doctor.py -q` | pass | `22 passed`; covers doctor/closeout behavior plus additive field mirror checks. |
| `./bin/ask repo doctor --json --robot` | pass | Doctor emits `next_command_kind: diagnostic_advisory` and `next_command_blocks_task: false` for non-blocking repo-surface debt. |
| `./bin/ask repo surface --json --robot` | pass with warning | Repo surface remains diagnostic debt; `blocking_findings: 4585`. |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` | pass | Eval artifact identity is valid. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` | pass | Eval Linear traceability is valid after adding the work-item contract. |
| `git diff --check -- Infrastructure/scripts/lib/ask/golden_path.py Infrastructure/tests/test_ask_golden_path.py Infrastructure/tests/test_ask_repo_doctor.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md` | pass | No whitespace errors in the phase diff. |
| `./bin/ask repo validate --changed-files Infrastructure/scripts/lib/ask/golden_path.py Infrastructure/tests/test_ask_golden_path.py Infrastructure/tests/test_ask_repo_doctor.py .harness/evals/agent-skills-jsc-246-agent-first-golden-path-eval.md --json --robot` | pass | Required failures `0`; warn-only issues `0`; validation logs `Infrastructure/artifacts/validation/20260508T111638Z`. |

## Blockers

Current closeout blocker:
`sync_required`

Reason:
the live worktree has broad unrelated generated/projection changes outside the
current phase diff.

Smallest recovery step:
complete phase-end review gates for only the `PLAN-JSC246-002` diff, then decide
whether to continue to `PLAN-JSC246-003` or run the projection-refresh lane as a
separate explicitly scoped action.

## Review Gates

| Gate | Status | Notes |
| --- | --- | --- |
| `simplify` | pending | Must review the `PLAN-JSC246-002` diff before commit. |
| `he-fix-bugs` | not triggered yet | Focused phase tests, eval lints, diff check, scoped repo validation, and live doctor probe pass; run only if review finds phase-specific failing evidence. |
| `he-code-review` | pending | Must review public robot-output contract risk before commit. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Evidence |
| --- | --- | --- |
| `JSC-246` | SA1, SA2 | Baseline command snapshots recorded above. |
| `JSC-246` | SA3, SA4, SA5, SA6 | Doctor continuation fields implemented additively and focused tests pass. |

## Next Step

Run phase-end review gates for `PLAN-JSC246-002`.

If review gates pass, continue with `PLAN-JSC246-003` route-state compatibility.
