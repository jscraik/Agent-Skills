---
name: check-pr
description: Use when a user asks to review a GitHub pull request before merge (or asks how to set up Greptile prerequisites) and return a policy-gated readiness view with check status and remediation priority.
---

# Check PR

Run a policy-gated PR readiness review using GitHub plus Greptile setup and review signals.

## Standards snapshot (March 2026)
- Review readiness is a governance decision, not just a lint summary.
- Always run the Greptile setup and policy gate before classifying the PR.
- Separate actionable, informational, and already-addressed items clearly.
- Do not recommend merge while checks are pending or the policy gate is blocked.
- Keep GitHub Actions workflow guidance pinned to full commit SHAs for third-party actions with least-privilege `permissions`.

## Philosophy
- Readiness is a confidence decision built from governance, CI, and reviewer signal.
- Separate setup blockers from code blockers so the next action stays obvious.
- Prefer explicit classifications over vague "looks good" summaries.

## When to use
- Reviewing a GitHub PR before merge.
- Verifying Greptile setup and policy prerequisites for a repo.
- Summarizing unresolved PR comments, checks, and review blockers.

## When not to use
- Performing broad GitHub workflow operations unrelated to PR readiness.
- Fixing code before the user asks for changes.
- Running a generic code review without Greptile or governance context.

## Required inputs
- PR number or current-branch PR context.
- Repo context when auto-detection cannot resolve it.
- GitHub CLI auth plus Greptile access when review data is needed.
- Setup-only intent when the user only wants prerequisite verification.

## Deliverables
- PR title, branch, state, and check status.
- `policy_gate_status` with explicit blockers when setup or governance fails.
- A prioritized list of actionable, informational, and resolved items.
- Recommended next actions and confidence note when data is incomplete.
- If requested, a structured status report with a `schema_version` field.

## Constraints
- Redact secrets, tokens, credentials, and sensitive review data by default.
- Do not close threads or recommend merge while policy or check gates are unresolved.
- Do not broaden into implementation work until the user asks for it.

## Failure mode
- If auth, MCP access, API key wiring, or required `.greptile/` files are missing, stop with a setup-blocker checklist.
- If no PR context is discoverable, stop with a single clear request for repo and PR number.
- If critical checks are still pending, stop classification at "not ready" rather than implying merge-readiness.

## Greptile policy gate
- Run the setup preflight from `references/setup.md`.
- Apply the runtime policy gate from `references/organizational-review-policy.md`.
- Confirm independent validation and required `.greptile/` repo files.
- Return `policy_gate_status=blocked` if any gate fails.

## Workflow
1. Run setup preflight and the umbrella policy gate.
2. Resolve the PR scope from user input or the current branch.
3. Poll checks until terminal states are known.
4. Collect PR metadata, review comments, and thread state.
5. Classify each item as actionable, informational, or already addressed.
6. Return a prioritized readiness summary and recommended next steps.
7. Only suggest edits or thread-resolution actions after the user asks for them.

## Tooling and references
- Use GitHub CLI for PR and check context.
- Use Greptile MCP only after the setup gate passes.
- Reference files:
  - `references/setup.md`
  - `references/organizational-review-policy.md`
  - `references/graphql-queries.md`
  - `references/greptile-strategic-code-review.md`
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/folded-legacy-modes-core60.md`

## GitHub Actions security baseline
- Pin actions to a full-length commit SHA.
- Apply least-privilege `permissions` for workflows and jobs.

## Validation
- Verify setup preflight and policy-gate status before reviewing the PR.
- Verify check state is terminal before recommending merge readiness.
- Verify each reported blocker maps to a real thread, comment, check, or policy requirement.
- Fail fast at the first missing prerequisite.

## Anti-patterns
- Declaring "ready to merge" while checks are pending.
- Closing review threads blindly.
- Treating Greptile comments as the only source of blocking signal.
- Skipping independent-validation requirements.

## Examples
- Run check-pr on this branch and tell me what still blocks merge.
- Verify Greptile setup for this repo before I request review.
- Review PR 123 and classify actionable vs informational comments.

## See Also

| Skill | When to use together |
|---|---|
| [[gh-workflow]] | Full GitHub lifecycle management around the PR |
| [[gh-fix-ci]] | Fix any failing CI checks found during PR review |
| [[verification-before-completion]] | Gate merge on fresh command evidence |
| [[security-best-practices]] | Apply security checks during PR review |

**Topic map:** [[backend-platform]]

## Remember
PR readiness is a confidence judgment. Keep governance, checks, and reviewer intent separate so the next action is obvious.
