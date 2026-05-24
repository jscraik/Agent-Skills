---
name: he-work
description: "Executes bounded implementation work from approved specs, plans, issues, or small fixes by editing files, running validation, preserving unrelated work, and recording rollback and handoff evidence. Use when asked to implement, execute a plan, apply changes, or build a scoped feature."
metadata:
  version: 1.0.0
  skill-type: team_automation
---
# Harness Engineering Work

## Philosophy
Ship the smallest approved slice and leave proof: changed files, exact validation, rollback, blockers, and next handoff.

## When to Use
Use when execution is already approved by a plan/spec/issue, or for a tiny low-risk fix: at most two files, no auth/security/data/CI/dependency/public API/tool/skill/plugin change, no external side effects, and a known validation command.

## Inputs
Approved plan/spec/issue, selected slice, branch, dirty state, PR/Linear context, validation command, and any explicit staging or tracker authority.

## Outputs
Return the YAML shape below. Use `blocked_reason` instead of guessing when scope, authority, validation, or ownership is unclear.

## Procedure
1. Check state before editing:
   `git status --short`, `git branch --show-current`, and `test -f <approved-plan-or-spec>`.
2. Confirm the approved slice names the behavior, allowed files or smallest file set, validation command, and rollback. If not, stop with `blocked_reason`.
3. Confirm the approved source includes strict boundary fields from
   `../../references/spec-plan-runtime-boundary-contract.md`: requested depth,
   execution boundary, proof boundary, runtime state/resumption key, live-state
   freshness, external mutation boundary, `coding_lens`, and `testing_lens`.
   If any required field is absent, stale, or inferred only from chat, stop
   before editing with `blocked_authority` or `blocked_source_of_truth`.
4. If the slice touches repo memory, artifacts, goal boards, Project Brain,
   Chronicle, Local Memory, vault sync, or brownfield adoption, apply
   `../../references/codex-native-memory-baseline.md` before editing.
5. Edit only the approved slice. Preserve unrelated dirty files and report them without staging.
6. Run the focused validation command. If it is unavailable, run the nearest syntax/audit gate and mark behavior validation `blocked`.
7. If validation fails, fix once inside scope and re-run the same command. If it still fails, stop and hand off to `he-code-review` with the exact failure.
8. Stage nothing, commit nothing, push nothing, and update no tracker unless separately authorized.

## Validation
Fail fast. Record every gate as `pass`, `fail`, or `blocked` with exact command text. Useful gates:

~~~bash
git status --short
test -f <approved-plan-or-spec>
rg -n "validation|rollback|scope|files_allowed" <approved-plan-or-spec>
python3 -m py_compile <python-file>
python3 -m pytest <focused-test> -q
./bin/ask skills audit <skill-path> --level strict --json --robot
~~~

## Failure Mode
Stop when the selected slice, source artifact, strict boundary fields, runtime
state, dirty-worktree ownership, validation command, or mutation authority is
unclear. Return the blocker class and smallest recovery step.

## Execution Boundaries
Mutate only files in the approved implementation slice. Do not stage, commit, push, resolve review threads, close trackers, or perform external mutation without explicit approval.

## Constraints
Redact secrets, preserve user edits, and do not treat generated projections as canonical source.

## Gotchas
- Green CI does not prove the touched behavior unless the focused gate covers it.
- A tempting adjacent fix is out of scope unless the approved slice includes it.

## Anti-Patterns
Editing before state checks, expanding scope, staging unrelated files, or claiming completion without exact validation evidence.

## Examples
- When the user asks, "Implement only U1 from `.harness/plan/JSC-246-dashboard.md`," inspect the plan, edit only named files, then run the focused pytest gate.
- When the user asks, "Tiny fix: correct the Linear field name in one template," inspect that template, make the one-file edit, and run its focused test.

## Output Template
~~~yaml
schema_version: 1
selected_stage: he-work
scope: "U1 dashboard summary count only"
changed_files:
  - Infrastructure/scripts/lib/ask/skill_review_dashboard.py
validation:
  - command: "python3 -m pytest Infrastructure/tests/test_ask_evals_command.py -q"
    outcome: pass
codex_native_memory_status: not_applicable
authority_scope_boundary:
  requested_depth: approved_slice
  approved_execution_boundary: ".harness/plan/JSC-246-dashboard.md PU-001"
runtime_persistence:
  runtime_state: "PU-001 ready for validation"
  resumption_key: ".harness/plan/JSC-246-dashboard.md#PU-001"
  runtime_invocation_receipt: "not_applicable: local bounded execution"
  artifact_chain_key: "jsc-246-dashboard"
coding_lens: "allowed files checked; no public API or data contract change"
testing_lens: "observable behavior proof covers SA-001 with focused pytest"
rollback: "Revert the dashboard summary count change."
git_staging_status: not_staged
blockers: []
next_handoff: he-code-review
~~~

## Assets
Reference `assets/` only for skill packaging and browseability; execution evidence belongs in validation output, PRs, and handoff notes.

## Stage Arc Boundary
Before artifact writes, mutation, scheduling, handoff, or closure claims, apply
`../../references/stage-arc-boundary-contract.md`. Structured outputs and
handoffs must include `stage_arc_boundary` with `left_arc`, `active_arc`,
`right_arc`, `coding_lens`, and `testing_lens`; block when left evidence is
stale, active mutation exceeds authority, right-side proof is missing, or a
required persona lens is not covered.

## References
- Stage and execution detail: `../../references/skills/he-work/work-execution-contract.md`, `../../references/skills/he-work/execution-modes.md`
- Shared gates: `../../references/stage-context-contract.md`, `../../references/execution-slice-contract.md`, `../../references/subagent-call-contract.md`
- Strict boundaries and persona lenses: `../../references/spec-plan-runtime-boundary-contract.md`
- Approval flow: `../shared/references/approval-flow.md`
- UI or visual proof: `../../references/ui-plan-routing-contract.md`, `../../references/visual-reference-contract.md`
- Deferred context index: `../../references/deferred-context-index.md`
- Codex-native memory baseline: `../../references/codex-native-memory-baseline.md`
- Cookbook-derived execution-plan and iterative repair lenses: `../../../../Infrastructure/references/openai-cookbook-expert-lens-pack.md`, `../../../../Infrastructure/references/openai-cookbook-skill-expertise-map.md`
- Software-literature execution lenses: `../../../../Infrastructure/references/software-literature-expert-lens-pack.md`, `../../../../Infrastructure/references/software-literature-skill-expertise-map.md`
- Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
