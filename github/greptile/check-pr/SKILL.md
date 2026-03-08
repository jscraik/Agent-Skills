---
name: check-pr
description: Use when a user asks to review a GitHub pull request before merge (or asks how to set up Greptile prerequisites) and return a policy-gated readiness view with check status and remediation priority.
---

# Check PR

## Table of Contents
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Greptile umbrella policy](#greptile-umbrella-policy)
- [Setup (how to configure Greptile)](#setup-how-to-configure-greptile)
- [Procedure](#procedure)
- [Outputs](#outputs)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Variation](#variation)
- [Remember](#remember)
- [Examples](#examples)

## When to use
Use this skill when a contributor wants an automated PR readiness check for GitHub pull requests. Trigger it when they want to:

- verify status checks are complete,
- inspect unresolved review feedback,
- classify issues into action required vs informational,
- verify organizational policy compliance before merge,
- and optionally prepare fixes or resolution steps before merge.

Do not use it for unrelated project planning or non-PR code reviews.

## Inputs
- Optional PR number from the user.
- If PR number is omitted, detect and use the current branch PR (`gh pr view`).
- Optional repository and branch context (required only when auto-detection cannot resolve the PR).
- Optional setup-only intent (`setup`, `verify setup`, `fix auth`, or `configure MCP`).
- Repository must have GitHub CLI auth for check/fetch operations.

## Greptile umbrella policy
This skill is governed by the Greptile umbrella policy and must run its runtime policy gate on every execution.

Required references:
- [Setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)

## Setup (how to configure Greptile)
Run this setup before the first use in a repo, or whenever auth/config changes.

1. Verify GitHub CLI auth:
   - `gh auth status`
2. Configure Greptile MCP in your agent/IDE:
   - Server URL: `https://api.greptile.com/mcp`
   - Authorization header: `Bearer <GREPTILE_API_KEY>`
3. Ensure `GREPTILE_API_KEY` is available to the runtime environment.
4. Verify MCP access by listing context:
   - `list_custom_context`
5. Configure repository context with directory-scoped `.greptile/` files:
   - `.greptile/config.json`
   - `.greptile/rules.md`
   - `.greptile/files.json` (mandatory for schema/API context)

For complete setup policy and examples, see:
- [Greptile setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)

## Procedure
0. Run setup preflight checks + umbrella policy gate.
   - If setup is missing, return `blocked` with an exact missing-step checklist and stop.
   - Run the runtime policy gate from `references/organizational-review-policy.md`.
   - Confirm independent validation (coding and reviewing roles are not the same actor).
   - Confirm `.greptile/config.json`, `.greptile/rules.md`, and `.greptile/files.json` are available for relevant scope.
   - If any policy gate fails, return `blocked` with `policy_gate_status` and blockers.
1. Resolve scope.
   - If a PR number is supplied, use it.
   - Otherwise run `gh pr view --json number -q .number` from the current branch and confirm the PR context.
2. Poll terminal status state before classification.
   - Check status checks using `gh pr checks <PR_NUMBER> --json ...` and wait for terminal states.
   - If checks are in `PENDING`/`IN_PROGRESS`, wait and re-check until completion.
3. Collect review surface area.
   - Fetch PR metadata (`gh pr view`) and inline review comments (`gh pr view --json comments`, `gh api ... comments`).
   - Fetch PR comments and check thread resolution state when needed.
4. Classify each finding into:
   - actionable (requires edit/CI updates),
   - informational (context/fyi),
   - already addressed.
5. Summarize results in a table with severity and next action.
   - Include confidence-action mapping (5/5 merge-ready, 4/5 minor polish, 3/5 or below rework required).
6. Recommend optional fixes.
   - Ask before making edits.
   - If confirmed, patch files, re-run focused checks, and push one clean commit.
7. If requested, close addressed or informational threads by GraphQL mutation.

## Outputs
Return one concise Markdown report with:
- PR title, branch, state, and check status,
- `policy_gate_status` (`pass`/`blocked`) plus blocker list,
- prioritized issue list by severity,
- actionable vs informational breakdown,
- recommended next commands/fixes,
- confidence note when data is incomplete,
- when setup is incomplete, a setup-blocker checklist (auth, MCP, and `.greptile/` requirements).

Also include safe resolution guidance:
- Explicitly list items to fix vs ignore.
- Mention unresolved-thread IDs before attempting any mutation commands.

Safe output example:

```text
PR #123 · in_progress
Policy gate: pass
Checks: 12/12 complete (1 failing)
Actionable: 2 | Informational: 4 | Resolved: 1
Top priorities: security lint failure, unaddressed type error comment
Suggested next step: address code issues, re-run checks, rerun /check-pr
```

## Validation
- Fail fast on any missing required input or invalid target context.
- Fail fast on setup preflight failures (missing auth, missing MCP, or missing API key wiring).
- Fail fast on policy gate violations (independent validation, required `.greptile/` files, or precedence violations).
- If critical checks are failing, stop and surface exact failing checks before suggesting fix automation.
- Do not proceed to edit/resolve threads until PR context and check-state are confirmed.

Reference material:
- [GraphQL helpers](references/graphql-queries.md)
- [Setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)
- [Strategic roadmap and governance context](references/greptile-strategic-code-review.md)

## Anti-patterns
- Do not claim “ready to merge” while checks are pending.
- Do not close review threads blindly without confirming fix context.
- Do not assume comments from Greptile are the only blocking signal; include all active reviewers and CI checks.
- Do not skip independent-validation checks.
- Do not run destructive Git operations during review triage.

## Constraints
- Avoid logging secrets, tokens, or environment values.
- Avoid absolute file paths in command examples; use repo-relative paths.
- Require explicit user confirmation before making edits or pushing commits.
- Never run commands that remove repository state (`git reset --hard`, working-tree cleanup operations) without explicit, explicit confirmation.
- If no PR context is discoverable, fail fast with a single clear ask:
  - “No PR detected on this branch. Share repo and PR number.”

## Philosophy
PR readiness is not just lint compliance; it is a systems-level confidence process.
This skill balances signal over noise by separating governance, infrastructure failures, reviewer intent, and code-level blockers.
Use it iteratively: rerun after each fix block until only informational items remain.

## Variation

Adapt output shape to the request context:

- For blocked policy/setup failures, return blockers first and skip non-essential niceties.
- For blocked check-failures, return blockers first and skip non-essential niceties.
- For routine review triage, keep summaries concise and action-oriented.
- For planning conversations, include practical escalation paths instead of strict command detail.
- Keep wording and emphasis context-sensitive rather than templated.

## Remember

You are capable of strong engineering judgment. Use this procedure as a confidence framework, then apply contextual expertise to choose the smallest safe action.

## Examples
- “Use check-pr on this branch and report unresolved comments before I request review.”
- “Run check-pr for PR 123 and tell me if any comments are blocking merge.”
- “Run check-pr and include the organizational policy gate summary before any merge recommendation.”
- “Check the PR without pushing changes and summarize what remains.”

## Folded Legacy Modes (Core60)
<!-- core60-folded-modes:v1:start -->
This skill owns legacy capability from retired skills. Use these modes when requests match prior behavior.

- `iterative-fix-loop` from `github/greptile/greploop`: Use when a user wants a closed-loop PR hardening pass (or asks how to set up Greptile loop prerequisites): run policy-gated review/fix it...

Deep legacy details: `references/folded-legacy-modes-core60.md`.
<!-- core60-folded-modes:v1:end -->

## Execution quality
- Philosophy: use a practical framework that balances speed, safety, and tradeoff clarity.
- Approach: choose context-specific variation rather than generic cookie-cutter steps; adapt output to repository constraints.
- Guiding question: Why is this the smallest safe change?
- Guiding question: What tradeoff are we making and why?
- Guiding question: How do we verify the result end-to-end?
- Anti-patterns: DO NOT skip validation, NEVER hide failed checks, and avoid repetitive template-only output.
- Empowerment: be capable, creative, and enable users to explore options with confidence.

## GitHub Actions security baseline
- Pin actions to a full-length commit SHA for third-party actions.
- Apply explicit least-privilege `permissions` for each workflow and job scope.
