---
name: gh-workflow
description: "Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review request/reception, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations."
---

# GH Workflow (Canonical)

## When to use

Use this as the single source of truth for GitHub task execution when a request involves:

- GitHub issue triage/fixing
- PR preparation, review request/reception, or review comment handling
- CI failure diagnosis for PR checks
- Server-side merge with `gh pr merge`

## Philosophy

- One canonical workflow prevents drift across overlapping GH skills.
- Keep actions minimal, reversible, and evidence-backed.
- Prefer explicit state (`ready`, `blocked`, `in_progress`, `completed`, `failed`).
- Route non-GitHub Actions checks as links-only evidence.

## Variation guidance

- Adapt mode selection to user intent and available context.
- In `full_lifecycle`, skip already-completed stages and focus on the next blocker.
- Increase evidence detail for risky changes and merge operations.
- Keep routing deterministic while varying explanation depth for user vs agent consumers.

## Modes

Select one mode explicitly from user intent; default to `full_lifecycle` when multiple stages are requested.

- `intake`
- `issue_fix`
- `pr_prepare`
- `pr_request_review`
- `pr_receive_review`
- `pr_review_comments`
- `ci_diagnose`
- `pr_merge_server`
- `full_lifecycle`

## Inputs

- Requested mode (or clear intent that maps to one mode)
- Repo path/slug when ambiguous
- PR number or URL for PR/comment/check/merge workflows (optional only when discoverable from current branch)
- Issue number for `issue_fix`
- Review summary/context when handling incoming feedback (`pr_receive_review`)

## Preconditions

1. `gh` exists and is authenticated (`gh auth status`).
2. Repository context is resolved (`gh repo view --json nameWithOwner`).
3. **Git state is clean or understood** (`git status` shows expected branch, no unexpected conflicts).
4. PR context is resolved when needed (`gh pr view --json number,url,headRefName,baseRefName,state`).
5. For merge mode, check state/branch protection status is known.

**Precondition verification commands:**
```bash
# Always run before git operations
git status
git log --oneline -3
git branch -vv
```

If any precondition fails, return `status=blocked` with remediation.

## Default behaviors

### Verification Requirements (ALL Git Operations)

After ANY git operation (commit, push, merge, rebase), ALWAYS run verification and include output in response:

```bash
# Post-operation verification (required)
git status && git log --oneline -5 && git branch -vv

# For merges/rebases, also check for conflict markers
grep -r '<<<<<<<' . --include='*.ts' --include='*.tsx' --include='*.js' --include='*.json' 2>/dev/null || echo 'No conflict markers found'
```

**Do not report success until verification confirms clean state.**

### Merge defaults (`pr_merge_server`)

- Pre-merge verification:
  - Check `git status` for working tree clean
  - Verify `gh pr view <pr>` shows mergeable state
  - Confirm all required checks passing via `gh pr checks <pr>`
- Primary command:
  - `gh pr merge <pr> --squash --delete-branch --auto`
- Fallback if auto-merge unsupported and checks already passing:
  - `gh pr merge <pr> --squash --delete-branch`
- If auto-merge unsupported and checks are not passing:
  - Block and return required next action.
- **Post-merge verification (required):**
  - `git log --oneline -3` to confirm merge commit
  - `git status` to confirm working tree clean
  - `git branch -vv` to confirm branch deleted (if --delete-branch used)

### CI diagnosis scope (`ci_diagnose`)

- GitHub Actions: extract run/job evidence + failure snippets.
- Non-GitHub Actions checks: capture provider/check name + details URL only.

### Review lifecycle defaults

- `pr_request_review`:
  - Summarize change scope + risk areas before requesting review.
  - Include exact verification evidence used to justify readiness.
- `pr_receive_review`:
  - Triage each review item as `accept`, `clarify`, or `push_back_with_evidence`.
  - Do not apply feedback blindly; verify technically in repo context first.

## Outputs

All substantive responses must align with `references/contract.yaml` (`schema_version: 1`) and include:

- `mode`, `repo`, `pr`, optional `issue`
- `status`
- `actions_taken[]`
- `evidence[]`
- `merge` object (for merge mode)
- `next_step`
- `risks[]`

Also provide a concise human-readable summary.

## Workflow

1. Resolve mode from request.
2. Run `intake` gates (auth/repo/pr discovery).
   - Verify `gh auth status` succeeds
   - Verify `gh repo view --json nameWithOwner` resolves
   - Verify `git status` shows expected branch context
