---
name: greploop
description: Iteratively remediate one GitHub PR against Greptile review feedback until the signal stabilizes or stop conditions are hit. Use when the user wants a bounded Greptile fix loop, not a one-shot readiness decision or generic GitHub workflow.
metadata:
  skill-type: code_quality_review

---

# Greploop

Run a bounded Greptile remediation loop for a single PR while keeping comment, commit, push, and review-trigger mutations behind explicit approval.

Imported from `greptileai/skills` on 2026-03-23; see [`artifacts/greploop-import-2026-03-23.txt`](../../../artifacts/greploop-import-2026-03-23.txt) for provenance.

## Philosophy
- Treat Greptile remediation as a bounded loop with explicit stop conditions, not an unending comment chase.
- Keep approvals explicit for any mutation that changes PR state, review state, or repository history.
- Prefer stable signal and clear handoff over squeezing every last non-blocking comment out of the queue.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Gotchas](#gotchas)

## Standards snapshot
- Treat `greploop` as an iterative PR-remediation lane, not a generic GitHub workflow or a one-shot readiness check.
- Keep the loop bounded: use explicit stop conditions and a max-iteration cap.
- Separate read-only analysis from mutating actions. Commenting, resolving threads, committing, pushing, and re-triggering review all require explicit approval in this repo.
- Preserve the upstream loop doctrine in `references/` rather than flattening it into a weaker summary.
- Use `check-pr` for readiness classification and setup blockers before a remediation loop when the repo state is still unclear.

## When to use
- The user wants a PR iteratively improved against Greptile review feedback.
- A Greptile-reviewed PR needs repeated fix, push, and re-review cycles until the feedback stabilizes.
- The user wants a bounded loop that tracks confidence score, unresolved comments, and iteration count.
- The repo already has Greptile installed or the user wants to run the loop once setup is verified.

## When not to use
- The user only wants a one-shot readiness or blocker summary; use [`check-pr`](/Users/jamiecraik/dev/Agent-Skills/github/greptile/check-pr/SKILL.md).
- The user mainly wants GitHub lifecycle operations like PR prep, merge, or comment handling outside a Greptile loop; use [`gh-workflow`](/Users/jamiecraik/dev/Agent-Skills/github/gh-workflow/SKILL.md).
- The task is generic code review without Greptile as the main feedback source.
- The user has not approved mutating PR state and only wants an audit of what the loop would do.

## Required inputs
- PR number or current-branch PR context.
- Repo context with `gh` auth available.
- Greptile-installed repo context or explicit confirmation that setup should be checked first.
- User-approved mutation posture:
  - audit only
  - propose fixes
  - approved fix loop with commit/push/comment steps

## Deliverables
- Resolved PR target and current loop mode.
- Current Greptile review state:
  - latest score if available
  - unresolved comment count
  - iteration count
- Actionable versus informational Greptile findings.
- Optional fix batch with verification evidence when approved.
- Clear stop reason:
  - perfect review reached
  - no more actionable comments
  - approval boundary reached
  - max iterations reached
  - blocked by setup or failing checks

## Failure mode
- If PR or repo context cannot be resolved, stop and ask for the smallest missing identifier.
- If Greptile is not installed or setup is unclear, stop and route to `check-pr`-style setup verification before looping.
- If mutation approval is missing, stop after the read-only loop analysis and present the exact next action.
- If the loop hits the iteration cap without convergence, stop and summarize the remaining blockers instead of continuing indefinitely.

## Output contract
Use this shape when structured output is requested:

```json
{
  "schema_version": 1,
  "pr_ref": "string",
  "loop_mode": "audit-only|propose-fixes|approved-fix-loop",
  "iteration_count": 0,
  "confidence_score": "string|null",
  "unresolved_comments": 0,
  "stop_reason": "string",
  "next_step": "string"
}
```

## Workflow
1. Resolve the PR from user input or the current branch.
2. Verify prerequisites:
   - `gh` auth
   - repo context
   - Greptile setup/install confidence
   - mutation approval level
3. Collect the current review baseline:
   - latest Greptile review summary
   - unresolved Greptile inline comments
   - current status checks
4. Choose the loop lane:
   - `audit-only` when no mutation approval exists
   - `propose-fixes` when the user wants a concrete remediation plan before any mutations
   - `approved-fix-loop` when comment, commit, push, and review re-trigger steps are approved
5. For each iteration:
   - classify comments as actionable or informational
   - fix only approved actionable items
   - verify the changed behavior
   - resolve addressed threads only when approved and supported by evidence
   - comment and/or push only when approved
   - request or wait for the next Greptile review cycle
6. Stop on the first terminal condition:
   - score target reached and no unresolved comments remain
   - no further actionable items remain
   - max iterations reached
   - user approval boundary blocks the next mutation
   - setup or CI blocker prevents a trustworthy next iteration
7. Return the current state, stop reason, and smallest safe next action.

If you need the original upstream loop semantics, comment trigger wording, or GraphQL thread-resolution mechanics, open:
- `references/upstream-greploop.md`
- `references/graphql-queries.md`

## Validation
- Verify the PR is resolved before analysis begins.
- Verify each claimed fix is tied to a specific Greptile comment or review signal.
- Verify no comment, commit, push, or thread resolution happens without explicit approval.
- Verify the loop stops at the configured cap instead of running indefinitely.
- Verify the final summary names the actual stop reason and next step.

## Constraints
- Redact secrets, tokens, credentials, and sensitive review data.
- Do not auto-commit, auto-push, or auto-comment just because the upstream skill did.
- Do not treat Greptile comments as infallible; classify false positives or informational comments explicitly.
- Do not resolve review threads without evidence that the underlying concern was addressed or intentionally dismissed with rationale.

## Anti-patterns
- Using `greploop` when `check-pr` is enough.
- Starting a fix loop before setup, check state, or mutation approval is clear.
- Running an unbounded review-fix-comment loop.
- Pushing speculative fixes only to chase a score without engineering judgment.

## Examples
- "Run greploop on PR 482, but stay audit-only and tell me what the first iteration would do."
- "Use greploop on my current branch PR and propose the smallest fix batch before touching GitHub."
- "We have approval to iterate on this Greptile-reviewed PR until the remaining actionable comments are gone."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- `references/task-profile.json`
- `references/upstream-greploop.md`
- `references/graphql-queries.md`

## See Also

| Skill | When to use together |
|---|---|
| [[check-pr]] | Verify setup and classify readiness before starting the loop |
| [[gh-workflow]] | Handle PR lifecycle actions outside the bounded Greptile loop |
| [[gh-fix-ci]] | Investigate failing CI if Greptile remediation exposes check failures |

**Topic map:** [[backend-platform]]

## Gotchas
- Upstream `greploop` assumes it can commit, push, and comment automatically.
  Local adaptation: keep those actions behind explicit approval.
  Check: loop mode clearly states whether the run is read-only or mutating.
- Chasing a perfect Greptile score can hide diminishing returns.
  Do instead: stop when remaining comments are informational, false-positive, or outside the approved scope.
  Check: final summary distinguishes actionable from non-actionable residue.
