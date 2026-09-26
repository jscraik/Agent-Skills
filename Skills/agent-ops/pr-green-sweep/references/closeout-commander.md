# PR Closeout Commander Reference

Read when `pr-green-sweep` needs more than the compact entrypoint: multi-PR action queues, right-validation-surface selection, dirty worktree classification, CLI/plugin evidence routing, CI failure explanation, and closeout ledgers.

For foreground review fixes, start with [Review Findings](review-findings.md).
The entrypoint mode rules apply throughout: heartbeat requirements govern
scheduled continuation only; merge and cleanup require explicit scope.

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
- Redact secrets and preserve unrelated local changes. For requested monitoring use exactly one
  heartbeat; keep one PR in the mutation lane, and a classified action queue.
- Group materially equivalent findings before patching. Recurrence across three independent tasks, or
  an explicitly selected steering-uptake pattern, needs a validated reusable guardrail (test,
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

Preserve standing grants that cover multiple rungs; do not ask again for the
same authorized operation. Stop at the last granted rung and ask only for the exact next permission when
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
| CircleCI CLI | Local CircleCI inspection or rerun path is needed. Discover and invoke the host-configured auth-backed wrapper with `~/.codex/.env`, without printing values. | Exact command, redacted auth state, failed job/log evidence. |
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
lane. Invoke credentialed CircleCI commands through
the host-configured auth-backed wrapper with `~/.codex/.env`; discover the
wrapper from the active Codex environment, never invoke an unqualified wrapper
or `op` directly, and never print secrets or copy env values into reports.

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

## Green PR Closeout

Use `green-closeout` for "review green pull requests, resolve review threads,
merge them, and reconcile the local branches." This is foreground work unless
the user also requests scheduled continuation. Preserve the named authority
through all applicable gates; ask only for a missing action class or material
scope decision. Do not manufacture code edits when current evidence already
addresses a finding.

1. Build the scoped PR queue from fresh hosted state. Treat displayed green
   counts as candidates for review, not merge clearance or a fixed check quota.
2. Read the current diff and all review sources. Confirm each finding and
   reconcile exact thread ids using `review-findings.md`, including live
   read-back. A bot task marked ready or delivery-blocked does not prove its
   fix reached the PR; check published commits and avoid competing writers.
3. Verify current-head required checks, qualifying independent reviews under
   repo policy, no unresolved threads, no conflicts, and the applicable receipt.
   If the head changes, refresh affected evidence before proceeding.
4. Merge only the verified head using the authorized strategy and the owning
   repository's guarded command with an enforced expected-head SHA condition.
   A separate precheck is not atomic protection: if the merge interface cannot
   enforce the verified SHA, block the merge. Read back the merged state, merge
   commit, and target base;
   a clicked confirmation or a submitted request is not a successful merge.
5. Delete the remote feature branch only when that action is authorized and
   an atomic compare-and-delete enforces the captured, verified branch SHA for
   the merged candidate. Never follow a ref precheck with an unconditional
   delete: a writer could advance it between those operations. If the ref moves
   or the interface cannot enforce that condition, retain the branch and report
   why. Confirm the deletion, then complete the separate local reconciliation
   below.

## Candidate-Bound Local Review

For a committed PR diff, materialize the latest hosted head in an owned checkout
(isolate it if needed; preserve unrelated work). Assert local `HEAD` equals that
exact SHA. Resolve the comparison ref and assert it equals the freshly verified
hosted base SHA; a stale local target branch is not sufficient. Pin that resolved
commit for `codex review --base <verified-base-sha>` and verify the comparison
matches the hosted PR diff. Record the checkout, candidate SHA, actual comparison
SHA, and review output together. `--base` selects the comparison base, not the
candidate. Recheck both hosted head and base afterward; changes invalidate
comparison-bound evidence. An empty diff from main,
another checkout, or an empty uncommitted diff does not prove PR review coverage.

## Local Branch Reconciliation

Reconciliation starts with accounting and safe synchronization. Branch or
worktree deletion requires matching cleanup authority and proof.

1. Inventory each scoped repository's status, branches, upstreams, worktrees,
   active writers, and unique commits. Record current refs before mutation.
   Fetch current remote refs through the permitted repo workflow; a missing
   upstream alone does not prove a branch is disposable.
2. Compare each local branch with its current upstream and classify it as
   equal, behind-only, ahead-only, divergent, gone, or unknown. Preserve dirty,
   active, ahead-only, divergent, and unknown-owned checkouts. Do not reset,
   rebase, stash, clean, or switch them merely because remote `main` advanced.
3. Fast-forward a clean, owned, behind-only checkout only within granted scope
   and repo policy. For a branch checked out elsewhere, use its owning
   worktree and verify it is idle and clean first; do not move its ref from
   another checkout. A dirty primary checkout can remain untouched while an
   independent clean checkout is safely updated.
4. Before deleting a local branch or worktree, require verified merge or
   abandonment, exact branch ownership, no unique work needing retention,
   no dirty changes or active writer, and no runtime links into a removed
   worktree. Squash or rebase merges need content-equivalence proof when
   ancestry alone does not establish containment; ambiguous cases are kept.
5. Re-read status, refs, upstream comparison, and worktree inventory after each
   change. Report before/after SHAs and `updated`, `already_current`, `retained`,
   or `blocked` with a reason. Report remote deletion separately from local
   branch/worktree deletion. A retained divergent branch is accounted for,
   not synchronized; leave its next decision visible.

### Recorded Workflow Basis

The September 13, 2026 recording shows Websites PR #41 and Skills Foundry
PRs #23 and #24 reaching hosted merged states. Displayed check totals were
19, 7, and 7; they are historical observations, not policy thresholds.
Review-conversation activity preceded the final Foundry merge. The supplied
summary records remote branch removal, while the event stream also contains
task commentary and draft reconciliation text. Neither commentary nor a draft
proves local branch updates. The reconciliation procedure above requires fresh
Git evidence; it is not a claim that those historical local updates completed.
Private event streams and unrelated task content are not packaged.

## Output Contract

For a non-trivial response, emit `heartbeat_status` first. Then emit
`schema_version: 1`, selected mode, a finding ledger (source URL/id, author,
observed head, affected path, disposition, reason, fix and proof), and an
action queue
(`auto_fixable_now`, `needs_merge_conflict_strategy`, `blocked_policy_or_approval`,
`blocked_external_ci`, `blocked_pr_metadata`, `blocked_artifact_context`,
`needs_user_decision`, `cleanup_only`), and heartbeat, dirty-worktree,
validation, receipt, merge, cleanup, and blocker ledgers. Group repeats in
`recurring_finding_classes` with
`finding_class_id`, `fingerprint_sha256`, `normalized_invariant`, occurrences,
root cause, guardrail, and merge eligibility.

Include `local_branch_reconciliation_ledger` for the selected reconciliation
lane, with before/after refs, classification, action, result, and retained work.