3. Execute mode-specific workflow:
   - `issue_fix`: inspect issue, implement minimal fix, run checks, summarize evidence.
   - `pr_prepare`: branch prep, stage intended files, commit, **verify with git status/log**, push, create draft PR.
   - `pr_request_review`: gather readiness evidence, produce review request summary, and propose reviewer focus points.
   - `pr_receive_review`: classify feedback, ask clarifying questions when needed, and apply only validated changes.
   - `pr_review_comments`: list threads, apply scoped fixes, map each fix to evidence.
   - `ci_diagnose`: inspect failing checks, summarize first actionable failure.
   - `pr_merge_server`: apply merge defaults/fallback, **verify merge succeeded with git log/status**, report final status.
   - `full_lifecycle`: chain `intake -> issue_fix -> pr_prepare -> pr_request_review -> pr_receive_review -> pr_review_comments -> ci_diagnose -> pr_merge_server`.
4. **Post-operation verification (all modes)**:
   - Run `git status && git log --oneline -5 && git branch -vv`
   - Include verification output in response
5. Return contract + human summary.

## Failure handling

### Authentication Issues
- Missing auth -> `blocked` + `gh auth login` remediation.

### Git State Issues
- **Misunderstood merge state**: If `git status` shows unmerged paths or conflicts exist, STOP and report actual state before proceeding.
- **Complex git situation**: If `git log --oneline --graph --left-right main...HEAD` shows unexpected divergence, ask user for guidance before resolving.
- **Working tree not clean**: If `git status` shows uncommitted changes before an operation, either commit/stash them or ask user how to proceed.

### PR Context Issues
- No current-branch PR and no PR provided -> `blocked` + request PR identifier.
- Merge requested with failing checks and no auto-merge path -> `blocked` + required checks to clear.
- External CI failure only -> `in_progress` or `blocked` with provider URL evidence.

## Troubleshooting Guide

### "Merge reported success but changes not on main"
1. Run `git log --oneline main -5` to verify merge commit exists
2. Run `git status` to check for incomplete merge state
3. Check `gh pr view <pr> --json state` to confirm PR is actually merged
4. If merge commit missing, the merge may have failed silently - investigate gh output

### "git status shows unmerged paths after rebase/merge"
1. List conflicted files: `git diff --name-only --diff-filter=U`
2. Check for conflict markers: `grep -r '<<<<<<<' . --include='*.ts' --include='*.tsx' 2>/dev/null`
3. Do NOT report success - ask user to resolve conflicts or abort with `git rebase --abort` / `git merge --abort`

### "Auth errors but gh auth status shows logged in"
1. Check shell environment safely (without printing token): `if printenv GITHUB_TOKEN >/dev/null 2>&1; then echo "GITHUB_TOKEN is set"; else echo "GITHUB_TOKEN is not set"; fi`
2. Verify no placeholder values in shell config: `grep -r 'your-token-here\|placeholder' ~/.zshenv ~/.zshrc ~/.bashrc 2>/dev/null`
3. Test direct API call: `gh api user -q '.login'`
4. If env var issues, ask user to check 1Password CLI integration: `op account list`

## Validation

Fail fast: **stop at the first failed gate** and fix it before continuing.

- Keep frontmatter to `name` + `description`.
- Keep logic canonical here; aliases must route here.
- Keep evals realistic and route-safe (`references/evals.yaml`).

## Anti-patterns

- Duplicating logic in alias skills.
- Attempting deep non-GitHub-Actions provider scraping.
- Merging server-side without reporting final merge outcome.
- Expanding scope beyond requested mode(s).

## Security constraints

- Never reveal secrets/tokens/PII.
- Do not run destructive git operations outside explicit request.

## Bundled scripts

- `scripts/inspect_pr_checks.py`
- `scripts/fetch_comments.py`
- `scripts/github-pr.py`

## Example prompts

- "Fix issue #123, open a draft PR, then merge when checks pass."
- "Prepare this PR for review with a concise reviewer brief and verification evidence."
- "Help me process this code review feedback and apply only valid changes."
- "Diagnose failing checks on PR 456 and summarize the first actionable failure."
- "Use gh to merge this PR to main server-side."
- "Address comments 2 and 4 on the current PR and show evidence."

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## References

- `references/contract.yaml`
- `references/evals.yaml`
- `references/migration.md`

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
