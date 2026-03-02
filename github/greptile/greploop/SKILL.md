---
name: greploop
description: "Use when a user wants a closed-loop PR hardening pass (or asks how to set up Greptile loop prerequisites): run policy-gated review/fix iterations toward high-confidence, merge-safe output."
knowledge_graph_profile: references/task-profile.json
---

# Greploop

## Table of Contents
- [When to use](#when-to-use)
- [Inputs](#inputs)
- [Greptile umbrella policy](#greptile-umbrella-policy)
- [Setup (how to configure Greptile loop prerequisites)](#setup-how-to-configure-greptile-loop-prerequisites)
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
Use this skill when the user wants a repeatable review-and-fix loop to reduce risk before merge.

It is appropriate when the goal is to:
- drive toward zero actionable comments,
- reach a stronger confidence signal (target 5/5 when available),
- enforce organizational policy compliance every iteration,
- and keep feedback cycles bounded and deterministic.

Do not use this for unrelated tasks such as editing docs without PR context.

## Inputs
- Optional PR number (defaults to current branch PR if omitted).
- Optional max-iteration setting (default 5).
- Target confidence objective (default 5/5 and zero unresolved actionable comments).
- Optional setup-only intent (`setup`, `verify MCP`, `configure api key`).
- Repository must support `gh` CLI and authenticated API access.

## Greptile umbrella policy
This skill runs under the Greptile umbrella policy and must execute the runtime policy gate before the first loop and before each subsequent iteration.

Required references:
- [Setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)

## Setup (how to configure Greptile loop prerequisites)
Before running the loop, verify setup once per environment/repository:

1. GitHub CLI auth is valid (`gh auth status`).
2. Greptile MCP server is configured:
   - URL: `https://api.greptile.com/mcp`
   - Authorization: `Bearer <GREPTILE_API_KEY>`
3. `GREPTILE_API_KEY` is available in the runtime environment.
4. MCP connectivity works (`list_custom_context`).
5. Repository-level `.greptile/` context exists (including mandatory `files.json`).

Full checklist and policy context:
- [Greptile setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)

## Procedure
0. Run setup preflight checks + umbrella policy gate.
   - If setup is incomplete, return `blocked` with missing prerequisites and stop.
   - Run runtime policy gate checks from `references/organizational-review-policy.md`.
   - Confirm independent validation and required `.greptile/` governance files.
   - If any gate fails, return `blocked` with `policy_gate_status` and blockers.
1. Resolve PR scope.
   - Detect PR number if missing.
   - Confirm branch state and latest commit hash before any loop iteration.
2. Run one review cycle per iteration (max 5).
   - Re-run policy gate at iteration start to catch drift.
   - trigger/refresh PR review signal (push if changes occurred),
   - wait for terminal check state,
   - fetch latest Greptile review and unresolved threads,
   - compute `confidence score` and unresolved actionable count.
3. Exit conditions (stop immediately).
   - confidence is 5/5 **and** unresolved actionable comments = 0,
   - user requests stop,
   - max iteration reached,
   - or any gating check fails (policy/auth/invalid PR).
4. If not done, handle comments.
   - classify each unresolved comment as actionable vs informational,
   - apply fixes only for actionable code defects,
   - skip intentional style disagreements unless policy changes.
5. Reconcile progress.
   - commit scoped fixes,
   - push branch,
   - reopen next cycle only with a clean state summary.
6. Report final loop outcome and any remaining risks.

## Outputs
Return a compact report in this schema:

| field | value |
|---|---|
| policy_gate_status | pass/blocked |
| iterations | N |
| final_confidence | X/5 |
| resolved_comments | N |
| remaining_actionable | N |
| remaining_informational | N |
| blocking_issues | list |

Include a suggested next step when the loop ends early.
If setup or policy is incomplete, include an explicit blocker checklist and do not run loop iterations.

Safe output example:

```text
Greploop complete
Policy gate: pass
Iterations: 2
Final confidence: 5/5
Resolved comments: 7
Remaining actionable: 0
Remaining informational: 1
Status: stop (target achieved)
```

Reference material:
- [GraphQL helpers](references/graphql-queries.md)
- [Setup and governance](references/setup.md)
- [Organizational review policy](references/organizational-review-policy.md)
- [Strategic roadmap and loops section](references/greptile-strategic-code-review.md)

## Validation
- Fail fast if required PR context, auth, or branch state cannot be confirmed.
- Fail fast if setup preflight fails (missing MCP config/API key wiring/auth).
- Fail fast on policy gate violations (independent validation, `.greptile/` governance, precedence/strictness checks).
- Do not exceed 5 iterations unless user explicitly increases the iteration cap and justifies the request.
- Stop as soon as blocking checks fail; do not continue blind rewrites when review data is stale.
- Keep each iteration atomic and clearly reported.

## Anti-patterns
- Don't enter an infinite automation loop.
- Don't auto-apply changes from comments lacking concrete file-path evidence.
- Don't force “ready” if CI is still non-terminal.
- Don't skip policy gate checks after the first iteration.
- Don't mix policy changes into code fixes inside the same automated loop without confirmation.

## Constraints
- Avoid command output that includes secrets/tokens, or environment variables.
- Use repository-relative paths only.
- Do not run destructive commands (`git reset --hard`, and other destructive cleanup operations) without explicit user confirmation.
- If any step cannot be executed safely, emit `blocked` and request permission before continuing.

## Philosophy
Autonomous validation is valuable when it is bounded, auditable, and reversible.
Greploop should optimize signal quality by repeating only the smallest safe unit of change and re-evaluating until confidence improves.
The loop ends at the first reliable stopping condition, not at a fixed attempt count.

## Variation

Choose the loop shape to match intent:

- Prioritize speed for exploratory fixes when confidence is low and the risk is localized.
- Prioritize strictness for release-bound PRs where every unresolved blocker matters.
- Prioritize communication-first summaries when the user asks for a review status update.
- Vary stopping rationale details based on context (confidence score available vs CI-blocked).

## Remember

The agent is capable of extraordinary work in this domain.
These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push responsibly when confidence allows.

## Examples
- “Run greploop on PR 210 until it reaches 5/5 confidence.”
- “Run one greploop iteration and show unresolved comments only.”
- “Run greploop with a policy gate report each iteration.”
- “Stop at 5 iterations and give me the remaining risks without changing files.”
