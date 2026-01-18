---
name: gh-actions-fix
description: "Use gh to locate failing PR checks, fetch GitHub Actions logs for actionable failures, summarize the failure snippet, then propose a fix plan and implement after explicit approval.. Use when When a user asks to debug or fix failing GitHub Actions checks on a PR.."
---

# Gh Pr Checks Plan Fix

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md


## Overview

Use gh to locate failing PR checks, fetch GitHub Actions logs for actionable failures, summarize the failure snippet, then propose a fix plan and implement after explicit approval.
- Depends on the `plan` skill for drafting and approving the fix plan.

Prereq: ensure `gh` is authenticated (for example, run `gh auth login` once), then run `gh auth status` with escalated permissions (include workflow/repo scopes) so `gh` commands succeed. If sandboxing blocks `gh auth status`, rerun it with `sandbox_permissions=require_escalated`.

## Philosophy
- Prefer evidence from logs over speculation; cite exact failing steps.
- Fix the smallest surface area needed to make CI green.
- Preserve reviewer trust: explain the why behind each fix.
- Treat CI as a signal of product risk, not a nuisance.

## Guiding questions
- What failed first in the log and why?
- Is the failure flaky, environment-related, or deterministic?
- What is the smallest change that resolves the failure?
- How will the fix be verified (re-run jobs, targeted tests)?

## When to use
- When a user asks to debug or fix failing GitHub Actions checks on a PR.
- When a user wants a plan before applying CI fixes.
- When the user needs a summary of failing jobs and log evidence.

## Inputs

- `repo`: path inside the repo (default `.`)
- `pr`: PR number or URL (optional; defaults to current branch PR)
- `gh` authentication for the repo host

## Quick start

- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
- Add `--json` if you want machine-friendly output for summarization.

## Workflow

1. Verify gh authentication.
   - Run `gh auth status` in the repo with escalated scopes (workflow/repo) after running `gh auth login`.
   - If sandboxed auth status fails, rerun the command with `sandbox_permissions=require_escalated` to allow network/keyring access.
   - If unauthenticated, ask the user to log in before proceeding.
2. Resolve the PR.
   - Prefer the current branch PR: `gh pr view --json number,url`.
   - If the user provides a PR number or URL, use that directly.
3. Inspect failing checks (GitHub Actions only).
   - Preferred: run the bundled script (handles gh field drift and job-log fallbacks):
     - `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "<number-or-url>"`
     - Add `--json` for machine-friendly output.
   - Manual fallback:
     - `gh pr checks <pr> --json name,state,bucket,link,startedAt,completedAt,workflow`
       - If a field is rejected, rerun with the available fields reported by `gh`.
     - For each failing check, extract the run id from `detailsUrl` and run:
       - `gh run view <run_id> --json name,workflowName,conclusion,status,url,event,headBranch,headSha`
       - `gh run view <run_id> --log`
     - If the run log says it is still in progress, fetch job logs directly:
       - `gh api "/repos/<owner>/<repo>/actions/jobs/<job_id>/logs" > "<path>"`
4. Scope non-GitHub Actions checks.
   - If `detailsUrl` is not a GitHub Actions run, label it as external and only report the URL.
   - Do not attempt Buildkite or other providers; keep the workflow lean.
5. Summarize failures for the user.
   - Provide the failing check name, run URL (if any), and a concise log snippet.
   - Call out missing logs explicitly.
6. Create a plan.
   - Use the `plan` skill to draft a concise plan and request approval.
7. Implement after approval.
   - Apply the approved plan, summarize diffs/tests, and ask about opening a PR.
8. Recheck status.
   - After changes, suggest re-running the relevant tests and `gh pr checks` to confirm.

## Variation rules
- Vary depth by failure type (lint/test/build/deploy).
- Prefer a targeted fix for single-check failures; broader fixes only if multiple jobs fail.
- Use different evidence granularity for flaky vs deterministic failures.

## Empowerment principles
- Empower the user to approve fixes before code changes.
- Empower maintainers with clear trade-offs and rollback notes.
- Empower reviewers with direct links to evidence and rerun results.

## Anti-patterns to avoid
- Changing unrelated code while chasing a CI failure.
- Ignoring the first failure and fixing downstream noise instead.
- Disabling tests to get green without justification.
- Proceeding without user approval for code changes.

## Example prompts
- "Fix the failing GitHub Actions checks on my PR."
- "Summarize the failing CI logs and propose a plan before changes."
- "Use gh to pull failing job logs for the current branch PR."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Bundled Resources

### scripts/inspect_pr_checks.py

Fetch failing PR checks, pull GitHub Actions logs, and extract a failure snippet. Exits non-zero when failures remain so it can be used in automation.

Usage examples:
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "123"`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --pr "https://github.com/org/repo/pull/123" --json`
- `python "<path-to-skill>/scripts/inspect_pr_checks.py" --repo "." --max-lines 200 --context 40`

## Outputs
- A structured response or artifact appropriate to the skill.
- Include `schema_version: 1` if outputs are contract-bound.


## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.


## Validation
- Run any relevant checks or scripts when available.
- Fail fast and report errors before proceeding.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
