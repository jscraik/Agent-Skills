---
name: resolve-pr-parallel
description: Resolve multiple unresolved GitHub PR review threads in parallel by applying fixes, responding, and closing verified threads. Use when the user wants a broad PR-comment cleanup sweep, not readiness classification or one-off comment handling.
metadata:
  skill-type: ci_cd_deployment
---

# Resolve PR Parallel

Use a focused GitHub remediation workflow for unresolved PR review threads. Preserve the imported compound-engineering flow, but keep routing tight so readiness review and general GitHub lifecycle work still go to their narrower owners.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow)
- [Parallel execution contract](#parallel-execution-contract)
- [Routing map](#routing-map)
- [Upstream preservation](#upstream-preservation)
- [Validation](#validation)
- [Constraints](#constraints)
- [Examples](#examples)
- [Remember](#remember)
- [Gotchas](#gotchas)
- [Failure mode](#failure-mode)

## Standards snapshot (March 2026)
- Use GitHub CLI and GraphQL as the source of truth for unresolved review threads and resolution status.
- Separate readiness review from remediation. Audit first, fix second.
- Keep CI-provider strategy separate from review-thread remediation. This skill verifies thread state and requested fixes; CircleCI workflow design or CircleCI-specific diagnosis belongs to [`circleci`](/utilities/circleci/SKILL.md).
- Do not resolve a review thread until the requested change or reviewer reply is actually ready.
- Keep parallel fanout bounded. Run at most 4 remediation workers at a time unless the user explicitly wants a different policy.
- Re-fetch unresolved, non-outdated threads after push before claiming completion.

## When to use
- Address all unresolved PR review threads on the current PR or a specified PR.
- Batch-fix review feedback after a review round and then resolve the completed threads on GitHub.
- Clear remaining review comments when the user explicitly wants parallel remediation or the thread count makes batching worthwhile.
- Handle mixed review feedback where some threads need code changes and others need reviewer replies, while keeping one verified completion pass.

## When not to use
- Do not use for PR readiness, policy, or merge-blocker review. Use [`gh-workflow`](/github/gh-workflow/SKILL.md) in `pr_readiness` mode.
- Do not use for broad GitHub lifecycle work like PR creation, review requests, or server-side merge. Use [`gh-workflow`](/github/gh-workflow/SKILL.md).
- Do not use for CI-only diagnosis. Use [`github:gh-fix-ci`](/plugins/cache/openai-curated/github/f78e3ad49297672a905eb7afb6aa0cef34edc79e/skills/gh-fix-ci/SKILL.md).
- Do not use for CircleCI workflow design, migration, policy, or CircleCI-specific pipeline diagnosis. Use [`circleci`](/utilities/circleci/SKILL.md).
- Do not use for a generic code review or technical critique with no remediation ask. Use [`ce-review`](/product/ops/ce-review/SKILL.md) or [`ce-technical-review`](/product/ops/ce-technical-review/SKILL.md).
- Do not use when the user only wants to address one or two specifically named comments manually. Use `gh-workflow` in `pr_review_comments` mode instead.

## Required inputs
- PR number, PR URL, or current-branch PR context.
- Repository context when auto-detection cannot resolve it safely.
- Permission to edit code, commit, push, and resolve threads when that intent is not already implied.
- Verification expectations when the user already knows the required tests or checks.

## Deliverables
- Resolved repo and PR context with the starting unresolved-thread inventory.
- A per-thread execution plan grouped into bounded batches.
- Fixes or reviewer replies for each unresolved thread.
- Commit, push, and GitHub thread-resolution evidence.
- A final verification result that shows either zero unresolved non-outdated threads or a precise blocked-state summary.
- If requested, a structured status report matching [`references/contract.yaml`](/github/resolve-pr-parallel/references/contract.yaml) with `schema_version: 1`.

## Workflow
1. **Resolve the PR context and baseline safety state.**
   - Confirm `gh` auth, repo context, current git status, and the target PR before planning work.
   - If the working tree is dirty in a way that would interfere with PR remediation, stop and surface the real state.
2. **Fetch and Summarize unresolved review threads.**
   - Use `scripts/get-pr-comments` to collect unresolved, non-outdated review threads.
   - **Interactive Status Report:** Present a numbered list of open comments to the user. For resolved threads, summarize as a single line with a ✅.
   - **Request Guidance:** Ask the user which threads they would like to address first or if any should be skipped. Do not begin batch remediation until the intent is confirmed.
3. **Classify the thread work.**
   - Split threads into code changes, reviewer questions, style/convention fixes, test additions, and blocked items.
   - Keep question-only threads separate so they return substantive reply text instead of fake code churn.
4. **Execute remediation in bounded parallel.**
   - For 1-4 unresolved items, direct parallel remediation is fine.
   - For 5+ unresolved items, run batches of at most 4 and keep parent-context summaries short.
   - Prefer the `pr-comment-resolver` agent when a worker-per-thread model is available; otherwise run the same checklist serially.
   - For very large runs, use a per-run scratch directory such as `.context/resolve-pr-parallel/<run-id>/` and keep only compact per-thread artifacts there.
5. Commit and push only completed work.
   - Commit the resolved batch with a clear feedback-oriented message.
   - Push before resolving GitHub threads so GitHub state reflects the actual branch state.
6. Resolve completed threads.
   - Use [`scripts/resolve-pr-thread`](/github/resolve-pr-parallel/scripts/resolve-pr-thread) for single-thread resolution.
   - Use [`scripts/resolve-pr-threads-batch`](/github/resolve-pr-parallel/scripts/resolve-pr-threads-batch) when multiple threads are ready at once.
   - Resolve only the threads whose requested change or reply is complete and verified.
7. Verify the final state.
   - Re-run [`scripts/get-pr-comments`](/github/resolve-pr-parallel/scripts/get-pr-comments) after push and thread resolution.
   - Completion means an empty array `[]` for unresolved, non-outdated threads, or an explicit blocked-state explanation for anything left open.

## Parallel execution contract
- Each remediation worker should return:
  - thread handled
  - disposition: `fixed | replied | blocked | skipped`
  - files changed
  - tests run or skipped
  - any blocker that still needs human attention
  - reply text when the thread is question-only
- The parent should synthesize the worker outputs, make the smallest safe commit set, and resolve only the completed threads.
- If the user did not actually ask for parallel delegation or the platform cannot support it safely, process the same per-thread checklist serially and keep the output contract unchanged.

## Routing map
- Read [`references/overlap-matrix.md`](/github/resolve-pr-parallel/references/overlap-matrix.md) before widening this skill's trigger wording.
- Use [`gh-workflow`](/github/gh-workflow/SKILL.md) in `pr_readiness` mode when the user wants to know whether a PR is ready, not to fix it.
- Use [`gh-workflow`](/github/gh-workflow/SKILL.md) when the work is a selected-comment response, broader PR lifecycle task, or one-mode GitHub operation.
- Use [`circleci`](/utilities/circleci/SKILL.md) when the blocker is CircleCI workflow design, migration, policy, or provider-specific diagnosis rather than GitHub thread remediation.
- Use [`ce-review`](/product/ops/ce-review/SKILL.md) or [`ce-technical-review`](/product/ops/ce-technical-review/SKILL.md) when the user wants critique rather than remediation.

## Upstream preservation
- The imported compound-engineering source is preserved in [`references/upstream-resolve-pr-parallel.md`](/github/resolve-pr-parallel/references/upstream-resolve-pr-parallel.md).
- The local install keeps the same core flow:
  - fetch unresolved review threads
  - plan per-thread work
  - remediate in parallel when appropriate
  - commit, push, resolve threads
  - verify no unresolved non-outdated threads remain
- The local adaptation adds tighter routing, Codex-native delegation guidance, pagination-safe helper scripts, and explicit blocked states.

## Validation
- Verify `gh` auth, repo context, PR context, and git state before changing code.
- Verify thread fetch results are unresolved and non-outdated before creating tasks.
- Verify each resolved thread maps to actual fix or reply evidence.
- Verify push succeeded before resolving GitHub threads.
- Verify the final fetch returns `[]` or return a blocked summary for anything left open.
- Fail fast at the first broken gate.

## Constraints
- Do not resolve review threads blindly.
- Do not treat outdated threads as fresh work unless the user explicitly asks for historical cleanup.
- Do not force-push unless the user explicitly asks for it.
- Do not invent reviewer replies; if a question needs human or product judgment, keep the thread open and surface the blocker.
- Redact secrets, tokens, credentials, and sensitive repository data by default.

## Examples
- "Resolve all remaining PR comments on this branch in parallel and tell me what still needs human attention."
- "Clear the unresolved review threads on PR 482, push the fixes, and verify GitHub shows nothing left."
- "Batch-handle the review feedback on my current PR and only resolve threads after the fixes are pushed."
- "Use resolve-pr-parallel for the current PR, but keep question-only threads open unless you have a real reply."

## Remember
- Review feedback is not done until GitHub thread state and branch state agree.
- A question-only thread still needs a substantive answer, not just a resolved badge.

## Gotchas
- Current-branch PR auto-detection can fail outside a repo, on detached HEAD, or when no PR exists.
- Large PRs can exceed one-page thread fetches; use the local helper script rather than one-shot GraphQL snippets.
- If the thread count is small and selected by the user, this skill can be overkill; route to `gh-workflow` instead.
- CircleCI can be the incoming pipeline without changing this skill's core job. It only changes where CI-provider-specific diagnosis and workflow guidance should route.

## Failure mode
- If `gh` auth, repo context, or PR discovery fails, stop with the exact remediation.
- If the working tree is dirty in a conflicting way, stop and surface the actual state before touching review threads.
- If unresolved threads remain after remediation, return an explicit blocked summary instead of implying success.

## See Also
| Skill | When to use |
|---|---|
| [[gh-workflow]] | Handle a single-threaded PR lifecycle or smaller review loop without fan-out |
| `github:gh-fix-ci` (plugin) | Debug failing Actions checks discovered while resolving review feedback |
| [[systematic-debugging]] | Diagnose a stubborn defect before continuing to resolve review feedback |

**Topic map:** [[backend-platform]]
