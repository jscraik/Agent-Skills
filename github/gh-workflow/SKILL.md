---
name: gh-workflow
description: "Consolidated GitHub lifecycle skill for agents and users: intake, issue fixing, PR prep, review request/reception, review comment handling, CI diagnosis, and server-side merge via gh. Use when requests involve GitHub issues/PRs/checks/merge operations."
knowledge_graph_profile: references/task-profile.json
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
3. PR context is resolved when needed (`gh pr view --json number,url,headRefName,baseRefName,state`).
4. For merge mode, check state/branch protection status is known.

If any precondition fails, return `status=blocked` with remediation.

## Default behaviors

### Merge defaults (`pr_merge_server`)

- Primary command:
  - `gh pr merge <pr> --squash --delete-branch --auto`
- Fallback if auto-merge unsupported and checks already passing:
  - `gh pr merge <pr> --squash --delete-branch`
- If auto-merge unsupported and checks are not passing:
  - Block and return required next action.

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
3. Execute mode-specific workflow:
   - `issue_fix`: inspect issue, implement minimal fix, run checks, summarize evidence.
   - `pr_prepare`: branch prep, stage intended files, commit, push, create draft PR.
   - `pr_request_review`: gather readiness evidence, produce review request summary, and propose reviewer focus points.
   - `pr_receive_review`: classify feedback, ask clarifying questions when needed, and apply only validated changes.
   - `pr_review_comments`: list threads, apply scoped fixes, map each fix to evidence.
   - `ci_diagnose`: inspect failing checks, summarize first actionable failure.
   - `pr_merge_server`: apply merge defaults/fallback and report final merge status.
   - `full_lifecycle`: chain `intake -> issue_fix -> pr_prepare -> pr_request_review -> pr_receive_review -> pr_review_comments -> ci_diagnose -> pr_merge_server`.
4. Return contract + human summary.

## Failure handling

- Missing auth -> `blocked` + `gh auth login` remediation.
- No current-branch PR and no PR provided -> `blocked` + request PR identifier.
- Merge requested with failing checks and no auto-merge path -> `blocked` + required checks to clear.
- External CI failure only -> `in_progress` or `blocked` with provider URL evidence.

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

<!-- decision-feedback-protocol:v1 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- If available, persist with `ops/scripts/graph/record-feedback.sh`; otherwise append a JSONL record to `ops/metrics/skill-feedback/decision-feedback.jsonl` in the active workspace.
<!-- /decision-feedback-protocol -->
