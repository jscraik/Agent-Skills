# PR Closeout Commander Reference

Read when `pr-green-sweep` needs more than the compact entrypoint: multi-PR action queues, right-validation-surface selection, dirty worktree classification, CLI/plugin evidence routing, CI failure explanation, and closeout ledgers.

## Entrypoint Support

Use this reference for the details that keep the entrypoint compact:

- Bind a heartbeat to the current PR URL, repository, number, head SHA, state,
  and stop rule. Refresh it before action. A merged, closed, superseded, or
  scope-conflicting target is `stale`, `rebound`, or `obsolete`; refresh the
  action queue before repair.
- Treat a check as source evidence only after correlating its observed head SHA,
  event/ref or payload identity, and applicable PR metadata contract. A stale
  PR-template or metadata event is `blocked_pr_metadata`: repair the metadata
  and obtain a fresh event rather than patching source speculatively.
- Record every worker, PM, QA, report, or receipt artifact with producer
  checkout/worktree, validator checkout/worktree, durable path or URL,
  validator command, and visibility result. An artifact invisible to its
  contract-owning validator is `blocked_artifact_context`, not passing proof.
- Redact secrets and preserve unrelated local changes. Use exactly one
  heartbeat, one PR in the mutation lane, and a classified action queue.
- Group materially equivalent findings before patching. A second occurrence, or
  a known steering pattern, needs a validated reusable guardrail (test,
  validator, schema, lint rule, shared helper, or workflow contract) or an
  explicit `blocked_durable_guardrail` reason before merge.
- Fail closed on an unclassified required gate. Stop for safety, authority,
  credentials, destructive action, or hosted-policy failures; otherwise patch
  an in-scope owner or make one deterministic cache/setup/worktree correction
  and rerun only the affected gate. Keep independent blocked lanes explicit.

## Specialist Lanes And Examples

Use the smallest lane set that changes the next safe action: GitHub or `gh` for
live PR truth; CodeRabbit for review threads; CircleCI for failed jobs; autofix
for approved fixes; Context7 for version-sensitive docs; architecture and
simplify for structural or cleanup blockers.

- "Set up a heartbeat to rotate through my open PRs, inspect CodeRabbit and
  CircleCI blockers, fix the real failures, then merge them."
- "PR #42 has CodeRabbit comments and a failing CircleCI job; fix only the
  proven blockers and push a follow-up."
- "After the release PRs merge, prune merged branches and stale worktrees with
  proof that no unique commits will be lost."

Use `[[he-heartbeat]]` for continuation setup, `[[autofix]]` for actionable
CodeRabbit work, `[[context7]]` for external documentation, and
`[[verification-before-completion]]` for latest-head merge and cleanup proof.

## Action Queue Classifier

Return one queue entry per PR:

- `auto_fixable_now`: current evidence points to an in-scope code, docs, contract, or config fix and local write authority is available.
- `needs_merge_conflict_strategy`: branch cannot safely advance without a merge/rebase/conflict decision.
- `blocked_policy_or_approval`: admin merge, force push, destructive cleanup, remote branch deletion, or policy override requires explicit user approval.
- `blocked_external_ci`: failure is in an external service, unavailable logs, transient outage, missing credentials, or remote-only rerun the agent cannot perform.
- `needs_user_decision`: product, release, roadmap, security risk, or ownership choice cannot be inferred from repo evidence.
- `cleanup_only`: PR is merged or closed and only branch/worktree cleanup remains, with merge proof required before deletion.

## Current Project Scope

Default to the current GitHub repository. Do not broaden to all repositories,
owners, orgs, or unrelated open PRs unless the user says `all`, `everything`,
`broad`, names multiple repos/orgs, or explicitly asks for cross-repo rotation.

For exact PR requests, inspect only the named PRs unless the user asks to keep a
wider queue moving. For broad sweeps, preserve the discovered priority order and
state what was not expanded.

## URL-First PR Card

Every surfaced PR entry should start with the canonical URL and include enough
current-state proof to prevent stale action:

~~~text
https://github.com/OWNER/REPO/pull/123 - title
Head: branch @ <sha>
State: mergeable|blocked|dirty|unknown; review threads: open|none|unknown
Checks: required pass/fail/pending with target URLs when available
Local: branch/worktree ownership and dirty-path classification
Next: exact action or blocker
~~~

Never use only `#123` for a PR that needs action, approval, merge, or cleanup.

## Authorization Ladder

Treat permissions as independent. A grant for one rung does not imply later
rungs:

1. discovery and read-only triage
2. heartbeat or cron continuation
3. local implementation and validation
4. push or public PR update
5. CI rerun or CI-fix iteration
6. merge or close
7. admin merge, force push, or policy override
8. remote branch deletion
9. worktree deletion or destructive cleanup
10. release, tag, publish, or registry mutation

Stop at the last granted rung and ask only for the exact next permission when
the current evidence is otherwise ready.

## Decision-Ready Blocker Brief

When user action is needed, provide a prepared decision rather than a rough
status:

- full canonical URL and title
- why the decision is needed now
- latest head SHA, branch, or worktree identity
- completed proof and exact commands/tool outcomes
- exact blocker text, check name, thread id, policy, quota, or missing access
- residual risk and what remains unproven
- recommendation and exact available choices

Do autonomous repair first. Do not ask the user to choose while a PR is stale,
red for a fixable reason, missing local validation, or still has unresolved
review state.

## One-PR-At-A-Time Rotation

Keep only one PR in the mutation lane at a time. Before starting another PR,
the current PR must have one of:

- pushed fix plus refreshed live state
- explicit blocked status with decision-ready brief
- no local edits and no pending validation
- cleanup-only status after merge/close proof

This prevents cross-PR staging mistakes, stale check claims, and ambiguous
dirty-worktree ownership.

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
| [@github] plugin | PR inventory, mergeability, branch protection, review state, and required checks need live GitHub truth. | PR number, head SHA, check names, review state, blocker. |
| `gh` CLI | Plugin access is blocked, a repo wrapper expects `gh`, or local shell evidence is easier to reproduce. | Exact command, redacted output summary, exit status. |
| [@coderabbit] plugin | Review-thread inventory, severity, stale classification, or resolution support is needed. | Thread id, finding class, action taken, stale/blocked reason. |
| [@circleci] plugin | Pipeline, workflow, job, rerun, or log truth is needed from CircleCI. | Workflow/job id, failed step, exact failure text, merge blocker status. |
| CircleCI CLI | Local CircleCI inspection or rerun path is needed. Invoke through the repository-owned `run-auth-backed.sh --env-file ~/.codex/.env` wrapper without printing values. | Exact command, redacted auth state, failed job/log evidence. |
| Context7 skill or CLI | A blocker depends on current external library, API, or CLI docs, especially version-sensitive flags or behavior. | Library id/source basis, retrieval path, inference vs docs-backed conclusion. |

Do not run every CLI by default. Each lane must name the evidence it adds, or it stays unused.

## CI Failure Explainer

For each failing check, return:

- exact check/job name
- exact failure from logs or `blocked` if logs are unavailable
- owner surface: source, test, dependency, CI config, secret/auth, external service, policy gate, or unknown
- local reproduction command when available
- likely fix file or owner
- whether it blocks merge

CircleCI evidence should come from the [@circleci] plugin or the CircleCI CLI
lane. Invoke credentialed CircleCI commands through the repository-owned
`run-auth-backed.sh --env-file ~/.codex/.env` wrapper, but never print secrets
or copy env values into reports.

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
