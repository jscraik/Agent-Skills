# PR Closeout Commander Reference

Read when `pr-green-sweep` needs more than the compact entrypoint: multi-PR action queues, right-validation-surface selection, dirty worktree classification, CLI/plugin evidence routing, CI failure explanation, and closeout ledgers.

## Action Queue Classifier

Return one queue entry per PR:

- `auto_fixable_now`: current evidence points to an in-scope code, docs, contract, or config fix and local write authority is available.
- `needs_merge_conflict_strategy`: branch cannot safely advance without a merge/rebase/conflict decision.
- `blocked_policy_or_approval`: admin merge, force push, destructive cleanup, remote branch deletion, or policy override requires explicit user approval.
- `blocked_external_ci`: failure is in an external service, unavailable logs, transient outage, missing credentials, or remote-only rerun the agent cannot perform.
- `needs_user_decision`: product, release, roadmap, security risk, or ownership choice cannot be inferred from repo evidence.
- `cleanup_only`: PR is merged or closed and only branch/worktree cleanup remains, with merge proof required before deletion.

## Validation Surface Selector

Before claiming a fix is validated, decide the correct surface:

| Changed surface | Validation surface |
| --- | --- |
| Skill package | `./bin/ask skills audit <skill> --level compat --json --robot`; strict/external review only when release-readiness is claimed. |
| Reference doc | Link, reachability, markdown, or no-index whitespace checks; do not run skill audit directly on a standalone reference file. |
| Generated manifest or contract | Owning generator/contract validator; do not hand-edit generated projections to satisfy a report. |
| PR template or repo docs | Repo docs/check gate or markdown/link validator when present. |
| CI config | Local config validator plus affected CI rerun or remote check evidence. |
| App/source code | Smallest relevant package or repo test/lint/typecheck command from repo instructions. |
| Runtime artifact or validation output | Usually do not validate as source; classify as generated evidence or exclude from staging. |

If the correct validator is unavailable, report `validation: blocked` with the missing command, auth, dependency, or external capability.

## Dirty Worktree Classifier

Before committing or pushing, classify every changed or untracked path:

- `intended_source`: required for the active PR fix.
- `generated_artifact`: produced by a tool; stage only when the repo contract says it is source of truth.
- `validation_output`: evidence from checks; usually report, do not stage.
- `temp_reference_material`: local research or bulky inputs; keep ignored or explicitly excluded.
- `unrelated_local_noise`: user or prior-run work; do not modify, stage, or revert.

If a path's ownership is unclear, leave it unstaged and report `needs_user_decision`.

## CLI And Plugin Lane Selector

Use service plugins first for live PR/service truth, then CLIs when local reproduction, repo wrappers, or fallback evidence requires them.

| Lane | Use when | Report |
| --- | --- | --- |
| GitHub plugin | PR inventory, mergeability, branch protection, review state, and required checks need live GitHub truth. | PR number, head SHA, check names, review state, blocker. |
| `gh` CLI | Plugin access is blocked, a repo wrapper expects `gh`, or local shell evidence is easier to reproduce. | Exact command, redacted output summary, exit status. |
| CodeRabbit plugin | Review-thread inventory, severity, stale classification, or resolution support is needed. | Thread id, finding class, action taken, stale/blocked reason. |
| CodeRabbit CLI | Local CodeRabbit evidence is available and useful as a fallback or reproduction path. | Exact command, whether evidence is current/live or cached. |
| CircleCI plugin | Pipeline, workflow, job, rerun, or log truth is needed from CircleCI. | Workflow/job id, failed step, exact failure text, merge blocker status. |
| CircleCI CLI | Local CircleCI inspection or rerun path is needed. Source credentials through `~/.codex/.env` without printing values. | Exact command, redacted auth state, failed job/log evidence. |
| Context7 skill or CLI | A blocker depends on current external library, API, or CLI docs, especially version-sensitive flags or behavior. | Library id/source basis, retrieval path, inference vs docs-backed conclusion. |
| Snyk CLI | Dependency security screening is policy-required, release-required for manifest-backed candidates, or explicitly requested. | Manifest path, severity summary, pass/fail/blocked; do not mix with prompt/security-policy findings. |

Do not run every CLI by default. Each lane must name the evidence it adds, or it stays unused.

## CI Failure Explainer

For each failing check, return:

- exact check/job name
- exact failure from logs or `blocked` if logs are unavailable
- owner surface: source, test, dependency, CI config, secret/auth, external service, policy gate, or unknown
- local reproduction command when available
- likely fix file or owner
- whether it blocks merge

CircleCI evidence should come from the CircleCI plugin/CLI lane. Use `~/.codex/.env` as the expected local environment source for CircleCI credentials, but never print secrets or copy env values into reports.

## Closeout Ledger

End every non-trivial sweep with:

- heartbeat status and stop rule
- action queue outcome
- PRs merged or remaining
- review items fixed, stale, deferred, or blocked
- CI checks fixed, rerun, waiting, or blocked
- validation surface decisions and command outcomes
- dirty paths included or excluded
- branches/worktrees pruned or intentionally skipped
- blockers requiring Jamie decision
