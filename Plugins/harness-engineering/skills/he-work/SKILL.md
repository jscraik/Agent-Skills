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
3. Edit only the approved slice. Preserve unrelated dirty files and report them without staging.
4. Run the focused validation command. If it is unavailable, run the nearest syntax/audit gate and mark behavior validation `blocked`.
5. If validation fails, fix once inside scope and re-run the same command. If it still fails, stop and hand off to `he-code-review` with the exact failure.
6. Stage nothing, commit nothing, push nothing, and update no tracker unless separately authorized.

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
Stop when the selected slice, source artifact, dirty-worktree ownership, validation command, or mutation authority is unclear. Return the smallest recovery step.

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
rollback: "Revert the dashboard summary count change."
git_staging_status: not_staged
blockers: []
next_handoff: he-code-review
~~~

## Assets
Reference `assets/` only for skill packaging and browseability; execution evidence belongs in validation output, PRs, and handoff notes.

## References
- Stage and execution detail: `../../references/skills/he-work/work-execution-contract.md`, `../../references/skills/he-work/execution-modes.md`
- Shared gates: `../../references/stage-context-contract.md`, `../../references/execution-slice-contract.md`, `../../references/subagent-call-contract.md`
- UI or visual proof: `../../references/ui-plan-routing-contract.md`, `../../references/visual-reference-contract.md`
