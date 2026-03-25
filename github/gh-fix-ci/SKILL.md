---
name: gh-fix-ci
description: "Diagnose failing GitHub Actions checks on a PR and prepare a fix path grounded in `gh` evidence. Use when the user wants CI failure analysis or repair for GitHub-hosted checks, not external CI triage."
metadata:
  skill-type: ci_cd_deployment
---

# GH Fix CI

Diagnose failing GitHub Actions checks on a PR, surface the first actionable failure, and only implement a fix after explicit approval.

## Standards snapshot (March 2026)
- Root cause beats symptom patching.
- GitHub Actions failures need run, job, and log evidence before proposing code changes.
- Keep non-GitHub providers link-only unless the user explicitly asks for broader provider work.
- Separate diagnosis, plan, approval, and implementation clearly.
- Preserve the GitHub Actions security baseline: pin third-party actions to a full commit SHA and use least-privilege `permissions`.

## Philosophy
- Diagnosis should reduce uncertainty before any code change is proposed.
- Prefer the first actionable failure over exhaustive but noisy log summaries.
- Keep the CI fix path narrow and reversible.

## When to use
- A user asks to inspect or fix failing GitHub PR checks backed by GitHub Actions.
- A PR is blocked on CI and the next step is log-backed diagnosis.
- The user wants a remediation plan before code changes are made.

## When not to use
- The failure is from Buildkite or another external provider and only the details URL is available.
- The user wants a full GitHub workflow lifecycle instead of CI diagnosis specifically.
- The task is local test debugging with no GitHub Actions context.

## Required inputs
- Repository path, or the current repo if it is unambiguous.
- PR number or URL when it cannot be discovered from the current branch.
- `gh` authentication with access to the repo and workflow data.

## Deliverables
- The failing check name, run URL, and first actionable failure snippet.
- A concise diagnosis summary and a proposed fix plan.
- Clear blocking notes when logs, auth, or provider access are missing.
- If requested, a structured status report with a `schema_version` field.

## Constraints
- Redact secrets, tokens, credentials, and sensitive log data by default.
- Do not claim a fix is correct without log-backed reasoning.
- Do not treat external CI providers as GitHub Actions unless the user explicitly broadens scope.

## Failure mode
- If `gh` auth is missing, stop with the exact remediation step.
- If there is no PR context, stop and ask for the PR number or URL.
- If the failing check is not GitHub Actions, report the provider and details URL only.
- If logs are unavailable or still pending, report that state instead of guessing.

## Workflow
1. Verify `gh` authentication.
2. Resolve the PR from user input or the current branch.
3. Inspect failing checks, preferring the bundled script.
4. Pull the first actionable GitHub Actions log evidence.
5. Summarize the failure and propose the smallest safe fix plan.
6. Only implement after explicit approval.
7. Recheck the relevant status after changes.

## Tooling and references
- Prefer `scripts/inspect_pr_checks.py` for durable check and log inspection.
- Use `gh pr checks`, `gh run view`, and direct Actions job log fetches as fallback.
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/folded-legacy-modes-core60.md`
  - `agents/openai.yaml`
- Use assets only when the task calls for bundled GH-specific support material from `assets/`.

## GitHub Actions security baseline
- Pin actions to a full-length commit SHA.
- Use explicit least-privilege `permissions` for each workflow and job.

## Validation
- Verify auth, PR context, and run context before diagnosing.
- Verify the reported failure comes from actual run evidence, not inference.
- Verify the proposed fix plan addresses the first real blocker.
- Fail fast at the first missing prerequisite.

## Anti-patterns
- Jumping from red CI to speculative fixes without log evidence.
- Treating external CI providers like GitHub Actions when only a URL is available.
- Mixing unrelated cleanup work into a CI fix path.
- Claiming success before checks rerun or the user explicitly accepts the residual risk.

## Examples
- Show me why this PR’s GitHub Actions checks are failing.
- Pull the first actionable failure from PR 123 and propose a fix.
- Diagnose this failing Actions run but do not change code yet.

## Remember
CI diagnosis should narrow the problem, not widen the scope. Pull the evidence first, then earn the fix.

## See Also

| Skill | When to use together |
|---|---|
| [[gh-workflow]] | Use for the full GitHub PR lifecycle — CI diagnosis is a single mode of this broader skill |
| [[systematic-debugging]] | When CI logs reveal a root-cause bug that needs structured investigation |
| [[verification-before-completion]] | Verify the fix passes CI before claiming the PR is ready |
| [[circleci]] | When the CI failure is from CircleCI rather than GitHub Actions |

**Topic map:** [[backend-platform]]


## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
